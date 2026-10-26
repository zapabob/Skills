---
name: osint-fallback-routes
description: OSINT一次情報取得失敗時の代替ルートパターン集。cronジョブやサブエージェントで再利用可能。
tags: [osint, fallback, resilience, skill]
version: 1.0
---

# OSINT Fallback Routes — 一次情報アクセス失敗時の代替手段

## 目的
cronジョブやサブエージェントで公式サイト・PDF・APIへのアクセスが失敗した際、即座に代替経路を試せるようにパターン化する。

## 基本原則
1. **推測で埋めない** — 取得失敗箇所は「失敗」として明記し、代替取得結果のみを報告
2. **冗長経路を3層用意** — 公式Web → 直リンクPDF/公式SNS → e-Gov/GovAPI → サードパーティ集約
3. **失敗理由を記録** — タイムアウト/403/課金/構造変更などを分類して次回改善に繋げる

---

## 代替ルートカタログ

### 1. 厚労省・省庁PDF・通達・告示
| 正攻法 | 代替1: 直リンク | 代替2: 公式X/note | 代替3: e-Gov法令API | 代替4: 国会会議録検索 |
|---|---|---|---|---|
| `mhlw.go.jp` サイト内検索 | 既知PDF直URL (`/content/.../xxx.pdf`) | `@MHLWitter` / 厚労省note | `https://elaws.e-gov.go.jp/api/1/lawdata/{law_id}` | `https://kokkai.ndl.go.jp/api/` |
| 失敗例: 課金/403/リダイレクトループ | 失敗例: URL変更 | 失敗例: ツイート未掲載 | 失敗例: 法令番号不明 | 失敗例: キーワード不一致 |

**実装Tips:**
```python
# PDF直リンク既知パターン
pdf_patterns = [
    "https://www.mhlw.go.jp/content/{year}{month}{day}-{docid}.pdf",
    "https://www.mhlw.go.jp/content/{bureau}/{docid}.pdf",
    "https://www.mhlw.go.jp/stf/newpage_{id}.html",  # HTML版
]
# 公式X検索
search_query = f"site:x.com @MHLWitter {keyword} PDF"
# e-Gov法令API (要法令ID/公布番号)
law_api = "https://elaws.e-gov.go.jp/api/1/lawdata/{law_id}"
```

### 2. 最高裁・裁判所判決・決定
| 正攻法 | 代替1: 裁判所Web | 代替2: LEX/DB・Westlaw | 代替3: 裁判所公式X |
|---|---|---|---|
| `courts.go.jp` 検索 | `https://www.courts.go.jp/app/hanrei_jp/detail?id={id}` | 有料DB (cronでは原則不使用) | `@courts_jp` |

### 3. 自治体公式ページ・条例・告示
| 正攻法 | 代替1: 直リンクPDF | 代替2: 公式X/LINE | 代替3: e-Gov条例API |
|---|---|---|---|
| `city.xxx.lg.jp` サイト内検索 | 既知パス `/soshiki/{dept}/{id}.html` | `@city_xxx_official` | `https://elaws.e-gov.go.jp/api/1/ordinancedata/{id}` |

### 4. 国会・法案・予算・会議録
| 正攻法 | 代替1: 国会会議録API | 代替2: 衆議院/参議院公式X |
|---|---|---|
| `kokkai.ndl.go.jp` 検索 | `https://kokkai.ndl.go.jp/api/meeting?keyword={kw}` | `@shugiin` `@sangiin` |

### 5. 統計・オープンデータ (e-Stat, RESAS, data.go.jp)
| 正攻法 | 代替1: API直叩き | 代替2: CKAN API | 代替3: GitHub公式リポ |
|---|---|---|---|
| `e-stat.go.jp` / `data.go.jp` | `https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData` | `https://data.go.jp/api/3/action/package_show` | `github.com/{ministry}/{dataset}` |

### 6. 国際機関・外国政府 (WHO, UN, US Gov等)
| 正攻法 | 代替1: 公式API | 代替2: 公式X/RSS | 代替3: 学術ミラー |
|---|---|---|---|
| 公式サイト検索 | 多くはREST API公開 | `@WHO` `@UN` `@CDCgov` | `github.com/{org}/{dataset}` |

### 7. 国家情報機関系の公開OSINT
日本政府・情報機関の公式公開情報をレポートに含める際のソースマップ。全て公開資料のみを対象とする(非公開情報・工作・内部資料は対象外)。

