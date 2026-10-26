---
name: provider-credential-pooling
description: "Add multiple API keys per provider for round-robin rotation."
version: 1.0.0
author: Hermes Agent + sedori-buyer
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [provider, credentials, api-key, round-robin, auth, nvidia, openrouter]
    category: autonomous-ai-agents
    related_skills: [hermes-agent, opencode-free-rotation, freellmapi-free-tier]
---

# Provider Credential Pooling

Manage multiple API credentials per provider so Hermes rotates across them automatically
instead of failing when one key hits its rate limit or quota. Also covers fallback chains
(across different providers) and quick-add workflows for common providers.

## When to Use

- Adding a secondary/tertiary API key for an already-configured provider.
- Setting up rotation so the same provider alternates between multiple keys.
- Extending the fallback chain when the primary model goes down.
- Verifying credential pool state after adding or removing keys.

## Key Distinction: Pool vs. Fallback

| Mechanism | What it does | When to use |
|-----------|--------------|-------------|
| **Credential pool** (same provider, multiple keys) | Rotates across keys for the same provider | Primary key hits rate limit / quota |
| **Fallback chain** (different providers/models) | Switches to a different provider/model | Primary provider is down or model unavailable |

Both can work together: pool rotation happens first within the provider, then fallback
triggers across providers if all keys in the pool are exhausted.

## Quick Add — Secondary Key for Round-Robin

```bash
hermes auth add <provider> --type api-key --label "<descriptive-name>" --api-key "<KEY>"
```

Flags:
- `--label` — human-readable name for the key (e.g., `"nvidia-secondary"`, `"openrouter-backup"`)
- `--api-key` — the key value (omit to prompt securely, but direct pass is faster for automation)

### Verify the pool

```bash
hermes auth list
```

You should see the provider listed with `2 credentials` and both entries present.
The `←` marker indicates the currently active credential in the pool.

## Common Provider Quick Reference

### NVIDIA (NIM)

```bash
hermes auth add nvidia --type api-key --label "nvidia-secondary" --api-key "nvapi-..."
```

- Provider ID: `nvidia`
- Base URL: `https://integrate.api.nvidia.com/v1`
- Common models: `nvidia/llama-3.1-nemotron-70b-instruct`, `nvidia/llama-3.3-70b-instruct`, `nvidia/nemotron-3-super-120b-a12b`
- Signup: https://build.nvidia.com/

### OpenRouter

```bash
hermes auth add openrouter --type api-key --label "openrouter-backup" --api-key "sk-or-..."
```

### Gemini / Google AI Studio

```bash
hermes auth add gemini --type api-key --label "gemini-secondary" --api-key "..."
```

Note: Gemini also reads `GOOGLE_API_KEY` and `GEMINI_API_KEY` env vars as separate pool entries automatically.

### OpenAI

```bash
hermes auth add openai-api --type api-key --label "openai-secondary" --api-key "sk-..."
```

## Managing the Fallback Chain

When credential pooling is not enough (all keys exhausted), Hermes falls back to
different providers/models in order.

```bash
# View current chain
hermes fallback list

# Add a fallback entry (interactive picker)
hermes fallback add

# Remove by index
hermes fallback remove 2

# Clear all
hermes fallback clear
```

## Pitfalls

1. **Don't replace the primary when adding a secondary.** Use `hermes auth add <provider>` again with a new label — this *appends* to the pool. Don't delete the first entry.

2. **Label must be unique within the provider.** Two entries with the same label under the same provider will collide.

3. **`--type api-key` is required for key-based providers.** OAuth providers (nous, openai-codex, xai-oauth) need different flags (`--no-browser`, etc.).

4. **Env-var keys are auto-pooled.** If you have both `GEMINI_API_KEY` and `GOOGLE_API_KEY` set, they become two pool entries automatically. A third added via `hermes auth add` makes three.

5. **Rate-limited entries show remaining cooldown.** In `hermes auth list`, rate-limited entries display `(Xm Ys left)`. Hermes skips these automatically during rotation.

6. **`hermes auth add` vs `hermes config set`.** `auth add` manages the credential pool. `config set model.api_key` sets a single key in config.yaml — this does NOT pool. Always prefer `auth add` for rotation.

## Verification

After adding a secondary key:

```bash
# Confirm pool size increased
hermes auth list | grep -A3 "provider-name"

# Confirm fallback chain is intact
hermes fallback list
```

## See Also

- `hermes-agent` references/providers-and-models.md for full provider catalog
- `opencode-free-rotation` for OpenCode Zen free-model pool patterns
