---
name: delegation-fallback
description: "Delegated worker failed: fall back to direct execution."
version: 1.0.0
author: Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, fallback, research, execution, openmanus, codex]
    related_skills: [openmanus-delegation, web-fallback, research-automation-runner]
---

# Delegation Fallback

When a delegated worker fails at runtime (not at planning), **do not block on the user**. Fall back to direct execution using the agent's own tools. This pattern applies to OpenManus, Codex, Claude Code, and any subagent/runtime that can fail independently.

## Trigger

- Worker exits non-zero with `Connection error`, `AuthenticationError`, `APIConnectionError`
- Worker times out at the 420s tool cap with no receipt
- Worker fails before first LLM call (missing runtime, bad config, unreachable endpoint)
- Worker reports `status: failed` with no `receipt.json`

## Core Rule

**A worker failure is not a task failure.** The agent that spawned the worker has its own tools (`web_search`, `web_extract`, `terminal`, `execute_code`, `read_file`). When the worker can't run, do the work directly and report what you produced. Only stop for true blockers (irreversible actions, secrets, explicit user gates).

## Fallback Patterns

### OpenManus worker fails (API key / runtime / network)

1. Diagnose from stderr:
   - `AuthenticationError` / 401 → `api_key_env` points to invalid key in `.hermes/.env`
   - `Connection error` → LLM endpoint unreachable (llama-server down, wrong URL)
   - `failed to remove directory \.venv\Lib` → `runtime_command` not set, `uv run` tried to rebuild repo venv
   - `error: every wide-research item needs a non-empty prompt` → wrong `items` schema (object vs string)
2. If fixable in <30s (set `runtime_command`, restart llama-server), fix and retry ONCE.
3. If not fixable (no API key, llama-server binary missing), **fall back to direct research**:
   - `web_search` with multiple query angles (4-8 parallel queries)
   - `web_extract` on the top URLs (char_limit=12000-15000 per page)
   - `execute_code` to parse/merge results
   - Synthesize a report from the extracted content
4. Report: "OpenManus は [reason] で稼働できなかったため、直接リサーチしました。" + the report.

### Codex / Claude Code CLI fails (auth / timeout / sandbox)

1. Check `stderr` for auth vs timeout vs sandbox denial.
2. If auth: suggest `codex login` / `claude login` to user, fall back to direct execution meanwhile.
3. If timeout: the task is too big for the CLI's context; decompose and run directly.
4. If sandbox denial: preserve the sandbox and authorization boundary. Use an
   already authorized equivalent within scope, or request approval if scope must
   change. Never bypass a denied operation by switching tools.

### Subagent (delegate_task) fails

1. Check the child's final summary for the failure reason.
2. If the child hit a tool error (not a reasoning failure), retry the task directly in the parent using the same tools the child would have used.
3. If the child's reasoning was flawed, steer it via `delegate_task(action='steer')` rather than abandoning it.

## When NOT to Fall Back

- The task requires the worker's specific capabilities (e.g., Daytona sandbox, browser automation with persistent login state) AND no equivalent exists in the parent.
- The user explicitly asked to wait for the worker.
- The failure is in the worker's reasoning (not infrastructure) — steer or restart instead.

## Verification

After fallback delivery:
- Confirm the report covers the same topics the worker was asked about.
- Cite sources (URLs) so the user can verify.
- Note any gaps the worker might have filled (e.g., "OpenManus would have browsed interactively; this is static extraction").

## Pitfalls

- **Don't retry the same failing worker 3x.** One retry after a fix attempt; then fall back.
- **Don't pretend the worker ran.** Be transparent: "Worker failed, did it directly."
- **Don't block on user input for fixable issues.** Fix and retry once; only ask if the fix needs secrets or irreversible changes.
- **420s cap is not a failure.** If the worker is still running past 420s, read its `receipt.json` — it may have completed normally.
