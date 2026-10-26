---
name: windows-silent-install
description: Windows 上でのサイレントインストール手順。`start /wait` はタイムアウトを超えるため使わず、PowerShell `Start-Process -Wait` をバックグラウンドで実行し、`process(action=poll)` で完了監視する。
version: "1.0"
author: "Hermes Agent"
license: "MIT"
platforms: ["windows"]
metadata:
  hermes:
    tags: ["windows", "install", "silent", "docker", "setup"]
    category: "devops"
---

# Windows サイレントインストール手順

## When to Use
- Docker Desktop など GUI インストーラを無人インストールしたいとき
- PowerShell 非対話インストールをバックグラウンドで実行し、完了を追いたいとき

## ダウンロード手順

Windows では `/c/Users/...` を PowerShell に渡すと `C:\c\Users\...` に変換される。
`Invoke-WebRequest` の `-OutFile` には `C:\\Users\\...` 形式で渡す。
bash から `curl.exe` を使う場合、保存先は MSYS 経由で成功するケースと失敗するケースがあるので、PowerShell 経由を優先する。

## PowerShell を bash から呼ぶときの注意点

Hermes の `terminal` は git-bash/MSYS2 で動作するため、PowerShell ワンライナーを呼ぶときは bash の変数展開に注意する。

### `$env:` のエスケープ

bash は `$env:VAR='val'` の中の `$env` をシェル変数展開しようとする。
`$env` が未定義の場合 `:VAR='val'` に化けて PowerShell 側でエラーになる。

**対策1: `\$` でエスケープ（推奨）**

```bash
# bad — bash が $env を展開
powershell.exe -Command "$env:CHANNEL='beta'; irm ... | iex"

# good — $ をエスケープ
powershell.exe -NoProfile -Command "\$env:CHANNEL='beta'; irm https://... | iex"
```

**対策2: bash の一重引用符で囲む**

```bash
# bash 一重引用符内では $ は展開されない
# 内側の ' は ''（引用符終了→一重引用符→再開）で表現
powershell.exe -NoProfile -Command '$env:CHANNEL=''beta''; irm ... | iex'
```

### `irm ... | iex` パターン（PowerShell スクリプト直接実行）

公式インストーラが PowerShell ワンライナーで提供されている場合:

```bash
# 変数なし
powershell.exe -NoProfile -Command "irm https://example.com/install.ps1 | iex"

# 環境変数でチャンネル指定
powershell.exe -NoProfile -Command "\$env:MY_CHANNEL='beta'; irm https://... | iex"
```

### -NoProfile 推奨

```bash
powershell.exe -NoProfile -Command "..."   # ◯ 起動が速く副作用なし
powershell.exe -Command "..."               # △ プロファイル読み込みあり
```

## インストール実行手順

1. **フォアグラウンド禁止**: `terminal(background=false)` の `start /wait ...` はタイムアウト上限に引っかかる。
2. **バックグラウンド実行**: 次の形で実行する。

```powershell
# PowerShell args は入れ子の " を避けるため bash 側で変数に分ける
```

3. **完了監視**: `process(action='poll', session_id='<id>')` で `status` が `running` ではなくなるまで待つ。
4. **再起動が必要な場合**: `Start-Process ... -Wait` はコマンド完了を待つだけでエクスプローラ等の再開は待たない。必要なら、明示的に再起動を適用する。
5. **初回起動の確認**: インストーラ完了後、`docker --version` があればエンジン初期化が必要なことが多い。

## 検証
```powershell
docker --version
docker info
```

## Scripts
- `scripts/verify-docker-install.ps1`: インストール後の Docker Desktop 状態確認