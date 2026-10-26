---
name: workflow-sync-hermes
category: productivity
description: Sync .hermes with repo to avoid script failures.
tags: [sync, hermes, git]
---

## Goal
Ensure `.hermes` profile and repository are synchronized to avoid script failures.

## Steps
1. Check repository status: `git status` in repo root.
2. Pull latest changes: `git pull`.
3. Compare `.hermes` with repository: `diff -r .hermes repo/.hermes`.
4. If differences, commit and push: `git add .hermes && git commit -m "Sync .hermes" && git push`.
5. Verify sync: run dependent script or `git diff --quiet`.
6. Schedule daily cron to automate steps 1‑4.

## Prerequisites
- Git installed.
- Access to repository.
- Cron access.

## Verification
- After sync, `git diff --quiet` should return no output.
- Dependent scripts run without errors.

## Notes
- Use `hermes repo-sync` if available.
- Keep environment variables consistent.