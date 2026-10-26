---
name: kanban-board-health-check
description: 'Kanban board health check: blocked>30d, cron, stale runs.'
version: 1.0.0
platforms: [linux, macos, windows]
environments: [kanban]
metadata:
  hermes:
    tags: [kanban, monitoring, cron, ops, secretary]
    related_skills: [kanban-worker, kanban-orchestrator]
---

# Kanban Board Health Check

> The secretary/ops profile runs this as a recurring cron (e.g. `secretary-daily-health-check`,
> `0 9 * * *`). Goal: inspect board + cron state, record findings to the task thread, and hand
> human-gated actions (archive, complete, config fixes) to the operator — never execute them.

## When this skill applies

- A scheduled job asks you to "inspect the board", "check for blocked > 30d", "verify cron jobs
  are running", or "check for stale runs".
- You are the secretary profile doing a periodic health check on a kanban board.

## Anti-temptation rules (same as orchestrator)

- **Comment + report only.** Actual archive/complete/reassign is human-approved. Board history
  persists forever; your report is the deliverable, not the fix.
- Do not mark other specialists' tasks complete.
- If follow-up work is real (e.g. "clean up zombie claim"), create a card for the right profile
  instead of doing it yourself — or flag it in the report for human approval.

## Check flow

1. **Orient.** `kanban_show()` on your task (defaults to `$HERMES_KANBAN_TASK`). If the task is
   already terminal (`done`/`complete`) — see "Already-terminal task" pitfall.
