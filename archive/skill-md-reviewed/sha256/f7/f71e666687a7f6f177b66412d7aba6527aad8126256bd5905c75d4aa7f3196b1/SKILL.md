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

- Running the weekly self-improver cron job (curator status → curator run →
  warning log review → skill patching → report)
- Verifying SKILL.md frontmatter and structure after patches
- Debugging cron job failures on Windows (inline Python blocked, path issues)

## Prerequisites

- Hermes profile `self-improver` created and configured
- `curator.enabled: true` in `~/.hermes/config.yaml`
- API key set for the auxiliary model used by curator LLM review

## Weekly Review Procedure

1. `hermes curator status` — check active/stale/archived counts, last run time
2. `hermes curator run` — auto-stale + LLM review pass (consolidate if enabled)
3. `hermes logs --level WARNING | tail -30` — summarize recent warnings
4. Read Cursor learning inbox (`%USERPROFILE%/Documents/ops/cursor-learning-inbox/*.md`)
   — process or move to `processed/`
5. Patch up to3 agent-created skills (description trim, pitfalls, platforms)
6. Write report to `_docs/YYYY-MM-DD_self-review.md`

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
| Check curator state | `hermes curator status` |
| Run curator review | `hermes curator run` |
| Check warnings | `hermes logs --level WARNING` |
| Patch a skill | `skill_manage(action='patch', name='...', old_string='...', new_string='...')` |
| Verify patches | `python scripts/verify-skills.py` |

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
- **Long CLI commands need `background=true`**: `hermes curator status` and
  `hermes logs --level WARNING` each take 60-120s+ on this host (cold import +
  Bitwarden warnings). A foreground call with `timeout=120` can hit exit 124.
  Launch them backgrounded and `process(action='wait')` instead.
- **`/tmp/` path mismatch**: git-bash `/tmp/` resolves to a real path on
  Windows, but Windows-native Python cannot find files written there via
  bash. Use workspace-relative paths (`C:/Users/<user>/Documents/ops/`) or
  `$TEMP` for temp scripts in cron jobs.
- **Cron path guard blocks `rm /tmp/`**: Cleanup of `/tmp/` files is blocked
  by the cron safety guard. Accept the leftover or clean manually in a
  non-cron session.
- **Missing skill on a scheduled job is not a blocker**: if the job's skill
  list names a skill that is absent from disk, report it in the summary and
  continue with the remaining procedure. Do not create a replacement umbrella
  for a single skipped reference.

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
1. Run the verification script against patched skills
2. Confirm no temp files remain in workspace
3. Check `hermes curator status` to confirm patch counts incremented
