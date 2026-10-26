---
name: scheduled-news-briefings
description: Create and manage recurring news briefings delivered by Hermes cron jobs, including text-only fast tests and optional generated visuals.
---

# Scheduled News Briefings

Use this skill when the user asks for recurring news digests, DeepResearch-style briefings, periodic alerts, transport/rail operation updates, timetable reminders, or test deliveries of scheduled news via Hermes cron jobs.

For transport-specific recurring alerts, also see `references/transport-operational-alerts.md`.

## Core workflow

1. **Create or update a cron job, not a one-off chat promise.**
   - Use `cronjob(action='create')` for new recurring briefings.
   - Use `cronjob(action='list')` before modifying/removing if the job ID is unknown.
   - Use `cronjob(action='update')` when changing frequency, topic mix, format, delivery destination, or enabled tools.
   - Use `cronjob(action='run')` for test delivery.

2. **Make the cron prompt fully self-contained.**
   Cron runs in a fresh session, so include:
   - Role and language.
   - Topic categories.
   - Source expectations.
   - Required output format.
   - Verification/uncertainty rules.
   - Telegram readability constraints: no tables; use headings and bullets.

3. **Enable only needed toolsets.**
   - News research: `enabled_toolsets=['web']`.
   - News plus generated image: `enabled_toolsets=['web', 'image_gen']`.
   - Do not enable `image_gen` for speed-first test runs.

4. **For fast tests, strip slow extras first.**
   If the user says they want it quickly (e.g. “早く”, “画像無しで早く”, “速報で”), update the job to a text-only speed-first prompt and then run it:
   - Set `enabled_toolsets=['web']`.
   - Add “速度優先。画像生成はしない。” to the prompt.
   - Reduce per-category item counts, e.g. 2–4 items.
   - Keep source links and uncertainty labels.

5. **For visual briefings, generate original editorial visuals.**
   When the user permits news images as references:
   - Treat article images/reporting photos as reference material, not copy-paste assets.
   - Prefer official, government, corporate, or clearly licensed sources where possible.
   - Ask image generation for an original digest-style collage/illustration, not faithful reproduction of people/logos/photos.
   - Keep image text minimal.
   - Include a short “画像について” note with key source links.

## Recommended Japanese prompt structure

```text
あなたは日本語のリサーチ担当です。現在時点の最新ニュースを、以下カテゴリについて調査してください：
1. AI
2. 国際情勢
3. 国内情勢

要件：
- 必ず最新の公開情報をWebで確認する。
- 可能な範囲で複数ソースで裏取りする。
- 重要度順に各カテゴリ2〜4件程度。
- 何が起きたか・なぜ重要か・今後の注目点を簡潔に解説。
- 一次情報を優先し、主要報道も併用。
- 速報・未確認・継続監視が必要な点は明示。
- Telegram向けに表は使わず箇条書き中心。
- 各項目に参照リンクを1〜2件。

出力フォーマット：
## 3時間ニュース速報 DeepResearch（YYYY-MM-DD HH:mm JST）

## 要点サマリー
- ...

## AI
- **見出し**：要約。重要性。今後の注目点。参照: ...

## 国際情勢
- ...

## 国内情勢
- ...

## 注意
- ...
```

## Pitfalls

- **Do not answer “latest news” from memory.** Use web-capable cron or web tools; otherwise say you cannot verify rather than inventing.
- **Do not assume a test run returns the briefing inline.** `cronjob(action='run')` starts the job and delivery usually arrives as a separate message to the configured destination.
- **Do not leave image generation enabled when the user is impatient.** Update to text-only first, then run.
- **Do not output mojibake in Japanese briefings.** If fetched titles/text contain broken UTF-8/Latin-1 artifacts such as `é»æ°`, `ã®`, or `â`, never paste them raw. Add explicit prompt rules to restore valid Japanese from another source or discard that source. NHK/Google News RSS paths are a common place this shows up.
- **When the user reports “文字化け”, fix the scheduled job before explaining.** List the cron jobs, patch the relevant briefing prompt with encoding/mojibake safeguards, then run a test delivery; summarize only after the update/run succeeded.
- **Do not use article images as direct reproductions unless the workflow explicitly supports licensed media handling.** Use them as referenced factual/editorial inspiration and link the sources.

## References

- `references/2026-05-26-telegram-news-briefing.md` — session example: 3-hour Telegram news digest, optional image generation, and speed-first text-only test delivery.
- `references/japanese-news-mojibake.md` — prompt pattern and response workflow for fixing Japanese news briefing mojibake.
- `references/transport-operational-alerts.md` — pattern for rail/transport operation alerts and station timetable cron jobs.

## Verification before final reply

After create/update/run, report:
- Whether the job was created/updated/run successfully.
- Delivery target.
- Frequency or next run when relevant.
- Whether images are enabled or disabled.
- What changed from the previous configuration.
