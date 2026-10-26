---
name: tailscale-centric-service-migration
description: Migrate Hermes services to Tailscale with rollback gates.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Tailscale, Hermes, Windows, Rollback, Operations]
---

# Tailscale-Centric Hermes Service Migration

This workflow migrates Windows-hosted Hermes services toward Tailscale Serve while preserving public webhook ingress and a rollback path. It does not prove boot recovery merely by creating scheduled-task definitions, and Tailscale Serve is not a replacement for a public HTTPS endpoint such as a LINE webhook. Invoke PowerShell through the `terminal` tool; inspect and edit artifacts with `read_file`, `search_files`, `patch`, and `write_file`.

## When to Use

- Centralizing Hermes service ingress on Tailscale Serve.
- Reducing Ngrok usage without changing a production route prematurely.
- Adding local, private-ingress, and public-ingress health gates.
- Registering Windows boot/logon startup for Hermes services.
- Preparing a reversible service or tunnel cutover.

## Prerequisites

- Windows PowerShell and authenticated Tailscale with `tailscale.exe` available.
- Current local ports, bindings, health endpoints, and dependency order.
- Existing Ngrok configuration when a public webhook is required.
- Administrator access for boot-level Task Scheduler changes.
- A writable snapshot directory and redaction policy. Never place API keys, tokens, passwords, OAuth secrets, or private keys in snapshots or logs.
- Inspect project instructions and existing launchers with `read_file` before modification.

## How to Run

Invoke scripts through the `terminal` tool using absolute Windows paths. Run `VerifyOnly` before changing routes, then configure idempotently and verify again. Use `-ShowVerbose` for diagnostics; do not name a parameter `$Verbose`, because PowerShell reserves that preference variable.

Canonical scripts:

- `%USERPROFILE%\Documents\New project\hermes-agent\scripts\windows\Manage-HermesTailscaleServe.ps1`
- `%USERPROFILE%\Documents\New project\hermes-agent\scripts\windows\Test-HermesTailscaleHealth.ps1`
- `%USERPROFILE%\Documents\New project\hermes-agent\scripts\windows\Register-TailscaleCentricHermesAutostart.ps1`

