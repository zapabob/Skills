---
name: windows-c-drive-safe-cleanup
description: Inventory and reclaim C: space on this Windows PC when the user excludes personal/system/Downloads data or asks to move large Temp GGUF models safely to H:.
argument-hint: "[inventory|cleanup|evacuate-gguf]"
disable-model-invocation: true
user-invocable: false
allowed-tools: Read, Grep, Bash
---

# Windows C: safe cleanup

## When to use

Use for machine-local C: capacity work on this PC when the user wants an inventory, bounded cache cleanup, or safe evacuation of valuable GGUF files from Temp. This is not permission for generic system cleanup, deleting personal folders, stopping unrelated processes, deleting browser profiles, or following junctions.

## Inputs and first checks

1. Confirm the exact requested phase: inventory only, approved cleanup candidates, or GGUF evacuation.
2. Confirm exclusions and preserve them unless the user explicitly changes scope: Downloads, Desktop, Documents, Pictures, Videos, Music, `C:\Windows`, Program Files, ProgramData, Recovery, System Volume Information, `C:\d\models`, Hugging Face cache, Google DriveFS, browser profiles, active `npm-cache`, current worktrees, and Android/rooting data.
3. Measure free space before work. For deep candidate roots, use the bounded non-mutating probe:
   ```powershell
   robocopy <path> NUL /L /S /BYTES /XJ /NFL /NDL /NJH /R:0 /W:0
   ```
4. Inspect attributes/link targets before recursive work. Treat every symlink, junction, and reparse point as protected unless explicitly authorized.
5. Check active process command lines before touching uv or npm caches. Do not terminate the user's Hermes, TTS, browser, or MCP processes.
6. For a Git-worktree candidate, require its exact path to be under the approved root, be an ordinary directory, and have `git status --porcelain --untracked-files=all` exit successfully with no output before calling it clean. A failed Git command is unsafe, not clean.
7. For selected Visual Studio/SDK Temp payloads, confirm the exact directories are ordinary non-reparse directories and no setup, `msiexec`, VSIX installer, or related process is active.

## Procedure

1. Build a current ranked inventory. Classify each root as regenerable cache, old dependency/build tree, current worktree, model data, active runtime state, junction, user work data, or protected root.
2. Present the ranked paths, sizes, risk classes, and the exact proposed allowlist before destructive work. Do not turn an inventory request into deletion.
3. For approved cache cleanup, use an exact absolute-path allowlist. The routine must reject broad roots/protected roots, avoid symlink/reparse traversal, record a dry-run/preflight, then remeasure C: and protected roots after execution. Skip locked files and report them.
4. Prefer `pnpm store prune` to deleting the entire pnpm store when it is an approved candidate. Treat `uv cache clean` timeout as inconclusive: inspect the exact command line and stop only the cleanup process started for this task if it is necessary.
5. For an explicitly authorized Git-worktree deletion, keep a fixed path allowlist; re-check containment and reparse status, delete only approved entries, then use `Test-Path` for each target and protected path. If residual `.idx`, `.pack`, or `.rev` files are read-only, remove that attribute only inside the approved target and retry.
6. For explicitly selected VS/SDK payload directories, use a fixed allowlist under Temp plus post-delete checks. Do not generalize the authorization to `DiagOutputDir`, uv cache, NVIDIA cache, or the rest of Temp.
7. For valuable Temp GGUF models authorized for evacuation:
   1. Copy `%USERPROFILE%\AppData\Local\Temp\*.gguf` to `H:\CDriveEvacuation\gguf-temp-YYYYMMDD` with Robocopy, e.g. `/J /COPY:DAT /DCOPY:T /R:0 /W:0`.
   2. Wait for every destination file, then compare source/destination sizes and SHA-256 for every file.
   3. Delete only the verified source paths with a routine constrained to the exact Temp root, existing explicit file list, and `.gguf` extension.
   4. Verify every source is absent, every H: copy remains, and report the before/after C: free-space values.

## Efficiency plan

- Start with the requested roots and `robocopy /L /S /BYTES /XJ` probes; ignore the expected `ERROR 1`/`ERROR 53` NUL-destination noise and use the final `Dirs`/`Files`/`Bytes` summary; do not recurse across all of AppData after major candidates are known.
- Use one ranked inventory table and one exact allowlist instead of repeated broad scans.
- Cache the preflight sizes, process check, and reparse-point results for the execution and verification phases.
- Stop after reporting approved results, protected-path preservation, locked remnants, and the distinction between logical candidate size and physical free-space gain.

## Pitfalls and fixes

- Symptom: PowerShell recursion or `uv cache clean` runs past a tool timeout. Cause: deep cache trees or a long-running cleanup. Fix: pivot to bounded `robocopy /L` probes; inspect the command line; a timeout is not proof of completion.
- Symptom: a deletion path is a junction, such as `C:\hermes-dtbuild\node_modules`. Cause: it can target the Hermes project. Fix: preserve it; never recursively delete a reparse point.
- Symptom: files remain in Temp or NVIDIA cache. Cause: locks/access denial. Fix: log and skip them unless the user explicitly authorizes stopping the owning process.
- Symptom: direct PowerShell deletion is rejected. Cause: execution safety controls. Fix: keep scope unchanged and use an explicit exact-root, extension-checked routine only after approval and verification.
- Symptom: logical deleted bytes exceed the free-space increase. Cause: NTFS compression, sparse files, or allocation. Fix: report both values separately.

## Verification checklist

- [ ] A current ranked inventory preceded any destructive step.
- [ ] The approved target set was an exact, normalized allowlist.
- [ ] Protected roots and reparse points were excluded and rechecked.
- [ ] Active process dependencies and locked remnants were preserved or explicitly handled.
- [ ] C: free space was measured before and after cleanup.
- [ ] For evacuated GGUF files: destination exists, per-file size and SHA-256 match, source is absent, and H: copy remains.
