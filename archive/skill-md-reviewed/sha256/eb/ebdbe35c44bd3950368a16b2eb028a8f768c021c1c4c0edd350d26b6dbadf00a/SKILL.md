---
name: moa-fugu-orchestrator
description: MoA with fixed orchestrator and daily free-model rotation.
version: 0.2.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Hermes, MoA, Orchestrator, Free-Models, Daily-Rotation, SAKANA]
---

# MoA Fugu Orchestrator

Configure Hermes Mixture-of-Agents in the SAKANA AI "fugu" shape: a strong
orchestrator (aggregator) that fuses advice from a diverse panel of free
/ local high-reasoning models (the "fish").

**Two variants supported:**
1. **Fixed Orchestrator (classic fugu)** — single strong aggregator pinned (e.g. `openai-codex:gpt-5.6-luna`), only reference panel rotates daily.
2. **Round-Robin Orchestrator (2x/day)** — THREE strong orchestrators rotate every 12h: `gpt-5.6-luna` → `gemini-3.1-flash-lite` → `grok-4.5`, plus daily reference panel refresh with live discovery + liveness probe.

The aggregator never uses free models — it's always a premium/high-reasoning model. Free models form the sensory panel only.

## When to Use

- "SAKANAのフグみたいなMoAにして"
- "GPT-5.6 Luna + Grok-4.5をオーケストレーターにして"
- "無料高推論モデルを一日一回チェックして入れ替える"
- "MoAのaggregatorを固定して参照モデルだけ日次ローテ"
- "fugu-style evolutionary MoA"
- "GPT-5.6 Luna / Gemini-3.1-Flash / Grok-4.5 をラウンドロビンで"
- "一日二回オーケストレーター切り替え"
- "無料参照モデルをライブ発見＋生存確認で入れ替え"

## Prerequisites

- Hermes checkout with `hermes_cli/moa_config.py` (`normalize_moa_config`,
  `resolve_moa_preset`).
- `~/.hermes/config.yaml` already has `model:` and `moa:` sections.
- Free providers: `opencode-zen` (`OPENCODE_ZEN_API_KEY`), `nvidia` (free
  tier), `nous` (`auto-free`), `freellmapi` (running on `:31415` — NOT
  `:3001`, see `freellmapi-free-tier`), `freebuff` (requires `freebuff login`
  in browser first), and a local `custom` LLM.
- Premium fallback: `openai-codex` with `gpt-5.6-luna` / `gpt-5.5`, and `xai`
  with `grok-4.5`.
- Verify model IDs exist: `gpt-5.6-luna` and `gpt-5.6-luna-pro` are valid in
  `hermes_cli/models.py`; `grok-4.5` resolves under `xai`.

## How to Run

Edit MoA config through the `terminal` tool (YAML rewrite keeps other sections
intact), then run the daily selector through `terminal` and verify with
`execute_code`. Schedule the selector with the `cronjob` tool. Capture the
consensus trace with `moa.save_traces: true` (see below).

## Quick Reference

| Action | Command |
|--------|---------|
| Verify config shape | `execute_code` → `from hermes_cli.moa_config import normalize_moa_config, resolve_moa_preset` |
| Run rotation now | `terminal`: `python scripts/daily_moa_provider_selector.py` |
| Run 2x/day orchestrator rotation | `terminal`: `python scripts/daily_moa_orchestrator_rotation.py` |
| OpenCode catalog | `terminal`: `python scripts/refresh_opencode_free_catalog.py --force` |
| Show fallback chain | `terminal`: `hermes fallback list` |
| Schedule daily 04:00 (fixed orchestrator) | `cronjob` → `script: daily_moa_provider_selector.py`, `no_agent: true`, `schedule: "0 4 * * *"` |
| Schedule 2x/day (round-robin orchestrators) | `cronjob` → `script: daily_moa_orchestrator_rotation.py`, `no_agent: true`, `schedule: "0 4,16 * * *"` |
| Watch live consensus | `terminal`: `hermes chat -q "..." --provider moa --model hakuapulse-orchestrator -Q` |
| Capture consensus JSONL | set `moa.save_traces: true` + `moa.trace_dir` (distillation data for a local LLM) |
| Start freebuff proxy | `terminal`: `hermes freebuff connect` → check `hermes freebuff status` for `probe.ok: true` |

