---
name: hermes-x-posting-workflows
description: "Post to X from Hermes with lm-twitterer, dry-run, and media workflows."
version: 1.0.0
author: zapabob
license: MIT
platforms: [windows, linux, macos]
tags: [x, twitter, social-media, lm-twitterer, hakua]
---

# Hermes X Posting Workflows (Hakua distribution)

Use when posting to X via the `lm-twitterer` plugin from the **hakua** profile.

## When to Use

- Drafting or posting tweets with explicit user confirmation
- VRChat photo + voice MP4 posts (`daily_vrchat_post.py` cron)
- Checking auth: `hermes lm-twitterer auth-check`

## Prerequisites

- [zapabob/hermes-agent](https://github.com/zapabob/hermes-agent) fork with `lm-twitterer` and `irodori-tts`
- `hermes plugins enable lm-twitterer irodori-tts`
- Cookies in profile `.env`: `LM_TWITTERER_AUTH_TOKEN`, `LM_TWITTERER_CT0`
- FFmpeg in PATH for MP4 posts

## Safety

1. Draft first; post only after explicit confirmation.
2. Never include secrets, medical info, or private schedules in public posts.
3. Sign posts transparently (`#hermesagent`).

## Daily VRChat cron

See `references/daily-vrchat-photo-cron-post.md`.

## Commands

```bash
hakua lm-twitterer status
hakua lm-twitterer post "draft text"          # dry-run default
hakua lm-twitterer post "text" --live
py -3 ~/.hermes/profiles/hakua/scripts/daily_vrchat_post.py --skip-post
```
