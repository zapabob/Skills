---
name: vrchat-permission-manager
description: Grants VRChat perms while running, auto-revokes on close.
category: devops
---

# VRChat Permission Manager Skill

Use when managing VRChat runtime permissions with state-based control: grant permissions when VRChat is running, automatically revoke when closed.

## Triggers & When to Use

Use this skill when you need to:
- Automatically grant VRChat permissions only while the application is running
- Revoke all VRChat permissions when the application closes
- Manage avatar bone control, chat message sending, and TTS/VOICEVOX permissions as a unified state
- Integrate with Hermes heartbeat cron for continuous monitoring

## When NOT to Use

- For one-shot VRChat posting tasks (use `vrchat-cron-management` instead)
- When you need specific content posting (use `daily_vrchat_post` or `vrchat_daily_tweet`)
- For X/Twitter integration (use `lm-twitterer-operations`)

## Permission States

| State | Description | Automatic Actions |
|-------|-------------|-------------------|
| `vrchat_running` | VRChat process detected running | Grant: chat send, avatar bones, TTS/VOICEVOX |
| `vrchat_closed` | VRChat process not running | Revoke: all permissions, clean up OSC state |
| `unknown` | Check in progress / ambiguous | No state change, continue monitoring |

## How It Works

### Monitoring Cycle

1. **Heartbeat check** (every 60-120 seconds): Detect VRChat process existence
2. **State transition**: If state changes, execute appropriate actions
3. **OSC messaging**: Send `/avatar/parameters` or `/chatbox` commands to VRChat
4. **Log state change**: Record permission on/off events for auditing

### Granted Permissions (when VRChat running)

- **Chat message sending**: VRChat chatbox input enabled
- **Avatar bone control**: `/avatar/parameters` OSC writes for bone movement
- **VOICEVOX/TTS**: `irodori-TTS / voice=hakua` 発話経路有効
- **Chatbox focus**: テキスト入力欄へのフォーカス権限

### Revoked Permissions (when VRChat closed)

- All OSC parameter writes blocked
- Chat input disabled
- TTS pipeline paused/disabled
- State reset for next VRChat session

## Prerequisites

- VRChat installed and running (Windows or Linux)
- Hermes Agent desktop app running
- OSC Bridge configured and connected to VRChat
- VOICEVOX/Hakua TTS server operational
- `tasklist` (Windows) or `ps` (Linux) available in PATH

## How to Run

### As a cron job (recommended)

```bash
hermes cron create \
  --name "vrchat-permission-manager" \
  --schedule "60s" \
  --prompt "$HOME/.hermes/scripts/vrchat-permission-manager.sh" \
  --skills ["vrchat-permission-manager"]
```

### Manual execution

```bash
hermes cron run \
  --name "vrchat-permission-manager" \
  --prompt "Check VRChat status and manage permissions"
```

## Script Logic

The script performs the following:

1. Detect VRChat process using `tasklist` (Windows) or `ps` (Linux)
2. Load previous permission state from JSON file
3. If state changed from closed→running: Send OSC messages to enable chat, bones, TTS
4. If state changed from running→closed: Send OSC messages to disable everything and reset state
5. Save current state to JSON for next cycle reference
6. Output current status for cron job logging

## State Transition Events

| Trigger | Action |
|---------|--------|
| VRChat starts | Enable chat, bone control, TTS; log "permissions granted" |
| VRChat closes | Disable all; log "permissions revoked" |
| Check interval | No change if state unchanged |

## Related Skills

- `vrchat-cron-management` - VRChat cron job management
- `irodori-tts-windows-startup` - Irodori TTS Windows startup
- `hermes-gateway-line-platform` - Hermes LINE gateway operations

## Session Notes

This skill was created to address the user's requirement: Grant VRChat permissions only while the application is running, automatically revoke when closed, including avatar bone control and VOICEVOX/TTS permissions. The monitoring cycle integrates with Hermes cron for continuous background operation.