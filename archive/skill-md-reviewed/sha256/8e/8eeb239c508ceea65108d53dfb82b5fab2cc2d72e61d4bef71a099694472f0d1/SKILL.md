---
name: recurring-news-delivery
description: Set up and manage recurring news summaries (AI, gadgets, international affairs) delivered via Telegram or other platforms using cronjob. Handles Japanese summaries, morning delivery, and destination configuration from env or explicit chat_id.
category: openclaw-imports
---

# Recurring News Delivery Skill

## When to use
- User requests regular news updates on specific topics (AI, tech/gadgets, global affairs)
- Setting up scheduled Telegram (or other gateway) deliveries
- User wants Japanese summaries delivered daily in the morning

## Core Workflow
1. Use clarify to capture frequency, language (Japanese preferred), topics, and delivery destination (chat_id or 'envに書いてある')
2. Read Hermes config/.env if destination is stored there (handle encoding issues gracefully)
3. Create cronjob with:
   - schedule: "0 7 * * *" for morning delivery
   - deliver: "telegram:<chat_id>" or platform-specific
   - prompt: Collect latest news on AI, gadgets, international affairs; summarize in Japanese (3-5 key topics); keep concise
4. Verify job with cronjob(action='list')

## Preferences Captured
- Japanese summaries for morning delivery
- Personal chat delivery
- Topics: AI, gadgets, international情勢

## Pitfalls
- Always include `schedule` when creating cron jobs
- Confirm deliver destination explicitly if env lookup fails
- Use model override if needed for news summarization quality

## References
- See references/telegram-destination.md for env lookup patterns
- See references/news-prompt-template.md for reusable prompt