---
name: google-auth-fallback
description: "Fallback Google OAuth flow when setup.py fails."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Google Auth Fallback

Use this skill when `productivity/google-workspace` cannot complete OAuth because:
- `google-auth-oauthlib` / `google-api-python-client` are unavailable in the active Python
- `setup.py --auth-code` fails with state mismatch
- The environment lacks `py -3` or the wrong `python` is resolved
- You still need a working access/refresh token for Gmail, Calendar, Drive, Sheets, Docs, or Contacts

## Session-proven script paths

Client secret and token paths are under `HERMES_HOME` (`~/.hermes` by default):
- `%USERPROFILE%/.hermes/google_client_secret.json`
- `%USERPROFILE%/.hermes/google_token.json`
- `%USERPROFILE%/.hermes/google_oauth_pending.json`

Auth URL generator:
- `E:/temp/google_oauth_stdlib.py`

Token exchange:
- `E:/temp/google_token_exchange_stdlib.py`

Verifier / refresh routine:
- `%USERPROFILE%/.hermes/scripts/google_token_refresh_stdlib.py`

These scripts use only Python stdlib (`urllib`, `json`, `hashlib`, `secrets`, `time`, `datetime`). They do not import `google-auth` or `google-api-python-client`.

## Windows/Microsoft Store Python pitfall

On this host, `python` can point to the Microsoft Store stub (`Python 3.14.6`) while the project venv uses `cpython-3.12-windows-x86_64-none`. Use the project venv explicitly:

```bash
"%USERPROFILE%/Documents/New project/hermes-agent/.venv/Scripts/python.exe" /path/to/script.py
```

`py -3` is not available here.

## Windows/MSYS native Python argv paths

When the interpreter is native Windows Python, never pass `$HOME/.hermes/...` as a script argument. MSYS rewrites it to `C:\c\Users\...` and Python cannot open the file. Use `%USERPROFILE%/.hermes/...` native paths. Load the callback from `google_callback.txt` inside Python so the auth code is not on the shell command line. Details: `references/msys-native-python-oauth-paths.md`.

## OAuth URL mismatch / stale callback recovery

The stored client may allow only `http://localhost`, while the user pastes `http://localhost:1/?...`. In that case:
- Do not retry the stale callback.
- Generate a fresh auth URL with redirect URI `http://localhost`.
- Persist a new `google_oauth_pending.json` with that same redirect/state/verifier.
- Ask the user to paste the final `http://localhost/?code=...&state=...` URL from the new flow.

A matching callback `state` is not enough. If `--auth-code` still returns `invalid_grant` / `Bad Request`, do not retry that URL — run `--auth-url` again and require a paste that includes the new pending `state`.

## Verification after token save

After exchange, verify with API calls rather than importing `googleapiclient`:

```bash
curl -s -H "Authorization: Bearer ACCESS_TOKEN" https://gmail.googleapis.com/gmail/v1/users/me/profile
curl -s -H "Authorization: Bearer ACCESS_TOKEN" "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=1"
```

Expected: HTTP 200 with valid JSON.

## Automatic refresh cron

Create a cron job to keep the token warm:

```bash
hermes cron create \
  --name "Google Workspace token refresh" \
  --script "%USERPROFILE%/.hermes/scripts/google_token_refresh_stdlib.py" \
  --schedule "every 20m" \
  --deliver local \
  --no-agent
```

The refresh script is quiet on healthy/no-op runs and prints `REFRESH_OK` only when it actually refreshes.

## Safety

- Never log access tokens, refresh tokens, client secrets, or auth codes.
- When exchanging callbacks, read the URL from stdin or a file argument; do not echo it in tool output.
- Verify the callback `state` matches the active pending file before proceeding.
