---
name: cron-news-briefing-telegram
description: Cronジョブとして実行される日本語ニュース収集・要約・Telegram配信スキル。はくあ的人格で深掘り論評を付与。
version: "1.0"
author: "Hermes Agent"
license: "MIT"
platforms: ["linux", "macos", "windows"]
metadata:
  hermes:
    tags: ["cron", "news", "telegram", "japanese", "briefing"]
    category: "autonomous-ai-agents"
    related_skills: ["warashibe-arbitrage-cron", "ebbinghaus-cron-runtime"]
    config:
      cron_schedule: "0 6,12,18 * * *"
      max_chars: 300
      persona: "hakua"
      language: "ja"
---

# Cronニュースブリーフィング（Telegram向け）スキル

## When to Use
- 定期実行されるcronジョブとして、最新ニュースを収集・要約しTelegramに配信する場合
- はくあ（ASI_HAKUA）人格での「深掘り論評」を付与した日本語ブリーフが必要な場合
- 200-300文字程度の簡潔な配信が求められる場合

## Prerequisites
- `web_search` / `web_extract` ツールが利用可能
- `terminal` で `date '+%Y-%m-%d %H:%M:%S %z'` 実行可能
- Telegram配信チャネルがgateway経由で設定済み
- 環境変数: `HERMES_TELEGRAM_CHAT_ID`（配信先）

## How to Run
```bash
# 手動実行時
hermes cron run --job