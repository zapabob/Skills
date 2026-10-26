---
name: pr-review-comment-fixes
description: "Delegate PR review fixes to Codex/Claude, then review diff."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Code-Review, PR, Codex, Claude-Code, Automation, Fixes]
    related_skills: [github-code-review, codex, claude-code, github-pr-workflow]
---

# PR Review Comment Fixes — AI-Delegated Workflow

When a maintainer leaves review comments on a PR, delegate the fix generation to Codex or Claude Code. You only review the generated changes.

## Overview

```
Maintainer Review Comments → Extract & Structure → Delegate to Codex/Claude → AI Generates Fixes → You Review Diff → Commit/Push
```

This skill provides the exact workflow, commands, and patterns to automate this cycle.

---

## Prerequisites

- **GitHub auth** configured (see `github-auth` skill)
- **Codex CLI** installed: `npm install -g @openai/codex` or `winget install --id OpenAI.Codex`
- **Claude Code** installed: `npm install -g @anthropic-ai/claude-code` and `claude auth login`
- Inside a git repository with the PR checked out locally

---

## Workflow: Step by Step

### 1. Fetch the PR and Review Comments

```bash
# Set up environment
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"

# Or inline setup
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # GITHUB_TOKEN from env or ~/.hermes/.env
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)

PR_NUMBER=123  # Replace with actual PR number
```

**Get review comments (structured):**

```bash
# With gh (easiest)
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews --jq '.[] | select(.state=="CHANGES_REQUESTED" or .state=="COMMENTED") | {user: .user.login, state: .state, body: .body, submitted_at: .submitted_at}'

# Get inline comments specifically
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments --jq '.[] | {path: .path, line: .line, side: .side, body: .body, user: .user.login, commit_id: .commit_id}'

# Get review threads (resolved/unresolved)
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/review_threads --jq '.[] | {path: .path, line: .line, comments: .comments[] | {user: .user.login, body: .body, created_at: .created_at}}'
```

### 2. Create Structured Fix Instructions

Transform review comments into a clear prompt for the AI agent. Save to a file for reference:

```bash
# Example: create-fix-prompt.sh
cat > /tmp/pr-${PR_NUMBER}-fixes.md << 'EOF'
# PR #${PR_NUMBER} — Review Comment Fixes

## Context
- Repository: ${OWNER}/${REPO}
- PR: #${PR_NUMBER}
- Base branch: main
- Current branch: $(git branch --show-current)

## Review Comments to Address

### 1. File: src/auth/login.ts, Line 45 (RIGHT side)
**Reviewer:** @maintainer
**Comment:** "This SQL query is vulnerable to injection. Use parameterized queries instead."
**Current code:**
```typescript
const query = `SELECT * FROM users WHERE email = '${email}'`;
```

### 2. File: src/utils/helpers.ts, Line 12
**Reviewer:** @maintainer
**Comment:** "Duplicated logic from src/core/utils.ts:34. Extract to shared utility."
**Current code:**
```typescript
export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}
```

### 3. File: tests/auth.test.ts
**Reviewer:** @maintainer
**Comment:** "Missing test for expired token case. Add test covering JWT expiration."
**Current code:** No test for expired tokens.

## Instructions for AI Agent
- Fix each comment in place
- Maintain existing code style and patterns
- Add tests where requested
- Run lint/typecheck after changes
- Commit each fix with a clear message referencing the review comment
EOF
```

### 3. Delegate to Codex (Recommended for Fixes)

**Option A: One-shot with print mode (fastest, non-interactive)**

```bash
cd /path/to/repo
# Checkout the PR branch if not already
git checkout pr-${PR_NUMBER}  # or: gh pr checkout ${PR_NUMBER}

# Run Codex to fix all comments
codex exec --full-auto "$(cat /tmp/pr-${PR_NUMBER}-fixes.md)

Fix all review comments listed above. After each fix:
1. Run: npm run lint && npm run typecheck
2. Run: npm test
3. Commit with message: 'fix: address review comment - <brief description>'
4. Push to the PR branch" --max-turns 20
```

**Option B: Background with monitoring (for complex fixes)**

