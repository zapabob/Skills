---
name: hypura-provider-plugin-workflow
description: Create Hypura model provider plugin, commit with Conventional Commits, push branch, and open PR.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Hypura, Plugin, Git, ConventionalCommits, PR]
---

# Hypura Provider Plugin Workflow

Create a Hypura model provider plugin for Hermes Agent, commit changes using Conventional Commits format, push the feature branch, and open a pull request. Covers plugin structure adherence, git branch conflict resolution, and end-to-end PR workflow.

## When to Use

- Adding a new model provider plugin to `plugins/model-providers/`
- Need to follow Conventional Commits for commit messages
- Git branch already exists and needs force-recreate
- Want a reproducible workflow from plugin creation to PR

## Prerequisites

- Hermes Agent repository cloned locally
- Git configured with upstream remote (`origin`)
- Write access to push branches and open PRs
- Python 3.10+ environment for plugin validation

## How to Run

Invoke through the `terminal` tool for git operations, `read_file`/`write_file` for plugin files, and `skill_view` to reference existing provider plugins.

## Quick Reference

```bash
# Explore existing provider structure
ls plugins/model-providers/

# Create plugin files
write_file plugins/model-providers/hypura/plugin.yaml
write_file plugins/model-providers/hypura/__init__.py

# Git workflow
git checkout main
git pull origin main
git branch -D feat/hypura-provider  # if exists
git checkout -b feat/hypura-provider
git add plugins/model-providers/hypura/
git commit -m "feat(providers): add Hypura storage-tier-aware LLM inference scheduler provider"
git push -u origin feat/hypura-provider
gh pr create --base main --head feat/hypura-provider --title "feat(providers): add Hypura provider" --body "Adds HypuraProvider plugin for Ollama-compatible local inference server."
```

## Procedure

1. **Explore existing provider structure**
   ```bash
   ls plugins/model-providers/
   read_file plugins/model-providers/ollama/plugin.yaml
   read_file plugins/model-providers/ollama/__init__.py
   ```

2. **Create Hypura plugin files**
   - `plugins/model-providers/hypura/plugin.yaml` — manifest with name, version, entrypoint
   - `plugins/model-providers/hypura/__init__.py` — `HypuraProvider` class implementing `fetch_models()` against `http://localhost:8080/api/tags`

3. **Verify plugin loads**
   ```bash
   python -c "from plugins.model_providers.hypura import HypuraProvider; print('OK')"
   ```

4. **Prepare git branch**
   ```bash
   git checkout main
   git pull origin main
   git branch -D feat/hypura-provider 2>/dev/null || true
   git checkout -b feat/hypura-provider
   ```

5. **Stage and commit with Conventional Commits**
   ```bash
   git add plugins/model-providers/hypura/
   git commit -m "feat(providers): add Hypura storage-tier-aware LLM inference scheduler provider

- Add HypuraProvider plugin for Ollama-compatible local inference server
- Implements fetch_models() against local /api/tags endpoint (port 8080)
- No authentication required, works with local Hypura instances
- Includes plugin.yaml manifest for discovery"
   ```

6. **Push branch and open PR**
   ```bash
   git push -u origin feat/hypura-provider
   gh pr create --base main --head feat/hypura-provider \
     --title "feat(providers): add Hypura provider" \
     --body "Adds HypuraProvider plugin for Ollama-compatible local inference server."
   ```

## Pitfalls

- **Branch already exists**: Use `git branch -D feat/hypura-provider` before recreating (force delete).
- **Conventional Commits format**: Must follow `type(scope): subject` with body explaining changes. Type must be `feat`, `fix`, `chore`, etc.
- **Plugin discovery**: `plugin.yaml` must have `entrypoint` pointing to the provider class.
- **Port assumption**: Hypura defaults to port 8080; adjust in `__init__.py` if different.
- **No auth**: Current implementation assumes local unauthenticated access.

## Verification

```bash
# Verify plugin loads
python -c "from plugins.model_providers.hypura import HypuraProvider; p=HypuraProvider(); print(p.fetch_models())"

# Verify PR exists
gh pr list --head feat/hypura-provider --state open
```

Expected: Plugin imports without error, `fetch_models()` returns list, PR shows open on GitHub.