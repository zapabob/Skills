---
name: github-pr-workflow-summary
description: "Summarize GitHub PR workflow steps."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: []
    related_skills: []
---

# GitHub PR Workflow Summary

Use this skill to quickly recall the GitHub PR lifecycle steps.

## 1. Branch Creation
- Start from clean `main`: `git checkout main && git pull origin main`
- Create feature branch: `git checkout -b feat/add-user-authentication`

## 2. Making Commits
- Stage files: `git add src/auth.py src/models/user.py tests/test_auth.py`
- Commit with conventional message: `git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"`

## 3. Pushing and Creating a PR
- Push branch: `git push -u origin HEAD`
- Create PR (use `gh` if available, else `curl`):
  - With `gh`: `gh pr create --title "feat: add JWT-based user authentication" --body-file /tmp/pr-body.md --repo OWNER/REPO --base main --head $BRANCH`
  - With `curl`: `curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/$OWNER/$REPO/pulls -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"`

## 4. Monitoring CI Status
- Check status: `gh pr checks` or `curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])"`
- Poll until complete: loop every 30s up to 10 minutes.

## 5. Auto-Fixing CI Failures
- Get failure details (gh run list, gh run view, or curl logs)
- Fix code using file tools (`patch`, `write_file`)
- Commit and push: `git add . && git commit -m "fix: resolve CI failure in <check_name>" && git push`
- Verify CI status again.

## 6. Merging
- Squash merge: `gh pr merge --squash --delete-branch`
- Auto-merge (curl): enable via GraphQL API.

## 7. Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` |
| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |

## 8. Common Pitfalls
- Avoid mixing unrelated local commits with upstreamable changes; use clean branches.
- Ensure PR body file is safe (no command substitution).
- Handle cherry-pick conflicts by aborting and copying only intended paths.

## 9. Verification
- After pushing, verify PR is open and CI is passing.
- After merging, verify branch is deleted and main is updated.