```bash
# Start Codex in background
terminal(command="cd /path/to/repo && codex exec --full-auto '$(cat /tmp/pr-${PR_NUMBER}-fixes.md)

Fix all review comments. Run lint, typecheck, and tests after each fix. Commit each fix separately.' --max-turns 30", background=true, pty=true, notify_on_complete=true)

# Returns session_id — monitor with:
process(action="poll", session_id="<session_id>")
process(action="log", session_id="<session_id>")
```

**Option C: Interactive tmux session (for complex iterative work)**

```bash
tmux new-session -d -s codex-pr-${PR_NUMBER} -x 140 -y 40
tmux send-keys -t codex-pr-${PR_NUMBER} "cd /path/to/repo && codex --full-auto" Enter
sleep 3
tmux send-keys -t codex-pr-${PR_NUMBER} "$(cat /tmp/pr-${PR_NUMBER}-fixes.md | sed 's/"/\\"/g')" Enter
# Monitor:
tmux capture-pane -t codex-pr-${PR_NUMBER} -p -S -50
```

### 4. Delegate to Claude Code (Alternative)

**Print mode (recommended for automated fixes):**

```bash
cd /path/to/repo
claude -p "$(cat /tmp/pr-${PR_NUMBER}-fixes.md)

Fix all review comments. After each fix:
1. Run lint/typecheck/tests
2. Commit with clear message referencing the review comment" \
  --allowedTools "Read,Edit,Write,Bash" \
  --max-turns 25 \
  --output-format json
```

**With worktree (isolated, safe):**

```bash
# Create isolated worktree for the fixes
claude -w pr-${PR_NUMBER}-fixes --tmux -p "$(cat /tmp/pr-${PR_NUMBER}-fixes.md)

Fix all review comments in this worktree. Run all checks." \
  --allowedTools "Read,Edit,Write,Bash" \
  --max-turns 25
```

### 5. Review the Generated Changes

After AI completes, **you only review the diff**:

```bash
# See all changes made
git diff main...HEAD --stat
git diff main...HEAD

# Or if on the PR branch already:
git diff origin/main...HEAD

# Run full test suite to verify
npm run lint && npm run typecheck && npm test

# Review each commit
git log --oneline -10
git show --stat HEAD
```

### 6. Push and Update PR

```bash
# Push fixes to the PR branch
git push origin HEAD  # or: git push origin pr-${PR_NUMBER}

# Optionally: mark review threads as resolved via GitHub
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/review_threads/1/resolve --method PATCH  # for each thread
```

---

## Complete Automation Script

Save as `scripts/pr-fix-delegate.sh` in your repo:

```bash
#!/usr/bin/env bash
# pr-fix-delegate.sh — Delegate PR review comment fixes to Codex/Claude Code
# Usage: ./pr-fix-delegate.sh <PR_NUMBER> [codex|claude]

set -euo pipefail

PR_NUMBER="${1:-}"
AGENT="${2:-codex}"  # codex or claude

if [[ -z "$PR_NUMBER" ]]; then
  echo "Usage: $0 <PR_NUMBER> [codex|claude]"
  exit 1
fi

# Setup
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)

# Checkout PR
gh pr checkout "$PR_NUMBER" 2>/dev/null || git checkout "pr-$PR_NUMBER"

# Fetch review comments
echo "Fetching review comments for PR #$PR_NUMBER..."
REVIEW_COMMENTS=$(gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments --jq '.[] | "### \(.path):\(.line // .original_line) (\(.side // \"RIGHT\"))\n**Reviewer:** @\(.user.login)\n**Comment:** \(.body)\n"')

REVIEW_THREADS=$(gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/review_threads --jq '.[] | "### \(.path):\(.line // .original_line)\n**Thread:**\n\(.comments[] | \"- @\(.user.login): \(.body)\")\n"')

# Build prompt
PROMPT_FILE="/tmp/pr-${PR_NUMBER}-fixes.md"
cat > "$PROMPT_FILE" << EOF
# PR #${PR_NUMBER} — Review Comment Fixes

## Repository: ${OWNER}/${REPO}
## PR Branch: $(git branch --show-current)
## Base: origin/main

## Review Comments to Address

${REVIEW_COMMENTS}

## Review Threads

${REVIEW_THREADS}

## Instructions
Fix each review comment in place. For each fix:
1. Make the minimal change to address the comment
2. Run: npm run lint && npm run typecheck
3. Run: npm test
4. Commit with message: "fix: address review comment - <short description> [#${PR_NUMBER}]"
5. Push when all fixes are complete

Maintain existing code style. Add tests where reviewers requested them.
EOF

echo "Prompt saved to $PROMPT_FILE"
echo "Delegating to $AGENT..."

if [[ "$AGENT" == "codex" ]]; then
  codex exec --full-auto "$(cat "$PROMPT_FILE")" --max-turns 30
elif [[ "$AGENT" == "claude" ]]; then
  claude -p "$(cat "$PROMPT_FILE")" --allowedTools "Read,Edit,Write,Bash" --max-turns 30 --output-format json
else
  echo "Unknown agent: $AGENT. Use 'codex' or 'claude'"
  exit 1
fi

echo "Done. Review changes with: git diff origin/main...HEAD"
```

