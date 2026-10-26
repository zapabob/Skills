---
name: osint-fusion-operations
description: Automated OSINT fusion reporting with multi-source intelligence platforms (World Monitor, Shinka, etc.) including tier selection, dependency management, scheduled delivery, and multi-channel distribution.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [osint, fusion, worldmonitor, shinka, cron, telegram, automated-reporting]
category: research
metadata:
  hermes:
    tags: [osint, fusion, worldmonitor, shinka, cron, telegram, automated-reporting]
    category: research
    related_skills: [deep-research-specialist, deepresearch-defense-standard]
    config:
      osint.fusion.default_tier: free
      osint.fusion.shinka_dependencies: ["google-genai"]
      osint.fusion.report_dir: "~/.hermes/worldmonitor-osint/reports"
      osint.fusion.default_schedule: ["0 23 * * *", "0 3 * * *", "0 11 * * *"]
      osint.fusion.worldmonitor_sidecar: "http://127.0.0.1:46123"
---

# OSINT Fusion Operations

This skill covers automated OSINT (Open Source Intelligence) fusion reporting using multi-source intelligence platforms like **World Monitor** and **ShinkaEvolve**, including tier selection, dependency management, scheduled report generation, and multi-channel delivery (Telegram, LINE, Discord, etc.).

## When to Use

- Generating periodic OSINT fusion reports on geopolitical, security, or domain-specific topics
- Configuring World Monitor + Shinka fusion pipelines with appropriate tier selection
- Setting up cron jobs for automated report generation and delivery
- Troubleshooting dependency issues in Shinka MILSPEC evaluation
- Multi-channel report distribution via Hermes messaging gateway

## Prerequisites

- Hermes Agent with `worldmonitor-osint` command available (built-in)
- For Shinka MILSPEC evaluation (`--wm-tier auto` or `pro`): **`pip install google-genai`** (NOT `google-generativeai` — deprecated since 2024, end-of-life)
- World Monitor local sidecar running at `http://127.0.0.1:46123` for `--wm-tier auto` (Pro features via local API)
- Configured messaging channels (Telegram, LINE, Discord) for `deliver: "all"`
- `cron` toolset enabled for scheduled jobs

## How to Run

### Quick Report (Free Tier)

```bash
hermes worldmonitor-osint fusion "日本の安全保障" --wm-tier free --source-mode real --save
```

- Completes in ~30-60 seconds
- Uses World Monitor Free tier (news digest, GPS jamming, OREF alerts)
- Skips Shinka MILSPEC evaluation
- Saves JSON report to `~/.hermes/worldmonitor-osint/reports/`

### Full Report (Auto/Pro Tier)

```bash
hermes worldmonitor-osint fusion "経済安全保障" --wm-tier auto --source-mode real --save
```

- Requires `google-generativeai` package for Shinka evaluation
- Includes MILSPEC scoring and scenario evolution
- Longer execution time (2-5 minutes typical)

### Scheduled Reports (Cron)

```bash
# Morning, noon, evening delivery to all channels
hermes cron create \
  --name "OSINT融合レポート 日本の安全保障 08:00" \
  --schedule "0 8 * * *" \
  --prompt 'hermes worldmonitor-osint fusion "日本の安全保障" --wm-tier free --source-mode real --save' \
  --deliver all

hermes cron create \
  --name "OSINT融合レポート 日本の安全保障 12:00" \
  --schedule "0 12 * * *" \
  --prompt 'hermes worldmonitor-osint fusion "日本の安全保障" --wm-tier free --source-mode real --save' \
  --deliver all

hermes cron create \
  --name "OSINT融合レポート 日本の安全保障 20:00" \
  --schedule "0 20 * * *" \
  --prompt 'hermes worldmonitor-osint fusion "日本の安全保障" --wm-tier free --source-mode real --save' \
  --deliver all
```

## Quick Reference

| Command | Tier | Shinka | Time | Use Case |
|---------|------|--------|------|----------|
| `--wm-tier free` | Free | ❌ | ~30-60s | Daily ops, quick briefings |
| `--wm-tier auto` | Auto | ✅* | 2-5 min | Deep analysis, MILSPEC scoring (uses local sidecar) |
| `--wm-tier pro` | Pro | ✅ | 2-5 min | Full pro features (requires auth) |
| `--source-mode mock` | Any | ✅* | ~30-60s | **Testing without API calls** (mock data) |
| `--llm-summary` | Any | Optional | +10-30s | **Japanese executive summary via Hermes LLM** |

*Requires `google-genai` package (NOT deprecated `google-generativeai`)

### ⚠️ Cron Timezone: JST vs UTC

**Cron schedules run in UTC.** For JST (UTC+9) delivery times, convert:

| JST Target | UTC Cron Schedule |
|------------|-------------------|
| 08:00 JST | `0 23 * * *` (previous day) |
| 12:00 JST | `0 3 * * *` |
| 20:00 JST | `0 11 * * *` |

## Procedure

### 1. Verify Dependencies

```bash
# Check Shinka dependency (google-genai, NOT google-generativeai)
py -3 -c "import google.genai; print('OK: google-genai')"
# If ModuleNotFoundError:
pip install google-genai

# Verify World Monitor local sidecar (for --wm-tier auto)
curl -s http://127.0.0.1:46123/health
```

### 2. Test Single Run

