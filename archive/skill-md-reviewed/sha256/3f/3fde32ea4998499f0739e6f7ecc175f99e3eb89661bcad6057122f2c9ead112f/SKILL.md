---
name: windows-hermes-runtime-restart
description: Use when the user asks to restart Hermes on this Windows PC, especially if they mention Desktop, ngrok, Tailscale, Gateway, WebUI, live health verification, or making Hermes auto-start on boot/logon.
argument-hint: "[repo-path]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Windows Hermes Runtime Restart

## When to use

Use this when the user wants an operational Hermes restart on this Windows machine, especially in or around `%USERPROFILE%\Documents\New project\hermes-agent`.

Typical triggers:
- restart Hermes
- restart Hermes including Desktop
- bring Gateway/WebUI/Hypura/ngrok/Tailscale back
- switch to the canonical Hermes checkout and relaunch
- make Hermes auto-start on power-on or logon

Non-goals:
- repo code edits unrelated to runtime recovery
- broad process kills without PID inspection
- disabling approved tunnels unless the user asks for that

## Inputs / context to gather

1. Confirm the target checkout and current CLI resolution:
- expected canonical repo: `%USERPROFILE%\Documents\New project\hermes-agent`
- expected CLI: `.venv\Scripts\hermes.exe`

2. Inspect the existing launcher surfaces:
- `scripts\windows\start-hermes-gateway.ps1`
- `scripts\windows\start-hermes-webui.ps1`
- `scripts\windows\start-hermes-stack.ps1`
- `scripts\windows\restart-hermes-autostart-admin.ps1`
- `%USERPROFILE%\AppData\Local\HermesWebUI\Start-HermesWebUI.ps1`
- `%USERPROFILE%\AppData\Local\HermesWebUI\Start-HermesLineNgrok.ps1`
- `%USERPROFILE%\AppData\Local\HermesWebUI\Update-HermesTailscaleServe.ps1`

3. Inspect current live state before stopping anything:
- `Get-CimInstance Win32_Process` for Hermes-related commands
- `Get-NetTCPConnection` for ports `4040`, `8646`, `8787`, `9120`, `9121`, `18794`
- `hermes_cli.main gateway status`
- `hermes_cli.main harness status`
- If Cron is part of the incident, also check `hermes_cli.main cron status`

4. If Desktop history looks missing, verify state DB provenance before assuming loss:
- `%USERPROFILE%\.hermes\state.db`
- `%USERPROFILE%\AppData\Local\hermes\state.db`
- Compare session/message counts or integrity before relaunching Desktop from a different path

5. If Desktop is in scope, confirm CLI contract first:
- `hermes desktop --help`
- `hermes dashboard --help`

6. If boot/logon durability is in scope, inspect the current task and shortcut surfaces:
- `Get-ScheduledTask -TaskName 'Hermes*'`
- `Get-ScheduledTaskInfo` queried task-by-task for the relevant Hermes tasks
- `scripts\windows\start-hermes-desktop.ps1`
- `scripts\windows\restart-hermes-autostart-admin.ps1`
- `scripts\create-hermes-desktop-shortcuts.ps1`
- `%USERPROFILE%\Desktop\Hermes.lnk`
- `%USERPROFILE%\Desktop\Hermes Agent\Hermes Desktop.lnk`

## Procedure

1. Verify canonical source and runtime-home split.
- Treat `%USERPROFILE%\Documents\New project\hermes-agent` as the source checkout.
- Treat `%USERPROFILE%\.hermes` as runtime home/config unless live evidence says otherwise.

2. Inventory live processes and listeners.
- Record Hermes-related PIDs before restart.
- Do not assume one PID per surface.

3. Stop only the explicit runtime surfaces in scope.
- Prefer targeted PID or command-line selection.
- Avoid broad `Stop-Process` filters that can catch the verification shell or unrelated Python jobs.

4. Before relaunching a Python-backed managed service, run its import contract.
- In the repo venv, import `pydantic`, `pydantic_core`, `fastapi`, and `uvicorn` before assuming a source/runtime issue.
- If `hermes serve` exits before binding with `ImportError: cannot import name '__version__' from 'pydantic_core'`, preserve dependency versions and repair only the locked binary package: `.venv\Scripts\python.exe -m pip install --no-deps --ignore-installed --only-binary=:all: pydantic-core==2.46.4`; re-run the import contract before restarting the watchdog.

