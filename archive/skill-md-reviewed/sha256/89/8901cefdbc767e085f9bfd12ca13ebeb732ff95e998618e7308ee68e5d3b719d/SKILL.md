---
name: hermes-config-tuning
description: Adjust Hermes configuration for NVIDIA fallback, increased timeouts, and cron stability.
category: devops
---

# Hermes Configuration Tuning

This skill outlines how to tune Hermes Agent configuration for better performance, reliability, and to enable NVIDIA model fallback.

## When to Use

- When cron jobs start but their content shows provider/model errors such as `404 Model not found`, `gpt-5.5-low model is not supported`, or paid/free catalog mismatches.
- When experiencing cron job delivery errors related to missing `aiohttp` or LINE platform.
- When you want to extend timeouts for long-running tasks (e.g., memory consolidation, delegation).
- When you want to configure stable model and fallback routing for gateway/cron runs.
- When adjusting memory sleep intervals for consolidation.

## Local llm / llama-server configuration
Use this section when routing Hermes through a local `llama-server` (llama.cpp) endpoint instead of remote providers.

**Minimal config (copy into `~/.hermes/config.yaml`)**
```yaml
model:
  provider: custom
  default: <model-id>
  base_url: http://127.0.0.1:8080/v1
  api_key: local
  context_length: 65536
  api_mode: chat_completions

fallback_providers:
  - provider: custom
    model: <fallback-model-id>
    base_url: http://127.0.0.1:8081/v1
    api_key: local
```

**llama-server start command (RTX 3060/3080 class)**
```bash
llama-server \
  --model <model>.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 65536 \
  --n-gpu-layers 99 \
  --flash-attn on \
  --cache-type-k f16 \
  --cache-type-v turbo4 \
  --jinja \
  --cont-batching \
  --parallel 1 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --reasoning off \
  --reasoning-budget 0 \
  --spec-type ngram-mod \
  --spec-ngram-mod-n-match 24 \
  --spec-ngram-mod-n-min 48 \
  --spec-ngram-mod-n-max 64
```

**Key rules**
- Tool calling via llama.cpp depends on a **build with `LLAMA_TOOLS=ON`**, not on a `-ninja` runtime flag.
- `-G Ninja` is a CMake generator option for faster builds; it has no effect on the runtime executable.
- Tool grammar failures in llama.cpp are auto-recovered by Hermes via the `llama_cpp_grammar_pattern` retry path.
- Hermes auto-detects 8080/8081/8082 as local-secretary endpoints in `llama_fallback_runtime.py`.
- If the local endpoint stops, remote provider fallback should still work; verify with a one-shot before relying on local only.

**Windows verification**
- `scripts/windows/check-local-llm.ps1` checks: `/v1/models`, context size, `chat/completions`, and structured `tool_calls`.
- `scripts/windows/start-llama-secretary.ps1` is the preferred launcher because it resolves HERMES_LLAMA_* env, retries GPU layer steps, and surfaces stderr/stdout logs.

**Backend precedence on this platform**
- On Windows, use the bundled PowerShell launcher scripts under `scripts/windows/` rather than typing a raw `llama-server` command in the terminal tool; that avoids PATH and PowerShell quoting issues when invoking long argument lists.

**Build prerequisites**
- `LLAMA_TOOLS=ON` at CMake configure time is required for tool-call grammar support.
- `Ninja` (`-G Ninja`) is optional; it only affects build speed, not runtime behavior.

## Steps
1. **Check the real failing layer before changing config**:
1. **Check the real failing layer before changing config**:
   - `hermes cron status` confirms the scheduler is alive.
   - `hermes cron list` identifies `last_status`, `last_delivery_error`, and affected job IDs.
   - Inspect recent `~/.hermes/logs/gateway.log`, `errors.log`, and `agent.log` for the concrete provider/model line. Treat `404` as ambiguous until the log says whether it is a web URL, delivery endpoint, or model catalog error.

