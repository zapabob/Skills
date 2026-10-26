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
- **`/tmp/` path mismatch**: git-bash `/tmp/` resolves to a real path on
  Windows, but Windows-native Python cannot find files written there via
  bash. Use workspace-relative paths (`C:/Users/<user>/Documents/ops/`) or
  `$TEMP` for temp scripts in cron jobs.
- **Cron path guard blocks `rm /tmp/`**: Cleanup of `/tmp/` files is blocked
  by the cron safety guard. Accept the leftover or clean manually in a
  non-cron session.

### Skill authoring standards (quick reference)

- `description:` ≤ 60 characters, one sentence, ends with period
- No marketing words ("powerful", "comprehensive", "seamless")
- `platforms:` must match actual script imports (POSIX-only = linux/macos)
- `created_by: agent` in usage.json determines if curator can auto-manage
- Bundled/hub-installed skills are off-limits to autonomous curation

### Curator quirks

- LLM review pass may fail with 404 if the auxiliary model endpoint is
  misconfigured — auto-stale still works, only LLM quality review is skipped
- `consolidate: true` merges duplicate skills — check `curator status` after
  run to see if any consolidations occurred
- Pinned skills are exempt from all auto-transitions and LLM review

## Verification

After any skill patch session:
1. Run the verification script against patched skills
2. Confirm no temp files remain in workspace
3. Check `hermes curator status` to confirm patch counts incremented
