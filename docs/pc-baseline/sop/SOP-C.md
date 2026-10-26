# SOP C

## Standard Toolchain

- Tests: project-standard C unit tests such as `CTest`, `Unity`, or `cmocka`
- Format: `clang-format`
- Analysis: `clang-tidy`, `cppcheck`, or project-standard static analysis
- Compiler warnings: high warning level, preferably treated as errors

## Rules

1. Make memory ownership, buffer length, and lifetime rules explicit.
2. Prefer bounded operations and defensive validation at every boundary.
3. Propagate errors explicitly; preserve `errno` or return-code meaning when relevant.
4. Use project logging macros or facilities instead of raw `printf` for operational logging.
5. Document public headers, contracts, and invariants.
6. Do not suppress error returns or silently continue after unsafe states.

## Completion Gate

- Static analysis, compile warnings, and tests are satisfied
- Memory, bounds, and error-handling behavior are explicit
- Public headers are documented
