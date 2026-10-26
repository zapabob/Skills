---
name: memory-composite-system
description: Sleep, diary, dreams, semantic graph, and wiki recall workflow.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Memory, Obsidian, SemanticGraph, CodeGraph, Visualization, Sleep, Diary, Dreams]
    related_skills: [memory-maintenance, memory-sleep-diary, obsidian-external-memory-journaling, memory-semantic-graph-3d-viz]
---

# Memory Composite System

Hermes 内部のエビングハウス記憶、Obsidian 外部記憶、codegraph/semantic graph 可視化を1ワークフローに統合する。日記・夢記録・睡眠サイクル・グラフ・検索を一貫して実行し、Git で外部記憶に反映する。

## When to Use

- 「記憶の統合と睡眠」「30000ms で睡眠して」「夢を記録して」などの複合記憶依頼
- セマンティックグラフ / codegraph の可視化要求
- Obsidian wiki の検索/想起フローの整備依頼
- 外部記憶へのコミット/プッシュ要求
- 複数の記憶サブシステムを一度に実行する必要があるとき

## Prerequisites

- Hermes `ebbinghaus_memory` ツール
- Hermes `semantic_graph_status` / `semantic_graph_export` ツール
- Python 3.12 + `pip install codegraph`
- Obsidian Wiki が Git 管理されている
- Web プレビューが利用できる Hermes デスクトップ環境

## How to Run

`terminal`、`write_file`、`read_file`、Hermes ツール群を組み合わせて実行する。複数サブシステムは並列に調査し、結果を Wiki に統合する。

## Quick Reference

- `ebbinghaus_memory(action="stats")` — 記憶状態確認
- `ebbinghaus_memory(action="sleep", forget_threshold=0.08, salience_keep_threshold=0.7, prune_mode="archive", rehearse_threshold=0.45)` — 睡眠サイクル
- `semantic_graph_status()` / `semantic_graph_export(format="json")` — グラフ出力
- `py -3 -m codegraph.main --output <path> <src_paths...>` — コードグラフ生成
- `py -3 tools/recall_external_memory.py "<query>" [--git-history] [--limit=N]` — Wiki 検索
- `write_file(path, content)` — 日記/夢/ツール/HTML生成
- `open_preview(url=...)` — グラフ確認
- `git status --short --branch && git diff --check && git add -A && git commit && git push` — 外部記憶反映

## Procedure

1. `ebbinghaus_memory(action="stats")` で内部記憶の状態を確認する。
2. 睡眠サイクルを実行する。`forget_threshold=0.08`、`salience_keep_threshold=0.7`、`prune_mode="archive"`、`rehearse_threshold=0.45`、`limit=200` を標準とする。
3. 日記 `diary/YYYY-MM-DD.md` と夢記録 `dreams/YYYY-MM-DD.md` を更新する。夢は `dream_candidates` の有無を明記する。
4. `semantic_graph_status()` / `semantic_graph_export(format="json")` でセマンティックグラフを取得する。
5. `py -3 -m codegraph.main --output <wiki_visualizations_path>/codegraph-<target>.html <src_paths...>` でコードグラフを生成する。
6. セマンティックグラフ可視化スクリプトを `tools/semantic_graph_3d_viz.py` として保存し、`visualizations/semantic-graph-3d-YYYY-MM-DD.html` を生成する。
   - 対象: `Actor` / `Claim` / `Preference` + `Event` 先頭 200 件
   - 座標: タイムスタンプを X、ノードIDハッシュを Y/Z に割り当てる
   - カメラ: bounding box 中心を `lookAt` する固定カメラ
7. Wiki 検索フローとして `tools/recall_external_memory.py` を整備する。シークレット/メール/トークンを赤線処理する。
8. `open_preview(url=...)` で 3D グラフを確認し、必要なら座標スケールやカメラ距離を調整する。
9. `terminal` で Wiki ルートの `git status --short --branch` と `git diff --check` を実行する。
10. `git add -A && git commit -m "chore(memory): composite system update YYYY-MM-DD"` を実行する。
11. `git push` を実行し、`git status --branch --short` と `git rev-parse --short HEAD` で clean と upstream 同期を確認する。

## Pitfalls

- Hermes lint は `innerHTML` を XSS として警告する。ツールチップは `textContent` + DOM 要素の個別追加で生成する
- `codegraph` のエッジキーは `source_node_id` / `target_node_id`。`source/target` ではない
- 全件の `Event` ノード可視化は重いので、先頭 150〜200 件に絞る
- `ebbinghaus_memory` は Hermes ツール経由が優先。Python スクリプトから直接 `import` すると失敗することがある
- 外部記憶には生ログ・秘密情報を保存しない。`recall_external_memory.py` はメール/トークン/パスワードを赤線処理する
- `git diff --check` の空欄テンプレート `- ` は末尾空白として失敗するため、`-` を使う
- 3D 可視化のカメラ初期位置は bounding box 中心から計算する。固定位置ハードコードは中心ズレの原因になる

## Verification

- `ebbinghaus_memory(action="stats")` の前後で active/archived 件数が変化している
- `open_preview(url=...)` で 3D グラフが中心に表示され、回転/ズーム/ツールチップが動作する
- `py -3 tools/recall_external_memory.py "記憶" --limit 3` が終了コード 0 で実行され、シークレットが `[REDACTED]` になっている
- `git status --branch --short` が clean で、`HEAD` が upstream と同期している
