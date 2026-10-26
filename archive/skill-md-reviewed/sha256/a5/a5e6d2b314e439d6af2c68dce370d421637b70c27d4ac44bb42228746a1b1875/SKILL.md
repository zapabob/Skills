---
name: secretary
description: "Secretary bot with seed42 memory base and random topic greetings for A2A agents"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [secretary, a2a, bot, greeting, memory]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [line-ai-bot]
---

# Secretary Bot

The secretary bot operates on port 9902 as an A2A agent, using seed42 as the memory base for reproducible random topic selection. It greets other bots and proposes coordination adjustments.

## Core Concepts

### Seed42 Memory Base
- Uses `seed42` as the deterministic random seed for topic selection
- Ensures consistent greeting topics across sessions when using the same seed
- Enables reproducible random topic generation for bot coordination

### A2A Agent Protocol
- Runs on port 9902 as specified in the main config
- Registered in `a2a_agents` section of `.hermes/config.yaml`
- Uses NIM keys with round-robin routing (2 NIM keys configured)

### LLMOps Daemon Monitoring
- Monitors LLMOps daemon status
- Provides health checks and routing suggestions

## Configuration

The secretary bot is configured in `.hermes/config.yaml`:

```yaml
a2a_agents:
  secretary:
    url: http://127.0.0.1:9902
    timeout: 120
```

### NIM Keys (Round-Robin)
Two NIM keys are configured for round-robin routing:
1. `model: nvidia/nemotron-3.5-lightning-30b-a3b`, `provider: nvidia`, `api_key: ''`
2. `model: nvidia/nemotron-3.5-lightning-30b-a3b`, `provider: nvidia`, `api_key: ''`

## Operation

### Greeting Other Bots
The secretary bot initiates greetings to other A2A agents using seed42-based random topic selection. Topics are chosen deterministically from a predefined set, ensuring reproducibility.

### Coordination Proposals
After greeting, the secretary bot proposes adjustment proposals for inter-bot coordination, including:
- Topic-specific coordination suggestions
- Resource allocation recommendations
- Timing alignment proposals

### Memory Persistence
- All greeting and coordination data is stored in seed42-based memory
- Memory enables consistent behavior across sessions
- Supports longitudinal tracking of bot interactions

## Usage

```bash
# Start the secretary bot via Hermes CLI
hermes chat -q "Secretary: greet other bots with seed42 memory"

# Or via A2A protocol to port 9902
curl -X POST http://127.0.0.1:9902/a2a/greet \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "target_agents": ["main-agent", "sedori-buyer"]}'
```

## Topics

The secretary bot uses a predefined set of greeting topics, selected deterministically using seed42:
- "daily-status-check"
- "resource-alignment"
- "timing-sync"
- "workflow-optimization"
- "status-update"

Each topic is selected using `random.seed(42)` ensuring reproducible ordering.