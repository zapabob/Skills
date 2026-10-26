---
name: line-personal-bridge-stabilize
description: Fix LINE bridge token expiry via Go webhook, Node keepalive.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [LINE, Go, NodeJS, Webhook, Keepalive, Git]
---

# LINE Personal Bridge Stabilization

This skill captures the workflow to fix the unstable LINE Personal Bridge (token expiry every 1–2 min via `V3_TOKEN_CLIENT_LOGGED_OUT`) by making the Go server (`personal-line-hakua-reply`) own message receipt, reply generation, and send coordination, while the Node bridge (`linejs` on :9101) only maintains the LINE socket and forwards to Go `/webhook`. Adds 20s keepalive + auto-re-login in the bridge, self-reply prevention via sent-ID tracking, and commits changes to both repos.

**Does not cover**: QR login flow, VRChat integration, or Hermes plugin development beyond the bridge.

## When to Use

- LINE Personal Bridge dies with `V3_TOKEN_CLIENT_LOGGED_OUT` / `NOT_AUTHORIZED_DEVICE` every 1–2 min
- Need to split concerns: Go handles logic, Node only maintains socket
- Want self-reply prevention (Go tracks sent IDs, Node returns `sentIds` from `/send`)
- Need to commit/push changes to `zapabob/line-bot-sdk-go` (Go bot) and `zapabob/line-personal-linets-bot` (bridge)

## Prerequisites

- Windows host with `go` (tested 1.26.5), `node` (tested 20+), `git`
- Hermes fork at `%USERPROFILE%\Documents\New project\hermes-agent`
- Plugin dir: `~/.hermes/plugins/line-personal-bridge/` (source of truth for `bridge.mjs`)
- Go source: `%USERPROFILE%\Desktop\line-bot-sdk-go-workspace\line-bot-sdk-go\examples\personal_line_bridge\main.go`
- Bridge repo: `%USERPROFILE%\Documents\line-personal-linets-bot` (remote `zapabob/line-personal-linets-bot`, branch `main`)
- Go bot repo: `%USERPROFILE%\Desktop\line-bot-sdk-go-workspace\line-bot-sdk-go` (remote `zapabob/line-bot-sdk-go`, branch `master`)
- LINE credentials in env: `LINEJS_PERSONAL_EMAIL`, `LINEJS_PERSONAL_PASSWORD`
- Allowed groups configured: `LINEJS_PERSONAL_ALLOWED_GROUPS` (comma-separated MIDs)
- Triggers: `LINEJS_PERSONAL_AUTO_REPLY_TRIGGERS` (default `#はくあ,#hermesagent`)

## How to Run

Invoke through the `terminal` tool. Each major step is a separate command block.

## Quick Reference

| Component | Port | Endpoint | Role |
|---|---|---|---|
| Go server | 9102 | `/health`, `/reply`, `/webhook` | Receipt, generation, send coordination |
| Node bridge | 9101 | `/send`, `/events` | LINE socket, forward to Go `/webhook` |
| Plugin source | — | `~/.hermes/plugins/line-personal-bridge/bridge.mjs` | **Source of truth** (copied to node dir on every start) |
| Node runtime copy | — | `~/.hermes/line-personal-bridge/node/bridge.mjs` | Overwritten on every `line_personal_start` |

## Procedure

### 1. Verify running state & discover Go server

```bash
# Check LINE bridge status
line_personal_status

# Find Go server process & port
netstat -ano | findstr :9102
tasklist | findstr personal-line-hakua-reply

# Test Go health
curl -s http://127.0.0.1:9102/health
```

### 2. Rewrite Go server (`main.go`) — add `/webhook`, `sendViaBridge`, self-reply tracking

Edit `%USERPROFILE%\Desktop\line-bot-sdk-go-workspace\line-bot-sdk-go\examples\personal_line_bridge\main.go`:

- Add `webhookIncoming` struct (messageId, text, from, to, isMyMessage, isGroup, replyTargetId, isReplyToUs)
- Add flags: `-bridge` (Node base URL), `-sent-ids` (path to `sent_ids.json`)
- Add `/webhook` handler: validate payload, detect trigger tags (`#はくあ`, `#hermesagent`), check `isReplyToUs` via `sent_ids.json`, call `generateReply()`, send via `sendViaBridge()` with `relatedMessageId`
- `sendViaBridge()`: POST to Node `/send` with `to`, `text`, `relatedMessageId`; parse response `sentIds[]`; return to caller
- `rememberSentID()`: persist sent message IDs to `sent_ids.json` (with `sync.Mutex`)
- `isReplyToUs()`: check if `replyTargetId` exists in known sent IDs
- Add startup single-run lock (prevent duplicate processes)

### 3. Read plugin `core.py` — confirm `bridge.mjs` copy behavior

```bash
read_file ~/.hermes/plugins/line-personal-bridge/core.py --limit 100 --offset 1
# Search for _write_worker_files() — it copies plugin bridge.mjs → node dir on every start_payload()
```

