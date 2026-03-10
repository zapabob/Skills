# @zapabob/skills

Portable multi-agent skill catalog and installer for Codex, ClaudeCode, Cursor, Antigravity, and Openclaw.

## What It Does

- Collects local skill folders from multiple agent ecosystems into one portable skill registry.
- Delivers the best available variant for each target with target-aware skill delivery.
- Packages your skill set as a reusable catalog/installer that is easy to publish on npm, GitHub, and external store packaging flows.

## Why It Stands Out

- Cross-ecosystem import: Codex, ClaudeCode, Cursor, and shared `.agents` skills can live in one registry.
- Variant-aware install: one skill slug can contain multiple target-specific implementations.
- Portable skill registry: the generated `registry/` can be versioned, published, and repackaged for external catalogs.
- Store-ready positioning: the project is easy to describe as a multi-agent skill catalog instead of a single one-off skill.

## Quick Start

```bash
npx @zapabob/skills list
npx @zapabob/skills install architect --target codex
npx @zapabob/skills install architect --target cursor
npx @zapabob/skills install --all --target claudecode
```

## Commands

```bash
npx @zapabob/skills discover
npx @zapabob/skills import-local
npx @zapabob/skills list
npx @zapabob/skills install <skill...> --target <target>
npx @zapabob/skills install --all --target <target>
```

## Install Behavior

`install` copies the best matching variant for the chosen target into that tool's default skills directory.

| Target | Default destination |
| --- | --- |
| `codex` | `~/.codex/skills` |
| `claudecode` | `~/.claude/skills` |
| `cursor` | `~/.cursor/skills` |
| `cursor-rules` | `~/.cursor/skills-cursor` |
| `antigravity` | `~/.antigravity/skills` |
| `openclaw` | `~/.openclaw/skills` |

Notes:

- `--dest <path>` overrides the default install root.
- `--force` replaces an existing destination directory for that skill.
- Antigravity and Openclaw are supported install targets even if no local source skills were discovered on this machine yet.

## Typical Workflow

For users:

```bash
npx @zapabob/skills list
npx @zapabob/skills install find-skills --target claudecode
```

For catalog maintainers:

```bash
npm run import-local
npx @zapabob/skills list
npm pack
```

## Registry Model

- `registry/index.json` stores the unified catalog metadata.
- `registry/skills/<slug>/variants/<source>/` stores each source-specific skill variant.
- The installer selects the first compatible variant for the requested target based on built-in target preferences.

This makes the package suitable for external catalogs, store packaging, and future commercial bundling without changing the public CLI.

## Development Notes

- Run `npm run import-local` to refresh the registry from local skill sources.
- Add a new source by extending `SOURCE_ROOTS` in `lib/constants.js`.
- Add a new install target by extending `TARGETS` in `lib/constants.js`.
- Run `npm pack` before publish to verify the tarball contents.

## Publishing

```bash
npm pack
npm publish --access public
```

The package is structured for public npm distribution first, while remaining portable enough for GitHub releases and Openclaw-style external catalogs.
