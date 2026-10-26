---
name: hermes-local-model-register
description: Register live llama-server model without changing primary.
version: 0.1.0
author: Hermes
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Hermes, llama.cpp, GGUF, Config, Fallback]
---

# Register a Live Local Model in Hermes

Wire a running OpenAI-compatible `llama-server` into Hermes as a named custom provider. This does **not** start the server and does **not** change `model.provider` / `model.default` unless the user explicitly asks to switch the primary. Serving flags live in `local-llm-server`.

## When to Use

- User says `モデル登録して`, "register the model", or "add this GGUF to Hermes".
- A local GGUF is already serving on `:8080` (or another custom endpoint) and must appear in the picker / fallback chain.
- User wants `/model custom:<name>:<id>` available without replacing Nous/Codex as the session default.

Do **not** use this to flip the default model. Do **not** use `patch` / `write_file` on `~/.hermes/config.yaml`.

## Prerequisites

- `llama-server` already healthy: `GET /health` → `{"status":"ok"}` and `GET /v1/models` lists the live id.
- Hermes CLI on PATH (`hermes config`, `hermes fallback`).
- Authoritative config is `C:\Users\<user>\.hermes\config.yaml` (this host: `%USERPROFILE%\.hermes\config.yaml`).
- For Qwen3.8-27B MTP on this host, serve first with `local-llm-server` (K=`q8_0`, V=`turbo3`, `--spec-type draft-mtp`). Live id: `qwen3.8-27b-abliterated-mtp`.

## How to Run

Inspect with `terminal` (`hermes config get …`). Write only via `hermes config set` nested keys. Confirm with `hermes fallback list` plus `/health` and `/v1/models`. Never `patch` the live config file.

## Quick Reference

| Task | Command |
|------|---------|
| Config path | `hermes config path` |
| Primary (must stay) | `hermes config get model` |
| Custom catalog | `hermes config get custom_providers` |
| Fallback chain | `hermes fallback list` |
| Live health | `curl -sS --max-time 8 http://127.0.0.1:8080/health` |
| Live model id | `curl -sS --max-time 8 http://127.0.0.1:8080/v1/models` |
| Set custom default | `hermes config set custom_providers.0.model <live-id>` |
| Set ctx | `hermes config set custom_providers.0.context_length <n_ctx>` |
| Set catalog list | `hermes config set custom_providers.0.models '["<live-id>","<old-alias>"]'` |
| Point last local fallback | `hermes config set fallback_providers.N.model <live-id>` |
| Use this session | `/model custom:127.0.0.1-8080:<live-id>` |
| New CLI session | `hermes --provider custom:127.0.0.1-8080 -m <live-id>` |

## Procedure

1. **Confirm the server is model-ready.** Through `terminal`:

   ```bash
   curl -sS --max-time 8 http://127.0.0.1:8080/health
   curl -sS --max-time 8 http://127.0.0.1:8080/v1/models
   ```

   Done when `/health` is `ok` and `data[].id` (or `models[].name`) is the id you will register. If `/health` is ok but `/v1/models` is empty, stop — the listener is not model-ready.

2. **Read current Hermes wiring.** Through `terminal`:

   ```bash
   hermes config get model
   hermes config get custom_providers
   hermes fallback list
   ```

   Done when you know: primary provider/model, custom entry `name` + `base_url`, existing `models` aliases, and the fallback index `N` whose provider is `custom:<name>` (on this host: `custom:127.0.0.1-8080`).

3. **Refuse the wrong writers.** `patch` / `write_file` on `~/.hermes/config.yaml` return `Refusing to write to Hermes config file`. `hermes config set model.provider custom` changes the **primary** — only do that if the user asked to switch the default.

