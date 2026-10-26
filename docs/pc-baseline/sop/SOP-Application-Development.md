# SOP Application Development

## Scope

Apply this SOP to desktop apps, services, CLIs, APIs, background workers, and packaged applications that are not purely web UI concerns.

## Mandatory Controls

1. Keep packaging, configuration, secrets, update paths, and runtime dependencies explicit.
2. Use predictable startup, shutdown, and error behavior.
3. Keep operational configuration separate from code where practical.
4. Document external dependencies, privileged operations, and failure containment.

## Runtime Rules

1. Favor explicit state transitions over implicit global state.
2. Log material events, failures, and retries.
3. Avoid undefined behavior from unchecked inputs, unsafe resource handling, or hidden concurrency assumptions.

## Release Gate

- Build and packaging are reproducible
- Startup and shutdown behavior is known
- Configuration and secret handling are documented
- Relevant tests and smoke checks exist
