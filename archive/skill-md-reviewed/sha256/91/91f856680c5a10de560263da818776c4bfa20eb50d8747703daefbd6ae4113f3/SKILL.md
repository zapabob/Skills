---
name: ssrf-safe-client
category: security
description: Connect-time DNS SSRF validation for httpx clients.
---

# SSRF-Safe Async Client

Use when building HTTP clients that need connect-time DNS resolution validation (not just response-hook preflight). The module lives at `tools/url_safety.py`.

## Quick Start

```python
from tools.url_safety import create_ssrf_safe_async_client

client = create_ssrf_safe_async_client(timeout=30.0)
```

Creates an `httpx.AsyncClient` with:
- **Connect-time validation**: every TCP connect resolves the hostname and checks the IP against private/link-local/metadata ranges before dialing
- **DNS rebinding closure**: the pre-flight URL → DNS check and the actual TCP connect are the same resolution — no window between validation and connect
- **Private-origin support**: see below
- **Cloud metadata always-blocked**: 169.254.169.254, metadata.google.internal, etc. — never allowlisted

## Private-Origin Support (allowlist)

The **configured origin** of a service (e.g., a local BlueBubbles on `http://localhost:1234`) is legitimately private. Allow it so self-hosted deployments keep working while **redirect hops** are still validated:

```python
from tools.url_safety import create_ssrf_safe_async_client, private_origin_key

origin_key = private_origin_key("http://localhost:1234")
allow = {origin_key} if origin_key else set()

client = create_ssrf_safe_async_client(
    allow_private_origins=allow,
    timeout=30.0,
)
```

`private_origin_key(url)` returns `(hostname, port)` — the exact connect key the backend uses for allowlist lookup. Only the configured origin is allowed to resolve to private IPs; every redirect hop still validates.

## Origin-Aware Redirect Hooks

For defense-in-depth (earlier error messages, `Authorization` strip on cross-origin hops), add response hooks:

```python
from tools.url_safety import make_origin_aware_redirect_hooks

client = create_ssrf_safe_async_client(
    event_hooks={
        "response": make_origin_aware_redirect_hooks(
            original_url, label="ServiceName"
        ),
    },
)
```

`make_origin_aware_redirect_hooks()` returns a list containing a single `response` hook function. It checks the `Location` header on redirect responses (using `redirect_target_from_response()` which handles both header-based and `next_request`-based resolution) and raises `ValueError` if the target is private and the origin is public.

## Pitfalls

### Response hooks alone DO NOT close DNS rebinding
The `next_request` object is `None` for many redirect responses, so URL preflight via hooks misses the actual connect. **Connect-time validation in the transport backend is required** — this is why `create_ssrf_safe_async_client()` wraps the transport, not just the hooks.

### `make_origin_aware_redirect_hooks` is additive, not a substitute
It provides earlier errors and authorization stripping but does not replace connect-time validation. Use both.

### `_resolved_http_connect_ips` now requires `allow_private_origins` parameter
If calling this function directly: `_resolved_http_connect_ips(host, port, scheme, allow_private_origins)`. The `_SSRFGuardedAsyncNetworkBackend` constructor also gained this parameter.

## See Also

- `tools/url_safety.py` — full module with `is_safe_url`, `is_always_blocked_url`, `ssrf_safe_http_transport()`, `create_ssrf_safe_client()` (synchronous variant), `SSRFConnectionBlocked` exception, `_TRUSTED_PRIVATE_IP_HOSTS`, `_ALWAYS_BLOCKED_IPS`, `_ALWAYS_BLOCKED_NETWORKS`.