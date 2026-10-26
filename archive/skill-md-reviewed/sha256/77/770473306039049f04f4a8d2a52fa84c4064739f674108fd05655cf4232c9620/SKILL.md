---
name: self-improver-operations
description: "Curator runs and skill upkeep for self-improver."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [curator, skill-maintenance, self-improver, cron, verification]
    category: devops
    related_skills: [ai-employee-org, hermes-agent]
---

# Self-Improver Operations

Skill maintenance and curator workflows for the self-improver profile.
Covers the weekly review cycle, ad-hoc skill verification, and Windows
cron pitfalls that affect autonomous maintenance jobs.

## When to Use

- Running the self-improver weekly/cron review: liveness check → cron census →
  curator run record → warning log review → skill patching → report
- Verifying SKILL.md frontmatter and structure after patches
- Triaging cron job failures on Windows — auth-retry loops, `[drift_skip]`,
  profile-scoped `cron status` misleading you
- Deciding what is safe to fix autonomously vs. what needs human approval
- Debugging cron job failures on Windows (inline Python blocked, path issues)

## Prerequisites

- Hermes profile `self-improver` created and configured
- `curator.enabled: true` in `~/.hermes/config.yaml`
- API key set for the auxiliary model used by curator LLM review

## Weekly Review Procedure

Run in this order. Steps 1–3 are file-first on purpose: the CLI equivalents are
slow and profile-scoped (see Pitfalls), and a wrong-but-plausible CLI answer
sent a whole review in the wrong direction on 2026-10-02.

1. **Establish liveness first** — `read_file`
   `%USERPROFILE%/.hermes/cron/ticker_heartbeat` and `ticker_last_success`
   (epoch floats). If these are recent, the scheduler is alive; do **not**
   infer a dead gateway from any CLI warning.
2. **Census cron via `search_files` counts** over
   `%USERPROFILE%/.hermes/cron/jobs.json` (see the pattern table below), then
   pull context for anything with a live `failure_streak`.
3. **Read the newest curator `run.json`** at
   `~/.hermes/profiles/self-improver/logs/curator/<newest>/run.json` —
   authoritative for `auto_transitions`, `tool_calls_total`, and `llm_final`.
4. **Only then** try `hermes curator status` / `hermes curator run` if a live
   view is genuinely needed — and expect the 420s cap.
5. Read the Cursor learning inbox (`%USERPROFILE%/Documents/ops/cursor-learning-inbox/*.md`)
   — process or move to `processed/`
6. Patch up to 3 agent-created skills (description trim, pitfalls, platforms)
7. Write report to `_docs/YYYY-MM-DD_self-review.md`
8. If headless: surface destructive items (cron pause/edit, DB or log removal,
   config mutation) as **explicit human-approval requests** in the handoff.
   Do not apply them; see "Reporting under a no-destroy constraint" below.

## Ad-hoc Skill Verification

After patching SKILL.md files, run a quick frontmatter + structure check.
See `scripts/verify-skills.py` for the reusable verification script.

Checks to run:
- SKILL.md exists in expected skill directory
- Frontmatter block present (--- delimited)
- `description:` field present and ≤60 characters
- `platforms:` field present when applicable
- Required sections present (Pitfalls, Verification, etc.)
- No leftover temp files in workspace

## Quick Reference

| Task | Command |
|---|---|
| Check curator state | `hermes curator status` (may hang — see Pitfalls) |
| Read curator last run | `read_file ~/.hermes/profiles/self-improver/logs/curator/<newest>/run.json` |
| Run curator review | `hermes curator run` |
| Check cron liveness | `read_file %USERPROFILE%/.hermes/cron/ticker_heartbeat` (epoch float) |
| Read all cron jobs | `read_file %USERPROFILE%/.hermes/cron/jobs.json` (profile-scoped CLI lies) |
| Check warnings | `hermes logs --level WARNING` |
| Patch a skill | `skill_manage(action='patch', name='...', old_string='...', new_string='...')` |
| Verify patches | `python scripts/verify-skills.py` |

## Cron health census (no CLI, no scripts)

The reliable way to inventory cron on this host is `search_files` counts over
`%USERPROFILE%/.hermes/cron/jobs.json` — each pattern maps to one metric:

