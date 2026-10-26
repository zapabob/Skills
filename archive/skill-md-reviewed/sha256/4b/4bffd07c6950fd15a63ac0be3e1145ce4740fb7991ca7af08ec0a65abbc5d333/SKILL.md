---
name: qr-authentication-workflows
description: Use for short-lived QR/PIN login flows with local bridges.
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [qr, authentication, local-bridge, session-safety]
    related_skills: [line-personal-bridge]
---

# QR Authentication Workflows

Use this class-level skill for QR-based authentication where a local bridge or companion worker must be authorized from a phone while protecting an existing desktop session.

## Core workflow

1. Stop competing workers before issuing a new challenge.
2. Start exactly one QR-only login attempt.
3. Immediately inspect status for `loginState`, `qrUrl`, `qrAvailable`, and PIN/number state.
4. Render the QR from the current status response; never reuse a cached URL or image.
5. Ask the operator to scan and complete mobile confirmation immediately.
6. Do not restart while `loginState` is `logging_in`; restarting invalidates the active challenge.
7. Verify `loginState: ready`, profile presence, and a real authenticated API operation before declaring success.
8. If the QR or PIN expires, discard the entire challenge generation and issue one fresh challenge.

## Session-safety pitfalls

- Do not silently fall back from QR to email/password or another credential login. A fallback can create a competing device session and repeatedly evict the desktop client.
- Do not run multiple forced starts while a QR challenge is active.
- QR availability does not prove authentication. Keep issuance, scan, mobile confirmation, readiness, and API usability as separate evidence checkpoints.
- If the bridge reports mobile verification cancellation such as `E2EE_GROUP_TOO_MANY_MEMBERS` / 「スマートフォンでの本人確認がキャンセルされました」, treat it as a failed challenge and reissue a fresh QR.

## LINEjs implementation pattern

For a LINEjs personal bridge that coexists with PC LINE:

- Force `LINEJS_PERSONAL_LOGIN_MODE=qr` in the worker launcher.
- Remove stale email/password/auth-token variables from the child environment.
- Give `loginMode === "qr"` its own branch that calls only `loginWithQR`.
- While `loginState === "logging_in"`, keepalive must return without starting another login.
- After session loss, expose a QR-required state or wait for an operator-triggered restart; do not auto-relogin with credentials.

## Operator-facing communication

Keep instructions short and concrete. State that the image is newly generated, warn that QR and PIN/認証番号 expire quickly, identify the exact image, and ask for one explicit confirmation after scanning. Never report success from QR issuance alone.

## References

- `references/short-lived-qr-challenges.md` — LINEjs expiry, cancellation, recovery, and verification evidence.
