# @zapabob/skills

Portable multi-agent skill catalog and installer for Codex, ClaudeCode, Cursor, Antigravity, and Openclaw.

## What It Does

- Collects local skill folders from multiple agent ecosystems into one portable skill registry.
- Delivers the best available variant for each target with target-aware skill delivery.
- Packages your skill set as a reusable catalog/installer that is easy to publish on npm, GitHub, and external store packaging flows.

## Why It Stands Out

- Cross-ecosystem import: Codex, ClaudeCode, Cursor, and shared `.agents` skills can live in one registry.
- Local Hermes import: a sibling `hermes-agent` checkout contributes `skills/`, `optional-skills/`, plugin skills, and vendored harness skills when present.
- Cursor staging import: `.cursor/skills-staging` and `.cursor/rules-staging` are treated as import sources so prepared Cursor skills are not lost.
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
npx @zapabob/skills install --all --target <target> --skip-existing --skip-incompatible
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
- `--skip-existing` preserves an already-installed target skill instead of failing or overwriting.
- `--skip-incompatible` lets bulk installs continue when a skill only has variants for another target.
- Antigravity and Openclaw are supported install targets even if no local source skills were discovered on this machine yet.

## Typical Workflow

For users:

```bash
npx @zapabob/skills list
npx @zapabob/skills install find-skills --target claudecode
npx @zapabob/skills install --all --target cursor --skip-existing --skip-incompatible
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
- Nested source folders are supported: the importer finds any directory under a source root that contains `SKILL.md`, then stores each slug once per source.

This makes the package suitable for external catalogs, store packaging, and future commercial bundling without changing the public CLI.

## Development Notes

- Run `npm run import-local` to refresh the registry from local skill sources.
- Add a new source by extending `SOURCE_ROOTS` in `lib/constants.js`.
- Add a new install target by extending `TARGETS` in `lib/constants.js`.
- Override sibling Hermes locations with `HERMES_AGENT_SKILLS_ROOT`, `HERMES_AGENT_OPTIONAL_SKILLS_ROOT`, `HERMES_AGENT_PLUGINS_ROOT`, or `HERMES_AGENT_VENDOR_SKILLS_ROOT` when the checkout is not next to this repo.
- Run `npm pack` before publish to verify the tarball contents.

## Publishing

```bash
npm pack
npm publish --access public
```

The package is structured for public npm distribution first, while remaining portable enough for GitHub releases and Openclaw-style external catalogs.
