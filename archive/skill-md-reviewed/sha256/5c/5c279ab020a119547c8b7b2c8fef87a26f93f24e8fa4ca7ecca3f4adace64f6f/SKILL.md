---
name: line-platform-integration
description: Use when configuring Hermes LINE platform webhooks.
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Hermes, LINE, Messaging-API, Webhook, Gateway, Tailscale-Funnel]
    related_skills: [hermes-debugging, hermes-agent]
---

# LINE Platform Integration

## Trigger

Use this class-level skill when enabling, configuring, starting, or troubleshooting Hermes' official `line-platform` adapter, including a dependent LINE AI bot and an external tunnel.

## Layer model

Treat these as independent boundaries:

1. **Plugin loading** — `register(ctx)` completes and the platform registry contains LINE.
2. **Gateway configuration** — LINE is explicitly enabled and instantiated.
3. **Local listener** — aiohttp listens on the intended host/port and verifies signatures.
4. **External/API boundaries** — LINE credentials and the public tunnel work independently of local health.

Never infer success at one layer from another layer.

## Verification sequence

1. Confirm `line-platform` and any dependent bot plugin are enabled. Plugin discovery output alone is insufficient; inspect gateway startup logs for adapter instantiation.
2. Configure `platforms.line.enabled: true`; use `platforms.line.extra.host` and `extra.port` for a deterministic listener. Keep access tokens and channel secrets in `.env`, never YAML.
3. Start the gateway and require both log signals:
   - `LINE: webhook listening on .../line/webhook`
   - `✓ line connected`
4. Probe local health first:
   `GET http://127.0.0.1:<port>/line/webhook/health`
   Expected JSON includes `status: ok` and `platform: line`.
5. Probe an unsigned local POST. `401 invalid signature` is positive evidence that the request reached the adapter; it is not an outage.
6. Test the public URL only after local health passes. It must return the adapter response, not a Hermes Web UI redirect or an ngrok interstitial.
7. Test the LINE API separately with the exact bearer token against `/v2/bot/info`. HTTP 401 is a credential/account issue, not proof that the webhook listener is broken.
8. After both boundaries pass, send a correctly HMAC-signed webhook and verify the dependent bot reply path.

## Tunnel diagnostic rule

A public URL can be reachable while forwarding to the wrong service. `302 Location: login?next=/line/webhook` with a `HermesWebUI` server identifies a dashboard target, not the LINE adapter. Inspect the tunnel upstream and route it to the adapter listener, not the Web UI or local LLM port.

## Plugin-loader pitfall

If many plugins log `name '_conversation_before' is not defined` after registration, the loader's post-registration bookkeeping is failing. Snapshot the existing conversation plugins immediately before invoking `register_fn(ctx)`:

```python
_conversation_before = list(self._conversation_plugins)
register_fn(ctx)
```

This is a runtime loader defect, not a LINE credential failure. Re-run plugin discovery and gateway startup after the scoped fix.

## Credential and configuration pitfalls

- A global `LINE_API_BASE_URL` may belong to another bot/plugin while the official adapter uses hard-coded LINE Messaging API endpoints. Inspect the adapter before attributing a 401 to a local LLM endpoint.
- Token shape alone is not proof of validity. Always make a minimal authenticated API request.
- Local webhook health does not validate the channel access token or channel secret.
- Never print raw tokens, secrets, or `.env` contents; report presence, length, and masked prefixes only.

## Completion standard

Report separately: plugin loaded, gateway connected, local listener healthy, public tunnel correctly routed, LINE API authenticated, and bot reply verified. Do not claim the integration complete without real probe evidence.

## References

- `references/gateway-verification.md` — compact evidence table and reproducible probe sequence.
- `references/aiohttp-recovery.md` — recover a LINE adapter blocked by a missing dependency or malformed platform config.
