---
name: github-pr-review-automation
description: Automate PR review fixes with Codex patch generation.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge]
    related_skills: [github-auth, github-code-review]
---
1. Fetch PR comments using `gh pr view <PR_NUMBER> --json comments --jq '.comments.nodes[].body'` or fallback with `curl`.
2. Create a delegate task that runs Codex CLI to generate a patch fixing the comments.
3. Apply the patch with `patch -p1 < /tmp/fix.patch`.
4. Commit changes with a conventional commit message and push.
5. Notify the user via the designated channel for final review.