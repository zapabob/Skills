# SOP Go

## Standard Toolchain

- Tests: `go test`
- Format: `gofmt`
- Import ordering: `goimports`
- Analysis: `go vet` and `staticcheck` where available

## Rules

1. Keep package boundaries small and cohesive.
2. Respect `context.Context` for cancellation, deadlines, and request scoping.
3. Wrap errors with context and preserve root causes.
4. Use `slog` or the project logging stack instead of `fmt.Println` in operational paths.
5. Add doc comments to exported identifiers and non-obvious behavior.
6. Use progress libraries such as `mpb` when long-running CLI work needs visibility.

## Completion Gate

- `gofmt`, `goimports`, `go vet`, and relevant tests are satisfied
- Error handling and cancellation behavior are explicit
- Exported API surfaces are documented
