---
name: warashibe-reselling
description: "わらしべ長者式せどり自動化: 少額資金からブラウザ自動化でリサーチ→仕入れ→出品→利益確定→再投資を複利で回す"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [reselling, arbitrage, browser-automation, compound-growth, mercari, yahoo-auctions, amazon, bookoff, hardoff, ebay]
    category: autonomous-ai-agents
    related_skills: [ai-employee-org, hermes-agent, browser-browser-use]
---

# Warashibe Reselling Skill

**わらしべ長者式せどり** — 1万円スタートでブラウザ自動化（Hermes `browser` ツール）を使い、複数マーケットプレイスを横断して「安く買って高く売る」サイクルを複利で回す自律エージェント運用スキル。

## When to Use

- 少額資金（1〜5万円）からせどりを始め、利益を再投資して資産を増やしたい
- メルカリ・ヤフオク・Amazon・ブックオフオンライン・ハードオフ・eBay 等を横断リサーチしたい
- 古物商許可取得済み（または取得予定）で、法令遵守しながら自動化したい
- AI社員（secretary/researcher/lister/shipper/ledger）に役割分担させたい

## Prerequisites

- Hermes `browser` ツール（Browserbase経由）が動作すること
- 古物商許可証（都道府県公安委員会）取得済み
- 各マーケットプレイスのアカウント（メルカリ・ヤフオク・Amazonセラー等）
- 発送用資材・プリンター・計量器
- 利益管理用 Google Sheets / Notion / SQLite

## Core Workflow (7 Phases)

```
┌─────────────┐   ┌──────────────┐   ┌────────────┐   ┌────────┐   ┌─────────┐   ┌────────────┐   ┌──────────┐
│ ① Research  │→│ ② Calculate  │→│ ③ Decision │→│④ Purchase│→│⑤ Listing│→│⑥ Ship   │→│⑦ Reinvest│
│  (browser)  │   │  (Python)    │   │ (Rules)   │   │(browser)│   │(browser)│   │(browser) │   │ (Ledger) │
└─────────────┘   └──────────────┘   └────────────┘   └────────┘   └─────────┘   └────────────┘   └──────────┘
     ↓                ↓                   ↓                 ↓           ↓            ↓              ↓
  複数サイト      手数料・送料      スコア≥閾値      購入ボタン    テンプレ    ラベル印刷    確定利益を
  横断検索        梱包費込みで      なら自動承認      クリック      出品        追跡登録      次期予算へ
  キーワード/     利益率≥30%                                      自動生成
  カテゴリ指定    利益額≥500円
```

### Phase Details

| Phase | Agent | Tools | Key Logic |
|-------|-------|-------|-----------|
| **① Research** | `researcher` | `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type` | キーワード・カテゴリ・価格帯で各サイト検索、商品カードから「現在価格・状態・送料・出品者評価」抽出 |
| **② Calculate** | `researcher` | `execute_code` (Python) | `profit = sell_price * (1 - fee_rate) - shipping - packing - buy_price` → `roi = profit / buy_price` |
| **③ Decision** | `secretary` | `delegate_task` + rules | `roi >= 0.3 AND profit >= 500 AND score >= 70` → 自動承認、 else human gate |
| **④ Purchase** | `buyer` | `browser` (click/keys) | カート→購入手続き→支払い確定（**実運用は手動承認ゲート推奨**） |
| **⑤ Listing** | `lister` | `browser` + template | タイトル生成（SEOキーワード込）、説明文テンプレ、画像最適化、価格設定 |
| **⑥ Ship** | `shipper` | `browser` + carrier API | ラベル発行（ゆうパケット/ネコポス/宅急便コンパクト）、追跡番号登録、購入者通知 |
| **⑦ Reinvest** | `ledger` | `file` / `terminal` | 損益通算CSV/DB更新 → 確定利益を次期予算に加算 → Secretary に次のサイクル指示 |

## Marketplace Parameters (内部設定)

