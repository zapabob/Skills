# SOP CSharp

## Standard Toolchain

- Tests: `dotnet test` with the project-standard framework
- Format: `dotnet format`
- Analysis: Roslyn analyzers and nullable reference types enabled
- Documentation: XML docs or project-standard public API docs

## Rules

1. Enable nullable reference types for maintained code.
2. Use dependency injection and explicit lifetimes where applicable.
3. Use `ILogger` or the project logging abstraction instead of `Console.WriteLine` in application paths.
4. Propagate or wrap exceptions with actionable context.
5. Add XML documentation to public APIs and non-obvious behavior.
6. Use progress reporting abstractions for long-running tasks when user-visible progress matters.

## Completion Gate

- Build, tests, analyzers, and format expectations are satisfied
- Nullability and logging rules are followed
- Public APIs are documented