---

## Review Checklist (Your Part Only)

After AI generates fixes, you only need to verify:

- [ ] **All review comments addressed** — cross-reference each comment with the diff
- [ ] **No regressions** — full test suite passes
- [ ] **Code style consistent** — lint/typecheck pass
- [ ] **Commits are clean** — each fix in its own commit with clear message
- [ ] **No over-engineering** — AI didn't add unnecessary abstractions
- [ ] **Security issues actually fixed** — not just moved around

---

## Common Patterns & Pitfalls

### Pattern: Multiple Reviewers, Conflicting Comments
```bash
# Fetch all comments, group by file, resolve conflicts manually before delegating
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments --jq 'group_by(.path) | .[] | {file: .[0].path, comments: map({line, body, user})}'
```

### Pattern: Large PR — Fix in Batches
```bash
# Split by file or priority
# Batch 1: Critical security fixes
# Batch 2: Style/nits
# Batch 3: Test additions
```

### Pattern: PR Requires Rebase First
```bash
git fetch origin
git rebase origin/main
# Resolve conflicts, then delegate fixes
```

### Pitfall: AI Over-Fixing
**Prevent:** Add to prompt: "Make MINIMAL changes. Only fix what the review comments explicitly request. Do not refactor unrelated code."

### Pitfall: AI Breaking Tests
**Prevent:** Add to prompt: "Run full test suite after EACH fix. If tests fail, revert that fix and try a different approach."

### Pitfall: Codex/Claude Can't Find Files
**Fix:** Ensure you're in the repo root. Add `--add-dir` for monorepos (Claude) or run from correct worktree.

---

## Agent Comparison

| Aspect | Codex (`--full-auto`) | Claude Code (`-p`) |
|--------|----------------------|-------------------|
| **Speed** | Fast, auto-approves edits | Slightly slower, more careful |
| **Test Running** | Good at running commands | Excellent at running/iterating tests |
| **Context** | Reads files as needed | Can pipe large diffs via stdin |
| **Output** | Terminal streaming | JSON structured output |
| **Best For** | Quick fixes, many files | Complex logic, test-heavy fixes |

---

## Integration with Hermes

Add to your Hermes workflow:

```yaml
# In a Hermes skill or plan
- name: "Fetch PR review comments"
  tool: terminal
  args:
    command: "gh api repos/owner/repo/pulls/123/comments"

- name: "Delegate to Codex"
  tool: terminal
  args:
    command: "codex exec --full-auto 'Fix all comments...' --max-turns 20"
    background: true
    pty: true
    notify_on_complete: true

- name: "Monitor Codex"
  tool: process
  args:
    action: "wait"
    session_id: "<from previous>"

- name: "Review diff"
  tool: terminal
  args:
    command: "git diff origin/main...HEAD"
```

---

## References

- [GitHub Code Review skill](github-code-review) — for review mechanics
- [Codex skill](codex) — Codex CLI reference
- [Claude Code skill](claude-code) — Claude Code CLI reference
- [GitHub PR Workflow skill](github-pr-workflow) — full PR lifecycle