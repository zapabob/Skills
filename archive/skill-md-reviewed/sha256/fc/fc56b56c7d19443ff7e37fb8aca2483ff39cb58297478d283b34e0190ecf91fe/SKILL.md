---
name: hermes-a2a-configuration
description: Hermes A2A config via hermes config command suite
category: devops
---

# hermes-a2a-configuration

## Purpose
Configure A2A agent URLs using `hermes config` command suite. Covers updating `a2a_agents` in main config.yaml, verifying changes, and profile interactions.

## Trigger
When updating or maintaining Hermes A2A `a2a_agents` configuration across profiles and the main config.

## Configuration Pattern
1. `hermes config set a2a_agents.<bot_name>.url http://127.0.0.1:<port>` — writes even with warning
2. `hermes config get a2a_agents` — view the block
3. `grep -A30 "a2a_agents:" ~/.hermes/config.yaml` — confirm file write
4. Profile configs (job-seeker, secretary) may already be pre-configured

## Lessons From This Session
- Looping issue resolved: `a2a_agents` exists in main config at line ~611; `hermes config set` works despite warnings
- Round-robin & 429/503 avoidance verified via test message delivery
- Profile configs are separate from main config.yaml

## Verification Commands
```bash
hermes config set a2a_agents.job-seeker.url http://127.0.0.1:9921
hermes config get a2a_agents
grep -A30 "a2a_agents:" ~/.hermes/config.yaml
```

## Session Reference
- `references/a2a-repo-comparison.md` — A2A repository comparison: official vs fork analysis (this session, 2026-09-06)

## Bot → Port Mapping
job-seeker: 9921, secretary: 9902, sedori-buyer: 9911, sedori-ledger: 9916, sedori-lister: 9913, sedori-researcher: 9912, sedori-secretary: 9914, sedori-shipper: 9915, delivery-worker: 9909, self-improver: 9931, main-agent: 9900, work: 9941
---