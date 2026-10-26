---
name: local-llm-server
description: Serve local GGUF models and verify Nimble evaluations.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [LLM, GGUF, PrismL, Nimble, Verification]
---

# Local GGUF Serving and Nimble Verification

Serve the exact requested GGUF, register its live ID without changing the primary model, and evaluate it through the actual Nimble plugin. This does not train weights, optimize refusal removal, certify reference labels, or establish capability retention without a matching baseline. The bundled helpers use Python's standard library plus the already-installed Hermes plugin and inspected Nimble adapter; they do not restart services or write profile configuration.

## When to Use

- 「このGGUFをPrismL版llamaサーバーで動かして」 or replace a live local model.
- 「モデルピッカーを更新して」 without switching the current chat or primary model.
- 「Jevの代わりにNimbleで各項目チェックして」 or evaluate every saved holdout row.
- Verify model identity, scorer probabilities, grouped metrics, or evidence delivery.

## Prerequisites

- The literal requested GGUF, a compatible `llama-server` binary, and sufficient disk/RAM/VRAM. PQ2_0 requires actual PQ2_0 support; another two-bit format is not equivalent.
- Hermes CLI and the active profile. `HERMES_HOME` selects that profile; never borrow another profile's credentials or edit its state.
- For Nimble: installed `plugins.nimble_scorer`, its `handle_score`/`handle_status` handlers, and an inspected checkout exposing `nimble.evaluation.evaluate_pilot.adapt_input` and `assess`.
- The tested local endpoint is `http://127.0.0.1:8080` without authentication. Do not copy the empty credential into an authenticated service.
- Inspect plugin configuration under `plugins.entries` and its current `CONFIG_ALIASES`. The batch helper requires the declared `n_probs` and `max_input_tokens` to match that configuration; it never changes them.
- Resolve Bash variables `PYTHON`, `ROOT`, `SKILL_DIR`, `LLAMA_SERVER`, `MODEL`, `ALIAS`, `UPSTREAM`, `DATASET`, and fresh `RUN_DIR` from real files. Use the repository interpreter, not an unrelated global Python.

## How to Run

Invoke commands through `terminal`, using `background=true` for a server and `notify=true` for a bounded long evaluation. If Windows tools return `command length exceeds safe limit`, use `execute_code` with `subprocess`, explicit argv/cwd, UTF-8 decoding with `errors="replace"`, and detached logging for long jobs; do not retry the broken terminal repeatedly.

Read the focused PrismL recipe with `skill_view(name='local-llm-server', file_path='references/prisml-nimble-verification.md')`. The workflow is one sequence: discovery → scoped launch → live checks → picker refresh → frozen evaluation → raw-output cross-check → delivery.

For a ready server and configured plugin, invoke through `terminal`:

```bash
"$PYTHON" "$SKILL_DIR/scripts/nimble_holdout.py" --repo "$ROOT" --nimble-src "$UPSTREAM" --dataset "$DATASET" --model "$MODEL" --alias "$ALIAS" --base-url http://127.0.0.1:8080 --output "$RUN_DIR" --n-probs 20000 --max-input-tokens 8192
```

The settings are observed conditions, not universal tuning recommendations. The helper derives the dataset count, writes each result before advancing, refuses an existing output directory, and returns 2 if any measurements are invalid. A failed or repaired run gets a new ID; preserve its predecessor.

## Quick Reference

- `GET /health`
- `GET /props`
- `GET /slots`
- `GET /v1/models`
- `POST /v1/chat/completions`
- `nimble_status`, `nimble_validate_schema`, `nimble_score`
- `hermes config path`; `hermes fallback list`
- `hermes config set custom_providers.N.model <live-id>`
- `hermes config set custom_providers.N.context_length <resolved-context>`
- `scripts/nimble_holdout.py`: plugin-backed full evaluation.
- `scripts/verify_nimble_run.py`: stdlib-only verification from saved raw probabilities.

## Procedure

1. **Discover and separate scope.** Use `read_file`/`search_files` and process inspection through `terminal` to locate the requested GGUF, binary, listener PID, full argv, creation time, and live `/props` path. Record rollback argv. Alias, filename similarity, and equal file size are not weight identity. Serving selection, picker registration, active chat, primary model, and autostart are separate changes.

