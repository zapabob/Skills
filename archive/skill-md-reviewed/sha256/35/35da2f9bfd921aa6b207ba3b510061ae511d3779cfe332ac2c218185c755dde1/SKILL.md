---
name: a2a-monitoring
description: LLMOps A2A monitoring daemon for MoE dynamic activation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [a2a, monitoring, moe, llmops, daemon]
    category: infrastructure
---
# A2A Server Monitoring & MoE Dynamic Activation

## Overview
LLMOps-bestpractices auto-monitoring and restart for Hermes A2A agents. Implements health checks, error detection, graceful restart for Mixture-of-Experts dynamic activation architecture.

## LLMOps Practices Applied
- Health Monitoring: 5-min interval checks via `/health` endpoint
- Error Classification: HTTP 429 → exponential backoff; HTTP 503 → 60s wait
- Graceful Shutdown: SIGTERM → wait tasks (max 10s) → force kill
- Resource Tracking: PID, uptime, error counts, last restart timestamp persisted to JSON
- Logging: All actions logged to `a2a_daemon.log`

## Configuration (this session)
- A2A Port: 9121 (localhost-only, conflict-avoiding ports 9901-9941)
- Max Error Count: 3 (3 consecutive failures trigger restart)
- Restart Delay: 30 seconds
- Health URL: `http://127.0.0.1:9121/health`
- Status File: `~/.hermes/a2a_servers_status.json`
- Log File: `~/.hermes/a2a_daemon.log`

## MoE Context
Part of Mixture-of-Experts architecture where each bot has independent A2A server on dedicated port. Server starts/stops dynamically based on task load. 11 bots configured: default(9901), secretary(9902), job-seeker(9921), sedori-buyer(9911), sedori-researcher(9912), sedori-lister(9913), sedori-secretary(9914), sedori-shipper(9915), sedori-ledger(9916), self-improver(9931), work(9941).

### Session-Specific Enhancements (2026-08-19)
- **Background Mode Operation**: Daemon supports background execution via `start /wait` pattern; user prefers minimal console footprint. Session tested `hermes_a2a_daemon_v2.bat` with `timeout 5` and `cmd /c` variants; display encoding issues resolved by setting `chcp 65001` externally.
- **TDD Cycle Integration**: Follows Red→Green→Refactor pattern. Session tested A2A round-robin with `hermes chat -q` (foreground, 120s timeout) and `background=true` with `notify_on_complete=true`. Key learning: 11-bot round-robin requires 300s+ timeout; use `background=true, notify_on_complete=true` for long-running orchestration.
- **seed42 Memory Integration**: Session demonstrated seed42-aware bot-to-bot conversation via `delegate_task` with 5 subagents. seed 42 ensures reproducible bot interaction patterns. Key outputs: self-improver bot provided skill improvement recommendations (feature filtering, load balancing dashboard, LLMOps integration).
- **Load Balancer Dashboard**: Initialized `%USERPROFILE%\.hermes\a2a_load_balancer.json` with `{"key_1_usage":0,"key_2_usage":0,"last_switch":null,"imbalance_alert_count":0,"total_requests":0}`. Monitors NIM key 1 & 2 usage counts, provides imbalance alert at 70% threshold, supports auto-rebalancing logic.
- **Memory Distributed Storage**: MEMORY.md consolidated to free ~600 bytes for seed42記憶. Structure: Semantic Graph (user preferences hierarchy), Embedding (vector-ready technical specs), ObsidianLLMwiki export format (see exported markdown template). seed42記憶定着: 領域確保後、指定された形式でメモリ定着。

## Related Skills
- `hermes-agent` — Core Hermes Agent skill (bundled, protected)
- `moe-dynamic-activation` — MoE architecture orchestration (sister skill)
- `cronjob` — Scheduled task management (complementary)