---
name: linejs-session-reliability
description: Fix linejs NOT_AUTHORIZED_DEVICE re-login loops.
---

# linejs Session Reliability

## When to use
- A linejs client loses connection every 1–2 minutes with `NOT_AUTHORIZED_DEVICE` / `V3_TOKEN_CLIENT_LOGGED_OUT`.
- LINE PC (or the user's phone) pops a "re-login required" prompt repeatedly — this is LINE's suspicious-access detection firing because the bridge does a full email/password re-login too often.
- You are building or maintaining any long-lived linejs process (auto-reply bot, group monitor, message forwarder).
- A Hermes plugin's `bridge.mjs` (or similar) edits keep "reverting" after restart.

## Root cause (read this first)
`@evex/linejs` `base/request/mod.js` `requestCore` does this on `NOT_AUTHORIZED_DEVICE`:

```js
if (res.data.e?.code === "NOT_AUTHORIZED_DEVICE") {
  delete this.client.authToken;
  this.client.emit("end", this.client.profile);
}
throw new InternalError(...);
```

It **deletes the authToken and emits `"end"`** instead of trying `tryRefreshToken()`. So any consumer that listens for `"end"` (or an `unhandledRejection` from the internal `noop` ping) and triggers a full re-login creates a loop:
`token expires → delete authToken → emit end → full re-login (email/password) → new short-lived token → expires in minutes → repeat`.

Email/password login yields a **short-lived** authToken that LINE invalidates quickly. Full re-logins trip LINE's anti-fraud ("不審なアクセス") which is why LINE PC asks the user to re-login.

## Fix 1 — Monkeypatch requestCore to refresh, not re-login (PRIMARY)
Wrap `client.base.request.request` right after login succeeds. On `NOT_AUTHORIZED_DEVICE`, call `tryRefreshToken()` then retry the original request once. This avoids the full re-login entirely.

```js
if (client?.base?.request?.request) {
  const originalRequest = client.base.request.request.bind(client.base.request);
  let refreshing = false;
  client.base.request.request = async function (...args) {
    try {
      return await originalRequest(...args);
    } catch (err) {
      const msg = String(err);
      if ((msg.includes("NOT_AUTHORIZED_DEVICE") || msg.includes("V3_TOKEN_CLIENT_LOGGED_OUT")) && !refreshing) {
        refreshing = true;
        try {
          if (client?.base?.auth?.tryRefreshToken) {
            await client.base.auth.tryRefreshToken();
            return await originalRequest(...args); // retry once with fresh token
          }
        } catch (refreshErr) {
          throw err; // re-throw original so legacy re-login handlers can still fire
        } finally {
          refreshing = false;
        }
      }
      throw err;
    }
  };
}
```
`tryRefreshToken()` reads `refreshToken` from the linejs `FileStorage` (persisted in `linejs-storage.json`). If the refreshToken itself is invalid (`accessTokenRefreshException: INVALID_REQUEST reasonCode 2`), the monkeypatch re-throws and the legacy full-re-login path takes over — but that should be rare once QR login is used (see Fix 2).

## Fix 2 — Explicit QR-only login when QR is requested
QR login is a separate worker session from LINE PC. Authenticating LINE PC does not authenticate the worker, and a worker password re-login can displace the PC session and trigger another PC QR prompt.

When the user requests QR authentication:
- In `bridge.mjs`, use a literal `const loginMode = "qr";` and a dedicated `loginMode === "qr"` branch that calls `loginWithQR(...)` **without** auth-token/email/password fallbacks. `auto` mode is unsafe because stale credentials can select password login before QR.
- In the launcher (`core.py`), set `LINEJS_PERSONAL_LOGIN_MODE=qr` and remove `LINEJS_PERSONAL_EMAIL`, `LINEJS_PERSONAL_ADDRESS`, `LINEJS_PERSONAL_PASSWORD`, `LINEJS_PERSONAL_PASS`, `LINEJS_PERSONAL_AUTH_TOKEN`, and `LINEJS_PERSONAL_DISABLE_QR` from the child environment. Also disable the legacy fallback unless explicitly requested.
- In QR mode, keepalive must not call `startLogin()` while `loginState === "logging_in"`, and must not auto-relogin after session loss. Expose `qr_required` / emit `login:qr:required` and wait for operator action.
- Generate a fresh QR from the current `/status` `qrUrl` immediately before presenting it. QR URLs are short-lived; after `有効期限切れ` or `読み込めない`, stop/start with `force=true`, fetch a new URL, and render it again. Never reuse an old QR PNG or URL.
- Success requires `loginState=ready`, profile data, and a real authenticated API smoke test; an HTTP status response alone is insufficient.

## Fix 3 — Keepalive with cooldown + exponential backoff
A naive `setInterval(..., 20000)` that calls `startLogin()` whenever `loginState === "error"` creates a tight re-login storm (observed: 76 re-login attempts in minutes). Gate it:

```js
let reloginCooldownUntil = 0;
let reloginBackoffMs = 60000; // start 60s
const RELOGIN_MAX_BACKOFF = 1800000; // 30 min cap
function startKeepalive() {
  setInterval(async () => {
    if (!client || loginState === "error") {
      const now = Date.now();
      if (now < reloginCooldownUntil) return; // still cooling down
      reloginCooldownUntil = now + reloginBackoffMs;
      try {
        await startLogin();
        reloginBackoffMs = 60000; // reset on success
      } catch {
        reloginBackoffMs = Math.min(reloginBackoffMs * 2, RELOGIN_MAX_BACKOFF);
      }
    }
  }, 20000);
}
```

## Fix 4 — Don't double-register process-level handlers
`process.on("unhandledRejection", ...)` registered inside `startLogin()` (called on every re-login) stacks handlers. One `noop` rejection then fires the handler 6×. Register ONCE, and debounce:
```js
let lastTokenErrorTs = 0;
process.on("unhandledRejection", (reason) => {
  const msg = String(reason);
  if (msg.includes("NOT_AUTHORIZED_DEVICE") || msg.includes("V3_TOKEN_CLIENT_LOGGED_OUT")) {
    const now = Date.now();
    if (now - lastTokenErrorTs < 60000) return; // 60s debounce
    lastTokenErrorTs = now;
    loginState = "error"; // let keepalive (Fix 3) handle re-login with backoff
  }
});
```

## Hermes-plugin source-of-truth gotcha
If the bridge is a Hermes plugin, `~/.hermes/plugins/<name>/bridge.mjs` is the SOURCE OF TRUTH. On every `start_payload()`, `core.py:_write_worker_files()` copies the plugin file over the node runtime copy (`~/.hermes/<name>/node/bridge.mjs`). **Edits to the node copy are lost on restart.** Always edit the plugin file, then sync/copy to the runtime copy for the current run, then restart.

## Self-reply loop prevention (bot-specific)
If the bot replies to its own trigger (e.g. user tests `#はくあ` on their own message), cap replies per window or you get an infinite self-conversation. Go-side pattern:
```go
const SelfTriggerWindow = time.Hour
const MaxSelfTriggersPerWindow = 3
func selfTriggerAllowed() bool {
    // reset count if window expired; permit while under cap
}
```
Forward self-messages that contain trigger tags to the webhook, but let the server enforce the 3× cap.

## Verification
- `node --check bridge.mjs` after every edit.
- `go test -run TestSelfTrigger ./...` for the cap logic.
- Runtime checks: `GET /health` (Go), `GET /status` (bridge — expect `qrAvailable:true` after QR login, `loginState:ready`), `GET /events` (expect `login:patched_request` once after login; expect ZERO `login:password:start` in the last 5 min once stable).
- Isolate-test the monkeypatch with a mock `client.base` (see references/monkeypatch-test.md).

## Pitfalls
- Don't call `startLogin()` directly from the `unhandledRejection` handler — that bypasses backoff and recreates the storm. Only set `loginState = "error"` and let keepalive handle it.
- Don't assume `client.auth.tryRefreshToken` exists — it's `client.base.auth.tryRefreshToken` (the Client wraps a BaseClient).
- Email/password `refreshToken` can become `INVALID_REQUEST reasonCode 2` after many re-logins; QR login is the durable fix, not more email/password retries.
- If `/send` fails with `NOT_AUTHORIZED_DEVICE`, refresh-then-retry in the handler too (return `sentIds` so the server can track self-replies).
