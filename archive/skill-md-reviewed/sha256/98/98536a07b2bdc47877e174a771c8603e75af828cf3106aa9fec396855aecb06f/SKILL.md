---
name: hermes-cron-v018-to-v019-migration
description: Migrate 0.18.2-era cron jobs to 0.19.0 interfaces and Hermes lifecycle events.
version: 0.1.0
author: Hermes
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [Cron, Migration, v0.19.0, Hermes, v0.18.2]
---

# Hermes Cron v0.18.2 → v0.19.0 Migration

Update legacy cron jobs (scripts, prompts, skill invocations) to the 0.19.0 Hermes
cron lifecycle: new job schema fields (`enabled_toolsets`, `model`, `provider`,
`workdir`), updated script entry points, and the agent-loop event contract
(`on_start`, `on_tool`, `on_complete`, `on_error`).

## When to Use

- Existing cron jobs that reference `v0.18.2` or older Hermes versions in their
  prompts
- Jobs using `no_agent: true` scripts that call deprecated Hermes CLI flags
- Jobs that need the new `enabled_toolsets` allowlist for token efficiency
- Migration from `xurl`/`lm-twitterer` direct calls to the `hermes-x-posting-workflows` skill

## Prerequisites

- Hermes 0.19.0+ installed and on PATH
- Cron jobs stored in `~/.hermes/cron/jobs.json` (per-profile)
- Access to `cronjob` tool or `hermes cron` CLI

## Key Changes in 0.19.0

| Area | 0.18.2 | 0.19.0 |
|------|--------|--------|
| Job schema | `script`, `prompt`, `skills` | + `enabled_toolsets`, `model`, `provider`, `workdir`, `attach_to_session` |
| Agent loop | Implicit events | Explicit `on_start`/`on_complete` hooks |
| Tool allowlist | All tools by default | `enabled_toolsets` (default: all) |
| Model pinning | Global config only | Per-job `model` + `provider` override |
| X posting | `xurl` CLI or raw `lm_twitterer_*` tools | `hermes-x-posting-workflows` skill + `lm-twitterer-operations` |
| VRChat daily | Custom `daily_vrchat_post.py` | `vrchat-hakua-daily-post` skill (HyperFrames + Irodori TTS) |

## Migration Steps

### 1. Inventory jobs

```bash
cronjob action=list
# or
hermes cron list
```

Identify jobs with:
- `prompt` containing "v0.18" or "v2026.7.7"
- `script` pointing to `daily_vrchat_post.py`, `lm-twitterer-post.py`, etc.
- `skills` missing `hermes-x-posting-workflows` for X posting jobs

### 2. Update prompt text (in-place)

For each job, replace version references:

```python
from cron.jobs import get_job, update_job

job = get_job("<job-id>")
new_prompt = job["prompt"].replace("v0.18.2", "v0.19.0") \
                          .replace("v2026.7.7.2", "v2026.7.21.0") \
                          .replace("2026年7月7日", "2026年7月21日")
update_job("<job-id>", {"prompt": new_prompt})
```

### 3. Add `enabled_toolsets` for token efficiency

```python
update_job("<job-id>", {
    "enabled_toolsets": ["web", "terminal", "skills", "tts"]
})
```

### 4. Pin model/provider if job needs specific routing

```python
update_job("<job-id>", {
    "model": "anthropic/claude-sonnet-4",
    "provider": "openrouter"
})
```

### 5. Migrate X posting jobs

- Remove `script: "lm-twitterer-post.py"` if present
- Add skills: `["hermes-x-posting-workflows", "lm-twitterer-operations"]`
- Rewrite prompt to use the skill's two-pass workflow (draft → post)

### 6. Migrate VRChat daily post jobs

- Replace `script: "daily_vrchat_post.py"` with `skill: "vrchat-hakua-daily-post"`
- Ensure `enabled_toolsets` includes `tts` and `terminal`
- Verify Irodori TTS endpoint (`http://127.0.0.1:8088`) and VOICEVOX (`http://127.0.0.1:50021`) are reachable

### 7. Test run

```bash
cronjob action=run job_id=<job-id>
# or
hermes cron run <job-id>
```

Check output in `~/.hermes/cron/output/<job-id>/<timestamp>.md`

### 8. Verify delivery

- Telegram: message arrives in target chat
- X: tweet appears on timeline (check `lm-twitterer-operations` logs)
- Local: markdown file written to cron output dir

## Common Patterns

### Viral tweet job (6-hourly)

```json
{
  "job_id": "f53c796a3dfd",
  "prompt": "Hermes Agent v0.19.0 の新機能を紹介し、フォロワーに役立つ情報を日本語でツイートしてください。最新の変更点や改善点を簡潔にまとめて、ハッシュタグ #HermesAgent を含めてください。",
  "schedule": "0 */6 * * *",
  "skills": ["hermes-x-posting-workflows", "lm-twitterer-operations"],
  "enabled_toolsets": ["skills", "terminal"],
  "deliver": "local"
}
```

### VRChat daily post (7 AM)

```json
{
  "job_id": "07f62cef0201",
  "skill": "vrchat-hakua-daily-post",
  "schedule": "0 7 * * *",
  "enabled_toolsets": ["tts", "terminal", "skills"],
  "workdir": "%USERPROFILE%/Documents/New project/hermes-agent",
  "deliver": "local"
}
```

## Pitfalls

- **Forgetting `enabled_toolsets`**: Jobs inherit all tools, bloating prompt tokens.
- **Script path drift**: `workdir` must be absolute; relative paths break under the scheduler.
- **Skill name typo**: `hermes-x-posting-workflows` (plural) vs `hermes-x-posting-workflow` (singular, wrong).
- **TTS endpoint mismatch**: Irodori default port 8088; VOICEVOX 50021. Cron runs headless — no auto-start.
- **Duplicate reply jobs**: `b5eb666384a8` and `046708440c99` both do mention replies; consolidate to one.

## Verification Checklist

- [ ] All version strings updated to v0.19.0 / v2026.7.21.0
- [ ] `enabled_toolsets` set on every migrated job
- [ ] X posting jobs use `hermes-x-posting-workflows` skill
- [ ] VRChat jobs use `vrchat-hakua-daily-post` skill
- [ ] Test run produces expected output (Telegram/X/local)
- [ ] No `no_agent: true` scripts calling deprecated Hermes CLI flags
- [ ] Duplicate jobs paused/removed

## Rollback

If a migrated job regresses:

```bash
cronjob action=pause job_id=<job-id>
# Fix prompt/script/skills, then
cronjob action=resume job_id=<job-id>
```

Previous prompt retained in job history for diff.