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
| └ **国家情報局(NIA) 検証済みURL** | `cas.go.jp/jp/gaiyou/jimu/nic_nib.html` / `nic_kaisai.html` | 2026-07-31施行の国家情報会議設置法(令8法28)。`cas.go.jp/rss/news.xml` は404、HTML直取りが有効 |
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

## 検証済みURLカタログ (2026-10-07 実測)

`web_search` / `web_extract` が `markdownify` 欠落で全滅した場合、**in-process Python urllib が唯一の安定経路**である（terminal guard / browser 402 を回避）。以下は実測で到達確認済みのルート。

**到達する（直接HTTP 200）:**
| 機関 | URL | 備考 |
|---|---|---|
| 首相官邸 | `https://www.kantei.go.jp/` | `koshin/index.xml` 等RSSは全て404。HTML顶层から `href="/jp/105/discourse/\|statement/\|actions/..."` を収集して本文URLを確定する |
| 官邸 総理指示 | `/jp/105/discourse/YYYYMMDDshiji.html` | 北朝鮮launch等は `discourse/` 配下 |
| 内閣官房 NIA | `cas.go.jp/jp/gaiyou/jimu/nic_nib.html` / `nic_kaisai.html` | `rss/news.xml` は404 |
| 防衛省 | `mod.go.jp/j/rss/news.xml` / `update.xml` | RSS直接有効。記事URLは `/j/press/news/YYYY/MM/DDx.html` |
| 外務省 | `mofa.go.jp/mofaj/index.html` | `rss/mofa_news.xml` と `mofaj/toko/index.html` は **403**。トップページ直取りで新着一覧が可能 |
| 外交青書 | `mofaj/gaiko/report.html` | 青書PDF本体はリンク遷移+JS |
| 公安調査庁 | `moj.go.jp/psia/kaitenR8.html` (令和8年版) | `kankyo/` `annual.html` は404。**`kouan_naigai_index.html`**=最近の内外情勢、`kouan_kaiko_index.html`=回顧と展望索引 |
| NISC/NCO | `cyber.go.jp/index.html` | **`nisc.go.jp` は `cyber.go.jp` へ301転送。組織名は国家サイバー統括室（NCO）へ変更済**（実測2026-10-11）。`cyber.go.jp/news/index.html` は静的取得可だが**新着本文はJS動的**（`Loading...`）→記事単位は取得不能。詐欺注意書き（NCO名を騙る電話/メール）はトップ静的HTMLに出現 |
| CIA | `cia.gov/stories/story/...` | **The World Factbook は2026-02-04 sunset済み**。国別ページを前提にした収集は構造変更 |
| GCHQ / SIS | `gchq.gov.uk/` / `sis.gov.uk/` | `section/annual-report` は404 |
| MI5 | `mi5.gov.uk/` | **HTTP 403** — 恒久的に取得不能 |

**ハーネス側の障害（毎回同じで再試験しても無駄）:**
- `web_search` / `web_extract`: `No module named 'markdownify'` → Scrapling依存が死んでいる
- `browser_exec` cloud: `BILLING_ERROR 402` / local: profile lock
- `terminal`: Windows command length guard が全コマンドを落とす

| 内閣官房 NIA 開催状況 | `cas.go.jp/jp/gaiyou/jimu/nic_kaisai.html` | 令和8年度＝7/31（会議運営方針等）・9/25（上半期情勢認識/下半期重点事項） |
| 外務省 新着報道発表 | `mofa.go.jp/mofaj/index.html` → `href="/mofaj/press/release/pressit_000001_0NNNN.html"` | **トップHTML直取りで本文URLが採れる**。IDは `pressit_000001_` + 連番（10/10時点=04275〜04277）。談話は `danwa/pageit_000001_NNNNN.html`、外相メッセージは `la_c/m_ca_c/{国}/pageit_000001_NNNNN.html`。RSS(`rss/mofa_news.xml`)と `press_kaocho/index.html` は**404/403** |
| 日米外相電話会談(2026-10-10) | `mofa.go.jp/mofaj/press/release/pressit_000001_04277.html` | ICC制裁・沖縄県強盗殺人事件・日米同盟強化を3点確認できる一次資料 |

**重要な構造変化（実測 2026-10-11）:**
- 内閣は **高市早苗内閣**。第222回国会 所信表明演説 = 2026-10-05。官邸記事IDは `/jp/105/{discourse,statement,actions}/YYYYMMDD*.html`
- `mod.go.jp/j/rss/update.xml` と `news.xml` は** interchangeably 最終更新が数日〜1週間遅れる**ため、24h窓で0件でも「取得失敗」ではなく「本当に新着なし」と読むべき
- 防衛大臣 = 小泉。`/j/press/kisha/YYYY/MMDD{a,b}.html` に**記者会見の逐語録**( Noujen 会見{Q&A含む) がそのまま載る = 最良の情報源（`a`=大臣会見/`b`=報道官会見）
- 日米再編訓練移転は **2系統が同時並行**：固定翼(嘉手納→築城)/回転翼・ティルトロータ(MV-22, 普天間→霧島・種子島)。回数を控えると動向の追跡指標になる

**結論: 官公庁系は RSS + HTML直取り、内閣官房/公安調査庁は正規URL探索で十分カバーできる。ブラウザ・検索APIに依存しないこと。**
** StavilyDerived: `terminal` は Windows ガードで全コマンドを落とすため、HTTP収集は必ず `execute_code` 内の in-process urllib で行うこと。**

---

## 次回改善アクション

1. このスキルを `osint-agent` 系cronプロンプトに `skills: ["osint-fallback-routes"]` として付与
2. 失敗分類タグをcron出力JSONに含め、`scripts/cron_failure_patterns.py` 等で傾向分析
3. 直リンクPDFパターンを自治体・省庁ごとに `references/pdf-url-patterns.yaml` として蓄積