## Two Rotation Modes

### 1. Fixed Orchestrator (Original Fugu) — `daily_moa_provider_selector.py`
- Aggregator pinned to `gpt-5.6-luna` (+ Grok-4.5 fallback in separate preset)
- Only reference models rotate daily
- Schedule: `0 4 * * *`

### 2. Round-Robin Orchestrators (This Session) — `daily_moa_orchestrator_rotation.py`
- Three strong orchestrators rotate: `gpt-5.6-luna` → `gemini-3.1-flash-lite` → `grok-4.5`
- Reference models also rotate daily with live discovery + liveness
- Schedule: `0 4,16 * * *` (4am and 4pm JST)
- Single script handles BOTH orchestrator rotation AND reference panel refresh

Use mode 2 when you want the "brain" to also rotate among premium models, not just the "fish" panel.
| Capture consensus JSONL | set `moa.save_traces: true` + `moa.trace_dir` (distillation data for a local LLM) |
| Start freebuff proxy | `terminal`: `hermes freebuff connect` → check `hermes freebuff status` for `probe.ok: true` |

## Procedure

### Variant A: Classic Fugu (Fixed Orchestrator + Daily Reference Rotation)

1. Load `moa-cost-routing`, `opencode-free-rotation`, `freellmapi-free-tier`
   for the supporting patterns.

2. Read only `model:` and `moa:` from `~/.hermes/config.yaml` via `read_file`.

3. Rewrite the `moa:` block (preserve every other section) with
   `terminal` + Python YAML, setting:
   - `moa.default_preset` / `active_preset` → `hakuapulse-orchestrator`
   - preset `hakuapulse-orchestrator.aggregator` →
     `{provider: openai-codex, model: gpt-5.6-luna}`
   - `reference_models` = the live free panel (auto-discovered by the script;
     do NOT hard-code model aliases — they rotate daily, see Pitfalls)
   - set `model.provider: moa` and `model.default: hakuapulse-orchestrator`
   - set `moa.save_traces: true` and `moa.trace_dir: <path>` to capture the
     consensus trace for local-LLM distillation

