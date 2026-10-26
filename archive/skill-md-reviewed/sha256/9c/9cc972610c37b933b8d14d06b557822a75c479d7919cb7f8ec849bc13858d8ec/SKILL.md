---
name: delegation-tuning
description: Tune Hermes delegation for parallel subagent execution.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata.hermes.category: devops
metadata.hermes.config:
  delegation.max_concurrent_children: int
  delegation.provider: string
  delegation.model: string
  delegation.max_spawn_depth: int
  delegation.orchestrator_enabled: bool
  delegation.subagent_auto_approve: bool
  delegation.child_timeout_seconds: int or null
---

## When to Use
Use this skill when you need to run multiple subagents in parallel via `delegate_task` and want to optimize throughput, reduce latency, or avoid hitting provider rate limits. Typical scenarios include:
- Running independent research tasks concurrently.
- Parallel code review or linting across multiple files.
- Batch processing of data where each chunk can be handled by a subagent.

## Prerequisites
- Hermes Agent v0.19.0 or later.
- A working LLM provider configured for subagents (see `delegation.provider` and `delegation.model`).
- Sufficient quota/rate limits on the chosen provider to handle increased concurrent requests.

## How to Run
Adjust the delegation settings in `~/.hermes/config.yaml` (or via `hermes config set`) then run your delegated task as usual. No special command is needed; the settings apply automatically to any `delegate_task` call.

## Procedure
1. **Set concurrency level**
   Increase `delegation.max_concurrent_children` to the desired number of parallel subagents (default 3).
   Example: `hermes config set delegation.max_concurrent_children 4`

2. **Choose provider and model for subagents**
   By default subagents inherit the parent's provider/model. To override, set:
   - `delegation.provider` (e.g., `openai`, `nous`, `anthropic`)
   - `delegation.model` (e.g., `qwen3`, `gpt-4o-mini`)
   Leave blank to inherit.

3. **Control nesting depth**
   Set `delegation.max_spawn_depth` to allow orchestrator subagents to spawn their own workers.
   - `1` (default): flat tree – only the parent can spawn workers.
   - `2` or higher: enables nested orchestration.

4. **Enable orchestrator role**
   Ensure `delegation.orchestrator_enabled` is `true` (default) if you plan to use `role: orchestrator` in your delegation calls.

5. **Optionally allow auto‑approval of dangerous commands in subagents**
   Set `delegation.subagent_auto_approve: true` only if you trust the subagent's actions and want to skip approval prompts (use with caution).

6. **Set a wall‑clock timeout per subagent (optional)**
   Configure `delegation.child_timeout_seconds` (seconds) to kill stalled subagents.
   Set to `null` or `0` to disable (default).

7. **Test the configuration**
   Run a simple parallel delegation to verify behavior, e.g.:
   ```
   hermes -z "Use delegate_task to run four tasks in parallel: each should echo its number (1‑4) and sleep 1 second. Return the results as a list."
   ```
   Observe that total time approximates the longest child runtime (≈1 s + overhead) rather than the sum.

## Verification
- Check that the number of concurrent subagent processes matches `delegation.max_concurrent_children` (visible via `hermes process list` or the delegation spinner in the TUI).
- Confirm that child agent logs show the expected provider/model (if overridden).
- Ensure that increasing `max_concurrent_children` reduces overall wall‑time for embarrassingly parallel workloads, up to the point of provider rate‑limit or resource saturation.
- If you see frequent `child_timeout` errors, increase `child_timeout_seconds` or investigate the subagent's workload for stalls.

## Pitfalls
- Raising `max_concurrent_children` too high can cause provider-side rate-limit errors (HTTP 429). Monitor logs and back off if needed.
- **Bounded fan-out APIs (e.g. `openmanus_wide_research`) take `items` as an array of plain strings.** Nesting objects or arrays (`[{"item": "..."}]`, `[["..."]]`) fails validation with `every wide-research item needs a non-empty prompt` before any worker spawns. Build each prompt yourself and merge sub-questions into one string per item.
- **`dry_run` defaults to true.** Supplying `allow_side_effects` + `acknowledge_side_effects` is *not* enough to go live — a response of `"status": "planned"` with no `exit_code` means nothing ran. Pass `dry_run: false` explicitly and treat any item lacking `exit_code` as not executed.
- **Host-side synthesis can fail after the workers succeed.** With `synthesize: true`, a host-LLM 429/limit error leaves valid per-item `receipt.json` files on disk. Read those directly rather than re-running the fan-out, or rerun with `synthesize: false`.
- **A worker failing at step 1 with `APIConnectionError` is an endpoint/model-name mismatch, not a network problem.** Every retry repeats the failure because the configured worker model name must match what the endpoint actually serves (check `GET <base_url>/v1/models`). Align the name or switch to a fast hosted model before retrying.
- Setting `delegation.model` to a model not supported by the chosen provider will cause fallback errors; verify compatibility.
- Enabling `subagent_auto_approve` can let subagents run destructive commands without oversight; only enable in trusted, sandboxed contexts.
- Nested delegation (`max_spawn_depth` > 1) increases API usage multiplicatively; plan quotas accordingly.
- **Delegation capture failure**: If you see repeated `Delegation owner exited before recording a terminal result; outcome unknown` errors across multiple jobs, the delegation layer may be broken. In this case, bypass delegation entirely by running scripts directly in foreground mode using `terminal(command="py -3 script.py", workdir="path/to/script")` to capture full output and exit codes.

## Debugging Delegation Failures
When delegation consistently fails to capture results (showing `status=unknown` or `Delegation owner exited before recording a terminal result`):

1. **Pause affected cron jobs** to stop the delegation loop:
   ```bash
   cronjob action=pause job_id=<job_id>
   ```

2. **Run the script directly in foreground mode** to capture actual output:
   ```bash
   terminal command="py -3 C:\\path\\to\\script.py" timeout=180 workdir="C:\\path\\to\\script\\dir"
   ```

3. **Examine the script directly** to identify failure points:
   ```bash
   read_file path="C:\\path\\to\\script.py"
   ```

4. **Fix identified issues** (OAuth tokens, locks, timeouts, etc.) then resume the cron job.

This approach bypasses the broken delegation capture mechanism and provides reliable debugging visibility.

## Quick Reference
| Setting | Example | Effect |
|---------|---------|--------|
| `delegation.max_concurrent_children` | `4` | Number of subagents that can run in parallel per delegation call. |
| `delegation.provider` | `openai` | LLM provider used by subagents (blank = inherit). |
| `delegation.model` | `qwen3` | Model name used by subagents (blank = inherit). |
| `delegation.max_spawn_depth` | `2` | Allows orchestrator subagents to spawn their own workers. |
| `delegation.orchestrator_enabled` | `true` | Enables the `orchestrator` role for subagents. |
| `delegation.subagent_auto_approve` | `false` | When `true`, skips dangerous‑command prompts in subagents. |
| `delegation.child_timeout_seconds` | `120` | Hard wall‑clock limit per subagent (seconds); `null` disables. |