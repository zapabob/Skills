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
7. **Keep source and deployed copies aligned — in both directions.** If a sync script declares the repository authoritative, patch the repository copy first, run the allowlisted sync, and then execute the deployed copy. A runtime-only fix will be overwritten on the next sync. But the drift is not always repo-ahead: **diff the deployed copy against the repo copy** (`difflib`/`git diff --no-index`) before assuming which side is stale. The deployed wrapper may carry fixes the repository never received; when it is strictly better, sync it *back* into the repository. Both directions lose information if you assume one is always authoritative.
   When several copies of the same script exist (repo root, `scripts/standalone/`, a Desktop round-trip), consolidate to one canonical file and turn any public entrypoint into a shim — see `references/canonical-copy-consolidation.md` for the decision procedure and the two regressions a consolidating shim creates.
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

## Merge-dropped scheduler helper (`NameError: _job_needs_sequential_tick`)

A live gateway can look healthy while every cron tick dies with:

```
NameError: name '_job_needs_sequential_tick' is not defined
```

at `cron/scheduler.py` `tick()` after `get_due_jobs()`. A merge can leave the sequential/parallel partition **call site** while dropping the helper (and often its siblings `_execution_home_for_job`, `_cron_profile_guard`, `_cron_profile_context`, `_scripts_dir_for_job`). Recurring jobs then re-arm every minute (`cron.persisted_error.recovered`) but never fire.

Repair:

1. Confirm the names exist as `def` in `cron/scheduler.py`, not only as call sites.
2. Restore the helpers from the last good commit (`8d7d2e4718` in this fork) rather than inlining only the workdir check — named-profile jobs must also serialize.
3. Add/keep `tests/cron/test_cron_profile_isolation.py::test_job_needs_sequential_tick_for_workdir_or_named_profile`.
4. Restart the **running** gateway after the file change; the in-process ticker will not pick up the new `scheduler.py` until reload.

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

## Append-only log files destroyed by an LLM cron job (verified 2026-10-04)

### Symptom

A monthly log that cron has appended to for months suddenly contains **one
entry, dated today, and every prior entry is gone** — while the *current* month's
file is complete and correct. `git status` shows the old month file as modified
but **unstaged**, so nothing in history explains it and the damage looks
irreversible until you notice HEAD still has the content.

### Root cause class

An LLM-driven cron job reconstructed a monthly note from its own context instead
of appending. Two distinct defects combine:

1. **A literal date/period in the skill or prompt.** The skill said
   `Ebbinghaus/2026-08_睡眠ログ.md` where it must have said a derived
   `$(date +%Y-%m)`. A literal month is *correct on the day it is written* and
   silently wrong forever after — and it survives in
   `skills/.curator_backups/` snapshots, so re-loading the skill re-injects it.
2. **No write discipline in the job.** The prompt said "append", but nothing
   *enforced* append. The model read the note, produced a fresh copy from its
   own context, and wrote it back whole.

The tell is a **self-contradicting run log**: the same execution committed the
correct current-month file *and* separately wrote the stale literal path. Two
different code paths, one of which was a year-old lesson frozen into prose.

### Diagnosis order

1. `git status` in the log's repo. An unstaged `M` on a log file that cron owns
   is the finding — do not `git checkout` it yet.
2. Copy the damaged file aside **before any repair**, so the evidence survives
   even if the repair goes wrong.
3. `git log --oneline --all -- <file>` to prove the content exists in HEAD.
4. `git show HEAD:<file>` and diff mentally: is the loss real?
5. Find the guilty run: list `~/.hermes/cron/output/<job_id>/` and search the
   dated transcripts for literal period filenames. A run transcript embeds the
   *full skill text it loaded*, so the stale path is quoted verbatim there.
6. Confirm in the job store (`~/.hermes/cron/jobs.json`, shape
   `{"jobs": [...]}`) which job's `prompt` or `skills` still carries the literal.
7. Search the skills tree for the literal too — the job is the symptom, the
   skill is the disease.

### Repair

- Restore with `git checkout -- <file>` **after** the aside copy exists.
- Replace every literal in the skill with a derived expression **and** state the
  rule in prose: resolve the period from the current local date, never from a
  remembered example.
- Prefer a job that routes the write through a helper that *refuses* to drop
  existing sections over any job that asks a model to "append". A helper with a
  `verify_preserved()` check plus atomic temp-file replace makes the whole class
  unrepresentable; a prompt instruction does not.
- Consolidate duplicate jobs down to that one guarded job — see below.

## Consolidating duplicate cron jobs (verified 2026-10-04)

Six memory-maintenance jobs ran the same routine at 02:00/03:30/04:40/07:00/19:00
plus a 2-hourly script, with **contradictory retention policies** — one carried
`prune=True` (hard delete) while the rest used `prune_mode=archive`. The
destructive job was not the one that deleted anything; it was the one whose
prompt let a model rewrite a file.

