---
name: devspace-setup
description: "Install DevSpace MCP server and expose via Tailscale."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata.hermes.tags: [DevSpace, MCP, Tailscale, Codex]
metadata.hermes.related_skills: []
---

# DevSpace Setup Skill

DevSpace (`@waishnav/devspace`) を Windows (Git Bash) にセットアップし、Tailscale Serve 経由で Codex App から接続できるようにする。Node v24 環境での better-sqlite3 互換性問題を回避する手順を含む。

## When to Use

- "DevSpace をセットアップして" / "Codex App からローカルファイルを操作したい"
- "Tailscale 経由で MCP サーバーを公開したい"
- DevSpace が起動しない、better-sqlite3 エラーが出る

## Prerequisites

- Node.js `>=22.19 <27` (v24.19.0 確認済み)
- Git Bash (MSYS2) — PowerShell/cmd.exe は不可
- Tailscale 接続済み (`tailscale status` で確認)
- npm `allow-scripts=true` (better-sqlite3 ビルドに必要)

## How to Run

1. `skill_view` で本スキルを読み込む
2. `terminal` で手順を実行
3. `tailscale serve` でポート公開
4. バッチファイル作成でバックグラウンド起動

## Quick Reference

| コマンド | 目的 |
|----------|------|
| `npm config set allow-scripts=true` | better-sqlite3 ビルドを許可 |
| `npm install -g @waishnav/devspace --force` | DevSpace インストール |
| `tailscale serve --bg 7676` | Tailscale でポート公開 |
| `curl -s http://127.0.0.1:7676/mcp` | 動作確認 (401 なら成功) |

## Procedure

### 1. 事前設定

```bash
# better-sqlite3 のネイティブビルドを許可
npm config set allow-scripts=true

# 既存の壊れたインストールがあれば削除
cmd //c "rmdir /s /q \"%USERPROFILE%\\AppData\\Roaming\\npm\\node_modules\\@waishnav\""
```

### 2. DevSpace インストール

```bash
npm install -g @waishnav/devspace --force
```

`--force` は `EEXIST: file already exists` エラーを回避するため必須。

### 3. 設定ファイル作成

`~/.devspace/config.json`:
```json
{
  "projectRoots": ["C:/Users/<user>/Documents"],
  "port": 7676,
  "publicBaseUrl": "https://<tailscale-hostname>.ts.net"
}
```

`~/.devspace/auth.json`:
```json
{
  "ownerPassword": "devspace-<random>"
}
```

### 4. Tailscale で公開

```bash
tailscale serve reset
tailscale serve --bg 7676
```

### 5. バックグラウンド起動バッチ作成

`~/bin/devspace-start.bat`:
```bat
@echo off
set DEVSPACE_OAUTH_OWNER_TOKEN=<32文字以上のトークン>
cd /d "%USERPROFILE%\\AppData\\Roaming\\npm\\node_modules\\@waishnav\\devspace"
node dist\\cli.js serve
```

### 6. 起動確認

```bash
sleep 5 && curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:7676/mcp
# 401 なら認証待ち (正常)
```

## Pitfalls

- **Node v24 + better-sqlite3**: プロセス終了時に `node::RemoveEnvironmentCleanupHook` クラッシュが発生するが、稼働中は問題ない。終了後にプロゾンビが残る場合は `taskkill` で削除。
- **Tailscale Funnel の競合**: 既に他のサービスが 443 ポートを使っている場合 `listener already exists` エラーが出る。`tailscale serve reset` してから再設定。
- **DEVSPACE_OAUTH_OWNER_TOKEN**: 16文字以上必須。`openssl rand -hex 32` で生成推奨。
- **Windows バックグラウンド起動**: `cmd //c start` は現在のセッション終了と共にプロセスが終了する。常時起動にはタスクスケジューラへの登録が必要 (UAC で手動操作が必要)。

## Verification

```bash
netstat -ano | grep LISTENING | grep 7676
curl -s http://127.0.0.1:7676/mcp
```

期待出力:
```
TCP    127.0.0.1:7676   0.0.0.0:0   LISTENING   <PID>
{"error":"invalid_token","error_description":"Missing Authorization header"}
```

Codex App 側設定:
- Connector URL: `https://<tailscale-hostname>.ts.net/mcp`
- Auth Type: Bearer
- Token: `DEVSPACE_OAUTH_OWNER_TOKEN` の値
