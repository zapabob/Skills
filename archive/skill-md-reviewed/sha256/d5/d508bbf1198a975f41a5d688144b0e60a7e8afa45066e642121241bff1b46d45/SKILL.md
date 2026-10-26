---
name: cronjob-management
description: Procedures for managing Hermes cron jobs, including listing, running, monitoring, and troubleshooting.
version: 1.0.0
category: devops
---

# Cron Job Management Skill

This skill provides procedures for managing Hermes cron jobs, including listing, running, monitoring, and troubleshooting scheduled tasks.

## Overview

Hermes cron jobs are scheduled tasks that run automations like news digests, memory syncs, or platform posts. This skill covers common operations and troubleshooting patterns.

## Procedures

### 1. List Cron Jobs
Use `cronjob(action='list')` to view all scheduled jobs, their status, schedule, and last run details.

### 2. Run a Cron Job Manually
To execute a job immediately (e.g., after a failure or for testing):
```
cronjob(action='run', job_id='<job_id>')
```
Replace `<job_id>` with the ID from the job list.

### 3. Check Job Output
After running a job, review its output in the job's output directory:
```
~/.hermes/cron/output/<job_id>/
```
Each run creates a timestamped Markdown file with the job's response.

### 4. Monitor Job Status
Check `last_status`, `last_delivery_error`, and `state` fields from `cronjob(action='list')` to determine if a job is healthy.

### 5. Troubleshoot Common Issues

#### Provider Timeouts
If a job fails with "provider timeout" or similar LLM provider errors:
- Re-run the job manually (see step 2)
- If the issue persists, consider:
  - Checking provider API status
  - Verifying API keys in `.env`
  - Trying a different model/provider via `cronjob(action='update', model='...', provider='...')`
  - Increasing timeout (if supported by the tool)

#### Delivery Errors
If `last_delivery_error` indicates a plugin issue (e.g., "Discord plugin not registered"):
- Ensure the required plugin is installed and enabled
- Verify plugin configuration in `config.yaml`
- Reinstall the plugin if necessary

#### Silent Failures (No Output)
If a job returns `[SILENT]` or produces no output:
- Confirm the job's prompt or script is valid
- Check for silent failures in the underlying tool (e.g., web search returning no results)
- Adjust the job's sensitivity or filters

#### Inference-Config Drift (spend-protection RuntimeError)
If a job fails with `RuntimeError: Skipped to prevent unintended spend: global inference config drifted ... and this job is unpinned`, the global default model changed after the job was created and the job was left unpinned. **THIS IS A GUARD, not a script bug.** Critical gotcha: the error text suggests `cronjob action=update job_id=<id> provider=<p> model=<m>` — but that `update` is a **silent no-op for model/provider** (returns success, `model` stays `null`, next run still fails). The working repair is **pause + recreate pinned**; you do NOT need to pin the global MoA preset or pause the orchestrator-rotation job. Full recipe + how to read the real error from `~/.hermes/cron/executions.db`: see `references/cron-inference-drift-repair.md`.

#### `.ps1` script jobs on Windows (no-agent)
A `no_agent` cron whose `script` ends in `.ps1` is executed by the cron runner via the **Python interpreter**, NOT PowerShell — so PowerShell syntax (`$msg = "..."`, `msg * /time:5 ...`) raises `SyntaxError: invalid syntax` and the job fails with `execution_error: ... line 4  ^  SyntaxError: invalid syntax`. Fix: point the cron at a `.py` file (or a PowerShell launcher invoked through `cmd /c`), never a bare `.ps1`. Cross-platform pattern: a Python script that calls `msg.exe` on Windows and `notify-send` on Linux. See `references/cron-ps1-windows-gotcha.md`.

