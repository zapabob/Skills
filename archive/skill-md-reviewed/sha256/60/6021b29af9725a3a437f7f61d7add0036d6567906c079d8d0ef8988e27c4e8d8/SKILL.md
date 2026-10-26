---
name: daily-dev-summary-obsidian
description: "Use when writing daily multi-repo dev summary diary."
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [diary, development, obsidian, cron, git, github]
    related_skills: [memory-maintenance, obsidian-memory-wiki-routing, obsidian-external-memory-journaling]
---

# Daily Dev Summary → Obsidian Diary

Cron / 手動の「今日の開発サマリー」「daily development summary」用クラススキル。
Ebbinghaus sleep は不要。コミット/PR/Issue を集めてサニタイズした日記を書く。

詳細レシピ: [`references/collection-and-diary.md`](references/collection-and-diary.md)

## Paths

| Role | Path |
|------|------|
| Diary content | `%USERPROFILE%/Documents/ObsidianVault/Hermes-Memory-Wiki/diary/YYYY-MM-DD.md` |
| Git root | `%USERPROFILE%/Documents/ObsidianVault` (nested wiki often has **no** `.git`) |
| Hermes fork | `%USERPROFILE%/Documents/New project/hermes-agent` |

## Procedure

1. Resolve local calendar day (`date`).
2. Collect local commits with **short per-repo** commands:
   ```bash
   cd "%USERPROFILE%/Documents/New project/hermes-agent" \
     && git log --since="YYYY-MM-DD 00:00" --until="YYYY-MM-DD 23:59:59" \
        --pretty=format:"%h|%ci|%an|%s" --all
   ```
   Priority repos: hermes-agent, akari-video, LINE bridges, hypura, irodori-tts-server.
3. Collect GitHub in parallel: user events for the day, `gh pr list` / `gh search prs --author=@me`.
4. Summarize by repo (tables), OPEN/MERGED PRs, issues (or "disabled").
5. `write_file` diary reusing prior day frontmatter/headings when present.
6. Verify file exists. Check parent vault:
   ```bash
   cd "%USERPROFILE%/Documents/ObsidianVault" \
     && git status --short -- Hermes-Memory-Wiki/diary/
   ```
7. Cron: **no auto commit/push**. Final response: concise JP + diary path. `[SILENT]` only if nothing new **and** diary already exists.

## Pitfalls

- Nested `Hermes-Memory-Wiki` is often not a git root — never `git -C` it alone.
- Windows cron: avoid giant bash arrays / deep multi-root `find` loops; split calls.
- Prefer `cd repo && git` over `git -C "/c/Users/..."`.
- hermes-agent Issues may be disabled — not a collection failure.
- Bot `npm run fix` PRs are CI noise; list briefly.
- Huge upstream merges: theme + stats only, no full file dumps.
- No emails, tokens, raw session text, or memory bodies in the diary.
- `obsidian-external-memory-journaling` holds overlapping diary rules but is **user-owned**; do not background-patch it — recommend `hermes curator adopt obsidian-external-memory-journaling` if that skill should absorb this flow.

## Overlap note

Related umbrellas: `memory-maintenance` (has older daily-summary section), `obsidian-memory-wiki-routing` (repo map), user-owned `obsidian-external-memory-journaling`. This skill is the durable cron-safe collector until those are adopted/merged.