5. Relaunch using existing launcher surfaces.
- Gateway: `scripts\windows\start-hermes-gateway.ps1`
- Harness: `hermes_cli.main harness start`
- WebUI: `%USERPROFILE%\AppData\Local\HermesWebUI\Start-HermesWebUI.ps1`
- ngrok: existing launcher or direct `ngrok http 8646 --url <approved-url>`
- Tailscale Serve: `%USERPROFILE%\AppData\Local\HermesWebUI\Update-HermesTailscaleServe.ps1`
- Dashboard: prefer `hermes dashboard --no-open --skip-build --port 9119` when `9120` is occupied, then verify with `hermes dashboard --status`
- Desktop: start from source; if `--source --skip-build` says workspace dependencies are missing, rerun without `--skip-build` instead of forcing the flag

6. If Desktop is included, quote Windows paths carefully.
- Both `--hermes-root` and `--cwd` must stay intact under `%USERPROFILE%\Documents\New project\...`.
- If the user asks for a launcher, run `scripts\windows\Retarget-HermesDesktopShortcut.ps1` and inspect `Desktop\Hermes.lnk` plus `Desktop\Hermes Agent\Hermes Desktop.lnk`; both must pass canonical `-HermesRoot` and `-HermesHome %USERPROFILE%\.hermes` to `start-hermes-desktop.ps1`.
- Never use `$home` as a local PowerShell variable: it collides with `$HOME`. Use `$hermesHomePath` and verify the saved shortcut arguments.

7. Verify each live surface after restart.
- WebUI: `http://127.0.0.1:8787/health`
- Gateway: `hermes_cli.main gateway status` and `%USERPROFILE%\.hermes\gateway_state.json`
- Harness: `hermes_cli.main harness status` and `http://127.0.0.1:18794/health`
- Dashboard: `hermes dashboard --status`, listener on the chosen port (`9119` or `9120`), plus process-command-line check
- Desktop helper dashboard: listener on `9121` when Desktop is active
- If packaged Desktop was rebuilt/relaunched, prefer the fresh `HERMES_BACKEND_READY port=...` line from `desktop.log` as the backend source of truth, then probe `http://127.0.0.1:<port>/api/status`
- ngrok: `http://127.0.0.1:4040/api/tunnels`
- Tailscale: `tailscale serve status`
- If the user wanted Hermes as a whole restarted, also verify the local secretary runtime with `scripts\windows\check-local-llm.ps1 -BaseUrl http://127.0.0.1:8080 -MinContext 64000`
- If Cron was part of the incident, verify `hermes_cli.main cron status` and the affected job's latest status after restart.
- If Desktop history was the symptom, re-check that the active Desktop is using the canonical `.hermes`-backed state, not the stale AppData packaged path.
- For canonical packaged Desktop proof, record the build stamp plus the exact `apps\desktop\release\win-unpacked\Hermes.exe` path; a successful build or a process alone is insufficient.
- For a shortcut/restart request, also prove an actual visible, responsive Win32 window with title `Hermes`; Electron can start hidden.
- When cognitive memory/embeddings are in scope, verify both `http://127.0.0.1:8082/v1/embeddings` (real non-zero vectors) and `http://127.0.0.1:8080/v1/chat/completions` (enough output budget for final content). Record generation command-line context such as `-c 131072` when the user specified it.
- For the current full-stack script, use `& .\scripts\windows\restart-hermes-stack.ps1 -StartLlama -StartGoWatchdog -SkipTunnels -WaitModelsSeconds 300` when those exact surfaces are requested. Independently probe `8080/health`, `8082/health`, `8787/health`, `9120`, `9920/health`, and harness `18794`; inspect listeners as a separate proof layer. If the script says `Using existing Go watchdog exe (skip rebuild)`, report a restart only, not a rebuild.
- If a helper collects Windows subprocess output into JSON, force `encoding="utf-8", errors="replace"` and call `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` before emitting JSON; default `cp932` decoding can make a healthy stack look like a verification failure.

