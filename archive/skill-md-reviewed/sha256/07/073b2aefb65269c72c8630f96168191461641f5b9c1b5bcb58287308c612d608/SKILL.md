---
name: cursor-hermes-skill-sync
description: Cursor learnings into Hermes skills via inbox drop.
version: "1.0.0"
author: zapabobouj
metadata:
  hermes:
    category: productivity
    tags: [cursor, skills, self-improvement]
---

# Cursor → Hermes Skill Sync

Cursor で得た知見を Hermes の skill ライブラリへ取り込む。Cursor 側の自己改善ループとは別系統として運用する。

## When to Use

- Cursor セッションで再現性のある手順・修正・設定が出たとき
- 週次 self-improver cron のインボックス取り込み時
- Hermes に「Cursor でやったこと」を引き継ぎたいとき

## Prerequisites

- インボックス: `%USERPROFILE%/Documents/ops/cursor-learning-inbox/`
- 処理済み: `.../cursor-learning-inbox/processed/`
- Hermes skill 編集は `skill_manage`（patch 優先）

## How to Run

### 人間（Cursor 終了時・任意）

1. インボックスに `YYYY-MM-DD_<topic>.md` を置く
2. 次のテンプレに沿って書く（200行以内）

```markdown
# <topic>
## Context
## What worked
## Pitfalls
## Commands / paths
## Suggested umbrella skill
```

### エージェント（週次 or 手動）

1. `read_file` でインボックスの未処理 `*.md` を列挙
2. `skills_list` + `skill_view` で既存の傘 skill を特定
3. 既存があれば `skill_manage` action=patch または write_file で `references/<topic>.md`
4. 傘が無ければ class-level で create（セッション名禁止）
5. 取り込み後 `processed/` へ移動（`terminal` で `mv`）

## Quick Reference

| 学習の種類 | 置き場所 |
|-----------|---------|
| 手順・ワークフロー | 既存傘 skill の Procedure / references |
| ユーザー嗜好 | memory + 該当傘 skill の Pitfalls |
| 一回きりの環境エラー | 取り込まない（レポートのみ） |

## Pitfalls

- Cursor Rules は Hermes skill に丸コピしない（Hermes 用に要約）
- bundled / hub skill は編集不可
- 新規 skill 乱立より patch + references を優先

## Verification

```powershell
Get-ChildItem %USERPROFILE%\Documents\ops\cursor-learning-inbox -Filter *.md
hermes curator status
```
