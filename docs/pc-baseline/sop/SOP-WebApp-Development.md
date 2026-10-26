# SOP WebApp Development

## Scope

Apply this SOP to browser-based applications, frontend-backend systems, APIs supporting web clients, and internet-facing user interfaces.

## Mandatory Controls

1. Treat accessibility, security, and performance as first-class acceptance criteria.
2. Use explicit API contracts and typed request/response validation.
3. Enforce authentication, authorization, session handling, and CSRF/XSS protections appropriate to the stack.
4. Preserve auditability for privileged actions and user-impacting state changes.

## Frontend Rules

1. Avoid hidden network behavior and fragile client-side state transitions.
2. Prefer resilient loading, error, and empty states.
3. Protect the UI against unsafe rendering of external or model-generated content.
4. Apply `SOP-Frontend-Design.md` for visual hierarchy, `DESIGN.md` token governance, Apple-informed UI/UX principles, accessibility, responsive behavior, and browser verification.

## Backend Rules

1. Validate every externally supplied input.
2. Apply rate limiting, timeout, retry, and idempotency controls where relevant.
3. Keep secrets server-side and avoid leaking internal errors to clients.

## Verification

1. Use unit, integration, and browser/runtime verification as needed.
2. Check accessibility, console health, and key user paths before completion.
