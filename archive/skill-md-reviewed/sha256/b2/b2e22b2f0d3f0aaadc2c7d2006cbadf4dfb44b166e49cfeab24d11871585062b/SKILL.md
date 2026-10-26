---
name: hermes-repository-organization
description: Organize repo root into classified folders with docs.
version: 1.0.0
category: devops
---

# Hermes Repository Organization

Organize a Hermes-family repository root into classified folders, with the
`AGENTS.md`/`README.md` pair in each, the `.gitignore` rules that match the
written policy, and a verified commit that carries nothing but the intended work.

Covers both a single misplaced script and a root that has accumulated dozens of
artifacts across several classes at once.

## When to Use

Use this skill when the repository root has accumulated files that do not belong
there, when a directory needs its `AGENTS.md`/`README.md` pair, or when a move
must preserve history. Two shapes are covered:

- **Single-file** — one misplaced script; see "Single-file move" below.
- **Bulk triage** — dozens of artifacts across several classes at once; see
  "Bulk root-surface triage" at the end of this skill.

Also use it when **scratch lives outside the repository** (an operator's Desktop,
a downloads folder) and needs an inbox inside it, and whenever a tidy pass is
about to stage an untracked tree that may contain large binaries. A tidy pass is
a **recurring** job, not a one-time cleanup — each round has new drift sources,
so scan by size and from outside the repo, not only by count at the root.

## Never Move

Before classifying anything, confirm the file is not one of these. Packaging and
upstream parity depend on the root surface:

| Kind | Examples |
|------|----------|
| Entry / packaging | `run_agent.py`, `cli.py`, `model_tools.py`, `hermes_*.py`, `toolsets.py`, `pyproject.toml`, `setup.py`, lockfiles |
| Docs / ledgers | `README*`, `AGENTS.md`, `SOUL.md`, `FEATURES.yaml`, `CARRY.yaml`, `DOWNSTREAM_POLICY.md` |
| Config | `.env.example`, `.gitignore`, `Dockerfile`, `docker-compose*.yml` |

If a file matches the project's own root-layout policy, that policy wins over
this skill's examples. Read it first.

## Single-file move

### 1. Identify the misplaced file

```bash
ls *.py                              # root scripts, if any
ls *_simulation.py *_tool.py 2>/dev/null || true
```

### 2. Determine the destination by content, not filename

Read the script. Route by what it does:

| Signal | Destination |
|--------|-------------|
| Domain-library work (bpy/bmesh, render, mesh, material) | `scripts/<domain>/` |
| Repo maintenance, cross-repo sync, dependency handling | `scripts/maintenance/` |
| Platform-specific API calls (X, Discord, LINE…) | `scripts/platforms/<platform>/` |
| Scheduled/cron job emitting safe JSON summaries | `cron/scripts/` |
| Shared helpers used by several scripts | `scripts/utils/` |
| One-off inspection with no reusable API | `doc/scripts/<class>/` — see bulk triage |

The last row matters: **not every script belongs in `scripts/`.** A throwaway
state-DB inspector is scratch, not a maintained utility. Putting it in
`scripts/` implies someone will maintain it.

### 3. Move preserving history

```bash
git mv old_path.py new_directory/new_path.py
git log --follow --stat -- new_directory/old_path.py   # verify history survived
```

Untracked scratch moves with plain `mv` — there is no history to preserve, and
`git mv` on an untracked path errors.

### 4. Create the documentation pair

Every functional directory needs both files. `AGENTS.md` is for agents (purpose,
how to use it, constraints); `README.md` is for humans (setup, examples,
expected output, troubleshooting). Write them **before or alongside** the move,
not as an afterthought.

### 5. Verify documentation completeness

Check every non-empty directory has both files:

```bash
find scripts/ -type d -not -path '*/\.*' | while read dir; do
  if [ -d "$dir" ] && [ "$(ls -A "$dir")" ]; then
    [ ! -f "$dir/AGENTS.md" ] && echo "Missing AGENTS.md: $dir"
    [ ! -f "$dir/README.md" ] && echo "Missing README.md: $dir"
  fi
done
```

### 6. Commit with explicit paths and a real message

```bash
git add scripts/<class>/AGENTS.md scripts/<class>/README.md \
       scripts/<class>/*.py

git diff --cached --name-only     # confirm the intent before committing

git commit -m "refactor: move [name] to <destination>

- Moved [name] from <origin> to <destination>
- Added AGENTS.md and README.md
- History preserved via git mv"
```

