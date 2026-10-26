---
name: osint-daily-morning-briefing
description: 毎朝実行される日本語OSINTブリーフィング生成・保存・配信ワークフロー。Shinka MILSPEC評価 + 政府RSS一次資料 + MHLW指定薬物モニターを統合し、Telegram向けMILSPEC/PDB形式Markdownを作成して所定パスに保存する。
category: research
trigger:
  - cron job scheduled for morning execution (JST)
  - manual request for "朝のOSINTブリーフ" or "MILSPEC morning briefing"
tools:
  - shinka_osint_briefing
  - gov_feed_digest
  - mhlw_designated_check
  -