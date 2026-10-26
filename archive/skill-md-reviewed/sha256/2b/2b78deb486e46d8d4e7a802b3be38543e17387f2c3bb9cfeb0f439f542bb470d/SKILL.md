---
name: cron-runtime-reliability
description: Make Windows Hermes cron jobs reliable and verifiable.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Cron, Reliability, Windows, Providers, News, Verification]
---

# Cron Runtime Reliability

Use this class-level skill when a Hermes scheduled job appears successful but emits bad data, fails only under the scheduler, selects an unexpected provider, or breaks because the deployed runtime and source checkout disagree.

## Scope

This skill covers both no-agent scripts and LLM-driven cron jobs:

- interpreter and workdir drift on Windows;
- provider/model/fallback resolution;
- scheduler/core signature mismatches;
- deterministic external-data parsing;
- duplicate or partial upstream records;
- end-to-end execution and delivery verification.

For general Hermes CLI syntax, load `hermes-agent` first. For the older focused no-agent procedure, see `cron-diagnosis-and-repair` if it is available and curator-adopted.

## Reliability procedure

1. **Inventory the actual job.** Use `hermes cron list`, `hermes cron status`, and `hermes cron runs <job_id>` from the same checkout and venv that owns the job. Record schedule, `workdir`, `script`, `no_agent`, provider/model, delivery target, last status, and the exact error.
2. **Classify the failure layer.** Separate scheduler/core errors, interpreter/import errors, provider/model errors, script/data errors, and delivery errors. Do not patch a prompt for a parser bug or rotate providers for a broken import.
3. **Reproduce the deployed path.** Run the exact script or `hermes cron run <job_id>` with the same interpreter. On Windows, avoid `python3` installer redirectors; use the job's explicit `.venv\Scripts\python.exe` or the interpreter shown by the job.
4. **Inspect raw data before changing parsing.** For structured feeds, inspect one current raw record and one linked detail record. Identify duplicate event IDs, partial速報 records, units, casing, and update precedence.
5. **Patch the smallest durable layer.** Prefer the parser's selection/normalization logic for data-quality defects; prefer the job's interpreter/workdir for deployment defects; prefer the scheduler/runtime version for signature mismatches; prefer a supported plugin entry point for missing CLI commands.
6. **Check command ownership before repairing a wrapper.** Run the exact executable with `--help` or the failing subcommand. If the CLI reports `invalid choice` / an unavailable command, do not keep retrying, rotate providers, or patch around it. Find the currently registered plugin/tool entry point, or migrate the job to an agent cron that calls the supported tool. Apply this to every sibling job using the same wrapper, not only the reported job.
7. **Keep source and deployed copies aligned.** If a sync script declares the repository authoritative, patch the repository copy first, run the allowlisted sync, and then execute the deployed copy. A runtime-only fix will be overwritten on the next sync.
8. **For no-agent migrations, fail soft but truthfully.** When a deterministic wrapper depends on a removed CLI, either replace it with a supported deterministic implementation or switch to an LLM cron using the real tool. On data-collection failure, emit a sanitized "調査不能" report and exit 0 when notification continuity is preferable; never invent prices, facts, or URLs.
9. **Verify semantic output, not only exit code.** For a news job, assert that qualifying records have a real name, magnitude, depth, coordinates when supplied, event time, and source timestamp. For price/OSINT reports, require source URLs and explicit prices/facts; an exit code 0 with `不明` placeholders, fabricated values, or empty unsupported claims is not acceptance.
10. **Verify cron state and delivery separately.** Rerun the job, inspect the new execution record, and confirm the configured delivery target. `last_status: ok` proves execution, not Telegram/LINE/Discord delivery.
11. **Record residual risk.** Note fallback-provider use, dependency pin drift, unavailable optional plugins, and unverified delivery in the implementation log.

## JMA earthquake feed pattern

JMA `list.json` may publish several records for the same `eid`:

- `VXSE51`: intensity速報, often with empty `anm`, `mag`, and `cod`;
- `VXSE52`: hypocenter information;
- `VXSE5k`: earthquake and intensity information, normally the most complete record.

Deduplicate by `eid` while preferring `VXSE5k`, never simply taking the first matching record. In the current schema:

- `at` = event time;
- `anm` = hypocenter region;
- `mag` = magnitude;
- `maxi` = maximum shindo as an integer string (`1`–`7`);
- `cod` = `+latitude+longitude-depth_m/`.

Convert `depth_m` to kilometres for display. Use the linked detail JSON as a fallback and read the current PascalCase paths `Body.Earthquake.Hypocenter.Area` and `Body.Intensity.Observation`.

## LLM cron compatibility

- `run_conversation() got an unexpected keyword argument ...` indicates a scheduler/core API mismatch. Inspect the installed Hermes runner and checkout before changing the job prompt or model.
- A successful fallback run must report the actual provider/model selected. It does not prove the primary route is healthy.
- If a job invokes a removed command such as an old OSINT subcommand, locate the current plugin entry point or replace it with a supported deterministic script; do not fabricate a command.

