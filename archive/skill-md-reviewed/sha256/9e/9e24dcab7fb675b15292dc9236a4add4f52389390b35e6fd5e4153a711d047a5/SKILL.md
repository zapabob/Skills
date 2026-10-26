---
name: windows-hermes-upstream-sync
description: Use when the user wants the Hermes fork synced with official upstream on this Windows PC while preserving fork-local behavior, avoiding duplicate CVE-class fixes, and finishing with publish-grade verification.
argument-hint: "[repo-path] [target-branch]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Windows Hermes Upstream Sync

## When to use

Use this when the user asks for a real upstream intake in or around `%USERPROFILE%\Documents\New project\hermes-agent`, especially if they mention:
- latest official features, vulnerability updates, or bug fixes
- preserving custom features or fork-owned behavior
- using the repo's Python sync workflow
- avoiding duplicate CVE or PR work
- ending on a clean `main` publish

Non-goals:
- commentary-only repo summaries
- blind fast-forwarding without merge-policy review
- broad cleanup of unrelated local work

## Inputs / context to gather

1. Confirm repo shape and remotes:
- `git remote -v`
- `git status --short --branch --untracked-files=all`
- `git worktree list`

2. Read the repo's sync truth first:
- `scripts/sync_all.py`
- `scripts/merge_tools/hermes-merge-conflict-strategies.json`
- If the task starts with a frozen campaign/snapshot phase, also read `scripts/upstream/snapshot_sync.py` and the latest `_docs/upstream-campaigns/` metadata.

3. Check whether the user also wants security or duplicate-fix avoidance:
- inspect relevant open PRs/issues before selecting local fixes

4. Identify local-only artifacts that must not leak into the publish path:
- `_docs/`
- generated/private media
- runtime logs
- local overlays that belong in `.git/info/exclude`, not tracked ignore rules

## Procedure

1. Verify the intended publish branch and whether another worktree already owns it.
- If `main` is already checked out elsewhere, use `git switch --ignore-other-worktrees main` instead of disturbing the other worktree.

2. Inspect divergence before editing.
- Fetch both `origin` and `upstream`.
- Measure `origin/main` vs `upstream/main` and note whether local fork commits or uncommitted work need to be preserved.

3. Read the merge-policy map before choosing a merge path.
- Treat `scripts/sync_all.py` as the primary entrypoint.
- Treat `scripts/merge_tools/hermes-merge-conflict-strategies.json` as the source of truth for `upstream`, `official_with_overlay`, and `preserve_custom` paths.
- Run `python scripts/sync_all.py --dry-run --allow-preflight-blockers` first so you can see overlap counts and whether `manual_api_followup` or `official_with_overlay` buckets are going to dominate the work.

4. If the user asked to avoid duplicate CVE-class work, triage upstream PRs/issues early.
- Do this before inventing new local security fixes.
- Prefer the upstream/open-PR path when it already covers the same family.

5. Protect local-only artifacts without changing repo policy.
- Use `.git/info/exclude` for private/generated machine-local files.
- Keep fork-owned custom features and generated docs out of the PR scope unless the user explicitly asks otherwise.

6. Execute the sync with the repo-native workflow, then preserve fork-local work deliberately.
- Prefer the repo's Python automation over ad hoc manual conflict handling.
- If uncommitted fork-local work must survive, isolate it on a side branch/worktree, then replay it onto the sync result in a controlled way.

7. For a requested snapshot freeze before product integration, make the baseline explicit.
- Use the prior frozen upstream SHA as `snapshot_sync.py --base-sha`; do not substitute Git merge-base, which can re-count the prior campaign.
- Generate report-only metadata from an isolated worktree, verify archive blobs byte-for-byte, and use deliberate `git add -f` only for intended ignored `_docs` campaign artifacts.
- Keep Phase 0 status explicit: metadata/generator completion is not product-code integration or a finished upstream sync.