| Pattern (as a regex) | Metric |
|---|---|
| `"id": "[0-9a-f]{12}"` | total registered jobs |
| `"enabled": true` | active jobs |
| `"state": "paused"` | paused jobs |
| `"state": "error"` | jobs in error state |
| `"last_status": "ok"` | last run succeeded |
| `"last_status": "(error\|failed)"` | last run failed |
| `"last_run_at": "2026-10-..` | jobs that fired in a window |
| `"failure_streak": [1-9][0-9]*` | jobs with a live failure streak |
| `"drift_alerted": true` | jobs the drift guard already warned about |
| `"preflight_alerted": true` | jobs already reported as blocked_config |

`failure_streak` is the priority sort key: a job with a streak in the
hundreds is burning a schedule slot every run and deserves a human decision
before anything with a single-digit streak.

## Reporting under a no-destroy constraint

Most reviews run with an explicit "no destructive changes, no cron
pause/edit, no DB deletion — surface items needing human approval" rule. That
constraint is not a limitation to apologise for; it is the shape of the
deliverable. The output is **a precise, ranked decision queue**, not a
half-applied fix.

How to make it maximally useful to the human who unblocks it:

1. **Rank by real harm, not by discovery order.** A job with
   `failure_streak: 1278` on a 20-minute schedule outranks everything with a
   single-digit streak. Sort by consequence.
2. **Attach a concrete fix command per item**, copied from the job's own error
   message where it provides one (Hermes drift guards embed the exact
   `hermes cron edit <id> --provider <provider> --model <model>` to run).
   A recommendation without a copy-pasteable command costs the human a lookup.
3. **State the human-time cost** where it is the real blocker — e.g. "MCP
   `notion`/`linear`/`figma` are parked on `OAuthNonInteractiveError`, which is
   impossible to clear headless; it needs ~3 min of interactive
   `hermes mcp login`." That converts "stuck" into "here is your queue".
4. **Distinguish "measured" from "could not measure".** If `du -sm` timed out or
   `curator status` exceeded the cap, say so in a dedicated section. A silently
   narrowed claim is worse than an acknowledged gap.
5. **Name leftover artifacts explicitly** (quarantined files, unverified
   counts) in the handoff `not_done` field so the next session inherits the
   truth instead of rediscovering it.
6. **Carry forward corrections, don't quietly overwrite them.** When a prior
   report's headline finding is falsified, put the retraction in its own
   section at the top with the evidence that overturned it. Silently
   correcting it destroys the audit trail and leaves the reader unsure whether
   the old claim was ever checked.

## Pitfalls

### Windows cron job constraints

- **Inline Python blocked**: `python -c "..."` is flagged as dangerous in
  cron mode (no user present to approve). Write scripts to a file first with
  `write_file`, then execute via `terminal(command="python path/to/script.py")`.
- **Security Center blocks ad-hoc scripts (second gate)**: the write-then-run
  workaround above is NOT sufficient. A `write_file`-created `.py` under a
  gitignored dir (`tmp/probes/`) is rejected with
  `Security Center blocked a unverified execution candidate: <path> (SCAN_ERROR, score 0)`,
  and `uv run python <path>` is blocked identically. **Do not fight this gate.**
  Read state with `read_file` / `search_files`, and prefer the Hermes CLI
  (`hermes curator usage`, `hermes curator list-archived`) over a hand-rolled
  parser. See `references/security-center-script-block.md`.
- **A blocked script path becomes UNDELETABLE — never create one in a Kanban
  workspace.** Confirmed 2026-10-02: after a `write_file` probe was refused
  execution, every `terminal` command *naming that path* was refused too,
  including `rm -f`, `find -delete`, and `rm` with an absolute path. The file
  could not be removed for the rest of the run and had to be left to workspace
  GC or a foreground operator. `read_file` / `ls` on the same path still work,
  so the block is easy to mistake for a transient. **The write is what creates
  the trap**: in headless Kanban mode, go straight to the `search_files` census
  in SKILL.md and never write an executable probe. If one already exists, cap
  retries at one and name the leftover in the handoff.