Never `git add -A` on a repo that carries pre-existing unstaged work: it sweeps
unrelated edits into your commit. Stage explicit paths.

## Best Practices

1. **Preserve history**: `git mv` for tracked files, plain `mv` for untracked.
2. **Follow the project's own policy first**: if `AGENTS.md` defines a root-layout
   rule, that governs; these are defaults.
3. **Document first**: write `AGENTS.md`/`README.md` before or alongside the move.
4. **Classify honestly**: scratch is scratch. Do not promote a throwaway
   inspection script into `scripts/` by moving it there.
5. **Validate placement**: re-check `parents[N]` path bootstraps after a depth change.
6. **Keep atomic**: one coherent change per commit, explicit paths only.

### Directory Structure Guidelines

- Keep the repository root to core modules and essential configuration; everything
  else belongs in a classified folder with its own `AGENTS.md` + `README.md`.
- Group related functionality under `scripts/` with clear subdirectories.
- Keep `doc/` for operator scratch and generated data — see bulk triage below.
- Maintain parallel structure between `scripts/` and `~/.hermes/scripts/` for
  user-specific scripts.
- Ensure every functional directory has both `AGENTS.md` and `README.md`.

## Troubleshooting

### Scripts Not Working After Move

1. Check for hardcoded paths referencing the old location.
2. **Re-derive `parents[N]`.** A file moved one level deeper keeps its old index
   and silently resolves to the wrong directory. See bulk-triage section 9.
3. Verify relative paths still resolve; check dependencies are still reachable.
4. Update import paths if the script imports from other moved files.
5. If a near-duplicate already exists at the correct depth, decide which is
   canonical before either is used — duplicated entry modules diverge.

### Missing Documentation Templates

Look at existing examples in comparable directories, and check the repository's
root-layout policy section. `CONTRIBUTING.md` states documentation standards.

## References

- `fork/local-workspace/AGENTS.md` — fork-specific navigation and policy
- `fork/local-workspace/README.md` — local-workspace conventions
- `CONTRIBUTING.md` — general contribution guidelines
- `references/2026-10-04-root-surface-doc-classification.md` — worked bulk-triage
  session: the `doc/` layout, the `.gitignore` block that passed its 14-assertion
  matrix, the `git add --force` self-inflicted mistake and its recovery, and the
  pnpm security-pin exclusion.
- `references/2026-10-04-desktop-inbox-and-weight-blob-guard.md` — second tidy
  session: the 988 MB untracked `model.safetensors` guard, the
  `.gitignore` last-match-wins ordering bug and its `check-ignore -v` diagnosis,
  the Desktop inbox + divergence ledger, and the ignore-matrix test that was
  itself wrong.

## Example Workflow

A misplaced Blender rendering script:

```bash
# 1. Identify it
ls *_render*.py                       # -> render_no_outputfile.py

# 2. Confirm destination by reading the file (bpy/bmesh, render, mesh)
#    -> scripts/blender/

# 3. Move preserving history
git mv render_no_outputfile.py scripts/blender/render_no_outputfile.py

# 4. Check documentation
ls scripts/blender/AGENTS.md 2>/dev/null || echo "Need to create AGENTS.md"
ls scripts/blender/README.md 2>/dev/null || echo "Need to create README.md"

# 5. Write the two files

# 6. Validate
python scripts/blender/render_no_outputfile.py --help

# 7. Stage explicitly and commit
git add scripts/blender/
git diff --cached --name-only
git commit -m "refactor: move render_no_outputfile.py to scripts/blender/
- Moved from root to scripts/blender/
- Added AGENTS.md and README.md
- History preserved via git mv"
```

### Verifying repository state after changes

```bash
git status                                    # correct branch?
git status --untracked-files=no               # what is actually modified?
git diff --cached                             # staged intent
git commit -m "..."
git push origin <branch>
git log --oneline origin/<branch>..HEAD       # must be empty after push
git rev-parse HEAD; git rev-parse origin/<branch>   # must match
```

Always close the loop on the remote SHA. A successful `git push` exit code is
not proof the intended commits landed — and a tidy pass must also confirm it did
not absorb unrelated work.

## Related Skills

- `hermes-agent`: core structure and extension patterns
- `cron-runtime-reliability`: when a cron job, not a human, writes into the repo
- `git-delivery-verification`: scoped-commit and push-SHA verification

---

## Bulk root-surface triage (verified 2026-10-04)

