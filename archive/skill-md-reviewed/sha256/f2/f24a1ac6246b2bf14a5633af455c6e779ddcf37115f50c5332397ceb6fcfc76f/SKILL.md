---
name: vrchat-osc
description: Operate VRChat OSC chat, gestures, and movement safely.
version: 1.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [VRChat, OSC, Chatbox, Avatar, Movement]
---

# VRChat OSC Control

Use this skill to send authorized chatbox text and control documented avatar/input OSC parameters in VRChat. It does not establish that VRChat received a UDP packet merely because a local send returned success, and it must not invent avatar parameter names. The integration depends on `python-osc` and VRChat's OSC receiver being enabled.

## When to Use
- The user asks to send text to the VRChat chatbox.
- The user asks for a bounded gesture, avatar parameter change, or movement.
- A chatbox or avatar OSC action appears not to take effect and needs verification.

## Prerequisites
- VRChat is running and OSC is enabled in VRChat settings.
- `python-osc` is installed. In the repository environment, install with `uv pip install "hermes-agent[vrchat]"` if needed.
- Defaults in `tools/vrchat_osc_tool.py`: host `127.0.0.1`, send port `9000`, receive port `9001`.
- Optional environment overrides: `VRCHAT_OSC_HOST`, `VRCHAT_OSC_SEND_PORT`, `VRCHAT_OSC_RECV_PORT`.
- Public chatbox text requires an explicit user-provided or user-approved message. Movement should have a clear, bounded direction/duration or destination, especially in a populated world.

## How to Run
Use the native VRChat OSC tools when exposed. Otherwise use `execute_code` from the repository environment to import `tools.vrchat_osc_tool`; use `computer_use` to inspect VRChat and verify visible effects. Do not use an unverified `success` return as proof that a public action appeared in-world.

## Quick Reference
- Chatbox: `/chatbox/input` with `text`, `sendImmediately`, optional notification bool; limit 144 characters.
- Typing indicator: `/chatbox/typing` with a bool.
- Avatar parameter: `/avatar/parameters/{name}` with bool, int, or float matching that parameter's type.
- Movement axis: `/input/Vertical` float `1` forward, `-1` backward; reset to `0` immediately after a bounded pulse.
- Movement buttons: `/input/MoveForward`, `/input/MoveBackward`, `/input/MoveLeft`, `/input/MoveRight`; send integer `1` to press and `0` to release.
- Local helper: `vrchat_status()`, `vrchat_chatbox(text, immediate=True)`, `vrchat_avatar_param(name, value)`, `vrchat_send_osc(address, args)`.

## Procedure
1. **Inspect first.** Confirm the target VRChat window/process and capture the current screen with `computer_use(action="capture", mode="vision", app="VRChat.exe")`. Note current avatar/world context; don't infer that a floating label is the local chatbox without checking.
2. **Check prerequisites, not just ports.** `vrchat_status()` reports local socket usability; it is not an end-to-end acknowledgement and does not prove that OSC is enabled or that VRChat applied a message. Check OSC is enabled in the client if actions fail.
3. **Send only approved text.** Keep it within 144 characters. The helper's `immediate=True` maps to the chatbox's send-immediately flag. In the current implementation it sends `/chatbox/input` with `[text, immediate, False]`; the final `False` suppresses notification sound. Its `{"success": true}` means the local UDP send call did not raise, not that the client displayed or delivered the message.
4. **Verify in the client.** Capture the VRChat window after sending and check that the displayed text changed. If it did not, do not blindly resend. Check OSC enablement, configured host/port, and the current VRChat window. Use UI typing only if the user has authorized that and the required focus change is acceptable; explain when foreground interaction will disrupt another window.
5. **Use known avatar parameters only.** Read the current avatar's generated OSC config under `LocalLow/VRChat/VRChat/OSC/<userId>/Avatars/<avatarId>.json` or consult creator documentation. Names such as `Happy`, `Smile`, or `GestureWave` are not universal and a successful UDP send cannot establish that a parameter exists.
6. **Keep gestures bounded.** Use the actual parameter's documented type/value. Do not assume `VRCEmote=1` means a wave for every avatar. If a gesture repeats or sticks, send the documented neutral/release value once (for the built-in emote trigger, try integer `0`), then visually verify. Stop issuing control values if it persists and ask the user to intervene.
7. **Keep movement bounded and fail-safe.** Send one short, user-authorized axis/button pulse, then send the corresponding zero/release immediately. Verify the scene before another pulse. Never leave an axis or button held at its active value.
8. **Report evidence accurately.** Distinguish “OSC send attempted,” “client screen visibly updated,” and “other users' delivery confirmed.” Do not claim the last unless the platform provides evidence.

## Pitfalls
- OSC uses unacknowledged UDP. A socket probe or `success: true` is not proof of VRChat receipt.
- VRChat's official chatbox OSC form is `/chatbox/input s b n`: `b=True` sends immediately; `b=False` opens and fills the keyboard; optional `n=False` suppresses notification sound.
- The repository helper rejects empty text, so its `vrchat_chatbox_clear()` wrapper, which calls it with an empty string, cannot clear the box as currently implemented. Don't claim it cleared the chatbox.
- Parameter lists are avatar-specific. A generated OSC config can be inspected locally, but do not print or expose unrelated identifiers when reporting results.
- Game input may not accept background keyboard events. Follow the `computer_use` verdict; don't retry an unverified action repeatedly or foreground the app without user authorization.

## Verification
After any chatbox, gesture, or movement action, take a fresh `computer_use` capture of the VRChat window and report only the effect visible there; if no visible confirmation exists, state that the OSC packet was sent but the effect remains unverified.

## References
- VRChat OSC as Input Controller: https://docs.vrchat.com/docs/osc-as-input-controller
- VRChat OSC Avatar Parameters: https://docs.vrchat.com/docs/osc-avatar-parameters
- Implementation inspected: `tools/vrchat_osc_tool.py`