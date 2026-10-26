---
name: warashibe-price-scan-public-only
description: Use for read-only わらしべ arbitrage price scans.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [warashibe, arbitrage, price-scan, public-web, read-only]
    category: job-recruiter
---

# わらしべ 穴場価格スキャン（公開情報のみ）

Read-only price scan for 穴場 (arbitrage) categories. **Never buys, logs in, or
lists.** Public web pages only.

Full detail: scan categories are GPU / ガンプラ / ポケカ / 左利き用品 / その他穴場.

## When to Use

- A cron/card asks for a わらしべ or "穴場" price scan across categories.
- You need 新品 and/or 中古 相場 with citable source URLs, read-only.

## Hard Boundaries (iron rules)

- **No purchase, no login, no listing, no cart.** Read-only HTTP GET on public
  pages. Never type credentials; stop at any login or CAPTCHA wall.
- **Never invent a price.** Only report a number actually seen in fetched
  output, with its source URL. If retrieval fails for an item, write
  `RETRIEVAL FAILED` — never estimate or fill from memory. A short verified
  table beats a long guessed one.
- Final reports must state explicitly that no purchase/login/listing occurred.

## Toolchain: Know the Fallback Order BEFORE Burning 20 Calls

On this host the shell-backed layer has failed wholesale before. Test the layer
early with a trivial command and pick the first working path:

1. `web_search` — best for 相場 when it works. **Intermittent here**: it often
   returns `DDGSException: No results found` / `Set EXA_API_KEY`. Retry once or
   twice; it does recover.
2. Deferred plugin egress (`worldmonitor_free_crawl`, `gov_feed_digest`) proves
   network egress works even when the shell layer is dead — useful purely as a
   diagnostic to distinguish "no network" from "broken tool".
3. `browser_exec` — broken here: prints CLI usage + exit 1 for any payload.
4. `computer_use` — `click`/`set_value` reject `element` (`unknown argument
   element_index`); `capture`/`list_windows` do work. Text input needs
   `delivery_mode='foreground'`, which steals the user's live desktop — **do not
   do this in an unattended cron run**.

### When terminal / read_file / search_files all fail

Symptom: every call returns `Windows terminal command length exceeds safe
limit`, even `echo ok`. This kills terminal, read_file, search_files,
execute_code (cron-blocked anyway) and browser_exec at once.

- Do **not** delegate the same fetch to subagents — they inherit the same host
  toolchain and hang until timeout. Verified: two subagents ran 10+ minutes and
  returned nothing usable.
- Do **not** try to route around it with `execute_code` — as of 2026-10-08 cron
  runs get a hard `BLOCKED: execute_code runs arbitrary local Python ...
  Use normal tools instead`, regardless of `approvals.cron_mode`. Do the FX
  arithmetic in your own head or in the report and label it as arithmetic.
- Batch the fallback `web_search` calls. English queries to 5-6 distinct
  categories in one turn is the fastest reliable shape, and the backend failure
  (`Unrecognized MCP response shape`) hits ~1 call in 4 — so pair every
  must-have query with a spare and expect to retry roughly one in four.
- Pivot straight to retrying `web_search` and report honestly on coverage gaps.

### Language asymmetry in the keyless tier (verified 2026-10-07)

When `ddgs` is missing and calls get rescued by the keyless free tier, **English
queries succeed and Japanese queries fail wholesale** with `Unrecognized MCP
response shape`. Same session, same tool: `RTX 5060 Ti 8GB used price eBay sold
October 2026` returned rich dated results; `RTX 5060 Ti 8GB 中古 最安値 相場 2026`
returned `success: false`. Most calls containing kana/kanji fail.

So when the shell layer is dead, don't burn the scan on JP queries. Pivot to
English queries for the same subject and convert at the end:

- `web_extract` is often down on the same run, with a misleading error:
  `No xAI credentials found` for every URL. That's the extractor failing, not a
  paywall on the page — never report it as "site blocked".
- Price in USD, then convert with BOJ's own daily FX PDF
  (`boj.or.jp/en/statistics/market/forex/fxdaily/`) and label the conversion as
  arithmetic on fetched rates, not a quoted 円 price.
- This costs real coverage: domestic JPY sources (price-rank.com, cardrankjp.com,
  altema.jp, pokecabox.com, gpu-kaitori.com) become unreachable. State explicitly
  which JPY-native sources are missing from the report.

## English-Language Fallback Sources (when the shell layer is dead)

