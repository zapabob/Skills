---
name: pplx-cli
description: >
  Install and use Perplexity's pplx CLI for live web search and page-content fetch
  from the terminal. Use to search the web, look up current information or news,
  fetch a URL's content as text, or install and authenticate the pplx command.
  On Windows where the pplx binary is unavailable, falls back to direct Perplexity
  Sonar API calls via curl.
when_to_use: >
  Any request like: search the web for X, find the latest news about X, look up
  current events, use Perplexity to search, search with pplx, install the Perplexity
  CLI, fetch this URL, get the content of this page, read this webpage, restrict a
  web search to certain domains or dates.
tags: [perplexity, search, web, api, sonar]
---

# pplx-cli — Perplexity Web Search & Content Fetch

## Authentication

**必須:** `PERPLEXITY_API_KEY` を `~/.hermes/.env` に設定。

### API キーの取得（Google OAuth 再利用）

1. https://www.perplexity.ai/account/api にアクセス
2. **「Continue with Google」** でログイン（Google OAuth 再利用）
3. API キーを生成・コピー
4. `~/.hermes/.env` に追記:

```bash
PERPLEXITY_API_KEY=[REDACTED]
```

**注意:**
- `pplx auth login` は TTY 専用（非対話環境では使えない）
- 環境変数 `PERPLEXITY_API_KEY` が最優先
- Windows では pplx バイナリ未対応のため、環境変数認証が唯一の方法

## インストール（Linux/macOS）

```bash
# インストール（SHA-256検証済み、sudo不要）
curl -fsSL https://github.com/perplexityai/perplexity-cli/releases/latest/download/install.sh | sh

# 確認
pplx --version

# アップデート
pplx update
```

**対応:** macOS arm64, Linux x86_64, Linux arm64 **のみ**。
**インストール先:** `~/.local/bin/pplx`（`PPLX_INSTALL_PATH` で変更可）

## 使い方

### 1. Web 検索（pplx CLI 使用時）

```bash
pplx search web "検索クエリ"
```

**トークン節約モード（推奨）:**

```bash
pplx search web "メインクエリ" "追加の言い換え" \
  -n 5 --output-dir out --stdout-preview=200
```

- `--stdout-preview` は `--output-dir` なしだと無効（全文出力）
- `PPLX_OUTPUT_DIR` を設定すれば毎回 `--output-dir` 不要
- **出力契約:** 成功 = exit 0 + stdout に JSON1つ。失敗 = exit 1 + stderr に JSON エラー

**フラグ例:**
```bash
# ドメイン制限
pplx search web "query" --domains example.com,site.org

# 日付範囲（MM/DD/YYYY 形式！）
pplx search web "query" --published-after-date 01/01/2026 --published-before-date 06/30/2026

# 新しさフィルター（日付範囲と併用不可）
pplx search web "query" --recency-filter week
```

### 2. URL コンテンツ取得（pplx CLI 使用時）

```bash
pplx content fetch https://example.com/article
pplx content fetch https://example.com --no-cache
pplx content fetch https://example.com --html --output-dir out --stdout-preview=200
```

- `error` / `is_paywall` フィールドを確認してから `content` を信用する
- `--html`: crawler 経由の raw HTML（大量データ注意）

### 3. Windows フォールバック — Sonar API 直接呼び出し

Windows では pplx CLI が使えないため、Perplexity Sonar API を直接叩く:

```bash
# Web 検索＋回答生成
curl -s https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [
      {"role": "system", "content": "Be precise and cite sources."},
      {"role": "user", "content": "検索クエリ"}
    ],
    "max_tokens": 1024,
    "temperature": 0.2
  }' | jq .
```

**利用可能モデル:**
| モデル | 説明 |
|--------|------|
| `sonar-pro` | Web検索＋高品質回答（推奨） |
| `sonar` | 軽量Web検索＋回答 |
| `sonar-deep-research` | 深層リサーチ（時間・コスト大） |

### 4. Python ラッパー（Windows 推奨）

`~/.hermes/scripts/pplx-search.py` を作成して使い回す:

```python
#!/usr/bin/env python3
"""Perplexity Sonar API ラッパー（Windows対応）"""
import os, sys, json, urllib.request, urllib.error

API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not API_KEY:
    print("ERROR: PERPLEXITY_API_KEY not set", file=sys.stderr)
    sys.exit(1)

def search(query: str, model: str = "sonar-pro", limit: int = 5) -> dict:
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "回答は簡潔に。引用元を明記。"},
            {"role": "user", "content": query}
        ],
        "max_tokens": 2048,
        "temperature": 0.2
    }
    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": {"code": str(e.code), "message": e.read().decode()}}

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read().strip()
    if not query:
        print("Usage: pplx-search.py <query>", file=sys.stderr)
        sys.exit(1)
    result = search(query)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

## ハマりポイント（Pitfalls）

1. **`pplx auth login` は TTY 専用** — エージェント/CI では `PERPLEXITY_API_KEY` 環境変数を使う
2. **`--stdout-preview` は `--output-dir` が必須** — 単体では無効（全文出力になる）
3. **複数クエリ文字列は同じ検索の言い換え** — 別トピックは別コマンドで
4. **日付は MM/DD/YYYY 形式** — ISO 8601 非対応（例: `--published-after-date 07/01/2026`）
5. **`--recency-filter` と日付範囲は併用不可** — `BAD_REQUEST` が返る
6. **pplx CLI は Windows 非対応** — 代替として Sonar API 直呼び or Python ラッパー
7. **環境変数 `.env` の変更後はプロセス再起動** — agent 起動後に変更した場合は次セッションで反映

## 出力フォーマット

### pplx CLI（成功時）
```json
{"hits": [{"url": "...", "title": "...", "domain": "...", "snippet": "..."}], "total": 5}
```

### pplx CLI（エラー時）
```json
{"error": {"code": "AUTHENTICATION", "message": "...", "command": "search"}}
```
エラーコード例: `AUTHENTICATION`, `UNKNOWN_ARGUMENT`, `ARGUMENT_ERROR`, `BAD_REQUEST`

### 判断基準
| 状態 | 判定 |
|------|------|
| exit 0 + stdout に JSON | 成功 |
| exit 1 + stderr に JSON | 失敗 → `error.code` を分岐 |
| 401 Unauthorized | APIキー未設定または期限切れ |
| 402 Payment Required | クレジット不足 |
