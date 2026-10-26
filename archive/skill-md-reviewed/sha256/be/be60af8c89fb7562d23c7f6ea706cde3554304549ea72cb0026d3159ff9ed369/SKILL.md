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
- SitDeck `sitdeck_osint_digest` / `sitdeck_crawl` returns `Loading data feed list` or stays on `#login` — load `references/sitdeck-feed-load-wait.md` via `skill_view`

## Prerequisites

- Hermes Agent with `worldmonitor-osint` command available (built-in)
- **User-specific World Monitor boundary:** do not use the plain `worldmonitor` MCP server. Use the desktop shortcut/exe or approved non-MCP OSINT paths instead; see `references/worldmonitor-non-mcp.md`.
- For Shinka MILSPEC evaluation (`--wm-tier auto` or `pro`): **`pip install google-genai`** (NOT `google-generativeai` — deprecated since 2024, end-of-life)
  - **FIXED (2026-06-18)**: Local ShinkaEvolve-OSINT checkout at `~/Desktop/ShinkaEvolve-OSINT-main` patched to use `google.genai` SDK
  - Supports **multiple embedding providers**: Google (Gemini), NVIDIA, Codex, Nous, OpenRouter, OpenAI, Azure
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
| `--wm-tier free` | Free | ❌ | ~30-60s | **Daily ops, quick briefings (RECOMMENDED for cron)** |
| `--wm-tier auto` | Auto | ⚠️ HANGS | 2-5 min* | Deep analysis, MILSPEC scoring — **currently broken** |
| `--wm-tier pro` | Pro | ✅ | 2-5 min | Full pro features (requires auth) |
| `--source-mode mock` | Any | ❌ (bypassed) | ~30-60s | **Testing without API calls / Shinka deps** |
| `--llm-summary` | Any | Dependent | +10-30s | **Japanese executive summary — requires Shinka import chain healthy** |
| `--llm-summary` (w/ Shinka broken) | Any | ❌ | ~same | **Silent no-op: `shinka_llm: {}` — no summary produced** |

*\*Auto tier currently hangs on Shinka import chain (`importable: false`). Use `mock` mode or `free` tier for reliable execution.*

### Supported Embedding Providers (via `shinka/llm/embedding.py`)

| Provider | Models | Auth Env Var |
|----------|--------|--------------|
| **Google (Gemini)** | `gemini-embedding-exp-03-07`, `gemini-embedding-001` | `GEMINI_API_KEY` / `GOOGLE_API_KEY` |
| **NVIDIA** | `nvidia/nv-embedqa-e5-v5`, `nvidia/nv-embedqa-mistral-7b-v2` | `NVIDIA_API_KEY` / `NGC_API_KEY` |
| **Codex** | `codex-embedding` | `CODEX_API_KEY` / `OPENAI_API_KEY` |
| **Nous** | `nous-embedding`, `nous-hermes-embedding` | `NOUS_API_KEY` |
| **OpenRouter** | Any `/` prefixed (e.g., `openai/text-embedding-3-small`) | `OPENROUTER_API_KEY` |
| **OpenAI** | `text-embedding-3-small`, `text-embedding-3-large` | `OPENAI_API_KEY` |
| **Azure OpenAI** | `azure-text-embedding-3-small`, `azure-text-embedding-3-large` | `AZURE_OPENAI_API_KEY` |

### ⚠️ Cron Timezone: Local Time (JST) — NOT UTC

### About Path Size

| JST Target | Cron Schedule (LOCAL) |
|------------|----------------------|
| 08:00 JST | `0 8 * * *` |
| 12:00 JST | `0 12 * * *` |
| 20:00 JST | `0 20 * * *` |

**Evidence**: Cron jobs created with `0 8 * * *` show `next_run_at: "2026-06-19T08:00:00+09:00"` — matching JST exactly. The previous UTC conversion guidance was incorrect for Hermes cron.

### Report Save Path: Profile-Dependent

When running under a **named Hermes profile** (e.g., `--profile job-recruiter` or via `hermes cron` that uses a non-default profile), reports save to:

```
~/.hermes/profiles/<profile>/worldmonitor-osint/reports/
```

When running under the **default profile** (no `--profile` flag), reports save to:

```
~/.hermes/worldmonitor-osint/reports/
```

Both paths use the `YYYYMMDDTHHMMSSZ_<topic>.json` naming convention. Cron jobs that verify saved output must check the correct path — checking the wrong one will show no new files and the agent may falsely conclude the run failed.

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

### 3. Configure Scheduled Delivery (LOCAL TIME = JST)

```bash
# List existing cron jobs before changing anything
hermes cron list

# For Telegram-first MILSPEC/PDB reports, prefer ONE canonical morning+evening pair.
# Avoid deliver=all unless the user explicitly wants multi-channel delivery.
# 08:00 JST
hermes cron create --name "osint-agent-morning MILSPEC markdown to Telegram" \
  --schedule "0 8 * * *" \
  --deliver telegram \
  --prompt '<self-contained prompt that calls shinka_osint_briefing + gov_feed_digest + mhlw_designated_check, saves .md, and returns Telegram-readable Markdown>'

# 18:00 JST
hermes cron create --name "osint-agent-evening MILSPEC markdown to Telegram" \
  --schedule "0 18 * * *" \
  --deliver telegram \
  --prompt '<same pattern, evening slot>'
```

When repairing existing OSINT cron, pause overlapping legacy jobs (`OSINT融合レポート`, `wm-osint-fusion-*`, `wm-osint-pdb-*`) so the user receives one clear morning/evening report instead of duplicate or conflicting outputs. See `references/milspec-telegram-cron-remediation.md` for the full remediation pattern and prompt skeleton.

### `worldmonitor_fusion_report` Tool (Working Primary Path)

The `worldmonitor_fusion_report` tool (from the `worldmonitor_osint` plugin) is the **working primary fusion tool** — it succeeded in this session where `osint_agent_brief` previously failed with AttributeError.

**Verified invocation (2026-08-03 evening slot):**
```json
{
  "slot": "evening",
  "topic": "日本の安全保障と世界情勢",
  "wm_tier": "free",
  "include_sitdeck": true,
  "include_mhlw": true,
  "include_wm_free": true,
  "llm_summary": true
}
```

