---
name: twitter-relay-pain-analysis
description: "Twitter/X Web App API relay (fa0311/twitter_api_safe_relay) を用いた、都内在住推定アカウントの「困りごと・悩み」投稿収集・ペイン深さ分類・静的ダッシュボード生成の一連パイプライン。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  commands: [node, pnpm, python3]
  env:
    TWITTER_RELAY_BASE_URL: "http://127.0.0.1:6900 (relay server)"
metadata:
  hermes:
    tags: [twitter, x, relay, data-collection, pain-analysis, dashboard, tokyo]
    upstream_repos:
      - https://github.com/fa0311/twitter_api_safe_relay
      - https://github.com/fa0311/twitter_api_safe_relay_skills
---

# twitter-relay-pain-analysis

`fa0311/twitter_api_safe_relay` (Playwright経由でログイン済みブラウザから X Web App API を叩く HTTP relay) を使い、**公式 API 制限なし・Cookie/CSRF 自動付与**で検索収集し、ペイン深さ (L1–L4) 分類 → HTML ダッシュボード + 原文詳細ページを生成するクラスレベルスキル。

## アーキテクチャ

```
twitter_api_safe_relay (port 6900)
  └─ Playwright Chromium → x.com login → inject bridge → /i/api/graphql/* relay
        │
        ▼
collect_pain_posts.py  (SearchTimeline, cursor paging, Tokyo score filter)
        │
        ▼
data/raw_posts.jsonl  (NDJSON, 10k+ target)
        │
        ▼
classify_pain.py  (rule-based L1–L4 + 7 categories)
        │
        ▼
data/classified_posts.json  (summary + posts[])
        │
        ▼
build_dashboard.py  (static HTML: index.html + posts/<id>.html)
        │
        ▼
out/  (deployable static site)
```

## セットアップ

```bash
# 1. relay repo
git clone https://github.com/fa0311/twitter_api_safe_relay.git
cd twitter_api_safe_relay
pnpm install
pnpm build:relay

# 2. settings.json を 6900 / headless:false / user_data_dir 指定で編集
#    (user_data_dir で永続プロファイル → 再ログイン不要)

# 3. 起動 → ブラウザで X ログイン
pnpm start:relay
# http://127.0.0.1:6900/health で {"status":"ok"} 確認

# 4. 収集側
export TWITTER_RELAY_BASE_URL=http://127.0.0.1:6900
python scripts/collect_pain_posts.py --probe-only
python scripts/collect_pain_posts.py --target 10000
python scripts/classify_pain.py
python scripts/build_dashboard.py
# → out/index.html
```

## 収集クエリ設計

- **geocode/near: は GraphQL SearchTimeline で空になりがち** → 代替: `placeキーワード in query` + `profile location/post-filter`
- `PLACE_HINT = '(都内 OR 東京 OR 渋谷 OR 新宿 ...)'` を OR で付与
- コアキーワード 14 群 × (plain / +PLACE_HINT) + 完全一致フレーズ = 30+ クエリ
- `-is:retweet` 固定、`lang:ja` 固定
- `product: "Latest"` (逆時系列) で最新から掘る

## Tokyo 推定スコアリング (0–1)

| 信号 | 重み | 条件 |
|------|------|------|
| profile.location | +0.8 | 正規表現で区・市・地名マッチ |
| tweet.place | +0.9 | X の place object |
| user.description (bio) | +0.35 | 同正規表現 |
| tweet.text | +0.45 | 本文に地名 |
| place-scoped query + 既存信号 | +0.15 | 弱い prior |

閾値既定 `0.35` (調整可)。**明示信号なしなら除外** (noise 排除)。

## ペイン深さ分類 (L1–L4)

| Level | Label | Color | キーパターン例 |
|-------|-------|-------|----------------|
| L1 | 軽度・表面 | #2563eb | めんどい, ちょっと困った, 迷う |
| L2 | 中程度 | #ca8a04 | 悩み, 相談, つらい, しんどい, 不安 |
| L3 | 深刻 | #ea580c | 限界, うつ, 借金, 失業, DV, 助けて |
| L4 | 危機・緊急 | #b91c1c | 死にたい, 消えたい, 自殺, 生きられない |

- ルールベース・説明可能・日本語特化
- 深い方が勝ち、同レベルなら weight×hit数で決着
- 長文(≥120)かつ「本当に/ずっと/何年/毎日/もう」で +1 level (上限 L3)

## カテゴリ (7)

仕事・キャリア / 人間関係 / お金・生活 / 健康・メンタル / 育児・介護 / 住まい・都内生活 / 学業 / その他

## レート制限・回復

- X 側 429 (Too Many Requests) → relay ログに `HTTP-429 codes:[1003]`
- 対処: relay 再起動 (ブラウザ再起動でセッションリフレッシュ) → 10–30 分待機 → 低速再開 (`--sleep 2.0 --page-size 20`)
- 同一 query で 500 連発なら query 単位でスキップ

## トラブルシュート

| 現象 | 原因 | 対処 |
|------|------|------|
| relay /health ok だが 500 | ブラウザセッション切れ/rate limit | relay 再起動 → ブラウザで再ログイン |
| geocode 0件 | GraphQL 側未対応 | place keyword query + post-filter へ |
| 収集が伸びない | cursor ループで同一ページ | `cursor == next_cursor` で break |
| 重複除外効かない | `seen` set が raw_posts.jsonl から再構築 | `load_seen()` で ID 抽出済み |

## 参照ファイル

- `references/collect_pain_posts.py` — 収集スクリプト (SearchTimeline, paging, Tokyo score)
- `references/classify_pain.py` — 分類ルール (L1–L4, 7 categories)
- `references/build_dashboard.py` — 静的 HTML 生成 (paginated table + detail pages)
- `references/search_timeline_template.json` — relay 用リクエストテンプレ (features 固定)
- `references/query_design.md` — クエリ設計の詳細

## テンプレート

- `templates/collect_pain_posts.py` — 収集スクリプト雛形
- `templates/classify_pain.py` — 分類スクリプト雛形
- `templates/build_dashboard.py` — ダッシュボード雛形
- `templates/search_timeline_template.json` — リクエストテンプレ雛形

## スクリプト

- `scripts/verify_relay.py` — relay ヘルスチェック + SearchTimeline プローブ
- `scripts/rebuild_views.py` — 分類→ダッシュボード一括再生成