---
name: warashibe-multi-market-arbitrage
description: Cross-market price scan and profit detection for warashibe reselling across Mercari, Yahoo Auction, eBay, and Amazon PA-API.
version: 0.1.0
author: Hermes
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Reselling, Arbitrage, PriceResearch, Warashibe, CloakBrowser]
---

# Warashibe Multi-Market Arbitrage Scan

This skill documents the reusable procedure for scanning public market prices across Mercari, Yahoo Auction, eBay, and Amazon (PA-API only — no HTML scrape), then evaluating buy→sell routes against warashibe profit gates (profit ≥ ¥500 AND rate ≥ 30%). The hourly cron prints either winners or a compact no-candidate heartbeat so execution can be distinguished from delivery failure.

## When to Use
- "warashibe arbitrage scan" / "わらしべ 横断裁定"
- "multi-market price check" / "メルカリ ヤフオク eBay 相場"
- "hourly profit watcher" / "毎時 黒字監視"
- "mercari q parameter broken" / "メルカリ 検索 結果 空"

## Prerequisites
- **Hermes Agent** with `cloakbrowser` installed (`uv pip install cloakbrowser`)
- **warashibe-reselling plugin** enabled (`plugins/warashibe-reselling/`)
- **Optional**: Amazon PA-API credentials for live Amazon quotes
  - `AMAZON_PAAPI_ACCESS_KEY`
  - `AMAZON_PAAPI_SECRET_KEY`
  - `AMAZON_PAAPI_PARTNER_TAG`
- **Env vars** (optional overrides)
  - `WARASHIBE_USDJPY` (default 150) — USD→JPY conversion for eBay
  - `WARASHIBE_ARB_BUDGET` (default 80000) — max buy price for arb scan
  - `WARASHIBE_ARB_KEYWORDS` (default 2) — keywords per hourly run
  - `WARASHIBE_ARB_LIMIT` (default 6) — items per market per keyword

## Keywords and Budget Strategy
- **Budget**: 10,000円スタート想定。cron は `WARASHIBE_ARB_BUDGET` で調整（デフォ 80,000）。
- **GPU**: VRAM容量で分類（8GB/12GB/16GB/24GB/32GB）。RTX 50系（5060〜5090）含む全世代。
- **ガンプラ**: 「未完成品」「箱のみ」「ジャンク」「完成品」の4種別で検索。
- **回転**: cron 内で `KEYWORD_POOL` を時刻シードで毎時ローテーション。全23語から `WARASHIBE_ARB_KEYWORDS`（デフォ2）ずつ実行。

## How to Run
```bash
# One-shot arbitrage scan (all 4 markets)
hermes warashibe arb -k "RTX 3060 グラボ" --budget 80000

# Price check only (dry-run)
hermes warashibe price -k "レフティ ゼクシオ" --platforms mercari yahoo_auction ebay amazon_jp --dry-run

# Japan→eBay export premium scan
hermes warashibe j2e -k "RTX 3060 グラボ" --min-premium 0.5 --budget 80000

# Hourly cron (no_agent, observable heartbeat)
cronjob create --name "わらしべ毎時黒字ルート監視" \
  --script warashibe-hourly-arb-scan.py \
  --schedule "0 * * * *" \
  --no-agent \
  --deliver origin,telegram:7201110294
```

## Japan→eBay Export Premium (j2e)

The `j2e` subcommand finds buy-cheap-in-Japan / sell-high-on-eBay routes:

```bash
hermes warashibe j2e -k "RTX 3060 グラボ" --min-premium 0.5 --budget 80000
```

- `--min-premium 0.5` = export_premium ≥ 50%（eBay売値が日本買値より50%以上高い）
- `export_premium` = `(sell_price - buy_price) / buy_price`、output に表示

## Procedure

1. **Keyword selection** — cron rotates through the pool by `(hour + i) % len(pool)`.
2. **Buy-price sanity filter** — `find_arbitrage()` now filters out unrealistically low prices (`< max(¥3,000, budget×5%)`) which are typically auction start prices, not buy-it-now.
3. **Per-market fetch** — `search_markets()` for each platform.
4. **Route estimation** — pairs cheapest buy (post-filter) vs 75th-percentile sell per market.
5. **Profit gate** — `profit ≥ 500 AND rate ≥ 0.30` (from `core.KPI_DEFAULTS`).

## Candidate Identity and Rotation Gates

- Treat X buzz as a discovery signal, not proof of resale demand or price.
- Accept a buy→sell route only when product identity matches across sides: exact name/model, edition, language, condition, quantity/box count, and sealed/shrink status.
- Reject broad-keyword false positives such as a single card paired with a sealed BOX, a 10-pack lot paired with a full BOX, or a Japanese product paired with a different-language product.
- A one-yen/auction-start listing, an item with unclear quantity, or an unverified future release is a watchlist item, not a KPI winner.
- For hourly discovery, keep a persistent seen-key set based on normalized SKU/product identity. Select a different identity each hour; permit at most one repeat, then suppress it until the rotation pool is exhausted.
- Report `confirmed`, `watchlist`, and `rejected` separately. Never present a keyword-level pairing as a confirmed arbitrage route.
- Detailed examples and the evidence hierarchy are in `references/candidate-identity-and-moa-rotation.md`.

## Pitfalls

- **Auction start prices (1-yen traps)** — Yahoo Auction 1円スタートの出品が最安値として拾われる可能性あり。`find_arbitrage()` は `landed_price < max(3000, budget×5%)` を自動除外。
- **Mercari `q=` returns empty** — must use `keyword=` + `status=on_sale`（`price_research.py` で修正済み）。
- **eBay cards are dynamic** — parser climbs 8 parents from `/itm/` anchor; skips "Shop on eBay" noise.
- **Amazon HTML blocked by policy** — PA-API only; missing keys = graceful skip with reason.
- **Yahoo Auction 1-yen starts** — landed price uses current price; watch for reserve bids.
- **Delivery diagnosis** — `last_status: ok` proves execution, not receipt. Run `channel_readiness_check()` and verify a recognized Telegram target; if Telegram has no candidate target, have the user send `/start` to the configured bot. See `warashibe-cron-recovery/references/delivery-diagnosis.md`.

## Verification
```bash
# Unit tests (8 passing)
scripts/run_tests.sh tests/plugins/test_warashibe_price_research.py -q

# Smoke: live arb scan
hermes warashibe arb -k "レフティ ゼクシオ" --budget 80000

# J2E premium scan
hermes warashibe j2e -k "レフティ ゼクシオ" --min-premium 1.0 --budget 80000
```