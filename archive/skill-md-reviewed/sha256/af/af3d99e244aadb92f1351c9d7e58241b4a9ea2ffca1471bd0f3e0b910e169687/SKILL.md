---
name: line-personal-bridge
description: Personal LINE account bridge for Hermes. Preferred runtime is a Playwright Chromium bridge behind a tiny local HTTP server. Official LINE channel adapters are untouched.
triggers:
  - line personal bridge
  - personal line account
  - linepy
  - LINE personal bridge
  - playwright line
  - qr login line
---

# line-personal-bridge

Personal LINE bridge for Hermes. Preferred runtime is a **Playwright Chromium bridge** behind a tiny local HTTP server. Official LINE channel adapters are untouched.

## Runtime choices

- **linejs plugin path (current for ボブにゃん):** active profile plugin `~/.hermes/plugins/line-personal-bridge` uses `@evex/linejs` from the zapabob/evex linejs lineage behind a local Node HTTP worker on port `9101`. Enable with `hermes plugins enable line-personal-bridge` and `hermes tools enable line-personal`. Auth envs are `LINEJS_PERSONAL_*`; legacy `LINE_PERSONAL_*` auth fallback is only used when `LINEJS_PERSONAL_USE_LINE_PERSONAL_FALLBACK=1`.
- **Playwright path:** useful when linejs/Thrift login is blocked; drives a real browser and can survive some protocol changes.
- **linepy path:** deprecated fallback. In practice it can be blocked at the Thrift layer (`EOFError` on `getRSAKeyInfo` / `getAuthQrcode`) and depends on guard patterns that change without notice.

## Plugin architecture (linejs path)

```
~/.hermes/plugins/line-personal-bridge/
├── plugin.yaml           # Plugin manifest, tool schemas, env requirements
├── __init__.py           # register(ctx) — registers tools + slash command
├── core.py               # Python side: HTTP client, env handling, schemas
├── bridge.mjs            # Node.js worker: @evex/linejs client, HTTP server
├── auth.py               # (legacy) linepy Auth wrapper
├── bridge.py             # (legacy) Playwright bridge
└── README.md
```

- **Python side (`core.py`)**: Discovers env, writes worker files, runs `npm install`, spawns Node worker, exposes HTTP JSON helpers (`status_payload`, `start_payload`, `send_payload`, etc.), registers tools with `toolset="line-personal"`.
- **Node side (`bridge.mjs`)**: Loads `@evex/linejs`, handles login (auth token / email+password / QR), listens for `message` events, serves HTTP endpoints (`/health`, `/status`, `/events`, `/chats`, `/send`).
- **Communication**: Python ↔ Node via localhost HTTP (port 9101). No shared memory, no stdin/stdout parsing.

## Files

- `core.py` — Python plugin core: env resolution, worker lifecycle, HTTP client, tool registration
- `bridge.mjs` — Node.js worker: @evex/linejs client, login, event loop, HTTP server
- `plugin.yaml` — Plugin manifest (tools, CLI command, env vars, config)
- `__init__.py` — Plugin entry point (`register(ctx)`)
- `scripts/bridge.py` — Playwright bridge + local HTTP server (legacy path)
- `scripts/playwright_screenshot.py` — one-shot page screenshot probe (legacy)
- `scripts/run.sh` — background launcher (legacy)
- `scripts/qr_login.py` — QR login helper (legacy)

## Env

### linejs worker path

- Primary env prefix: `LINEJS_PERSONAL_*`
- If the operator explicitly says to use the existing `LINE_PERSONAL_*` credentials, set `LINEJS_PERSONAL_USE_LINE_PERSONAL_FALLBACK=1`, load `~/.hermes/.env` into the current process, and restart the worker with `force=True`.
- Fallback mapping: `LINE_PERSONAL_AUTH_TOKEN`, else `LINE_PERSONAL_ADDRESS`/`LINE_PERSONAL_EMAIL` + `LINE_PERSONAL_PASS`/`LINE_PERSONAL_PASSWORD`.
- Default linejs port: `9101` to avoid the older Playwright bridge on `9100`.
- See `references/linejs-env-fallback.md` for the exact restart/debug workflow and safe interpretation of `INVALID_IDENTITY_CREDENTIAL`.

