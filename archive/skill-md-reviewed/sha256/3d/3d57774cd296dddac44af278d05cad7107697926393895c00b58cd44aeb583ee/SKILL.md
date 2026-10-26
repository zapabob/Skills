---
name: hermes-cron-security-automation
description: Automate security audits and dev workflows via cron and MoA.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Cron, Security, Automation, MoA, Delegation]
---

# Hermes Cron Security Automation

Automates 8 repetitive development/security tasks using Hermes cron jobs, MoA free-tier routing, and Codex/Claude Code delegation. Saves ~39.5h/month and reduces token costs by ~$84/month.

**Does NOT cover:** One-off manual tasks, non-Hermes environments, or tasks requiring interactive user input.

## When to Use

- Setting up recurring security audits (daily/weekly)
- Automating Dependabot PR merges for non-security updates
- Daily vulnerability scanning across repos
- Social memory sync from LINE/Telegram/Discord
- Daily dev summaries written to Obsidian
- Meal reminders to prevent missed meals
- PR review comment fix delegation to Codex/Claude Code
- MoA orchestrator rotation for token efficiency

## Prerequisites

- Hermes Agent installed with MoA provider configured
- `gh` CLI authenticated for target repos (moeru-ai/airi, hermes-agent)
- Obsidian vault at `Hermes-Memory-Wiki/daily/` for daily summaries
- Telegram bot configured for `chat_id: 7201110294` (security audit delivery)
- Skills installed: `dependabot-security-fix`, `sec-audit`, `memory-social-sync-patterns`, `line-personal-bridge`, `memory-maintenance`, `obsidian-external-memory-journaling`, `github-pr-workflow`, `code-review`
- Windows environment (uses `py -3` for Python, PowerShell for notifications)

## How to Run

All cron jobs are created via `cronjob` tool. The MoA rotation script runs twice daily via existing cron `a8cde7947d9c`.

```bash
# Verify MoA config after rotation
py -3 -c "
import yaml
from pathlib import Path
config = yaml.safe_load((Path.home() / '.hermes' / 'config.yaml').read_text(encoding='utf-8'))
moa = config.get('moa', {})
preset = moa.get('presets', {}).get('hakuapulse-orchestrator', {})
print('provider:', config.get('model',{}).get('provider'))
print('aggregator:', preset.get('aggregator'))
print('refs:', len(preset.get('reference_models', [])))
"
```

## Quick Reference

| Cron Job | Schedule | Skills | Delivery |
|----------|----------|--------|----------|
| meal-reminder | 0 7,12,18,20 * * * | — (no_agent) | local |
| vuln-scan-daily | 0 2 * * * | dependabot-security-fix, sec-audit | local |
| dependabot-auto-merge | 0 3 * * * | dependabot-security-fix | local |
| social-memory-sync | */30 * * * * | memory-social-sync-patterns, line-personal-bridge | local |
| daily-dev-summary-obsidian | 0 23 * * * | memory-maintenance, obsidian-external-memory-journaling | local |
| security-audit-weekly | 0 9 * * 1 | sec-audit, dependabot-security-fix | telegram:7201110294 |
| pr-review-fix-delegate | 0 */4 * * * | github-pr-workflow, code-review | local |
| moa-rotation (existing) | 0 4,16 * * * | — (script) | local |

## Procedure

### 1. Create Meal Reminder Cron (Zero Token)
```python
cronjob(action='create', name='meal-reminder', schedule='0 7,12,18,20 * * *',
  script='notify-send "🍽️ 食事の時間です" --app-name="Hermes" --category=reminder',
  no_agent=True, deliver='local')
```

### 2. Create Daily Vulnerability Scan
```python
cronjob(action='create', name='vuln-scan-daily', schedule='0 2 * * *',
  skills=['dependabot-security-fix', 'sec-audit'],
  prompt='Run daily vulnerability scan: 1) Check dependabot alerts across all repos 2) Run security audit on codebase 3) Report critical/high findings via Telegram',
  deliver='local')
```

### 3. Create Dependabot Auto-Merge (Non-Security Only)
```python
cronjob(action='create', name='dependabot-auto-merge', schedule='0 3 * * *',
  skills=['dependabot-security-fix'],
  prompt='Auto-merge dependabot PRs that are: 1) non-security updates 2) all CI checks pass 3) version bump is patch/minor only',
  deliver='local')
```

### 4. Create Social Memory Sync (30-min Interval)
```python
cronjob(action='create', name='social-memory-sync', schedule='*/30 * * * *',
  skills=['memory-social-sync-patterns', 'line-personal-bridge'],
  prompt='Summarize unread messages from LINE, Telegram, Discord channels. Extract action items and create tasks. Update Hermes memory with key decisions.',
  deliver='local')
```