## Dependency and runtime rules

- Check imports with the same Python executable used by the job. A package installed in system Python does not repair a project `.venv`.
- When a namespace-package import is broken, reinstall the package inside the owning venv, then verify the exact import. Check project pins afterward to avoid a later sync reverting the fix. For lm-twitterer's direct-import path, install into the job venv with `uv pip install --python <venv>/Scripts/python.exe 'twitter-openapi-python>=0.0.44,<0.1' 'tweepy-authlib>=1.7.3,<2'`, then verify imports with that same interpreter.
- Standalone scripts that load plugin modules with `importlib.util.spec_from_file_location()` must register the module in `sys.modules` before `exec_module()`; otherwise module-level dataclasses can fail during import. Prefer a normal package import when possible; otherwise use the registration pattern documented in `python313-dataclass-cron-fix`.
- Keep no-agent/cron stdout restricted to a safe status summary. Do not print tracebacks, raw candidate records, cookies, tokens, or environment values; include only counts and a sanitized message on failure.
- Do not treat transient missing credentials or binaries as a permanent feature limitation; capture the repair or the explicit residual risk.

## Verification boundaries

- Verify the changed script directly first: `git diff --check`, `py_compile` with the job interpreter, then one real smoke execution with the requested side-effect mode.
- Run the repository-wide test command only as a separate confidence check. If it fails on unrelated optional dependencies or pre-existing tests, report that boundary explicitly rather than presenting the cron smoke test as a full-suite pass.

## Acceptance checklist

- [ ] Job metadata and exact execution path recorded.
- [ ] Raw upstream record and duplicate/update precedence inspected.
- [ ] Parser or runtime fix exercised with real data.
- [ ] No placeholder fields remain when the source supplies values.
- [ ] Cron rerun has a new successful execution record.
- [ ] Delivery target checked independently.
- [ ] Fallback/provider/dependency residual risks documented.

## Global inference config drift (verified 2026-08-02)

### Symptom

Unpinned cron jobs skip silently with this error class:

```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted
since this job was created (model 'hakuapulse-orchestrator' -> 'hakuapulse-lite-free'),
and this job is unpinned. No inference call was made.
```

A second, related failure surfaces when the resolved model is set to a catalog
name that no longer exists, e.g. `HTTP 404: Model 'hakuapulse-lite-free' not
found. The requested model does not exist in our configuration or OpenRouter
catalog.` Aimed at the Nous inference API at `inference-api.nousresearch.com`.

### Root cause

When the global `model.*` config changes (provider swap, model rename, free-tier
rotation) without explicit pinning, the scheduler refuses to run unpinned jobs to
avoid silent unexpected spend. Pinning at job creation locks `provider` + `model`;
an unpinned job follows the current global config. See the in-app issue ref
`#44585`.

### Repair (CORRECTED 2026-08-03)

`cronjob action=update job_id=<id> provider=<p> model=<m>` does NOT pin the job.
The `update` action silently ignores `model`/`provider` (returns `No updates
provided` and leaves `model: null` in the listing). Do not rely on it — see
`references/2026-08-03-drift-repair-correction.md` for the evidence.

Two working approaches:

1. **Per-job recreate (fast, but fragile).** `cronjob pause <id>` then
   `cronjob create` with the SAME `prompt`/`schedule`/`workdir`/`skills`/`deliver`
   AND an explicit `model`+`provider`. At creation the scheduler snapshots the
   CURRENT global config, so the job runs as long as the global does not drift
   again. Verify with `cronjob run <new_id>`. This breaks again if the global is
   later rotated, so prefer approach 2.

2. **Durable global pin (recommended).** The drift is almost always caused by the
   **`Daily MoA Orchestrator Rotation`** cron (`script: daily_moa_orchestrator_rotation.py`,
   schedule `0 4,16 * * *`) rotating `moa.active_preset` between
   `hakuapulse-orchestrator` and `hakuapulse-lite-free`. Fix:
   - `cronjob pause` that rotation job first.
   - Pin the global with the real `hermes` executable (NOT the repo `.venv` — the
     install venv at `%USERPROFILE%\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes`
     is the one that has the `hermes` module; `~/.hermes/config.yaml` is
     agent-protected and cannot be `patch`ed):
     ```text
     hermes config set model.default hakuapulse-orchestrator
     hermes config set moa.default_preset hakuapulse-orchestrator
     hermes config set moa.active_preset hakuapulse-orchestrator
     ```
   - `hermes config set` warns that previously-unpinned jobs will now fail closed
     until recreated — that is expected; recreate them (approach 1) so their
     snapshot matches the now-stable global.
   - Leave the orchestrator-rotation cron paused unless every job is explicitly
     model-pinned (which `cronjob update` cannot do — see above).

3. **Cleanup.** Recreating jobs leaves the old `error`/`paused` originals and any
   accidental duplicates (e.g. `(pinned)` copies made during iteration). Remove
   them with `cronjob remove <old_id>` so `cronjob list` stays clean and no job
   double-runs.

### Auxiliary / MoA client failures (same date)