### Playwright bridge path

- `LINE_PERSONAL_ADDRESS`
- `LINE_PERSONAL_PASS`
- `LINE_PERSONAL_ALLOWED_USERS` (optional, comma-separated)
- `LINE_PERSONAL_PORT` (default `9100`)
- `LINE_PERSONAL_HOST` (default `127.0.0.1`)
- `LINE_PERSONAL_HEADLESS` (`1` default; `0` to show browser)
- `LINE_PERSONAL_PROFILE_DIR` (optional Chrome user data dir for session reuse)

## Quick start

```bash
bash scripts/run.sh
```

## Sanitization (input/output guard)

Both Python (`core.py::_sanitize_text`) and Node (`bridge.mjs::sanitizeResponse` / `sanitizeForLog`) apply multi-pass redaction before anything is logged or sent:

| Pass | Pattern | Example |
|------|---------|---------|
| 1 | `LINE(JS)?_PERSONAL_(AUTH_TOKEN\|PASSWORD\|PASS\|EMAIL\|ADDRESS)=` | `LINEJS_PERSONAL_AUTH_TOKEN=abc` → `LINEJS_PERSONAL_AUTH_TOKEN=<redacted>` |
| 2 | Common secret keys with `=`/`:` | `API_KEY=sk-...` → `<redacted>` |
| 3 | Email addresses | `test@example.com` → `<redacted>` |
| 4 | Long alphanumeric strings (32+ chars) | `[REDACTED_TOKEN]` → `<redacted>` |

Use `_sanitize_text(text)` in Python tool handlers; the Node worker auto-sanitizes `message.text` before logging and sanitizes every outbound reply via `sanitizeResponse()`.

## Auto-reply (group-only, tag-triggered)

Configured via `LINEJS_PERSONAL_*` env vars (fallback to `LINE_PERSONAL_*` when `LINEJS_PERSONAL_USE_LINE_PERSONAL_FALLBACK=1`):

| Env var | Default | Purpose |
|---------|---------|---------|
| `AUTO_REPLY` | `1` | Enable/disable |
| `AUTO_REPLY_TRIGGERS` | `#はくあ,#hermesagent` | Comma-separated trigger tags (case-insensitive) |
| `AUTO_REPLY_ONLY_GROUPS` | `1` | Only reply in group/room chats (MID starts with `c`/`r`) |
| `AUTO_REPLY_COOLDOWN_MS` | `5000` | Per-chat cooldown |

Default reply: `はくあです！ #はくあ #hermesagent`

## Dynamic replies via webhook

Set `LINEJS_PERSONAL_AUTO_REPLY_WEBHOOK` to an HTTP endpoint. On each trigger:

1. Worker POSTs JSON payload (sanitized):
```json
{
  "message": { "text": "...", "from": {...}, "to": "c...", "isGroup": true, "mid": "..." },
  "profile": { "mid": "...", "displayName": "..." },
  "trigger": "#はくあ"
}
```
2. Expects `{ "text": "reply content" }` within `AUTO_REPLY_WEBHOOK_TIMEOUT_MS` (default 10s)
3. On timeout/error, falls back to default reply
4. Every outbound reply passes through `sanitizeResponse()`

## Login flow & PIN handling

- ボブにゃん環境は **email/password login only**。QR loginページは読めないため使わない。`start_personal_line_bridge.py` sets `LINEJS_PERSONAL_LOGIN_MODE=email_password` and `LINEJS_PERSONAL_DISABLE_QR=1`; plugin `bridge.mjs` must fail clearly if email/password credentials are absent instead of falling back to QR.
- Password login emits `login:pin` event with 6-digit PIN
- Operator must enter PIN in LINE app **before** the internal `fetch` call times out (~30-60s)
- If `NOT_AUTHORIZED_DEVICE` / `V3_TOKEN_CLIENT_LOGGED_OUT` appears, delete `linejs-storage.json` and restart to force fresh email/password login; do not switch to QR for this environment.
- The worker writes events to `bridge.log`; tail it to catch the PIN in real time

