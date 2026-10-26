---
name: warashibe-reselling
description: "わらしべ長者式せどり：1万円スタート→ブラウザ自動化でリサーチ/仕入れ/出品/発送/古物台帳を回すエンドツーエンドスキル。古物商許可申請・AI社員リロール・試算シート・発送API検証を含む。"
version: 1.0.0
author: hakua
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [reselling, sedori, browser-automation, antique-dealer, moa, kanban]
    category: autonomous-ai-agents
    related_skills: [ai-employee-org, browser-browser-use, hermes-agent, moa-fugu-orchestrator]
---

# Warashibe Reselling Skill

## 概要
- **開始資金**: 10,000円
- **手法**: ブラウザ自動化（`browser-browser-use` / `browser-use`）でメルカリ/ヤフオク/Amazon/ブックオフ/ハードオフ/EBAY を横断リサーチ → 利益率30%以上・回転14日以内のみ仕入れ → 自動出品・発送・古物台帳記帳
- **運用**: Hermes Kanban `sedori-ops` ボード + AI社員5役（secretary/researcher/buyer/lister/shipper/ledger）で完全自動化

## サブモジュール

| モジュール | 役割 | エントリーポイント |
|---|---|---|
| `license-package` | 古物商許可申請書類一式・警察署相談メール・営業所図面テンプレ | `scripts/license_package.py` |
| `ai-employee-reroll` | `ai-employees` プラグインを `sedori-` プレフィクスで複製・書き換え | `scripts/reroll_ai_employees.py` |
| `research-sheet` | Keepa + オークファン → 利益率/回転日数試算シート自動生成 | `scripts/research_sheet.py` |
| `shipping-label` | ヤマトB2 / ゆうプリ / ネコポス API 検証・ラベル自動発行 | `scripts/shipping_label.py` |

## 前提条件
- `hermes plugins enable browser-browser-use` または `browser-use` （BROWSER_USE_API_KEY 必須）
- Python 3.10+ / `playwright` / `openpyxl` / `requests` / `pandas`
- 古物商許可取得済み（東京都公安委員会＝警視庁管轄）

## クイックスタート
```bash
# 1. 古物商許可パッケージ生成
hermes skill run warashibe-reselling license-package --output ~/Documents/ops/sedori/license_pkg

# 2. AI社員リロール実行
hermes skill run warashibe-reselling ai-employee-reroll

# 3. リサーチ試算シート実行（キーワード指定）
hermes skill run warashibe-reselling research-sheet --keyword "Switch ゲームソフト" --budget 10000

# 4. 発送API検証
hermes skill run warashibe-reselling shipping-label --verify-only
```

## Kanbanボード構成
```
Board: sedori-ops
Columns:
  Backlog → Research → Buy Decision → Purchased → Inspection → Listing → Sold → Shipped → Closed
Assignees:
  researcher   : Research, Buy Decision
  buyer        : Purchased
  inspector    : Inspection
  lister       : Listing
  shipper      : Shipped
  ledger       : Closed (古物台帳記帳)
```

## 設定ファイル
- `config/targets.yaml` 対象プラットフォーム・カテゴリ・除外ワード
- `config/thresholds.yaml` 利益率・回転日数・リスクスコア閾値
- `config/apis.yaml` Keepa/オークファン/各発送API キー（.envから読込）

## 参照ファイル
- `references/keepa_api.md` Keepa Product Finder 使い方
- `references/aucfan_api.md` オークファンAPI仕様
- `references/yamato_b2.md` ヤマトB2クラウドAPI
- `references/japanpost_yuupri.md` 日本郵便ゆうプリAPI
- `references/necopos.md` ヤマトネコポスAPI
- `references/antique_dealer_tokyo.md` 東京都古物商許可要件まとめ