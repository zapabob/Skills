---
name: vrchat-troubleshooting
description: Diagnose and fix VRChat runtime, controller, OpenXR, OSC input, and Quest/Virtual Desktop problems on Windows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [VRChat, Quest, Virtual Desktop, OpenXR, SteamVR, troubleshooting, Windows]
---

# VRChat Troubleshooting

Use this skill when the user reports VRChat not entering VR mode, Quest/Quest 2 controllers not responding, hands not moving, OpenXR/SteamVR confusion, OSC input interfering with controls, or Virtual Desktop / Air Link / Link runtime issues.

## Operating stance

1. **Diagnose first, then change settings.** Prefer read-only evidence from logs, processes, OpenXR registry, and VRChat config before applying fixes.
2. **Close the app before destructive resets.** Stop VRChat/SteamVR before deleting bindings or changing runtime settings.
3. **Back up before deleting.** Binding/cache resets should copy or rename the old folder/file first.
4. **Separate PC-side fixes from headset-side steps.** The agent can patch registry/config and clear caches, but the user must relaunch from the correct headset flow.
5. **Avoid blaming Hermes/OSC too early.** OSC can interfere only if configured as an input controller; ordinary outbound OSC/chatbox usage is usually unrelated.

## Quest 2 + Virtual Desktop controller triage

For “Quest 2 controller does not respond in VRChat” on Windows:

1. Run the local doctor if available:
   ```bash
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/windows/vrchat_quest2_controller_doctor.ps1
   ```
2. Inspect these signals:
   - `virtual_desktop_running`
   - `steamvr_running`
   - `oculus_runtime_running`
   - `likely_in_vr` / `likely_desktop_or_headless`
   - VRChat log: `Oculus Touch controller = False`
   - VRChat log: `VRCInputProcessorOpenXR: can use OpenXR controller`
   - VRChat log: `Loaded Input Binding[_OPENXR_GENERIC]: Custom`
3. If using Virtual Desktop, prefer the Virtual Desktop OpenXR runtime for the user hive:
   ```bash
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/windows/vrchat_quest2_controller_doctor.ps1 -Fix -ResetBindings -OpenXrRuntime VirtualDesktop
   ```
   Note: HKLM writes require elevated PowerShell; HKCU often suffices for the current user.
4. Disable VRChat OSC input-controller mode when not intentionally using OSC for controls.
5. Reset/remove VRChat custom bindings if the log says `Custom` binding is loaded.
6. Patch/review Virtual Desktop Streamer settings only if the local helper supports it, and preserve the generated backup path.
7. Ask the user to restart Virtual Desktop Streamer from the tray if the agent cannot stop it due to access denial.
8. Headset-side relaunch is mandatory: **Quest headset → Virtual Desktop → Games tab → VRChat**. Do not launch VRChat from the desktop mirror Steam UI when debugging controller passthrough.
9. If still broken, isolate Virtual Desktop by testing USB Link/Air Link or launching through Oculus/Meta PC flow.

## User-facing summary format

Keep the report practical:

- “やったこと” — exact fixes applied and backup paths.
- “残っている手動操作” — headset/tray steps the user must do.
- “今の診断” — a few decisive signals, not a raw JSON dump.
- “次に試す順番” — launch path and reset steps.

## References

- `references/quest2-virtual-desktop-controller.md` — session-proven workflow and interpretation notes for Quest 2 + Virtual Desktop controller failures.
