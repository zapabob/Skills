---
name: windows-local-service-ops
description: "Windows service ops: port zombies, env pollution, health."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [windows, service, ops, port, zombie, restart, irodori, line-bridge]
    related_skills: [line-personal-bridge, irodori-tts-windows-startup, hermes-gateway-operations]
---

# Windows Local Service Ops

## When to Use

- A local background service on this Windows box is down, crash-looping, or failing health checks
- The daily audit flags a service failure (LINE bridge, irodori-TTS, llama)
- `listen EADDRINUSE` appears repeatedly in a service log
- Launching a venv server from the Hermes shell and it crashes on import

Covers port-zombie recovery, MSYS/git-bash quirks, venv env pollution, and the launch → health-check pattern. The canonical per-service skills (`irodori-tts-windows-startup`, `line-personal-bridge`) live in the DEFAULT profile (`~/.hermes/skills/`) — read them for service internals; this skill is the generic recovery playbook that works from any profile.

## Service inventory (this box)

| Service | Port | Health probe | Launcher |
|---|---|---|---|
| Irodori-TTS | 8088 | GET /health | `.venv/Scripts/python.exe -m irodori_openai_tts` (server repo) |
| Personal LINE bridge worker | 9101 | GET /status | `start_personal_line_bridge.py` supervisor |
| Personal LINE reply server | 9102 | GET /health | same supervisor |
| Local llama server | 8080 | GET /v1/models | SuperGemma4-LlamaServer.vbs (Startup) |

## Port zombie recovery (EADDRINUSE crash loop)

Symptom: a service crash-loops with `listen EADDRINUSE: address already in use 127.0.0.1:<port>` (e.g. every 5 min in its log), or a watchdog keeps failing to bind.

1. Find the holder: `netstat -ano | grep <port> | grep LISTEN` → PID.
2. Identify it before killing: `wmic process where "ProcessId=<PID>" get Name,CommandLine`.
3. Kill it — **git-bash mangles Windows flags**: plain `taskkill //F //PID <PID>` fails with "Invalid argument/option". Use:
   `MSYS_NO_PATHCONV=1 taskkill /F /PID <PID>`
4. Confirm the port is free (TIME_WAIT remnants are harmless).
5. Restart via the service's normal launcher, then health-check.

## Launching venv servers from the Hermes shell

- **Never** use nohup/& wrappers — Hermes rejects them. Launch with `terminal(command=..., background=true)`, then probe health in a separate call after a short wait (model servers take ~20-30s).
- **Python environment pollution pitfall** — an inherited `PYTHONPATH` can make a server venv import another interpreter's packages, producing `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` even when the server's own dependencies are intact. Compare package origins under inherited and isolated environments before reinstalling anything. For a module installed in its own venv, launch `.venv/Scripts/python.exe -I -m <server_module>`: isolated mode ignores `PYTHONPATH`, `PYTHONHOME`, and user-site packages without mutating the parent. Irodori's shared PowerShell launcher uses this boundary. For source-only applications that require `PYTHONPATH`, explicitly construct the child environment rather than removing the parent's settings globally. Verify child package origins, health, and an actual request.
- Use the venv's own interpreter (`.venv/Scripts/python.exe`); bare `python` on this box is the MS Store stub — use `python3.12` for ad-hoc scripts.
- Always health-check after launch: curl the health endpoint AND confirm a LISTEN line on the port.

## Pitfalls

- **Detached Windows children can hold captured pipes open:** `subprocess.run(capture_output=True)` may wait for EOF after PowerShell has exited if `Start-Process` passes inherited handles to a persistent server. Even timeout cleanup can block inside `communicate()`. Confirm that the script exited and that the requested artifact was actually written before blaming slow inference. Capture wrapper stdout/stderr with `tempfile.TemporaryFile()` handles and decode them after the wrapper exits. Keep these handles outside the input `TemporaryDirectory`: ordinary named files in that directory may remain locked by the server and cause `WinError 32` during cleanup. A live regression should prove that the wrapper returns while the server still answers health. The test driver must use bounded `Popen.wait()` and clean up only its own synthetic server.
- A crash-loop with EADDRINUSE is almost always a zombie process holding the port; killing the holder fixes the loop — do not chase the crash itself.
- MSYS rewrites `/c/...`-style args too; prefix `MSYS_NO_PATHCONV=1` for any Windows-native flag/arg that must pass through verbatim.
- `skill_view` can't see default-profile skills from the secretary profile; read them via read_file at `%USERPROFILE%\.hermes\skills\...` when needed.

## Verified recipes

- `references/line-personal-bridge-recovery.md` — EADDRINUSE loop + QR re-link workflow.
- `references/irodori-launch-cpu.md` — PYTHONPATH-crash fix and verified CPU launch.
