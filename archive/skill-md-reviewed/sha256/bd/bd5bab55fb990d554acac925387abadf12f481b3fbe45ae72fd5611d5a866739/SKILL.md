---
name: public-marketplace-price-research
description: "公開フリマ/オークションの価格調査（CloakBrowser・hermes warashibe price）とX話題穴場のcron回転監視。購入なし。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [warashibe, mercari, yahoo-auctions, cloakbrowser, price-research, cron, sedori]
    category: autonomous-ai-agents
    related_skills: [warashibe-reselling, cronjob-management, ai-employee-org]
---

# Public Marketplace Price Research

公開ページだけを低頻度で取り、相場ダイジェストを出す。**ログイン・購入・出品はしない。**

わらしべ本体（複利サイクル・台帳・AI社員）は `warashibe-reselling`。
スキル名が衝突している場合は `autonomous-ai-agents/warashibe-reselling` を明示。

## When to Use

- `hermes warashibe price` / CloakBrowser 公開調査
- GPU・ガンプラ・ポケカ・左利き用品など穴場の定期監視
- Xで話題のカテゴリをcronで日次回転スキャン
- メルカリ検索が0件になるバグの修正・再発防止

## Commands

```bash
hermes warashibe price -k "キーワード" --platforms mercari --limit 8
hermes warashibe price -k "キーワード" --platforms mercari yahoo_auction --limit 6
hermes warashibe price -k "キーワード" --dry-run   # URL形状のみ
```

実装: `plugins/warashibe-reselling/price_research.py`
ユニット: `tests/plugins/test_warashibe_price_research.py`

```bash
scripts/run_tests.sh tests/plugins/test_warashibe_price_research.py -q
```

## Mercari 2026 (CRITICAL)

| 悪い | 良い |
|------|------|
| `https://jp.mercari.com/search?q=...` | `https://jp.mercari.com/search?keyword=...&status=on_sale` |
| `article[data-testid='item-cell']` | `a[href*='/item/']` + 近傍テキスト `¥ 30,200 タイトル` |

症状: TITLE「検索結果」、本文「商品を検索しましょう」、items=[] → **ほぼ必ず `q=` か旧セレクタ**。

## Yahoo Auctions

- 行: `li.Product`
- タイトル: `a[data-auction-title]` / `data-auction-title`
- 価格: `.Product__priceValue`（例: `81円`）
- 旧 `.ProductList__item` は0件になりやすい

## X穴場 cron パターン

スクリプト: `~/.hermes/scripts/warashibe-x-niche-price-scan.py`

| 項目 | 既定 |
|------|------|
| schedule | `0 10,21 * * *` |
| mode | `no_agent=true` |
| platforms | mercari only（速度） |
| keywords/run | 4（カテゴリ回転） |
| categories | gpu, gunpla, pokeka, lefty_iron, niche |
| output | Markdownダイジェスト + `~/.hermes/warashibe/price-scans/*.json` |

```text
cronjob(action='create', name='わらしべ穴場価格スキャン (X話題カテゴリ)',
  schedule='0 10,21 * * *', script='warashibe-x-niche-price-scan.py',
  no_agent=True, deliver='telegram:<chat_id>')
```

### キーワード運用メモ

- GPU: 「グラボ」「単体」を付けてPC本体ノイズを減らす
- ポケカ/ガンプラ: 相場透明化 → 価値誤認・完成品・箱傷限定が穴場寄り
- 左利き/レフティ: 供給薄・競合少・回転遅め
- Xで拾った具体名を `CATEGORY_POOL` に足す

## Pitfalls

1. **`q=` で0件** → `keyword=` に直す（最優先）
2. 連打で一時0件 → 間隔・1回語数を抑える
3. CloakBrowser は venv の hermes 経由（システムpythonに無いことがある）
4. 公開調査と購入アカウント操作を混ぜない
5. no_agent cron は **stdoutが配信文面**。空stdoutは無通知
6. skill 名 `warashibe-reselling` が3パス衝突 → このスキル or カテゴリ付きパスを使う

## Verification

- [ ] dry-run URL に `keyword=` が含まれる
- [ ] live mercari `limit 3` で items>0
- [ ] unit tests green
- [ ] cron スクリプト `py_compile` と手動1回でダイジェスト出力

## References

- `references/mercari-yahoo-selectors-2026.md` — セレクタと再現手順
- `references/x-niche-cron.md` — cronスクリプト契約・カテゴリ例
