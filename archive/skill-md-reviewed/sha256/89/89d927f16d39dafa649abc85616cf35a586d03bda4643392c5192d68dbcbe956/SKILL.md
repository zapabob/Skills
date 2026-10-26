---
name: linepy-integration
description: Personal LINE account integration using the linepy Python client — auth, QR login, Thrift pitfalls, and fallback skill/script packaging when Hermes plugin autodiscovery fails.
---

# linepy Integration

Personal LINE account integration using the `linepy` Python client.

## Best practice

- Prefer auth token flow if a token is already available.
- If starting from scratch, QR login requires an interactive scan; it is not headless.
- Before attempting authentication, verify Thrift connectivity to LINE hosts. A premature `EOFError` during `getAuthQrcode` or `getRSAKeyInfo` usually means the Thrift transport is being cut off before application-level auth can start.

## Credential/env mapping

- Email account: `LINE_PERSONAL_ADDRESS`
- Password:[REDACTED]
- Auth token (post-login): `LINE_PERSONAL_AUTH_TOKEN`
- Self mid: `LINE_PERSONAL_MID`

## Import quirk (v3.0.8)

- `from linepy.auth import Auth` works for the installed `linepy==3.0.8`.
- `from linepy import Auth` does not.

## Fallback when Hermes plugin load fails

- If a Hermes plugin is not auto-discovered by `discover_plugins()`, fall back to a skill + standalone helper script structure.
- The helper should be invokable as a script and optionally expose a local HTTP API if the agent needs tool-style access.