Quotable with a date, unlike snippets:

- **GPU 中古** — `siliconcomps.com/gpu/<model>/` (eBay BIN *asking* median, daily,
  flags its own filter breaks), `getpcparts.com/market-prices/gpu-graphics-cards/`
  (verified eBay **sold** average, weekly), `rigprice.com` (going rate + delisted
  count), `resaleprices.com/gpu/...` (fair asking band, 30d/90d momentum).
  Asking median vs sold average on the same model is often the widest 穴場 signal
  available — quote both, never just one.
- **ポケカ** — `cofre.trade/market` (pack EV per set, JP-vs-EN print ratio, set
  concentration), `doubleholo.com` (daily movers with % and raw-vs-PSA10 gap),
  `cardtrack.com` (cross-market % gaps), `joinmassive.com` (PSA 9≈raw NM vs PSA 10
  at 3–6× — the grading cliff, 50k-card study), `pricecharting.com` (sold ladder).
- **ガンプラ** — KitMaker Network forum field-notes threads (`kitmaker.net`) quote
  dated 未組立 prices straight off Japanese listings. Worth more than any
  aggregator for a 転売 grade ladder.
- **左利き** — Logitech/Amazon product pages carry real prices incl. Renewed and
  `New & Used (N) from $X` resale tiers; slickdeals.net is a public record of
  Amazon-resale street prices.
- **その他穴場** — `pricecharting.com` Loose/Complete/New/Graded ladder per
  console; `marketplaceiq.app/price-checker/...` for dated median sold.

### Currency conversion

`https://www.boj.or.jp/en/statistics/market/forex/fxdaily/index.htm` — the BOJ
daily PDF is the citable FX source (e.g. 2026-10-06 17:00 JST = 158.10–158.13).
Searching `"dollar yen exchange rate mid-market <month year>"` surfaces it.

**Exact PDF URL pattern (verified 2026-10-08):** the daily PDF is directly
guessable and its text is indexable by `web_search`, so you can quote the rate
without opening the PDF at all:
`https://www.boj.or.jp/en/statistics/market/forex/fxdaily/fxlist/fxYYMMDD.pdf`
(e.g. `fx261007.pdf` → Oct 7 spot 17:00 JST `158.10-11`, central rate `158.46`).
Use the 17:00 mid rate, not the 9:00 one.

## High-Value Public 相場 Sources (citable, no login)

- **price-rank.com** — best GPU/EC aggregate. `price-rank.com/p/<id>?condition=used`
  vs the bare id gives 中古最安値 and 新品最安値 plus listing counts.
- **CardRank JP** (`cardrankjp.com/hobby/gunpla/items/...`) — ガンプラ 中古
  中央値/最安 from 楽天 shop listings with an explicit 取得 date. Ideal for MG.
- **altema.jp/pokemoncard/mikaihubox**, **pokeca-chart.com/box/**,
  **pokecabox.com** — ポケカ 未開封BOX 相場; the latter tracks all 82 BOX types
  daily with 値上がり/割安 rankings.
- **gpu-kaitori.com** — GPU 買取相場 columns with month-stamped price trends.
- **Amazon / 価格.com / 楽天 category pages** — for left-handed gear. Prices come
  from search-result snippets, so quote the snippet, not a guess.

## Reporting Template

Per category: 商品名 / 新品 or 中古 相場 / source URL / 値上がり・値下がり. Then a
short 穴場 read (where 仕入→転売 margin looks open) framed strictly as analysis
— never as an instruction to buy. End with a one-line
no-purchase/no-login/no-listing attestation and list any `RETRIEVAL FAILED` rows.

## Pitfalls

- A snippet citing an aggregator is still *snippets*, not a full page fetch. Say
  so; don't imply you read the whole price table.
- Snippet prices carry their own crawl lag (often "2 days ago"). Prefer sources
  that state a 取得 date and carry it through to the report.
- A middleman's 買取価格 is that buyer's bid, not the market 相場. Label it
  買取目安, not 相場.
- Pokemon's 30th anniversary (Oct 2026) is distorting sealed-BOX pricing — say so
  rather than presenting those numbers as a normal baseline.
- Don't invent niche categories for "その他穴場" — only report a pick you
  actually priced.

## Verification

Done only when every reported number carries a source URL and a crawl date, or
`RETRIEVAL FAILED` appears for anything unconfirmed. If more than half the rows
are `RETRIEVAL FAILED`, state the scan was degraded rather than padding it.