## HTTP (linejs worker)

- `GET /health` — `{ ok: true }`
- `GET /status` — login state, profile, auth methods, auto-reply config, event count
- `GET /events?limit=N` — recent events (default 20, max 200)
- `GET /chats?limit=N` — joined chats (default 50, max 500); requires `loginState: ready`
- `POST /send { "to": "<mid>", "text": "<text>", "e2ee": true }` — send message; text is sanitized

## Quick start (linejs path)

```bash
# 1. Ensure .env has credentials (at least one auth method)
LINEJS_PERSONAL_EMAIL=[REDACTED_EMAIL]
LINEJS_PERSONAL_PASSWORD=yourpassword
# or
LINEJS_PERSONAL_AUTH_TOKEN=your_auth_token
# Legacy fallback (if already configured):
LINEJS_PERSONAL_USE_LINE_PERSONAL_FALLBACK=1

# 2. Enable plugin + toolset
hermes plugins enable line-personal-bridge
hermes tools enable line-personal

# 3. Start worker (installs npm deps on first run)
/line-personal start

# 4. If email+password: check /status for pinCode, enter in LINE app
#    If auth token: should go ready immediately

# 5. Verify
/line-personal status
```

## Tools & slash command

| Tool | Description |
|------|-------------|
| `line_personal_status` | Show bridge readiness (no secrets) |
| `line_personal_install` | Write worker files + `npm install` |
| `line_personal_start` | Start worker (`force=true` to restart) |
| `line_personal_stop` | Stop worker (`force=true` to kill) |
| `line_personal_send` | Send text to a chat MID |
| `line_personal_events` | Fetch recent events |
| `line_personal_chats` | List joined chats |

Slash command: `/line-personal [status|install|start|stop|events|chats|send <mid> <text>]`

## Upstream contribution to zapabob/linejs

For ボブにゃん's current runtime, the installed package is usually under `~/.hermes/line-personal-bridge/node/node_modules/@evex/linejs` (older notes may mention `~/.hermes/plugins/...`). That installed JSR/NPM package is normally **not a git repo** and may contain JSR-transformed imports (`.js`, `jsr:@...`) that should not be copied directly into upstream source.

Recommended workflow:

1. Verify whether the runtime package has real local modifications. Compare it with the clean JSR tarball from `package-lock.json` (`https://npm.jsr.io/.../@jsr/evex__linejs/<version>.tgz`). If hashes match, there are no local linejs-package changes to upstream.
2. Clone the source repo separately:
   ```bash
   git clone https://github.com/zapabob/linejs.git ~/Documents/linejs-upstream-work
   cd ~/Documents/linejs-upstream-work
   ```
3. Edit upstream source under `packages/linejs/` (not the installed package root) and add tests near the affected feature.
4. On Windows without Deno installed, use `deno-bin` via npx. Use a Windows-format `DENO_DIR` when running the Windows Deno binary from Git Bash:
   ```bash
   DENO_DIR='%USERPROFILE%\Documents\linejs-upstream-work\.deno-cache' npx -y deno-bin@2.2.7 fmt packages/linejs/path/to/file.ts
   DENO_DIR='%USERPROFILE%\Documents\linejs-upstream-work\.deno-cache' npx -y deno-bin@2.2.7 test --no-check --allow-all packages/linejs/path/to/file.test.ts
   ```
   If plain type-checking fails on unrelated existing `@ts-expect-error` comments, record that and run the focused runtime test with `--no-check`.
5. Push a branch and open a PR unless the user explicitly insists on direct `main` push:
   ```bash
   git switch -c fix/<short-name>
   git add packages/linejs/...
   git commit -m "fix: <summary>"
   git push -u origin fix/<short-name>
   gh pr create --base main --head fix/<short-name>
   ```
6. After merge/release, update the local Hermes plugin by reinstalling the linejs dependency or linking a local checkout for pre-release testing.

Always run `/line-personal status` to ensure the worker is running with your changes.

