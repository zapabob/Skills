---
name: warashibe-arbitrage-cron
description: "Hermes no_agent cron for public-market warashibe arbitrage scans (hourly black routes, KPI digests, Telegram-safe silent empty). Use when fixing warashibe-hourly-arb-scan, rerunning cacc584f9396, or matching user-approved 💹 arb report format."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [warashibe, arbitrage, cron, no-agent, mercari, yahoo, ebay, telegram]
    category: autonomous-ai-agents
    related_skills: [warashibe-reselling, concise-communication]
---

# Warashibe Arbitrage Cron

Public-market-only cross-platform arb monitoring for Hermes cron (`no_agent`). No purchase, no login automation in the scan path.

## When to use

- Fix or rewrite `~/.hermes/scripts/warashibe-hourly-arb-scan.py`
- Job `わらしべ毎時黒字ルート監視` / `cacc584f9396` fails
- User wants 💹 black-route digest in the approved shape
- KPI / empty-stdout delivery questions for this job

## Job contract

| Field | Value |
|-------|--------|
| schedule | `0 * * * *` |
| deliver | Telegram home chat |
| no_agent | true |
| script | `~/.hermes/scripts/warashibe-hourly-arb-scan.py` |
| JSON out | `~/.hermes/warashibe/arb-scans/arb-YYYYMMDD-HHMMSS.json` |

### CLI per keyword

```text
hermes warashibe arb -k "<keyword>" \
  --platforms mercari yahoo_auction ebay amazon_jp \
  --budget 80000 --limit 6 \
  --min-profit 500 --min-rate 0.3
```

### KPI (user-required — do not soften)

- 利益 ≥ ¥500 **かつ** 利益率 ≥ 30%
- Emit only `go: true` winners
- **0 winners → empty stdout** (no Telegram message)
- Hits → print approved digest to stdout

### Env knobs

`HERMES_BIN`, `WARASHIBE_KEYWORDS`, `WARASHIBE_PLATFORMS`, `WARASHIBE_ARB_KEYWORDS` (default 2, hourly rotate), `WARASHIBE_ARB_BUDGET`, `WARASHIBE_ARB_LIMIT`, `WARASHIBE_MIN_PROFIT`, `WARASHIBE_MIN_RATE`

## Approved Telegram shape (user: 「こんな感じにして」)

```text
💹 わらしべ黒字ルート速報 {YYYY-MM-DD HH:MM} JST
候補 N件 / 公開相場のみ・購入なし
保存: {json_path}

{keyword}  [{buy} → {sell}]
- 仕入¥X → 想定売¥Y / 利益¥Z (R%)  【KPI: 利益≥¥500 かつ 利益率≥30%】
- 送料概算¥S / 手数料¥F
- 仕入候補: {title}
- {url}

市場サマリ:
...
注意: 送料・関税・状態差・規約で利益は変動。...
仕入れ実行は人手確認後のみ。
```

## Recovery workflow

1. Read the cron target script. If truncated mid-line, **do not** piecemeal-patch.
2. Rewrite whole file with `pathlib.Path.write_text` via `execute_code` (Windows: long `write_file` / bash heredoc often truncates or EOF-breaks).
3. Optional source recovery: `scripts/__pycache__/warashibe-hourly-arb-scan.cpython-*.pyc` → skip 16-byte header → `marshal.loads` for `co_consts` / names.
4. `python -m py_compile` on absolute path.
5. `cronjob(action='run', job_id='cacc584f9396')` → `execution_success: true` + new `arb-*.json`.

Sibling template: `~/.hermes/scripts/warashibe-x-niche-price-scan.py` (price-only niche scan; same subprocess style).

## Keyword defaults (hourly rotation)

Gunpla (未完成/箱/ジャンク/完成), high-VRAM GPU (30/40/50 + RX), ポケカ BOX/プロモ, レフティ, プレバン. Prefer unbuilt kits and high VRAM unless user sets `WARASHIBE_KEYWORDS`.

## Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| Treating Amazon scrape as available | Official PA-API only; otherwise SKIP in summary |
| Softening KPI in prose | Always restate 利益≥¥500 かつ 利益率≥30% |
| Next-run time from memory | Run `date` (JST) first |
| Confusing with purchase automation | This skill is **scan-only**; purchase stays human-gated |

## References

- `references/hourly-arb-cron.md` — job ids, JSON keys, repair checklist