The single-request case above ("move one misplaced script") is the easy half.
The hard half is a root that has accumulated **dozens** of untracked artifacts
across several classes at once. Do not improvise a layout — map first.

### 1. Inventory before touching

Classify by *what the file is*, not by what it is called:

```text
git status --porcelain --untracked-files=all    # full untracked list
git ls-files --error-unmatch <name>             # per-file: tracked or not
```

A root inventory of ~226 entries typically splits into: entry/packaging modules
(never move), product ledgers (never move), and then the scratch classes —
ad-hoc scripts, bulk JSON/JSONL datasets, log/TXT captures, generated reports,
and archives.

**Decide tracked-vs-untracked per class before moving.** Untracked files move
with plain `mv` and carry no history. Tracked files need `git mv`. Mixing them
up in one batch either loses history or invents it.

### 2. Scratch that is hiding in a source tree

Root is not the only place scratch accumulates. Check for files in `tools/`
(etc.) that never called `registry.register`:

```text
grep -L "registry.register" tools/*.py
```

Scratch sitting in `tools/` is worse than scratch at the root: it reads as
product code, so a future agent may try to import or wire it. Those files move
out. Document the **promotion path** in their new README — what a real
capability would need (registration, a test) — so the move is not mistaken for
a demotion.

### 3. The `doc/` layout that satisfies "every class folder gets AGENTS.md + README.md"

One folder per class, each carrying its own pair of policy files:

```text
doc/
  README.md                    <- the map
  AGENTS.md                    <- root rules
  scripts/<class>/             <- e.g. db-inspect, osint, jma, sync, semantic-scan
  json/    logs/    reports/   <- bulk data, captured output, generated docs
  archive/                     <- the ONE exception: contents committed
```

`.gitignore` gets a single `doc/` block that ignores contents at every depth
while force-including `README.md`, `AGENTS.md` and the directories, so a fresh
clone gets a self-describing empty tree:

```text
!/doc/
/doc/*
!/doc/README.md
!/doc/AGENTS.md
!/doc/*/
/doc/*/*
!/doc/*/README.md
!/doc/*/AGENTS.md
```

**The generic `logs/` rule swallows `doc/logs/` wholesale.** Re-include the
directory before narrowing it again — exactly as `output/logs/` already does.
Without that, `doc/logs/README.md` silently disappears.

### 4. Verify the ignore design with a real matrix

Never trust the block by reading it. Assert the intent:

```text
git check-ignore -q doc/README.md               # expect: NOT ignored
git check-ignore -q doc/logs/README.md          # expect: NOT ignored
git check-ignore -q doc/logs/q_lines.txt        # expect: ignored
git check-ignore -q doc/json/<big>.json         # expect: ignored
```

Run the full matrix (every policy file NOT ignored, every data file ignored)
before committing. One `FAIL` in the matrix means the policy table you just
wrote into `AGENTS.md` is a lie.

### 5. Never defeat your own .gitignore with `--force`

**`git add --force <dir>` silently defeats the entire ignore design.** It stages
everything beneath, including multi-MB datasets the policy just declared
untracked, and the commit looks normal until you read the staged list.

Stage policy files by explicit enumeration instead:

```text
git add doc/README.md
# then walk for the README.md / AGENTS.md pair at each depth and add those paths
git diff --cached --name-only -- doc      # assert: only *.md (+ archive contents)
```

If you do hit it, `git reset -- <dir>` recovers cleanly (nothing was committed
yet) — then re-stage explicitly. The staged-file assertion is what catches it,
not the exit code.

### 6. Keep the policy, the .gitignore, and the docs mutually consistent

A tracked-exception folder (`doc/archive/`) needs an explicit re-include, or the
general depth rules re-ignore it and the written policy becomes false:

```text
!/doc/archive/
!/doc/archive/*
```

Then **re-run the matrix** — the exception is exactly where the block is most
likely wrong. When the policy and the mechanism disagree, the mechanism is the
bug.

### 7. Non-obvious exclusions: leave other people's deletions alone

A tidy pass finds unstaged deletions it did not make. Those belong to the
operator. In the 2026-10-04 run, `pnpm-lock.yaml` and `pnpm-workspace.yaml`
were already deleted in the worktree; `pnpm-workspace.yaml` carried a
`tar: 7.5.22` Dependabot security override, so committing the deletion would
have silently dropped a security pin. They were left unstaged, named in the
commit body as *deliberately not staged*, and reported for a decision.