- **Long CLI commands need `background=true`**: `hermes curator status` and
  `hermes logs --level WARNING` each take 60-120s+ on this host (cold import +
  Bitwarden warnings). A foreground call with `timeout=120` can hit exit 124.
  Launch them backgrounded and `process(action='wait')` instead.
- **`process(action='wait'/'poll')` can also hang past its own timeout**: on
  this host the process tool itself timed out at 420s waiting on the very
  commands the note above tells you to background. Do not burn three retries
  on it — fall back to reading state files directly (see below), and treat
  `execute_code`, `python -c`, and bash heredocs as **blocked** in headless
  single-query mode (`approvals.single_query_mode`). The only script route
  that survives is the Security-Center-approved one, which is usually not
  worth fighting. State-file reads via `read_file` / `search_files` /
  `stat` + `tail` cover the same ground.
- **`hermes cron status` / `hermes cron list` are PROFILE-SCOPED**: run from
  the `self-improver` profile they resolve to
  `~/.hermes/profiles/self-improver/cron/`, which holds **zero** jobs, and
  report `No scheduled jobs` / `cron jobs will NOT fire`. The real jobs
  (59 enabled of 71) live in the **default** profile at
  `%USERPROFILE%/.hermes/cron/jobs.json`. **Falsified diagnosis caught
  here on 2026-10-02**: a prior review reported "Gateway stopped, cron will
  NOT fire" as P0 based on that output — the gateway was actually running.
  Never trust `cron status` output without confirming which profile it
  resolved. Read `~/.hermes/cron/jobs.json` for ground truth.
- **`last_error` is HISTORIC, not current**: cron never clears it after a
  later success. Seven jobs still carried
  `Failed to compute next run ... (is the 'croniter' package installed?)`
  from an old incident while actually running fine. Diagnose with the
  **triple**: `last_status` AND `next_run_at` AND `fire_claim`. A non-null
  `last_error` alone proves nothing about current health.
- **Ticker liveness is the fastest health check**: read
  `~/.hermes/cron/ticker_heartbeat` and `ticker_last_success` (epoch floats).
  Age in seconds = seconds since last tick. This is a two-`read_file` check
  that avoids the slow CLI entirely, and it is authoritative.
- **`hermes curator status` hangs past the 420s tool cap on this host**:
  the fallback is reading the newest
  `~/.hermes/profiles/self-improver/logs/curator/<ts>/run.json` directly.
  It carries `duration_seconds`, `auto_transitions` (marked_stale /
  archived), `counts.tool_calls_total`, and `llm_final` — enough to tell
  whether the auto pass ran even when the LLM pass 404'd.
- **`/tmp/` path mismatch**: git-bash `/tmp/` resolves to a real path on
  Windows, but Windows-native Python cannot find files written there via
  bash. Use workspace-relative paths (`C:/Users/<user>/Documents/ops/`) or
  `$TEMP` for temp scripts in cron jobs.
- **Cron path guard blocks `rm /tmp/`**: Cleanup of `/tmp/` files is blocked
  by the cron safety guard. Accept the leftover or clean manually in a
  non-cron session.
- **A whole-run tool-layer outage is possible, not just a slow CLI.** Observed
  2026-10-04: every filesystem/shell tool call — `terminal` (including a
  3-character `echo hi`), `read_file`, `write_file`, `search_files` — failed
  instantly with `RuntimeError: Windows terminal command length exceeds safe
  limit`. The message is **misleading**: it names command length, but it fired
  on all tools and all payload sizes, including `read_file` which sends no
  command at all. `skill_view` / `skill_manage` kept working, so the fault is
  in the shell/filesystem dispatch path, not the whole runtime.
  **Do not burn the run retrying it** — after `echo hi` fails, the outage is
  confirmed; further identical retries only trip the loop guard. Fall back to:
  (a) report the outage plainly, (b) apply only `skill_manage` work that is
  safe without verification, (c) leave `_docs/` for the next healthy run
  rather than assuming `write_file` succeeded — it did not.
- **Missing skill on a scheduled job is not a blocker**: if the job's skill
  list names a skill that is absent from disk, report it in the summary and
  continue with the remaining procedure. Do not create a replacement umbrella
  for a single skipped reference.

