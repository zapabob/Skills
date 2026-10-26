---
name: freebuff
description: Run Codebuff Freebuff free terminal coding agent from Hermes.
version: 0.1.0
author: zapabob
platforms: [linux, macos, windows]
metadata:
  hermes:
    category: devops
    tags: [coding-agent, freebuff, codebuff, terminal]
---

# Freebuff Skill

Hermes bridge for [Codebuff Freebuff](https://freebuff.com/cli) — the free,
ad-supported terminal coding agent from [CodebuffAI/codebuff](https://github.com/CodebuffAI/codebuff).

## When to Use

- You want a **zero-cost** coding agent with strong open models (DeepSeek, Kimi, MiniMax).
- The task needs **multi-file edits**, test runs, or browser research inside a repo.
- Hermes should **hand off** heavy implementation work to Freebuff's dedicated TUI.

## Prerequisites

- Node.js 18+ and npm on PATH.
- Run once: `hermes freebuff setup` then `hermes freebuff install`.
- First launch downloads the native binary to `~/.config/manicode/`.

Enable tools: `plugins.enabled` includes `freebuff`, and `tools.cli.enabled` includes `freebuff`.

## How to Run

```text
hermes freebuff doctor
hermes freebuff run /path/to/project
```

## Using Freebuff as Hermes Model Provider

Freebuff can also be used as a free AI model provider for Hermes chat via a local OpenAI-compatible proxy. This allows you to use powerful models like DeepSeek V4 Flash through Freebuff's free tier for your Hermes conversations, without consuming your usual model quotas.

### Setup

1. Install the proxy: `hermes freebuff proxy install`
2. Start the proxy: `hermes freebuff proxy start` (it will run in the background)
3. Connect Hermes to use Freebuff: `hermes freebuff connect`
   - This configures Hermes to use `provider: freebuff`, `default: deepseek/deepseek-v4-flash`, and `base_url: http://127.0.0.1:8765/v1`
   - For immediate effect without restart: `hermes freebuff connect --apply-model`

### Usage

Once connected, all Hermes chat interactions will use the Freebuff-backed model. Monitor usage and logs at:
- Log file: `~/.hermes/logs/freebuff-proxy.log`
- Proxy status: `hermes freebuff status` (checks proxy health)

### Notes

- The free tier has rate limits; monitor the proxy logs if you encounter errors.
- The proxy is interactive-only in the sense that it requires the Freebuff backend service, but it provides a standard OpenAI-compatible API endpoint for Hermes.
- To revert to your previous model provider, edit `~/.hermes/config.yaml` manually or rerun setup.

From chat (after toolset enabled):

- `freebuff_status` — install/binary probe
- `freebuff_doctor` — preflight
- `freebuff_launch` — returns launch command (dry_run default)

## Quick Reference

| Command | Purpose |
|---------|---------|
| `hermes freebuff setup` | Enable plugin + toolset in config.yaml |
| `hermes freebuff install` | `npm install -g freebuff` |
| `hermes freebuff run .` | Start interactive TUI in cwd |
| `/freebuff doctor` | Gateway slash preflight |

Freebuff is **interactive only** — use `terminal` or a real console to drive the TUI.

## Procedure

1. Call `freebuff_doctor`. Fix Node/npm or run `hermes freebuff install` if missing.
2. Call `freebuff_launch` with `workdir` set to the target repo (keep `dry_run=true`).
3. Run the returned command via `terminal` in that directory, or tell the user to run `hermes freebuff run`.
4. After Freebuff finishes, resume Hermes work with `read_file` / `search_files` on changed paths.

## Pitfalls

- Freebuff shows **terminal ads** before/after turns — expected for the free tier.
- **Limited mode** outside full-access regions caps daily sessions.
- Do not expect headless/JSON API — unlike `@codebuff/sdk`, Freebuff has no stable programmatic API in Hermes.
- Windows Defender may quarantine the downloaded binary; whitelist `~/.config/manicode/`.

## Verification

```text
hermes freebuff status
```

Expect `binary.exists: true` or `cli_on_path` set after install and first `freebuff` run.
