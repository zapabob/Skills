---
name: sedori-greeting
description: Greet other bots with seed42 memory-based random topics and report sedori business status
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sedori, greeting, report, random, seed42]
    category: devops
    requires_toolsets: [none]
---

# SDLC Greeting Skill

Generate seed42 memory-based random topics for greeting other agents, and produce sedori business report summaries.

## When to Use

- When the cron heartbeat tick fires (controlled by ticker_heartbeat / ticker_last_success)
- To send a greeting to other agents via the a2a Bot Chat
- To report current sedori business status as a random topic

## How to Run

### Greeting Mode

```text
python greet.py --mode greeting --seed 42
```

This generates a random topic based on seed42 and sends a greeting to other bots via the a2a Bot Chat.

### Report Mode

```text
python greet.py --mode report --seed 42
```

This generates a sedori business report with a random topic and reports it.

## Random Topic Generation

Uses seed42 as the base seed for reproducible random topic selection. Topics are drawn from sedori inventory categories and market observations.

Example topics:
- Game consoles and controllers reselling
- Funko Pop sticker market trends
- Small electronics price spreads
- LEGO resale opportunities
- Outdoor clothing category analysis

## Sedori Business Report

Reports current state including:
- Last heartbeat timestamp
- Last success timestamp
- Randomly selected topic
- Status of inventory categories

## Configuration

- seed42 base seed: 42 (hardcoded for reproducibility)
- a2a agent: sedori-buyer on port 9911
- Cron timing: ticker_heartbeat and ticker_last_success