2. **Replace only the authorized service.** Inspect `/slots`; wait for an actual idle state within a bounded observation window. If active requests persist, ask whether to interrupt or defer. Recheck PID identity immediately before termination; never kill every `llama-server` process. Preserve working settings unless a change is requested or justified. A tested PrismL launch through `terminal` was:

   ```bash
   "$LLAMA_SERVER" -m "$MODEL" -c 65536 --parallel 1 -ngl 99 -fa on -ctk q4_0 -ctv q4_0 --jinja --alias "$ALIAS" --host 127.0.0.1 --port 8080
   ```

   Confirm that exact build supports these flags. Filter obsolete `LLAMA_ARG_*`/`LLAMA_TURBOQUANT_*` only in the child environment when needed; preserve the parent's environment and unrelated services.

   If the service refuses to come up, read the launcher's own guards before changing anything — a `throw "Missing GGUF: $model"` from `Test-Path` is **silent to the app**, surfacing only as an endpoint timeout. A GGUF renamed or re-quantized after the launcher was written is the usual cause; resolve the real filename from the filesystem and update the launcher, every `models-*.ini` section, and any hardcoded readiness assertion together. Re-check PID/argv/listener after the relaunch.

3. **Prove readiness, not merely listening.** Poll `/health` in a separate check. HTTP 503 with `Loading model` is not a crash; inspect progress, the same process, logs, and resources before extending observation or rolling back. Require the exact GGUF in `/props`, intended ID in `/v1/models`, resolved context, and a nonempty short Japanese chat reply with an appropriate finish reason. Recheck PID/argv/listener and leave the requested service running. A configured 65K context is not a 65K capability test.

4. **Register without changing the primary.** Inspect the matching custom provider and any already-existing matching fallback. Use `hermes config set` for nested keys, never `patch`/`write_file` on live `config.yaml`. Preserve aliases and model metadata: `models` may be a list or ID-to-metadata mapping, not a serialized string. Replace only discovered indices; do not assume provider 0 or fallback 5. Do not create or change a fallback unless that scope is requested. Load `hermes-local-model-register` for the supported registration commands.

5. **Refresh the exact endpoint's catalog.** A successful config write may still be hidden by old endpoint-cache IDs. After inspecting current signatures, use this supported refresh for the verified unauthenticated endpoint:

   ```python
   from hermes_cli.models import cached_fetch_api_models
   from hermes_cli.inventory import load_picker_context, build_model_options_payload
   live = cached_fetch_api_models('', 'http://127.0.0.1:8080/v1', force_refresh=True, timeout=10)
   payload = build_model_options_payload(load_picker_context(), explicit_only=True, refresh=False)
   ```

   Check the exact ID in the matching provider row; expose only name, slug, IDs, and aliases, not complete config/provider payloads. Report settings stored, shared candidate present, and GUI label rendered separately. Use `computer_use` only with fresh verification; stop driving the UI when the user moves to another workflow.

6. **Exercise the actual plugin.** Inspect/load the Nimble tools and test enum, boolean, ordinal labels, Japanese comprehension, code comprehension, tool routing, and a meaning-changing/data-instruction control. The native schema supports `enum` and `boolean`; ordinal dataset scores are adapted to numeric-string enum choices. Validate unique single-token candidate codes, complete finite candidate probabilities, and supported input bounds. Missing logprob candidates are invalid observations, not invented zeroes.

7. **Freeze and evaluate every input.** Inspect the current adapter and dataset. Invoke `scripts/nimble_holdout.py` as above; it checks the live GGUF/alias and active-profile settings, freezes model/dataset/handler/scorer/adapter hashes, and uses `handle_score`, not just the underlying library. Only inputs reach the model; references are used afterward. Presentation rounding may be renormalized explicitly before `assess`. Record all rows, including errors, with index/ID/type/domain/input variant/reference/raw response/grade/timing. Re-read them and verify every expected index exactly once.

8. **Check metrics through a separate calculation path.** Invoke `scripts/verify_nimble_run.py` from Verification. It re-derives predictions, agreement, NLL, Brier, numeric expected-score error, and ECE from raw probabilities without importing the grader or trusting saved grades. It checks dataset identity/order, candidate IDs, input bounds, and all total/type/domain/variant groups. Valid-zero rates and ECE are N/A. Report attempted and valid denominators. Dataset `base`/`counterfactual` means input variants, not baseline/fine-tuned models.

9. **Verify the native tool round trip separately.** Preserve the first response and warnings. On the observed PrismL build, object-valued `tool_choice` was ignored, so a returned call did not prove forced-choice enforcement. A separate `tool_choice="auto"` check emitted `add(a=17,b=25)`; perform only that known local addition, return the result with the emitted call ID, and verify the model consumes it. Do not execute arbitrary generated code. Emission, execution, returned-result consumption, and general agent ability are different claims.

