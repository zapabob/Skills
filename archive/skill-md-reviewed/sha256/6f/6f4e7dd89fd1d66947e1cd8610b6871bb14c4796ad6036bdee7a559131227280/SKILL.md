---
name: hermes-gateway-operations
description: Operate and troubleshoot Hermes messaging gateway services safely from LINE/Telegram/Discord/API contexts, including start/stop/restart boundaries, service status checks, and user-facing reporting.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, gateway, messaging, service-management, troubleshooting]
---

# Hermes Gateway Operations

Use this skill when the user asks to start, stop, restart, inspect, or troubleshoot the Hermes Gateway or messaging-platform delivery from inside a gateway chat such as LINE, Telegram, or Discord.

## Bot naming

When the user wants the Hermes bot to present as a specific name across Telegram/Discord/LINE while keeping a separate CLI persona skin:

- Telegram managed-bot default name is controlled in two places:
  - `telegram_managed_bot.py`: `DEFAULT_BOT_NAME`
  - `web_server.py`: `/api/messaging/telegram/onboarding/start` fallback `body.bot_name`
- Dashboard/web UI onboarding uses the same backend fallback.
- CLI persona display is controlled by the active skin's `branding.agent_name`; this is independent from the bot account name and should be left alone unless the user explicitly asks to change the persona.

Preferred pattern:
- Set bot-visible name to `Hermes` in `telegram_managed_bot.py` and `web_server.py`.
- Keep persona skin such as `hakua` unchanged, so CLI still shows `はくあ (Hakua)`.

## Core rule

Gateway control commands may behave differently depending on where they are run:

- From an outside shell: `hermes gateway stop`, `hermes gateway restart`, and `hermes gateway status` are normal service-control commands.
- From inside the running gateway process: stopping the gateway can be blocked by a safety guard to prevent restart loops and self-termination from a message handler.

If a gateway stop/restart command is requested from a messaging chat, try the direct command only when appropriate, but report the actual output honestly. If Hermes refuses because the command is being run inside the gateway process, tell the user to run the same command from a PC terminal outside the gateway.

## Safe workflow

1. Identify that the request concerns Hermes Gateway service control.
2. Prefer official CLI commands:
   - `hermes gateway status`
   - `hermes gateway stop`
   - `hermes gateway restart`
   - `hermes gateway start`
3. If executing from inside a gateway channel and the command refuses self-stop, do not bypass the guard with process killing unless the user explicitly asks for an external/OS-level shutdown path.
4. Reply with the exact practical next step, usually:
   - `hermes gateway stop` from Git Bash / terminal outside the gateway
   - `hermes gateway restart` from Git Bash / terminal outside the gateway
5. Keep the explanation short on LINE because LINE renders Markdown literally and has tight bubble limits.

## Pitfalls

- Do not claim the gateway was stopped unless the tool output confirms it.
- Do not treat Bitwarden/secret warnings printed before a command as the cause unless the final error says so. For example, a missing `BWS_ACCESS_TOKEN` warning can appear before a self-stop refusal; the refusal is the operative blocker for gateway shutdown.
- Do not modify protected bundled skills such as `hermes-agent`; record local operational additions here instead.

## References

- `references/inside-gateway-stop-guard.md` — observed self-stop refusal transcript and recommended response pattern.
