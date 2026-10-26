---
name: hermes-repo-sync
category: productivity
description: Use when .hermes and repo sync; auto-sync scripts cron.
author: Hermes Agent
license: MIT
metadata:
  tags: ["sync", "automation", "cron"]
  related_skills: ["hermes-repo-sync"]
version: 1.0.0
---

## When to Use
Use this skill to keep the `.hermes` directory synchronized with the repository, ensuring cron jobs run reliably and preventing missed telegram messages.

# Herms-Repo Sync Skill

## Steps
1. **Check .hermes existence**: Verify `.hermes` directory exists in the workspace.
2. **Compare with repo**: Use `git status` to see if any `.hermes` files are untracked or modified.
3. **Run sync script**: Execute the sync script located at `scripts/hermes_sync.sh` which copies `.hermes` changes into the repo and commits them.
4. **Schedule cron**: Ensure the cron job `hermes-sync` is listed in `crontab -l` and set to run daily at a convenient time.
5. **Test cron**: Manually trigger the cron command and verify that the `.hermes` directory updates and a test telegram message is sent.

## Pitfalls
- **Missing .hermes**: If the directory is absent, the sync will fail; create it first.
- **Permission errors**: Ensure the script has execute permission (`chmod +x scripts/hermes_sync.sh`).
- **Cron not running**: Verify the cron entry is active; restart the cron service if needed.
- **Stale scripts**: Update `hermes_sync.sh` if repo structure changes.

## Verification
- Run `./scripts/hermes_sync.sh` and confirm a new commit appears in the repo.
- Check `crontab -l` for the `hermes-sync` entry.
- Send a test telegram message via the cron job and confirm receipt.