10. **Deliver evidence and limits.** Run focused plugin tests with `NIMBLE_TEST_LIVE=1`; the separate legacy holdout test uses `NIMBLE_BENCH=1`. Explain skips and which full evaluation actually ran. Recheck artifact hashes and service identity. Package explicitly selected manifest/JSONL/summary/raw-check/smoke/tool/test/picker/runtime/report files, never an entire profile. Hash entries, reopen the ZIP, verify exact entries/CRCs/hashes, and keep its own hash outside it. Deliver files with `MEDIA:` and preserve implementation records according to workspace policy.

## Pitfalls

- **Reference agreement is not certified accuracy.** Record reference provenance and human-review counts; an assertion in the dataset is not an independent audit. No same-protocol baseline means no improvement or capability-retention claim.
- **Probability scales differ.** Candidate-restricted confidence is not calibrated correctness. Binary Brier uses one true-class term; multiclass Brier sums class terms. Numeric top-1 exact agreement differs from expected-value MAE; string enums may report `expected_score=null` in the plugin.
- **ECE uses measured means.** Weight each nonempty bin's absolute difference between actual mean confidence and agreement by its sample count. Do not substitute bin centers merely because a helper is named ECE.
- **Checks are not approval.** A raw-output recomputation by the run author is not third-party review, label certification, or user approval. A hash is identity/integrity evidence, not semantic correctness.
- **Windows adapters can disagree.** Native programs need native quoted paths; Bash continuations are not CMD carets. Follow `computer_use` verdicts, verify fresh captures, and avoid double-scaling coordinates if the adapter already scales them.
- **A timeout is not a model fault.** With `--parallel 1`, one large request owns the server: prompts of ~65k tokens were measured at ~145 s of prompt processing (~450 tok/s) before the first token, so a concurrent small probe times out against a perfectly healthy endpoint. Confirm via `print_timing` in the server log showing large `n_tokens` climbing, and via an idle `/slots`, before suspecting the model. Raising `--parallel` admits concurrency but multiplies KV cache — present it as a VRAM trade-off. See `references/local-endpoint-timeout-triage.md`.
- **Helpers have explicit limits.** The batch runner supports the inspected single-decision Nimble dataset and a loopback server, not arbitrary multi-field corpora or authenticated remote APIs. It uses inspected plugin settings readers; re-inspect source after a plugin revision.
- **Verification does not rerun inference.** `--check-files` also hashes available model/source paths; older manifests without scorer/adapter path fields cannot prove those file checks. The receipt lists the checks actually performed.

Existing specialized references are retained; load only the relevant one with `skill_view`:
- `references/live-model-switching.md`: scoped replacement, idle authorization, detached launch, loading diagnostics.
- `references/prisml-nimble-verification.md`: exact plugin contracts, metric definitions, picker cache, evidence boundaries.
- `references/evaluation-backed-model-cards.md`: paired comparisons, statistical caveats, model-card packaging.
- `references/hf-model-substitution-preflight.md` and `references/turboquant-hf-repo-resolution.md`: HF resolution versus actual model readiness.
- `references/turboquant-hf-kv-substitution.md` and `references/turboquant-tuning.md`: runtime-specific KV and fit conditions.
- `references/windows-gguf-filesystem-anomaly.md`: nested-path/file-lock anomalies; do not delete the GGUF without authorization.
- `references/gguf-finetune-trainability-triage.md`: training-parent/VRAM prerequisites, separate from serving.
- `references/qwen38-mtp-and-hermes-register.md` and `references/nemotron-3.5-lightning-30b-a3b.md`: model-specific MTP support; never enable it without the required model layers.
- `references/moe-and-speculative-decoding.md`, `references/moe-cron-model-change.md`, and `references/multi-port-hot-standby.md`: specialized routing/serving scopes.
- `references/embedding-server-setup.md`: embedding endpoint setup, separate from the chat server.
- `references/local-endpoint-timeout-triage.md`: ordered triage for `layer: endpoint, code: timeout` against a loopback provider — dead port, renamed GGUF vs filesystem anomaly, VRAM budget, `--parallel 1` starvation, grammar-sampling limits, and supervisor port ownership.

## Verification

Invoke this single saved-run check through `terminal`; it makes no inference requests and never changes service/configuration:

```bash
"$PYTHON" "$SKILL_DIR/scripts/verify_nimble_run.py" --run-dir "$RUN_DIR" --check-files
```

Success requires exit 0 and a receipt showing expected/actual row counts, raw-probability cross-check, grouped metrics, ECE, tested prompt-token range, and the file checks actually performed. Use `--receipt <new-file>` to persist it without overwriting old evidence. `--self-test` additionally exercises enum/boolean/ordinal formulas, zero-valid handling, and rejection of NaN, token collisions, and excessive input length.
