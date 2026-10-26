---
name: daily-osint-briefing
description: |
  Generate daily Japanese MILSPEC/PDB OSINT briefing for Telegram delivery.
  Combines Shinka MILSPEC evaluation, government RSS feeds (MOD, CISA, Digital Agency),
  MHLW designated drug monitor, and JMA disaster alerts into a single markdown report.
version: 1.0.0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [osint, briefing, telegram, milspec, cron, japan, security]
    category: research
    related_skills: [disaster-news-jp, cronjob-management, shinka-run]
---

# Daily OSINT Briefing (MILSPEC/PDB Morning Edition)

Generates a daily Japanese-language OSINT briefing in MILSPEC/PDB markdown format
suitable for Telegram delivery. Designed to run as a scheduled cron job.

## When to Use

- Scheduled daily cron job (e.g., 07:00 JST)
- On-demand briefing generation for Telegram channel
- Any situation requiring fused OSINT from Shinka MILSPEC + government feeds + disaster alerts

## Required Tools

- `shinka_osint_briefing` (plugin tool — see **⚠️ note below**)
- `gov_feed_digest` (plugin tool — see **⚠️ note below**)
- `mhlw_designated_check` (via disaster-news-jp skill or direct — see **⚠️ note below**)
- `disaster-news-jp` skill (for JMA earthquake/tsunami check)