Two related failure classes appeared alongside the drift skips:

1. `agent.auxiliary_client: resolve_provider_client: unknown provider 'moa'` —
   the MoA loop asks auxiliary_client for a `moa` provider that the resolver does
   not know. Auxiliary then fails every MoA reference and aggregator call. This
   indicates the MoA fallback chain points at `provider: moa` in config but no
   concrete backing provider is registered — repair the auxiliary / MoA
   fallback config to point at real providers (`openai-codex`, `openrouter`,
   `nvidia`, etc.) rather than the abstract `moa` alias.
2. `openrouter: 403 Key limit exceeded (daily limit)` and
   `openai-codex: 429 usage_limit_reached (plan_type=prolite, resets_at=...)` —
   plan-level rate limits on the reference models. openrouter is marked unhealthy
   for 600s on payment/credit errors, openai-codex fails after 3 retries. These
   are account/quota states, not code defects: bump plan, wait for reset
   (`resets_at` epoch in the error body), or fail over to a different auxiliary
   provider in the configured chain. When all references fail the run falls back
   to aggregator-alone — report that degradation, do not pretend the reference
   review happened.

## MCP server connection parking (verified 2026-08-02)

Several MCP servers fail initial connection and are parked without retries:

- `world-intel`: permanent `FileNotFoundError [WinError 2]` — the configured
  command `%USERPROFILE%\Documents\New project\hermes-agent\.venv\Scripts\world-intel-mcp.exe`
  does not exist on disk. This is a deployment/path defect; either reinstall the
  package or remove the entry from `mcp_servers` config.
- `notebooklm-mcp`: `MCP server 'notebooklm-mcp' has no 'command' in config` —
  the entry is missing a `command` key entirely. Either add a real command or
  remove the entry.
- `blender`, `egov-law`: `Connection closed` after 3 attempts — uvx-based
  servers that need their underlying package installed or the spawned process
  is dying on startup. Inspect with `uvx --from <pkg> <module>` in a foreground
  shell to reproduce.

Parked servers stay parked for the rest of the session; dependent tools remain
unavailable. Do not treat a parked tool as a code defect on the caller side —
repair the MCP entry first.

## Unsupported CLI subcommand pattern

If a no-agent cron script calls a Hermes subcommand that the installed CLI does not register, do not keep retrying it. Either replace it with a supported deterministic implementation or migrate the job to a normal LLM-driven cron that calls the currently supported tool or plugin. Apply the fix to every sibling job using the same wrapper. Example failures seen in the wild:

- `invalid choice: 'warashibe'` — the installed CLI has no `warashibe` subcommand.
- `hermes worldmonitor-osint ...` / `hermes osint-agent ...` — these subcommands are absent from the current CLI.

Durable migration pattern:

1. Replace `no_agent=true` + `script=...` with `no_agent=false` and a self-contained prompt.
2. In the prompt, call the actual registered tool (`osint_agent_brief`, `web_search`, etc.).
3. On partial data failure, instruct the agent to emit a sanitized "調査不能" report and exit 0 rather than inventing values.
4. If the task class has reusable fallback routes, attach the matching skill, e.g. `skills: ["osint-fallback-routes"]`.

## OSINT / public-data fallback skill

For jobs that scrape or query official sites, PDFs, and public APIs, attach `osint-fallback-routes`. It encodes the standard retry order: official site → direct PDF URL → official X/note → e-Gov/GovAPI → third-party aggregators, plus failure tags for billing, rate limit, redirect loops, structure changes, PDF corruption, and auth walls.

## References

- `references/jma-duplicate-records.md` — the observed JMA duplicate-record failure and canonical field mapping.
- `references/cron-failure-classification.md` — symptom-to-layer triage table for Windows Hermes cron jobs.
- `references/unsupported-cli-migration.md` — how to diagnose obsolete Hermes subcommands and migrate no-agent wrappers durably.
- `references/automation-pattern-2026-08-02.md` — full automation session: 7 new cron jobs created, MoA round-robin orchestrator deployed, PR review fix delegation pattern established, monthly impact estimates.
- `references/2026-08-02-config-drift-and-mcp-parking.md` — full forensic capture of the global inference config drift skip (`hakuapulse-orchestrator` → `hakuapulse-lite-free`), the unknown `moa` auxiliary resolver, plan-level quota exhaustion, and MCP server parking (`world-intel`, `notebooklm-mcp`, `blender`, `egov-law`).
- `references/2026-08-03-drift-repair-correction.md` — CORRECTION: `cronjob update model=` does NOT pin (silent no-op); durable fix is pause the MoA rotation cron + global pin via `hermes config set` + recreate jobs.
- `references/2026-08-03-osint-cli-recovery.md` — evidence that `hermes worldmonitor-osint` and `hermes osint-agent` are absent from the current CLI, and the working LLM-cron migration using `osint_agent_brief`.
- `references/2026-08-03-warashibe-cli-recovery.md` — evidence that `hermes warashibe` is absent, and the replacement pattern using `web_search` with purchase/login/post prohibition.
