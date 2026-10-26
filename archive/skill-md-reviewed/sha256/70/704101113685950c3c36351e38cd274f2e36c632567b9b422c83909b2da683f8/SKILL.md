---
name: a2a-heartbeat-cron
description: Sends A2A heartbeat messages to main agent every 3 hours via cron with 600s wait time and feedback collection
version: 1.0.0
author: Hermes
platforms: [windows]
tags: [A2A, Cron, Heartbeat, Automation]
---

# A2A Heartbeat Cron Skill

## Description
Sends A2A heartbeat messages to the main agent every 3 hours via cron, with 600-second wait time and feedback collection. This skill automates regular A2A communication for status checking and task coordination between bot mode and the main agent.

## When to Use
- When you need periodic A2A heartbeats to maintain agent connectivity
- When you want to collect status/feedback from the main agent on a schedule
- When you need token-efficient regular check-ins without full conversations
- When setting up A2A-based monitoring or keepalive patterns

## Trigger Conditions
- Set up when A2A server is running and main-agent peer is registered
- Cron schedule: `0 */3 * * *` (every 3 hours)
- Requires A2A tools available in platform_toolsets

## Configuration

### Cron Job Creation
```
hermes cron create "0 */3 * * *" \
  --script "a2a_heartbeat.py" \
  --no-agent \
  --name "a2a-heartbeat-3h" \
  --deliver "origin"
```

### Required Script (`~/.hermes/scripts/a2a_heartbeat.py`)
The script must:
1. Use `a2a_call` tool to send heartbeat message to `main-agent`
2. Capture and save feedback results
3. Handle errors gracefully
4. Exit with code 0 on success

## A2A Call Pattern
```python
tool_call({
    "name": "a2a_call",
    "arguments": {
        "agent": "main-agent",
        "message": "💓 A2A Heartbeat from bot mode - checking status and collecting feedback. Please respond with current status, any pending tasks, and system health metrics."
    }
})
```

## Script Details

### `a2a_heartbeat.py`
- **Location**: `~/.hermes/scripts/a2a_heartbeat.py`
- **Mode**: no-agent (script stdout delivered directly)
- **Timeout**: 600 seconds (configured in script or cron options)
- **Delivery**: origin (current chat session)
- **Output**: JSON feedback saved to `~/.hermes/a2a_results/`

### Script Responsibilities
1. Send A2A call to main-agent with status request message
2. Parse the response
3. Save result JSON to `~/.hermes/a2a_results/`
4. Print summary to stdout (delivered to chat via no-agent mode)
5. Handle connection errors gracefully

## Error Handling
- If A2A call fails: report error via stdout, exit code 1
- If peer unreachable: include timeout info in feedback
- If response malformed: log warning, continue with partial feedback
- Script should always produce some stdout output (even if just "heartbeat failed")

## MoA Integration
- Can be paired with MoA free-tier model routing
- Aggregator can rotate between models for token efficiency
- Reference models can be configured in `~/.hermes/config.yaml` under `moa.presets.hakuapulse-orchestrator.reference_models`

## Example Cron Job
```bash
# Creates a 3-hourly heartbeat job
hermes cron create "0 */3 * * *" \
  --script "a2a_heartbeat.py" \
  --no-agent \
  --name "a2a-heartbeat-3h" \
  --deliver "origin"
```

### Next Run Calculation
- Cron schedule: `0 */3 * * *` (every 3 hours at hour 0)
- Next run: calculated based on current time, rounded to next 3-hour boundary
- Example: if current time is 14:25, next run is 15:00

## Pitfalls & Gotchas
- **Script path**: Must be relative to `~/.hermes/scripts/`, use filename only (e.g., `a2a_heartbeat.py`)
- **no-agent mode**: Script stdout is delivered verbatim; empty stdout = silent (design script to always output something)
- **A2A server**: Must be running on configured port (default 9900)
- **Peer registration**: `main-agent` must be configured in `a2a_agents` section of config.yaml
- **Timeout handling**: 600s wait time; if peer doesn't respond within 600s, script should handle gracefully
- **Delivery target**: `origin` delivers to current chat; use `local` for no delivery, `all` for fan-out

## Verification
```bash
# List cron jobs to verify
cronjob(action='list') | jq '.jobs[] | select(.name | test("a2a-heartbeat")) | {name, schedule, skills, state, next_run_at}'

# Check A2A results directory
ls -la ~/.hermes/a2a_results/

# Verify A2A server is up
curl -sS http://127.0.0.1:9900/.well-known/agent-card.json
```

## Related Skills
- `hermes-cron-security-automation` - Related cron automation patterns
- `memory-social-sync-patterns` - For social memory integration if needed
- `line-personal-bridge` - If LINE integration is desired alongside A2A

## History
- **Created**: 2026-08-18
- **Purpose**: Automate A2A heartbeats for bot mode main-agent communication
- **Version**: 1.0.0
- **Compatible with**: Hermes Agent, A2A protocol v1.0, MoA provider