2. **For cron model 404s, prefer a known-working provider/model pair**:
   ```yaml
   model:
     api_key: ''
     api_mode: ''
     base_url: ''
     default: auto-free
     max_tokens: 8192
     provider: opencode-zen

   fallback_providers:
   - model: auto-free
     provider: opencode-zen
   - model: nvidia/nemotron-3-super-120b-a12b
     provider: nvidia
   - base_url: http://127.0.0.1:8080/v1
     key_env: LOCAL_API_KEY
     model: huihui-gemma-4-12b
     provider: custom
   ```
   Verify with a one-shot before restarting the gateway:
   ```bash
   hermes chat -Q --provider opencode-zen --model auto-free -q '日本語で一言だけ: cronモデル疎通OK'
   ```

3. **Avoid stale GPT-5.5/Codex and Nous-free aliases in cron defaults**:
   - `gpt-5.5-low` can be unsupported for a ChatGPT Codex account.
   - `provider: nous` + `auto-free` or `nvidia/...:free` may resolve to Hermes/Nuos catalog 404s when those aliases are not present.
   - If OpenCode Zen reports `auto-free` unsupported once but then routes to a concrete model such as `big-pickle`, confirm logs show successful follow-up API calls before declaring failure.

4. **Ensure aiohttp is installed** (only if logs show the dependency error):
   ```bash
   pip install aiohttp
   ```

5. **Enable LINE platform in config** (if using LINE notifications):
   ```yaml
   platforms:
     line:
       streaming: false
   ```

6. **Increase timeouts** in `.hermes/config.yaml`:
   - `delegation.child_timeout_seconds: 1200`
   - `agent.clarify_timeout: 1200`
   - `terminal.timeout: 1200`
   - `agent.gateway_timeout_warning: 1200`
   - `memory.sleep.idle_after_seconds: 1200`

7. **Adjust memory sleep settings** (optional):
   - `memory.sleep.idle_after_seconds: 1200` (already above)
   - Keep `wake_greeting: "\u304A\u306F\u3088\u3046\uFF01\u30DC\u30D6\u306B\u3083\u3093\u3002"`

8. **Save config, restart Hermes Gateway, then verify a real cron run**:
   ```bash
   hermes gateway restart
   hermes cron status
   hermes cron run <job_id>
   ```
   Tail logs until either the job completes or the failure mode changes. A successful fix should show the new provider/model in `agent.log`, not the old `gpt-5.5-low` / Nous 404 sequence.

## Verification

- Run a one-shot model probe before touching cron: `hermes chat -Q --provider opencode-zen --model auto-free -q '日本語で一言だけ: cronモデル疎通OK'`.
- Restart the gateway after config edits so the embedded cron ticker reloads settings.
- Trigger one affected job with `hermes cron run <job_id>` and inspect logs for the new provider/model.
- Confirm the original error sequence is gone: no `gpt-5.5-low` unsupported line and no `provider=nous model=auto-free` or `nvidia/...:free` catalog 404.
- If the job is long-running, do not rely only on `hermes cron list`; `last_run_at` may remain stale while the job is still running. Check `agent.log` for active `cron_<job_id>_...` calls.

## Pitfalls

- Do not set `idle_after_seconds` too low; it may cause premature memory consolidation.
- Ensure the LINE platform is only added if you use LINE notifications; otherwise, it can be omitted.
- Do not assume every 404 in cron is a web-content 404. Model-provider 404s are common and are only visible in `errors.log`/`agent.log` provider lines.
- Avoid encoding stale catalog aliases as durable fallbacks. Confirm the provider/model pair with a real one-shot probe first.
- A first `opencode-zen auto-free` warning such as `Model auto-free is not supported` can be followed by successful routing to a concrete free model. Judge by subsequent API calls and final job status.

## References

- See `references/cron_fix_details.md` for the exact error and resolution steps.
- See `references/cron-model-404-gpt55.md` for the GPT-5.5/Codex and Nous alias 404 debugging pattern.
- See `references/llama-server-tool-calling.md` for Windows `llama-server` tool-calling requirements and preferred launch path.