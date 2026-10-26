# SOP CPP

## Standard Toolchain

- Tests: project-standard C++ unit tests such as `GoogleTest` or `Catch2`
- Format: `clang-format`
- Analysis: `clang-tidy`
- Compiler warnings: high warning level, preferably treated as errors

## Rules

1. Prefer RAII and deterministic resource ownership.
2. Prefer standard containers, smart pointers, and safe abstractions over raw memory management.
3. Avoid unchecked casts, hidden ownership transfer, and undefined behavior traps.
4. Use structured logging or project logging facilities instead of `std::cout` for operational logging.
5. Document public interfaces, ownership rules, and invariants.
6. Do not catch exceptions silently; if exceptions are disabled, enforce explicit error-code discipline.

## Completion Gate

- Format, static analysis, compile health, and tests are satisfied
- Ownership and lifetime rules are explicit
- Error and logging behavior are documented
