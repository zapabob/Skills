---
name: vrchat-cron-management
description: VRChat cron job management and failure patterns.
category: devops
---

# VRChat Cron Management Skill

Use when managing, pausing, stopping, or scheduling VRChat-related cron jobs in Hermes Agent. VRChat cron jobs post daily VRChat photos, tweets, or other content to VRChat and related platforms (X/Twitter, LINE, Telegram), often integrating with FishAudio TTS (Hakua voice), image generation, and social media posting.

## Triggers & When to Use

Use this skill when you need to:
- List all VRChat-related cron jobs
- Pause or stop VRChat cron jobs (e.g., due to TTS token expiration, API errors, or maintenance)
- Debug failing VRChat cron workflows
- Set up new VRChat posting schedules
- Coordinate between VRChat and other platform postings (X, Telegram, Discord)

## Common VRChat Cron Job Types

| Job Name | Description | Typical Failures |
|----------|-------------|------------------|
| `Daily VRChat Photo Post - Hakua Morning` | Posts daily morning VRChat screenshot with Hakua voice | Fish Audio HTTP 401: Invalid Token, TTS generation failures |
| `vrchat_daily_tweet` | Posts VRChat daily tweet | Script timeouts, API rate limits, media duration errors |
| `morning-vrchat-hakua-post` | Morning Hakua post to VRChat | Token expiry, audio generation failures |
| `daily_vrchat_post` | General daily VRChat post | Similar to above |

## How to Pause/Stop VRChat Cron Jobs

### Pause a specific job:
```
hermes cron pause <job_id>
```

### List VRChat-related jobs:
```
hermes cron list | grep -i -E "vrchat|VRChat|daily_vrchat|hakua"
```

### Common job IDs to know:
- `07f62cef0201` - Daily VRChat Photo Post - Hakua Morning
- `80b6cac36fc5` - vrchat_daily_tweet
- `8836c500a031` - morning-vrchat-hakua-post

## Known Failure Modes & Fixes

### Fish Audio Hakua HTTP 401 Invalid Token
Symptom: `Fish Audio HTTP 401: {"status":401,"message":"Invalid Token"}`
Cause: expired PIN/auth token for FishAudio TTS
Fix: Re-authenticate FishAudio bridge or refresh credentials

### Script Timeout (1200s limit)
Symptom: `Script timed out after 1200s`
Cause: Long-running TTS or image generation
Fix: Set `background=true, notify=true` for cron jobs; Kill competing ComfyUI processes on port 8188 before generation; Use BF16 (non-quantized) model path to avoid PyTorch segfaults

### X/Twitter Media Duration Too Long
Symptom: `error code 324 "Duration too long, maximum:2.minutes+20.seconds"`
Cause: MP4 exceeding 140-second limit (actual: 160s)
Fix: Trim videos to ≤140 seconds before posting

### API Rate Limit (HTTP 429)
Symptom: `HTTP 429: Hold up for a bit, you've exceeded the rate limit`
Cause: Too many API calls in short period
Fix: Stagger cron schedules, add delays between calls, respect rate limits

## Best Practices

1. Stagger schedules: Don't run multiple heavy VRChat/Twitter jobs at the same tick
2. Check token validity: Before starting, verify FishAudio/Twitter tokens are valid
3. Trim media: Always ensure X/Twitter videos are ≤140 seconds
4. Kill competing processes: Before starting ComfyUI generation, kill any process on port 8188
5. Use background mode: For bounded tasks, use `background=true, notify=true` so outcomes are delivered
6. Monitor error patterns: If a job fails repeatedly (e.g., "X failures in a row"), pause it and investigate

## Related Skills

- `lm-twitterer-operations` - X/Twitter posting workflows
- `x-posting` - X/Twitter posting class
- `hermes-x-posting-workflows` - Hermes X posting workflows
- `daily_vrchat_post` - VRChat post script
- `vrchat_autonomy` - VRChat autonomous agent management

## Session-Specific Notes

This skill was created after observing multiple VRChat cron job failures in session on 2026-09-10, including:
- Fish Audio Hakua generation failures (HTTP 401 Invalid Token)
- Script timeouts exceeding 1200s limit
- X/Twitter video duration limits (max 140s, actual 160s failed)
- API rate limit errors (HTTP 429)
- Authentication block states requiring re-authentication

For job-specific troubleshooting, refer to the individual job transcripts and error outputs from the session.