---
name: code-review
description: "Code review. Reviews a file or diff for correctness first, style second, and reports findings with line numbers."
---

Review the code that follows and report findings.

Correctness first: wrong results, unhandled cases, races, resource leaks.
Then security. Then clarity. Style last, and only where it hides a bug.

For each finding give the line, what is wrong, and what would fix it. If the
code is fine, say that plainly rather than inventing minor notes to seem
useful. Never restate what the code does.