Before staging a batch, check what the diff already contains:

```text
git diff --stat                     # look for deletions you did not make
git show --name-only --format= HEAD # confirm the commit carries no such path
```

Rule: **commit only what you changed; surface what you found.** A tidy pass that
silently absorbs an unrelated deletion is worse than an untidy root.

Beware substring-count false alarms: grepping a commit body for `pnpm` also
matches the prose explaining *why* pnpm was excluded. Verify with
`git show --name-only` (file names), never by counting occurrences in a message.

### 8. Windows root-surface hazards

- **A file named `nul`** (0 bytes) is created by a `> nul` redirect run under a
  POSIX shell. It is a reserved device: `os.unlink` / `Path.unlink` fail with
  `PermissionError: [WinError 5]`. It is usually already git-ignored, so it
  cannot reach worktree status — document it and leave it rather than fighting
  the API.
- **Literal-path directories**: a shell that expands an absolute user path into
  a relative name can create a stray directory (e.g. `CUsers...`) at the root.
  Confirm it is empty, then remove it.
- **Reserved-name listing is unreliable** — `Path.glob("**/x")` and `rglob` can
  raise `FileNotFoundError` on long paths under `output/` (`node_modules`
  trees). Scope walks to the directory you actually care about.

### 9. Path-depth traps in relocated scripts

A file moved between directory depths can silently break a relative path
calculation. `Path(__file__).resolve().parents[N]` must be re-derived for the new
depth — a copy that sat at the root with `parents[2]` resolves two levels too
high, to the user's home or `Documents`, not the repo. It can still *appear* to
work (sys.path picks up an installed copy), which is why it survives review.

When relocating a script, read its `parents[N]` / `sys.path` bootstrap lines and
recompute. If a near-duplicate already exists at the correct depth, say so and
leave the fix to a scoped change rather than silently rewriting a tracked
entry module mid-tidy.

### 10. Scan for untracked large blobs BEFORE staging anything

A tidy pass must inventory untracked files **by size**, not just by count.
Model/experiment trees are the usual offenders:

```text
git status --porcelain --untracked-files=all     # full untracked list
# then stat each untracked path; anything over ~1 MB needs a decision
```

A single `base_checkpoint/model.safetensors` was found at **988 MB** with **no
gitignore rule covering it**, alongside four 4.3 MB adapters — one `git add`
away from ~1 GB written permanently into history. Presence in `git status` is
not a size warning; nothing flags it.

Add the guard *before* staging, then re-scan to prove it worked:

```text
/rsi/experiments/**/base_checkpoint/
/rsi/experiments/**/runs/**/adapter/
**/*.safetensors
**/*.gguf
**/*.bin
```

Keep evidence and provenance tracked — manifests, datasets, protocols, receipts,
review documents. Exclude only the weights. The claim "the experiment is
reproducible" lives in the JSON manifests, never in the weights.

Re-scan after the rule lands. 8 untracked files >1 MB (1,010 MB) -> 0 is the
proof; the rule is not proof until the scan says so.

### 11. `.gitignore` rule ORDER decides the winner — last match wins

A new ignore block placed **before** a broad one silently loses. Git applies the
**last** matching pattern, not the first and not the most specific.

Observed: the `doc/desktop-inbox/` block was inserted at line 290, while the
generic `/doc/*/*` rule sat at line 349. The generic rule won and swallowed even
the policy `.md` files the block was meant to re-include.

Diagnose by asking git which rule matched:

```text
git check-ignore -v --no-index doc/desktop-inbox/DIVERGENCE.md
# -> .gitignore:349:/doc/*/*   doc/desktop-inbox/DIVERGENCE.md
```

That output names the winning line number directly. Any block that re-includes
something the generic depth rules already match **must be placed after them**,
and the ordering constraint belongs in the SOP you write — otherwise the next
session reintroduces it.

### 12. Inbox pattern for directories outside the repository

Scratch does not only accumulate at the repo root. A working surface — the
operator's Desktop — accumulates scripts that then **drift with no detection**.
Three divergent copies of `memory_sync.py` existed because of it.

Do not move files from an outside directory before checking for live references:

```text
<name> in ~/.hermes/cron/jobs.json        # cron jobs
<name> in schtasks /query /fo csv /v       # scheduled tasks
git grep -l <name>                        # repo references
```

With no live references found, **move** (not copy) into an inbox folder
(`doc/desktop-inbox/{scripts,data}/`) so the Desktop stops being a silent drift
source. With a live reference, **copy and leave in place**.

