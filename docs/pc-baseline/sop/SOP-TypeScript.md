# SOP TypeScript

## Standard Toolchain

- Tests: `vitest`, `jest`, or the project standard
- Format: `prettier`
- Lint: `eslint` with `typescript-eslint`
- Type discipline: `tsconfig` strict mode
- Boundary validation: `zod` or project-standard runtime schema validation

## Rules

1. Avoid `any` unless narrowly justified.
2. Prefer discriminated unions, exhaustive checks, and explicit return types on public APIs.
3. Keep imports grouped and stable.
4. Use structured logging abstractions instead of ad hoc `console.log` in production paths.
5. Add TSDoc/JSDoc to public APIs and non-obvious behavior.
6. Do not catch errors without adding context or handling them explicitly.

## Completion Gate

- TypeScript strict checks pass
- Lint and format expectations are met
- Browser or runtime verification exists for user-visible behavior