### Recurring config defects (fix in config, not per-job)

- **A cron `skill:` naming a PROFILE is a latent defect.** Observed on
  2026-10-02: `320b7b876e04` (self-improver-weekly-review) carries
  `skill: "self-improver"`, and `842f96e965de` carries
  `skill: "delivery-worker"` — both are *profile* names, not skills. A skill
  of that name does not exist, so the load silently yields nothing. Real
  alternatives: `self-improver-operations` for self-improver,
  `delivery-worker`-adjacent review skills for delivery-worker. This is a
  recurring template bug in the cron *creator*, not a one-off — check it on
  every review and prefer fixing the creating template.
- **`auxiliary.<role>.model: ''` makes drift guards misfire.** With
  `curator.provider: auto` and an empty model, the role inherits the global
  inference config; when that global changes, every unpinned job trips
  `[drift_skip:silent]` and is skipped to avoid unintended spend. The fix is
  either pin the job (`hermes cron edit <id> --provider/--model`) or pin the
  role in config. Both change cost/model behaviour, so both need human
  approval — surface them, never apply them autonomously.
- **A job whose auth prerequisite is missing retries forever.** Seen:
  `510d48c0c367` (Google Workspace token refresh, every 20m) reached
  `failure_streak: 1278` purely because `google_token.json` never appeared.
  Cron has no `blocked_config` equivalent to stop it. When reporting, rank
  by streak and recommend pause-with-reason rather than "keep retrying".

### Skill authoring standards (quick reference)

- `description:` ≤ 60 characters, one sentence, ends with period
- No marketing words ("powerful", "comprehensive", "seamless")
- `platforms:` must match actual script imports (POSIX-only = linux/macos)
- `created_by: agent` in usage.json determines if curator can auto-manage
- Bundled/hub-installed skills are off-limits to autonomous curation

### Curator quirks

- **The LLM pass is optional — auto-transitions still run.** A failed LLM
  review does not abort the run. The pure time-based pass (mark-stale at 30d,
  archive at 90d) is separate and always executes. A 404 or provider stall
  therefore still yields a real, non-empty result; report it as
  "LLM pass skipped, auto pass applied", not as a failed run.
- **HTTP 404 = wrong model/route, not a bad API key.** Seen twice
  (2026-09-27): `llm: API call failed after 2 retries: HTTP 404: 404 page not
  found`, where `REPORT.md` names
  `custom:127.0.0.1-8080/qwen3.8-27b-abliterated-mtp` via `nvidia`. A 404 is
  the endpoint rejecting the *path/model*, so no amount of key rotation fixes
  it. Earlier a stall appeared instead: `Provider has been unresponsive ... for
  7 consecutive stale attempts`. Check the configured auxiliary model resolves
  before blaming credentials.
- **When the LLM pass fails, consolidation silently does not happen.**
  `consolidate: on` is reported in `curator status`, but with 0 tool calls the
  run consolidates nothing. Duplicate/overlapping agent skills will keep
  accumulating until the auxiliary model is fixed — this is the main reason
  the managed-skill count drifts upward.
- **A 30-day-idle profile re-stales in bulk.** A 27-day gap since the last run
  meant every skill past 30d flipped at once (26 stale + 11 archived in one
  29-second run). That is expected behaviour, not a bug, but review the newly
  archived list before the gap grows again — recovery is
  `hermes curator restore <name>`.
- Pinned skills are exempt from all auto-transitions and LLM review.

## Verification

After any skill patch session:
1. Re-load the skill with `skill_view(name)` and read the rendered content —
   confirm each intended section is actually present and correctly nested.
   This is the only reliable check when `scripts/verify-skills.py` cannot run
   headless (it hits the same Security Center gate as any other script).
2. **List the workspace directory** (`ls -la`) and confirm no leftover temp
   files. If a probe path has been quarantined, `ls` still works even though
   `rm` does not — so this check catches what the blocked `rm` cannot report.
3. Confirm the report file exists at its `_docs/` path and is non-trivial in
   size (a stub or a truncated write is worse than nothing).
4. Check `hermes curator status` for incremented patch counts — only if it
   completes inside the 420s cap; otherwise read the next `run.json` later.
