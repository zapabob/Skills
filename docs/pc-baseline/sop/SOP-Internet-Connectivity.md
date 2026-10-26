# SOP Internet Connectivity

## Scope

Apply this SOP to any outbound or inbound network connection, third-party API call, remote model call, package fetch, webhook, browser fetch, or internet-mediated deployment path.

## Mandatory Controls

1. Use TLS-protected transport unless an exception is explicitly justified.
2. Set timeouts, retry limits, and backoff policies deliberately.
3. Keep outbound dependencies minimal and documented.
4. Validate responses before trusting or acting on them.
5. Preserve request/response auditability at the level appropriate to the sensitivity of the data.

## Security Controls

1. Never send secrets or regulated data to endpoints that are not explicitly approved.
2. Prefer allowlists, explicit base URLs, and fixed provider configuration over dynamic endpoints.
3. Treat remote content as untrusted input.
4. Guard against SSRF, prompt injection via remote content, dependency confusion, and unsafe download-execute behavior.

## Reliability Controls

1. Use idempotency where duplicate execution is harmful.
2. Define degraded-mode behavior for provider outage or network failure.
3. Log connectivity failures with actionable detail.

## Completion Gate

- Network dependencies are known
- Timeout and retry behavior is explicit
- Secret and payload handling is reviewed
- Fallback or failure behavior is documented
