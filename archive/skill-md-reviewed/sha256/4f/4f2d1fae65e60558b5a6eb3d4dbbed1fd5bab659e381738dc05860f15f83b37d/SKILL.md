---
name: linejs-token-refresh-pattern
description: Stop linejs NOT_AUTHORIZED_DEVICE from looping re-logins.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [LINE, linejs, NodeJS, token, refresh, keepalive]
---

# linejs Token Refresh Pattern (anti infinite-relogin)

`@evex/linejs` (used by the LINE Personal Bridge) emits `NOT_AUTHORIZED_DEVICE` / `V3_TOKEN_CLIENT_LOGGED_OUT` when the auth token expires. Its internal `requestCore` does `delete this.client.authToken; this.client.emit("end", profile)` on that error. Naive handlers that set `loginState="error"` and immediately call full re-login on every keepalive tick cause:

1. **Infinite re-login loop** — keepalive (20s) → re-login → token expires in minutes → re-login again.
2. **Account flagging / collateral damage** — hammering LINE auth servers flags the device; the **LINE PC app also gets forced into endless re-login prompts** for the same account. This is the most visible symptom to the user.

## Correct handling order (prefer least disruptive)

1. **Try `tryRefreshToken()` first**, before any full re-login. The client keeps a `refreshToken` in storage; refresh extends the session without a new device login.
2. **Full email/password re-login is the LAST resort**, and MUST be rate-limited with cooldown + exponential backoff (start 60s, double up to 30 min max).
3. **Debounce error events** — `process.on("unhandledRejection")` registered inside `startLogin()` re-adds the listener on every login, so one error fires the handler 6×. Register ONCE at module load with a 60s dedupe flag.

## Key facts about the linejs client shape

- `client` is `@evex/linejs` `Client`; the underlying base is `client.base`.
- `tryRefreshToken()` lives on `client.base.auth.tryRefreshToken` (NOT `client.auth`). Call `await client.base.auth.tryRefreshToken()`.
- After refresh, retry the original call (e.g. `client.sendCompactMessage(to, text)`).
- `NOT_AUTHORIZED_DEVICE` is thrown as `RequestError: Request internal failed, <method>(/S4) -> {"code":"NOT_AUTHORIZED_DEVICE","reason":"V3_TOKEN_CLIENT_LOGGED_OUT"}`. Match on `includes("NOT_AUTHORIZED_DEVICE") || includes("V3_TOKEN_CLIENT_LOGGED_OUT")`.

## Reference implementation (keepalive with backoff)

```javascript
let reloginCooldownUntil = 0;
let reloginBackoffMs = 60000;
const RELOGIN_MAX_BACKOFF = 1800000;

function startKeepalive() {
  setInterval(async () => {
    try {
      if (!client || loginState === "error") {
        const now = Date.now();
        if (now < reloginCooldownUntil) return;
        pushEvent("login:relogin:attempt", { reason: "token_or_state_error", backoffMs: reloginBackoffMs });
        reloginCooldownUntil = now + reloginBackoffMs;
        await startLogin();
        reloginBackoffMs = 60000; // reset on success
      }
    } catch (err) {
      pushEvent("login:relogin:error", { error: redactError(err) });
      reloginBackoffMs = Math.min(reloginBackoffMs * 2, RELOGIN_MAX_BACKOFF);
    }
  }, 20000);
}
```

## `/send` handler: refresh-before-relogin

```javascript
} catch (compactError) {
  const msg = String(compactError);
  if (msg.includes("NOT_AUTHORIZED_DEVICE") || msg.includes("V3_TOKEN_CLIENT_LOGGED_OUT")) {
    try {
      if (client?.base?.auth?.tryRefreshToken) {
        await client.base.auth.tryRefreshToken();
        result = relatedMessageId
          ? await client.base.talk.sendMessage({ to, text, relatedMessageId })
          : await client.sendCompactMessage(to, text);
        const sentIds = rememberSentMessage(result);
        return sendJson(res, 200, { ok: true, result, sentIds, refreshed: true });
      }
    } catch (refreshErr) {
      pushEvent("login:refresh:failed", { error: String(refreshErr) });
    }
    loginState = "error";
    return sendJson(res, 503, { ok: false, error: "token_expired_retry", retry: true });
  }
  // fallback path...
}
```

## Pitfalls

- **Never set `loginState="error"` + immediate `startLogin()` on every tick.** That is the infinite loop. Always cooldown + backoff.
- **`client.auth.tryRefreshToken` is undefined** — use `client.base.auth.tryRefreshToken`.
- **`process.on("unhandledRejection")` inside `startLogin()` duplicates the handler.** Register once at module scope.
- **Collateral account flag**: a re-login storm also breaks the LINE PC app for the same account. If the user reports "LINE PC keeps asking to log in", suspect a background re-login loop and stop the bridge process (kill node on :9101, and if needed the LINE.exe app) before re-applying the rate-limited fix.
- **Verify the process is actually stopped** with `netstat -ano | findstr :9101 | findstr LISTENING` before claiming it's down — a supervisor (e.g. `core.py`) may auto-restart it.

## Related

- `line-personal-bridge-stabilize` (user-owned skill) — covers the full Go+Node split architecture. NOTE: its Step 5 keepalive snippet is the OLD broken pattern; adopt + patch it via `hermes curator adopt line-personal-bridge-stabilize` then apply this skill's corrected snippet.
- Source of truth for bridge code is `~/.hermes/plugins/line-personal-bridge/bridge.mjs` (copied to `~/.hermes/line-personal-bridge/node/bridge.mjs` on every `line_personal_start`).