## Quick Reference

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<repo>\scripts\windows\Manage-HermesTailscaleServe.ps1" -Action VerifyOnly -ShowVerbose
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<repo>\scripts\windows\Manage-HermesTailscaleServe.ps1" -Action Configure -WaitSeconds 10
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<repo>\scripts\windows\Test-HermesTailscaleHealth.ps1" -CriticalOnly -ShowVerbose
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<repo>\scripts\windows\Test-HermesTailscaleHealth.ps1" -ShowVerbose
```

Representative targets:

```text
/                     -> http://127.0.0.1:8787
/v1                   -> http://127.0.0.1:8080/v1
/memory-graph         -> http://127.0.0.1:8765
/personal-line-health -> http://127.0.0.1:9102/health
/personal-line-reply  -> http://127.0.0.1:9102/reply
/line                 -> http://127.0.0.1:8646/line
```

## Procedure

1. **Inventory before mutation.** Use `read_file` and `search_files` to inspect launchers, scheduled tasks, startup entries, Tailscale Serve state, Ngrok configuration, logs, ports, bindings, PIDs, and external routes. Mark unknown values `NOT VERIFIED`; do not infer them.

2. **Capture a redacted rollback snapshot.** Invoke snapshot commands through `terminal` and save service/task/route/listener state under a timestamped directory. Preserve old Ngrok routes and task definitions. Record secret presence only. Completion gate: every planned mutation has a restorable state record.

3. **Classify services.** Use:
   - `TailnetInternal`: local origin plus Tailscale Serve and HTTPS health.
   - `ExternalIngress`: public webhook origin requiring Ngrok or another approved public tunnel.
   - `OptionalDevelopment`: non-critical service that may be stopped.

   Do not make an `ExternalIngress` failure disappear by excluding it from `-CriticalOnly`; report local-origin, tunnel-process, and public-endpoint gates separately.

4. **Design routes without cutover.** Define one route map and target per path. Keep old public ingress enabled while Tailscale routes are tested. Do not disable legacy Ngrok, gateway, dashboard, or Hypura tasks without explicit per-task approval and a tested replacement.

5. **Validate scripts first.** Run PowerShell syntax validation and the management script's `VerifyOnly` or dry-run path. Inspect stderr and exit code. Unexpected stderr means the script is not verified.

6. **Configure Tailscale Serve idempotently.** Invoke `Manage-HermesTailscaleServe.ps1 -Action Configure` through `terminal`, with propagation wait. Confirm every expected route maps to its intended local target; a partial route listing is not success.

7. **Start in dependency order.** Start Tailscale, local origins, memory/data services, application/API services, the LINE worker and reply service, then the public tunnel. After each stage inspect logs, processes, ports, and the next dependency. Avoid duplicate workers and duplicate Ngrok endpoints.

8. **Verify three planes independently.** Check local origin port/health, private Tailscale route/HTTPS, and public ingress tunnel/process/URL/local webhook origin. A Tailscale `200` proves tailnet reachability only.

9. **Register autostart after verification.** Invoke the registration script with elevation. Query every expected Task Scheduler entry and record state, trigger, run-as identity, and last-run result. If elevation times out or state cannot be observed, mark autostart `NOT VERIFIED`.

10. **Perform restart evidence.** A task definition is not boot-recovery evidence. After an approved reboot, verify dependency order, routes, local ports, private HTTPS, and public webhook delivery. Separate observed results from intended configuration.

11. **Rollback on a failed critical gate.** Stop only newly introduced processes, restore route/task state from the snapshot, re-enable the approved public path, and rerun all verification planes. Preserve the pre-change snapshot.

12. **Write an implementation log.** Use `write_file` under workspace `_docs` with requirements, changes, commands, observed results, unresolved gates, rollback location, and residual risk. Use statuses `PASS`, `FAIL`, `NOT RUN`, and `NOT VERIFIED`.

## Pitfalls

1. Tailscale Serve is private ingress; it cannot satisfy a third-party public webhook requirement by itself.
2. If local webhook port `8646` is not listening, a public tunnel cannot deliver successfully. Test origin, tunnel process, and public URL independently.
3. Do not use `$Verbose` as a parameter; rename it to `$ShowVerbose`.
4. `Get-NetTCPConnection` may miss listeners in this Windows environment. Use `Test-NetConnection -ComputerName 127.0.0.1 -Port <port>` for reachability, while recording actual bindings separately.
5. Some endpoints return `501 Not Implemented` to `HEAD`. Catch HEAD failures and fall back to `GET`; accept only the intended status range.
6. Windows PowerShell does not support every modern expression form. Avoid `exit (if (...) { 0 } else { 1 })`; use ordinary `if/else` followed by `exit 0` or `exit 1`.
7. If direct `ConvertFrom-Json` on Tailscale process output fails, write raw output to a temporary file, parse it, and clean up without logging secrets.
8. Unexpected stderr is not benign noise. `VariableNotWritable Host` is a real PowerShell defect; rename the colliding variable and rerun cleanly.
9. A configured route to a stopped optional service is `route PASS`, `origin FAIL`, not overall success.
10. Do not disable legacy tasks by wildcard; preserve existing production/public paths until explicit cutover approval.
11. Do not expose endpoint credentials or tokens; use `<tailnet-name>.ts.net` and `[REDACTED]`.
12. A timed-out elevated command is not success. Query resulting state; otherwise mark it `NOT VERIFIED`.
13. Do not claim all services are healthy from a critical-only probe. Run full classification separately and report optional and external-ingress failures.

## Verification

Run through the `terminal` tool and require exit code `0`, no unexpected stderr, and `CriticalServicesOk: true`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<repo>\scripts\windows\Test-HermesTailscaleHealth.ps1" -CriticalOnly -ShowVerbose
```

Then separately verify the approved public webhook URL, its local origin, and every expected scheduled task. Migration is complete only when all applicable gates are `PASS`; otherwise report exact `FAIL`, `NOT RUN`, or `NOT VERIFIED` gates and preserve rollback evidence.
