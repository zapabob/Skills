---
name: a2a-bot-meeting
description: "Coordinate meetings across Hermes bot-mode profiles."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [A2A, Bot-Mode, Multi-Agent, PowerShell, Cron]
---

# A2A Bot Meeting Coordinator

Coordinate meetings across multiple Hermes **bot-mode** profiles: deliver a shared message/info to every bot's "Bot Chat" session, then collect and integrate replies. This skill captures the working pattern from a production deployment where go-a2a-hub drove 12 bot profiles.

**What it does:** delivers to all bots asynchronously (non-blocking), supports topic-deep-dive dispatch, collects replies, and notifies via the hub `/records` endpoint — all wired into Hermes `cronjob` for unattended operation.

**What it does NOT do:** it does not replace the go-a2a-hub server (that is the delivery substrate); it does not auto-summarize replies into memory (collect only — you integrate).

**Dependency stance:** PowerShell + the `hermes` CLI built from the Hermes repo (`hermes-agent/.venv/Scripts/hermes.exe`). Bot-mode plugin must be enabled in `config.yaml` (`plugins.enabled` includes `hermes-bot-mode`). No third-party services.

## When to Use

- "set up bot meetings across my bots"
- "send a message to all bot profiles' Bot Chat"
- "dispatch a topic to the bots and collect their replies"
- "wire up periodic A2A sync between my agent profiles"
- Any task needing 1-to-many message fan-out across `hermes -p <profile>` sessions.

## Prerequisites

- Hermes repo built with venv: `%USERPROFILE%\Documents\New project\hermes-agent\.venv\Scripts\hermes.exe` (adjust path to your checkout).
- bot-mode plugin enabled (`hermes-bot-mode` in `plugins.enabled`).
- Optional relay substrate: go-a2a-hub (a Go HTTP server on `:9123`) exposing `/send`, `/status`, `/records`. If you only need CLI fan-out, the hub is optional.
- PowerShell available (`pwsh`).

## How to Run

Invoke scripts through the `terminal` tool. The canonical dispatch:

```
pwsh -File scripts/a2a-bot-meeting.ps1
pwsh -File scripts/a2a-topic-dispatch.ps1 -Topic zapabob_ouj -Depth deep
pwsh -File scripts/a2a-records-notify.ps1 -Quiet
```

Schedule recurring meetings with the `cronjob` tool (example prompt in `references/cron-prompts.md`).

## Quick Reference

- Deliver to one bot: `hermes -p <bot> chat --in ~ -c "Bot Chat" -Q -q "Message from <src>: <text>"`
- Get a bot's Bot Chat session id: run the above with a probe string, parse `Resumed session <id> "Bot Chat"`.
- Hub send (bot-mode relay): `curl -X POST http://127.0.0.1:9123/send -H "Content-Type: application/json" -d '{"target_bot":"<bot>","message":"..."}'`
- Hub status: `curl http://127.0.0.1:9123/status`
- Hub records: `curl http://127.0.0.1:9123/records`

## Procedure

1. **List your bot profiles.** The roster lives under `~/.hermes/profiles/<name>/`. Edit the `$bots` array in each script to match your actual profiles.

2. **Deliver a shared message (broadcast).** Use `scripts/a2a-bot-meeting.ps1`. It loops `$bots` and fires, for each:
   ```
   Start-Process -FilePath "cmd.exe" -ArgumentList "/c","hermes -p $bot chat --in ~ -c `"Bot Chat`" -Q -q `"$quoted`"" -WindowStyle Hidden
   ```
   `Start-Process` (not `&`) makes delivery non-blocking so the parent returns immediately. This is the key fix for the "hub /send hangs" problem.

3. **Deep-dive a topic.** Use `scripts/a2a-topic-dispatch.ps1 -Topic <name> -Depth deep`. Topics are defined as templates inside the script (`zapabob_ouj`, `hermes-a2a`, `career`). Add your own by editing the `$topics` hash.

4. **Collect replies.** Each bot answers in its own "Bot Chat" session. To fetch a session id without knowing it, send a probe:
   ```
   hermes -p <bot> chat --in ~ -c "Bot Chat" -Q -q "a2a_session_probe_$(date +%s)"
   ```
   The stdout line `↻ Resumed session <id> "Bot Chat"` is the id. Then read the session with the `session_search` tool: `session_search(profile="<bot>", session_id="<id>")`.

5. **Notify from hub records.** `scripts/a2a-records-notify.ps1` hits `/records`, formats Japanese Markdown, and re-dispatches to `origin` via `Start-Process hermes chat -q`.

6. **Automate.** Create three `cronjob` entries (see `references/cron-prompts.md`): hourly meeting, bi-hourly records notify, daily topic deep-dive. Set `deliver: origin`.

## Pitfalls

- **JSON-RPC -32601 from bot-mode.** A bot-mode profile's `/a2a/chat` endpoint registers NO JSON-RPC methods, so `POST {"message":...,"sender":...}` returns `{"error":{"code":32601,"message":"method not found"}}`. Do NOT try to fix the bot; deliver via the `hermes -p <bot> chat` CLI instead. This is by design.
- **`Start-Process` arg-splitting with Japanese/emoji.** Passing the message through `cmd.exe /c` with escaped double-quotes (`\"`) is the only reliable way we found on Windows; `Start-Process -ArgumentList` directly mangles multibyte text. The scripts use this pattern — keep it.
- **`/send` blocks if synchronous.** If the hub calls `hermes` and waits for the model reply, the HTTP request hangs until the bot finishes (can be minutes). Make `/send` spawn a goroutine and return `202 Accepted` immediately (see `references/hub-botmode-layer.md`).
- **`hermes sessions` has no `show`.** There is `sessions list/export/...` but NOT `sessions show <id>` and NOT `hermes session show`. Use the `session_search` tool (pass `session_id` + `profile`) to read a bot's replies. `sessions export <id>` dumps ALL sessions and is too heavy.
- **Bot Chat sessions are gateway server-side.** They do NOT appear in `hermes -p <bot> sessions list`. You must obtain the id by probing (step 4) or from a known prior session.
- **Hub `/records` resets on restart.** The in-memory record slice is empty after a hub restart; only `a2a_servers_status.json` (bot registry) is persisted. Persist records in the hub if you need history across restarts.
- **FTS5 does not index Bot Chat replies.** `session_search(query="Bot Chat meeting")` returns the DISPATCHING session, not the bot's reply, unless you pass the bot's `session_id` directly. Always search by `session_id`.
- **Avoid `&` for detached CLI on Windows.** `nohup ... &` does not work under MSYS; use `Start-Process` (PowerShell) or a Scheduled Task to launch the hub headless.

## Verification

Probe one bot and confirm a reply lands in its Bot Chat:

```
hermes -p job-seeker chat --in ~ -c "Bot Chat" -Q -q "a2a_verify_$(date +%s)"
```

Then `session_search(profile="job-seeker", query="a2a_verify")` should show the bot's acknowledgement. If the hub is used, `curl http://127.0.0.1:9123/status` must list your bots with `"bot_mode":true`.