8. Repair Windows-specific fallout before publish.
- If `uv` mutates the venv and hits access-denied errors, use the existing `.venv\Scripts\ruff.exe` directly for lint-only verification.
- For Python tests after a sync, prefer `.venv\Scripts\python.exe -m pytest ...`; the system Python on this PC has missed repo plugins such as `pytest_asyncio`.
- If `uv.lock` becomes inconsistent during conflict resolution, restore it to the last known-good state before re-running verification.
- Normalize touched files to LF before staging if CRLF churn causes false trailing-whitespace failures.
- If the user wants validation with the latest `uv`, prefer `%USERPROFILE%\.local\bin\uv.exe` plus `UV_PROJECT_ENVIRONMENT='.venv-ci'` so the live `.venv` does not block the run.
- If runtime advisory validation is part of the task, use explicit `uv run --with <package>==<version> ...` import smoke checks rather than assuming `--extra dev` includes the runtime package.
- If editable install fails under build isolation on Windows, retry the sync/validation path with `--no-build-isolation`.
- If Desktop restart blocks on an OAuth MCP prompt, inspect `~/.hermes/profiles/*/config.yaml` and disable only the blocking server (for example `mcp_servers.worldmonitor`) rather than removing unrelated tools.
- If Desktop relaunch is part of closeout, pass `Start-Process -ArgumentList` as one quoted string so `--hermes-root` and `--cwd` under `%USERPROFILE%\Documents\New project\...` do not get split.
- If Hermes logging fails with `No space left on device`, move old `%USERPROFILE%\.hermes\logs` content to H: instead of deleting evidence.

9. Finish with publish-grade verification.
- `git diff --check`
- `.venv\Scripts\ruff.exe check ...`
- targeted `pytest` for touched risk areas
- `git rev-list --left-right --count origin/main...HEAD`
- `git ls-remote origin refs/heads/main`
- `git status --short --branch`
- `gh run list --repo zapabob/hermes-agent --branch main` when CI freshness is part of the ask
- if Desktop/runtime proof is requested, read the newest `HERMES_BACKEND_READY` or `HERMES_DASHBOARD_READY` port from `%USERPROFILE%\.hermes\logs\desktop.log`, prefer `netstat -ano` over `Get-NetTCPConnection` on this host, confirm the matching listener/process, and probe the applicable exact-port endpoint (`/api/health` or `/api/status`). For an explicit llama-off requirement, confirm identity before stopping it and then prove both `llama-server.exe` process count=0 and no observed `8080–8082` listeners.

## Efficiency plan

- Read the sync policy files once, then reuse that map through the whole run.
- Triage duplicate-fix risk before editing so you do not build a patch that upstream already has in flight.
- Keep verification focused on touched surfaces and publish alignment.
- Stop treating `manual_api_followup` / `official_with_overlay` paths as normal cherry-pick targets once the dry-run shows they dominate the overlap.
- Stop once local checks, branch alignment, and requested CI evidence all agree.
- Query Actions with the owning fork explicitly (for example `gh run view <run-id> --repo zapabob/hermes-agent`); a run ID against the upstream repo can return 404.

## Pitfalls and fixes

- Symptom: `git switch main` fails because the branch is already used by another worktree.
- Likely cause: another local worktree already owns `main`.
- Fix: use `git switch --ignore-other-worktrees main`.

- Symptom: `uv run --with ruff ...` fails with Windows access-denied errors in `.venv`.
- Likely cause: `uv` is mutating the environment during lint invocation.
- Fix: run `.venv\Scripts\ruff.exe` directly.

- Symptom: the sync appears complete but `uv.lock` or `package-lock.json` is broken afterward.
- Likely cause: conflict resolution drift or wrong merge-policy classification.
- Fix: restore the last known-good lock state, then re-run lock verification.

