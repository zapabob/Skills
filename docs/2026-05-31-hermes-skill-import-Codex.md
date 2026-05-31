# 2026-05-31 Hermes Skill Import

## Operator

Codex

## Scope

Import local skill folders from the installed Codex/Cursor locations and the sibling `hermes-agent` checkout into the portable `@zapabob/skills` registry without duplicate slugs. Make the resulting catalog installable into Codex and Cursor.

The repository-local `AGENTS.md`, `AGENT.md`, `SOP/README.md`, and `SOP/ENCODING.md` were missing, so the common policy was read from `C:\Users\butte\Documents\Codex\2026-05-26\agent-md-milspec-llmops-sop-mlops\AGENTS.md`.

## Changes

- Added source roots for `cursor-staging`, `cursor-rules-staging`, `hermes-agent`, `hermes-agent-optional`, `hermes-agent-plugins`, and `hermes-agent-vendor`.
- Added recursive skill discovery so nested folders with `SKILL.md` are imported once per source.
- Cleaned `registry/skills/` during import to remove stale variants before regenerating the catalog.
- Added target preferences so Hermes variants can be installed into Codex, Cursor, ClaudeCode, Antigravity, and Openclaw when no native variant exists.
- Added `--skip-existing` and `--skip-incompatible` for safe bulk installs.
- Regenerated `registry/index.json`, `registry/sources.json`, and `registry/skills/`.

## Verification

- Clean source import counts:
  - Codex: 69
  - Cursor staging: 41
  - Cursor rules staging: 6
  - Hermes built-in: 93
  - Hermes optional: 86
  - Hermes plugin: 1
  - Hermes vendor harness: 8
- Registry:
  - Unified skills: 265
  - Source variants: Codex 69, Cursor staging 41, Cursor rules staging 6, Hermes built-in 93, Hermes optional 86, Hermes plugin 1, Hermes vendor harness 8
- Registry integrity check:
  - duplicate slugs: 0
  - duplicate variant pairs: 0
  - stale `C:\Users\downl` origins: 0
- Codex install replay:
  - installed: 0
  - skipped existing: 259
  - skipped incompatible: 6
- Cursor install replay:
  - installed: 0
  - skipped existing: 259
  - skipped incompatible: 6
- Post-install target scan:
  - Codex duplicate slug groups: 0
  - Cursor duplicate slug groups: 0
- `npm.cmd pack --dry-run`
  - completed successfully

## Notes

The first Codex bulk install exposed one existing-folder edge case: `Obsidian Knowledge Management` already existed with spaces in the folder name. The installer now treats slug-equivalent existing directories as existing, and the normalized duplicate created during the first pass was removed while preserving the original folder.
