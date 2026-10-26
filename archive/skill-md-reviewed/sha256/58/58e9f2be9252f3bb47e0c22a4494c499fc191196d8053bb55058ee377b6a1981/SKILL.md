---
name: memory-integration-diary-sleep-obsidian-commit
description: 記憶統合と日記・睡眠・セマンティックグラフ・Obsidianコミットを一括実行。
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Memory, Ebbinghaus, Diary, Obsidian]
---

# Memory Integration Diary Sleep Obsidian Commit

記憶の連続性を保つ統合として、日記・睡眠・セマンティックグラフの読み書き・Obsidianへの版管理を一連の作業で実行する。

## When to Use
- 記憶の統合と睡眠、日記、睡眠、セマンティックグラフ書き込み、Obsidianへのコミットプッシュを同時に要求されたとき

## Prerequisites
- ebbinghaus_memory ツール
- semantic_graph_export
- Obsidian Wiki Git リポジトリ
- python 3.12

## Procedure
1. ebbinghaus_memory stats
2. sleep 1回 (forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode=archive, rehearse_threshold=0.45)
3. diary/YYYY-MM-DD.md を更新
4. semantic_graph_export json → semantic_graph_3d_viz 生成
5. memory_llm_wiki_export dry_run -> real
6. git status → add -A → commit → push
7. commit後 SHA と branch と status を検証して報告

## Verification
- stats 有効/アーカイブ件数の変化
- git rev-parse HEAD が remote と一致
