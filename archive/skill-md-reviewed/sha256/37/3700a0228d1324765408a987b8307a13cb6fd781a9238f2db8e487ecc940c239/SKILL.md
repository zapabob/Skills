---
name: warashibe-cron-recovery
description: Restore warashibe arbitrage cron and filters.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Warashibe, Cron, Recovery, Arbitrage, Windows]
---

# Warashibe Cron Recovery

This skill restores the hourly warashibe arbitrage cron after script truncation, syntax breakage, or bad market-noise results. It does not buy, bid, list, log in, or scrape Amazon HTML; Amazon is PA-API/SP-API only. Dependency stance: use existing Hermes tools and the repo venv; keep fixes small because large file writes can time out.

## When to Use
- User says `修正してcronを復旧して` for warashibe.
- `わらしべ毎時黒字ルート監視` has `last_status: error`.
- `warashibe-hourly-arb-scan.py` is truncated or syntax-broken.
- The scanner reports fake wins from 1-yen auction starts.
- User asks to add RTX 50 series, high-VRAM GPUs, Gunpla boxes, incomplete kits, or 10,000-yen start logic.

## Prerequisites
- Repo workdir: `%USERPROFILE%\Documents\New project\hermes-agent`.
- Cron script: `%USERPROFILE%\.hermes\scripts\warashibe-hourly-arb-scan.py`.
- Plugin files:
  - `plugins/warashibe-reselling/price_research.py`
  - `plugins/warashibe-reselling/core.py`
- Existing cron job: `cacc584f9396`, name `わらしべ毎時黒字ルート監視`, script `warashibe-hourly-arb-scan.py`, schedule `0 * * * *`, no_agent, Telegram delivery.
- Use repo venv command prefix from the workspace: `.venv/Scripts/python.exe`.

## How to Run
Use `read_file` and `cronjob` to inspect current state, then use small `patch` calls rather than one large `write_file`. Verify with `terminal` from the repo workdir.

## Quick Reference
- `cronjob(action="list")` — inspect job status, job id, delivery target, and `last_delivery_error`.
- `hermes status` through `terminal` — verify Hermes gateway and Telegram configuration.
- `hermes send --to telegram:<chat_id> "テスト" --json` through `terminal` — prove direct Telegram delivery.
- `channel_readiness_check()` — inspect separate OpenClaw channel readiness; do not use it as the sole Hermes check.
- `read_file(path="C:\\Users\\downl\\.hermes\\scripts\\warashibe-hourly-arb-scan.py")` — inspect cron script.
- `.venv/Scripts/python.exe -m py_compile "%USERPROFILE%/.hermes/scripts/warashibe-hourly-arb-scan.py"`
- `scripts/run_tests.sh tests/plugins/test_warashibe_price_research.py -q`
- `timeout 200 .venv/Scripts/python.exe "%USERPROFILE%/.hermes/scripts/warashibe-hourly-arb-scan.py"`

## Procedure
1. Inspect cron and script state:
   - Use `cronjob(action="list")` and find `cacc584f9396`.
   - Use `read_file` on `warashibe-hourly-arb-scan.py`.
   - If truncated, rebuild it in small `patch` chunks: imports/constants, keyword pool, `run_arb()`, then `main()`.

2. Ensure the keyword pool covers current user targets:
   - Gunpla: `ガンプラ 未完成品`, `ガンプラ 箱`, `ガンプラ ジャンク`, `ガンプラ 完成品`, `プレバン ガンプラ`.
   - GPUs: `RTX 3060 12GB`, `RTX 3070 8GB`, `RTX 3080 10GB`, `RTX 3090 24GB`, `RTX 4060 8GB`, `RTX 4070 12GB`, `RTX 4080 16GB`, `RTX 4090 24GB`, `RTX 5060 8GB`, `RTX 5070 12GB`, `RTX 5080 16GB`, `RTX 5090 32GB`, `RX 6800 16GB`, `RX 7800 16GB`, `RX 7900 24GB`.
   - Other niches: `ポケモンカード BOX`, `ポケカ プロモ`, `レフティ アイアン ゴルフ`, `レフティ ゼクシオ`.

3. Keep cron behavior bounded and observable:
   - `WARASHIBE_ARB_KEYWORDS` default `2`.
   - `WARASHIBE_ARB_LIMIT` default `6`.
   - `WARASHIBE_ARB_BUDGET` default `80000`.
   - If no winner exists, print a compact `候補なし` heartbeat instead of empty stdout; empty stdout makes a successful no_agent run look like a missing delivery.
   - Separate three checks: script execution (`last_status`), output (stdout or saved report), and channel delivery (`channel_readiness_check`).

4. Patch auction-start noise in `price_research.py` if fake 1-yen/1,000-yen wins appear:
   - In `find_arbitrage()`, after `buy_items` selection, filter buy items with:
```python
sane = [i for i in buy_items if i["landed_price"] >= max(3000, int(budget * 0.05))]
if not sane:
    continue
buy_item = min(sane, key=lambda x: x["landed_price"])
```
   - This excludes unrealistic auction starts while keeping the 10,000-yen-start strategy workable.

5. Verify locally:
   - Invoke through `terminal`:
```bash
.venv/Scripts/python.exe -m py_compile "%USERPROFILE%/.hermes/scripts/warashibe-hourly-arb-scan.py"
scripts/run_tests.sh tests/plugins/test_warashibe_price_research.py -q
export WARASHIBE_ARB_KEYWORDS=1 WARASHIBE_ARB_LIMIT=3 WARASHIBE_ARB_BUDGET=80000
timeout 200 .venv/Scripts/python.exe "%USERPROFILE%/.hermes/scripts/warashibe-hourly-arb-scan.py"
```

6. Confirm cron recovery:
   - Use `cronjob(action="list")`.
   - Confirm `cacc584f9396` is `enabled: true`, `state: scheduled`, next run is the next hour, and the latest `last_status` is `ok` after a successful scheduled/manual run.

7. Preserve a Markdown artifact and make no-result runs observable:
   - Save each run as `OUT_DIR / f"arb-{stamp}.md"`; do not create a new JSON report file.
   - Write the same Markdown text to stdout even when there are zero winners. For `no_agent`, empty stdout means no Telegram delivery.
   - Include the actual MD path in the no-result heartbeat so the operator can locate the artifact.

8. Resolve Hermes profile boundaries before diagnosing delivery:
   - Inspect `HERMES_HOME` through `terminal`; cron may run under `C:\\Users\\downl\\.hermes` while an interactive shell uses `C:\\Users\\downl\\.hermes\\profiles\\delivery-worker`.
   - Search both the main Hermes home and the active profile for the newest `warashibe/arb-scans/*.md` before concluding that no file was written.
   - Treat `channel_readiness_check` as OpenClaw-only; verify Hermes with `hermes status`, `cronjob(action="list")`, and a real `hermes send` probe.

## Pitfalls
- Large `write_file` or `patch` calls can stream-timeout; split changes into chunks under the tool limit.
- A syntax-valid truncated script can still do nothing; always read the full file and run `py_compile`.
- Yahoo Auction start prices can look like huge profit; use the buy-price sanity floor above.
- Do not unpause the old daily job `3929260814d7` unless explicitly requested; it was superseded by the hourly job.
- Amazon JP HTML scraping remains disallowed; leave missing Amazon credentials as a graceful skip.
- `last_status: ok` proves execution, not that a Telegram message reached the user.
- `channel_readiness_check` checks OpenClaw, not Hermes. Use `hermes status` for Hermes gateway configuration, then use `hermes send --to telegram:<chat_id> ... --json` for a real delivery test.
- If the user sends `/start`, confirm the Hermes gateway log contains an inbound Telegram session line; `Ignoring /start platform ping` is a normal acknowledgement, not a failure.
- A direct `hermes send` result with `success: true` and a message ID proves credentials and chat ID. Only after that should cron delivery be tested.
- If `channel_readiness_check` reports Telegram `candidateTargets: 0`, it may reflect the separate OpenClaw config even when Hermes Telegram is working.
- During delivery troubleshooting, use `deliver: telegram:<chat_id>` as the canonical production target. Use `origin,telegram:<chat_id>` only as an explicitly temporary dual route.
- A terminal launched inside a cron context may set `HERMES_CRON_AUTO_DELIVER_PLATFORM`, `HERMES_CRON_AUTO_DELIVER_CHAT_ID`, and `HERMES_CRON_SESSION`; a direct `hermes send` to the same target is then intentionally skipped as a duplicate. For an independent Telegram probe, invoke through `terminal` after unsetting those three variables.
- A successful cron run must be judged in three layers: `execution_success`, non-empty stdout/MD artifact, and Telegram delivery. `last_status: ok` alone is not proof of user-visible delivery.
- Keep the operator-facing artifact Markdown-only for this workflow. JSON may still be used internally by `hermes warashibe arb` stdout parsing, but it should not be persisted as the scheduled report.

## Verification
A restored setup must pass this single check sequence through `terminal` and `cronjob`:
```bash
.venv/Scripts/python.exe -m py_compile "%USERPROFILE%/.hermes/scripts/warashibe-hourly-arb-scan.py" && scripts/run_tests.sh tests/plugins/test_warashibe_price_research.py -q
```
Then inspect `cronjob(action="list")`, verify `cacc584f9396` is enabled and scheduled, and run `channel_readiness_check()` before claiming delivery success.

For the delivery-specific session recipe, read [`references/delivery-diagnosis.md`](references/delivery-diagnosis.md).