## Windows autostart workspace

For ボブにゃん's Windows setup, the `line-bot-sdk-go-workspace` checkout is repurposed as the **personal LINE supervisor + Hakua dynamic reply webhook** without changing the official LINE gateway adapter.

Files:
- `%USERPROFILE%\Desktop\line-bot-sdk-go-workspace\line-bot-sdk-go\examples\personal_line_bridge\main.go` — local Go webhook server at `127.0.0.1:9102`, endpoint `POST /reply`, calls `hermes chat -q` to generate sanitized Hakua replies.
- `...\examples\personal_line_bridge\start_personal_line_bridge.py` — starts the Go reply server, sets non-secret runtime policy (`AUTO_REPLY`, triggers, webhook URL), loads existing Hermes `.env` without printing it, and starts the `line-personal-bridge` plugin worker.
- `...\examples\personal_line_bridge\install_startup_personal_line_bridge.ps1` — installer for startup automation.
- Startup entry actually installed: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\HakuaPersonalLineBridge.vbs`.

Operational notes:
- This is Windows-logon autostart, not a system service before login.
- The startup script embeds no secrets; credentials remain in Hermes env/storage and are never printed.
- If password login emits `LINE_PIN_REQUIRED=<pin>`, the operator must enter it in the LINE app quickly.
- Health checks: `http://127.0.0.1:9102/health` for the Hakua reply webhook, `http://127.0.0.1:9101/status` for the linejs worker. Tailscale Serve exposes the Go reply server at `https://downl.taile4f666.ts.net/personal-line-health` and `https://downl.taile4f666.ts.net/personal-line-reply`; `.env` keys are `PERSONAL_LINE_GO_TAILNET_HEALTH_URL`, `PERSONAL_LINE_GO_TAILNET_REPLY_URL`, and `HAKUA_PERSONAL_LINE_REPLY_URL`. `start_personal_line_bridge.py` must call `ensure_tailscale_serve()` on every autostart and idempotently run/verify `tailscale serve --bg --yes --set-path /personal-line-health http://127.0.0.1:9102/health` and `/personal-line-reply http://127.0.0.1:9102/reply`, preserving existing Serve routes. In Git Bash/MSYS, run manual Tailscale Serve path commands with `MSYS_NO_PATHCONV=1` or `/personal-line-*` turns into `C:/Program Files/Git/...`.
- If `install_startup_personal_line_bridge.ps1` fails under Windows PowerShell 5 with a parser error around Japanese/emoji text or `&&`, rewrite it ASCII-only and avoid `&&` in generated VBS (`sh.CurrentDirectory = repoRoot`; `cmd = "cmd /c py -3 ..."`). Then reinstall the Startup VBS.
- PowerShell array literals can split generated VBS lines if concatenation is left as unparenthesized comma-separated items (seen as `repoRoot = "` / path / `"` on three lines). Generate the line as `('repoRoot = "{0}"' -f $repoRoot)` and remove commas between `$lines` entries, then reinstall and verify `HakuaPersonalLineBridge.vbs` has a single-line `repoRoot = "C:\\..."`.
- For no-duplicate startup, `start_personal_line_bridge.py` must compare live worker policy (webhook configured, 5s cooldown, allowed group MIDs, trigger tags) and force-restart only when the live worker differs; otherwise it should return `already_running=true` with one listener on 9101 and one on 9102.
- If linejs logs `fetchMyEvents(... AUTHENTICATION_FAILURE)`, `noop(... V3_TOKEN_CLIENT_LOGGED_OUT)`, or DNS `fetch failed` and the Node worker exits after briefly reaching `loginState=ready`, add `process.on("unhandledRejection"...)` / `process.on("uncaughtException"...)` guards in both plugin and worker `bridge.mjs`, then restart and verify `/status` stays ready after ~20s.
- Human-like reply policy: outbound LINE personal bot messages/replies must include both `#はくあ` and `#hermesagent`, 180-char default max, 8–28s jitter before sending, and the default 5s per-chat cooldown. The trigger tags are input triggers, and the same tags are also required as output identity markers.
- Reply threading: outbound auto-replies are sent as LINE replies (`relatedMessageId`) and their IDs are remembered. Later group messages that reply to those remembered Hakua messages trigger even without `#はくあ`/`#hermesagent`, using a 30s reply-thread cooldown.
- Manual reply send: the linejs `/send` HTTP endpoint should accept `relatedMessageId` / `replyToMessageId` and route through `client.base.talk.sendMessage({ to, text, relatedMessageId })` so operator-triggered replies are real LINE replies, not plain messages. See `references/manual-reply-send.md`.
- Allowed groups: Windows startup restricts reactions/admin commands via the private environment variable `LINEJS_PERSONAL_ALLOWED_GROUP_MIDS`; do **not** hardcode real group MIDs in public repos. Other groups are logged as `message:ignored` with `group_not_allowed` and get no reply.
- Group management: group chat commands support `!kick`, `!ban`, `!kickban`, `!unban`, or `#はくあ` / `＃はくあ` + `キック/バン/キックバン/キック(バン)/解除`. Targets can be the replied-to message author, a LINE mention, or an explicit user MID. Only the logged-in personal account itself or MIDs configured in `LINEJS_PERSONAL_GROUP_ADMIN_MIDS` / `LINEJS_PERSONAL_GROUP_ADMINS` can run them. `ban` persists a local per-chat banlist and tries to kick banned users again when they talk.
- Reply LLM provider rotation: the Go Hakua reply webhook accepts `-providers` / `HAKUA_REPLY_PROVIDERS`; default is `openai-codex,nvidia,nous,opencode-zen` and rotates on 429/rate-limit/connection/timeout errors.