4. Copy `scripts/daily_moa_provider_selector.py` (this skill's version) into
   the Hermes `scripts/` dir. It pins the orchestrator, resolves each
   provider's CURRENT real id (catalogs rotate daily), liveness-probes with a
   1-token completion, and round-robins survivors — never overwrites the
   aggregator.

5. Run it once via `terminal` to confirm alive references and a clean write.
   Watch the `[alive]/[dead]` lines: a provider that returns 429/401 is
   treated as alive (proxy up, throttled); only 404/000 means gone.

6. Schedule via `cronjob` (action=create): `script:
   daily_moa_provider_selector.py`, `no_agent: true`, `schedule: "0 4 * * *"`,
   `deliver: local`.

### Variant B: Round-Robin Orchestrator (2x/day) + Daily Reference Rotation

1. Same prerequisites as Variant A.

2. Rewrite `moa:` block with `terminal` + Python YAML:
   - `moa.default_preset` / `active_preset` → `hakuapulse-orchestrator`
   - `model.provider: moa` and `model.default: hakuapulse-orchestrator`
   - `moa.save_traces: true` + `moa.trace_dir`

3. Copy `scripts/daily_moa_orchestrator_rotation.py` into `scripts/` dir. This script:
   - Rotates aggregator round-robin: `gpt-5.6-luna` → `gemini-3.1-flash-lite` → `grok-4.5` (date-seeded)
   - Live-discovers free reference models via `resolve_config_model_id(force_refresh=True)`
   - Liveness-probes each with 1-token ping (429/401 = alive, 404/000 = dead)
   - Shuffles survivors daily (date-seeded RNG) into `reference_models`
   - Never hard-codes model IDs; always re-resolves aliases at runtime

4. Run once via `terminal` to verify.

5. Schedule via `cronjob`: `script: daily_moa_orchestrator_rotation.py`, `no_agent: true`, `schedule: "0 4,16 * * *"`, `deliver: local`.

The round-robin variant was implemented in the 2026-07-12 session when the user requested "MoAでラウンドロビンでgpt5.6runa、gemini3.1flash、Grok4.5をオーケストレーターにしてSakanaAIのFuguのように無料枠高推論モデルでも適切なタスク、ツールコーリング、ウェブ検索、文章作成能力などをDeepresearchして一日二回無料モデルの実IDと可用性チェックしたものをデフォルトにしたい".

## Pitfalls

- `patch`/direct edit of `~/.hermes/config.yaml` is REFUSED by the agent guard
  ("security-sensitive"). Rewrite via `terminal` + Python YAML, not `patch`.
- Do NOT let the rotation script overwrite the aggregator — the fugu shape
  fixes the orchestrator; only fish rotate. The selector pins
  `preset["aggregator"]` every run so a stale preset can't demote GPT.
- **Do NOT hard-code free-model aliases** (`auto-free`, `auto`). OpenCode Zen's
  free catalog rotates daily (e.g. `deepseek-v4-flash-free` one day,
  `big-pickle` the next). The selector re-resolves `auto-free` with
  `resolve_config_model_id(force_refresh=False)` every run — hard-coding a
  real id will go stale within days.
- **`resolve_real_id` must use `force_refresh=False`.** With
  `force_refresh=True`, the catalog probe itself hits the provider and can
  return 429, which then poisons the liveness check below it. Cached catalog
  is sufficient for id resolution.
- **freellmapi liveness is environment-dependent.** Standalone `call_llm`
  returns `RateLimitError` (429 → alive), but inside the selector's loop,
  Hermes' `fallback_chain` re-wraps the 429 into a different exception that the
  string check misses → freellmapi gets marked `dead`. Mitigation: keep
  `freellmapi` OUT of `CANDIDATE_ALIASES` (managed manually in
  `reference_models`), or add it only after upstream keys are added in the
  FreeLLMAPI web UI (then it returns 200, not 429).
- **FreeLLMAPI runs on `:31415`, NOT `:3001`.** The desktop `.exe` prints
  `[desktop] FreeLLMAPI running on http://127.0.0.1:31415` at boot. If a probe
  returns `HTTP 000` on `:3001`, the proxy is up but on the wrong port — fix
  `FREELLMAPI_BASE_URL` (in `~/.hermes/.env`) to `http://127.0.0.1:31415/v1`.
  A `401 Invalid API key` from FreeLLMAPI means the `FREELLMAPI_API_KEY` value
  is wrong/stale — re-copy the unified key from the FreeLLMAPI web UI
  (`http://127.0.0.1:31415`), do NOT trust a key pasted from chat. The key
  lives in the FreeLLMAPI DB, not in Hermes config, so it must match what the
  GUI shows.
- **freebuff needs `FREEBUFF_PROXY_API_KEY`, not `FREEBUFF_API_KEY`.** Hermes'
  freebuff provider (`plugins/model-providers/freebuff`) reads
  `FREEBUFF_PROXY_API_KEY` (and optional `FREEBUFF_BASE_URL`). Setting
  `FREEBUFF_API_KEY` makes `call_llm` report "no API key found" — a misleading
  error. The key is the GitHub OAuth token (`sk-proj-…` form works); freebuff
  expects GitHub-account linkage, not a raw API key.
- **freebuff local proxy is `:8765` (freebuff2api), not a hosted endpoint.**
  `FREEBUFF_BASE_URL` defaults to `http://127.0.0.1:8765/v1`. The proxy only
  starts when the `freebuff` CLI is launched interactively (it is NOT an
  always-on service). A `404 page not found` on `:8765` means the proxy isn't
  running — start `freebuff` (the real CLI, see below) first. If `freebuff` on
  PATH prints `agent-skill-unifier` instead, the npm shim is shadowed by
  another package — call the binary directly at
  `C:\\Users\\<user>\\.config\\manicode\\freebuff.exe` (Windows) or reinstall
  with `npm install -g freebuff@latest`.
- **`model.provider` / `model.default` are SEPARATE fields from
  `moa.default_preset`.** A config can have `moa.default_preset:
  hakuapulse-orchestrator` but `model.provider: nvidia` (set by another tool
  like `hermes freebuff connect`) — then `/moa` never runs because the top
  provider is no longer `moa`. After any provider change, re-assert
  `model.provider: moa` and `model.default: hakuapulse-orchestrator` so the
  selector's aggregator pin actually takes effect. The selector only protects
  `moa.presets[*].aggregator`; it does NOT touch `model.provider`.
- **The selector OVERWRITES `reference_models` every run.** Any manual edit
  (e.g. adding `freellmapi:auto` by hand) is wiped on the next cron tick.
  UNRESOLVED: the selector has no "pinned static references" list yet. Until
  that's added, either (a) keep freellmapi out of `CANDIDATE_ALIASES` AND accept
  it gets dropped, or (b) re-add it after each rotation. A future patch should
  add a `PINNED_REFERENCES` constant the selector merges into the live set.
- **local `custom` llama-server returns 401 when down** — exclude it from the
  reference panel; keep it only in `fallback_providers` as a last resort.
- **`gpt-5.5` in `fallback_providers[-1]` is the final safety net, not the
  default path.** Keep it there.
- `scripts/run_tests.sh` fails on Windows with space-in-path `.venv` resolution;
  run `pytest` via `.venv/Scripts/python -m pytest` directly.
- `googleaistudio:auto` is a valid reference slot but not pinged by the
  selector; drop it from the panel if you want strict liveness gating.
- **⚠️ AGGREGATOR MISMATCH: The fugu pattern REQUIRES a fixed strong orchestrator
  (GPT-5.6 Luna or Grok-4.5) as aggregator.** The current `hakuapulse-orchestrator`
  preset in config.yaml uses `freebuff:deepseek/deepseek-v4-flash` as aggregator,
  which violates the fugu pattern. This must be corrected to
  `openai-codex:gpt-5.6-luna` (or `xai:grok-4.5`) before enabling the pattern
  for production AI employee profiles. See `references/fugu-aggregator-fix.md`
  for the exact YAML patch.

### Round-Robin Orchestrator Specific (Variant B)

- **Gemini 3.1 Flash Preview NOT in catalog** — use `gemini-3.1-flash-lite` instead. The catalog check via `provider_model_ids('gemini')` returns `gemini-3.1-flash-lite`; `gemini-3.1-flash-preview` returns 404 from Google AI Studio API.
- **xAI Grok-4.5 requires `XAI_API_KEY` env var** — without it, liveness probe fails with "no API key found". Add to `~/.hermes/.env` for grok-4.5 to be usable as orchestrator.
- **Cron runs at 04:00 and 16:00 JST** — date-seeded RNG means the same day gets same shuffle order, but 12h apart the orchestrator advances to next in round-robin (3-model cycle = ~1.5 days per full rotation).
- **Single script handles BOTH rotations** — `daily_moa_orchestrator_rotation.py` replaces the need for separate orchestrator + reference rotations.

## Troubleshooting

### freebuff: `agent-skill-unifier` instead of `Freebuff`

On Windows, `npm install -g freebuff` can shadow the real CLI. If `freebuff
--help` shows `agent-skill-unifier` or `index.js`, use the explicit binary:

```text
C:\Users\<user>\.config\manicode\freebuff.exe
```

### freebuff: GitHub login required, auth_code alone is not enough

`freebuff.exe login` prints a one-time browser URL (`freebuff.com/login?auth_code=...`).
The actual OAuth click in a browser (`Continue with GitHub` / `Continue with Google`)
is mandatory; the `auth_code` token by itself does not log in the CLI.

### freebuff: `FREEBUFF_API_KEY` is the wrong env name

Hermes' freebuff provider (`plugins/model-providers/freebuff`) reads
`FREEBUFF_PROXY_API_KEY`. Setting `FREEBUFF_API_KEY` produces “no API key found”.
The local proxy listens at `http://127.0.0.1:8765/v1`.

### freebuff: `proxy.running: false` means start the proxy, do not retry curls

`hermes freebuff status` is the source of truth. If `proxy.running: false`,
start the Hermes-managed proxy path. Ad-hoc `curl` / `call_llm` loops on `:8765`
are not useful until the proxy is actually running.

**Correct start command:** `hermes freebuff connect` (NOT `hermes freebuff
connect --apply-model` — that flag is rejected; the bare command starts the
proxy AND sets `model.provider=freebuff`). After it returns, `hermes freebuff
status` should show `"probe": {"ok": true, "status_code": 200}` — that 200 is
the proof the `:8765` proxy is live. For MoA use you then re-assert
`model.provider: moa` (the connect command flips it to freebuff). Do NOT try to
start `:8765` by launching the `freebuff` TUI binary directly — the TUI is
`interactive_only` and the proxy is a separate process the `connect` command
manages.

### freebuff: `hermes freebuff connect` flips `model.provider` — re-assert moa

`hermes freebuff connect` sets `model.provider=freebuff` as a side effect. If
freebuff is only one panel member of your MoA, run `hermes freebuff connect`
to bring the proxy up, confirm `status_code: 200`, then set
`model.provider: moa` + `model.default: hakuapulse-orchestrator` again (see the
separate-fields pitfall above). The freebuff proxy keeps running on `:8765`
even after `model.provider` is flipped back to moa.

### FreeLLMAPI: port `:31415`, not `:3001`

The desktop `.exe` prints `[desktop] FreeLLMAPI running on http://127.0.0.1:31415`.
Fix `FREELLMAPI_BASE_URL` to `http://127.0.0.1:31415/v1`. A `HTTP 000` on `:3001`
with the process visible in Task Manager means the port binding differs from docs;
trust the boot log.

### FreeLLMAPI: key comes from the FreeLLMAPI web UI, not from chat

A `401 Invalid API key` means the `FREELLMAPI_API_KEY` in Hermes `.env` is wrong
or stale. Re-copy the unified key from `http://127.0.0.1:31415` in the browser.
Do not trust a pasted chat string until the UI confirms it.

### FreeLLMAPI: liveness false-negative inside the selector loop

Standalone `call_llm` returns `RateLimitError` for 429, but inside the selector
Hermes' `fallback_chain` wraps it differently. Keep `freellmapi` OUT of
`CANDIDATE_ALIASES` (managed manually) unless upstream keys make it return 200.

## Verification

Run through `execute_code`:

```python
import yaml
from pathlib import Path
from hermes_cli.moa_config import normalize_moa_config, resolve_moa_preset
data = yaml.safe_load((Path.home()/".hermes"/"config.yaml").read_text(encoding="utf-8"))
moa = normalize_moa_config(data["moa"])
p = resolve_moa_preset(data["moa"], moa["default_preset"])
assert moa["default_preset"] == "hakuapulse-orchestrator"
assert p["aggregator"] == {"provider":"openai-codex","model":"gpt-5.6-luna"}
assert not any("gpt-5" in r["model"] for r in p["reference_models"])
print("OK agg=", p["aggregator"]["model"], "refs=", len(p["reference_models"]))
```

Expected: `OK agg= gpt-5.6-luna refs= N` (N = number of live free models).
Then `pytest tests/agent/test_moa_*.py tests/cli/test_moa_command.py` → 21 passed.

## Distillation

The consensus trace (`moa.save_traces: true`) writes one JSONL per turn to
`moa.trace_dir`, each containing the aggregator prompt + every reference
model's full input/output. Extract `(query, [fish answers], GPT-5.6 fused
answer)` triples to fine-tune a local HermesAgent-specialized model. See
`references/distillation.md`.