```yaml
marketplaces:
  mercari:
    fee_rate: 0.10
    payment_fee: 0.02  # 決済手数料目安
    shipping_options:
      - name: ゆうパケットポスト
        max_size: A4/3cm/2kg
        cost: 215
      - name: 宅急便コンパクト
        max_size: 専用箱/25cm/2kg
        cost: 450
    search_url: "https://www.mercari.com/search?keyword={kw}&price_min={min}&price_max={max}&status=on_sale"
    selectors:
      item_card: "[data-testid='item-cell']"
      price: ".mer-price__number"
      title: ".mer-item-thumbnail__title"

  yahoo_auctions:
    fee_rate: 0.088
    payment_fee: 0.01
    shipping_options:
      - name: ねこポス
        max_size: A4/2.5cm/1kg
        cost: 210
      - name: 宅急便コンパクト
        cost: 450
    search_url: "https://auctions.yahoo.co.jp/search/search?p={kw}&aucminprice={min}&aucmaxprice={max}"

  amazon:
    fee_rate: 0.15  # カテゴリ平均
    fba_fee: 300  # 目安
    search_url: "https://www.amazon.co.jp/s?k={kw}&rh=p_36%3A{min}00-{max}00"

  bookoff_online:
    # 買取専用（仕入れ先）
    buyback_url: "https://www.bookoffonline.co.jp/kaitori/"

  hardoff:
    # 店舗/宅配買取専用
    buyback_url: "https://www.hardoff.co.jp/kaitori/"

  ebay:
    fee_rate: 0.1235
    shipping_options:
      - name: eBay International Shipping
        cost: 0  # 買い手負担
    search_url: "https://www.ebay.com/sch/i.html?_nkw={kw}&_udlo={min}&_udhi={max}"
```

## Profit Calculation Formula

```python
def calculate_profit(buy_price, sell_price, marketplace, shipping_method, pack_cost=50):
    mp = MARKETPLACES[marketplace]
    fee = sell_price * mp['fee_rate']
    payment_fee = sell_price * mp.get('payment_fee', 0)
    shipping = next(s['cost'] for s in mp['shipping_options'] if s['name'] == shipping_method)
    profit = sell_price - fee - payment_fee - shipping - pack_cost - buy_price
    roi = profit / buy_price if buy_price else 0
    return {"profit": profit, "roi": roi, "breakdown": {"fee": fee, "shipping": shipping, "pack": pack_cost}}
```

**合格ライン**: `roi >= 0.30` (30%) **AND** `profit >= 500` 円

## Scoring Rules (Phase ③)

| Factor | Weight | Detail |
|--------|--------|--------|
| 利益率 ROI | 30% | ≥30%で満点、線形減点 |
| 利益額 | 20% | ≥2000円で満点 |
| 回転日数予測 | 20% | Keepa/オークファン相場から推定、≤14日で満点 |
| 出品者評価 | 15% | ★4.5以上・取引100件以上で満点 |
| 商品状態 | 15% | 「未使用に近い」>「目立った傷なし」>「やや傷汚れあり」 |

**スコア ≥ 70** で自動購入承認、`delegate_task` で `buyer` に引き継ぎ。

## Kanban Board Structure

```
Board: warashibe-reselling
Lanes:
  backlog          → ① Research 完了・未判断
  research_done    → ② Calculate 完了
  buy_decision     → Secretary が判断（自動/手動）
  purchased        → ④ Purchase 完了
  inspection       → 到着・検品・撮影
  listing_draft    → ⑤ Listing 下書き
  listed           → 出品中
  sold             → ⑥ Ship 待ち
  shipped          → 発送済み・追跡中
  completed        → ⑦ Reinvest 完了・利益確定
```

## Agent Role Mapping (ai-employee-org 連携)

| Role | Profile | Primary Phase |
|------|---------|---------------|
| Secretary | `secretary` | ③ Decision, ⑦ Reinvest 指示 |
| Researcher | `job-seeker` → repurpose | ① Research, ② Calculate |
| Buyer | `delivery-worker` → repurpose | ④ Purchase |
| Lister | `job-recruiter` → repurpose | ⑤ Listing |
| Shipper | `delivery-worker` | ⑥ Ship |
| Ledger | `self-improver` → repurpose | ⑦ Reinvest, 古物台帳記帳 |