**Returned structure:**
- `success: true`
- `generated_at`: ISO timestamp
- `worldmonitor`: { `success`, `tier: "free_web"`, `focus: "japan_security"`, `sections: {gpsjam, oref_alerts, version, app_shell}`, `errors: [news_digest 401]`, `pro_only_skipped: [country_risk, country_intel_brief, regional_brief, risk_scores]`, `news_headlines: []` }
- `shinka_milspec`: { `success: true`, `scenario_count: 3`, `average_score: 0.0`, `runs: [...]` — **all blocked by policy** }
- `shinka_llm`: provider resolution info (openai-codex/gpt-5.6-sol)
- `primary_sources`: egov-law MCP hint
- `methodology`: fusion description

**Key findings:**
- **World Monitor free tier**: GPSJAM (global, 1038 High hexes), OREF alerts (0 in 24h), app shell metadata. **news_digest returns 401 "API key required" even on free web endpoint** — treat as credentials constraint, not "no news".
- **Shinka MILSPEC**: All 3 test scenarios (`japan_russia_military_overview`, `national_security_framework`, `cyber_defense_posture`) blocked with `"scenario_id '...' is not in the permitted Shinka OSINT policy"`. Permitted domains include `japan_russia`, `national_security`, `cyber_defense` but specific scenario IDs must be registered. `shinka_osint_list_scenarios` returns 0 scenarios for `milspec_security_jp` example.
- **LLM summary**: `shinka_llm.resolved.provider_id: "openai-codex"`, `model: "gpt-5.6-sol"` — but `llm_summary: true` did not produce a `summary_ja` field in output (may require Shinka import chain healthy).
- **Primary sources**: Points to `egov-law` MCP server for Japanese legal citations.

### Direct `osint_agent_brief` Failure Fallback

When the integrated `osint_agent_brief` plugin is exposed but fails at runtime (for example, a serialization error such as `AttributeError: 'NoneType' object has no attribute '__dict__'`), do not fabricate a merged report and do not silently retry indefinitely. **Do not re-call with identical arguments after the first TOOL_RUNTIME failure** (loop warning / wasted turns). Preserve the failed call as a collection constraint, then use this bounded fallback:

1. Call `osint_agent_status` if the deferred tool surface is healthy; if `tool_call` bridge also fails, skip and go to step 3. Note `reports_dir` when available — osint_agent plugin: `~/.hermes/osint-agent/briefs` (Windows: `C:\\Users\\<user>\\.hermes\\osint-agent\\briefs`), **distinct** from `worldmonitor-osint/reports`.
2. Optional: `osint_agent_multilayer_collect` with the **same topic** (no `fetch_wm_free` argument). Expect WM Free **HTTP 401 "API key required"** often even on free web — credentials constraint, not "no news".
3. Execute web-search queries in parallel: `site:mod.go.jp`, `site:mhlw.go.jp`, `site:npa.go.jp`, `site:jma.go.jp`, `site:mofa.go.jp`, `site:kantei.go.jp`.
4. **Body fetch preference (2026-08-06 evening verified):**
   - If `web_extract` returns `BILLING_ERROR` / 402 → **stop extract retries**; use terminal `curl -sL -A "Mozilla/5.0"` + HTML strip.
   - **JMA / NPA / MHLW HTML** usually return real bodies via curl.
   - **`mod.go.jp`** often hits Cloudflare (`Just a moment...`) → tag `WAF_CHALLENGE`; use search title/date + secondary reprint (`j-defense.ikaros.jp/docs/mod/*`) labeled **代替取得** (統幕転載). Never present reprint as direct MOD HTML.
   - MOFA/METI: Access Denied or stale 404 → rediscover URL; do not invent.
5. Keep verified facts, analysis, and uncertainty in separate sections. Lead with a **収集ステータス** table listing TOOL_RUNTIME / BILLING_ERROR / WAF / primary OK. Explicitly state which requested layers (SitDeck, MHLW, WM Free) returned no content or failed.
6. Full curl/WAF recipe: `references/evening-jp-gov-curl-waf-2026-08-06.md` (also see `references/jma-primary-curl-endpoints.md`).

A configured credential or successful readiness check is not evidence that SitDeck or MHLW content was actually collected. Distinguish a World Monitor API-key/HTTP error from an absence of news.

**Verified end-to-end (2026-07-31, morning AND evening slots, topic=日本の安全保障と世界情勢):** `osint_agent_brief` failed with the AttributeError in both runs; the 5-step fallback above produced complete Telegram-ready Japanese Markdown briefs (収集ステータス表 → 確認済み事実 by agency → 分析 → 不確実性) saved to `~/.hermes/osint-agent/briefs/osint_brief_2026-07-31_morning.md` and `osint_brief_2026-07-31_evening_fallback.md`. This confirms the fallback is sufficient on its own without the integration tool.

