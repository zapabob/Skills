---
name: messaging-platform-integrations
description: Use for Hermes webhook integrations and verification.
---

# Messaging Platform Integrations

Use this class-level skill when enabling a Hermes gateway platform adapter, wiring an external messaging webhook, or validating an AI-reply plugin behind a public tunnel.

## Reliable workflow

1. **Separate the gates.** Verify platform plugin registration, gateway configuration, the AI/reply plugin, credentials, local listener, public tunnel, and provider-side webhook configuration independently. A healthy webhook URL does not prove provider API authentication, and a valid token does not prove the local listener is reachable.
2. **Inspect registration before editing.** Confirm the plugin is enabled and discoverable, and has valid `plugin.yaml`, `__init__.py`, and adapter entry point. For Hermes platform plugins, confirm `register(ctx)` calls `ctx.register_platform(...)`.
3. **Configure through supported interfaces.** Keep secrets in `.env`; prefer `hermes config set` for platform YAML when direct config mutation is blocked. Explicitly configure `enabled: true` and listener host/port when needed.
4. **Restart and inspect logs.** Require an adapter log such as `webhook listening on <host>:<port>/<path>`, a successful `... connected` line, and a gateway-running line. A process being alive is not enough.
5. **Probe locally.** Test the adapter health endpoint directly. An unsigned POST returning `401 invalid signature` proves routing reached the adapter and signature validation is active; it is not an end-to-end provider test.
6. **Verify the tunnel target, not merely its hostname.** A stale tunnel may forward to a Web UI and return `302 login`; a public `502` means the proxy backend is unavailable. Compare local and external health responses. If a fixed ngrok endpoint is already owned and restart returns `ERR_NGROK_334`, use a stable alternate route rather than repeatedly retrying it.
7. **Use a durable path proxy when appropriate.** A validated Tailscale pattern is `tailscale funnel --bg --set-path=/line http://127.0.0.1:8646/line`; the provider webhook URL then ends in `/line/webhook`. Avoid duplicating the path prefix.
8. **Align runtime URLs and restart.** Set the public base and complete webhook endpoint to the same route, restart, and verify the adapter log reports the updated public URL.
9. **Validate provider credentials independently.** Call the provider identity endpoint with the exact bearer token. HTTP 401 is a credential/channel issue, not evidence that the webhook adapter or tunnel is broken. Never treat token shape or Base64-looking data as proof of validity.
10. **Only then test the AI bridge.** Confirm both platform and reply plugins are enabled, then use a signed provider event or provider-side webhook verification and confirm an actual reply. Health checks and plugin listings alone do not prove LLM invocation.

## Common pitfalls

- A gateway can listen correctly while a stale tunnel forwards to another local service.
- A plugin can appear enabled yet fail during registration; inspect startup logs for registration exceptions.
- Bundled and user copies of the same platform plugin can both appear; identify the active source and avoid duplicate registrations.
- Never print or persist full access tokens, channel secrets, or tunnel auth tokens in reports or skill references.
- Provider-side webhook verification, outbound API authentication, and AI reply behavior are separate acceptance criteria.

## Reference

Read `references/hermes-line-webhook.md` for the validated LINE-specific routing pattern, diagnostic signatures, configuration commands, and verification checklist.
