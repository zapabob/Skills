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

## Photon / iMessage quick triage

When `hermes photon setup` succeeds but iMessage gets no reply:

1. Do not stop at `hermes photon status`; also confirm the gateway log contains `✓ photon connected`.
2. If Photon is absent from startup logs, enable the bundled platform plugin and restart:
   ```bash
   hermes plugins enable photon-platform
   hermes gateway restart
   ```
3. If `✓ photon connected` is present but no inbound lines appear after the user sends blue iMessage bubbles, treat it as a Photon/Spectrum routing or shared-user issue before blaming the LLM.
4. If sidecar outbound testing logs `AuthenticationError: [spectrum-imessage] Target not allowed for this project`, distinguish:
   - `PHOTON_ALLOWED_USERS` = Hermes-side allowlist only.
   - Photon/Spectrum target authorization = cloud-side; local allowlists cannot override it.
5. For shared users, use Photon’s official redirect endpoint (`/users/<userId>/redirect?msg=...`) to initialize the conversation path, then retest.

See `references/photon-imessage-troubleshooting.md` for the full evidence-based workflow and escalation bundle.

## Pitfalls

- Do not claim the gateway was stopped unless the tool output confirms it.
- Do not treat Bitwarden/secret warnings printed before a command as the cause unless the final error says so. For example, a missing `BWS_ACCESS_TOKEN` warning can appear before a self-stop refusal; the refusal is the operative blocker for gateway shutdown.
- Do not assume `hermes photon setup` enables the runtime platform plugin. Verify `photon-platform` is enabled and the gateway connects Photon.
- Do not treat an unauthenticated sidecar probe returning `unauthorized` as a sidecar failure; sidecar endpoints require `X-Hermes-Sidecar-Token`.
- Do not modify protected bundled skills such as `hermes-agent`; record local operational additions here instead.

## References

- `references/inside-gateway-stop-guard.md` — observed self-stop refusal transcript and recommended response pattern.
- `references/photon-imessage-troubleshooting.md` — Photon setup succeeds but iMessage has no reply; plugin enablement, sidecar checks, shared-user target authorization, and support escalation details.
- `references/photon-imessage-no-reply.md` — Photon/iMessage setup-success-but-no-replies diagnostic: enable `photon-platform`, restart gateway, verify sidecar/connect logs, and check allowlist safely.
