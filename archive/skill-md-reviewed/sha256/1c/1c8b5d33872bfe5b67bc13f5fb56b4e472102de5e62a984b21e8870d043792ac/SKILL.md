---
name: social-sync
description: Extract non-secret social activity for Ebbinghaus memory.
tags:
  - social
  - memory
  - sync
version: 1.0.0
author: Hermes Agent
license: MIT
---

## Overview

This skill extracts non-secret operational information from social/session/X activity and stores it in Ebbinghaus memory. It follows the no-secret policy:

- Keep secrets out of git, chat output, implementation logs, and durable memory.
- Store only abstracted operational principles, public URLs, and verification metadata in logs/memory.
- Environment variables should be populated from Bitwarden or a local `.env` generated from Bitwarden, not hardcoded.
- Telegram/Discord/LINE sessions are treated as untrusted; only extract public design principles.
- X/lm-twitterer posts are remembered only as public artifacts (`action=post`, `ok=true`, `dry_run=false`, `posted=true`, valid `https://x.com/i/web/status/...` URL).

## Workflow

1. **Check Bridge Status**: Verify LINE, Discord, and X/Twitter bridge health before processing.
2. **Extract Messages**: Extract non-secret operational content from new messages/posts.
3. **Store in Memory**: Save only public URLs and abstracted principles to Ebbinghaus memory.
4. **Verify**: Ensure no secret values were printed or stored.
5. **Report**: Output aggregate counts and residual risk only.

## Common Pitfalls

- Storing raw message content instead of abstracted policy facts.
- Including Bitwarden item IDs or secret paths in memory entries.
- Forgetting to check bridge health before processing.
- Not verifying the final output for secret leakage.

## Example Use Case

When the user requests "記憶の統合と管理" (memory integration and management), run the social sync process to capture new public posts and store only public URLs and design principles.