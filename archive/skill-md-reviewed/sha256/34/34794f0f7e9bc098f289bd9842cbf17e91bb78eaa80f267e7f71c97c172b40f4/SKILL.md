---
name: local-ai-workstation
description: "Use for local AI workstation and API free-tier operations."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [local-ai, comfyui, api-monitoring, cron, windows]
    related_skills: [cronjob-management, security-and-hardening]
---

# Local AI Workstation Operations

Use this class-level skill for Windows desktop AI workflows, localhost inference services, model/LoRA wiring, secret-safe provider monitoring, and daily health-check automation.

## Local inference workflow

1. Inspect the actual server root, interpreter, model directories, output directory, existing cron jobs, and project instructions before editing.
2. Prefer Tkinter plus Python standard library for small Windows utilities. Keep lifecycle commands fixed and explicit; never expose arbitrary command execution through a GUI.
3. Bind local services to `127.0.0.1` by default. Poll a health endpoint such as `/system_stats` in a background thread before enabling generation.
4. Track process ownership explicitly: terminate only a server started by the GUI; use the server interrupt endpoint for generation cancellation.
5. Use API-format workflow JSON. For img2img, upload via multipart/form-data and inject the returned server-side image name into `LoadImage`.
6. When adding `LoraLoader`, rewire both model and CLIP references to its outputs while keeping the checkpoint VAE connected to `VAEDecode`.
7. Use conservative resolutions on constrained VRAM and verify a non-empty output file, not merely a successful prompt submission.

## Secret-safe free-tier monitoring

1. Read only required provider variables from `.env`; never print, persist, hash, prefix-match, or interpolate secret values.
2. Send credentials only in HTTPS headers, never URL query parameters.
3. Probe read-only metadata endpoints such as model catalogs or account-limit metadata; do not spend quota with generation calls just to test availability.
4. Report only provider, key presence, coarse connection state, free-model count or official free-tier link, and timestamp. Discard response bodies and suppress exception text.
5. Distinguish authentication failures, rate limiting, network failures, and other HTTP statuses.
6. Treat user classifications as user classifications: report NVIDIA NIM as `無料扱い（ユーザー指定）`, not permanent official free pricing.
7. If a provider lacks a verified stable metadata endpoint, report key presence and `要確認`; never guess an endpoint.

### OpenRouter の NVIDIA 無料モデル

`NVIDIA_API_KEY` が設定されていなくても、OpenRouter 経由で NVIDIA モデルを無料で叩ける。

| モデル | コスト | コンテキスト | 備考 |
|---|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 0（無料） | 1,000,000 tokens | Nemotron 3 Ultra, reasoning 付き |
| `nvidia/nemotron-3.5-lightning-free` | 0（無料） | | Nemotron 3.5 Lightning |

**使用例:**

```bash
hermes --provider openrouter -m "nvidia/nemotron-3-ultra-550b-a55b:free" chat -q "prompt" -Q
```

**API 叩き方（直接 curl でテストする場合）:**

```bash
curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/nemotron-3-ultra-550b-a55b:free","messages":[{"role":"user","content":"Say PONG"}]}'
```

**注意:**
- OpenRouter の API キーは `~/.hermes/.env` の `OPENROUTER_API_KEY` に格納されている
- 環境変数として export されていない場合があるため、スクリプト内で `grep` で読み取って export する必要がある
- コマンドパーサーの制限に引っかかる場合は、シェルスクリプトを書いて `bash` 経由で実行する

### 外部キー（.env に格納済み）の確認

`.hermes/.env` にあるキーは以下の通り。リポジトリの `.env` には含めないこと。

- `NVIDIA_API_KEY` — `nvapi-...` 形式。NVIDIA 直接 API 用（integrate.api.nvidia.com）
- `OPENROUTER_API_KEY` — `sk-or-...` 形式。OpenRouter 経由で NVIDIA モデルを叩く際にも使用
- 他: `LINEAR_API_KEY`, `AITUBERKIT_API_KEY`, `OPENMANUS_API_KEY`, `HEYGEN_API_KEY`, `LAPRAS_API_KEY`, `FREEBUFF_API_KEY`, `FISH_AUDIO_API_KEY`

## Daily cron

- List existing jobs and group by purpose, script, schedule, and delivery before creating a monitor.
- Prefer a deterministic `no_agent` script with a fixed path, terminal-only tools, origin delivery unless otherwise requested, and one daily schedule such as `0 9 * * *`.
- Run it once manually, then verify status, next-run time, delivery errors, report path, and a secret-marker scan.
- Include requested traceability markers such as `#はくあ #hermesagent` when appropriate.

## Verification gate

- Run syntax validation.
- Assert txt2img, img2img, and img2img+LoRA workflow construction, including VAE wiring.
- Verify the live health endpoint and expected server version.
- Run a bounded smoke generation and confirm a non-empty output file.
- Scan reports for markers such as `nvapi-`, `sk-`, `AIza`, `Bearer `, `TOKEN=`, and `API_KEY=`.
- Verify the scheduled job is enabled and its manual run succeeds.
- Record skipped checks and residual risk; never invent quota or generation results.

## References

- `references/secret-safe-api-monitoring.md` — redaction boundaries, provider probing, and status classification.
- `references/provider-matrix.md` — sanitized provider observations and validated metadata endpoints.
- `references/local-inference-gui.md` — Windows lifecycle, ComfyUI wiring, and smoke-test patterns.
- `references/openrouter-nvidia-free-models.md` — OpenRouter 経由で NVIDIA モデルを無料で叩く方法（NVIDIA API Key なし）
