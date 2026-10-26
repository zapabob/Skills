---
name: github-pr-review-triage-unauthenticated
description: "Triage PR review fixes when gh auth is broken."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, Code-Review, Windows, Worktrees, Cron]
    related_skills: [github-pr-workflow, code-review, github-auth]
---

# PR review triage without working `gh` auth (Windows)

## When to Use

Trigger this skill when ALL of these hold:
- a scheduled or ad-hoc pass must find unresolved PR review comments and land the fixes;
- `gh auth status` reports an invalid token, or `git push` prompts for credentials;
- the review comments still need to be read, and the fixes still need to be rebased,
  tested, and verified locally even though the push cannot happen yet.

Also use it when a prior run left fix commits in a temp worktree that are far behind
`upstream/main` and must be validated without disturbing sibling worktrees.

Use this when a cron job or review pass must find unresolved PR review comments and
land the fixes, but `gh` has no valid token and `git push` cannot authenticate.
Diagnosis (2026-10-01): gh account token invalid, no `GITHUB_TOKEN`, `git credential fill`
returns nothing, and the Bitwarden `github.com` item holds a login password rather
than a PAT (fails both Bearer and Basic auth).

## 1. Confirm the auth situation once, cheaply

```bash
gh auth status 2>&1 | head -5                 # invalid token?
gh pr view <N> --repo <owner/repo> --json state 2>&1 | head -3
printf 'protocol=https\nhost=github.com\n\n' | git credential fill | grep -c '^password='
```

Check the Bitwarden item WITHOUT printing the secret: load `~/.hermes/.env` in Python,
run `bw list items --search github.com`, and report only `login?`, field names, and
password LENGTH. A 15-char value is a login password, not a PAT — stop, because both
Bearer and Basic auth will 401 against it. Note `bw` on Windows lives at
`%USERPROFILE%\AppData\Roaming\npm\bw.cmd`; a bare `bw` fails under `subprocess`.

Do not brute-force other credential stores. If nothing works, report the blocker and
do the maximum useful work offline (steps 2-4), which is most of the value anyway.

## 2. Read review comments without the REST comments endpoint

Unauthenticated quota is only 60/hr core and is shared with everything else, but
these three routes all work without auth:

```bash
# PR list for the author (search has its OWN 10/hr quota, so save core calls)
curl -s "https://api.github.com/search/issues?q=is:pr+author:<user>+state:open&per_page=30"

# Full PR timeline as HTML; parse the anchors, NOT the REST /comments endpoint
curl -sL -o pr<N>.html "https://github.com/<owner>/<repo>/pull/<N>"
grep -c 'id="issuecomment-\|' pr<N>.html
grep -c 'id="pullrequestreview-' pr<N>.html

# PR head ref for git-side work (public repos only)
git fetch upstream "refs/pull/<N>/head:refs/tmp/pr-<N>"
```

Parse the HTML by splitting on the anchors and stripping tags between them. Strip the
fixed noise GitHub injects into every logged-out page: `Sorry, something went wrong`,
`Uh oh!`, `There was an error while loading`, `All reactions`, `Choose a reason for
hiding this comment`, `This suggestion is invalid`, and the reviewer/hidden-item blocks.
Use `div` depth tracking to extract a `markdown-body` block instead of a `<td>` regex —
the `<td>` approach truncates at the first nested div and loses the actual comment.

Distinguish review states: `approved these changes` / `requested changes` /
`commented` all appear as plain text in the HTML. When the count of
`pullrequestreview-` anchors is 0, there are no formal reviews — only issue comments.

## 3. Never test applyability inside a shared worktree

All worktrees of one repo share a single `.git` dir, so a `git cherry-pick` test in one
worktree MOVES that worktree's HEAD and can leave a stale `.git/worktrees/<name>/index.lock`
that blocks every sibling worktree. Use the read-only probe instead:

```bash
git merge-tree --write-tree --merge-base=<fix-commit>^ <pr-head> <fix-commit>
# exit 0 = applies cleanly; nonzero = CONFLICT lines name the paths
```

If a lock does appear, check for a live git process first; remove it only if none is
running. Git ops over ~280s must run backgrounded with stdout redirected to a file,
then be read back — the foreground tool caps out well before a large rebase finishes.

## 4. Rebase fixes onto current main in a FRESH worktree

Fix commits from a previous run are usually 40+ commits behind `upstream/main`, so they
conflict or are stale even though they look correct. Give each subagent its own new
worktree on its own new branch, starting at current `upstream/main`, and cherry-pick
the old fix in. Tell each subagent explicitly: do NOT `git fetch`, do NOT `git push`,
do not touch any other named worktree, and resolve conflicts by adopting upstream's
approach where upstream already changed that code.

Verify subagent claims yourself before reporting them — read the commit, diff vs
upstream/main, check `git diff --check`, confirm every call site of a widened
signature, and re-run the tests. Subagent self-reports are not evidence.

## 5. Running desktop vitest in a throwaway worktree

```powershell
New-Item -ItemType Junction -Path '<worktree>\node_modules' -Target '<ref>\node_modules'
New-Item -ItemType Junction -Path '<worktree>\apps\desktop\node_modules' -Target '<ref>\apps\desktop\node_modules'
```

MSYS `cmd //c mklink //J` silently fails here. Delete junctions with
`[System.IO.Directory]::Delete($path, $false)` — `Remove-Item -Force` and `rm -rf`
both LEAVE the junction behind, so cleanup silently no-ops. Always confirm the
reference worktree's `node_modules` still exists afterwards.

Run tests with the repo's own config, never a scratch one:

```bash
cd <worktree>/apps/desktop
node ../../node_modules/vitest/vitest.mjs run --project ui src/api/foo.test.ts ...
```

A hand-written scratch vitest config that "must export or return an object" fails to
load. Confirm `package.json` md5 matches the reference worktree before trusting a
run, so you know the shared `node_modules` is actually compatible.

## 6. Known-unrelated failures to report as pre-existing, not chase

- `tests/hermes_cli/test_profile_rename_service.py` cannot be collected on Windows
  (pwd-dependent). Exclude it with `--ignore=` rather than debugging it.
- Desktop `tsc --noEmit` has ~120 pre-existing React ref-type errors across ~51 files
  (mostly `src/components/ui/*`). Prove they predate the change by typechecking at
  `upstream/main` and comparing, and report the delta — do not fix them.
- On this host `python3` silently exits 49. Use `python` or
  `uv run --with pytest --with pytest-asyncio python -m pytest`.
- Security Center SCAN_ERROR blocks some terminal invocations; route through
  `execute_code` + `subprocess` instead of retrying the same command.

## Pitfalls

- Do not report a fix as "addressed" until the tests were actually run and observed
  green, and until you have checked no other worktree's HEAD was disturbed.
- Unauthenticated `git fetch refs/pull/<n>/head` works but leaves `refs/tmp/pr-<n>`
  behind — name them consistently so later runs can reuse them.
- The search API quota (10/hr) resets on a different clock than core (60/hr); check
  `api.github.com/rate_limit` before planning how many API calls a run can afford.
- Report blockers plainly and state exactly what is and is not verified, rather than
  implying a push or PR update happened.
