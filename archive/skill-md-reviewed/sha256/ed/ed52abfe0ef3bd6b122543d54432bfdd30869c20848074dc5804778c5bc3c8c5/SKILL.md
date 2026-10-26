---
name: windows-daemon-bootstrap
description: Bootstrap Windows daemons for autostart and verify health.
version: 0.1.0
author: Hermes Agent
platforms: [windows]
metadata:
  category: devops
  tags: [windows, daemon, autostart, task-scheduler, startup, verification]
---

# Windows Daemon Bootstrap

Register a long-running Windows executable to start automatically at user login, then verify it became healthy through its HTTP health endpoint.

## When to Use

- A compiled binary (Go, Rust, Python, etc.) should start at user login
- Startup folder alone is insufficient and Task Scheduler registration is needed
- You need to verify the daemon reached a healthy state after launch

## Prerequisites

- The daemon must expose a health/status HTTP endpoint (e.g. `GET /status`)
- Admin rights are required for Task Scheduler registration (triggers UAC)
- The binary should be compiled and placed at a stable, known path

## How to Register

### Option A: Startup Folder (simple, no admin rights needed)

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$ps1 = "C:\path\to\daemon-launcher.ps1"
$startup = [Environment]::GetFolderPath("Startup")
$lnk = "$startup\MyDaemon-Launcher.lnk"

$Shortcut = $WshShell.CreateShortcut($lnk)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps1`" -YourSwitch"
$Shortcut.WorkingDirectory = Split-Path $ps1 -Parent
$Shortcut.Save()
```

Verify: `Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\MyDaemon-Launcher.lnk"`

### Option B: Task Scheduler (robust, requires admin)

```powershell
$taskName = "MyDaemon-AutoStart"
$ps1Path = "C:\path\to\daemon-launcher.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps1Path`" -YourSwitch"
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Remove old task if it exists to avoid conflicts
Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -User $env:USERNAME -Force -RunLevel Highest
```

**UAC note:** `Register-ScheduledTask` requires elevation. If the calling PowerShell is not admin, the call fails with access denied (0x80070005). Use a self-elevation wrapper script that calls `Start-Process -Verb RunAs`, or run the registration from an already-elevated session.

## How to Verify (one-shot — do NOT loop)

1. **Kill stale instances** on the daemon's port first:
   ```powershell
   # PowerShell
   Get-NetTCPConnection -LocalPort <PORT> -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
   ```
   ```bash
   # Bash (git-bash/MSYS)
   taskkill /F /IM <binary.exe> 2>/dev/null
   ```

2. **Start the daemon** (via Startup shortcut, Task Scheduler, or manually).

3. **Wait briefly**, then hit the health endpoint **once**:
   ```bash
   sleep 3 && curl -s http://127.0.0.1:<PORT>/status
   ```

4. **Check the specific field** that indicates healthy state (e.g. `heartbeat_intervals`, `mode`, `seed42`, etc.). If the expected field is present with the expected value, **declare done**. Do not re-curl repeatedly.

## Pitfalls

- **Port already in use:** A previous daemon instance may still be bound to the port. Always kill stale processes on the port before starting a new one, or the new instance will fail with `bind: Only one usage of each socket address`.
- **UAC hangs:** `Start-Process -Verb RunAs` from a non-interactive context may hang waiting for user approval. If running headless, pre-elevate or use a scheduled task configured to run with highest privileges.
- **Loop verification:** Re-calling `curl /status` in a loop after the first successful check is wasted work and creates false sense of ongoing verification. One successful check is enough — declare done.
- **Empty responses after tool calls:** If a tool call returns results, always process them and produce a meaningful summary. Never return an empty response after executing tools — the user needs to know what happened.
- **schtasks argument splitting:** When the `/TR` value contains spaces and switches (e.g. `-A2A /SC ONLOGON`), `schtasks` may misinterpret arguments. Prefer PowerShell `Register-ScheduledTask` for complex command lines with multiple switches.
- **PowerShell in bash:** When running PowerShell commands from a bash-based terminal (git-bash/MSYS), always invoke via `powershell -Command '<ps>'` or `powershell -File <path>`. Direct PowerShell cmdlets like `Get-ScheduledTask` will not resolve in bash.

## Verification Checklist

- [ ] Startup folder shortcut exists: `Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\<name>.lnk"`
- [ ] Task Scheduler task registered: `Get-ScheduledTask -TaskName "<name>" -ErrorAction SilentlyContinue`
- [ ] Daemon process is running: `Get-Process <binary> -ErrorAction SilentlyContinue`
- [ ] Health endpoint responds with expected fields: `curl http://127.0.0.1:<PORT>/status`

## References

- `references/task-scheduler-gotchas.md` — detailed schtasks vs Register-ScheduledTask comparison, UAC patterns, and argument-quoting rules