**日本側:**
| 機関 | 公式サイト | 主な公開物 | 備考 |
|---|---|---|---|
| 首相官邸 / 国家安全保障局(NSS) | `kantei.go.jp` | 国家安全保障戦略・プレスリリース | 防衛・外交方針の一次資料 |
| **国家情報局(NIA) NEW** | `cas.go.jp/jp/gaiyou/jimu/nic_nib.html` | 国家情報会議開催状況・設置法概要・局長人事 | **2026年7月31日発足（令和8年法律第28号）**、内調を発展的に改組、首相直属の国家情報会議事務局、初代局長 原和也氏 |
| 内閣情報調査室(CIRO) | `cas.go.jp` (内閣官房内) | 情報機能に関する公開説明・予算資料 | 詳細公開は限定的、国家情報局へ改組済み |
| 内閣サイバーセキュリティセンター(NISC) / **国家サイバー統括室(NCO)** | `nisc.go.jp` / `cyber.go.jp` | サイバーセキュリティ戦略・月例報告 | 2025年発足の「内閣サイバー情報局」への改編動向も注視、NCOはNISC発展的改編 |
| 公安調査庁 | `moj.go.jp/psia` | 内外情勢の回顧と展望(年次)・機関誌 | テロ・国際情勢分析の公開資料 |
| 防衛省 | `mod.go.jp` | 防衛白書・防衛力整備計画・統合防衛戦略 | 中国・北朝鮮・ロシア分析の一次資料 |
| 外務省 | `mofa.go.jp` | 外交青書・広報資料・国家安全保障戦略関連 | 国際情勢の公式見解 |

**海外主要情報機関の公開物:**
| 機関 | 公式サイト | 主な公開物 |
|---|---|---|
| CIA (米) | `cia.gov` | The World Factbook・公開レポート |
| DIA (米) | `dia.mil` | 公開インテリジェンス報告 |
| GCHQ / MI5 / MI6 (英) | `gchq.gov.uk` / `mi5.gov.uk` / `sis.gov.uk` | 年次脅威評価・公開広報資料 |
| 韓国国情院(NIS) / 豪ASIO等 | 各国公式サイト | 年次脅威評価の公開部 |

**収集パターン:**
```python
# 国家情報機関系の検索クエリ例
queries = [
    "site:kantei.go.jp 国家安全保障 発表",
    "site:cas.go.jp 国家情報局 NIA",
    "site:nisc.go.jp サイバーセキュリティ 戦略",
    "site:moj.go.jp/psia 内外情勢の回顧と展望",
    "site:mod.go.jp 防衛白書 PDF",
    "site:cia.gov world factbook Japan",
    "GCHQ annual threat report PDF",
]
# 年次物は「前年度版」が出ているかを確認し、最新版のみ採用
```

**注意:**
- 「国家情報局」等の名称は組織改編(例: 内閣サイバー情報局・情報集約機関構想)により変わり得るため、必ず公式サイトで現行組織名を確認
- 機密・非公開情報へのアクセス・工作・不正入手は一切行わない。**公開されている公式発表のみ**をOSINTとして扱う
- 中国・ロシア・北朝鮮の情報機関は公式公開物が限定的なため、二次資料は明確に「二次情報」とラベル付け
- **2026年7月31日発足の国家情報局(NIA)**は内閣情報調査室(CIRO)を発展的に改組したものであり、首相を議長とする国家情報会議の事務局を兼務。公式ページは `https://www.cas.go.jp/jp/gaiyou/jimu/nic_nib.html` と開催状況 `nic_kaisai.html`

---

## cronジョブ組み込みテンプレート

プロンプトに以下を必ず含める:

```text
【一次情報取得プロトコル】
- 公式サイト → 直リンクPDF → 公式X/note → e-Gov/GovAPI の順で試行
- いずれも失敗時は「取得不能: {理由}」と明記し、推測で補完しない
- 代替ルート成功時は「代替取得: {ルート名}」と明記
- 取得失敗があってもcron自体は正常終了 (ok) とする
```

---

## 失敗分類タグ (ログ用)

| タグ | 意味 | 対応 |
|---|---|---|
| `BILLING_ERROR` | スクレイピング課金不足 | 直リンク/公式X/e-Govへ即切替 |
| `HTTP_403` / `HTTP_429` | アクセス制限/レート制限 | ヘッダ追加/待機/代替ルート |
| `REDIRECT_LOOP` | リダイレクトループ | 直リンク既知パターンを試行 |
| `STRUCTURE_CHANGED` | DOM/URL構造変更 | サイトマップ/RSS/公式Xで新URL発見 |
| `PDF_CORRUPT` | PDF破損/暗号化 | HTML版/テキスト版/公式X要約を探索 |
| `AUTH_REQUIRED` | ログイン必須 | 公開情報のみ対象とし「取得不能」記録 |

---

## 次回改善アクション

1. このスキルを `osint-agent` 系cronプロンプトに `skills: ["osint-fallback-routes"]` として付与
2. 失敗分類タグをcron出力JSONに含め、`scripts/cron_failure_patterns.py` 等で傾向分析
3. 直リンクPDFパターンを自治体・省庁ごとに `references/pdf-url-patterns.yaml` として蓄積