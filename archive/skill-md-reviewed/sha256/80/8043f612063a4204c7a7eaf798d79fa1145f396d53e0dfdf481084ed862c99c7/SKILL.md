---
name: google-workspace
description: Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration via Python. Uses OAuth2 with automatic token refresh. No external binaries needed — runs entirely with Google's Python client libraries in the Hermes venv.
version: 1.0.0
author: Nous Research
license: MIT
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya]
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — all through Python scripts in this skill. No external binaries to install.

## References

- `references/cron-gmail-calendar-briefings.md` — cron-safe morning briefing pattern using the Google Workspace Python API instead of IMAP-only mail CLIs.
- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)
- `references/oauth-telegram-iphone.md` — Telegram/iPhone OAuth flow, including localhost redirect URI mismatch and malformed 400 recovery.
- `references/2026-06-03-telegram-iphone-oauth-session.md` — session-proven auth-url/auth-code flow for iPhone + Telegram, including the intermediate Google `unknownerror` page and final localhost callback.
- `references/oauth-refresh-recovery.md` — quick recovery path when `setup.py --check` returns `REFRESH_FAILED invalid_grant`.
- `references/oauth-state-mismatch-windows.md` — recovery for OAuth `state mismatch`, Windows `py -3` launcher use, and post-auth Gmail/Calendar smoke checks.
- `references/cron-safe-gmail-calendar.md` — cron-safe morning briefing pattern for Gmail + Calendar using the Google Workspace Python API wrapper instead of relying on shell `PATH` or a separate mail CLI.

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — API wrapper CLI (agent uses this for all operations)

## First-Time Setup

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

Define a shorthand first. Use `$HOME` rather than `~` inside quoted shell variables; quoted tildes are not expanded by bash/MSYS and will be treated as a literal path component.

```bash
GSETUP="python $HOME/.hermes/skills/productivity/google-workspace/scripts/setup.py"
```

### Step 0: Check if already set up

```bash
$GSETUP --check
```

If it prints `AUTHENTICATED`, skip to Usage — setup is already done.

### Step 1: Triage — ask the user what they need

Before starting OAuth setup, ask the user TWO questions:

**Question 1: "What Google services do you need? Just email, or also
Calendar/Drive/Sheets/Docs?"**

- **Email only** → They usually don’t need this skill at all. Default to the `himalaya` skill for raw Gmail IMAP/SMTP access. If the user explicitly wants Gmail OAuth2 (or app passwords are unavailable / undesired), use the OAuth2-capable Himalaya flow in `email/himalaya` instead of steering them to an app password path. For the simplest non-OAuth setup, an app password is still the shortest route; for OAuth2, follow the himalaya recovery reference.

- **Calendar, Drive, Sheets, Docs (or email + these)** → Continue with this
  skill's OAuth setup below.

**Question 2: "Does your Google account use Advanced Protection (hardware
security keys required to sign in)? If you're not sure, you probably don't
— it's something you would have explicitly enrolled in."**

- **No / Not sure** → Normal setup. Continue below.
- **Yes** → Their Workspace admin must add the OAuth client ID to the org's
  allowed apps list before Step 4 will work. Let them know upfront.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> You need a Google Cloud OAuth client. This is a one-time setup:
>
> 1. Go to https://console.cloud.google.com/apis/credentials
> 2. Create a project (or use an existing one)
> 3. Click "Enable APIs" and enable: Gmail API, Google Calendar API,
>    Google Drive API, Google Sheets API, Google Docs API, People API
> 4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
> 5. Application type: "Desktop app" → Create
> 6. Click "Download JSON" and tell me the file path

Once they provide the path:

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

### Step 3: Get authorization URL

```bash
$GSETUP --auth-url
```

This prints a URL. **Send the URL to the user** and tell them:

> Open this link in your browser, sign in with your Google account, and
> authorize access. After authorizing, you'll be redirected to a page that
> may show an error — that's expected. Copy the ENTIRE URL from your
> browser's address bar and paste it back to me.

### Step 4: Exchange the code

The user will paste back either a URL like `http://localhost:1/?code=4/0A...&scope=...`
or just the code string. Either works. The `--auth-url` step stores a temporary
pending OAuth session locally so `--auth-code` can complete the PKCE exchange
later, even on headless systems:

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED"
```

### Step 5: Verify

```bash
$GSETUP --check
```

Should print `AUTHENTICATED`. Setup is complete — token refreshes automatically from now on.

### Notes

- Token is stored at `google_token.json` under the active profile's `HERMES_HOME` and auto-refreshes.
- Pending OAuth session state/verifier are stored temporarily at `google_oauth_pending.json` under the active profile's `HERMES_HOME` until exchange completes.
- Hermes now refuses to overwrite a full Google Workspace token with a narrower re-auth token missing Gmail scopes, so one profile's partial consent cannot silently break email actions later.
- To revoke: `$GSETUP --revoke`

## Usage

All commands go through the API script. Set `GAPI` as a shorthand. Use `$HOME` rather than `~` inside quoted shell variables so the path expands correctly on bash/MSYS and other POSIX shells:

```bash
GAPI="python $HOME/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
```

### Gmail

```bash
# Search (returns JSON array with id, from, subject, date, snippet)
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:[REDACTED_EMAIL] newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# Read full message (returns JSON with body text)
$GAPI gmail get MESSAGE_ID

# Send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html

# Reply (automatically threads and sets In-Reply-To)
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."

