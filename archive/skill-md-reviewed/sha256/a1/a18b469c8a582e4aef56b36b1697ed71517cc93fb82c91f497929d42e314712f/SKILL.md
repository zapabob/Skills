---
name: hermes-messaging-channel-setup
description: Set up and verify Hermes messaging channel plugins (Photon/iMessage, LINE, Telegram, Discord, etc.) with profile-safe config, command discovery, and post-setup status checks.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, messaging, gateway, photon, imessage, setup, troubleshooting]
    category: messaging
---

# Hermes Messaging Channel Setup

Use this skill when configuring, logging in to, or troubleshooting Hermes messaging channels such as Photon/iMessage, LINE, Telegram, Discord, Slack, or gateway platform plugins.

## Principles

1. **Load `hermes-agent` first if the task is about Hermes CLI/config.** Treat official docs and the current CLI output as source of truth.
2. **Discover the actual subcommands before assuming names.** Many channel plugins onboard through `setup`, not `login`.
3. **Never print or persist secrets in replies.** Redact phone numbers, tokens, project secrets, API keys, and auth.json/.env credential values.
4. **Prefer status verification after setup.** A setup is not done until the platform status command confirms stored credentials and runtime dependencies.
5. **Separate transient setup state from durable lessons.** Missing credentials or local dependencies are fixable setup state; capture the fix or command sequence, not “tool is broken.”

## Generic Workflow

1. Inspect help/status:
   ```bash
   hermes <channel> --help
   hermes <channel> status
   ```
2. Run the channel’s setup command with explicit flags when possible.
3. If setup waits for browser/device login, use the documented non-browser/device-code mode if available.
4. If command output is expected but missing in non-interactive execution, retry with unbuffered output or a tracked background process.
5. Verify with status:
   ```bash
   hermes <channel> status
   ```
6. If the gateway must pick up new credentials, start or restart it:
   ```bash
   hermes gateway start
   # or
   hermes gateway restart
   ```

## Photon/iMessage Setup Pattern

Photon currently exposes these subcommands:

```bash
hermes photon setup
hermes photon status
hermes photon install-sidecar
hermes photon telemetry on|off
```

There is **no** standalone `hermes photon login`; device login is part of `hermes photon setup`.

Recommended flow:

```bash
hermes photon --help
hermes photon setup --phone '+818012345678' --no-browser
hermes photon status
```

If the user gives a phone number with spaces such as `+81 80 1234 5678`, normalize it to E.164 before running setup:

```text
+81 80 1234 5678 -> +818012345678
```

If setup appears to hang in a non-TTY tool call before printing the device login URL or progress, retry with unbuffered output and a tracked process:

```bash
PYTHONUNBUFFERED=1 hermes photon setup --phone '+818012345678' --no-browser --skip-sidecar-install
```

Use a background process only when you will immediately poll/wait for it. The useful pattern is:

1. Start setup with `PYTHONUNBUFFERED=1`.
2. Poll for the device URL or completion output.
3. Wait until it exits or the user completes browser approval.
4. Run `hermes photon status`.

A successful Photon status should show, with secrets redacted in the user-facing report:

```text
device token        : ✓ stored
project id          : <uuid>
project secret      : ✓ stored
my number           : +818****5678
assigned number     : +162****0000
sidecar deps        : ✓ installed
telemetry           : off
```

## Cron / Scheduled Delivery Triage

Use this sub-workflow when cron jobs run successfully but the user says Telegram/Discord/LINE notifications are not arriving.

1. Check scheduler and gateway first:
   ```bash
   hermes cron status
   hermes cron list --all
   hermes gateway status
   ```
2. Inspect each job’s `Deliver:` target. `last_status: ok` only proves the job ran; it does **not** prove the output went to Telegram. Jobs with `deliver: local` intentionally do not notify, and `deliver: origin` only reaches the originating conversation if there is a valid origin context.
3. For Telegram, prefer an explicit known chat target for recurring jobs that must always notify the user:
   ```text
   telegram:<chat_id>
   ```
   Example update:
   ```bash
   hermes cron edit <job_id>
   # or via cron tooling: set deliver to telegram:<chat_id>
   ```
4. Run a direct platform smoke test before changing many jobs. A successful Telegram Bot API `sendMessage` to the intended `chat_id` proves bot token + chat reachability independently of cron job content.
5. After changing delivery targets, restart or verify the gateway so the scheduler sees current jobs/config:
   ```bash
   hermes gateway restart
   hermes cron status
   ```
6. Distinguish delivery failure from job-body failure. If a Telegram-targeted job shows `last_status: error` from a long OSINT/tool step, fix timeout/content flow separately; delivery may never have been attempted.

## Common Pitfalls

- `hermes photon login` is an invalid command; use `hermes photon setup`.
- `--phone` must be one shell argument; quote it and remove spaces.
- `--skip-sidecar-install` is useful for isolating login/project provisioning, but follow up with `hermes photon install-sidecar` or verify `sidecar deps` if dependencies are not installed.
- Bitwarden Secrets Manager warnings (`BWS_ACCESS_TOKEN` missing) may be unrelated to the channel setup. Mention them separately, but do not treat them as Photon failure if Photon status passes.
- Do not expose full personal phone numbers in final summaries unless the user explicitly asks; prefer masked forms.
- A channel-readiness report can show Telegram credentials present while still saying no candidate chats are known. If a known chat id exists from gateway logs or prior config, use an explicit `telegram:<chat_id>` delivery target instead of relying on platform-only discovery.
- Do not bulk-change `deliver: local` jobs unless their purpose is user notification; local-only jobs often exist for X posting, background sync, or silent watchdogs.

## References

- `references/photon-imessage-setup.md` — session-derived Photon/iMessage setup workaround: `setup` vs `login`, E.164 normalization, unbuffered non-TTY execution, and status verification shape.
- `references/cron-telegram-delivery.md` — session-derived checklist for “cron ran ok but Telegram didn’t arrive”: inspect `Deliver:`, direct Bot API smoke test, explicit `telegram:<chat_id>`, gateway restart, and timeout-vs-delivery separation.

## Verification Checklist

- [ ] Help output confirms the subcommand names.
- [ ] Setup command completed or produced a device approval URL.
- [ ] `status` confirms stored token/credentials.
- [ ] Runtime dependency status is understood (`sidecar deps`, Node binary, gateway service).
- [ ] User-facing summary includes the next command to start/restart the gateway.
