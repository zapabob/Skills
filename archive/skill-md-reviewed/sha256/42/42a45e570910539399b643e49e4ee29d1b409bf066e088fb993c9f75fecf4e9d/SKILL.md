---
name: disaster-news-jp
description: |
  Fetches earthquake and tsunami information from Japan Meteorological Agency (JMA) JSON API.
  By default, reports seismic intensity 3 or higher earthquakes from the past hour (suitable for hourly cron alerts).
  Can be customized via environment variables to report different time windows, include lower intensity earthquakes,
  include tsunami information, and produce concise output under 200 characters for notifications.
version: 2.0.0
platforms: [linux, windows, macos]
metadata:
  hermes:
    tags: [disaster, earthquake, tsunami, japan, jma, cron, notification]
    category: productivity
    related_skills: [cronjob]
---

# Disaster News Japan (地震・津波速報)

This skill provides disaster and security news updates focused on Japan,
specifically earthquake and tsunami information from the Japan Meteorological Agency (JMA).

## Overview

The script fetches real-time earthquake and tsunami data from JMA's JSON APIs,
filters based on configurable criteria (time window, minimum intensity, tsunami inclusion),
and formats a notification message in Japanese.

## When to Use

- Set up as a recurring cron job to get periodic disaster alerts
- Use when you want automated monitoring of seismic and tsunami activity in Japan
- Ideal for disaster preparedness and situational awareness
- Can be adapted for different reporting frequencies (e.g., daily summary) via environment variables

## Durable Operational Rules

- **Keep the source of truth authoritative:** when the deployed copy is synchronized from a repository or operational-script source, patch the repository/skill script first, then run the sync and verify the deployed copy. A runtime-only fix will be overwritten by the next sync.
- **Deduplicate JMA reports by `eid`:** JMA may publish `VXSE51` (intensity-only with empty `anm`/`mag`/`cod`), `VXSE52` (hypocenter), and `VXSE5k` (combined hypocenter + intensity) for one event. Prefer `VXSE5k`, then `VXSE52`; never let the first `VXSE51` record suppress the complete record.
- **Parse `cod` explicitly:** JMA encodes `+latitude+longitude-depth_m/`; convert depth from metres to kilometres before output.
- **Never manufacture unknown earthquake facts:** if a qualifying event lacks verified location, magnitude, or depth after the detail fetch, omit it from the confirmed list rather than outputting `不明`. State that only complete hypocenter records are reported when appropriate.
- **Required verification:** run the repository-to-deployed sync, execute the deployed script against live JMA data, and perform one manual cron run; confirm the output contains concrete name, coordinates, magnitude, and depth for every listed event.

A concise regression recipe is in `references/unknown-fields-regression.md`.

## How It Works

1. **Fetch Data**: Downloads from:
   - `https://www.jma.go.jp/bosai/quake/data/list.json` (earthquakes)
   - `https://www.jma.go.jp/bosai/tsunami/data/list.json` (tsunamis, if enabled)
2. **Parse Entries**: Processes each entry in the JSON arrays
3. **Filter**: Selects events based on:
   - Time window (default: past 1 hour)
   - Minimum seismic intensity (default: 3, set to 0 to include all)
   - Tsunami inclusion (default: false)
4. **Format**: Creates a Japanese-language report with:
   - Header with timestamp
   - 判定 (Judgment): Count and details of recent earthquakes/tsunamis
   - 津波 (Tsunami): Tsunami information (if enabled)
   - 影響 (Impact): Brief assessment of situation
   - 次に取る行動 (Next Actions): Recommendation to check JMA website
5. **Output**: Prints formatted message to stdout (for cron to capture)

## Script Location

`scripts/disaster-news-jp.py`

## Related References

- `references/jma-api-overview.md` - Overview of JMA JSON API structure
- `references/jma-api-structure.md` - Detailed structure of JMA earthquake/tsunami JSON APIs
- `references/cron-troubleshooting.md` - Troubleshooting guide for cron job issues
- `references/user-request-example.md` - Example showing how to achieve the exact format requested in a specific user session (past 24 hours, labeled output)

## Setup Instructions

1. Ensure the script is executable:
   ```bash
   chmod +x ~/.hermes/scripts/disaster-news-jp.py
   ```

2. Test manually (with default settings):
   ```bash
   ~/.hermes/scripts/disaster-news-jp.py
   ```

3. Set up as a cron job (example: every 10 minutes):
   ```bash
   # Edit crontab
   crontab -e

   # Add line:
   */10 * * * * ~/.hermes/scripts/disaster-news-jp.py
   ```