# Labels
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### Calendar

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (ISO 8601 with timezone required)
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "[REDACTED_EMAIL],[REDACTED_EMAIL]"

# Delete event
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5
```

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
# Read
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# Write
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

### Docs

```bash
$GAPI docs get DOC_ID
```

## Output Format

All commands return JSON. Parse with `jq` or read directly. Key fields:

- **Gmail search**: `[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**: `{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**: `{status: "sent", id, threadId}`
- **Calendar list**: `[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**: `{status: "created", id, summary, htmlLink}`
- **Drive search**: `[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Contacts list**: `[{name, emails: [...], phones: [...]}]`
- **Sheets get**: `[[cell, cell, ...], ...]`

## Rules

1. **Never send email or create/delete events without confirming with the user first.** Show the draft content and ask for approval.
2. **Check auth before first use** — run `setup.py --check`. If it fails, guide the user through setup.
3. **Use the Gmail search syntax reference** for complex queries — load it with `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")`.
4. **Calendar times must include timezone** — always use ISO 8601 with offset (e.g., `2026-03-01T10:00:00-06:00`) or UTC (`Z`).
5. **Respect rate limits** — avoid rapid-fire sequential API calls. Batch reads when possible.
6. **For Gmail + Calendar briefing cron jobs, prefer this skill's Python API over IMAP-only CLIs.** Scheduled jobs can have a narrower PATH than interactive sessions; avoid letting an old/non-OAuth mail binary become the dependency for a Workspace briefing. Make the cron prompt self-contained: use absolute script paths, run `setup.py --check`, and set any required `PYTHONPATH`/repo path before invoking `google_api.py`.
7. **When the user is coordinating appointments, travel, or “必要なことは全部” type planning, do the full itinerary pass:**
   - check the current calendar state first,
   - resolve the final schedule before adding buffers,
   - add explicit wait / transit blocks when they change where the user should be,
   - include location notes such as parking, waiting place, and transfer trigger (“終わり次第”).
   - re-list the calendar after edits to verify the final state.
   - If the user changes one appointment in the chain, review adjacent blocks for knock-on edits before finishing.
8. **When an incoming meeting notice matches an existing calendar block, merge/update the existing event rather than creating a duplicate.** Preserve the user's original label and duration unless explicitly changed, add the external meeting name and URL to summary/location/description, then re-list the date to verify. See `references/appointment-itinerary-patterns.md`.
9. **When Gmail and Calendar disagree, trust the latest scheduler confirmation first.** For TimeRex/Calendly/other booking flows, search both the scheduler mail and the calendar notification thread, then compare against the live Calendar event list. Older Google Calendar notification emails can lag behind the current event metadata (for example, stale Zoom IDs or stale descriptions), so use the newest confirmation email plus the current calendar event as the source of truth before drafting a reschedule. See `references/external-scheduler-source-of-truth.md`.

## Scheduled Gmail/Calendar Checks

For recurring Gmail + Calendar briefings, prefer this skill's `google_api.py` path over IMAP-only mail clients. It uses the same Google Workspace OAuth token for both Gmail and Calendar and avoids cron jobs depending on a shell `PATH` that may point at a different email CLI binary than the interactive session.

Cron prompt pattern:

```bash
export PYTHONPATH="%USERPROFILE%/Desktop/clawdbot-main3/hermes-agent-upstream"
GSETUP="python %USERPROFILE%/.hermes/skills/productivity/google-workspace/scripts/setup.py"
GAPI="python %USERPROFILE%/.hermes/skills/productivity/google-workspace/scripts/google_api.py"
$GSETUP --check
$GAPI gmail search 'is:unread newer_than:2d' --max 10
$GAPI calendar list
```

If `setup.py` or `google_api.py` fails with `ModuleNotFoundError: hermes_constants` in a detached/cron context, run it from the Hermes checkout or set `PYTHONPATH` to the checkout containing `hermes_constants.py`. Do not switch back to Himalaya for Calendar-capable briefings unless the task is explicitly IMAP-only.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 above |
| `REFRESH_FAILED` | Token revoked or expired — redo Steps 3-5 |
| `ERROR: OAuth state mismatch` | The pasted localhost callback belongs to an older pending OAuth session. Run `--auth-url` again, send the fresh URL to the user, and exchange only the new callback. On Windows/MSYS, prefer `py -3` if bare `python` fails. See `references/oauth-state-mismatch-windows.md`. |
| `HttpError 403: Insufficient Permission` | Missing API scope — `$GSETUP --revoke` then redo Steps 3-5 |
| `HttpError 403: Access Not Configured` | API not enabled — user needs to enable it in Google Cloud Console |
| Generic Google OAuth `400 malformed` before final localhost redirect | Check `google_client_secret.json` `redirect_uris`; generate the auth URL with the same redirect URI stored in the client, and persist that URI in pending OAuth state. See `references/oauth-telegram-iphone.md`. |
| `ModuleNotFoundError` | Run `$GSETUP --install-deps` |
| Advanced Protection blocks auth | Workspace admin must allowlist the OAuth client ID |
| Gmail IMAP via Himalaya returns XOAUTH2 `400` / `Invalid credentials` | Re-do the Gmail OAuth2 flow and make sure the Himalaya config has `backend.auth.method = "xoauth2"` plus the Gmail scope. See `email/himalaya/references/gmail-oauth2-recovery.md`. |

## Revoking Access

```bash
$GSETUP --revoke
```
