---
name: recurring-news-delivery
description: "Set up and manage recurring news summaries via cronjob."
version: 1.1.0
author: Hermes Agent
license: MIT
category: openclaw-imports
metadata:
  hermes:
    tags: [news, cron, delivery, telegram, japanese, summary]
---

# Recurring News Delivery Skill

## When to use
- User requests regular news updates on specific topics (AI, tech/gadgets, global affairs)
- Setting up scheduled Telegram (or other gateway) deliveries
- User wants Japanese summaries delivered daily in the morning

## Core Workflow
1. Capture frequency, language (Japanese preferred), topics, and delivery destination (chat_id or 'envに書いてある') with direct questions.
2. Read Hermes config/.env if destination is stored there (handle encoding issues gracefully).
3. Create cronjob with:
   - schedule: "0 7 * * *" for morning delivery
   - deliver: "telegram:<chat_id>" or platform-specific
   - prompt: Collect latest news on AI, gadgets, international affairs; summarize in Japanese (3-5 key topics); keep concise
4. Verify job with `cronjob(action='list')`.

## Preferences Captured
- Japanese summaries for morning delivery
- Personal chat delivery
- Topics: AI, gadgets, international affairs

## Pitfalls
- Always include `schedule` when creating cron jobs.
- Confirm deliver destination explicitly if env lookup fails.
- Use model override if needed for news summarization quality.
- **Stale skill**: this skill was auto-marked stale by curator (33d+ inactivity). If reused, it auto-reactivates.

## References
- See `references/news-prompt-template.md` for reusable prompt.