## Session-specific references

- `references/group-allowlist-admin-rotation.md` — allowlisting `日本メンタル(雑談/通話グル)` and `生成AI、LLMなど`, reply-selected kick/ban targets, full-width command normalization, provider rotation, and restart/copy workflow for the linejs worker.
- `references/autostart-tailscale-and-login-validation.md` — Windows autostart must restore Tailscale Serve paths for the Go reply webhook, and LINE health must be validated with a real fetch because `loginState=ready` can still fail with `NOT_AUTHORIZED_DEVICE`.
- `references/linejs-logout-refetch.md` — recovery when status/health looks alive but real fetches fail with `V3_TOKEN_CLIENT_LOGGED_OUT` / `NOT_AUTHORIZED_DEVICE`; backup stale storage, force restart, surface PIN, then verify with `/chats`.
- `references/fetch-react-reauth-and-tailnet-verification.md` — end-to-end pattern for “fetch LINE writes and react”: handle false-positive ready states, reauth with PIN, verify `/chats` and delayed noop/fetch stability, send a threaded LINE reply, and verify Tailscale Serve routes when the write mentions Tailnet/autoconnect.
- `references/github-export-linets-worker.md` — cleanly export the personal LINE LineTS/LINEjs worker to a private GitHub repo; includes safe repo shape, `.gitignore`, secret scan, `npm run check`, audit note, and `gh repo create` flow.
- `references/reauth-fetch-reply-verification.md` — session-proven reauth pattern: stop worker, timestamp-backup `linejs-storage.json`, restart, enter PIN, verify `/chats` immediately and again after 90-120s, then send manual LINE replies with `relatedMessageId` and `#はくあ #hermesagent` markers.
- `references/github-export-linets-worker.md` — cleanly export the personal LINE LineTS/LINEjs worker to a private GitHub repo; includes safe repo shape, `.gitignore`, secret scan, `npm run check`, audit note, and `gh repo create` flow.
- `references/line-go-bot-public-export.md` — commit/push the Go reply webhook + Windows supervisor under `line-bot-sdk-go/examples/personal_line_bridge`; includes public-repo hygiene, real MID/secret scanning, verification commands, and visibility correction.
- `references/pin-handling.md` — details on handling the 6‑digit PIN required for email/password login, including how to detect the PIN via `/status` and automate user prompting.

## Troubleshooting