8. If auto-start was requested, align durability surfaces to the canonical checkout.
- Treat `%USERPROFILE%\Documents\New project\hermes-agent` as the intended source checkout.
- Verify the boot tasks (`HermesGatewayBootAutoStart`, `HermesHypuraHarnessBootAutoStart`, `HermesLineNgrokBootAutoStart`, `HermesWebUIBootAutoStart`, `HermesDashboardBootAutoStart`, `HermesTailscaleServeBootUpdate`) and the logon tasks (`HermesGatewayAutoStart`, `HermesHypuraHarnessAutoStart`, `HermesLineNgrokAutoStart`, `HermesWebUINativeAutoStart`, `HermesDashboardAutoStart`, `HermesDesktopAutoStart`, `HermesTailscaleServeUpdate`) one by one.
- Ensure `scripts\windows\start-hermes-desktop.ps1` clears stale packaged `%USERPROFILE%\AppData\Local\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe` processes before launching source Electron.
- Ensure `scripts\create-hermes-desktop-shortcuts.ps1` owns both the Desktop-root `Hermes.lnk` and the `Desktop\Hermes Agent\Hermes Desktop.lnk` launcher path so regeneration does not drift back to the old packaged binary.
- Inspect `HermesGoWatchdogBootAutoStart` separately when the Go watchdog owns the managed backend. If its action targets an old worktree and task modification is access denied, do not create a replacement task or bypass elevation: report current-session health separately from unverified next-boot behavior and require administrator-authorized update plus reboot proof.
- For the canonical-main reconciliation contract, use `scripts\windows\repair-hermes-autostart.ps1 -VerifyOnly` before and after repair, and `-StartNow` only after approved registration. The verified current set is `HermesGoWatchdogBootAutoStart`, `HermesGatewayBootAutoStart`, `HermesHypuraHarnessBootAutoStart`, `HermesMemoryGraphBootAutoStart`, `HermesDashboardBootAutoStart`, `HermesDesktopAutoStart`, `HermesDashboardAutoStart`, and `HermesMemoryGraphAutoStart`; reject any legacy `hermes-agent-hakua-production` action reference.

## Efficiency plan

- Read the launcher scripts and CLI `--help` output once, then reuse that contract through the restart.
- Use ports and state files as the main proof surface instead of repeated blind relaunch attempts.
- If the user explicitly includes Desktop, include it in the first restart pass rather than doing Gateway/WebUI first and revisiting later.
- Read each shortcut once after retargeting; do not retry launcher creation blindly when process existence is the only evidence.
- If the user explicitly includes Desktop and webui together, treat them as one operational bundle and resolve shared port/process drift in the same pass.
- If the symptom is missing Desktop history, compare the two state DB locations before spending time on speculative data-loss recovery.
- If the user also asks for durability, verify the existing registered task state directly before spending time on the UAC wrapper path.
- Treat wrapper exit, independent endpoint health, clean build stamp, and scheduled-task target as separate acceptance dimensions; a fixed WebUI readiness timeout can make the wrapper fail even after services become healthy.
- Stop once the expected ports, status commands, and tunnel checks all agree.

## Pitfalls and fixes

- Symptom: `http://127.0.0.1:8646/health` fails.
- Likely cause: Gateway does not expose the health shape expected there.
- Fix: use `hermes_cli.main gateway status` and `%USERPROFILE%\.hermes\gateway_state.json` instead.

- Symptom: Desktop launch fails or splits the repo path.
- Likely cause: PowerShell argument tokenization under a path with spaces.
- Fix: use the exact `--source --skip-build --hermes-root "<repo>" --cwd "<repo>"` form with carefully quoted paths.

- Symptom: `dashboard --status` looks noisy or ambiguous.
- Likely cause: multiple dashboard-related helper processes.
- Fix: pair status output with the `9120` listener and process-command-line inspection.

- Symptom: Desktop backend checks hit the wrong port or `/` returns 404.
- Likely cause: a stale `HERMES_DASHBOARD_READY` line was reused, or the root path was treated like the health probe.
- Fix: route to the fresh `HERMES_BACKEND_READY` line for packaged Desktop and verify `/api/status` instead of `/`.

- Symptom: dashboard startup fails even though Hermes is already partly alive.
- Likely cause: `9120` is occupied by an unrelated service.
- Fix: inspect listeners first and use `9119` as the verified fallback port.

- Symptom: the Desktop keeps reopening from an AppData packaged path.
- Likely cause: stale `%USERPROFILE%\AppData\Local\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe` is still alive or the shortcut still targets it.
- Fix: kill that exact packaged path, then verify `start-hermes-desktop.ps1` plus both owned `.lnk` targets point back to the canonical source launcher.

- Symptom: `hermes desktop --source --skip-build` fails immediately.
- Likely cause: workspace dependencies are not installed for the source Desktop path.
- Fix: rerun without `--skip-build` and let Desktop install/build normally.

- Symptom: Desktop history looks gone after restart.
- Likely cause: Desktop is pointing at the stale AppData-local install/state instead of the canonical `%USERPROFILE%\.hermes` user home.
- Fix: compare `%USERPROFILE%\.hermes\state.db` against `%USERPROFILE%\AppData\Local\hermes\state.db`, then relaunch from the canonical source path.

