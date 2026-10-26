---
name: vrchat-autonomous-15min
description: Monitor VRChat 15 minutes with OSC heartbeat and vision.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [VRChat, OSC, Autonomous, Monitoring]
---

# VRChat Autonomous 15-Minute Monitor

Run a bounded 15-minute autonomous watch over a running VRChat session. It verifies the VRChat process, checks OSC reachability, captures the world view with multimodal judgment, and emits heartbeat chatbox messages via OSC. Optionally routes text to Irodori TTS for voice, but falls back to chat-only when TTS is unavailable.

## When to Use
- User asks for a short autonomous watch in VRChat for a fixed duration.
- User wants heartbeat chat messages while monitoring world changes.
- User wants multimodal screen judgment before sending bounded OSC actions.

## Prerequisites
- VRChat is running (process `VRChat.exe`).
- OSC enabled in VRChat: send port 9000, receive port 9001, host 127.0.0.1.
- `tools/vrchat_osc_tool.py` available with `vrchat_status`, `vrchat_chatbox`.
- Optional Irodori TTS server on 127.0.0.1:8089 for voice fallback.
- `computer_use` available for screen capture of `VRChat.exe`.

## How to Run
Use `execute_code` to import `tools.vrchat_osc_tool` and verify status. Use `computer_use` action=`capture` with app=`VRChat.exe` and mode=`vision` for multimodal judgment. Send heartbeats with `vrchat_chatbox`.

## Quick Reference
- Status check: `vrchat_status()`
- Chatbox send: `vrchat_chatbox(text, immediate=True)`
- Screen capture: `computer_use(action='capture', app='VRChat.exe', mode='vision')`
- Irodori health: `http://127.0.0.1:8089/health`

## Procedure
1. Verify VRChat process via PowerShell `Get-Process -Name VRChat`.
2. Verify OSC reachability with `vrchat_status()`.
3. Capture VRChat window with `computer_use`.
4. Judge scene calmness / chat activity from vision analysis.
5. Send bounded heartbeat chat via `vrchat_chatbox` (max 144 chars).
6. Repeat steps 3-5 every ~30-60s for up to 15 minutes.
7. Stop after duration and report summary.

## Pitfalls
- OSC uses UDP; `success: True` means send attempted, not client display.
- TTS may be unloaded; fallback to chat-only.
- Do not invent avatar parameter names; use only documented OSC params.
- Movement should remain bounded or disabled unless explicitly authorized.

## Verification
After a heartbeat, capture VRChat again and confirm chat text appears in the speech bubble or nameplate area.