### `INVALID_IDENTITY_CREDENTIAL`
- Email/password rejected by LINE. Update `.env` with current password, or switch to `LINEJS_PERSONAL_AUTH_TOKEN`.
- After updating, restart with `force=true`: `/line-personal start force=true`

### `V3_TOKEN_CLIENT_LOGGED_OUT` / `NOT_AUTHORIZED_DEVICE`
- Indicates the LINE session was invalidated, often because another device logged in or the token expired.
- Important: `loginState=ready` is not sufficient proof of usability. After restart, immediately verify with `/chats`, then validate stability after 90–120s by checking `/events` no longer emits auth errors (`NOT_AUTHORIZED_DEVICE`, `V3_TOKEN_CLIENT_LOGGED_OUT`, `fetchMyEvents(... AUTHENTICATION_FAILURE)`).
- Fix: delete the storage file `linejs-storage.json` in the worker directory (`~/.hermes/line-personal-bridge/`) and restart the bridge (`/line-personal start force=true`). Alternatively, configure `LINEJS_PERSONAL_AUTH_TOKEN` to avoid repeated logins.
- If reauth requires PIN, complete it inside the LINE app before the 30–60s fetch window closes; otherwise the worker reaches `ready` but subsequent fetches fail with the same error.
- Prevent: ensure only one device (this bridge) is logged into the LINE account; log out other devices via LINE app → Settings → Account → Devices.

### Worker won't start / port in use
- Check `LINEJS_PERSONAL_PORT` (default 9101). Kill existing process on that port.
- `netstat -ano | findstr :9101` → `taskkill /PID <pid> /F`

### `npm install` fails
- Ensure Node.js ≥18 and npm are in PATH.
- Run manually: `cd ~/.hermes/plugins/line-personal-bridge/node && npm install`

### Auto-reply not firing
- Verify `LINEJS_PERSONAL_AUTO_REPLY=1` (default on)
- Check trigger tags in `LINEJS_PERSONAL_AUTO_REPLY_TRIGGERS`
- Ensure chat is a group/room (MID starts with `c` or `r`) if `AUTO_REPLY_ONLY_GROUPS=1`
- Check cooldown: `LINEJS_PERSONAL_AUTO_REPLY_COOLDOWN_MS` (default 5000ms)
- Check events: `/line-personal events` for `auto_reply` or `auto_reply:error`

### Auto-reply looks like Hermes logs or prompt text
- The Go Hakua reply webhook must call `hermes chat` in quiet mode (`-Q`) and strip CLI framing such as `session_id:`, `Query:`, `Warning: Unknown toolsets:`, and Bitwarden setup warnings before returning `{ "text": ... }` to LINE.
- If `Warning: Unknown toolsets: <name>` appears, remove stale names from `platform_toolsets.cli` in `~/.hermes/config.yaml` (use the active profile path). Historical stale names seen here: `messaging`, `mcp-codegraph`; the personal bridge toolset is `line-personal`.
- After changing `examples/personal_line_bridge/main.go`, run `gofmt`, rebuild `personal-line-hakua-reply.exe`, restart the 9102 reply server, then POST a sample `/reply` payload and verify the JSON text is a natural one-line reply only.

### Secrets appearing in logs
- Sanitization runs on both sides but is a safety net. Never intentionally put tokens/passwords in message text.
- If a secret leaked, rotate it immediately.
- **Credential login blocker in restricted networks:** If Playwright fails before form interaction due to page/router-level blocking, changing networks (mobile tether, VPN/Tailscale exit) is the most reliable fix. Blind retries are not helpful.
- **Selector drift:** If login stops at `wait_for_selector`, inspect current LINE DOM and update the browser selectors in `scripts/bridge.py`.

## Input/output sanitization (linejs path)

Both Python (`core.py::_sanitize_text`) and Node (`bridge.mjs::sanitizeResponse`) apply multi-pass redaction before any text enters logs, events, or outbound messages.