## Browser Automation Patterns (Hermes `browser` ツール)

```python
# 共通ヘルパー
async def search_marketplace(browser, url, selectors):
    await browser_navigate(url)
    await browser_snapshot()
    # スクロールして全件読み込み
    for _ in range(3):
        await browser_scroll(direction="down")
        await asyncio.sleep(1)
    await browser_snapshot()
    # 抽出
    items = []
    for idx in extract_indices(selectors['item_card']):
        items.append({
            "title": await browser_get_text(title_idx),
            "price": parse_price(await browser_get_text(price_idx)),
            "url": await browser_get_attribute(link_idx, "href"),
        })
    return items

# メルカリ検索例
mercari_items = await search_marketplace(browser,
    "https://www.mercari.com/search?keyword=ニンテンドースイッチ&price_min=1000&price_max=10000",
    MERCARI_SELECTORS)
```

## 古物台帳自動記帳 (法的必須)

```csv
取得日,取得先氏名住所,品名,数量,取得価格,販売日,販売先氏名住所,販売価格
2026-07-15,メルカリ出品者A(東京都),Nintendo Switch 本体,1,8000,2026-07-20,購入者B(大阪府),12000
```

- `ledger` エージェントが `kanban_complete` フックで自動追記
- 3年間保存・警察立入検査時に即提示可

## Pitfalls & Mitigations

| Pitfall | Mitigation |
|---------|------------|
| メルカリ/ヤフオク非公式API・スクレイピングは規約違反リスク | **Hermes `browser` ツール（人間模倣操作）に留める**、公式API申請並行 |
| 購入ボタン自動クリックで誤購入 | **手動承認ゲート**をSecretaryに挟む（`kanban_block`） |
| 送料誤計算で赤字 | 実測重量・サイズで計算、梱包後再計量ルーチン |
| 在庫切れ・キャンセル率上昇 | 出品者評価・発送速度をスコアに組み込み、閾値以下はスキップ |
| 古物台帳漏れ | `ledger` エージェントを Kanban 完了フックに**強制紐付け** |
| アカウント凍結リスク | 複数アカウント分散・IPローテーション・操作間隔ランダム化 |

## Verification Checklist

- [ ] `hermes plugins enable browser-browser-use` 完了
- [ ] 古物商許可証コピーを `~/Documents/ops/warashibe/license.pdf` 保存
- [ ] Kanban ボード `warashibe-reselling` 作成
- [ ] 5役職プロファイルに `warashibe-reselling` スキルインストール
- [ ] 初回キーワードリスト（`keywords.yaml`）作成
- [ ] 利益計算テスト（既知商品で手計算と比較）
- [ ] 手動承認ゲート動作確認（Secretary → Buyer）

## References

- `references/marketplace-params.yaml` — 手数料・送料・セレクタ定義
- `references/keywords.yaml` — 検索キーワード・カテゴリ・価格帯プリセット
- `references/ledger-template.csv` — 古物台帳テンプレート
- `scripts/calculate_profit.py` — 利益計算CLI（`execute_code` から呼び出し可）
- `scripts/kanban_hooks.py` — 完了時フック（台帳記帳・再投資予算更新）

## Templates

- `templates/listing/mercari.md` — メルカリ出品テンプレ
- `templates/listing/yahoo_auctions.md` — ヤフオク出品テンプレ
- `templates/listing/amazon.md` — Amazon出品テンプレ
- `templates/listing/ebay.md` — eBay出品テンプレ

## Next Steps

1. `hermes skills install warashibe-reselling` でスキル有効化
2. 各プロファイルにインストール: `hermes -p secretary skills install warashibe-reselling` 等
3. `references/keywords.yaml` に最初の狙い目キーワードを追加（例: 「ニンテンドースイッチ」「レゴ」「フィギュア」「古本 セット」「工具 セット」）
4. Secretary に最初のタスク投入: `hermes kanban create "初期リサーチ: 1万円以内で仕入れ可能な高回転商品20件" --assignee secretary --priority 1`