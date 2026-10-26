---
name: viral-tweet-scheduler
category: productivity
description: Automates scheduling of viral tweets for Hermes Agent v0.17.0 features, rotating through topics while respecting character limits, emoji usage, hashtag, and signature requirements.
---

# Viral Tweet Scheduler

A class-level skill that automates the generation and posting of viral tweets highlighting new Hermes Agent features, rotating through a predefined set of topics, and adhering to user style constraints (140 Japanese characters, one emoji, #hermesagent hashtag, ending with "はくあ").

## Trigger

- Scheduled via cron job `hermes-viral-tweets-v017` (every 6 hours).
- Can be invoked manually via `hermes cron run viral-tweet-scheduler`.

## Process

1. **Topic Selection** – Randomly select a feature from the rotation list.
2. **Tweet Generation** – Construct a tweet respecting:
   - Max 140 Japanese characters.
   - Include at most one emoji (🚀 or ✨).
   - Append `#hermesagent`.
   - End with `はくあ`.
3. **Posting** – Use `lm_twitterer_post` with `dry_run: false` to publish.
4. **Logging** – Record tweet URL in `~/.hermes/logs/viral-tweets.log`.

## Configuration

- Schedule: `0 */6 * * *` (every 6 hours).
- Provider: `freebuff` (free tier rotation).
- Emoji set: `{🚀, ✨}`.
- Rotation list (v0.17.0 features):
  - デスクトップ大強化
  - バックグラウンドサブエージェント
  - 画像生成が画像編集に対応
  - デスクトップ大強化
  - Raft エージェントネットワーク連携
  - メモリツール大幅アップグレード
  - ダッシュボード：プロフィールビルダー＋セキュアログイン
  - リリース規模感

## Pitfalls

- **Character count**: Overrun can be checked with `wc -m`.
- **Emoji limit**: Ensure only one emoji is used; extra emojis will break formatting.
- **Hashtag & signature**: Must include `#hermesagent` and end with `はくあ`.
- **Provider availability**: If the free tier is exhausted, the job will fail; monitor `last_delivery_error`.

## Supporting Files

- `references/rotation-topics.md` – Detailed list and description of rotation topics.
- `scripts/generate-tweet.sh` – Helper script to randomly select a topic and output a formatted tweet.

## Usage

```bash
# Run the scheduler manually
hermes cron run viral-tweet-scheduler

# Or wait for the automatic schedule
```

## Maintenance

- Update `rotation-topics.md` when new features are added.
- Adjust emoji set or length constraints if user preferences change.
- Review `viral-tweets.log` for any posting issues.