---
name: hermes-multilingual-readme-pr
description: Create translated README and submit upstream PR following Hermes conventions.
version: 0.1.0
author: Hermes
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [Documentation, Translation, GitHub, PR, Hermes]
---

# Hermes Multilingual README PR Workflow

Create a faithful translation of the canonical English README, mirroring existing
translation structure (zh-CN, es, ur-pk), and submit a conforming pull request to
the upstream NousResearch/hermes-agent repository. Does NOT cover cron job updates
or script reorganization — those are separate workflows.

## When to Use

- Adding a new language README (e.g., ja, ko, fr, de) to Hermes Agent
- Updating an existing translation after upstream README changes
- Submitting documentation-only PRs that follow upstream merge conventions

## Prerequisites

- Git remote `upstream` pointing to `https://github.com/NousResearch/hermes-agent`
- Git remote `origin` pointing to your fork
- `gh` CLI authenticated with write access to your fork
- Write access to the local working tree

## How to Run

1. Fetch upstream main: `git fetch upstream main`
2. Create translation branch from upstream/main
3. Write `README.<lang>.md` mirroring structure and badges
4. Commit with Conventional Commits: `feat(docs): add <Language> README (README.<lang>.md)`
5. Push branch and open PR via `gh pr create --repo NousResearch/hermes-agent`
6. Wait for CI (OSV scan, affected-areas detection) to pass
7. Merge locally to fork main after PR approval

## Quick Reference

| Action | Command |
|--------|---------|
| Fetch upstream | `git fetch upstream main` |
| New branch | `git checkout -b feat/readme-<lang> upstream/main` |
| View canonical README | `git show upstream/main:README.md` |
| View existing translation | `git show upstream/main:README.zh-CN.md` |
| Push branch | `git push origin feat/readme-<lang> --force` |
| Create PR | `gh pr create --repo NousResearch/hermes-agent --base main --head <fork>:feat/readme-<lang> --title "feat(docs): add <Language> README (README.<lang>.md)"` |
| Check PR status | `gh pr view <num> --repo NousResearch/hermes-agent --json state,mergeable` |
| Local merge to main | `git checkout main && git merge feat/readme-<lang> --no-ff -m "Merge pull request ..."` |

## Procedure

1. **Sync with upstream**
   ```
   git fetch upstream main
   git checkout -b feat/readme-<lang> upstream/main
   ```

2. **Study canonical and existing translations**
   - Read `git show upstream/main:README.md` for structure
   - Read `git show upstream/main:README.zh-CN.md` for badge order and formatting

3. **Write translation**
   - Create `README.<lang>.md` at repo root
   - Preserve: banner, badges (Docs, Discord, License, Built by, Lang links), table structure, code blocks, ASCII architecture diagram, all URLs
   - Translate: descriptive text, feature descriptions, section headers, CLI commands table, footer
   - Keep badge markup identical; only change alt text and link targets for Lang badges

4. **Commit with proper message**
   ```
   git add README.<lang>.md
   git commit -m "feat(docs): add <Language> README (README.<lang>.md)

   Mirror of the canonical English README with faithful <Language> translation.
   Follows the same structure, badge pattern, and formatting as existing
   translations (zh-CN, es, ur-pk)."
   ```

5. **Push and open PR**
   ```
   git push origin feat/readme-<lang> --force
   gh pr create --repo NousResearch/hermes-agent \
     --base main \
     --head <fork-owner>:feat/readme-<lang> \
     --title "feat(docs): add <Language> README (README.<lang>.md)" \
     --body "<structured body per template>"
   ```

6. **Monitor CI**
   ```
   gh pr checks <pr-number> --repo NousResearch/hermes-agent
   ```

7. **Merge to local main after approval**
   ```
   git checkout main
   git merge feat/readme-<lang> --no-ff -m "Merge pull request #<num> from <fork-owner>/feat/readme-<lang>

   feat(docs): add <Language> README (README.<lang>.md)"
   git push origin main
   ```

## Pitfalls

- **Fork divergence**: Local main may diverge from upstream; always create branch from `upstream/main`, not local `main`.
- **README.md drift**: Do NOT modify canonical `README.md` in the translation PR — it must stay identical to upstream for translation consistency.
- **Badge order**: Preserve exact badge sequence: Docs → Discord → License → Built by → Lang links (zh-CN, ur-pk, es, new lang).
- **Line endings**: Windows may convert LF to CRLF; Git handles this but verify diff shows only content changes.
- **PR permissions**: You cannot merge directly to upstream via `gh pr merge` without write access; merge locally to your fork's main instead.
- **CI scope**: Only markdown linting and OSV scan run; no code tests for docs-only PRs.

## Verification

After PR creation, run:
```
gh pr view <pr-number> --repo NousResearch/hermes-agent --json additions,deletions,files
```
Confirm: only `README.<lang>.md` added with expected line count (~170 lines for Japanese), 0 deletions, no other files modified.