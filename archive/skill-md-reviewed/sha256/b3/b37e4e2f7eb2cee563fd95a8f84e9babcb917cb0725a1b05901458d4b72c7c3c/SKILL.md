---
name: X Social Handling
description: Manage posting, replying, and monitoring on X/Twitter via Hermes.
version: 0.1
author: Hermes Agent
license: MIT
tags: social-media, twitter, x, automation
---

This skill provides a structured approach for handling X/Twitter interactions, including mention monitoring, reply generation, tweet posting, and API change resilience. It incorporates best practices for credential safety, rate limiting, and fallback handling when platform endpoints evolve.

## API Endpoint Resilience

- Monitor X/Twitter API health via `/lm-twitterer status`; a 404 on `CreateTweet` indicates an endpoint shift. Treat posting as deferred until the endpoint is restored.
- Implement exponential back‑off retry for mention‑reply loops, limited to 3 attempts per mention.
- Keep the whitelist lean; clear stale `replied_ids` after endpoint changes to avoid duplicate replies.
- Document endpoint‑shift incidents in `references/x-social-handling/api-endpoint-shifts.md` for future debugging.

## Core Commands

- `/lm-twitterer status` – show plugin health and configuration.
- `/lm-twitterer mentions [count]` – list recent mention candidates without replying.
- `/lm-twitterer post [topic...] [--live]` – generate and optionally publish a tweet.
- `/lm-twitterer reply [count]` – generate replies for whitelisted mentions.

## Safety Checks

- All credential material stays in `.env`; never expose tokens in logs.
- Use `dry_run=True` by default; manual approval required for live posting.
- Rate limit: max 3 replies per run; configurable via `config.yaml`.

## API Endpoint Resilience

- Monitor X/Twitter API health via `/lm-twitterer status` and the `status` command; treat 404 on `CreateTweet` as a known endpoint shift and defer posting until the endpoint is restored.
- Implement exponential back‑off retry for mention‑reply loops, capped at 3 attempts per mention, to tolerate transient endpoint changes.
- Keep the whitelist lean; when X changes query IDs, clear stale `replied_ids` to avoid duplicate‑reply attempts.
- Log endpoint shift incidents in `references/x-social-handling/api-endpoint-shifts.md` for future reference.