Evening-slot deltas (verified 2026-07-31 evening, both runs):
1. CLI brief stdout piped through `tail` may show only the L1–L6 collection-plan block — the real report is the saved `<ts>_evening_<topic>.md` in the briefs dir. Verify via the file, never stdout. (Second run's `tail -60` did show the full brief — treat stdout as best-effort, the file as truth.)
2. A sibling process may drop compose artifacts (`evening_YYYYMMDD.md`, `compose_evening.py`) into the same briefs dir — they are secondary-source leads (cite NHK/Yahoo) and must be verified before inclusion (e.g. 国家情報局 7/31設置 was re-confirmed via NHK/mainichi/yomiuri/TBS searches on the second run).
3. JMA typhoon detail (`data.jma.go.jp/multi/cyclone/cyclone_detail.html?id=NN&lang=jp`) yields exact 実況/予報 tables (pressure, wind, track) and the JMA 熊本地震 portal (`jma.go.jp/jma/menu/<id>.html`) carries the official 地震概要 + 今後の見通し — both extract cleanly via web_extract. The generic quake index `jma.go.jp/jp/quake/` is DEAD (auto-redirects to `jma.go.jp/bosai/`); go straight to the portal/event pages instead.
4. Manual fallback brief filename convention: `osint_brief_YYYY-MM-DD_evening.md` (plain name, no `_fallback` suffix — an earlier run used `..._evening_fallback.md`; use the plain name going forward). Second evening run produced a full 6,994-byte brief plus a 1,004-char Telegram body (≤1200 target) from this recipe alone.

**Second verification (same day, later run; third run = evening slot 18:41 JST):** the CLI `hermes osint-agent brief --slot morning|evening --topic ... --wm-tier free --source-mode real --cron-stdout` **succeeds even while the tool-side `osint_agent_brief` fails** (different code path) and saves `<ts>_<slot>_<topic>.json/.md` to the same briefs dir. However its layers are mostly empty (WM Free 401, MHLW 新規項目なし, Shinka score 0.0, SitDeck skipped) — the report substance came from the parallel primary-source web harvest (mod.go.jp/js/press/, kantei kaiken transcript, JMA earthquake/typhoon pages, npa.go.jp/newlyarrived). Treat the CLI output as a layer-provenance skeleton, not the finished brief. Full recipe: `references/morning-brief-fallback-recipe.md`.

### Agent-Cron CLI Fallback for MILSPEC/PDB Markdown

When the user asks a scheduled agent to call `shinka_osint_briefing`, `gov_feed_digest`, and `mhlw_designated_check`, but those plugin tools are not exposed in the current tool surface, use the Hermes CLI equivalents instead of stopping:

```bash
# Shinka briefing equivalent; bounded timeout recommended in cron
./.venv/Scripts/python.exe -m hermes_cli.main shinka-osint briefing '日本の安全保障と世界情勢' \
  --source-mode real --max-scenarios 3 --example milspec_security_jp --save

# Fusion fallback that also saves a JSON report when Shinka real-mode is slow/fail-closed
./.venv/Scripts/python.exe -m hermes_cli.main worldmonitor-osint fusion '日本の安全保障と世界情勢' \
  --wm-tier free --source-mode real --max-scenarios 3 --save

# Primary government RSS and MHLW designated-drug monitor
# ⚠️ 'scrapling-feeds' is NOT a valid subcommand in this fork ("invalid choice" error, verified 2026-07-31).
# Use the osint-agent CLI brief instead (verified working even when the osint_agent_brief TOOL fails):
./.venv/Scripts/python.exe -m hermes_cli.main osint-agent brief --slot morning --topic '日本の安全保障と世界情勢' \
  --wm-tier free --source-mode real --cron-stdout
# Flags: --no-sitdeck / --no-mhlw disable layers (defaults ON; there are NO --include-* flags),
# --llm-summary optional, --source-mode {mock,real}, --cron-stdout prints markdown only.
# Expect mostly empty layers (WM Free 401, MHLW 新規項目なし, Shinka 0.0) — supplement with primary-source web collection.
# Full verified recipe: references/morning-brief-fallback-recipe.md
```

If Shinka real-mode fails with fail-closed source fetch errors, do **not** switch to mock scores silently. Include the failure under `検証上の制約`, report score as unavailable/0-equivalent, and still save a concise Markdown artifact under `~/.hermes/osint-agent/briefs/`. See `references/milspec-evening-cron-cli-fallback.md` for the exact fallback recipe and Telegram compression pattern.

**Direct tool path** (when plugin tools ARE available): see `references/milspec-evening-cron-direct-pattern.md` for the gov_feed_digest → web_search supplement → shinka_osint_list_scenarios lightweight check → MHLW reporting → save workflow.

### 4. Verify Delivery

- Reports saved to `~/.hermes/worldmonitor-osint/reports/YYYYMMDDTHHMMSSZ_<topic>.json`
- Delivered to all connected channels (Telegram, LINE, Discord) via `deliver: all`
- Telegram requires at least one user message to bot for chat ID detection

## Plugin Tool Invocation Pattern

OSINT plugin tools (`gov_feed_digest`, `mhlw_designated_check`, `worldmonitor_snapshot`, `sitdeck_status`, `sitdeck_crawl`, `sitdeck_osint_digest`) are **plugin-provided** — they appear in `tool_search()` results but NOT as top-level tools. The agent MUST invoke them via `tool_call(name=..., arguments=...)` wrapper:

```
tool_call(name="gov_feed_digest", arguments={"hours": 24, "max_per_feed": 5})
tool_call(name="mhlw_designated_check", arguments={"record_baseline": false, "scan_enforcement": true})
tool_call(name="worldmonitor_snapshot", arguments={"country_code": "JP", "news_lang": "en", "news_limit": 10, "region_id": "east-asia"})
```

**Do not** call them as bare function-call expressions — that will fail with "tool does not exist". Use `tool_call` with the name and arguments dictionary. If tool_call itself is not available, fall back to the Hermes CLI equivalents documented in `references/milspec-evening-cron-cli-fallback.md`.

### World Monitor Sidecar Resilience

World Monitor's local sidecar (`http://127.0.0.1:46123`) may not be running. When it is down, `worldmonitor_snapshot` still succeeds and returns data via **free web backfill**:
- News digest from Google News RSS (politics, security, military, crisis categories)
- GPS jamming / spoofing data from Wingbits
- OREF rocket/missile alerts

The sidecar-dependent endpoints (country_risk, country_intel_brief, regional_brief, risk_scores) will return connection-refused errors, but the tool's `success: true` and the obtained data is still usable for briefings. Report the sidecar failure under `## 検証上の制約` or a constraints section.

### Telegram Character Limit (1200 Max)

Telegram messages are capped at ~4096 chars but for concise daily briefings target **1200 chars or fewer**. Use this compression pattern:
1. Write the full draft first, save to file.
2. Check char count with `wc -m <file>`.
3. If >1200: strip tables (use inline `—` separators), compress multi-sentence items into single lines, remove redundant source citations, prefer `▶` headers over `##` for sub-sections.
4. Save the compressed version; the file on disk carries the full detail.

This session's original draft was 1951 chars → compressed to 1059 chars.

### CISA Feed 403 Block

All three CISA feeds (advisories, ICS, news) return HTTP 403 when fetched with polite `urllib`. Scrapling Fetcher (stealth HTTP) is not installed in this environment. Report this as a collection constraint in the briefing — do not claim "no CISA advisories exist."

**Recommended fix order:**
1. Try CISA KEV JSON first — no auth, works with plain `urllib`, covers Known Exploited Vulnerabilities (most actionable for daily briefings). See `references/cisa-json-api-fallback.md` for exact endpoints and Python snippet.
2. Install Scrapling Fetcher (`pip install scrapling-fetcher`) as a permanent stealth-HTTP solution for RSS feeds.
3. As a last resort, register for a CISA API key at https://api.cisa.gov/register for the full API surface.

### Japanese Government Feed Patterns (Weekends & Holidays)

防衛省 and デジタル庁 RSS feeds typically return **0 new entries** on weekends and Japanese national holidays. This is expected behavior — do not flag it as a collection failure. The report should note "新規0件（日曜/休日のため更新なし）" and move on.

### MHLW First-Run Flood

The first `mhlw_designated_check(record_baseline=false)` call returns **every known meeting notice and enforcement on the page** (observed: 40+ items, going back 2+ years). This is because no baseline ID is recorded to filter against. For initial cron setup, suppress historical clutter in the Telegram body by filtering to items within 90 days. For subsequent runs, set `record_baseline=true` on one dedicated run to capture the baseline, then the tool will only return genuinely new items.

## Pitfalls

### Shinka Hangs on Missing/Deprecated Dependency — **MULTIPLE FAILURE MODES (2026-07-03)**

**Symptom**: `hermes worldmonitor-osint fusion` runs >10 min with no output, or fails fast with a Python traceback in the report's `shinka_milspec.error`.

**Failure Mode A: Deprecated `google.generativeai`** (observed 2026-06-18)

**Symptom**: `FutureWarning: All support for the google.generativeai package has ended` or import error.
**Cause**: Shinka MILSPEC evaluation tried to import deprecated `google.generativeai` (end-of-life, no updates since 2024).
**Fix Applied**: Local checkout at `~/Desktop/ShinkaEvolve-OSINT-main` patched to use `google.genai` SDK.

**Failure Mode B: NumPy ≥2.5.0 + SciPy incompatibility** (observed 2026-07-03)

**Symptom**: Shinka import chain fails with:
```
UserWarning: A NumPy version >=1.23.5 and <2.5.0 is required for this version of SciPy (detected version 2.5.0)
```
Then cascades through `shinka/core/config.py` → `shinka/llm/__init__.py` → full eval failure.
**Cause**: SciPy pinned to a version incompatible with NumPy 2.5.0 on this host.
**Fix**: Downgrade NumPy:
```bash
pip install "numpy<2.5"
```

**Failure Mode C: General import chain failure** (intermittent)

**Symptom**: `shinka_osint_status` shows `importable: false`, `tool_count: 0`.
**Workaround**: Use `--wm-tier free` without `--llm-summary` for production cron jobs.

**Critical interaction with `--llm-summary`**: Even `--wm-tier free --source-mode mock --llm-summary` triggers the Shinka import chain. The `--llm-summary` flag routes through Shinka's LLM provider layer, which pulls in the full `shinka.llm` module chain. If Shinka imports fail, `shinka_llm` will be empty `{}` and NO summary is generated — the flag is silently a no-op. To confirm Shinka is healthy enough for LLM summary:
```bash
py -3 -c "import numpy; print(numpy.__version__)"   # must be <2.5
py -3 -c "from google import genai; print('genai OK')"
```

**Workaround for reliable cron output without Shinka**:
```bash
# World Monitor data only, no Shinka import at all
hermes worldmonitor-osint fusion "topic" --wm-tier free --source-mode real --save
# ~30-60 seconds, includes: news_digest, GPS jamming, OREF alerts
# No --llm-summary flag → no Shinka import attempted
```

---

### SitDeck digest is chrome-only / still loading

**Symptom**: `sitdeck_osint_digest` / `sitdeck_crawl` returns `success: true` but body is `SITUATION DECK` + `Loading data feed list N%`, `final_url` is `#login`, and only `/api/auth/me` (plus billing/notifications) was captured.

**Cause**: The SPA shows logo chrome before feeds finish. Session reuse used to skip post-login wait; wait-on-`SITUATION` returns too early. `headless=false` does not fix this.

**Fix**: Reject that payload. Open `https://app.sitdeck.com/` (not `#login`), wait until `Loading data feed list` is gone (up to ~90s), then extract. Invoke `scripts/sitdeck_extended_wait_crawl.py` through the `terminal` tool. Full recipe: `references/sitdeck-feed-load-wait.md` (load with `skill_view`). Label SitDeck text as dashboard extract, not verified fact.

### Telegram Delivery Not Working

**Cause**: `channel_readiness_check` shows `telegram.liveRoundtripReady: false` and `candidateTargets: {directChats: 0, groupChats: 0}`

**Fix**: Send a message to the Telegram bot first (e.g., `/start`) to register chat ID. Subsequent cron deliveries will work.

### OSINT Cron Delivery Fails or Duplicates

**Symptoms**:
- `last_delivery_error` mentions a platform not configured, or `deliver: all` fans out to channels the user did not ask for.
- Several OSINT jobs run around the same time and produce duplicate reports.
- Direct script/no-agent jobs produce raw plugin output, hang, or fail to generate the requested Markdown structure.

**Fix**:
1. `hermes cron list` and identify all OSINT job families.
2. Keep a single canonical pair for `osint-agent-morning` and `osint-agent-evening`.
3. Set `deliver: telegram` for Telegram-requested reporting; do not use `all` unless explicitly requested.
4. Prefer an agent-driven self-contained prompt that calls the OSINT tools, saves a `.md` artifact, and returns a concise Telegram Markdown summary.
5. Pause overlapping legacy `worldmonitor-osint fusion`, `wm-osint-fusion-*`, and `wm-osint-pdb-*` jobs.

See `references/milspec-telegram-cron-remediation.md`.

### OSINT Cron Provider Timeout / Free-Tier Rotation

When a scheduled OSINT/PDB job fails with provider timeout or exhausted fallback chain, first remove unnecessary LLM dependency from the cron path instead of only increasing retries. For routine WorldMonitor/PDB reports, convert the job to `no_agent: true` and run a deterministic script that calls `worldmonitor-osint situation-report --slot <morning|evening> --cron-stdout`; validate the script directly before reporting success. Route delivery to the requested concrete channel (usually `telegram:<chat_id>`) rather than `all`, so Discord/LINE/Photon delivery failures do not mark a successful report as failed.

If the user asks that async subagents use free quota, configure delegation via `hermes config set delegation.provider opencode-zen` and `delegation.model auto-free` (do not patch `~/.hermes/config.yaml` directly). Pin any remaining agent-driven OSINT cron jobs to `opencode-zen / auto-free` with `cronjob(action="update", model={...})`. Full runbook and script template: `references/osint-cron-timeout-and-free-rotation.md`.

### Shinka LLM Summary Uses Unsupported Codex Model

**Symptom**: `--llm-summary` returns `The 'gpt-5.2' model is not supported when using Codex with a ChatGPT account.`

**Cause**: The Shinka OSINT provider bridge previously fell back to a stale hardcoded Codex model instead of Hermes Agent's configured provider/model.

**Fix Applied (2026-06-25)**: `plugins/shinka-osint/providers.py` now reads Hermes `model.provider` + `model.default`/`model.model`, prioritizes the configured Hermes provider when supported, and falls back to `get_default_model_for_provider("openai-codex")` / `gpt-5.5` rather than `gpt-5.2`. Verify with:

```bash
python -m pytest tests/plugins/test_shinka_osint_providers.py -q -o 'addopts='
python -m hermes_cli.main worldmonitor-osint fusion '認知戦' --wm-tier free --source-mode mock --llm-summary --save
```

Expected verification: `shinka_milspec.executive_summary.success=true` and `shinka_llm.resolved.model` equals the Hermes configured model, e.g. `nvidia/nemotron-3-super-120b-a12b`.

### Fusion Tool Output Truncation / Unusable LLM Summary

**Symptom**: `worldmonitor_fusion_report` or `hermes worldmonitor-osint fusion ... --llm-summary --save` succeeds, but the tool response is huge/truncated, or `shinka_milspec.executive_summary.summary_ja` contains meta-prompt/process text instead of a clean user-facing Japanese briefing.

**Fix**:
1. Do not relay the raw truncated response or raw `summary_ja` blindly.
2. Use the saved JSON report as the source of truth. Check BOTH possible paths:
   - Default profile: `~/.hermes/worldmonitor-osint/reports/`
   - Named profile: `~/.hermes/profiles/<profile>/worldmonitor-osint/reports/`
3. Extract structured fields: run metadata, World Monitor tier/sections, top news by `importanceScore`, GPSJam stats/regions, OREF status, and Shinka run scores/errors.
4. Reconstruct a concise Japanese report from those structured fields.
5. Label constraints explicitly: `source_mode=mock`, `wm-tier=free`, sidecar/pro not used, and Shinka scenario validation errors such as allowlist failures or import errors.

See `references/fusion-report-json-postprocess.md` for the extraction checklist and minimal Python extractor.

### Cron Job Output Truncation

**Symptom**: Large JSON reports not fully delivered

**Cause**: Messaging platforms have message size limits (Telegram: 4096 chars)

**Fix**: Reports are saved as files; delivery sends summary. Access full report via saved JSON file at `~/.hermes/worldmonitor-osint/reports/`.

### World Monitor Local Sidecar Not Running

**Symptom**: `--wm-tier auto` fails with connection refused to `http://127.0.0.1:46123`

**Cause**: Auto tier requires World Monitor sidecar (koala73/worldmonitor) running locally for Pro features.

**Fix**: Start sidecar before running auto tier, or use `--wm-tier free` which works without sidecar.

## Verification

```bash
# Check report saved
ls -la ~/.hermes/worldmonitor-osint/reports/

# Verify cron jobs (times shown in LOCAL TZ)
hermes cron list

# Test channel readiness
hermes channel-readiness-check

# Verify Shinka dependency status
hermes shinka-osint status
# Check importable: true, tool_count > 0 for full Shinka eval

# Verify World Monitor sidecar (for --wm-tier auto)
curl -s http://127.0.0.1:46123/health

# Current Shinka status (2026-06-18): importable=false, tool_count=0
# → Use --wm-tier free for production cron
```

### Mock Mode Quick Test (Bypasses Shinka Import Issues)

```bash
# Fast test without API keys or sidecar
hermes worldmonitor-osint fusion "テスト" --wm-tier auto --source-mode mock --llm-summary --save
# Completes in ~30s, generates report with mock risk scores + LLM Japanese summary
# Use this to test fusion pipeline without Shinka dependency

# Free tier real test
hermes worldmonitor-osint fusion "テスト" --wm-tier free --source-mode real --save
# Completes in ~30-60s, real World Monitor data, no Shinka
```

## Absorbed workflow map

This umbrella now covers the former morning/evening briefing, World Monitor wrapper, Shinka MILSPEC workflow/troubleshooting, SitDeck digest, and Telegram news briefing classes. Their session-specific material is preserved in:

- `references/osint-daily-morning-briefing.md`
- `references/worldmonitor-osint-tool-wrapper.md`
- `references/shinka-milspec-workflow.md`
- `references/sitdeck-osint-digest.md` — deferred `sitdeck_*` tools and digest reject rules. Load when the user asks for a SitDeck digest.
- `references/sitdeck-feed-load-wait.md` — SitDeck digest false-success: `#login` + `Loading data feed list` is not a briefing; wait for app root + feed list gone; do not treat `dashboard_detected` as done. Script: `scripts/sitdeck_extended_wait_crawl.py` via `terminal`.
- `references/cron-news-briefing-telegram.md`
- `references/feed-fallback-patterns.md`, `references/shinka-milspec-policy.md`, and the re-homed templates/scripts

Select the relevant labeled reference rather than creating a new one-session OSINT skill.

## References

- `references/worldmonitor-non-mcp.md` — User-specific rule: World Monitor must not be used through plain MCP; use desktop/exe or approved non-MCP paths.
- `references/evening-osint-fallback-web-browser-2026-08-07.md` — **Evening 2026-08-07**: `osint_agent_brief` AttributeError (4th reproduction), `web_extract` BILLING_ERROR → **web_search + curl** primary chain for government/Intel agency sources. **NIDS/NPA/ CIA Factbook direct curl 成功**、NIA発足(7/31)主要紙クロスチェック確認、CIA Factbook 2/4終了・アーカイブ化確認。Blocked: mod.go.jp/mofa.go.jp/moj.go.jp/cas.go.jp/cyber.go.jp (WAF/403/404)。Failure tags: `TOOL_RUNTIME`、`BILLING_ERROR`、`WAF_CHALLENGE`、`HTTP_403`、`HTTP_404`、`STRUCTURE_CHANGED`。Telegram-ready report template with status table included. **WAFなしドメイン優先収集ルート確立** (NIDS/NPA/JMA)。
- `references/evening-osint-fallback-web-browser-2026-08-06.md` — **Evening 2026-08-06**: `osint_agent_brief` TOOL_RUNTIME (AttributeError), `web_extract` BILLING_ERROR/402 → **web_search + browser_navigate + browser_console** primary chain for government/Intel agency sources. Verified working: Wikipedia (NCO), Tokyo portal (NISC 2025), DEFENSE NAVI (2026白書), CIA Factbook archive, NCSC/DIA/ODNI PDFs, 国会API. Blocked: mod.go.jp/mofa.go.jp/moj.go.jp/nisc.go.jp (WAF/403), 官邸会見 (404). Failure tags: `TOOL_RUNTIME`, `BILLING_ERROR`, `WAF_CHALLENGE`, `HTTP_403`, `HTTP_404`. Telegram-ready report template with status table included.
- `references/worldmonitor-tier-comparison.md` — Tier feature matrix and performance characteristics
- `references/shinka-dependency-fix.md` — Shinka MILSPEC dependency resolution guide
- `references/cron-delivery-patterns.md` — Multi-channel cron delivery configuration patterns
- `templates/osint-fusion-cron.yaml` — Cron job template for common schedules
- `scripts/verify-shinka-deps.py` — Quick dependency verification script
- `references/milspec-evening-cron-direct-pattern.md` — Direct tool-call MILSPEC evening briefing (primary path when plugin tools available)
- `references/milspec-evening-cron-cli-fallback.md` — CLI fallback for MILSPEC evening briefing (when tools not exposed)
- `references/jma-primary-curl-endpoints.md` — curl-only JMA quake/typhoon JSON + 概要PDF extraction, mod.go.jp Cloudflare workaround, and fork-venv `osint-agent` CLI notes. Use whenever `web_extract` is unavailable so the brief still rests on real primary data instead of nothing.
- `references/evening-briefing-verified-2026-08-03.md` — **Verified evening cron output pattern**: complete JSON structure, 18 gov_feed entries (防衛省12/デジタル庁6), CISA 403, SitDeck skipped, Shinka blocked by policy, web_search fallback recipe, Telegram compression to 1059 chars.
- `references/osint-agent-brief-failure-pattern.md` — **Verified failure pattern & fallback**: `osint_agent_brief` AttributeError reproduction, 5-step web_search fallback, osint-fallback-routes integration, CLI alternative path that works.
- `references/osint-fallback-routes-applied-2026-08-04.md` — **Cross-skill integration record**: `osint-fallback-routes` skill failure tags (`AUTH_REQUIRED`, `STRUCTURE_CHANGED`, `BILLING_ERROR`) applied verbatim in morning briefing report; alternate route catalog mapped to each failed agency source; cron template protocol followed. (Note: osint-fallback-routes is user-owned, not curator-managed — cannot auto-patch; see this reference for integration evidence)
- `references/osint-agent-brief-morning-verified-2026-08-05.md` — **3rd verified session**: `osint_agent_brief` tool direct call (slot=morning, wm_tier=free, include_sitdeck/mhlw/wm_free=true, llm_summary=true) → AttributeError 3rd occurrence + World Monitor 401 → osint_agent_multilayer_collect plan → web_search×12 parallel → SERIALIZATION_ERROR tag added to taxonomy → 10 primary sources verified → unified template report generated
- `references/evening-jp-gov-curl-waf-2026-08-06.md` — **Evening 2026-08-06**: `osint_agent_brief` TOOL_RUNTIME (no identical retry), `web_extract` BILLING_ERROR → **curl primary** for JMA/NPA/MHLW; `mod.go.jp` Cloudflare WAF → Jディフェンス統幕転載を「代替取得」明記; SitDeck/WM free 未達を収集ステータス表で分離。`osint-fallback-routes` は user-owned のため adopt 推奨

---

## 実戦検証済みフォールバックチェーン (2026-08-04 朝枠)

本セッションで機能した完全な代替経路を再現可能な手順として記録:

### 1. 統合ツール失敗時の即時フォールバック順序

```
osint_agent_brief (tool)
  → 失敗: AttributeError: 'NoneType' object has no attribute '__dict__'
  → osint_agent_multilayer_collect (plan取得成功、wm_freeブロックで401確認)
  → web_search × Nクエリ並列実行 (site:go.jp OR site:mod.go.jp OR site:mofa.go.jp 等)
  → 成果をMarkdownレポートへ合成
```

### 2. 各ツールの実測失敗モードと実効代替

| ツール | 失敗モード | 代替手段 | 成果 |
|--------|------------|----------|------|
| `osint_agent_brief` | `AttributeError` (シリアライズエラー) | `osint_agent_multilayer_collect` → `web_search` 手動 | 収集計画取得成功、以降手動クエリで補完 |
| `web_extract` (防衛省・警察庁) | `BILLING_ERROR: insufficient_funds` (402) | `web_search` スニペット + 公式サイト構造確認 | 概要事実確認可能、詳細PDF未取得 |
| World Monitor Free API | `HTTP 401: API key required` | なし (Free tier応答なし) | 取得不能記録 |

### 3. 失敗分類タグ実装検証 (osint-fallback-routesとの連携)

実ジョブで以下タグが機能したことを確認:
- `BILLING_ERROR` — スクレイピング課金不足 → 即座に `web_search` 代替へ切替有効
- `HTTP_401` / `AUTH_REQUIRED` — 認証必須API → 代替ルートなしで「取得不能」記録
- `STRUCTURE_CHANGED` — 公式サイト構造変更 (MHLW PDF直リンク不明) → 検索経由で公式ページ存在確認のみ

### 4. レポート出力テンプレート (Telegram向け簡潔版・1200字以内)

```markdown
# エグゼクティブサマリー
- 3-5行で核心のみ

## 🏛️ 政府・省庁一次情報（確認済み事実）
| 項目 | 内容 | 出典 |
|------|------|------|

## ⚔️ 安全保障・地政学（分析・不確実性含む）
| 観点 | 確認済み事実 | 分析・不確実性 |

## 🌪️ 自然災害・レジリエンス（確認済み）
| 現象 | 状況 | 対応 |

## 📊 情報収集ギャップ・代替ルート実績
| 対象 | 正攻法失敗理由 | 代替ルート成果 |

## 🎯 今後注視ポイント
1. ...
2. ...

## 📌 凡例
- ✅ 確認済み事実
- 🔍 分析・不確実性
- ❌ 取得不能
- **代替取得**: web_searchスニペット等で補完
```

### 次回適用すべき改善

1. `osint_agent_brief` 呼び出し前にヘルスチェック的試行を入れ、失敗時即座に `osint_agent_multilayer_collect` へフォールバックするプロンプトテンプレート化
2. `web_extract` 対象URLを事前に「課金発生しやすいドメイン」リスト (go.jp, mod.go.jp, npa.go.jp, mhlw.go.jp 等) と照合し、初めから `web_search` 併用を明示
3. 失敗タグをレポートJSONに構造化して含め、後続の `cron_failure_patterns.py` 解析に直結させる
4. `osint-fallback-routes` スキルの `AUTH_REQUIRED` / `STRUCTURE_CHANGED` タグを本スキルのピットフォール節にもミラーし、クロス参照可能にする

---

### 実戦検証済みフォールバックチェーン (2026-08-05 朝枠・osint_agent_brief tool実行)

本セッションで `osint_agent_brief` tool (slot=morning, topic=日本の安全保障と世界情勢, wm_tier=free, include_sitdeck=true, include_mhlw=true, include_wm_free=true, llm_summary=true) を直接実行し、以下の完全な代替経路を機能検証:

#### 1. 統合ツール失敗時の即時フォールバック順序

```
osint_agent_brief (tool)
  → 失敗: AttributeError: 'NoneType' object has no attribute '__dict__'
  → osint_agent_multilayer_collect (plan取得成功、wm_freeブロックで401確認)
  → web_search × 4クエリ並列実行 (site:go.jp OR site:mod.go.jp OR site:mofa.go.jp 等)
  → 成果をMarkdownレポートへ合成
```

#### 2. 各ツールの実測失敗モードと実効代替

| ツール | 失敗モード | 代替手段 | 成果 |
|--------|------------|----------|------|
| `osint_agent_brief` | `AttributeError` (シリアライズエラー) | `osint_agent_multilayer_collect` → `web_search` 手動 | 収集計画取得成功、以降手動クエリで補完 |
| `osint_agent_multilayer_collect` (L1 wm_free) | `HTTP 401: API key required` | なし (Free tier応答なし) | 取得不能記録、planのみ活用 |
| `web_search` (4クエリ) | なし | — | 20件の公式・準公式ソース取得成功 |

#### 3. 失敗分類タグ実装検証 (osint-fallback-routesとの連携)

実ジョブで以下タグが機能したことを確認:
- `HTTP_401` / `AUTH_REQUIRED` — World Monitor Free API認証必須 → 代替ルートなしで「取得不能」記録
- `STRUCTURE_CHANGED` — 公式サイト構造変更 (MHLW PDF直リンク不明) → 検索経由で公式ページ存在確認のみ

#### 4. レポート出力テンプレート (Telegram向け簡潔版・1200字以内) — 本セッション採用版

```markdown
# エグゼクティブサマリー
- 3-5行で核心のみ

## 🏛️ 政府・省庁一次情報（確認済み事実）
| 項目 | 内容 | 出典 |
|------|------|------|

## ⚔️ 安全保障・地政学（分析・不確実性含む）
| 観点 | 確認済み事実 | 分析・不確実性 |

## 🌪️ 自然災害・レジリエンス（確認済み）
| 現象 | 状況 | 対応 |

## 📊 情報収集ギャップ・代替ルート実績
| 対象 | 正攻法失敗理由 | 代替ルート成果 |

## 🎯 今後注視ポイント
1. ...
2. ...

## 📌 凡例
- ✅ 確認済み事実
- 🔍 分析・不確実性
- ❌ 取得不能
- **代替取得**: web_searchスニペット等で補完
```

#### 5. 本セッションで確認した一次ソース (検証用リンク集)

| # | 機関 | ページ | 取得日 |
|---|------|--------|--------|
| 1 | 外務省 | https://www.mofa.go.jp/mofaj/gaiko/page22_000407.html | 2026-08-05 |
| 2 | 防衛省 | https://www.mod.go.jp/j/press/wp/index.html | 2026-08-05 |
| 3 | 防衛省 | https://www.mod.go.jp/j/surround/northKorea/index.html | 2026-08-05 |
| 4 | 警察庁 | https://www.npa.go.jp/news/release/2026/20260716001.html | 2026-08-05 |
| 5 | 気象庁 | https://www.data.jma.go.jp/typhoon/position_table/table2026.html | 2026-08-05 |
| 6 | 厚労省 | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/kekkaku-kansenshou/kiki_sonae.html | 2026-08-05 |
| 7 | 内閣官房 | https://www.cas.go.jp/jp/seisakukaigi/anzenhosyoukaigi/kaisai.html | 2026-08-05 |
| 8 | NISC | https://www.cyber.go.jp/index.html | 2026-08-05 |
| 9 | JST-CRDS | https://crds.jst.go.jp/dw/20260408/2026040845034/ | 2026-08-05 |
| 10 | 防衛省 | https://www.mod.go.jp/j/approach/anpo/2026/0115a_usa-j.html | 2026-08-05 |

#### 6. 次回適用すべき追加改善 (2026-08-05 朝枠追記)

5. `osint_agent_brief` tool呼び出し時のパラメータ `slot=morning, wm_tier=free, include_sitdeck=true, include_mhlw=true, include_wm_free=true, llm_summary=true` を cronプロンプトにハードコード化し、失敗時即座に `osint_agent_multilayer_collect` → `web_search` 並列へ分岐するテンプレートを `templates/osint-agent-brief-fallback-prompt.md` として保存
6. 失敗タグ (`HTTP_401`, `AUTH_REQUIRED`, `STRUCTURE_CHANGED`) をレポート本文の「情報収集ギャップ」セクションに構造化して含め、`scripts/cron_failure_patterns.py` 解析に直結
7. `osint-fallback-routes` スキルの「省庁横断」カタログ (World Monitor, 防衛省・外務省・警察庁・気象庁・厚労省等) を本スキルの代替ルートカタログ節にミラー統合済み — クロス参照可能にする

---

### 2026-10-04 朝枠: `osint_agent_brief` 首次完全成功 + web_extract 復旧 + web_search 全面停止

**1. `osint_agent_brief` TOOL が初めて `success: true` を返した**（以往は AttributeError 4回再現）。
Layer 実態:
- `wm_free`: HTTP 401 "API key required"（認証制約、`news_digest` のみ）
- `sitdeck`: `final_url=#login` + `Loading data feed list 30%` + `/api/auth/me` のみ → **false-success。SKILL の reject ルール通り棄却**（ダッシュボード本文ゼロ）
- `gov_feeds`: `skipped` — `hermes_scrapling_feeds.gov_digest` に `digest_feeds` 属性が無い（fork 不整合、構造的欠陥）
- `mhlw`: 新規2件（ただしCBD/薬物乱用防止の定常ページでEat）
- `shinka_milspec`: 全シナリオ `score=0.0 / verified=None / evidence_blocks=None` → LLM要約も「証拠不足」判定
→ **レイヤー定義どおり "失敗 soft" で完了。輸出価値は MHLW のみ。中身は web_extract 一次収集が支配した。**

**2. `web_extract` は復活（BILLING_ERROR 解消）** — cas.go.jp / mod.go.jp / moj.go.jp / cyber.go.jp / npa.go.jp / mofa.go.jp / kantei.go.jp / jma.go.jp / mi5.gov.uk すべて HTML 本文取得成功。mod.go.jp も Cloudflare を html 抽出は通過（`__CF$cv$params` スクリプトは混在するが本文は取れる）。→ **`BILLING_ERROR` 時は curl へ切り替える既存ルールを、本日は「web_extract を優先」へ反転。**

**3. `web_search` は backend 全面停止** — 全クエリが `empty search result ... Automatic web search and CloakBrowser fallback failed`。**search 依存のフォールバック設計は本日使えず**、直接既知 URL の web_extract が唯一の道路になった。

**4. `browser_exec` も不可** — cloud provider が Nous Tool Gateway 未接続、local も Edge プロファイルロック。即座に諦めて web_extract へ。

### 重要 primary 発見: CIA The World Factbook は 2026年2月4日 sunset
`cia.gov/the-world-factbook/countries/japan/` は `Spotlighting The World Factbook as We Bid a Fond Farewell`（**February 4, 2026**）に転送され、本文に *"One of CIA's oldest and most recognizable intelligence publications, The World Factbook, has sunset."*。
→ **この cron の英機関一次ソースカタログから Factbook を外すこと。代替は NIDS / ODNI / NCSC / 各省 PDF。**
（新Factbook續投 исход的な移行先を確認していないため「代替先あり」とは断定しない）

### 収集 Continuity (-------------------------------------------------------------------)
- **国家情報会議/国家情報局**: `cas.go.jp/jp/gaiyou/jimu/nic_nib.html` + `nic_kaisai.html` で全文取得。令和8年7月31日 施行（令和8年法律第28号）、会議は**令和8年度に2回開催**(7/31 運営方針・諸規則制定 / 9/25 上半期情勢認識・下半期重点事項)。議長は内閣総理大臣、議員に国家公安委員会委員長(警察庁)・法務大臣(公安調査庁)・外務大臣・防衛大臣ら。**国家情報局長=内閣情報官の格上げ**、内閣情報分析官8人。**代打りの国家情報局長(原和也氏)は当該ページに明記なし → 要検証**。
- **国家サイバー統括室(NCO)**: `cyber.go.jp` は `index.html` のみ有効、`/news/list.html` は404（**STRUCTURE_CHANGED**）。ホーム的新着情報は **JS 動的 (`#newsList` → `Loading...`) のため web_extract で取得不能**。aptop の注意喚起のみ静的に取得可。
- **警察庁**: `npa.go.jp/news/release/` は全文取得可、北朝鮮 WaterPlum（Contagious Interview 同系名）合同アトリビューション(9/18, 日・米・豪・独)、上半期サイバー脅威報告(9/10)、家庭IoT攻撃官民一体対策(7/21)等を確認。
- **外務省**: 報道発表 10/3 = 北朝鮮 日米韓電話協議 / 世界のエネルギー情勢 G7首脳オンライン会議。**日・カタール外相会談(10/2)、日・イラン外相電話会談(10/1)**など。
- **首相官邸**: 官房長官会見 9/18午後で **高市総理 9/21-24 ニューヨーク出国（国連総CLUSIONS第81会・一般討論演説、日米首脳会談最終調整中、日本国連加盟70周年）**を確認。**官邸`/jp/headline/` は404（STRUCTURE_CHANGED）→ `/jp/tyoukanpress/` を使う。**
- **公安調査庁**: `kaitenR8.html`（令和8年版「内外情勢の回顧と展望」）が最新。**`kouan_naigai_index.html` は年別インデックス (2026年1〜12月)**で本文PDFは月別リンクだが、当日抽出では本文テキスト取れず（_INDEX_CHANGED）。
- **MI5**: `/threat-report` は404 → **正URL `https://www.mi5.gov.uk/threat-levels`（canonical: `/threats-and-advice/terrorism-threat-levels`）**。`Current Threat Level: SEVERE`（英国内全テロ＝攻撃の可能性が「非常に高い」）。北アイルランド関連は別枠。
