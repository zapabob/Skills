---
name: evidence-changelog-closeout
description: Use when a user asks for a changelog, release notes, README or model-card updates, implementation logs, publish closeout, evidence tables, or final release framing.
---

# Evidence Changelog Closeout

## Overview

Use this skill when a change needs a durable human-facing record. The output should be grounded in current files, commits, tests, artifacts, and source links rather than memory or optimistic summary.

## Source Order

1. Current git state: commits, staged diff, working diff, PR branch, tags.
2. Local evidence: test logs, benchmark outputs, `_docs` logs, generated reports, release artifacts.
3. Public/current evidence: official docs, live endpoints, registry metadata, HF/GitHub metadata, or primary sources when claims are time-sensitive.
4. Memory: only as a hint for what to verify, not as proof for current claims.

## Workflow

1. Identify the audience:
   - developer changelog
   - README/model card
   - release notes
   - implementation log
   - PR summary
2. Pull facts from artifacts:
   - changed files and commit IDs
   - verification commands
   - exact artifact names, repo IDs, PR IDs, HF commit URLs, or release URLs
   - benchmark/statistical outputs when present
3. Keep claim boundaries explicit:
   - distinguish implementation, tested behavior, current external state, and known limitations
   - do not turn a diagnostic smoke result into a broad runtime claim
   - for quantization/runtime claims, separate weight compression, KV-cache behavior, runtime support, and speculative decoding
4. Write the closeout:
   - include the change summary
   - include verification and residual risk
   - include user-visible changes first for README/release notes
   - include commands and file lists for implementation logs
5. Preserve the record:
   - write a `_docs` implementation or closeout log for substantive changes
   - if `_docs` is ignored but the user wants the log committed, stage the intended file with `git add -f`

## Changelog Template

```markdown
## Summary
- ...

## Changed
- ...

## Fixed
- ...

## Verification
- `command` passed/failed with reason

## Known Limits
- ...
```

Use only sections that have real content.

## Common Mistakes

- Writing release claims before checking the actual artifacts.
- Removing figures, statistics, or proof links when the task calls for publishable evidence.
- Forgetting commit IDs, repo IDs, and verification state in `_docs` closeout logs.
- Repeating stale public claims without refreshing primary sources.
