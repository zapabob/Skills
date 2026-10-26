---
name: gmail-calendar-follow-up-monitoring
description: Use for authorized Gmail and Google Calendar follow-up monitoring when the user wants recent changes highlighted and confirmed actionable mail flagged with the explicitly requested Gmail label (for example `要対応` or `STARRED`).
argument-hint: "[previous-run-time] [timezone]"
disable-model-invocation: true
allowed-tools:
  - Read
  - Grep
  - Bash
---

# Gmail and Google Calendar Follow-up Monitoring

## When to use

Use for an authorized follow-up check such as “recent email and calendar activity,” “highlight important changes,” or “flag items needing attention.” This procedure is for reading and reporting, with a narrow Gmail-label action only when the request authorizes flagging.

Non-goals:

- sending, deleting, archiving, or changing calendar events without explicit approval
- labeling based only on a subject line, sender, or system importance marker
- following security or payment links embedded in email

## Inputs / context to gather

1. Confirm the authorized Gmail and Calendar connectors are available.
2. Get the last successful-run timestamp from automation memory or a supplied fallback. Record the timezone; use `Asia/Tokyo` only when it is the requested context.
3. Decide the Calendar horizon (normally the next 14 days) and which Gmail flag/label, if any, the user explicitly authorized (`要対応` and `STARRED` are distinct past workflows).
4. If automation memory is inaccessible, capture the exact failure and use the available prior timestamp; do not loop on the same read failure.

## Procedure

1. Run a bounded Gmail candidate search. Put date/exclusion operators in `query`, for example `after:YYYY/MM/DD -in:spam -in:trash`; do not put these operators in `label_ids`.
2. Search the primary Calendar using explicit RFC3339 `time_min`, `time_max`, and timezone. If the result is paginated, retain those same bounds while continuing.
3. Separate routine notices from potentially actionable items. Read each potential security, payment, deadline, interview, or changed-event message with the available batch-read operation (`gmail_batch_read_email_threads` or `gmail_batch_read_email`) before classifying it.
4. Report actionable mail and calendar changes prominently, then summarize routine/no-action notices separately. For security or payment notices, direct the user to the official app/site rather than opening a link from the email.
5. Only if flagging is within the request: use the connector's supported label operation for the exact requested label. For `要対応`, use `gmail_apply_labels_to_emails` with `add_label_names:["要対応"]`; set `create_missing_labels:true` only if needed. For `STARRED`, use the available batch-modify operation with `add_labels:["STARRED"]`.
6. Record the exact time window, whether automation memory was available, exact modified message IDs, mutations made, and the tool success result. State explicitly that no send/delete/event mutation occurred unless one was actually authorized and performed.
7. When email confirms an appointment, reconcile it against the bounded Calendar result and a targeted appointment-name search. Report a missing entry, but never create or edit it without explicit authorization.

## Efficiency plan

- Start with direct tool names (`gmail_search_emails`, `gmail_batch_read_email_threads`, `google_calendar_search_events`, `gmail_apply_labels_to_emails`) instead of dumping the entire tool registry.
- Reuse one date window across query, Calendar pagination, and final report.
- Read only candidates that plausibly need action; never skip the body-read gate for a message that will be labelled.
- Stop after the bounded searches, body confirmation, authorized labels, and a clear report. Do not retry inaccessible automation memory indefinitely.

## Pitfalls and fixes

- Symptom: automation memory returns `CreateProcessAsUserW failed: 5 (アクセスが拒否されました)`.
  - Likely cause: host access restriction on `automation-3/memory.md`.
  - Fix: use a supplied/known prior-run timestamp as the fallback cutoff, make the limitation explicit, and avoid reprocessing an unbounded historical mailbox.

- Symptom: a cross-source query returns `USER_NOT_LOGGED_IN` or `connector_auth_failure`.
  - Likely cause: the connector is not authorized.
  - Fix: restore an authorized source before interpreting results; do not infer messages or flags.

- Symptom: tool output is truncated before the required Gmail/Calendar function is found.
  - Likely cause: broad tool-list inspection.
  - Fix: query/choose the four direct tool names above.

- Symptom: a login or payment message is flagged incorrectly.
  - Likely cause: classification relied on subject/labels rather than the message body.
  - Fix: confirm the actual body and message ID first; use official channels for verification.

## Verification checklist

- Gmail date/exclusion syntax was supplied in `query` and the Calendar range is explicit.
- Each labelled message was body-confirmed and used an actual message ID.
- The requested label operation returned `success:true`, and the exact modified message IDs—not a broad `is:starred` search—were verified when possible.
- The report separates actionable items from routine notifications and includes the checked time window.
- The report states any inaccessible memory/connector constraint and all mutations performed.
- No email link was used for security/payment verification, and no unapproved send/delete/calendar modification occurred.
