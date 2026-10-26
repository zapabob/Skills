---
name: japanese-daily-calendar-gmail-briefing
description: Use for a Japanese morning brief covering today's Calendar, important unread Gmail, and concrete actions; keep it read-only unless the user explicitly authorizes a mutation.
argument-hint: "[YYYY-MM-DD] [timezone]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Japanese Daily Calendar and Gmail Briefing

## When to use

Use when the user asks for 「カレンダーの予定、重要な未読メール、今日対応が必要なこと」, `デイリーブリーフ`, or a comparable morning briefing.

Non-goals:

- Sending, archiving, labelling, deleting, or changing Calendar events without explicit authorization.
- Treating Gmail `IMPORTANT` or a subject line as a final urgency decision.
- Treating a login alert as proof of compromise or following links inside the message.

## Inputs / context to gather

1. Determine the requested day and timezone; use `Asia/Tokyo` only when that is the requested context.
2. Read `%USERPROFILE%\.codex\automations\automation\memory.md` for the prior cutoff and duplicate-notification baseline. If it is inaccessible, report the limitation and continue from live sources.
3. Confirm authorized Gmail and primary Google Calendar access. Use an explicit RFC3339 start/end for the local calendar day.

## Procedure

1. Query primary Calendar using explicit day bounds, `calendar_id:"primary"`, and the requested timezone. Preserve the exact window in the final report.
2. Inspect each Calendar/Gmail response's connection state and `isError` before interpreting empty results. An empty successful Calendar result is no events; an authorization or connector error makes that source unavailable.
3. Query Gmail in `query` with a bounded unread search such as `is:unread after:YYYY/MM/DD -in:spam -in:trash -category:promotions`, then a bounded priority query such as `is:unread is:important newer_than:7d -in:spam -in:trash`. Use labels only as candidate filters, not as the primary query syntax.
4. Shortlist security, payment, deadline, appointment, engineering, and job-search messages. Deduplicate repeated GitHub notices by thread, PR, or workflow; choose priority by content, not `UNREAD` or `IMPORTANT` alone.
5. Read only the smallest candidate set needed to classify priority and today-action status. Prefer snippets/headers and one representative body over full MIME/HTML batches.
6. Deliver a concise Japanese brief in this order: today's schedule, priority unread mail, concrete actions for today, then non-urgent follow-up. Clearly say when Calendar has no events, and separately label an unavailable source rather than calling it empty.
7. For login/security notices, frame the next step as verification through the official service app/site. If the login is unrecognized, do not use an email link or claim compromise; treat unverified geopolitical mail as a claim requiring primary-source confirmation.
8. If the run is authorized to maintain automation memory, append the timestamp, time window, important new findings, actions, and whether any provider state changed. State explicitly that Calendar/Gmail remained unchanged whenever true.

## Efficiency plan

- Begin with the automation memory and the direct Gmail/Calendar operations; do not dump broad prompt files or tool registries.
- Reuse one date boundary through Calendar query, Gmail filter, reporting, and memory record.
- Stop after bounded source queries, minimal candidate reads, deduplication, a clear report, and any authorized local-memory update.

## Pitfalls and fixes

- Symptom: Gmail output is truncated.
  - Cause: too many full MIME/HTML messages were read.
  - Fix: narrow by query/snippet first, then inspect only actionable candidates and group duplicate CI notifications.

- Symptom: automation memory is inaccessible.
  - Cause: host access restriction such as `CreateProcessAsUserW failed: 5`.
  - Fix: make the missing-history limitation explicit, use bounded live data, and do not repeatedly retry or invent a checkpoint.

- Symptom: Gmail returns `UNAUTHORIZED`, `oauth_token_invalid_grant`, or `Reauthentication required`.
  - Cause: the connected Gmail OAuth grant is no longer valid.
  - Fix: preserve and report any successful Calendar result, mark mail findings unavailable rather than inferred, state that no provider state changed, and require reauthentication before a later unread-mail query.

- Symptom: a Calendar query returns no events or a Gmail query returns no messages.
  - Cause: empty data can be confused with an error response.
  - Fix: check the response connection state and `isError`; state “none” only after the source query succeeded.

- Symptom: a security alert seems urgent.
  - Cause: the alert alone does not establish compromise.
  - Fix: ask whether the event was user-initiated and direct verification to the official site/app.

## Verification checklist

- Calendar bounds and timezone are explicit; no-event results are stated.
- Response connection state and `isError` were checked before treating Calendar or Gmail results as empty.
- Important mail was body- or snippet-confirmed rather than inferred from `IMPORTANT`.
- Duplicate GitHub/CI items are grouped by thread, PR, or workflow.
- The Japanese report separates schedule, priority unread mail, today actions, and later follow-up.
- All mutations are stated; absent explicit authorization, there were no Gmail/Calendar mutations.
- If Gmail authorization failed, the report labels the briefing partial and does not fabricate unread-mail findings.