4. To customize behavior, set environment variables in the cron job or shell:
   - `JMA_TIME_WINDOW_HOURS`: Number of hours to look back (default: 1)
   - `JMA_MIN_INTENSITY`: Minimum seismic intensity to report (0=all, default: 3)
   - `JMA_INCLUDE_TSUNAMI`: Set to "true" to include tsunami information (default: false)
   - `JMA_LABELLED_OUTPUT`: Set to "true" to output labeled format (e.g., "過去24時間の地震: ...") when using concise output (default: false)
   - `JMA_USER_AGENT`: Custom User-Agent string (optional)

   Example cron line with custom settings:
   ```bash
   */10 * * * * JMA_TIME_WINDOW_HOURS=24 JMA_MIN_INTENSITY=0 JMA_INCLUDE_TSUNAMI=true ~/.hermes/scripts/disaster-news-jp.py
   ```

## Output Format

The script generates a concise, factual notification in Japanese, limited to 200 characters, with no sensational or promotional language. It lists recent earthquakes and tsunamis with time, location, magnitude or tsunami height.

For time format:
- When looking back less than 24 hours: HH:MM format (e.g., 12:53)
- When looking back 24 hours or more: MM/DD HH:MM format to disambiguate same-time events on different days (e.g., 07/04 08:29)

Example output for past hour: `12:53 宮古島北西沖 M5.0 / 10:44 宮城県沖 M4.8 / 07:05 岩手県沖 M3.9`
Example output for past 24 hours: `07/04 08:29 愛知県東部 M2.1 / 07/04 07:25 日向灘 M3.1 / 07/04 02:48 千葉県北東部 M2.8 / 07/03 23:37 岩手県沖 M3.8 / 07/03 18:32 山梨県東部・富士五湖 M2.5`

For tsunami events, when available, the output includes both the earthquake magnitude and tsunami description (e.g., `M6.4 (津波予報・若干の海面変動)`).

If no events match the criteria, it outputs: ''過去24時間に顕著な地震・津波の観測はありません。'' (with the time period adjusted based on settings).

```
【災害・安全保障速報｜2026-07-03 05:40 JST】

■ 判定
- 確認済み速報: 2件（過去1時間以内、震度3以上）
  1. 根室半島南東沖 M3.3 震度1 (07/03 05:30)
  2. 宮城県沖 M3.5 震度1 (07/03 05:24)
  他 0 件
- 根拠時刻: 2026-07-03 05:40:00 +0900

■ 津波
- 過去1時間以内に津波の発表はありません。

■ 影響
- 現在のところ、注目すべき地震・津波の情報はありません。

■ 次に取る行動
- 最新の情報は気象庁ウェブサイト等でご確認ください。
```

## Example Output (With Custom Settings)

With `JMA_TIME_WINDOW_HOURS=24 JMA_MIN_INTENSITY=0 JMA_INCLUDE_TSUNAMI=true`:

```
【災害・安全保障速報｜2026-07-03 05:40 JST】

■ 判定
- 確認済み速報: 5件（過去24時間以内、震度0以上）
  1. 根室半島南東沖 M3.3 震度1 (07/03 05:30)
  2. 宮城県沖 M3.5 震度1 (07/03 05:24)
  3. 与那国島近海 M4.6 震度1 (07/02 23:44)
  4. 福島県会津 M4.6 震度2 (07/02 20:48)
  5. 静岡県西部 M3.6 震度2 (07/02 20:13)
  他 0 件
- 根拠時刻: 2026-07-03 05:40:00 +0900

■ 津波
- 過去24時間以内に津波の発表はありません。

■ 影響
- 現在のところ、注目すべき地震・津波の情報はありません。

■ 次に取る行動
- 最新の情報は気象庁ウェブサイト等でご確認ください。
```
### ラベル付き出力の例 (JMA_LABELLED_OUTPUT=true)

With `JMA_TIME_WINDOW_HOURS=24 JMA_MIN_INTENSITY=0 JMA_INCLUDE_TSUNAMI=true JMA_LABELLED_OUTPUT=true JMA_CONCISE=true`:

```
過去24時間の地震: 07/04 08:29 愛知県東部 M2.1　07/04 07:25 日向灘 M3.1　07/04 02:48 千葉県北東部 M2.8　07/03 23:37 岩手県沖 M3.8　07/03 18:32 山梨県東部・富士五湖 M2.5　過去24時間の津波: 07/03 13:05 宮古島北西沖 M6.4 (津波予報（若干の海面変動）))
```

## カスタマイズ