### 4. Patch plugin `bridge.mjs` — Patch A: replace auto-reply with forward-to-Go

```bash
# Target: ~/.hermes/plugins/line-personal-bridge/bridge.mjs
# Replace inline auto-reply block (lines ~425–492) with:
if (!message.isMyMessage && isGroup) {
  forwardToGoWebhook(message, chatMid);
}
# Disable legacy auto-reply: if (false && autoReplyEnabled ...)
```

Use `patch` tool with exact old_string/new_string.

### 5. Patch plugin `bridge.mjs` — Patch B: add keepalive + auto-re-login

After `client.listen({ talk: true, square: false });` add:

```javascript
// Keep connection alive; auto re-login if token logs out.
startKeepalive();
```

Then add functions:

```javascript
// ---- Keepalive / auto re-login on token logout ----
function startKeepalive() {
  setInterval(async () => {
    try {
      if (!client || loginState === "error") {
        pushEvent("login:relogin:attempt", { reason: "token_or_state_error" });
        await startLogin();
      }
    } catch (err) {
      pushEvent("login:relogin:error", { error: redactError(err) });
    }
  }, 20000);
}

// ---- Forward received group messages to Go webhook server ----
const webhookForwardUrl = (lineEnv("WEBHOOK_FORWARD_URL") || "http://127.0.0.1:9102/webhook").trim();

function forwardToGoWebhook(message, chatMid) {
  const payload = JSON.stringify({
    messageId: message.raw?.id,
    text: message.text,
    from: message.from,
    to: chatMid,
    isMyMessage: message.isMyMessage,
    isGroup: isGroupChat(message),
    replyTargetId: getReplyTargetId(message),
    isReplyToUs: false,
  });
  fetch(webhookForwardUrl, {
    method: "POST",
    headers: { "content-type": "application/json; charset=utf-8" },
    body: payload,
  }).catch(err => pushEvent("webhook:forward_error", { error: redactError(err) }));
}
```

Also add `LOGIN_MODE` / `DISABLE_QR` env handling in `startLogin()` to enforce email/password only.

### 6. Fix syntax & verify plugin `bridge.mjs`

```bash
node --check ~/.hermes/plugins/line-personal-bridge/bridge.mjs
# Must exit 0 (no syntax errors)
```

### 7. Rebuild Go binary

```bash
cd /c/Users/downl/Desktop/line-bot-sdk-go-workspace/line-bot-sdk-go/examples/personal_line_bridge
gofmt -w main.go
go test ./...
go vet ./...
go build -o personal-line-hakua-reply.exe .
# Exit 0, ~10 MB exe produced
```

### 8. Sync plugin `bridge.mjs` → node runtime copy

```bash
cp ~/.hermes/plugins/line-personal-bridge/bridge.mjs ~/.hermes/line-personal-bridge/node/bridge.mjs
node --check ~/.hermes/line-personal-bridge/node/bridge.mjs
# Must exit 0
```

### 9. Restart Node bridge & Go server; verify

```bash
# Stop bridge
line_personal_stop

# Start bridge (force=true ensures fresh copy)
line_personal_start force=true

# Verify bridge status
line_personal_status
# Should show: loginState: ready, profile: B0B_nYAn

# Kill old Go process, relaunch background
taskkill /PID <old_pid> /F
start /B personal-line-hakua-reply.exe

# Test Go health + webhook self-reply
curl -s http://127.0.0.1:9102/health
curl -s -X POST http://127.0.0.1:9102/webhook -H "Content-Type: application/json" -d "{\"messageId\":\"test-1\",\"text\":\"#はくあ テスト\",\"from\":{},\"to\":\"g1\",\"isMyMessage\":false,\"isGroup\":true,\"replyTargetId\":\"\",\"isReplyToUs\":false}"
# Should return: {"accepted":true,"ok":true}
```

### 10. Patch Node `/send` handler to return `sentIds` array

In plugin `bridge.mjs`, `/send` handler: return `{ ok: true, sentIds: result.sentIds || [] }` from LINE send result.

### 11. Patch Go `sendViaBridge` to parse & return `SentIDs`

In `main.go`, `sendViaBridge()`: parse JSON response, extract `sentIds[]`, return to caller for `rememberSentID()`.

### 12. Reformat + rebuild Go; restart & verify end-to-end

```bash
cd /c/Users/downl/Desktop/line-bot-sdk-go-workspace/line-bot-sdk-go/examples/personal_line_bridge
gofmt -w main.go
go test ./...
go vet ./...
go build -o personal-line-hakua-reply.exe .

line_personal_stop
line_personal_start force=true

# Verify node copy has sentIds handling (grep for 'sentIds')
grep -c sentIds ~/.hermes/line-personal-bridge/node/bridge.mjs
# Should show 5+ occurrences

curl -s http://127.0.0.1:9102/health
curl -s -X POST http://127.0.0.1:9102/webhook -H "Content-Type: application/json" -d "{\"messageId\":\"test-2\",\"text\":\"#hermesagent テスト\",\"from\":{},\"to\":\"g1\",\"isMyMessage\":false,\"isGroup\":true,\"replyTargetId\":\"\",\"isReplyToUs\":false}"
# Should return: {"accepted":true,"ok":true}
```