```bash
# Free tier (fast, no deps, real data)
hermes worldmonitor-osint fusion "your_topic" --wm-tier free --source-mode real --save

# Auto tier (full, needs google-genai, uses local sidecar)
hermes worldmonitor-osint fusion "your_topic" --wm-tier auto --source-mode real --save

# **Mock mode for testing (no API calls, fast)**
hermes worldmonitor-osint fusion "your_topic" --wm-tier auto --source-mode mock --llm-summary --save

# With Japanese LLM summary (uses Hermes LLM, not google-genai)
hermes worldmonitor-osint fusion "your_topic" --wm-tier free --source-mode real --llm-summary --save
```

### 3. Configure Scheduled Delivery (JST → UTC)

```bash
# List existing cron jobs
hermes cron list

# Create scheduled jobs for JST delivery (convert to UTC!)
# 08:00 JST = 23:00 UTC previous day
hermes cron create --name "OSINT Report <topic> 08:00 JST" \
  --schedule "0 23 * * *" \
  --prompt 'hermes worldmonitor-osint fusion "<topic>" --wm-tier free --source-mode real --save' \
  --deliver all

# 12:00 JST = 03:00 UTC
hermes cron create --name "OSINT Report <topic> 12:00 JST" \
  --schedule "0 3 * * *" \
  --prompt 'hermes worldmonitor-osint fusion "<topic>" --wm-tier free --source-mode real --save' \
  --deliver all

# 20:00 JST = 11:00 UTC
hermes cron create --name "OSINT Report <topic> 20:00 JST" \
  --schedule "0 11 * * *" \
  --prompt 'hermes worldmonitor-osint fusion "<topic>" --wm-tier free --source-mode real --save' \
  --deliver all
```

### 4. Verify Delivery

- Reports saved to `~/.hermes/worldmonitor-osint/reports/YYYYMMDDTHHMMSSZ_<topic>.json`
- Delivered to all connected channels (Telegram, LINE, Discord) via `deliver: all`
- Telegram requires at least one user message to bot for chat ID detection

## Pitfalls

### Shinka Hangs on Missing/Deprecated Dependency

**Symptom**: `hermes worldmonitor-osint fusion --wm-tier auto` runs >10 min with no output, or fails with `FutureWarning: All support for the google.generativeai package has ended`

**Cause**:
- Shinka MILSPEC evaluation tries to import deprecated `google.generativeai` (end-of-life, no updates since 2024)
- The process hangs instead of failing fast, or crashes with import error

**Fix**:
1. Install the **new** package: `pip install google-genai`
2. **But**: ShinkaEvolve-OSINT codebase itself must be updated to use `google.genai` instead of `google.generativeai` — this is an upstream fix needed in `shinka/llm/embedding.py` and `shinka/core/config.py`
3. **Workaround for now**: Use `--wm-tier free` (skips Shinka) or `--source-mode mock` for testing. Free tier provides World Monitor risk scores, GPS jamming, OREF alerts, news digest without Shinka evaluation.

### Telegram Delivery Not Working

**Symptom**: Cron job runs but no Telegram message

**Cause**: `channel_readiness_check` shows `telegram.liveRoundtripReady: false` and `candidateTargets: {directChats: 0, groupChats: 0}`

**Fix**: Send a message to the Telegram bot first (e.g., `/start`) to register chat ID. Subsequent cron deliveries will work.

### Cron Job Output Truncation

**Symptom**: Large JSON reports not fully delivered

**Cause**: Messaging platforms have message size limits (Telegram: 4096 chars)

**Fix**: Reports are saved as files; delivery sends summary. Access full report via saved JSON file at `~/.hermes/worldmonitor-osint/reports/`.

### Cron Timezone Mismatch (JST vs UTC)

**Symptom**: Reports delivered at wrong local time (e.g., 8 AM JST scheduled but arrives at 5 PM JST)

**Cause**: Cron schedules execute in **UTC**, but user thinks in JST (UTC+9).

**Fix**: Convert JST → UTC before creating cron:
- 08:00 JST → `0 23 * * *` (23:00 UTC previous day)
- 12:00 JST → `0 3 * * *`
- 20:00 JST → `0 11 * * *`

### World Monitor Local Sidecar Not Running

**Symptom**: `--wm-tier auto` fails with connection refused to `http://127.0.0.1:46123`

**Cause**: Auto tier requires World Monitor sidecar (koala73/worldmonitor) running locally for Pro features.

**Fix**: Start sidecar before running auto tier, or use `--wm-tier free` which works without sidecar.

## Verification

```bash
# Check report saved
ls -la ~/.hermes/worldmonitor-osint/reports/

# Verify cron jobs (note: times shown in local TZ)
hermes cron list

# Test channel readiness
hermes channel-readiness-check

# Verify Shinka dependency (google-genai)
py -3 -c "import google.genai; print('google-genai OK')"

# Verify World Monitor sidecar
curl -s http://127.0.0.1:46123/health
```

### Mock Mode Quick Test

```bash
# Fast test without API keys or sidecar
hermes worldmonitor-osint fusion "テスト" --wm-tier auto --source-mode mock --llm-summary --save
# Completes in ~30s, generates report with mock risk scores + LLM Japanese summary
```

## References

- `references/worldmonitor-tier-comparison.md` — Tier feature matrix and performance characteristics
- `references/shinka-dependency-fix.md` — Shinka MILSPEC dependency resolution guide
- `references/cron-delivery-patterns.md` — Multi-channel cron delivery configuration patterns
- `templates/osint-fusion-cron.yaml` — Cron job template for common schedules
- `scripts/verify-shinka-deps.py` — Quick dependency verification script