### Procedure

1. `cronjob action='list'` — build the full inventory; expect dozens.
2. Group by routine. Note schedule, `script`, `no_agent`, `workdir`, `skills`,
   provider/model, and retention policy for each member.
3. Pick the survivor on **safety, not recency**: the one whose write path is
   enforced by code beats the one whose prompt merely asks nicely. Resolve
   conflicting policies explicitly (`prune=True` vs `archive` is a real
   decision — surface it to the user, do not silently pick).
4. Ask the user before deleting. This is destructive and irreversible through
   the tool surface.
5. Back up the job store, then edit it:
   `~/.hermes/cron/jobs.json` is `{"jobs": [...], "updated_at": ...}`; each job
   keys on **`id`**, not `job_id`.
6. **Verify the survivor is present and the expected number of jobs remain.**
   See the pitfall below — this step is not optional.
7. Sweep the skills tree for literal period filenames left behind by the removed
   jobs.
8. Confirm via `cronjob action='list'` that the count matches and the survivor's
   schedule is intact.

## Pitfalls

- **A list-comprehension filter can silently empty the store.** Filtering jobs
  into a fresh list and writing it back is one refactor away from
  `data["jobs"] = [j for j in jobs if j["id"] == KEEP]` — which keeps *one* job
  and deletes the other 74. This happened live. Always `assert` the post-write
  count and the survivor's presence, and keep the pre-edit backup open until the
  assertion passes.
- **`jobs.json` is a `dict` with a `jobs` list**, not a bare list. Iterating it
  directly yields the wrong keys and looks like "0 matches".
- **The job is the symptom, the skill is the disease.** Removing the offending
  cron fixes today's run; the literal path lives on in
  `skills/**/SKILL.md` and `skills/.curator_backups/**/cron-jobs.json` and will
  re-infect the next job that loads it.
- **A run transcript is the best forensic artifact you have.** It contains the
  complete skill text as loaded, so a stale instruction is quotable rather than
  inferred.
- **`git checkout --` is destructive.** Back the file up first, always, even when
  you are certain HEAD is good.
- **Sibling profiles carry their own cron stores.** `~/.hermes/profiles/*/cron/`
  duplicates the same class of jobs; a fix in the default profile does not
  reach them.

## Verification

- [ ] Damaged log backed up aside before any repair.
- [ ] `git show HEAD:<file>` non-empty; `git checkout --` restored it; the
      pre-damage entries are readable again.
- [ ] `search_files` for the literal period filename across the skills tree
      returns zero live hits (curator backups are historical, not live).
- [ ] Post-edit job count equals pre-edit minus the intended removals, asserted.
- [ ] `cronjob action='list'` shows the survivor with its original schedule.
- [ ] On the survivor's next tick, confirm the log gained an entry and lost
      nothing (`git diff --stat` shows insertions, not deletions).

## References

- `references/sync-allowlist-workflow.md` — durable workflow for adding a new operational script to the sync allowlist and repository as the source of truth.
- `references/canonical-copy-consolidation.md` — consolidating divergent copies into one canonical file: deciding with evidence (an editable install can mask a `parents[N]` bug), the shim pattern, the two regressions it creates (`exec` as `__main__` breaking imports; public-only re-export breaking monkeypatch), re-checking CLI-surface resolvers, and retiring a copy without losing stricter filtering.
- `references/jma-duplicate-records.md` — the observed JMA duplicate-record failure and canonical field mapping.
- `references/cron-failure-classification.md` — symptom-to-layer triage table for Windows Hermes cron jobs.
- `references/unsupported-cli-migration.md` — how to diagnose obsolete Hermes subcommands and migrate no-agent wrappers durably.
- `references/automation-pattern-2026-08-02.md` — full automation session: 7 new cron jobs created, MoA round-robin orchestrator deployed, PR review fix delegation pattern established, monthly impact estimates.
- `references/2026-08-02-config-drift-and-mcp-parking.md` — full forensic capture of the global inference config drift skip (`hakuapulse-orchestrator` → `hakuapulse-lite-free`), the unknown `moa` auxiliary resolver, plan-level quota exhaustion, and MCP server parking (`world-intel`, `notebooklm-mcp`, `blender`, `egov-law`).
- `references/2026-08-03-drift-repair-correction.md` — CORRECTION: `cronjob update model=` does NOT pin (silent no-op); durable fix is pause the MoA rotation cron + global pin via `hermes config set` + recreate jobs.
- `references/2026-08-03-osint-cli-recovery.md` — evidence that `hermes worldmonitor-osint` and `hermes osint-agent` are absent from the current CLI, and the working LLM-cron migration using `osint_agent_brief`.
- `references/2026-08-03-warashibe-cli-recovery.md` — evidence that `hermes warashibe` is absent, and the replacement pattern using `web_search` with purchase/login/post prohibition.
