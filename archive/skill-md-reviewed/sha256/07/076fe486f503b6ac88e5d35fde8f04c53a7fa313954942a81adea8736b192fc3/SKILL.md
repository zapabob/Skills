---
name: open-source-maintainer-applications
description: "Prepare applications for open-source maintainer programs, grants, credits, and contributor recognition using verified GitHub evidence."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [open-source, maintainer, grants, applications, github, codex, contributor-credit]
---

# Open Source Maintainer Applications

Use this skill when helping the user apply to open-source maintainer programs, AI/OSS grants, cloud/API credit programs, contributor funds, or similar opportunities where they must explain project impact and attach credible contribution evidence.

## Core approach

1. **Separate program fit from contribution proof.**
   - Program fit: what the program wants to fund or support.
   - Contribution proof: what the user has actually shipped, submitted, maintained, or been credited for.
2. **Prefer verified wording over hype.**
   - Use `submitted upstream PRs` for open PRs.
   - Use `merged`, `included in release`, or `credited upstream` only after checking GitHub metadata.
   - If a PR was closed but its work was salvaged/cherry-picked, say exactly that.
3. **Build the application around maintainer workload.**
   Strong themes for OSS support programs include issue triage, PR review, release workflows, security hardening, cross-platform reliability, documentation, automation, and safe supervision of AI-generated work.
4. **Produce both a one-page narrative and an evidence appendix.**
   - Narrative: concise, funder-facing, outcome-oriented.
   - Appendix: PRs/issues/commits/releases with URLs and accurate states.

## GitHub evidence checklist

When the user wants to attach GitHub history:

1. Confirm the GitHub login with `gh api user --jq '.login'` or the user-provided handle.
2. Search PRs/issues by author for each relevant repo:
   ```bash
   gh search prs --repo OWNER/REPO --author USER --limit 100 --json number,title,state,url,createdAt,updatedAt
   gh search issues --repo OWNER/REPO --author USER --limit 100 --json number,title,state,url,createdAt,updatedAt
   ```
3. For PRs that matter, inspect merge metadata:
   ```bash
   gh pr view N --repo OWNER/REPO --json number,title,state,url,mergedAt,mergeCommit,reviewDecision,additions,deletions,changedFiles
   ```
4. Search commits for contributor credit, co-author lines, salvage notes, and PR numbers:
   ```bash
   gh search commits USER --repo OWNER/REPO --limit 30 --json sha,commit,url
   gh search commits 'Co-authored-by USER' --repo OWNER/REPO --limit 30 --json sha,commit,url
   gh search commits 'Salvaged from PR #N' --repo OWNER/REPO --limit 30 --json sha,commit,url
   ```
5. Fetch decisive commits to quote exact messages and authorship:
   ```bash
   gh api repos/OWNER/REPO/commits/SHA
   ```
6. Verify release/tag inclusion when claiming a contribution shipped:
   ```bash
   gh release list --repo OWNER/REPO --limit 100
   gh api repos/OWNER/REPO/compare/COMMIT_SHA...TAG
   ```
   Interpret compare carefully:
   - `status: ahead` with the tag ahead of the commit means the tag contains the commit.
   - `status: behind` or `diverged` needs closer inspection; do not claim release inclusion unless clear.

## Wording patterns

Use accurate evidence language:

- Open PRs: `I have submitted upstream PRs covering ...`
- Closed but salvaged: `PR #N was closed, but its work was salvaged/cherry-picked into upstream commit SHA and credited to USER.`
- Release inclusion: `That commit was verified as included in the vX.Y release line.`
- Co-author only: `Additional upstream commits include Co-authored-by credit for ...`
- Not merged: `Most other PRs are open or under review, so I describe them as submitted contributions rather than accepted/merged work.`

Avoid overclaiming:

- Do not call a closed PR `merged` unless `mergedAt` is present.
- Do not call co-author credit release inclusion unless tag containment was verified.
- Do not inflate application claims with private or unverified work.

## Suggested application structure

1. **Opening identity:** who the applicant is and what OSS workflow/project they maintain or contribute to.
2. **Problem:** invisible maintainer work: triage, review, releases, security, support, cross-platform testing.
3. **Approach:** how the applicant uses the target tool/program to reduce that burden.
4. **Evidence:** concise upstream contribution summary with links.
5. **Use of support:** concrete plan for credits/funding/access.
6. **Impact:** reusable templates, docs, workflows, or improvements for other maintainers.

## References

- `references/codex-for-oss-hermes-evidence.md` — session pattern for Codex for Open Source positioning around Hermes Agent/Hermes WebUI and verifying salvaged/cherry-picked contributor credit.
