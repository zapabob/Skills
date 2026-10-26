---
name: fork-upstream-sync
description: "Sync a fork to upstream, keeping custom features."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, github, fork, upstream, merge, conflict, schema, drift]
    related_skills: [git-pr-fork-routing, github-repo-management, github-pr-workflow]
---

# Fork ↔ Upstream Sync (customizations preserved)

Use when the user says any of: "取り込んで / 追従 / pull in upstream's latest features, security updates and bugfixes while keeping my custom features", "sync my fork", "rebase my fork on upstream", "keep my custom API in step with upstream's latest".

This is a **class of task**, not a one-off: fork is N commits behind, has a small set of fork-only files, and the user wants (a) upstream's fixes, (b) their customizations intact, and (c) their custom data/config still valid against upstream's *current* schema/API.

## Step 0 — Verify the checkout is actually the fork (non-skippable)

A local directory named after the repo is frequently **not** the fork. Check before touching anything:

```bash
git remote -v            # origin must be the FORK, not upstream
git branch -a            # "* (no branch)" == detached
cat .git/shallow         # non-empty == shallow clone, cannot merge history
```

Common trap seen in practice: the local dir was a **shallow, detached tag checkout of upstream** (`origin` = upstream URL, `HEAD` = a release tag, `.git/shallow` present, 1 commit of history). Merging there is impossible and silently wrong.

**Fix: clone the fork fresh into a scratch dir and work there.** Do not try to repair the broken checkout. Tell the user plainly that the local dir was not the fork — it changes their mental model of the task.

```bash
git clone https://github.com/<YOU>/<repo>.git /tmp/<repo>-merge
cd /tmp/<repo>-merge
git remote add upstream https://github.com/<UPSTREAM>/<repo>.git
git fetch upstream
git rev-list --left-right --count HEAD...upstream/main   # ahead <TAB> behind
```

## Step 1 — Survey before merging

Two numbers decide the strategy:

- `git log --oneline upstream/main..HEAD` — the **fork-only commits**. If this is 1–3 commits of config/docs, a merge is trivially safe. If it's a divergent feature branch, expect real conflicts.
- `git diff --stat upstream/main...HEAD` — the exact fork-only file set. **This list IS the protection policy** for step 2.
- Overlap of `diff --name-only upstream/main...HEAD` and `diff --name-only HEAD...upstream/main` = the only files that can conflict. Usually it's just lockfiles.

## Step 2 — Merge with an explicit ours/theirs policy

Write the policy down as code, don't resolve by hand. Use `scripts/merge_upstream.py` in this skill (edit the constants at the top):

- `OURS_PATHS` — fork-only config/state dirs (`.akari/`, `.claude/`, custom reports). Always `--ours`.
- `THEIRS_PATHS` — **generated** artifacts (`package-lock.json`, `poetry.lock`, `uv.lock`). Always `--theirs`; the fork's lockfile is stale by definition and regenerating from upstream's manifest is correct.
- Anything else conflicting → stop and surface to the user.

```bash
python scripts/merge_upstream.py --report    # triage: security / fix / feature / other
python scripts/merge_upstream.py --merge     # branch merge/upstream-YYYY-MM-DD
```

Use `--no-ff` onto a dated branch (`merge/upstream-YYYY-MM-DD`), **never** merge straight into `main`. Push the branch; let the user open the PR.

Classify the incoming commits into security / fix / feature / other and report the counts. When the user asks for "脆弱性更新" / security updates specifically and the security bucket is 0, **say so explicitly** rather than letting the reader assume security work was included.

## Step 3 — Verify the custom API still tracks upstream (the part people skip)

Merging cleanly does **not** mean the fork's custom data still matches upstream's contract. Upstream may have changed a JSON Schema or a TS interface that the fork's config files must satisfy. Validate mechanically with `scripts/verify_custom_api.py`:

