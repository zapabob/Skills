# go-a2a-server-lifecycle Skill

Enable Hermes to build, start, verify, and register Go A2A server binaries with manual control mode. Covers the full lifecycle: build from source, verify `/status` endpoint, register startup via both PowerShell scheduled task and Windows startup folder, and ensure port conflict avoidance.

## When to Use
When initializing or reconfiguring Hermes A2A bot clusters that require Go-based hub and roundrobin servers to be built and set to auto-start.

## Prerequisites
- Go 1.22+ installed
- Repositories at `/c/Users/downl/go-a2a-servers/` with `go-a2a-hub/` and `go-a2a-roundrobin/` subdirectories
- PowerShell access for Windows task/shortcut registration
- Memory capacity above 21,500 chars (99% threshold) — clear if needed

## How to Run
1. Build hub: `cd "/c/Users/downl/go-a2a-servers/go-a2a-hub" && go build -o go-a2a-hub.exe .`
2. Build roundrobin: `cd "/c/Users/downl/go-a2a-servers/go-a2a-roundrobin" && go build -o go-a2a-roundrobin.exe .`
3. Start hub: `start /B "go-a2a-hub" "%USERPROFILE%\go-a2a-servers\go-a2a-hub\go-a2a-hub.exe"`
4. Verify status: `curl -s http://127.0.0.1:9123/status | grep heartbeat_intervals`
5. Register startup folder lnk (hub): `$shell.CreateShortcut($env:APPDATA + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\go-a2a-hub.lnk').TargetPath = '%USERPROFILE%\go-a2a-servers\go-a2a-hub\go-a2a-hub.exe'`
6. Register task scheduler (roundrobin): Use PowerShell `Register-ScheduledTask -TaskName 'go-a2a-roundrobin' -Action (New-ScheduledTaskAction -Execute '%USERPROFILE%\go-a2a-servers\go-a2a-roundrobin\go-a2a-roundrobin.exe') -Trigger (New-ScheduledTaskTrigger -Daily -At 09:05)`
7. Verify both registered: `schtasks /query /tn "go-a2a-hub" /query /tn "go-a2a-roundrobin"`

## Pitfalls
- **go: cannot find main module**: Always cd into the subdirectory with go.mod before building, not the parent
- **cd path syntax error**: Use `%USERPROFILE%\go-a2a-servers` (backslashes) or `/c/Users/downl/go-a2a-servers` (MSYS forward slashes) — not mixed or relative paths
- **schtasks -UserId invalid**: Use PowerShell `Register-ScheduledTask` with `-Principal` instead of `schtasks.exe -u` flag
- **Start-ScheduledTask file not found**: Ensure binary is built and path is correct before attempting to start
- **Startup shortcut not surviving reboot**: Verify the .lnk file is in the correct Startup folder and points to valid exe path
- **Port conflict**: job-seeker moved from 9901 to 9921 to avoid default 9901 collision — ensure all bot ports are reviewed before running
- **Memory at 99%**: If `MEMORY.md` shows 21,800+/22,000 chars, manually clear ~600 chars before running build scripts

## Verification
- Both binaries exist and are executable: `ls -la "/c/Users/downl/go-a2a-servers/go-a2a-hub/go-a2a-hub.exe"` and `ls -la "/c/Users/downl/go-a2a-servers/go-a2a-roundrobin/go-a2a-roundrobin.exe"`
- `/status` returns `{"heartbeat_intervals":[3600,10800]}` — confirms alternating 1h/3h intervals
- Scheduled tasks show `Ready` state: `schtasks /query /tn "go-a2a-hub" /query /tn "go-a2a-roundrobin"`
- Startup folder contains both .lnk files with correct exe targets

## Support Files
- `references/build-output.md` — captures actual build terminal output for reproducibility
- `references/status-check.md` — captures /status endpoint JSON for verification
- `scripts/register-startup.ps1` — PowerShell script to register both shortcut and scheduled task
- `scripts/verify-heartbeat.py` — Python script to poll /status and validate heartbeat intervals

---
*Note: This skill was created following successful completion of go-a2a-hub/go-a2a-roundrobin build + registration pipeline on 2026-08-21. Binaries built, /status verified with heartbeat_intervals [3600, 10800], and both startup registration methods (lnk + Task Scheduler) completed successfully.*