- To change the time window, set `JMA_TIME_WINDOW_HOURS` environment variable (default: 1 for hourly checks)
- To change the seismic intensity threshold, set `JMA_MIN_INTENSITY` (0 to include all earthquakes, default: 3)
- To add tsunami information, set `JMA_INCLUDE_TSUNAMI=true` (default: false)
- To enable concise output (for strict character limits), set `JMA_CONCISE=true` (default: false)
- To control the time format in concise output, set `JMA_TIME_FORMAT` to either `"datetime"` (MM/DD HH:MM, default) or `"time_only"` (HH:MM only)
- To adjust the User-Agent, set `JMA_USER_AGENT` (optional)

### ラベル付き出力の例

If you need a labeled output such as "過去24時間の地震: ... 過去24時間の津波: ...", you can combine the following settings and post-process the output:

- `JMA_TIME_WINDOW_HOURS=24`
- `JMA_MIN_INTENSITY=0`
- `JMA_INCLUDE_TSUNAMI=true`
- `JMA_CONCISE=true`
- `JMA_TIME_FORMAT=time_only`

This will produce a comma-separated list of events (or a no-event message) in HH:MM format. You can then label the earthquake and tsunami parts.

Example shell script:

```bash
# Get concise output (comma-separated, time only)
OUTPUT=$(JMA_TIME_WINDOW_HOURS=24 JMA_MIN_INTENSITY=0 JMA_INCLUDE_TSUNAMI=true JMA_CONCISE=true JMA_TIME_FORMAT=time_only ~/.hermes/scripts/disaster-news-jp.py)

# If no events
if [[ "$OUTPUT" == *"に顕著な地震・津波の観測はありません。"* ]]; then
    FORMATTED="過去24時間に顕著な地震・津波の観測はありません。"
else
    # Split by commas (Japanese reading comma is '、')
    # Replace commas with full-width space for readability
    SPACED=$(echo "$OUTPUT" | tr '、' '　')
    # Simple separation: assume first part is earthquakes, last part is tsunami if tsunami info present
    # For simplicity, we label everything as earthquakes; you can refine as needed.
    FORMATTED="過去24時間の地震: $SPACED"
    # If you want to separate tsunami, you need to parse further; see advanced example below.
fi
echo "$FORMATTED"
```

For a more refined separation, you can extract tsunami entries by looking for keywords like "津波" in the output.

When `JMA_CONCISE=true`, the script outputs only the list of events (or a no-event message) in Japanese, comma-separated, truncated to 200 characters if needed. This is suitable for notifications with strict length limits.

For backward compatibility, you can also achieve concise output by setting:
  - `JMA_TIME_WINDOW_HOURS=24` for daily summary
  - `JMA_MIN_INTENSITY=0` to include all seismic activity
  - `JMA_INCLUDE_TSUNAMI=true` to check for tsunami advisories
  - And post-processing the output to extract key facts only if needed.

## ヒント: 200文字以内の簡潔出力（補足）

200文字以内の簡潔な出力が必要な場合（例：通知タイトル制限など）は、`JMA_CONCISE=true` を設定してください。これにより、過去のセッションで示された要件に対応したフォーマットが得られます。

また、以下の環境変数設定と後処理を組み合わせても同様の結果が得られます：
- ユーザーのリクエストに合致する形式（過去24時間、ラベル付き）を得るには：JMA_TIME_WINDOW_HOURS=24, JMA_MIN_INTENSITY=0, JMA_INCLUDE_TSUNAMI=true, JMA_CONCISE=true を設定し、出力の先頭に「過去24時間の地震：」および津波部分に「過去24時間の津波：」を追加してください。（例: 「過去24時間の地震: 07/04 02:48 千葉県北東部 M2.8　過去24時間の津波: 07/03 13:05 宮古島北西沖 M6.4 (津波予報（若干の海面変動))」）

- `JMA_TIME_WINDOW_HOURS=24`（過去24時間）
- `JMA_MIN_INTENSITY=0`（すべての地震を含む）
- `JMA_INCLUDE_TSUNAMI=true`（津波情報を含む）
- `JMA_TIME_FORMAT=time_only`（時刻のみ表示: HH:MM）

その後、出力から不要な装飾を除去し、全角スペースで区切った1行形式に整形します。例：

```
07/03 05:30 根室半島南東沖 M3.3　07/03 05:24 宮城県沖 M3.5　07/02 23:44 与那国島近海 M4.6　07/02 20:48 福島県会津 M4.6　07/02 20:13 静岡県西部 M3.6
過去24時間に津波の観測はありません。
```

このフォーマットは、過去のセッションで示された要件に対応しています。