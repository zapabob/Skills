---
name: memory-semantic-graph-3d-viz
description: Render Hermes semantic graph as a centered Three.js 3D view.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Memory, SemanticGraph, Obsidian, Visualization, ThreeJS]
    related_skills: [memory-maintenance, memory-sleep-diary, obsidian-external-memory-journaling]
---

# Memory Semantic Graph 3D Visualization

このスキルは、Hermes semantic_graph のエクスポートからノード/エッジを抽出し、Obsidian Wiki 内に Three.js による 3D 可視化 HTML を生成する。2D D3 の描画位置ずれや中心ズレを避けるため、ノード座標を事前に正規化して固定カメラで中心に据える。

## When to Use

- ユーザーが「セマンティックグラフを可視化」「3D で見たい」「ノードグラフを開いて」と言ったとき
- memory-maintenance / memory-sleep-diary / obsidian-external-memory-journaling のあとに、外部記憶にグラフ表現を追加したいとき
- プレビューでグラフが中心から外れている、またはズーム位置がおかしいと指摘されたとき

## Prerequisites

- Hermes `semantic_graph_status` / `semantic_graph_export` ツールが利用可能
- Hermes `ebbinghaus_memory` ツールが利用可能
- Obsidian Wiki が存在し、Git 管理されている
- Web プレビューが利用できる Hermes デスクトップ環境

## How to Run

`terminal` と `write_file`、`read_file` を中心に使い、semantic_graph ツールと git で完結させる。

## Quick Reference

- `semantic_graph_status()` — DB パス、ノード/エッジ数確認
- `semantic_graph_export(format="json")` — グラフ JSON 出力
- `write_file(path, content)` — HTML/スクリプト生成
- `open_preview(url=...)` — 生成物をプレビュー
- `git status --short --branch && git diff --check && git add -A && git commit && git push` — 外部記憶へ反映

## Procedure

1. `semantic_graph_status()` を実行し、`db_path`、`nodes`、`edges`、`memory_node_links` を確認する。
2. `semantic_graph_export(format="json")` を実行する。出力 JSON は `nodes`、`edges` を持ち、エッジのキーは `source_node_id` / `target_node_id`。
3. 生成スクリプトを `tools/semantic_graph_3d_viz.py` として Wiki に保存する。
   - 対象ノード: `Actor` / `Claim` / `Preference` に加え、`Event` は先頭 150〜200 件だけサンプルして可視化する
   - 座標正規化: `created_at` / `updated_at` をタイムスタンプに変換し、X 軸を時間に割り当てる。Y/Z はノード ID のハッシュ値で安定化する
   - 中心と半径: `cx/cy/cz` をノード座標から算出し、`camRadius` を bounding box から決める
   - カメラ: `PerspectiveCamera` で center を `lookAt` し、球面座標で回転・ズームする
4. `write_file` で HTML を `visualizations/semantic-graph-3d-YYYY-MM-DD.html` に出力する。
5. `open_preview(url=...)` で開き、中心ズレ・ハングル回転・ズームを確認する。
6. 必要なら座標スケールやカメラ距離を調整し、再生成する。
7. `terminal` で Wiki ルートの `git status --short --branch` と `git diff --check` を実行する。
8. `git add -A && git commit -m "chore(memory): semantic graph 3d visualization YYYY-MM-DD"` を実行する。
9. `git push` を実行し、`git status --branch --short` と `git rev-parse --short HEAD` で clean と upstream 同期を確認する。

## Pitfalls

- export の `edges` は `source/target` ではなく `source_node_id` / `target_node_id` を使う
- 全件の `Event` ノードを出すと重いので、先頭 150〜200 件に絞る
- カメラの自動初期位置は bounding box 中心から計算する。固定位置ハードコードは中心ズレの原因になる
- ノード座標は事前に Python で算出して HTML に埋め込む。ブラウザ側のレイアウト依存で中央が来ることは期待しない
- `_x/_y/_z` のような内部キーはそのまま HTML に埋め込む。Three.js の `userData` 経由でツールチップに使う
- ツールチップは `innerHTML` を使わず `textContent` + DOM 要素の個別追加で生成する。Hermes lint は `innerHTML` 使用を XSS として警告するため、安全な DOM 構成にすること

## Verification

- `open_preview(url=...)` でグラフが中心に表示され、左ドラッグで回転、スクロールでズーム、ホバーでツールチップが出る
- `git status --branch --short` が clean で、`HEAD` が upstream と同期している
- `semantic_graph_status()` のノード数と、生成 HTML のノード数が一致する