#### Diagnose a failing cron from the CLI
When `Last run:` shows `error:`, do NOT guess — pull the real transcript and classify:
1. `hermes cron list` → find the job and its `error:` message.
2. `hermes cron runs <job_id> --limit 3` → prints recent run IDs with stderr/stdout. Grep the error token. NOTE: `hermes cron show <id>` / `hermes cron status <id>` do NOT exist (they error) — use `runs`. The `runs` call can be slow (10–120s) and may emit an unrelated `cryptography` DLL ImportError on startup; wait it out.
3. Read the job's `Script:`/`Workdir:` file and reproduce the failing function in isolation (e.g. import the module, call the validator on each candidate input) to separate a logic bug from an environment bug.
4. Classify and act:
   - **Logic bug in user script** → fix and re-verify by re-running the isolated function.
   - **Environment bug** (`hermes -z` timeout, TTS server won't start, paging-file DLL error) → infra, not a script edit.
   - **Internal Hermes wrapper error** (e.g. `name '_scripts_dir_for_job' is not defined`) → platform bug; the user script runs fine manually. Report, don't edit the script.
   - **Agent output truncated** (`Response truncated due to output length limit`) → bound/summarize the agent output.

#### Pitfall: naive substring sanitizer false-positives
Public-post `no-agent` scripts (e.g. `lm-twitterer-post.py`) often block FORBIDDEN markers like `"SECRET"`, `"TOKEN"`, `"C:\Users\"` via `if marker.upper() in text.upper()`. This FALSE-POSITIVES on legitimate substrings: `"secret-free"` and `"secrets"` both contain `"SECRET"`. Symptom: `Refusing unsafe public text marker: SECRET` even though the post is safe. Fix: rephrase to avoid the substring (e.g. `secret-free` → `leak-free`) or use word-boundary/allowlist matching, then re-verify by importing the validator and running it over every candidate string. See `references/diagnose-broken-cron-recipe.md`.

### 6a. Safe headless plugin execution and aggregate reporting

For no-agent jobs that call a Hermes plugin directly, run the repository-local Python/venv and dynamically import the plugin only after registering the module in `sys.modules`; this is required for modules containing `@dataclass` declarations. Verify the subprocess exit code and emit only sanitized aggregate status fields. For social or account integrations, never print raw records, credentials, environment variables, cookies, tokens, or API responses; report counts and a short status message instead. When a read returns zero candidates, distinguish “zero surfaced/eligible in this run” from a definitive claim that the remote service has no matching records.


- For `no_agent` jobs, empty stdout is intentionally silent. Always emit a compact heartbeat when the user needs every-run delivery, including when there are no candidates.
- When `HERMES_CRON_AUTO_DELIVER_*` and `HERMES_CRON_SESSION` are present, a script-side `hermes send` to the same target can be suppressed by the duplicate-target guard. If direct script delivery is the chosen fallback, remove those four cron auto-delivery variables only in the child subprocess and set the cron job's `deliver` to `local` to prevent duplicates.
- Inspect `HERMES_HOME` before validating artifacts. Cron may run under a named profile such as `~/.hermes/profiles/<name>` while the interactive shell uses the main home; report the absolute artifact path.
- For delegation failures, use registered provider names and the official CLI (`hermes config set delegation.provider nous` and `hermes config set delegation.model auto-free`) rather than editing protected config files directly.
- Detailed reproduction and verification steps are in `references/no-agent-delivery-profile-boundaries.md`.

### 7. Maintaining Version-Specific Automated Posting Jobs

For automated jobs that post version-specific content (like viral tweet announcements), follow these practices:

**Update Version Information Promptly**
- When releasing a new version, update the cron job's prompt to reflect the new version number
- Replace old version references (e.g., `v0.18.2` → `v0.19.0`) in the job's prompt
- Update any date-specific references in the prompt
- Consider adding instructions to avoid reusing old wording (`v0.18.2の古い文面をそのままで使わないようにし`)

**Example Pattern (Hermes Viral Tweets Job)**
```
# Before update:
Hermes Agent v0.18.2（v2026.7.7.2、2026年7月7日）の新情報を軸に、6時間ごとに日本語のバズるX投稿を1件生成・即時投稿する。v0.18.0の古い文面をそのままで使わないようにし、最新のプロンプトガイドラインに従って内容を生成してください。

# After update:
Hermes Agent v0.19.0 の新機能を紹介し、フォロワーに役立つ情報を日本語でツイートしてください。最新の変更点や改善点を簡潔にまとめて、ハッシュタグ #HermesAgent を含めてください。
```

**Verification Steps**
1. Use `cronjob(action='get', job_id='<job_id>')` to verify the updated prompt
2. Run the job manually with `cronjob(action='run', job_id='<job_id>')` to test the new content
3. Check the output in `~/.hermes/cron/output/<job_id>/` to confirm proper generation
4. Monitor the next scheduled run to ensure successful delivery

**Best Practices**
- Rotation-mint checklist (verified 2026-09-04): when minting topics_vNNN.json + hermes-vNNN script + new cron, pause ALL superseded version jobs in the same pass — `list` first, then pause each old job ID. Overlapping live rotations (v018 + v022 + v024 all firing at once happened before) double-post and burn budget. Pause, don't remove, so rollback is one resume.
- Verify-before-claim for public angles: every marketing claim in a new topics file must be backed by same-session evidence (`netstat` LISTEN lines, `tasklist` process names, `git log` hashes, build artifact paths). Never carry an unverified angle forward from an old version file.
- Keep version-specific jobs enabled only for a reasonable period after release (consider disabling older version jobs)
- Use clear, action-oriented prompts that focus on current features rather than historical comparisons
- Include relevant hashtags or community tags in the posting instructions
- Test the updated job manually before relying on the scheduled run

### 7. Pause/Resume Jobs
- Pause: `cronjob(action='pause', job_id='<job_id>')`
- Resume: `cronjob(action='resume', job_id='<job_id>')`

### 7. Remove Jobs
Use with caution: `cronjob(action='remove', job_id='<job_id>')`

### 8. Duplicate / Noise Triage
When the user complains that cron is noisy, duplicated, or causing cognitive clutter, do an active consolidation pass instead of only explaining options:

1. Run `cronjob(action='list')` and group jobs by purpose, schedule, delivery target, script, and prompt preview.
2. Keep one canonical job per purpose. Prefer the job that is enabled, recently healthy, script-based/no-agent when possible, and has the most explicit delivery target.
3. Pause—not remove—suspected duplicates first, especially social posting, memory/sleep, OSINT/news, heartbeat, and reminder jobs.
4. Leave a short final report with job IDs paused and canonical jobs kept.
5. If the user also reports reasoning/process clutter, check display/config knobs such as `display.show_reasoning`, `display.interim_assistant_messages`, and `display.turn_completion_explainer`; quiet them when the user's intent is clear.

Session example: see `references/cron-duplicate-noise-triage.md`.

## Daily Development Summary (cross-repo commit collection)

For cron jobs that generate a daily dev summary by collecting commits across
multiple local git repos and appending to an Obsidian daily note:

- **Always query `--all` in addition to the default branch.** `git log --since`
  only shows commits reachable from HEAD; unmerged feature branch commits are
  invisible without `--all`. Identify which branch each extra commit is on
  (`git branch --contains <hash>`) and attribute it explicitly in the note.
- If the daily note already exists from an earlier cron run, read and patch it
  rather than overwriting — add missing repos and fix branch attribution.
- See `references/daily-dev-summary-cross-repo-commit-collection.md` for the
  full repo list, pitfall details, and note structure.

## Best Practices

- Always verify job output after manual runs
- Keep plugin and tool dependencies up to date
- Monitor job history for recurring failures
- Use descriptive job names for easier identification
- Test new jobs with `dry_run=true` or manual runs before enabling schedules
## References

- `references/cron-duplicate-noise-triage.md`
- `references/cron-script-path-mismatch.md` - Common pitfall where cron job's `script` path doesn't match actual file location relative to `workdir`
- `references/json-parse-gitbash-issue.md`
- `references/provider-timeout-troubleshooting.md`
- `references/warashibe-cron-script-fix.md`
- `references/diagnose-broken-cron-recipe.md` - CLI failure-diagnosis workflow + substring-sanitizer false-positive pitfall
- `references/cron-inference-drift-repair.md` - Unpinned LLM cron blocked by config-drift guard; `update` is a no-op, use pause+create-pinned. Read real error from executions.db
- `references/cron-ps1-windows-gotcha.md` - `no_agent` cron with a `.ps1` script runs under Python and fails with SyntaxError; use a `.py` wrapper
- `references/2026-07-15-cron-sync-tool-issues.md` - Tool failures encountered during scheduled cron sync and lessons for Windows/MSYS script deployment relative to `workdir`
- `references/json-parse-gitbash-issue.md`
- `references

## Automated MOA Provider Evaluation

When you:
     ```
     hermes cron create --name "Daily MOA Provider Evaluation" --script "daily_moa_provider_selector.py" --no-agent --deliver local "0 4 * * *"
     ```
   - This runs the script daily at 4:00 AM

3. To manually activate the fallback preset:
   - Set `moa.active_presetypeP"<
<|reserved_token_1635921936|>reserved_token1638400000000166237379999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999