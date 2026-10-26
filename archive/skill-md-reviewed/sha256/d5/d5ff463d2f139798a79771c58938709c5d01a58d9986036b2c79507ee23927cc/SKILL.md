---
name: osint-briefing
category: osint
description: Generates a Japanese OSINT briefing in MILSPEC/PDB format for Telegram delivery, combining government RSS feeds, MHLW designated substance monitoring, and optional Shinka MILSPEC evaluation. Supports both morning and evening delivery.
---
# OSINT Briefing Generation Skill

## Description
Generates a Japanese OSINT briefing in MILSPEC/PDB format for Telegram delivery. Supports **morning** (Shinka-heavy, comprehensive) and **evening** (lightweight, feed-only, 1200字 cap) variants. Sources: government RSS feeds (防衛省, CISA, NISC, デジタル庁), MHLW 指定薬物モニター, and optionally Shinka MILSPEC evaluation (morning only).

## When to Use
Use this skill when a cron job or user requests a daily OSINT briefing for Japanese security and world affairs, targeting Telegram delivery in compact Markdown format without tables. Two variants:
- **Morning (朝刊)**: Full evaluation with Shinka MILSPEC, detailed sections, no strict character limit.
- **Evening (夕刊)**: Lightweight, feed-only, max 1200 chars, no tables, no Shinka MILSPEC evaluation.

## Prerequisites
- Hermes agent with access to: gov_feed_digest, mhlw_designated_check, web_search, web_extract tools
- For morning variant only: ShinkaEvolve-OSINT environment (with working numpy<2.5.0,>=1.23.5 for SciPy compatibility)
- Write access to ~/.hermes/osint-agent/briefs/ directory

## Step-by-Step Procedure

### 0. Determine Variant (Morning or Evening)
- Check the task instruction or cron schedule.
- **Morning**: Use Shinka evaluation. Filename: `*_milspec_morning.md`
- **Evening**: Skip Shinka. Filename: `*_milspec_evening.md`. Enforce 1200字 max, no tables.

### 1. Determine Current JST Timestamp
```bash
TZ=Asia/Tokyo date +"%Y%m%d_%H%M"   # for filename
TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M JST"   # for header
```
**Windows/MSYS pitfall:** On git-bash/MSYS2, `TZ=Asia/Tokyo` is silently ignored — the output shows UTC time with `+0000` offset. Check `%z` in the output. If it's `+0000`, manually offset: compute JST by running `date +%s` (epoch UTC), add 32400 (9h in seconds), and format with `date -d @$((epoch + 32400)) +"%Y%m%d_%H%M"`. Alternatively, run both commands and if values match (no offset applied), compute JST manually.

### 2. Run Shinka MILSPEC Evaluation (MORNING ONLY)
**First, validate available scenario IDs**: Call `shinka_osint_list_scenarios(example="milspec_security_jp")` to get the list of permitted scenario IDs. The tool validates against a policy list — only IDs in the policy will score > 0.

Execute:
```python
shinka_osint_briefing(
    example="milspec_security_jp",: No module named 'numpy'`, install compatible numpy:
  ```bash
  uv pip install "numpy>=1.23.5,<2.5.0"
  ```
- If encountering SciPy version warning, downgrade numpy to <2.5.0 as above.
- If the tool fails with exit code 1, treat as "検証上の制約" and note in briefing.

**EVENING: Skip this step entirely.** Do not call shinka_osint_briefing — it is too heavy for evening runs.

### 3. Fetch Government RSS Feeds
Execute:
```python
gov_feed_digest(hours=24, max_per_feed=5)
```
**Known failure patterns & fallbacks:**
- **CISA feeds (cisa_advisories_all, cisa_ics_advisories, cisa_news)**: Known to return HTTP 403 since mid-2026. Do NOT retry. Instead, run **web_search** with `site:cisa.gov` prefix (DuckDuckGo can return empty for broad queries):
  ```python
  web_search(query="site:cisa.gov advisory", limit=5)
  web_search(query="site:cisa.gov known exploited vulnerability", limit=3)
  ```
  Then extract the KEV alert page, ICS advisory listing, or main advisory page with `web_extract`:
  ```python
  web_extract(urls=["https://www.cisa.gov/news-events/ics-advisories"], char_limit=3000)
  web_extract(urls=["https://www.cisa.gov/known-exploited-vulnerabilities-catalog"], char_limit=3000)
  web_extract(urls=["https://www.cisa.gov/news-events/cybersecurity-advisories"], char_limit=4000)
  ```
  The cybersecurity-advisories listing page is **not blocked** (no 403) and returns dated entries sorted by date with type labels (Alert / Advisory). Drill into individual advisory URLs (pattern: `cybersecurity-advisories/<code>`) with web_extract char_limit=4000-6000 for full multi-agency attribution.
