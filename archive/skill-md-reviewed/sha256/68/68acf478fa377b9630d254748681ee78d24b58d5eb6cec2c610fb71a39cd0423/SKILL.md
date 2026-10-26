---
name: messaging-send
description: "Correct usage patterns for the send_message tool, including MEDIA attachments and target selection."
---

# send_message Usage

The `send_message` tool **always** requires both `action` and `message` (and usually `target`).

Common failure pattern observed:
- Calling with only `message` (or malformed MEDIA syntax) produces repeated "Both 'target' and 'message' are required" errors.
- The agent looped 50+ times on the exact same call.

Correct pattern:
1. Use `action='list'` first when the target platform or chat_id is unknown.
2. Always include `target` when sending to a specific channel/DM.
3. For file attachments use the literal string `MEDIA:/absolute/path` inside the `message` field.

## References

- `references/send_message.md` — session-specific error transcript and reproduction recipe.