### 5. Create Daily Dev Summary to Obsidian
```python
cronjob(action='create', name='daily-dev-summary-obsidian', schedule='0 23 * * *',
  skills=['memory-maintenance', 'obsidian-external-memory-journaling'],
  prompt='Generate daily development summary: 1) Collect today\'s commits, PRs, issues from all repos 2) Summarize key changes, decisions, blockers 3) Write to Obsidian Hermes-Memory-Wiki/daily/{date}.md',
  deliver='local')
```

### 6. Create Weekly Security Audit (Telegram Delivery)
```python
cronjob(action='create', name='security-audit-weekly', schedule='0 9 * * 1',
  skills=['sec-audit', 'dependabot-security-fix'],
  prompt='Run weekly Hermes Agent security audit: 1) Dependency vulnerability scan (npm/pip/go) 2) Code security scan (secrets, patterns) 3) Dependabot alert review 4) Deliver markdown report to Telegram',
  deliver='telegram:7201110294')
```

### 7. Create PR Review Fix Delegation (4-hour Interval)
```python
cronjob(action='create', name='pr-review-fix-delegate', schedule='0 */4 * * *',
  skills=['github-pr-workflow', 'code-review'],
  prompt='Check for open PRs with unresolved review comments. For each PR: 1) Fetch review comments via gh API 2) Delegate fix generation to Codex/Claude Code via delegate_task 3) Apply patches 4) Push updates 5) Notify user for final review. Only process PRs in moeru-ai/airi and hermes-agent repos. Use MoA free-tier models.',
  deliver='local')
```

### 8. Run MoA Orchestrator Rotation (Twice Daily)
```bash
# Already scheduled as cron a8cde7947d9c (0 4,16 * * *)
# Manual run:
py -3 scripts/daily_moa_orchestrator_rotation.py
```
This rotates aggregator round-robin (gpt-5.6-luna → grok-4.5 → gemini-3.1-flash-lite) and shuffles 5 free reference models daily.

### 9. Delegate PR Fix Generation (Ad-hoc)
```python
delegate_task(context='User wants to automate PR指摘修正 (maintainer review comment fixes) by delegating to Codex/Claude Code. They do the review only. Repository: moeru-ai/airi (monorepo with Electron, Vue, TypeScript). Need a reusable skill or documented pattern.',
  goal='Create a reusable skill/pattern for PR review comment fixes: when maintainer leaves review comments on a PR, delegate to Codex/Claude Code to generate fixes, then you only review the generated changes. Document the exact workflow and commands.',
  role='leaf')
```

## Pitfalls

- **Windows notify-send**: `notify-send` is WSL-only. For native Windows toast, use PowerShell `New-BurntToastNotification` (requires BurntToast module) or Python `ctypes.windll.user32.MessageBoxW`.
- **MoA live discovery**: The rotation script's `resolve_real_id` and `liveness` probes may fail if provider catalogs are unreachable; it falls back to static models.
- **Telegram delivery**: Requires valid `chat_id` and bot token in Hermes config. Test with a manual message first.
- **Obsidian path**: Ensure `Hermes-Memory-Wiki/daily/` exists in your vault; the cron writes `{date}.md` files there.
- **Delegation limits**: `max_concurrent_children=3`, `max_spawn_depth=1`. Nested delegation requires config change.
- **Cron overlap**: 4-hour PR check + daily scans may overlap; `deliver='local'` prevents notification spam.
- **Skill dependencies**: All referenced skills must be installed (`skill_view` to verify) before cron runs.

## Verification

```bash
# 1. List all created cron jobs
cronjob(action='list') | jq '.jobs[] | select(.name | test("meal-reminder|vuln-scan|dependabot-auto|social-memory|daily-dev|security-audit|pr-review")) | {name, schedule, skills, state}'

# 2. Verify MoA config updated
py -3 -c "
import yaml
from pathlib import Path
c = yaml.safe_load((Path.home() / '.hermes' / 'config.yaml').read_text())
m = c.get('moa', {}).get('presets', {}).get('hakuapulse-orchestrator', {})
print('Aggregator:', m.get('aggregator'))
print('Refs:', len(m.get('reference_models', [])))
assert c.get('model',{}).get('provider') == 'moa'
assert c.get('model',{}).get('default') == 'hakuapulse-orchestrator'
print('OK')
"

# 3. Test meal reminder notification (Windows)
py -3 -c "import ctypes; ctypes.windll.user32.MessageBoxW(0, '🍽️ テスト', 'Hermes', 0x40)"

# 4. Check next run times
cronjob(action='list') | jq '.jobs[] | select(.enabled) | {name, next_run_at, last_status}'
```
All 7 jobs should show `state: scheduled`, `enabled: true`, and valid `next_run_at`.