**Redaction passes (in order):**
1. `LINE(?:JS)?_PERSONAL_(AUTH_TOKEN|PASSWORD|PASS|EMAIL|ADDRESS)=<value>` → `<redacted>`
2. `API_KEY|SECRET|TOKEN|PASSWORD|PASS|AUTH_TOKEN|EMAIL|ADDRESS[:=]<value>` → `<redacted>`
3. Email addresses → `<redacted>`
4. Alphanumeric strings ≥32 chars (likely tokens) → `<redacted>`

This runs on:
- Incoming message text before it's pushed to the event log
- Outbound message text before it's sent via `/send`
- Any text logged via `pushEvent()` or `console.log`

**Do not log raw credentials.** The sanitization is a safety net; the primary rule remains "never put secrets in message text."

## Auto-reply (group-only, trigger tags)

When enabled, the worker auto-replies in group/room chats only (MIDs starting with `c` or `r`) when a message contains a configured trigger tag.

| Setting | Env var | Default |
|---------|---------|---------|
| Enabled | `LINEJS_PERSONAL_AUTO_REPLY` | `1` (on) |
| Trigger tags (comma-separated) | `LINEJS_PERSONAL_AUTO_REPLY_TRIGGERS` | `#はくあ,#hermesagent` |
| Group chats only | `LINEJS_PERSONAL_AUTO_REPLY_ONLY_GROUPS` | `1` (on) |
| Cooldown per chat | `LINEJS_PERSONAL_AUTO_REPLY_COOLDOWN_MS` | `5000` ms |

**Behavior:**
- 1:1 chats are ignored when `AUTO_REPLY_ONLY_GROUPS=1`
- Trigger match is case-insensitive substring search
- Per-chat cooldown prevents spam
- Reply text: `はくあです！ #はくあ #hermesagent` (sanitized before send)
- Events emitted: `auto_reply` (success) or `auto_reply:error` (failure)

## Env (linejs worker path)

### Primary auth
- `LINEJS_PERSONAL_AUTH_TOKEN` — auth token for `loginWithAuthToken`
- `LINEJS_PERSONAL_EMAIL` / `LINEJS_PERSONAL_PASSWORD` — email+password for `loginWithPassword`

### Legacy fallback (gated)
- `LINEJS_PERSONAL_USE_LINE_PERSONAL_FALLBACK=1` enables fallback to `LINE_PERSONAL_*` vars
- Fallback mapping: `LINE_PERSONAL_AUTH_TOKEN` → `LINE_PERSONAL_ADDRESS`/`LINE_PERSONAL_EMAIL` + `LINE_PERSONAL_PASS`/`LINE_PERSONAL_PASSWORD`

### Worker config
- `LINEJS_PERSONAL_HOST` (default `127.0.0.1`)
- `LINEJS_PERSONAL_PORT` (default `9101`)
- `LINEJS_PERSONAL_DEVICE` (default `DESKTOPWIN`)
- `LINEJS_PERSONAL_STORAGE` (default `./linejs-storage.json` in worker dir)
- `LINEJS_PERSONAL_ALLOWED_USERS` — comma-separated MIDs; if set, messages from other users are ignored (event type `message:ignored`)

### Auto-reply config
- `LINEJS_PERSONAL_AUTO_REPLY` — `1`/`true`/`yes` to enable
- `LINEJS_PERSONAL_AUTO_REPLY_TRIGGERS` — comma-separated trigger tags
- `LINEJS_PERSONAL_AUTO_REPLY_ONLY_GROUPS` — `1`/`true`/`yes` for group-only
- `LINEJS_PERSONAL_AUTO_REPLY_COOLDOWN_MS` — cooldown in milliseconds

### Playwright bridge path (legacy)
- `LINE_PERSONAL_ADDRESS`, `LINE_PERSONAL_PASS`
- `LINE_PERSONAL_ALLOWED_USERS` (optional, comma-separated)
- `LINE_PERSONAL_PORT` (default `9100`)
- `LINE_PERSONAL_HOST` (default `127.0.0.1`)
- `LINE_PERSONAL_HEADLESS` (`1` default; `0` to show browser)
- `LINE_PERSONAL_PROFILE_DIR` (optional Chrome user data dir for session reuse)