> **⚠️ Tool Availability**: The `shinka_osint_briefing`, `gov_feed_digest`, and
> `mhlw_designated_check` tools are provided by Shinka/Hermes OSINT plugins
> (e.g. Self Evolution plugin #24). These tools may NOT be registered because:
> - Self Evolution is disabled in Hermes tools config (most common)
> - The shinka-evolve-osint plugin only provides evolution/MCP tools, not these briefing tools
> - The Shinka OSINT vendor checkout is missing or misconfigured
>
> **If unavailable → use Fallback Mode** (`references/fallback-no-shinka-tools.md`)

## Workflow

### 1. Get Current JST Timestamp
```bash
python3 -c "from datetime import datetime, timezone, timedelta; jst=timezone(timedelta(hours=9)); n=datetime.now(jst); print(n.strftime('%Y-%m-%d %H:%M JST')); print(n.strftime('%Y%m%d_%H%M'))"
```

### 2. Run Shinka MILSPEC Briefing
```python
# Tool call: shinka_osint_briefing
{
  "topic": "日本の安全保障と世界情勢",
  "example": "milspec_security_jp",
  "source_mode": "real",
  "max_scenarios": 3,
  "save_report": true
}
```
**Pitfall**: The Shinka OSINT policy restricts permitted scenario IDs. The `example` parameter must match a permitted domain. If scenarios fail with "not in permitted Shinka OSINT policy", check the returned `policy.permitted_domains` and adjust `example` or use explicit `scenario_ids` from the permitted list.

### 3. Run Government Feed Digest (24h window)
```python
# Tool call: gov_feed_digest
{
  "hours": 24,
  "max_per_feed": 5
}
```
**Pitfall**: CISA feeds often return HTTP 403 (WAF/geo-block). Treat as "collection constraint" not failure. Note in report and recommend direct site check.

### 4. Run MHLW Designated Drug Monitor
```python
# Via disaster-news-jp skill or direct tool
mhlw_designated_check(record_baseline=false, scan_enforcement=true)
```
Or use the disaster-news-jp script with appropriate env vars.

### 5. Run JMA Disaster Check (past 1 hour, intensity ≥3)
```bash
JMA_TIME_WINDOW_HOURS=1 JMA_MIN_INTENSITY=3 ~/.hermes/scripts/disaster-news-jp.py
```

### 6. Assemble Markdown Report
Use the template in `templates/milspec_morning_briefing.md` (see below).

**Template Variables:**
- `{{MILSPEC_BULLET_LIST}}` — bullet list of scenario results (replaces old `{{MILSPEC_TABLE_ROWS}}` table)
- Other variables unchanged

### 7. Save Report
```
C:\Users\<user>\.hermes\osint-agent\briefs\YYYYMMDD_HHMM_milspec_morning.md
```

### 8. Output for Telegram
Return the markdown content (or condensed "key points + path + links" if over Telegram length limits).

## Markdown Structure

```markdown
# MILSPEC OSINT PDB Morning（YYYY-MM-DD HH:mm JST）
- 分類: Open Source / Non-classified
- 対象: 日本の安全保障と世界情勢
- 生成方式: Shinka MILSPEC + 政府RSS + MHLW指定薬物モニター

## TOP LINE
## MILSPEC評価
## 一次資料アップデート（24h）
## Cyber / CII Watch
## MHLW 指定薬物モニター
## NEXT 24h WATCHLIST
## 保存先
## 主要リンク
```

**Formatting rules**: No tables (use bullet lists), no unverified claims, no secrets/API keys.

## Telegram Delivery

If markdown exceeds ~4000 chars, condense to:
- 要点 (3-5 bullets)
- 保存先パス
- 主要リンク (5-7 items)

## ⚠️ Fallback Mode (Shinka Tools Unavailable)

When `shinka_osint_briefing`, `gov_feed_digest`, or `mhlw_designated_check`
are not registered as Hermes tools, use `web_extract` + `web_search` as drop-in
replacements. See `references/fallback-no-shinka-tools.md` for the complete
step-by-step fallback workflow with exact URLs and known failure modes.

### Key Replacements

| Shinka Tool → | Fallback |
|---------------|----------|
| `shinka_osint_briefing` | `web_search("日本の安全保障 …")` + cross-reference first-party sources |
| `gov_feed_digest` | `web_extract([MOD_rss_URL, Digital_Agency_rss_URL, …])` |
| `mhlw_designated_check` | `web_extract([MHLW_committee_page])` + parse table |
| JMA disaster-news-jp script | `web_extract([JMA_quake_JSON])` → filter `maxi≥3` |

### Output Adjustments in Fallback Mode

- MILSPEC評価 section: note "Shinka tools unavailable, manual web collection"
- No scored scenarios → provide qualitative assessment from cross-referenced sources
- Template `{{MILSPEC_BULLET_LIST}}`: write "ツール未使用のためMILSPECスコアなし" or list key headlines
- LLM provider/model: use the model that generated the briefing (not Shinka's LLM)

## Cron Setup Example

```bash
# Daily 07:00 JST
0 22 * * * /path/to/hermes run daily-osint-briefing  # UTC 22:00 = JST 07:00
```

## References

- `references/shinka-policy.md` — Shinka OSINT permitted domains and provider policy
- `references/gov-feeds.md` — Government RSS feed catalog and known issues
- `references/mhlw-drug-monitor.md` — MHLW designated drug committee monitoring notes
- `references/jma-disaster.md` — JMA API parameters and output formats
- `references/fallback-no-shinka-tools.md` — Complete fallback workflow when Shinka tools unavailable
- `references/fallback-session-2026-08-03.md` — Verified fallback execution record: osint_agent_brief AttributeError → web_search/site:domain collection → full report assembly
- `references/fallback-session-2026-08-04.md` — **2回目の実戦検証**: osint_agent_brief AttributeError + web_extract BILLING_ERROR + World Monitor 401 → osint_agent_multilayer_collect計画取得 → web_search×9クエリ並列 → osint-fallback-routes失敗タグ語彙(BILLING_ERROR/AUTH_REQUIRED/STRUCTURE_CHANGED)完全適用 → 統一テンプレート準拠レポート生成成功
- `references/fallback-session-2026-08-05.md` — **3回目の実戦検証・osint_agent_brief tool直接呼び出し初検証**: 同tool AttributeError 3連続 + World Monitor 401 → osint_agent_multilayer_collect計画取得 → web_search×12クエリ並列 → 失敗タグにSERIALIZATION_ERROR追加・語彙拡張 → 統一テンプレート準拠レポート生成成功・10機関一次ソース検証完了
- `references/fallback-session-2026-08-07.md` — **4回目の実戦検証・cron job自動実行**: osint_agent_brief AttributeError + web_extract BILLING_ERROR全件 + Cloudflareブロック + 日本政府サイト構造的アクセス困難 → osint_agent_multilayer_collect計画取得 → web_search×12 + browser_navigate×9並列 → 失敗タグCLOUDFLARE_BLOCK追加・語彙拡張 → 統一テンプレート準拠レポート生成成功・10機関一次ソース検証完了・CIA Factbook終了確認