- Symptom: detached Desktop verification looks healthy but the backend never answers or the wrong path gets launched.
- Likely cause: `Start-Process -ArgumentList` split the `New project` path.
- Fix: pass the Desktop launch arguments as one quoted string, then verify the newest ready port directly.

- Symptom: restart verification claims nothing is listening even though the Desktop later comes up.
- Likely cause: `Get-NetTCPConnection` returned stale or misleading host state.
- Fix: trust the newest `HERMES_DASHBOARD_READY` line, use `netstat -ano`, and probe the exact backend port with HTTP.

- Symptom: closeout says llama was not touched, but the requirement was for llama to be off.
- Likely cause: non-interference was mistaken for the required state.
- Fix: inspect the candidate process name, executable path, command line, and listener; stop only the matching identity, then prove process count and observed-port listener count are both zero while the requested Desktop/backend health remains good.

- Symptom: CI run lookup returns 404.
- Likely cause: the run was queried on the official upstream rather than the fork that owns it.
- Fix: include the fork repository explicitly in `gh run view` / `gh run list`.

- Symptom: Hermes restart logs fail with `No space left on device`.
- Likely cause: `C:` is too full for ongoing logging.
- Fix: move older Hermes logs to H:, then retry the restart/verification flow.

- Symptom: repeated cherry-picks keep conflicting in hot files.
- Likely cause: the run skipped the repo-native inventory/overlay classification and is forcing ad hoc commit replay.
- Fix: restart from `scripts/sync_all.py --dry-run --allow-preflight-blockers` and handle `manual_api_followup` / `official_with_overlay` as explicit overlay work.

- Symptom: snapshot report generation is excessively slow.
- Likely cause: a Git subprocess is spawned per commit.
- Fix: batch commit subjects and paths using one `git log` invocation before retrying.

- Symptom: a frozen snapshot is reported as a completed sync.
- Likely cause: Phase 0 metadata work was conflated with product-code integration.
- Fix: report the freeze separately and retain the remaining integration work as open.

- Symptom: a merge stops on brand-new upstream skills even though there are no textual conflicts.
- Likely cause: the merge-policy map has no rule for the new upstream-only paths.
- Fix: add explicit `upstream` entries in `scripts/merge_tools/hermes-merge-conflict-strategies.json`, then rerun the repo-native sync.

- Symptom: `gh workflow run ci.yml` fails with HTTP 422 or `gh run watch` times out.
- Likely cause: the workflow has no `workflow_dispatch`, or the watch is slower than the tool timeout.
- Fix: inspect the push-triggered run by SHA and poll with `gh run view` / `gh run list` instead.

- Symptom: staging introduces a flood of CRLF/LF or trailing-whitespace noise.
- Likely cause: Windows line-ending normalization changed during the conflict flow.
- Fix: normalize touched files to LF first, then use ordinary `git add`.

- Symptom: the agent starts building a security patch that duplicates upstream work.
- Likely cause: PR/issue triage happened too late.
- Fix: check the upstream PR/issue queue first and only add local fixes for uncovered gaps.

## Verification checklist

- The sync used `scripts/sync_all.py` and the policy map rather than a blind manual merge.
- Fork-owned paths and requested exclusions stayed out of the publish scope.
- Local-only generated/private artifacts are handled via `.git/info/exclude` or equivalent local-only means.
- `git diff --check` is clean.
- `ruff` and targeted `pytest` passed for the touched surfaces.
- `git rev-list --left-right --count origin/main...HEAD` shows the expected publish alignment.
- `git status --short --branch` matches the intended clean branch state.
- If CI proof was requested, fresh GitHub Actions evidence was checked before closeout.
- If Desktop/runtime proof was requested, the final proof used the newest ready port, matching listener/process, direct HTTP checks, and host-appropriate listener checks rather than only script exit status.
- If llama-off was requested, target identity was verified before any stop, `llama-server.exe` and observed `8080–8082` listeners were absent afterward, and Desktop/backend health was rechecked.
