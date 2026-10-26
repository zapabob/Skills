---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. On Windows, also check Obsidian Desktop's vault registry before asking the user: `%APPDATA%/obsidian/obsidian.json` (MSYS/Python path: `Path.home()/"AppData/Roaming/obsidian/obsidian.json"`) contains a `vaults` object with per-vault `path` values. Prefer a vault that already contains Hermes/session notes when multiple vaults exist. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

If the intended append anchor appears more than once (for example repeated monthly log sections with identical final bullets), do not use `replace_all=true` just to force the append. Widen the anchor to include a unique heading plus the full final section, then replace that block with itself plus the new section. This preserves older entries and avoids duplicating content in the wrong place.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## Hermes/session-log inventory notes

When exporting Hermes/OpenClaw session-log inventories into Obsidian for this user:

1. Resolve the vault path first (`OBSIDIAN_VAULT_PATH`, then Obsidian Desktop registry on Windows, then the documented fallback). Prefer a vault that already contains `Hermes-Sessions/` or Hermes memory notes when multiple vaults exist.
2. Do **not** dump raw session DB/JSONL content into Git-managed notes. Write a Markdown inventory/summary with counts, sources, month/day breakdowns, recent session previews, and next-action queues.
3. Sanitize previews before writing: redact secret-looking assignments (`token`, `api_key`, `password`, `cookie`, `bearer`, etc.), long opaque tokens, email addresses, and absolute home paths.
4. Verify the written note by reading it back and running a targeted secret-pattern search on the note.
5. Git management is allowed, but stage/commit/push are distinct steps: `git add` may be used for the generated inventory note; do not commit or push without explicit user intent, and always require explicit approval before any remote push.