- **NISC feeds (nisc_updates, nisc_cyber)**: May also fail if Scrapling Fetcher is not installed. Fall back to web_search if needed.
- **World Monitor sidecar**: If worldmonitor_snapshot returns connection refused (sidecar not running), use web_search and web_extract to manually fetch headline news instead.
- Extract up to 5 entries per feed for the briefing.

### 4. Check MHLW Designated Substances
Execute:
```python
mhlw_designated_check(record_baseline=False, scan_enforcement=True)
```
**Notes:**
- Capture new enforcement notices and meeting notices.
- Include new_count and list of new items in the briefing.
- The tool returns a `new_items` array and a `markdown` field with pre-formatted output; extract new enforcement/designation items for the briefing.

### 5. Supplement with Web Search
When primary feeds fail (CISA 403, sidecar down), or when the briefing needs current-context depth:
- Search for Japan security news (Japanese and English queries)
- Search for CISA KEV additions, ICS advisories
- Search for major geopolitical developments (e.g., USMC deployments, NATO summits, ASEAN meetings)
- Use `site:` prefixes for reliable results when DuckDuckGo returns empty for broad queries
- Extract key articles with web_extract for concrete detail (char_limit=3000-5000)
- Only use headlines/published dates from reliable sources (mod.go.jp, mofa.go.jp, cisa.gov, nato.int, janes.com)

### 6. Compose Markdown Briefing

#### Morning Variant
Use the comprehensive format with Shinka evaluation and full sections.
Filename: `YYYYMMDD_HHMM_milspec_morning.md`

```markdown
# MILSPEC OSINT PDB Morning（YYYY-MM-DD HH:mm JST）
- 分類: Open Source / Non-classified
- 対象: 日本の安全保障と世界情勢
- 生成方式: Shinka MILSPEC + 政府RSS + MHLW指定薬物モニター

## TOP LINE
[One-sentence summary of the most critical finding]

## MILSPEC評価
[Shinka evaluation output summary]

## 一次資料アップデート（24h）
[Feed entries listed by source]

## Cyber / CII Watch
[Cyber-related items]

## MHLW 指定薬物モニター
[New designated substances]

## NEXT 24h WATCHLIST
[Watch items]

## 保存先
[File path]
```

#### Evening Variant (for Telegram delivery)
Compact, 1200字 maximum. **No tables.** Use emoji section headers. Single-section flow preferred.
Filename: `YYYYMMDD_HHMM_milspec_evening.md`

```markdown
# MILSPEC PDB Evening｜YYYY-MM-DD HH:mm JST

🔺 TOP LINE
[Critical finding in 1-2 sentences]

📡 一次資料アップデート（24h）
・[Feed Name]: [key items bulleted]

🛡 Cyber／CII
[Cyber watch items with CVE/reference details]

💊 MHLW指定薬物モニター
[New items summary]

📅 Next 24h WATCHLIST
① [Item]
② [Item]
...

保存先: briefs/YYYYMMDD_HHMM_milspec_evening.md
```

**Character budget management (evening):**
- TOP LINE: ~150 chars
- 一次資料アップデート: ~250 chars
- Cyber/CII: ~350 chars (most detail-heavy section)
- MHLW: ~100 chars
- Next 24h: ~200 chars
- Headers/lines overhead: ~150 chars
- Total target: ~1000-1200 chars

### 7. Save the Briefing
- Create directory: `mkdir -p "%USERPROFILE%\.hermes\osint-agent\briefs"`
- Save markdown to: `%USERPROFILE%\.hermes\osint-agent\briefs\<YYYYMMDD_HHMM>_milspec_<morning|evening>.md`

### 8. Deliver the Final Response
- Provide the briefing text directly as the final answer (the cron system auto-delivers it).
- Do NOT use send_message for cron jobs — the final response IS the delivery.
- If nothing new to report (all feeds empty, no changes), respond with exactly `[SILENT]`.