### 13. Write implementation log

```bash
write_file /c/Users/downl/Desktop/line-bot-sdk-go-workspace\line-bot-sdk-go\_docs\2026-08-03_personal-line-go-webhook-receive_Codex.md <content>
```

### 14. Commit & push Go bot repo (`zapabob/line-bot-sdk-go`, master)

```bash
cd /c/Users/downl/Desktop/line-bot-sdk-go-workspace/line-bot-sdk-go
git add examples/personal_line_bridge/main.go examples/personal_line_bridge/start_personal_line_bridge.py examples/personal_line_bridge/install_startup_personal_line_bridge.ps1
git commit -m "feat: Go bot receives LINE webhook and routes replies via Node bridge

- Add /webhook endpoint that accepts Node linejs bridge payloads
- Detect trigger tags (#はくあ, #hermesagent) and self-reply targets
- Send generated replies through Node /send with relatedMessageId
- Persist sent message IDs for self-reply detection
- Add startup single-run lock and harden launcher scripts

Co-Authored-By: zapabob <[REDACTED_EMAIL]>"
git push origin master
# Verify: git fetch origin && git log --oneline origin/master -2
```

### 15. Sync & commit & push bridge repo (`zapabob/line-personal-linets-bot`, main)

```bash
# Sync plugin bridge.mjs → bridge repo src/
cp ~/.hermes/plugins/line-personal-bridge/bridge.mjs /c/Users/downl/Documents/line-personal-linets-bot/src/bridge.mjs

cd /c/Users/downl/Documents/line-personal-linets-bot
git add src/bridge.mjs
git commit -m "feat: sync bridge.mjs with plugin (forward-to-Go webhook, keepalive, email/password-only login)

- Add forwardToGoWebhook(): forwards every non-self group message to Go /webhook
- Add startKeepalive(): 20s interval ping + auto re-login on token logout
- Add LOGIN_MODE / DISABLE_QR env to enforce email/password auth (no QR)
- Disable legacy auto-reply (Go webhook now owns reply generation + sending)
- Go server handles tag detection (#はくあ, #hermesagent) and self-reply routing

Co-Authored-By: zapabob <[REDACTED_EMAIL]>"
git push origin main
# Verify: git fetch origin && git log --oneline origin/main -2
```

## Pitfalls

- **Plugin `bridge.mjs` is source of truth** — edits to `~/.hermes/line-personal-bridge/node/bridge.mjs` are lost on restart. Always edit the plugin copy.
- **`core.py:_write_worker_files()` overwrites node copy** on every `start_payload()`. Must restart bridge after plugin edits.
- **`zapabob/linejs` (main) has no `bridge.mjs`** — it's a library repo. Do not attempt to push bridge changes there.
- **`V3_TOKEN_CLIENT_LOGGED_OUT` every 1–2 min** means email/password auth yields short-lived tokens. Keepalive + auto-re-login in bridge is mandatory.
- **Self-reply prevention** requires both sides: Node `/send` returns `sentIds[]`, Go tracks them in `sent_ids.json`.
- **Windows `python` is store stub** — use `py -3` for scripts. Go uses `go` directly.
- **Git line-endings warning** (LF→CRLF) on `.ps1`/`.py`/`.go` is harmless; `.gitattributes` can silence it.
- **Dependabot high alerts** on `line-personal-linets-bot` are pre-existing (not from this change).

## Verification

Single command that proves the whole chain works:

```bash
# 1. Go health OK
curl -sf http://127.0.0.1:9102/health | grep -q '"ok":true' && echo "Go health OK"

# 2. Webhook accepts payload & returns accepted
curl -sf -X POST http://127.0.0.1:9102/webhook -H "Content-Type: application/json" -d "{\"messageId\":\"v-$(date +%s)\",\"text\":\"#はくあ verify\",\"from\":{},\"to\":\"g1\",\"isMyMessage\":false,\"isGroup\":true,\"replyTargetId\":\"\",\"isReplyToUs\":false}" | grep -q '"accepted":true' && echo "Webhook OK"

# 3. Bridge loginState ready
line_personal_status | grep -q 'loginState.*ready' && echo "Bridge ready"

# 4. Both repos synced with origin
cd /c/Users/downl/Desktop/line-bot-sdk-go-workspace/line-bot-sdk-go && git fetch origin --quiet && git rev-list --left-right --count master...origin/master | grep -q '^0	0$' && echo "Go bot synced"
cd /c/Users/downl/Documents/line-personal-linets-bot && git fetch origin --quiet && git rev-list --left-right --count main...origin/main | grep -q '^0	0$' && echo "Bridge repo synced"

echo "ALL VERIFICATIONS PASSED"
```