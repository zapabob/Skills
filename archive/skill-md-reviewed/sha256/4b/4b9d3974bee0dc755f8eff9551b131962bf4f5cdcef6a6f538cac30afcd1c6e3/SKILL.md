---
name: hermes-upstream-redteam-security
description: >-
  Red-teams NousResearch/hermes-agent on upstream/main for AI-agent execution
  hardening (env/credential leakage, path traversal, SSRF, authz, tool-approval
  bypasses), opens non-duplicate King's English PRs, and tracks a 10-PR goal
  loop. Use when running the hermes upstream redteam security campaign,
  hardening Hermes agent safety boundaries, or opening security PRs to
  NousResearch/hermes-agent from a clean upstream worktree.
disable-model-invocation: true
---

# Hermes Upstream Redteam Security

Defensive security campaign against **official** Hermes Agent. Harden AI-agent
execution without gutting capability.

## Goal loop

Continue until **10 completed PRs** (merged or successfully opened and
CI-greenable; prefer opened+valid). Track progress in this skill's session
board and in a local fork `_docs/` report only — **never commit `_docs` to
upstream PRs**.

## Remotes and worktree

| Remote | Repo |
|--------|------|
| `upstream` | `NousResearch/hermes-agent` |
| `origin` | `zapabob/hermes-agent` (push contributor branches) |

```powershell
# Windows PowerShell: use ; not &&
cd "%USERPROFILE%\Documents\New project\hermes-agent"
git fetch upstream main
git worktree add ..\hermes-agent-sec-wt upstream/main
```

**Clean worktree rules:** branch from `upstream/main` only. Exclude fork-only
features, SillyTavern/VRChat overlays, and `_docs`. No fork drift in PRs.

## Decision tree (every finding)

```
1. Search issues/PRs first (gh)
2. Classify against upstream/main:
   ├─ FULLY closed + adequate tests → SKIP (true duplicate)
   ├─ EXISTS but INCOMPLETE (partial mitigation, wrong call site,
   │  missing sibling path, test gap, regression) → SALVAGE
   │     credit prior PR/issue → extend remaining gap → new PR
   └─ unreported / still broken → NEW minimal fix
3. Verify still broken on current upstream/main
   └─ cannot reproduce? → SKIP
4. Minimal fix on clean worktree branch
5. Tests (scripts/run_tests.sh or focused pytest via wrapper)
6. Push to origin → gh pr create -R NousResearch/hermes-agent
   (King's English; if salvage, state prior coverage vs remaining gap)
7. Update progress board k/10 + local _docs session report
```

## Salvage vs true duplicate

**Do NOT skip** when a prior issue/PR/fix exists but is incomplete.
Incomplete means: partial mitigation, wrong call site, missing sibling
path, test gap, or regression. Salvage the approach, credit the original
in the new PR body, and close the remaining gap with a minimal
capability-preserving patch.

**True duplicate only when** the vulnerability is **fully** closed on
`upstream/main` with adequate tests.

Before coding:

```powershell
gh search prs --repo NousResearch/hermes-agent "KEYWORD" --state open
gh search issues --repo NousResearch/hermes-agent "KEYWORD" --state open
gh api search/issues -f q="repo:NousResearch/hermes-agent is:pr KEYWORD"
```

**Known true-duplicate skip:** Slack multi-image redirect SSRF is
ALREADY_FIXED via #69482 / #62932 / `f54e8706f7` — do not reopen.

## Hardening focus (preserve excellence)

Priority surfaces:

1. Env / credential leakage to subprocesses, browsers, MCP, plugins
2. Path traversal / unsafe archive extraction / file tools / sync / backup / curator tar
3. SSRF / redirect / webhook / `download_url`
4. Authz on dashboard / API / gateway
5. Tool approval / dangerous-command bypasses (AI runaway / unexpected tools)

Fix the **security boundary**; do not gut features.

## Disclosure posture

- Defensive disclosure only
- No exploit PoCs beyond existing unit-test patterns
- Tests assert invariants (blocked path, sanitized env, rejected URL) — not weaponized payloads

## PR standards

- Language: **King's English**
- Scope: one vuln class per PR when practical
- Include: reproduction premise, minimal fix, test evidence
- Exclude: fork overlays, `_docs`, unrelated refactors

```powershell
git push -u origin HEAD
gh pr create -R NousResearch/hermes-agent --title "fix(security): ..." --body "$( @'
## Summary
- ...

## Test plan
- [ ] ...

'@ )"
```

## Progress tracking template

Copy and update each session:

```markdown
# Upstream redteam progress

Goal: 10/10 PRs (opened+valid or merged)

| # | PR URL | Title | Vuln class | Status |
|---|--------|-------|------------|--------|
| 1 | | | | open/merged/skipped |

Rejected / duplicates avoided:
- ...

Next targets:
- ...
```

Local log only: `fork` checkout `_docs/YYYY-MM-DD_hermes-upstream-redteam_{Agent}.md`.

## Session checklist

- [ ] `git fetch upstream main`
- [ ] Clean worktree from `upstream/main`
- [ ] Dedup search for each candidate
- [ ] Repro on upstream/main
- [ ] Minimal fix + tests
- [ ] PR in King's English to NousResearch/hermes-agent
- [ ] Update k/10 board + local `_docs` report
- [ ] Stop or continue until 10

## Additional resources

- Candidate hunt patterns: [reference.md](reference.md)
- Session report template: [progress-template.md](progress-template.md)
