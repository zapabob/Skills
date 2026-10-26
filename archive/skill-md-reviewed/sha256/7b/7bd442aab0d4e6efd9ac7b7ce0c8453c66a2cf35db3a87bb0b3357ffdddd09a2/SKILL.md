---
name: mail-oauth2-recovery
description: Recover desktop mail OAuth2 / XOAUTH2 logins when token refresh or consent flow fails.
version: 1.0.0
author: Hermes
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Email, OAuth2, XOAUTH2, Gmail, IMAP, SMTP, Recovery]
---

# Mail OAuth2 Recovery

Use this skill when a desktop mail client or CLI mail tool needs OAuth2 recovery and the existing token no longer authenticates.

## Trigger conditions
- IMAP/SMTP auth fails with XOAUTH2 `400`, `Invalid credentials`, or a token refresh loop.
- The tool expects OAuth2 credentials but the current token set no longer works.
- A consent flow was started, but the redirect/callback did not complete cleanly.

## Recovery workflow
1. Confirm the exact auth mode the tool expects.
   - For Gmail IMAP with XOAUTH2, verify the scope includes `https://mail.google.com/`.
2. Treat repeated XOAUTH2 `400` / `Invalid credentials` as a stale credential set, not a transient retry.
3. Re-run consent with a fresh offline grant:
   - `access_type="offline"`
   - `include_granted_scopes="true"`
   - `prompt="consent"`
4. Prefer a local loopback callback on the same machine that is opening the auth URL.
   - Match the registered redirect URI exactly.
   - Capture the full `http://localhost...` callback URL or let the local listener consume it directly.
5. After token exchange, re-run the mailbox list/read command immediately to verify the credential set before moving on.

## Pitfalls
- A browser HTTP 400 page during consent usually means the callback/redirect path was mismatched or the wrong device handled the flow.
- Pasting only the auth URL into a remote device is brittle when the redirect URI is localhost.
- A valid Google login is not enough if the scope is too narrow for the client’s IMAP/SMTP use case.
- If the tool’s config references separate client/token fields, all of them must be regenerated together; mixing old and new values often produces another XOAUTH2 400.

## Verification
- The mail tool can list the mailbox successfully.
- The token set survives a second immediate list operation without reauth.

## Support files
- `references/gmail-loopback-recovery.md` — concise recovery notes and failure signatures.
- `scripts/gmail_oauth_local_server.py` — reusable helper to print an auth URL, wait for the localhost callback, and emit refreshed credentials.
