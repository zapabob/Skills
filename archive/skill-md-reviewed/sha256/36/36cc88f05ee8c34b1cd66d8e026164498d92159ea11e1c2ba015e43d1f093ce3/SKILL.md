---
name: hermes-webui-upstream-redteam
description: >-
  Merges official nesquena/hermes-webui into the zapabob fork via
  scripts/merge_official_updates.py while preserving fork features, then
  red-teams the official tip for unresolved issues and unreported
  CVE/CVSS-class defects and opens King's English PRs. Use when the user asks
  to sync official Hermes WebUI, keep fork features, harden AI agent safety
  (env leaks, path traversal, runaway tools), or continue until N red-team PRs
  (default goal 15) are completed.
disable-model-invocation: false
---

# Hermes WebUI — Official Merge + Red-Team PR Loop

## Goal (verbatim)

ゴール＝15件完成する迄続ける

修正およびPRはAIエージェント実行基盤としての脆弱性、環境変数の漏洩、バストラバーサルなどのAIが予期しない動作をしないことを保証するように強固にする（hermes-WebUIのAIエージェントとしての優秀さは失わないこと、あくまでAIが暴走しないことを求める）

## When to use

- Official upstream sync / merge while keeping fork-only features
- Python merge script runs (`scripts/merge_official_updates.py`)
- Red-team review from the latest official tip
- Finding unresolved GitHub issues, duplicate-PR gaps, or unreported CVE/CVSS-class bugs
- Opening defensive PRs to `nesquena/hermes-webui` in King's English
- Continuing a multi-session campaign until **15 completed** red-team deliverables

## Definitions

| Term | Meaning |
|------|---------|
| **Completed item** | One of: (A) merged fork sync commit on `master` with CI green, (B) accepted upstream PR, (C) opened high-quality upstream PR with tests + King's English body that is **not** a duplicate of an open PR/issue for the same root cause |
| **Goal counter** | Track in `_docs/redteam-campaign-counter.md` — stop or pause only when count ≥ 15 or user aborts |
| **Fork features** | Irodori TTS, OPENCODE_API_KEY shared detection, Windows native launcher, `merge_official_updates.py`, fork update-check behavior |
| **Hardening focus** | Agent execution boundaries: env/secret leakage, path traversal / symlink escape, SSRF to metadata, unsafe subprocess, CSRF/auth gaps on agent tools — **without** removing legitimate agent capability |

## Phase A — Official merge (fork preserve)

1. Read `AGENTS.md`, `docs/CONTRACTS.md`, `scripts/merge_official_updates.py`.
2. Prefer isolated trial state unless the user explicitly wants real `HERMES_HOME`.
3. Dry-run then merge:

```powershell
cd "<hermes-WebUI-repo>"
py -3 scripts/merge_official_updates.py --dry-run
py -3 scripts/merge_official_updates.py
```

4. Conflict policy:
   - **Equivalent features** → take **official latest**, then re-apply **fork advantages** on top (do not invent parallel APIs).
   - **Fork-only surfaces** → keep local behavior; align call sites to **official APIs**.
   - Use `FORK_PRESERVE_HINTS` in the merge script as the conflict checklist.
5. Never drop: Irodori TTS paths, OPENCODE shared key detection, Windows launcher password/`-Open`, merge script itself, fork update-check tag filtering.
6. Update fork `[Unreleased]` CHANGELOG; do **not** rewrite official release sections.
7. Commit on `master` (or user-named main), push `origin`, drive CI to green (`gh run list` / `gh run watch`). Fix failing tests with minimal official-aligned patches.

## Phase B — Red team from official tip

1. Fetch and branch from official tip (not the fork tip):

```powershell
git fetch upstream master
git checkout -B redteam/<short-topic> upstream/master
```

2. Intake sources (defense-only; no exploit PoCs):
   - Open/closed issues labeled bug/security that are **unresolved** or weakly fixed
   - Open PRs — skip if the same root cause already has an open PR
   - Code paths: `api/routes.py` file/memory/workspace, TTS proxies, gateway subprocess, static path joins, env dumps, debug endpoints
3. Apply `deepresearch-defense-standard` before claiming CVE/CVSS severity. Prefer primary sources (NVD, GHSA, maintainer advisories). If no public CVE ID exists, describe as **CVE-class / CVSS-class** with impact, not a fake CVE number.
4. Prefer fixes that **constrain unexpected agent behavior** while preserving useful agent tools:
   - Deny symlink/path escape outside allowed roots
   - Redact secrets from logs/API responses
   - Bound subprocess argv (no shell), timeouts, concurrency locks
   - Loopback-only credential forwarding (Irodori pattern)
5. Ship PR to `nesquena/hermes-webui`:
   - Title/body in **King's English** (clear, formal, precise)
   - Tests for the invariant
   - No fork-only files (`_docs/`, Windows-only conveniences) unless the PR is about that feature upstream
6. Increment the campaign counter and write a short `_docs` log entry per completed item.

## Phase C — Campaign discipline (until 15)

```
Campaign Progress:
- [ ] Item count in _docs/redteam-campaign-counter.md
- [ ] Each item has: finding → fix → test → PR URL (or fork merge SHA + CI)
- [ ] No duplicate open PR for same root cause
- [ ] No exploit payloads / weaponized PoCs in repo or PR body
- [ ] Agent capability preserved; only runaway / leak / escape paths closed
```

If blocked (needs maintainer decision, cannot reproduce, duplicate), log as **blocked**, do **not** count toward 15, pick the next finding.

## Safety rules

- Defense and responsible disclosure only. Never write exploit PoCs, malware, or attack scripts.
- Do not print API keys, OAuth tokens, full `.env`, or `auth.json`.
- Do not delete real `~/.hermes` without explicit approval.
- Prefer `./scripts/test.sh` (or Windows `.venv` + targeted pytest) for verification.

## Output template (per red-team PR)

```markdown
## Summary
- What invariant was broken
- Why it matters for an AI agent execution host
- How the fix preserves legitimate agent capability

## Test plan
- [ ] Automated test for the invariant
- [ ] Manual smoke of the affected agent/UI path
```

## Additional resources

- Merge script: `scripts/merge_official_updates.py`
- Campaign counter: `_docs/redteam-campaign-counter.md`
- Fork preserve hints live inside the merge script `FORK_PRESERVE_HINTS`
