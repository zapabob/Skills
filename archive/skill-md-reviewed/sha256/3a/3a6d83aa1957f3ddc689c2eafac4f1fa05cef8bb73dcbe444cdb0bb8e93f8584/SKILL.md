---
name: hermes-gpt56-luna-switch
description: Switch Hermes to GPT-5.6-luna and verify routing.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Hermes, Model, Codex, Configuration, Verification]
---

# Hermes GPT-5.6-luna Model Switch

This skill changes Hermes Agent's default model to `gpt-5.6-luna` through the `openai-codex` provider and verifies the effective configuration. It does not edit OAuth files, API keys, cookies, or `.env` contents. Prefer Hermes configuration commands; use direct file inspection only to verify a result or diagnose a blocked configuration command.

## When to Use

- The user asks to change Hermes to GPT-5.6-luna.
- Hermes is still routing through an old default model.
- A cron or session reports the wrong active model.
- The user wants Codex-backed model routing verified.

## Prerequisites

- Hermes Agent installed and the `openai-codex` provider authenticated.
- The user has explicitly requested the model change.
- Use the active Hermes profile; do not modify another profile without explicit direction.
- Never print or store OAuth tokens, API keys, cookies, or `.env` contents.

## How to Run

Use `terminal` to invoke Hermes configuration commands, `read_file` to inspect the effective config when necessary, and `terminal` again for a non-destructive verification. Do not use a live posting or external side effect as a model smoke test.

## Quick Reference

- View config: `hermes config`
- Set default model: `hermes config set model.default gpt-5.6-luna`
- Set provider: `hermes config set model.provider openai-codex`
- Set reasoning: `hermes config set agent.reasoning_effort medium`
- Check auth without exposing secrets: `hermes status --all`
- Windows config path: `%USERPROFILE%\.hermes\config.yaml`

## Procedure

1. **Inspect before changing.** Invoke through `terminal`:

   ```text
   hermes config
   ```

   Record only the current provider and model names. Do not copy credential fields into the response.

2. **Set the requested model.** Invoke through `terminal`:

   ```text
   hermes config set model.default gpt-5.6-luna
   hermes config set model.provider openai-codex
   ```

   Preserve unrelated model settings, including an existing `base_url`, unless the user explicitly requests a routing change.

3. **Set a compatible reasoning level when requested.** For the medium setting used in this workflow, invoke through `terminal`:

   ```text
   hermes config set agent.reasoning_effort medium
   ```

   Do not use `max` or `ultra` merely because a remote model catalog advertises them; use the requested supported level.

4. **Verify the persisted values.** Invoke through `terminal`:

   ```text
   hermes config
   ```

   Require `model.default` to be `gpt-5.6-luna`, `model.provider` to be `openai-codex`, and `agent.reasoning_effort` to be `medium` when that option was requested.

5. **Check readiness without secrets.** Invoke through `terminal`:

   ```text
   hermes status --all
   ```

   Confirm the provider is available. Treat authentication failure separately from a model-routing failure.

6. **Handle a blocked config command.** If the Hermes config command cannot write because of a profile or security guard, do not bypass it by editing authentication files. Use `read_file` to inspect the target config, then report the exact blocked operation and ask before using a profile-appropriate configuration path. If the user has already authorized direct config repair, make the smallest targeted edit and re-read the resulting values.

7. **Restart only when needed.** Configuration changes for a long-running gateway may require a restart before cron or messaging sessions use the new model. Do not restart an active gateway blindly; verify whether the current process reloads config and restart through the normal Hermes operation only when required.

## Pitfalls

- Changing `model.default` without `model.provider` can leave Hermes routing through the previous provider.
- `openai-codex` authentication is separate from the model name; a correct model setting does not prove OAuth readiness.
- `last_status: ok` on a cron proves only that the job body completed; it does not prove that the new model was used unless the effective model is logged or shown by status.
- A direct edit that rewrites the whole YAML can reorder or damage unrelated settings. Prefer `hermes config set` or a targeted patch.
- Do not expose `auth.json`, `.env`, refresh tokens, API keys, or provider headers while diagnosing routing.
- Model catalogs can contain reasoning levels unsupported by an older Codex CLI. The requested `medium` level is a safe compatibility target in this workflow.

## Verification

Run through `terminal`:

```text
hermes config
```

The skill succeeds when the effective configuration shows `gpt-5.6-luna` with provider `openai-codex`, and `medium` reasoning when requested, without exposing credential material.
