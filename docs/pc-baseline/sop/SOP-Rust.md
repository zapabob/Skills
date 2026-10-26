# SOP Rust

## Standard Toolchain

- Tests: `cargo test`
- Format: `cargo fmt`
- Lint: `cargo clippy`
- Documentation: `rustdoc`

## Rules

1. Prefer ownership-safe design and explicit lifetimes only when necessary.
2. Avoid `unwrap()` and `expect()` in production paths unless the failure is intentionally fatal and documented.
3. Use typed errors where feasible and add context on propagation.
4. Use `tracing` or the project logging stack instead of ad hoc printing.
5. Add doc comments to public items and non-obvious invariants.
6. Use progress libraries such as `indicatif` for meaningfully long-running CLI workflows.

## Completion Gate

- `cargo fmt`, `cargo clippy`, and `cargo test` evidence exists where applicable
- Error and panic behavior is explicit
- Public APIs are documented
