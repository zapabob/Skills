---
name: dev-daily-digest
description: "Daily dev digest: git, PRs, issues, cron, Obsidian diary."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
category: devops
metadata:
  hermes:
    tags: [git, github, cron, obsidian, daily-summary]
    category: devops
---

# Development Daily Digest

Compile a concise, sanitized development summary from multiple repositories, GitHub PRs/issues, and Hermes cron job status, then append it to the Obsidian daily diary.

## Trigger

- User requests "daily development summary" or similar.
- Cron job that needs a daily dev activity report.
- End-of-day recap across repos and automation.

## Required inputs

- Date in `YYYY-MM-DD` format (use `date +"%Y-%m-%d"`).
- Repo list: at least the Hermes fork, plus any active related repos (e.g. akari-video, line-bot-sdk-go, linejs, linets-bot).
- GitHub CLI (`gh`) authenticated for the primary repo.
- Hermes CLI (`hermes cron list`) for cron status.
- Obsidian vault diary path. Default probe: `~/Documents/hermes-memory-vault/diary/`. If missing, search `~/Documents` for a directory matching `*memory*vault*` or `*obsidian*` and confirm the diary subdirectory.

## Execution sequence

1. **Date anchor**: compute today and tomorrow boundaries for `git log --since/--until`.
2. **Git logs**: for each repo, run `git log --oneline --since="<today> 00:00:00" --until="<tomorrow> 00:00:00" --all`. On Windows, quote paths with backslashes or use POSIX `/c/Users/...` form. If a repo has no commits, record "No commits today".
3. **GitHub PRs/issues**: from the primary repo only, collect:
   - `gh pr list --state=open --json number,title,author,createdAt,updatedAt --limit <N>`
   - `gh issue list --state=open --json number,title,author,createdAt --limit <N>`
4. **Cron failures**: parse `hermes cron list` for jobs whose `Last run` shows `error`. Record job name, schedule, and the first line of the error. Do not retry or fix during this workflow.
5. **Obsidian append**: create the diary directory if missing. Append a new section to `<date>.md` with the digest. Keep it concise and sanitized.

## Output format

Use the following structure in the daily note:

```markdown
# YYYY-MM-DD 開発サマリー

## <repo-name>
### 主要コミット
- <category>: <description> (<refs if notable>)

### PR (N件新規)
- #<num> <title>

### Issue (N件新規)
- #<num> <title>

### Cron 失敗 (要対応)
- <job name> (<time>): <error headline> → <remediation hint>

## <other-repo>
- <bullets>

## 他
- 件名情報はサニタイズ済み
```

Rules:
- Top-level repo sections in order: hermes-agent first, then others alphabetically.
- Keep commit descriptions to one line, grouped by area (gateway, agent, secrets, discord, tui, etc.).
- Limit PR/Issue lists to the first 10 items each.
- Cron failures: list only jobs with errors; include time, short error, and a one-line remediation hint.
- Sanitize any user-specific paths, tokens, or internal IDs before writing.
- Write in Japanese unless the user asks otherwise.

## Verification

- Confirm the diary file exists after writing and read it back to verify content.
- Report the absolute path of the appended note in the final response.

## Pitfalls

- **Windows git paths**: `git log` under `C:\...` needs escaped backslashes or POSIX paths; otherwise the shell passes a truncated path.
- **gh scope**: `gh pr/issue list` without `--repo` uses the repo of the current directory. If the cwd is not the target repo, cd first or pass `--repo OWNER/REPO`.
- **Cron error parsing**: `hermes cron list` includes multi-line stderr in the error block. Extract only the first meaningful line to keep the digest concise.
- **Obsidian path**: the vault is often under `~/Documents/hermes-memory-vault/`, not `~/Documents/obsidian/`. Probe both before failing.
- **Sanitization**: never write raw tokens, session IDs, or internal hostnames into the diary; replace with placeholders or omit.
