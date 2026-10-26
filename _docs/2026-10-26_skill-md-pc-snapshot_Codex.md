# PC skill and engineering-baseline snapshot

Date: 2026-10-26

## Overview and requirements

The user requested a Git commit and push of every `SKILL.md` discoverable on this PC, including cache, backup, and antivirus sandbox locations, plus the canonical PC-wide `AGENTS.md` and SOP set. The destination is the public `zapabob/Skills` repository. The snapshot is reference material and must not alter the installable skill registry or npm package.

## Applicable instructions and decisions

The PC-wide and Codex-local `AGENTS.md`, required pre-implementation prompt, common engineering SOP, implementation start gate, skill selection SOP, security SOP, and applicable Python and application/network SOPs were consulted. The Git workflow, skill creator, documentation, and MILSPEC Codex skills informed the work. The Codex-local `AGENTS.md` omitted the canonical prompt path; the home-level `AGENTS.md` identified it. An isolated clone was created during discovery before that home-level pointer was found. No original skill, AGENTS, or SOP source was edited.

The source scan used the two mounted filesystem volumes, C: and H:. Content was deduplicated by SHA-256. The public index uses source categories and counts instead of absolute source paths. Known credential patterns, non-example email addresses, local user-home prefixes, trailing whitespace, and extra blank lines at the end of files were removed from public skill copies. Contents with explicit redistribution restrictions, an all-rights-reserved notice, or a private-key marker were withheld while their hashes and counts remained in the index.

## Changed files and behavior

- `archive/skill-md-reviewed/`: content-addressed, non-installable `SKILL.md` snapshot, index, and usage notes.
- `docs/pc-baseline/`: exact copy of canonical `AGENTS.md` and 21 SOP Markdown files, plus provenance notes.
- `.gitattributes`: disables text normalization for the hash-verified archive and canonical copies.
- `README.md`: links to both reference snapshots.
- This implementation log: scope, evidence, and residual risks.

The existing `registry/`, CLI, package metadata, and source skill files were not changed. The npm package uses a `files` allowlist that excludes `archive/` and `docs/`.

## Commands and verification evidence

The scan used `rg --files --hidden --no-ignore -g SKILL.md` on C: and H:. It found 42,950 readable file locations, representing 3,982 distinct source contents. The reviewed archive contains 3,957 public skill copies and 25 withheld records: 16 redistribution-restricted, 8 all-rights-reserved, and 1 private-key marker. The index accounts for every readable location found in the scan.

`node --check` passed for the local audit/build/verification scripts. The final verifier checked each archive path and published SHA-256, record and duplicate counts, source-copy hashes for all 22 canonical files, and zero residual matches for the selected private-key, token, credential assignment, credential URL, personal email, local-home path, and JWT patterns. Git initially normalized some line endings; `.gitattributes` and `git add --renormalize` restored byte-exact staged blobs. The final verifier compared all 3,982 staged archive/baseline blobs with their raw working-file bytes. Its output was: `fileLocations=42950`, `uniqueContents=3982`, `published=3957`, `withheld=25`, `canonicalDocs=22`, `stagedBlobFilesChecked=3982`, and `problems=0`. `git -c core.whitespace=cr-at-eol diff --cached --check` passed after public-copy whitespace cleanup. `npm pack --dry-run --json --ignore-scripts` listed 1,361 npm files and no `archive/` or `docs/pc-baseline/` paths.

## Residual risks and rollback

The `rg` scan reported 157 traversal errors across C: and H: (156 access denials and one path-too-long error), so the result covers readable locations and does not prove that those locations contain no additional `SKILL.md`. Pattern screening cannot prove that every possible secret or personal identifier was found. Some third-party material has no machine-readable license declaration; the archive notes that the package MIT label does not change original rights. The snapshot is deliberately outside the installer registry because antivirus and cache sources are untrusted.

Two earlier local snapshot drafts under `archive/skill-md/` and `archive/skill-md-safe/` were not selected for publication. Automatic approval review rejected both broad and exact-file deletion attempts, so these drafts remain as untracked local files. Only `archive/skill-md-reviewed/` is intended for the commit. To roll back the public change, revert the resulting Git commit and push the revert; do not delete the original PC source files.

## Next action

Review the staged Git path list and diff checks, commit only the reviewed archive and canonical baseline, then push and verify the exact remote SHA.
