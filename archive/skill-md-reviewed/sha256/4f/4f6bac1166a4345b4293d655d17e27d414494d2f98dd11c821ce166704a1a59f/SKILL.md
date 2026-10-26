---
name: hermes-ebbinghaus-cron
description: "Hermes Ebbinghaus cron sleep with archive pruning."
version: "1.0.0"
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [memory, ebbinghaus, cron, consolidation]
    related_skills: []
---
# Hermes Ebbinghaus Cron Sleep Cycle

## Quick Start
```python
from hermes_tools import ebbinghaus_memory
ebbinghaus_memory({
    "action": "sleep",
    "prune_mode": "archive",
    "rehearse_threshold": 0.45,
    "forget_threshold": 0.08,
    "salience_keep_threshold": 0.7,
    "limit": 200
})
```

## Typical Results
- **Before**: count=6207 active=4980 archived=1227
- **After**: count=6207 active=4980 archived=1227
- **Rehearsed**: 2 items
- **Forgotten**: 0
- **Pruned**: 0

## Failure Fixes
- **Terminal access**: Ensure bash/PTY; validate paths pre-run
- **YAML config write blocks**: Use `hermes config set --force`, not direct file write
- **Config duplication**: Top-level `<n>.llm.model` block wins (YAML after-wins quirk)

## Cron Schedule
```
0 2 * * * cd /path/to/hermes && python -c "from hermes_tools import ebbinghaus_memory; ebbinghaus_memory({'action': 'sleep', 'prune_mode': 'archive', 'rehearse_threshold': 0.45, 'forget_threshold': 0.08, 'salience_keep_threshold': 0.7, 'limit': 200})"
```

## Verification
```bash
hermes ebbinghaus_memory action=stats
```