Maintain a **divergence ledger** (`doc/desktop-inbox/DIVERGENCE.md`) listing each
inbox file that already has a repo counterpart, with sha256 for both sides and an
explicit verdict:

| Inbox file | sha256[:12] | Repo counterpart | sha256[:12] | Verdict |
|---|---|---|---|---|
| `memory_sync.py` | `27516810310d` | `sync_memory.py` | `9826d31ca171` | Diverge; a third copy exists |

**Never merge blind.** Never assume "the newer location is newer". Three copies
of one file is the failure the policy exists to stop, so resolving them is an
explicit decision for the operator — not an overwrite performed mid-tidy.

### 13. Assert ignore intent per file, not per extension

The verification matrix must be **per file**, because `.md` alone does not mean
"policy file". `doc/reports/some_report.md` is generated payload and is ignored;
`doc/logs/README.md` is policy and is not. A matrix that asserts on suffix alone
reports a false failure and, worse, invites "fixing" the .gitignore to match the
wrong expectation.

Classify by **exact filename in a policy set**, then check the whole tree:

```text
POLICY = {"README.md", "AGENTS.md"}
for each file under doc/:
    expected_ignored = False if name in POLICY or under doc/archive/ else True
    assert git check-ignore == expected_ignored
```

When the matrix disagrees with your expectation, suspect the expectation before
the policy. Report the mismatch; do not edit the mechanism to match a guess.

Also check whether a policy folder is excluded *locally* rather than by
`.gitignore` — `_docs/` was excluded via `.git/info/exclude` (per-clone, not
shared) while 150 `_docs` files were already tracked. Such files need
`git add -f` and will stage fine; a missing entry there is not a failure.

### 14. Verify with real tests, then report honestly

Tidy passes usually touch real code alongside the moves. Run the affected
suites before committing and state the results:

- the moved/new module's own tests,
- any modified tracked file's tests,
- the ignore matrix (section 4),
- `git status --porcelain` showing only intended entries.

Record the outcome in a dated `_docs/` audit file per project convention. If a
pre-existing defect is found but deliberately left unfixed (path-depth trap,
unrelated deletion), **say so in the commit body and in the report** — a tidy
pass that hides a known bug is a worse outcome than a slightly untidy tree.

### 15. Distinguish a live fix from future-proofing in what you report

When a change is verified by a test, check **whether the test actually exercises
the changed behaviour** before describing the change as a bug fix. Observed:
a shim re-exporting only public names raised `AttributeError` against
`monkeypatch.setattr("sync_memory._export_obsidian", ...)` — but the test calls
`run_sync(..., export_obsidian=False)` and `run_sync` guards the call with
`if export_obsidian:`, so the suite would have passed either way. The failure was
real; the *test coverage* was not.

Report it as what it is:

- **Live fix** — the test fails without the change. Say so plainly.
- **Future-proofing** — the latent failure would surface on the next flag flip,
  but nothing exercises it today. Say that instead.

This is cheap to check (read whether the guarded branch is reachable from the
test) and it is exactly the distinction a reviewer cannot easily recover later.
Overclaiming a fix is worse than noting a latent risk, because it removes the
motivation to ever close the gap.

### 16. Re-verify an exclusion before carrying it forward

A deletion you deliberately left unstaged in one session is **not settled** — the
next tidy pass may find it restored, or still deleted, and must re-check rather
than inherit the earlier conclusion. Observed: `pnpm-lock.yaml` and
`pnpm-workspace.yaml` were unstaged deletions on 2026-10-04 with a Dependabot
`tar: 7.5.22` override at risk; by the following session both were restored and
the worktree was already clean.

Re-verifying found the exclusion had dissolved, and also surfaced that
`package.json` carries `tar: 7.5.22` in **both** its `pnpm.overrides` and its npm
`overrides` block while every workflow in `.github/workflows/` uses `npm` — so
the security pin survived regardless of package manager. Carry forward the
*question*, not the earlier answer:

```text
git status --porcelain -- <path>            # still deleted? restored? committed?
git cat-file -e HEAD:<path>                 # present at HEAD?
jq '.overrides, .pnpm.overrides' package.json
grep -rl "pnpm" .github/workflows/          # which PM does CI actually use?
```

When the question dissolves, say so and change nothing. Reporting "no action
needed, here is the evidence" is a real outcome; repeating a stale exclusion is
noise that hides a live risk.