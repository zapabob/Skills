---
name: public-web-price-scan
description: Market price surveys via web_search when plugins are absent.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [research, price-scan, warashibe, market-data, public-web, cron]
---

# Public Web Price Scan

Scan public web sources for market price data using only `web_search` — no browser scraping, no login, no purchases, no API keys. This is the fallback when dedicated price-research plugins (warashibe-reselling, CloakBrowser, etc.) are not installed or when `web_extract`/Firecrawl credits are exhausted.

## When to Use

- "わらしべ穴場価格スキャン" / warashibe price discovery
- "相場調べて" / market price survey (GPU, ガンプラ, ポケカ, 左利き用品, etc.)
- Scheduled cron job that needs category-level price data from public sources only
- `hermes warashibe` CLI or `warashibe-reselling` plugin not available
- `web_extract` / Firecrawl credits exhausted (402 billing error)

## Core Principle

**Public web information only.** No purchases, no logins, no listings, no account creation. Explicitly state in output: "公開ウェブ情報のみ参照" and that no transactions were performed.

## Procedure

### 1. Keyword Selection (parallel batch)

Select 4–6 search keywords, one per category. Issue all `web_search` calls in a single batch:

- GPU: `"<model> 中古 相場 <year><month> メルカリ ヤフオク 価格"`
- ガンプラ: `"ガンプラ 激安 穴場 <year><month> Amazon あみあみ 再販"`
- ポケカ: `"ポケカ <弾名> BOX 相場 <year><month> プレミア率"`
- 左利き: `"左利き <item> 中古 激安 <year> メルカリ ヤフオク"`
- その他: `"<product> 最安値 <year><month> 価格比較"`

### 2. Price Extraction from Search Snippets

Search result `title` and `description` fields often contain enough price data:
- "中古最安 ¥32,890" / "新品最安 ¥46,000"
- "平均落札 ¥41,545"
- "プレミア率166%（定価¥6,000）"
- "実勢最安は¥9,980"
- "買取相場 1.7万〜3万円"

Extract these inline — no page fetch needed.

### 3. Follow-up Round (model/item specific)

Issue a targeted second batch for specific items that need more data:
- Specific GPU model: `"RTX 4060 中古 価格 <year><month> 相場"`
- Specific ポケカ弾: `"アビスアイ BOX 相場 <year><month> 安定 プレミア率"`
- Specific ガンプラ再販: `"ガンプラ <month>月再販 <year> HGUC MG 定価"`

### 4. Consolidate into Markdown Tables

Per category, build a table:

| Item | Price Range | Source Platform | Notes |
|------|-------------|-----------------|-------|
| RTX 4060 | 中古 ¥32,890 / 新品 ¥46,000 | price-rank.com | コスパ最強候補 |

Add a ★ rating column for 穴場度 (value-for-money).

### 5. Deliver

Consolidate into a single Markdown report with:
- Per-category tables
- A 総括 (summary) table with ratings
- Disclaimer: "公開ウェブ情報に基づく参考値。横断裁定・購入行為は一切行っていません。"

## What Works from Search Alone

- Price range headlines ("中古最安 ¥X", "平均落札 ¥Y")
- Premium rates ("プレミア率166%")
- Reissue/restock schedule announcements
- Category-level market trend descriptions
- Buy-back price ranges from specialty buyers

## What Does NOT Work Without Plugin

- Per-item buy→sell route pairing with exact identity matching
- Automated profit gate calculation (profit ≥ ¥500 AND rate ≥ 30%)
- Cross-market arbitrage route detection
- Persistent seen-key rotation
- Exact listing-level price (only aggregated/summary prices)

This method is a **discovery and reporting tool**, not an arbitrage scanner.

## Pitfalls

- **web_extract / Firecrawl 402 billing error**: When Firecrawl credits are exhausted, `web_extract` returns `Payment Required: Failed to scrape` with `insufficient_funds`. Fall back to `web_search` only — the search snippet descriptions are sufficient for category-level price scans.
- **Browser fails on Shift_JIS Japanese sites**: `browser_navigate` may fail with `'utf-8' codec can't decode byte 0x82` on Shift_JIS-encoded Japanese sites. Do NOT retry browser — use `web_search` results which are already UTF-8 decoded.
- **1-yen auction start prices**: Yahoo Auction 1円スタート listings appear as "最安値" but are auction starts, not buy-it-now. Filter mentally: if a price looks too good (under ¥3,000 for a GPU), it's likely an auction start.
- **DuckDuckGo ad redirects**: Some search results are DuckDuckGo ad redirects (duckduckgo.com/y.js?...) rather than direct links. Skip these — extract data from organic results only.
- **Price data staleness**: Search results may reference data from months ago. Always check the year/month in the snippet. Add "調査日時点" to all price claims.
- **warashibe plugin/CLI absence**: `hermes warashibe` is NOT a built-in Hermes command — it requires the `warashibe-reselling` plugin installed. Check `hermes status` / plugin list before attempting CLI commands. If absent, use this skill's procedure instead.

## Category-Specific Notes

### GPU
- VRAM capacity is the primary classifier (8/12/16/24/32GB)
- AI demand drives VRAM-heavy models (3090, 4090) up sharply
- Check both "新品最安" and "中古最安" — the gap indicates market tightness
- RTX 5090 scarcity lifts 4090/3090 used prices

### ガンプラ
- あみあみ: 10–25% discount, fastest restock
- ヨドバシ: 10% point return, free shipping
- Amazon: check "出荷元・販売元ともAmazon" — avoid 転売品
- Monthly再販カレンダー sites track schedules

### ポケカ
- Check プレミア率 (premium rate = market price / retail price)
- 絶版 (out-of-print) BOX trend upward over time
- New弾 (new expansion) prices stabilize after 60–90 days
- いまいくら？ポケカ (poke.imaikura.jp) and ポケカるっく (pokecalook.com) are reliable source sites

### 左利き用品
- Low demand = lower market prices (buyers' advantage)
- ジモティー for zero-shipping direct pickup
- ヤフオク often cheaper than メルカリ for left-handed items
- 左ききの道具店 (hidari-kiki.jp) is a specialty retailer

## Verification

- All prices include year/month reference
- No purchases, logins, or listings performed
- Output explicitly states "公開ウェブ情報のみ参照"
- Search snippets cited as source (title + URL)
- 1-yen auction starts filtered out