## Verification
- Verify that the file was created successfully.
- Check character count for evening variant (≤1200 chars).
- Check that no tables are used in evening variant.
- Ensure no API keys, cookies, machine hostnames, or local credentials are leaked.
- Ensure no fabricated CVE numbers or invented data — if web_search found nothing, say "確認できず" rather than inventing.

## Calendar Awareness
- Japanese holidays (e.g., Obon, Golden Week, New Year) often mean zero feed updates.
- U.S. holidays also mean no CISA announcements.
- If N feeds = 0 on a known holiday, note the holiday and don't treat it as anomalous.
- Weekend evening briefings are expected to be lighter than weekday morning briefings.

## Pitfalls
- **Do NOT auto-submit shinka_osint_briefing on evening runs** — the user explicitly considers it too heavy for evening.
- **Do NOT retry CISA RSS on 403** — the feeds changed their requirements mid-2026, persistent retries waste time.
- **Do NOT fabricate CVE or alert data** — if feeds are empty and web_search turns up nothing, say "新規なし" or "特段の緊急警報なし".
- **World Monitor sidecar is unreliable in cron context** — the local sidecar at 127.0.0.1:46123 is often not running during cron job execution. Do not depend on it; treat web_search as the primary fallback for international news.
- **Keep the character budget** — 1200字 goes fast. Be ruthless with editing. Remove fluff words like "について", "に関する", "おいて".
- **No tables** in evening Telegram output (renders poorly on mobile).
- **Windows/MSYS TZ env var silently ignored** — `TZ=Asia/Tokyo date` returns UTC on git-bash. Always verify by checking `%z` in the output; if `+0000` appears, compute JST manually (epoch + 32400 seconds).
- **DuckDuckGo returns empty for broad queries** — `"CISA advisory July 2026"` can yield `{success:false}`. Use `site:cisa.gov` prefix for reliable CISA results.
- **Check active international security events actively** — NATO summits, ASEAN meetings, and other multilateral forums often dominate the Japan-security news cycle. When Japanese government feeds are quiet, these events are frequently the top-line finding.
- **SitDeck browser automation requires Playwright chromium** — `sitdeck_osint_digest` fails with "Executable doesn't exist at ... chrome-headless-shell.exe" if Playwright chromium is not installed. Run `npx playwright install chromium` as a one-time setup step before first use.
- **osint_agent_brief tool is broken** — throws `AttributeError: 'NoneType' object has no attribute '__dict__'`. Do not rely on this tool; use individual tools (`shinka_osint_briefing`, `gov_feed_digest`, `mhlw_designated_check`, `sitdeck_osint_digest`, `worldmonitor_free_crawl`) directly instead. validates scenario IDs against a permitted policy list. If the provided scenario IDs (e.g., `japan_russia_military_overview`, `national_security_framework`, `cyber_defense_posture`) are not in the permitted list, **all evaluations will fail with score=0**. The permitted domains (e.g., `national_security`, `cyber_defense`, `japan_russia`) are broader categories; the specific scenario IDs must match exactly what's in the policy. When this happens, treat it as "検証上の制約

## References
- See `references/feed-fallback-patterns.md` for known RSS failure patterns and web fallback search queries.
- See `references/shinka-milspec-policy.md` for Shinka MILSPEC scenario policy, permitted domains/IDs, and workarounds.
- See `references/osint-stack-setup.md` for OSINT agent stack enablement and cron installation commands.

## Shinka MILSPEC Integration

### Briefing Command
```bash
hermes shinka-osint briefing "TOPIC" --source-mode real --llm-summary --save
```
**Note**: Command is `briefing` (not `brief`). Requires `--source-mode real` for live primary-source retrieval.

### MILSPEC Scenario Policy Constraint
Shinka validates scenario IDs against a permitted policy list. If the provided scenario IDs (e.g., `japan_russia_military_overview`, `national_security_framework`, `cyber_defense_posture`) are not in the permitted list, **all evaluations fail with score=0**. The permitted domains (e.g., `national_security`, `cyber_defense`, `japan_russia`) are broader categories; the specific scenario IDs must match exactly what's in the policy.

**Workaround**: Use `--scenario-id` with exact permitted IDs, or let the system auto-select by

## Author
Hermes Agent (OSINT Briefing Skill)