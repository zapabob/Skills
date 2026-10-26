---
name: macos-productivity-automation
description: Operate macOS productivity and personal-device automation through CLI or UI bridges. Use for Apple Notes, Apple Reminders, Find My/AirTags, iMessage/SMS, Mail OAuth recovery, and macOS computer-use tasks that require app automation, screenshots, AppleScript, or dedicated CLIs.
---

# macOS Productivity Automation

This umbrella skill groups macOS personal productivity automations. Use it when the task is about controlling or recovering Apple ecosystem apps or local macOS UI state.

## Operating stance

1. Confirm the host is macOS before running macOS-only commands; if the current environment is not macOS, explain what must be run on the Mac.
2. Prefer purpose-built CLIs when present (`memo`, `remindctl`, iMessage/SMS tools, mail clients) before fragile UI automation.
3. Use UI automation/screenshot tools only when no stable API/CLI exists, and verify visually or by a follow-up read.
4. Never expose raw phone numbers, Apple IDs, tokens, OAuth refresh tokens, or private note/reminder contents unless the user explicitly asks.

## App-specific patterns

- **Apple Notes:** use the `memo` CLI for create/search/edit/export when installed. Avoid direct database writes unless the CLI cannot perform the task.
- **Apple Reminders:** use `remindctl` for list/add/complete/delete and pay attention to the distinction between due time and alarms/early nudges.
- **Find My:** Apple exposes no stable public CLI. Use AppleScript/screenshot or Peekaboo-style UI automation, switch between Devices/Items deliberately, and report uncertainty if OCR/screenshot evidence is weak.
- **iMessage/SMS:** prefer the configured messaging bridge/CLI. Verify target chat identity before sending and avoid sending messages without clear user intent.
- **Mail OAuth recovery:** handle OAuth2/XOAUTH2 token refresh as an auth recovery workflow; distinguish expired tokens from IMAP/SMTP connectivity failures.
- **General macOS computer use:** use the smallest automation layer that can observe and act; verify the app state after interaction.

## Verification checklist

- [ ] Command/tool availability checked on the Mac.
- [ ] Target app/account/list/chat/device disambiguated.
- [ ] Action result read back or visually verified.
- [ ] Sensitive identifiers redacted in the summary.

## References

- `references/absorbed-apple-notes-reminders.md` — CLI patterns for Notes and Reminders.
- `references/absorbed-apple-device-messaging-mail.md` — Find My, iMessage/SMS, mail OAuth, and macOS UI automation notes.
