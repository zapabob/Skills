---
name: memory-composite-twice-daily-sync
description: Use for twice-daily memory sleep, graph, and Obsidian sync.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [memory, sleep, semantic-graph, obsidian, cron]
    related_skills: [memory-composite-system, memory-maintenance, memory-sleep-diary]
---

# Twice-Daily Composite Memory Sync

定期的に Ebbinghaus、セマンティックグラフ、ハイブリッド記憶、Obsidian 外部記憶を統合する。生の会話履歴・秘密情報・認証情報は外部記憶へ出力しない。

## When to Use

- 記憶統合を1日2回のCronで運用するとき
- `/learn` で今回の統合手順を再利用可能にするとき

## Prerequisites

- `ebbinghaus_memory`
- `semantic_graph_status` と `semantic_graph_export`
- `memory_llm_wiki_export`
- Wikiの実ルートをエクスポート結果の `wiki_root` から確認
- Gitリポジトリとpush権限

## Procedure

1. `ebbinghaus_memory(action="stats")` で開始状態を記録する。
2. 同一パラメータの睡眠サイクルを最大2回実行する。`forget_threshold=0.08`、`rehearse_threshold=0.45`、`salience_keep_threshold=0.7`、`prune_mode="archive"`。完全削除ではなくアーカイブを使う。
3. `semantic_graph_status` でノード・エッジ・DBを確認し、読み書き可能なグラフ情報をハイブリッド記憶の構造として扱う。完全スナップショットが必要な場合は構造フィールドだけをWiki内 `raw/semantic-graph/` に保存し、summary・rationale・metadata・artifact・証拠本文は除外する。
4. `memory_llm_wiki_export(dry_run=true)` で件数と対象ルートを確認する。件数が既存規模から異常に減った場合は実エクスポートを中止し、集計ログだけにする。妥当なら `dry_run=false` を実行する。
5. Wikiの `diary/YYYY-MM-DD.md` と `YYYY-MM_睡眠ログ.md` を事実ベースで追記する。夢情報が入力されていない場合は、夢なしと明記し、創作しない。
6. 変更対象を確認し、`git diff --check` と追加行の秘密・個人情報・絶対パス監査を行う。無関係な変更はステージしない。
7. 変更がある場合だけコミットし、実際のリモートへpushする。push後に `git status --branch --short`、`git rev-parse --short HEAD`、upstreamとの一致を確認する。
8. 実行結果は件数・パス・SHA・エラーだけを簡潔に報告し、記憶本文や秘密値を出力しない。

## Pitfalls

- 同じsleepを3回以上連続実行しない。
- `semantic_graph_export` は外部ディレクトリかつ上限付きの場合があるため、Wiki内の構造化スナップショットを必要時に別途作る。
- `git add -A` は無関係なHTMLを拾うことがある。対象パスを明示する。
- `wiki_root` を履歴や設定から推測しない。
- Cron自身を作成・変更・削除しない。既存ジョブの重複を作らない。
- gateway停止中は保存済みジョブが発火しないため、スケジュール済みと稼働中を区別する。

## Verification

- 開始・終了のEbbinghaus件数が確認できる
- グラフのノード・エッジ件数と保存先が確認できる
- dry-run後にだけ実エクスポートされる
- Wikiの変更が監査済みで、push後のHEADとupstreamが一致し、working treeがclean