- Symptom: `npm run pack` fails with `EBUSY: resource busy or locked` for `apps\desktop\release\win-unpacked`.
- Likely cause: the prior unpacked target `Hermes.exe` holds the output directory.
- Fix: enumerate processes and stop only ones whose executable path exactly matches that target; rerun the pack command. A process with title `Hermes`/`Responding=True` is still not proof that a reported auth prompt has been reached or understood.

- Symptom: user reports an unexpected passkey/auth prompt while Desktop starts.
- Likely cause: could be a browser/provider prompt; enabled OAuth MCPs can emit `OAuthNonInteractiveError`, but that is not conclusive passkey evidence.
- Fix: capture prompt title/text or a screenshot and correlate browser/auth processes. Inspect profile-scoped token storage without exposing credentials; disable/park optional OAuth MCPs or run `hermes mcp login <server>` interactively only when the provider is actually required.

- Symptom: scheduled-task or dense inline PowerShell inspection errors with `An empty pipe element is not allowed.`
- Likely cause: brittle pipeline composition.
- Fix: rewrite the check as a loop with an intermediate array.

- Symptom: the elevated auto-start registration wrapper appears to stall or finish unclearly under UAC.
- Likely cause: the elevation wrapper did not provide a trustworthy completion signal.
- Fix: inspect the already-registered Hermes scheduled tasks directly and verify their task info instead of trusting the wrapper alone.

- Symptom: a restart wrapper exits 1 on the first `8787/health` check, but later WebUI/Dashboard/Harness requests pass.
- Likely cause: the script uses a fixed readiness timeout that elapsed during startup.
- Fix: retain the nonzero wrapper exit in the report, then independently verify each in-scope endpoint and do not change the script merely to mask the timeout.

- Symptom: a short chat probe returns empty content after a generation restart.
- Likely cause: model reasoning consumed the small token budget.
- Fix: retry with a sufficiently large `max_tokens` and distinguish `finish_reason=length` from a transport/model failure.

- Symptom: the watchdog launches but the managed backend exits before its listener binds.
- Likely cause: a partial `pydantic_core` binary installation in the repo venv.
- Fix: run the import contract, reinstall only the lockfile-pinned `pydantic-core` wheel with `--no-deps --ignore-installed --only-binary=:all:`, verify imports, then relaunch. Do not broadly upgrade dependencies during an operational repair.

- Symptom: restart kills a user-approved tunnel.
- Likely cause: the restart treated every exposure as disposable.
- Fix: preserve or restore approved ngrok/Tailscale surfaces unless the user explicitly asked to disable them.

- Symptom: Gateway still fails after the restart pass.
- Likely cause: a real runtime blocker surfaced during reconnect or slash-command sync.
- Fix: inspect the active traceback and keep going until the blocker is removed; on this machine a Discord adapter constant regression was a real restart blocker, not just log noise.

## Verification checklist

- `hermes` resolves to the intended repo venv if source precedence was part of the task.
- WebUI `8787`, Gateway `8646`, Harness `18794`, Dashboard on the chosen port (`9119` or `9120`), and ngrok `4040` are live when they are in scope.
- Desktop helper `9121` is live when Desktop is in scope.
- `gateway_state.json` reports `gateway_state: "running"`.
- `tailscale serve status` still maps `/` to `8787` and `/line` to `8646/line` when Tailscale is in scope.
- `http://127.0.0.1:4040/api/tunnels` shows the approved ngrok tunnel when ngrok is in scope.
- If the user wanted the whole runtime recovered, `check-local-llm.ps1` passes against `http://127.0.0.1:8080`.
- If auto-start is in scope, the expected boot/logon tasks are registered and report sane per-task state, and both Desktop shortcuts target PowerShell plus the canonical `start-hermes-desktop.ps1` path.
- No unrelated repo changes were touched during the operational restart.
- If cognitive memory is in scope, `/v1/embeddings` returns the expected count of non-zero vectors and `/v1/chat/completions` produces final content with the requested generation context confirmed in the child command line.
- If a Python-backed managed service was restarted, the four-module import contract passed before final service proof.
- If Go watchdog boot autostart is in scope, its registered action points to the canonical checkout; otherwise explicitly mark next-boot behavior unverified.
- For a Scheduled Task reconciliation, every target is `Ready` with `LastTaskResult=0`, task actions contain the canonical checkout and no legacy root, and the started runtime has listener `9119` plus HTTP 200 on in-scope `8787`, `8765`, `9120`, `9123`, `9124`, and `18794`. Immediate start is not evidence of actual power-reboot triggering.
