---
name: lm-twitterer-topic-bank-automation
description: "Automated X posting via topic bank with weekly rotation."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [lm-twitterer, x, twitter, social-media, cron, automation, topic-bank]
metadata:
  hermes:
    tags: [lm-twitterer, x, twitter, social-media, cron, automation, topic-bank]
    related_skills: [lm-twitterer-operations, hermes-x-posting-workflows, x-posting, x-cjk-posting]
---

## When to Use

Use this skill when setting up or maintaining automated X/Twitter posting via lm-twitterer with a topic bank (ネタ帳) that rotates through curated angles and gets weekly updates from real Hermes usage data. The system always includes `#hermesagent #はくあ` in every post.

# LM-Twitterer Topic Bank Automation

**Validated: 2026-08-10 session**

Complete system for automated X/Twitter posting using a curated topic bank with rotation state management and weekly updates based on real operational data.

## Architecture

### Core Components

| File | Purpose |
|------|---------|
| `~/.hermes/lm-twitterer/topic_bank.json` | Single source of truth: topics + rotation state |
| `~/.hermes/scripts/lm-twitterer-topic-bank-post.py` | 6-hourly cron: picks next unused topic, posts with `#hermesagent #はくあ` |
| `~/.hermes/scripts/lm-twitterer-topic-bank-weekly-update.py` | Weekly (Mon 09:00): scans impl logs, git commits, active crons, memory stats → suggests topic updates |

### Topic Bank Schema

```json
{
  "version": "1.0",
  "updated": "2026-08-10",
  "note": "ネタ帳: 実運用・活用・実用面でのネタを週次で更新。#hermesagent #はくあ を必ず含める。",
  "topics": [
    {
      "id": 1,
      "title": "朝の定期投稿・VRChat思い出",
      "angle": "毎日7時、はくあがVRChat写真を選んで音声付きMP4で投稿。生活リズムの一部になった自動化",
      "category": "daily-life",
      "source": "daily_vrchat_post.py cron実績",
      "tags": ["VRChat", "朝のルーチン", "Irodori-TTS"]
    }
  ],
  "rotation_state": {
    "used_ids": [1, 2],
    "last_updated": "2026-08-10T12:16:56.468674",
    "cycle_count": 0
  }
}
```

### Rotation Logic

1. **Sequential pick**: Always selects lowest unused ID (predictable, debuggable)
2. **Cycle reset**: When all topics used, `used_ids` clears and `cycle_count` increments
3. **State persistence**: Updated atomically after successful post

### Tweet Format

```
【{title}】
{angle}

#hermesagent #はくあ
```

- Length capped at 240 chars (X weighted limit)
- Required hashtags enforced by validation step

## Cron Jobs

| Job ID | Schedule | Script |
|--------|----------|--------|
| `dffcb54e11ba` | every 360m (6h) | `lm-twitterer-topic-bank-post.py` |
| `41a8b620f5f6` | 0 9 * * 1 (Mon 09:00) | `lm-twitterer-topic-bank-weekly-update.py` |

## Weekly Update Data Sources

The weekly update script scans:

1. **Implementation logs** (`_docs/*.md` from last 7 days) — keywords from 実装内容/概要 sections
2. **Git commits** (last 7 days, no merges) — feat/fix/refactor messages
3. **Active cron jobs** — `hermes cron list` output
4. **Memory stats** — `hermes memory stats` output

### Auto-detection Keywords

Maps implementation keywords → topic categories:

| Keyword | Topic Angle |
|---------|-------------|
| VRChat | VRChat関連の新機能・運用改善 |
| NotebookLM | NotebookLMパイプラインの進化 |
| ComfyUI | ComfyUI/動画生成の新知見 |
| MiniMax | MiniMax-H3関連のブレイクスルー |
| Ebbinghaus | 記憶システムの改善・実績 |
| LINE | LINEブリッジの安定化・新機能 |
| MoA | Mixture-of-Agentsの新構成・モデル追加 |
| OSINT | OSINT自動化の精度向上・新ソース |
| わらしべ | せどり自動化の利益実績・新カテゴリ |
| AI従業員 | AI従業員組織の新プロファイル・成果 |
| cron | Cron信頼性向上・新ジョブ追加 |
| 自律 | 自律エージェントの新ユースケース |
| スキル | 新スキル追加・既存スキル大幅改善 |
| メモリ | メモリ統合・検索精度向上 |
| 音声 | TTS/音声合成の品質向上・新ボイス |

## Posting Pattern (from `lm-twitterer-operations` skill)

Uses the validated **SourceFileLoader bootstrap** (required on Windows):

```python
loader = importlib.machinery.SourceFileLoader("lm_twitterer_core", CORE_PY)
spec = importlib.util.spec_from_loader(loader.name, loader)
core = importlib.util.module_from_spec(spec)
sys.modules["lm_twitterer_core"] = core
loader.exec_module(core)

auth = core.auth_check()
result = core.post("", text=tweet_text, dry_run=False)
```

This bypasses the plugin tool wrapper's Python environment issues.

## Verification Commands

```bash
# Syntax check all scripts
py -3 -m py_compile ~/.hermes/scripts/lm-twitterer-topic-bank-post.py
py -3 -m py_compile ~/.hermes/scripts/lm-twitterer-topic-bank-weekly-update.py

# Validate topic bank JSON
py -3 -c "import json; d=json.load(open('~/.hermes/lm-twitterer/topic_bank.json', encoding='utf-8')); print(f'Topics: {len(d[\"topics\"])}, Used: {d[\"rotation_state\"][\"used_ids\"]}, Cycle: {d[\"rotation_state\"][\"cycle_count\"]}')"

# Dry-run weekly update
py -3 ~/.hermes/scripts/lm-twitterer-topic-bank-weekly-update.py --dry-run
```

## Integration with Sync System

Both scripts are in the operational scripts allowlist (synced between repo and `~/.hermes/scripts`):

```python
ALLOWLIST = (
    ...
    "lm-twitterer-topic-bank-post.py",
    "lm-twitterer-topic-bank-weekly-update.py",
    ...
)
```

Sync runs every 30m via `sync-hermes-operational-scripts.py` cron.

## Pitfalls

1. **Windows SourceFileLoader required**: `spec_from_file_location` returns `None` for `spec.loader` on Windows — must use `SourceFileLoader` directly (validated pattern from `hermes-v020-release-rotation.py`)

2. **Rotation state atomicity**: Update `topic_bank.json` ONLY after successful post (URL received). Never pre-mark.

3. **Required hashtags**: Validation fails fast if `#hermesagent #はくあ` missing. This is a hard requirement from user.

4. **Length limit**: X's weighted limit (CJK = 2 chars) can reject even when Python `len()` < 280. Cap at 240.

5. **Weekly update dry-run by default**: Requires `--auto` flag or interactive confirmation. Prevents accidental topic bank corruption.

6. **Topic ID reassignment**: When new topics added, all IDs renumbered sequentially. Rotation state `used_ids` must be manually adjusted if topics inserted mid-cycle (or wait for natural cycle reset).

## Successful Posts (Verification)

| Topic ID | Posted | URL |
|----------|--------|-----|
| 1 | 2026-08-10 12:15:57 | https://x.com/i/web/status/2086652762641887392 |
| 2 | 2026-08-10 12:16:56 | https://x.com/i/web/status/2086653001905971588 |

Next: ID 3 (LINE個人ブリッジの実運用)