4. **Register without flipping primary.** Through `terminal` (keep old aliases; put the live id first):

   ```bash
   hermes config set custom_providers.0.model qwen3.8-27b-abliterated-mtp
   hermes config set custom_providers.0.context_length 65536
   hermes config set custom_providers.0.models '["qwen3.8-27b-abliterated-mtp","Huihui-gemma-4-12B-agentic-fable5-Q4_K_M","Qwen3.8-27B-Uncensored-IQ4_XS","default"]'
   hermes config set fallback_providers.5.model qwen3.8-27b-abliterated-mtp
   ```

   Replace index `0` / `5` and the id with the values from step 2. Preserve the actual `models` shape: it may be a JSON/YAML list or an ID-to-metadata mapping; do not flatten a mapping and lose context metadata, or store either shape as a string. The fallback write applies only when the user authorized changing that existing matching fallback; registration alone does not authorize it. A `✓ Set …` response proves a write, not picker visibility; complete the read-back and shared-payload checks below.

5. **Verify all four surfaces.** Through `terminal`:

   ```bash
   hermes config get model
   hermes config get custom_providers
   hermes fallback list
   curl -sS --max-time 8 http://127.0.0.1:8080/v1/models
   ```

   Done when: primary is unchanged; `custom_providers[].model` is the live id; `context_length` matches `n_ctx`; fallback last local entry uses the live id; `/v1/models` still lists that id.

6. **Verify the shared picker payload, not only the config writer.** A stale custom-endpoint catalog can replace the newly declared model with the old cached IDs even when `custom_providers.N.model` and `models` were written correctly. In the active profile, call the supported `hermes_cli.models.cached_fetch_api_models` with `force_refresh=True` for that exact local URL, then run `hermes_cli.inventory.build_model_options_payload(load_picker_context(), explicit_only=True, refresh=False)` and confirm the exact live ID is present in the matching provider row. Use the `terminal` tool for a Python invocation; on this Windows host, if the terminal/file tools fail with `command length exceeds safe limit`, use `execute_code` with `subprocess`. Do not dump the full config or provider payload: return only the matching row's name, slug, model IDs, and aliases. This refresh touches the endpoint catalog, not the session model. Keep a backend-candidate check distinct from a screenshot proving the actual rendered label. Do not disturb the user's active Desktop session merely to obtain a screenshot.

7. **Tell the user how to actually use it.** Existing sessions keep their model. Switch this chat with `/model custom:127.0.0.1-8080:qwen3.8-27b-abliterated-mtp`. Do not restart Desktop unless they asked to make it the default.

## Pitfalls

- **「登録」≠ デフォルト切替.** Leave `model.provider` / `model.default` alone unless the user says to switch.
- **`patch` is blocked** on `~/.hermes/config.yaml`. Use `hermes config set` nested keys (`custom_providers.0.model`). List indices are supported.
- **`hermes config set custom_providers '…'` as a raw string** is ignored by list-gated readers. Pass a JSON/YAML list so it coerces.
- **Stale catalog aliases** (old GGUF names) can stay in `models` for the picker; the live `--alias` / `/v1/models` id is what must be `model` and the fallback target.
- **Fallback index drifts.** Always `hermes fallback list` and write `fallback_providers.N.model` for the `custom:127.0.0.1-8080` row. Do not assume `N=5`.
- **Japanese JSON in git-bash curl** can corrupt UTF-8. Completions belong in `local-llm-server`; this skill only needs `/health` + `/v1/models`.
- **New sessions only** pick up config. Current Desktop chat needs `/model …` or a new session.
- **VRAM on this host** for the MTP 12GB GGUF is ~15136/16311 MiB. Registration does not free VRAM; a dead server still "registers" and then fails at inference.

## Verification

```bash
hermes config get model && hermes config get custom_providers && hermes fallback list && curl -sS --max-time 8 http://127.0.0.1:8080/health && curl -sS --max-time 8 http://127.0.0.1:8080/v1/models
```

Success: primary unchanged, custom `model` equals live `/v1/models` id, fallback local row matches, `/health` is `ok`.