2. **Board state.** Query the board DB directly (tools don't expose aggregate views):
   status counts, blocked > 30d list, non-done cards (running/ready/todo/triage/complete),
   stale claims, non-terminal runs, profile activity. See
   `references/board-health-check.md` for the exact SQL and DB/cron store locations.
3. **Cron health.** `hermes cron list --all` + `hermes cron status` for the display view; dig
   into `executions.db` (per-profile store for board jobs!) for failed/unknown runs.
4. **Delta vs last check.** Compare with the previous check's comment/numbers so trends
   (blocked growing, profile inactivity, gateway downtime) are explicit.
5. **Report.** `kanban_comment` on the parent/seed task with the full findings table + recommended
   human actions. Optionally write a dated markdown report file into the workspace and attach it.
6. **Close.** `kanban_complete` with a concise summary + machine-readable metadata
   (counts, cron failures, stuck task ids). If you cannot complete because the task is already
   terminal, deliver the report and stop — see pitfall below.

## Report shape (works well)

```
## 定期健全性チェック結果 — <date> JST
### 1. ボード全体状態 (table: total/done/blocked/triage/complete/ready/todo/running + delta)
### 2. blocked 30日超滞留 (list: id | age | assignee | 分類 | 推奨アクション)
### 3. Cron ジョブ (table: job | schedule | status incl. failed/unknown executions + reason)
### 4. プロファイル活動 (16日超非活動アラート or なし)
### 5. 放置・stale 検出 (stuck tasks, zombie claims, stuck runs)
### 6. 推奨アクション（要 human 判断、実操作は user 承認後）
### 差分サマリ（前回比）
```

## Pitfalls

**Goal-mode judge block loop.** A recurring monitor card created with `goal_mode=True` can have
its `kanban_complete` rejected by the goal judge (`NotFoundError`) → worker never terminates →
`block_loop_detected` → card auto-escalates to `triage` (needs_input) and strands for days.
Recurring seed cards should be `goal_mode=False`: the cron schedule is the loop, each run should
be able to finish in one shot.

**Already-terminal task.** A cron session can inherit a stale `HERMES_KANBAN_TASK` pointing at a
card a previous run already completed. `kanban_complete` then errors with "unknown id or already
terminal" and a protocol-violation nudge may claim the task is still `running`. Trust
`kanban_show` + the DB: if status is `done`/`complete` and `current_run_id` is null, don't
retry-loop on `kanban_complete` — the deliverable (comment + report file) is what counts; deliver
it and stop. Exact verification (local SQLite board at `~/.hermes/kanban/boards/<board>/kanban.db`):
```sql
SELECT id, status, started_at, completed_at, current_run_id FROM tasks WHERE id='<task>';
-- plus the newest row in task_runs:
SELECT id, status, outcome, started_at, ended_at FROM task_runs
WHERE task_id='<task>' ORDER BY started_at DESC LIMIT 1;
```
A `current_run_id` of NULL + `status` in (done, complete) means terminal; the kernel's
"already terminal" rejection of a redundant `kanban_complete` is itself the confirmation — report
the verified state and stop, do not force-complete.

**Cron `skills` field may name profiles, not skills.** Per-role cron prompts in this org
(e.g. `job-seeker-daily-crawl`, `job-recruiter-weekly-sync`) declare `"skills": ["job-recruiter"]`
— a profile name, not an installed skill. The dispatcher logs `⚠️ Skill(s) not found and skipped:
<job-recruiter>` at startup; the job still runs fine with normal tools. Do not flag this as a
missing dependency in the health report.

**Cron failed ≠ cron broken.** A `failed` execution with
`RuntimeError: Skipped to prevent unintended spend: global inference config drift` means the
runner refused a catch-up execution because model/provider config drifted. The next scheduled run
of the same job may succeed. Correlate timestamps (scheduled vs catch-up) before alarming.

**Job store is per-profile.** `hermes cron list` shows board jobs, but their run history lives in
`~/.hermes/profiles/<profile>/cron/executions.db`, NOT the global `~/.hermes/cron/`. Grep the
global jobs.json for a job id and find nothing → check the profile store.

**Windows `python` stub.** On this host `python` is the Microsoft Store stub (prints "Python",
exit 0, no output). Use `python3.12` for scripts; `which python` → `WindowsApps` is the tell.

**`HERMES_HOME` can point at a temp dir in cron.** Observed 2026-08-06: session inherited
`HERMES_HOME=%USERPROFILE%/AppData/Local/Temp/hermes-gmail-token` (left over from Gmail-token
ops). Symptom: `hermes kanban boards` lists only `default` and
`hermes kanban --board ai-company show <id>` errors "board 'ai-company' does not exist" — the
CLI reads HERMES_HOME, not the active profile. Fix: prefix every CLI call with
`HERMES_HOME=%USERPROFILE%/.hermes`. Check with `echo $HERMES_HOME` first. Direct SQLite reads
of the board db are unaffected by this.

**Inline `python3.12 -c` heredocs can crash the terminal guard.** A terminal command embedding
multi-line sqlite code was rejected outright with `'PurePosixPath' object has no attribute
'resolve'` (crash inside `cron/lifecycle_guard.py`), not a normal error. Second reason for the
"write a script file, run it" pattern: never inline multi-line python/sqlite in terminal on this
setup. Use `scripts/board_health_check.py` instead of re-typing the queries each run.

**Headless deliverable when `kanban_comment` tool is not exposed.** With the right HERMES_HOME:
`hermes kanban comment --author secretary <task_id> "$(cat report.md)"` (pass the full markdown
via a file, not long inline args) and `hermes kanban attach <task_id> <path>` to attach the dated
report file. Verify the comment landed via SQLite (`task_comments` newest row) before declaring
success.

## Support files

- `references/board-health-check.md` — the exact SQL queries (blocked>30d, zombie claims, stuck
  runs, profile activity), cron store locations, `executions` status semantics, the HERMES_HOME
  cron-session quirk, and observed global-job error signatures.
- `scripts/board_health_check.py` — consolidated diagnostic: status counts, blocked>30d, zombie
  claims, stuck runs, profile activity, non-terminal tasks, and cron execution tails. Self-heals
  the HERMES_HOME trap (falls back to `~/.hermes` when the env var has no kanban board dir). Run
  with `python3.12 scripts/board_health_check.py [board_slug]`.