- Pair each fork-only data file with upstream's current schema (`packages/schemas/*.schema.json` or equivalent) and validate with `jsonschema`.
- For custom files with **no** upstream schema, locate the governing TS/py interface and diff the key set by hand. Check whether upstream parses it as `Partial<T>` / with defaults — if so, extra fork-only keys are a **safe extension**, not drift. If upstream does a strict parse, extra keys are a break.
- The script falls back to a structural check (required keys, types, enums, `additionalProperties`) when `jsonschema` is unavailable, so it always yields a verdict.

## Step 4 — Report honestly what was NOT verified

A merge that compiles in your head is not a verified merge. State the residual risk explicitly:

- `npm ci` / `build` / `lint` / tests **not run** (e.g. no `node_modules`) → runtime regression unverified.
- Lockfile taken from upstream → fork-specific deps may need reinstall.
- Branch pushed, **not** merged to main.

Then offer to run the build. Do not describe the merge as "done" when only the git operation is done.

## Step 5 — Generic Harness Independence (Phase 2-4: after sync is stable)

When the fork's goal shifts from "track upstream" to "grow as an independent generic harness" (e.g. `zapabob/hermes-agent-windows` as Windows AI workstation base, zero runtime dependency on `NousResearch/hermes-agent`), extend the lifecycle:

### 5a. Brand-separation audit (Phase 2)

Before declaring independence, audit hard-coded upstream brand strings so future merges stay clean:

```bash
# Find residual brand references that would re-entangle merges
rg -n "NousResearch|nous-research|hermes-agent.*upstream" --glob '!uv.lock' --glob '!*.bak'
# Classify each hit: attribution (keep) vs. runtime dependency (remove)
# Attribution stays in README/LICENSE/CARRY.yaml; runtime deps must be zero
py -3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print([x for x in d['project']['dependencies'] if 'nous' in x.lower()])"
# Expect [] — no PyPI dep on nous
```

Record the result in `_docs/YYYY-MM-DD_generic-harness-independence.md` and `fork/harness/GENERIC_HARNESS.md` (the permanent harness definition). Patch `fork/README.md` with an Identity block declaring `upstream = fetch-only, zero runtime dependency`.

### 5b. Harness growth policy (Phase 3-4)

- **Narrow waist**: keep `run_agent.py` / `gateway/` / `tool registry` thin; new capability goes to `plugins/` / `skills/` / `downstream/` (Footprint Ladder).
- **Windows Tier-1**: any new feature touching paths/processes/IPC must have a `WINDOWS_PLATFORM_CONTRACT.md` regression.
- **Freeze gate**: when upstream stalls (90 days no `main` activity or architectural deadlock), freeze `UPSTREAM_SNAPSHOT.json` at the last SHA and archive `scripts/sync_all.py` — thereafter the fork owns its release cycle.
- **A2A decision meetings**: when Phase 2 vs. expansion priority is contested, run a 4-perspective `delegate_task` batch (conservative / expansion / risk-CI / operations) to force explicit trade-offs before committing. See `references/generic-harness-independence.md`.

## Pitfalls

- **A repo dir with the upstream URL in `origin` is not your fork.** Always `git remote -v` first; re-clone rather than repair.
- **Shallow clones cannot merge** (`.git/shallow` present, no merge base). Re-clone with full history.
- **Don't hand-resolve lockfile conflicts.** Take theirs and regenerate.
- **Don't merge into `main` directly** on a 100+ commit catch-up. Dated merge branch + PR.
- **Don't claim security fixes were pulled in** unless the commit classification actually found some.
- **Windows:** the real interpreter is `py -3`; bare `python` may be the Microsoft Store stub. Invoke as `py -3 scripts/merge_upstream.py`.
- Write the implementation log to the **project's** `_docs/YYYY-MM-DD_<topic>_<AI>.md` per the PC-wide AGENTS.md baseline, even when the merge itself happened in a scratch clone.
- Committing the two scripts into the fork itself is a good outcome — it makes the next catch-up a one-command operation.

## Bundled files

- `scripts/merge_upstream.py` — survey + policy-guarded merge + fork-file survival assertion.
- `scripts/verify_custom_api.py` — validate fork-only JSON against upstream's current schemas; reports drift.
