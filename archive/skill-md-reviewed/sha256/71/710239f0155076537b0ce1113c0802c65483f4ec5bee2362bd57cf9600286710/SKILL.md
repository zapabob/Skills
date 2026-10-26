---
name: line-gateway-operations
description: "Operate Hermes via LINE Messaging API: acknowledge quickly, handle group invocation patterns, set reminders/cron deliveries back to the origin chat, and explain delayed responses without over-assuming gateway failures."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [line, gateway, messaging, reminders, cron, user-interaction]
---

# LINE Gateway Operations

Use this skill when the user is interacting through LINE, asks about LINE/Hermes behavior, wants a reminder delivered to the current LINE chat, or is testing invocation/mention behavior in a group.

## Operating principles

1. **Acknowledge quickly before long work.** On LINE, latency feels like silence. If the next step will use tools, scheduling, web, filesystem, or other slow work, send or structure the response so the user gets a short confirmation first when possible, then perform the work. Keep final LINE replies concise.
2. **Act, then verify.** For reminders/scheduled messages, check the current date/time when relevant, create the cron job with `deliver: origin` unless the user asks for another target, and report the job id plus next run time from the tool output.
3. **Avoid overpromising native mentions.** LINE group mentions may not be available through the generic delivery path. If the user asks for a mention, phrase the scheduled message with an explicit visible addressee/name as a fallback rather than claiming a native mention will definitely fire.
4. **Respect group invocation behavior.** In LINE groups, assume Hermes may be configured to respond only when clearly invoked. Natural triggers include `はくあ、...`, `はくあ ...`, `To はくあ. ...`, a direct reply/mention, or a configured wake phrase. English text is fine when the invocation is clear.
5. **Explain delays plainly.** If the user asks why a reply may not arrive, list likely causes without declaring the gateway broken: long tool execution, model latency, external API wait, gateway delivery delay, or platform-side “Get answer” behavior.
6. **No secret persistence.** Do not save raw LINE user IDs, channel IDs, tokens, webhook URLs, or credentials in skills or memory. Store only reusable behavior patterns.

## Reminder / cron pattern for LINE

When scheduling a one-shot LINE reminder:

1. If the date/time is absolute or near-term, verify current time with a tool before scheduling.
2. Create a cron job with:
   - `schedule`: ISO timestamp or explicit schedule from the user.
   - `repeat: 1` for one-shot reminders.
   - `deliver: origin` for the current LINE conversation unless another destination is requested.
   - A self-contained prompt that includes message content, optional URL, random-choice instructions if requested, and mention fallback wording.
3. Report only the useful outcome: scheduled time, destination, content behavior, URL if any, and job id.

## LINE response style for this user

- Japanese is preferred by default.
- Keep LINE replies short and direct; LINE does not render Markdown reliably, so avoid heavy Markdown tables or long bullet walls.
- If the user signals impatience (e.g. “焦らされた”), treat it as feedback to acknowledge faster next time, especially before slow tool work.

## References

- `references/2026-06-13-line-invocation-and-reminder.md` — session-specific notes that motivated this skill: quick acknowledgement, group invocation, English wake text, and reminder scheduling with a mention fallback.
