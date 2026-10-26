---
name: delegation-performance-tuning
description: Optimize Hermes delegation (sub‑agent spawning) for true parallel execution and minimal latency.
version: 1.0
author: Hermes Agent
tags: [delegation, performance, concurrency, config]
---
# Delegation Performance Tuning

## When to Use
Use this skill when you need to improve the throughput of Hermes delegation (sub‑agent spawning) – e.g., running multiple independent tasks in parallel, reducing wall‑clock time for batch workloads, or diagnosing why delegation appears sequential despite `max_concurrent_children` being set >1.

## Quick Checklist
- [ ] Verify `delegation.max_concurrent_children` >= desired parallelism (`hermes config get delegation.max_concurrent_children`).
- [ ] Ensure delegation uses the same provider/model as the parent (inherit or explicitly set) to avoid costly per‑child model init.
- [ ] Disable unnecessary reasoning overhead for child agents (`delegation.reasoning_effort: low`).
- [ ] Confirm the delegated model endpoint is reachable (no stray `base_url` pointing to a dead service).
- [ ] Run a small benchmark (e.g., 4× 1‑second sleep tasks) and measure wall‑clock time with `time hermes -z "..."`.
- [ ] If benchmark still slow, check delegation logs for fallbacks or model‑load overhead.

## Detailed Procedure

1. **Inspect current delegation config**
   ```bash
   hermes config get delegation
   ```
   Look for:
   - `provider` (should match parent’s provider, e.g., `moa`)
   - `model` (empty string → inherit parent’s model)
   - `base_url` / `api_key` (empty → inherit)
   - `max_concurrent_children` (desired parallelism)
   - `reasoning_effort` (optional, set to `low` to reduce per‑child token overhead)

2. **Fix common misconfigurations**
   - If `provider` is set to an external service (e.g., `openai`) but `base_url` points to a non‑existent localhost port, delegation will timeout and fall back to sequential retries.
   - Correct by inheriting or pointing to a working endpoint:
     ```bash
     hermes config set delegation.provider moa
     hermes config set delegation.model ""        # inherit
     hermes config set delegation.base_url ""     # inherit
     hermes config set delegation.api_key ""      # inherit
     hermes config set delegation.reasoning_effort low
     ```

3. **Validate endpoint reachability (if using a custom endpoint)**
   ```bash
   curl -s http://<host>:<port>/v1/models
   ```
   Should return a JSON list of models; otherwise fix the service or revert to inheritance.

4. **Run a representative benchmark**
   ```bash
   time hermes -z "Use delegate_task to run four tasks in parallel: each task should echo its number (1-4) and sleep 1 second. Return the results as a simple list."
   ```
   Expected output: a list like `[1,2,3,4]` (order may vary) and total time ≈ 1‑2 seconds.

5. **Interpret results**
   - **≈1‑2 s**: Delegation is truly parallel; each child is reusing the parent’s model/client.
   - **>>10 s per child**: Indicates per‑child model initialization or fallback retries. Re‑check config inheritance and endpoint health.
   - **Mixed times**: Some children may be falling back; inspect logs (`hermes logs --follow`) for warnings.

6. **Optional: Reduce child overhead further**
   - Turn off child memory/context inheritance if not needed:
     ```bash
     hermes config set delegation.skip_memory true
     hermes config set delegation.skip_context_files true
     ```
   - Limit child toolsets to only what’s necessary (e.g., `terminal`, `file`) to avoid loading heavy toolsets.

## Pitfalls & How to Avoid Them
- **Pitfall:** Setting a custom `base_url` that points to a dead or misconfigured local server causes each child to timeout and fall back to the default provider, adding latency and breaking parallelism.
  - **Fix:** Either ensure the custom server is running and healthy, or set `base_url` and `api_key` to empty strings to inherit the parent’s working configuration.
- **Pitfall:** Leaving `reasoning_effort` at its default (often `medium` or `high`) makes each child spend extra tokens on internal chain‑of‑thought, increasing latency.
  - **Fix:** Explicitly set `delegation.reasoning_effort: low` (or `none` if supported) for lightweight tasks.
- **Pitfall:** Forgetting that each child agent re‑initializes its own LLM client unless the config fields are left empty (inherit). Explicitly setting `model` or `provider` to a different value forces a new client creation.
  - **Fix:** Keep `model`, `provider`, `base_url`, `api_key` empty to inherit, or explicitly set them to the same values as the parent.

## Verification Steps
After applying changes, re‑run the benchmark and confirm:
1. Output list contains all expected numbers.
2. Total time is close to the slowest single task plus minimal overhead.
3. No fallback warnings appear in the delegation logs.

## References
- See `references/delegation-config-options.md` for a full list of delegation‑related config keys.
- See `templates/delegation-benchmark.txt` for a ready‑to‑run benchmark command.
- See `scripts/check-delegation-endpoint.sh` for a quick connectivity test.

---
*This skill encapsulates the workflow discovered during the session on 2025‑07‑25 where a mis‑routed OpenAI endpoint caused sequential delegation, and correcting the delegation config to inherit the parent’s MoA setup restored true parallel execution.*