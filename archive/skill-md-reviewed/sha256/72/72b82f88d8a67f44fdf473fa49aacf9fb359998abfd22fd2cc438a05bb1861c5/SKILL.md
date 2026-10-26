---
name: windows-di[REDACTED_TOKEN]
description: C:ドライブ満杯からの復旧手順。安全に削除可能なキャッシュ類の特定と一括削除。
version: "1.0"
author: "Hermes Agent"
license: "MIT"
platforms: ["windows"]
metadata:
  hermes:
    tags: ["windows", "disk-cleanup", "c-drive", "devops", "recovery"]
    category: "devops"
---

# Windows C:ドライブ満杯復旧スキル

## When to Use
- `wmic logicaldisk where deviceid='C:' get size,freespace` で空き容量が 0-10GB 以下
- `No space left on device` / `OSError: [Errno 28] No space left on device` エラー
- pip install / cargo build / npm install がディスク不足で失敗
- **Docker Desktop / WSL が起動しない・ハングする（2026-08-08 実証）**: C: 空き 10GB 前後だと WSL2 VHDX が拡張できず、`docker info` が永遠にタイムアウト、`wsl -l -v` / `wsl -d docker-desktop -e true` も応答なし、Docker Desktop ログに `DockerDesktop/Wsl/CommandTimedOut`。先に `cmd.exe /c "dir C:\ /a | findstr 空き"` で空きを確認し、Temp/npm/pip キャッシュを削除してから再試行。詳細は `buzz-integration-hermes` スキルの "Windows Docker Desktop Daemon Recovery" 節を参照。

## 安全削除優先順位（影響なし・再生成可能）

| パス | 推定サイズ | 優先度 | 備考 |
|------|-----------|--------|------|
| `C:\\Users\\<user>\\.cache` | 数百 GB | **最高** | フォントキャッシュ・bcmap・json.gz 大量。完全安全。 |
| `C:\\Users\\<user>\\.unsloth` | 3-5 GB | 高 | unslothスタジオ環境。再インストール可能。 |
| `C:\\Users\\<user>\\.rustup` | 10-20 GB | 中 | `rustup clean` で削減可。ツールチェーン再DL可能。 |
| `C:\\Users\\<user>\\.cargo\\registry\\cache` | 5-15 GB | 高 | `cargo clean` で削除可。クレート再DL可能。 |
| `C:\\Users\\<user>\\.cargo\\git` | 5-10 GB | 中 | git checkout キャッシュ。再clone可能。 |
| `C:\\Users\\<user>\\.cargo-targets` | 5-15 GB | 中 | ビルド成果物。`cargo clean` で削除可。 |
| `C:\\Users\\<user>\\.cache\\huggingface` | 数-数十 GB | 高 | `HF_HOME` を D: 等へ移設推奨。再DL可能。 |
| `C:\\Users\\<user>\\AppData\\Local\\Temp` | 数-数十 GB | 高 | `del /s /q /f %TEMP%\\*` 安全。 |
| `C:\\Windows\\Temp` | 数 GB | 高 | `del /s /q /f C:\\Windows\\Temp\\*` 管理者で実行。 |
| `C:\\Users\\<user>\\AppData\\Local\\pnpm\\store` | 数-数十 GB | 中 | `pnpm store prune` または丸ごと削除。 |
| `C:\\Users\\<user>\\.cache\\codex-runtimes` | 数 GB | 中 | Codex Pythonランタイム。再DL可能。 |

## 追加発見: AppData\\Local 大型フォルダ（実測値 2026-08-06）

| パス | 実測サイズ | 優先度 | 削除/対処方法 |
|------|-----------|--------|--------------|
| `C:\\Users\\<user>\\AppData\\Local\\wsl` | **34 GB** | **最高** | `wsl --shutdown` → `Optimize-VHD` で縮小。WSL不要なら `wsl --unregister <distro>` で完全削除 |
| `C:\\Users\\<user>\\AppData\\Local\\VRChatCreatorCompanion` | **24.8 GB** | 高 | 不要なら丸ごと削除。VRChat創作活動中は保持、モデルはD/Eドライブへ移動 |
| `C:\\Users\\<user>\\AppData\\Local\\Programs` | **42.8 GB** | 高 | 中身確認必須。ポータブルアプリ多数。不要アプリ削除 |
| `C:\\Users\\<user>\\AppData\\Local\\Comfy-Desktop` | **7.3 GB** | 高 | ComfyUI Desktop本体+モデルキャッシュ。モデルはD/Eドライブ推奨、ジャンクション張り替え |
| `C:\\Users\\<user>\\AppData\\Local\\VRCT` | **3.2 GB** | 中 | VRChat関連キャッシュ。不要なら削除 |
| `C:\\Users\\<user>\\AppData\\Local\\Temp` | **6.2 GB** | **最高** | `del /s /q /f %TEMP%\\*` 完全安全 |
| `C:\\Users\\<user>\\AppData\\Local\\hermes` | **5.3 GB** | 中 | Hermesキャッシュ/ログ。古いログ削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\Google` | **5.6 GB** | 高 | Chromeキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\Microsoft` | **9.4 GB** | 中 | VS Code/Edgeキャッシュ等。一部削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\Docker` | **8.4 GB** | 高 | `docker system prune -a --volumes` で削減可 |
| `C:\\Users\\<user>\\AppData\\Local\\npm-cache` | **2.3 GB** | 高 | `npm cache clean --force` |
| `C:\\Users\\<user>\\AppData\\Local\\Perplexity` | **2.1 GB** | 高 | Perplexityアプリキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\Packages` | **2.2 GB** | 中 | UWPアプリ。不要アプリ削除で減らせる |
| `C:\\Users\\<user>\\AppData\\Local\\Unity` | **2.7 GB** | 中 | Unityキャッシュ/エディタ。古いバージョン削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\uv` | **1.4 GB** | 中 | `uv cache clean` または `UV_CACHE_DIR` 移設 |
| `C:\\Users\\<user>\\AppData\\Local\\go-build` | **1.1 GB** | 中 | `go clean -cache` |
| `C:\\Users\\<user>\\AppData\\Local\\cursor-updater` | **0.5 GB** | 低 | 自動更新キャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\electron` | **1.0 GB** | 低 | Electronアプリキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\GitHubDesktop` | **1.0 GB** | 低 | GitHub Desktopキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\Hypura` | **0.8 GB** | 低 | Hypura関連。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\LINE` | **1.9 GB** | 中 | LINEアプリキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\lm-studio-updater` | **0.8 GB** | 低 | LM Studio更新キャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\NVIDIA` | **0.6 GB** | 低 | NVIDIAドライバキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\OpenAI` | **1.1 GB** | 低 | OpenAI関連キャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\Package Cache` | **1.2 GB** | 低 | VS/インストーラキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\VoicemodV3` | **0.7 GB** | 低 | Voicemodキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Local\\app.worldmonitor.desktop` | **0.7 GB** | 低 | World Monitor Desktop。削除可 |

## 追加発見: AppData\\Roaming 大型フォルダ（実測値 2026-08-06）

| パス | 実測サイズ | 優先度 | 削除/対処方法 |
|------|-----------|--------|--------------|
| `C:\\Users\\<user>\\AppData\\Roaming\\Cursor` | **15.9 GB** | 高 | `Ctrl+Shift+P → Developer: Clear Cache` またはフォルダ削除 |
| `C:\\Users\\<user>\\AppData\\Roaming\\Claude` | **15.9 GB** | 高 | 設定 → データ削除、またはフォルダ削除 |
| `C:\\Users\\<user>\\AppData\\Roaming\\Python` | **5.5 GB** | 高 | `pip cache purge` または仮想環境整理 |
| `C:\\Users\\<user>\\AppData\\Roaming\\npm` | **3.2 GB** | 中 | グローバルnpmパッケージ整理。不要なら削除 |
| `C:\\Users\\<user>\\AppData\\Roaming\\Kiro` | **1.7 GB** | 中 | Kiroエディタキャッシュ。削除可 |
| `C:\\Users\\<user>\\AppData\\Roaming\\Zoom` | **0.7 GB** | 低 | Zoomキャッシュ。削除可 |

## 即時実行コマンド（管理者不要）

```cmd
:: 1. Python/uv/pip キャッシュ
pip cache purge 2>nul
uv cache clean 2>nul

:: 2. Python バイトコード
python -m compileall -f -q C:\Users\%USERNAME% 2>nul
del /s /q C:\Users\%USERNAME%\__pycache__ 2>nul

:: 3. Windows Temp
del /s /q /f C:\Windows\Temp\* 2>nul
del /s /q /f C:\Users\%USERNAME%\AppData\Local\Temp\* 2>nul

:: 3. Rust/cargo
cargo clean 2>nul
rustup clean 2>nul

:: 4. Node/pnpm/bun
npm cache clean --force 2>nul
pnpm store prune 2>nul
bun pm cache rm 2>nul

:: 5. HuggingFace キャッシュ移設（推奨）
setx HF_HOME D:\hf-cache
setx TRANSFORMERS_CACHE D:\hf-cache
robocopy C:\Users\%USERNAME%\.cache\huggingface D:\hf-cache /MIR /R:0 /W:0
rmdir /s /q C:\Users\%USERNAME%\.cache\huggingface

:: 6. .cache 丸ごと削除（最強・安全）
rmdir /s /q C:\Users\%USERNAME%\.cache

:: 7. .unsloth 削除
rmdir /s /q C:\Users\%USERNAME%\.unsloth

:: 8. uv temp/cache redirect（C:空きが極端に少ない場合も大規模DLを可能にする）
setx UV_CACHE_DIR D:\\uv_cache
:: 一時的にだけ使用する場合（cmd.exe）:
::   set UV_CACHE_DIR=D:\\uv_cache
::   set TMP=D:\\tmp
::   set TEMP=D:\\tmp

:: 9. 追加: AppData\\Local 大型フォルダ対処コマンド
:: WSL縮小（管理者PowerShellで実行）
:: wsl --shutdown
:: Optimize-VHD -Path "C:\\Users\\%USERNAME%\\AppData\\Local\\Packages\\CanonicalGroupLimited.UbuntuonWindows_*\\LocalState\\ext4.vhdx" -Mode Full

:: Dockerクリーンアップ
docker system prune -a --volumes 2>nul

:: ComfyUIモデル移動（D/Eドライブへ）→ ジャンクション張り替え
:: robocopy "C:\\Users\\%USERNAME%\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyGUI\\ComfyUI\\models" "D:\\ComfyUI_models" /MIR /R:0 /W:0
:: rmdir /s /q "C:\\Users\\%USERNAME%\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyGUI\\ComfyUI\\models"
:: mklink /J "C:\\Users\\%USERNAME%\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyGUI\\ComfyUI\\models" "D:\\ComfyUI_models"

:: Cursor/Claudeキャッシュクリア（アプリ内コマンド推奨、またはフォルダ削除）
:: rmdir /s /q "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Cursor" 2>nul
:: rmdir /s /q "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Claude" 2>nul

:: 10. 空き容量確認
wmic logicaldisk where deviceid='C:' get size,freespace /format:value
```

## 期待効果
- **数十〜百 GB 解放** 見込み
- 実行後、pip install / cargo build / hermes plugin インストールが正常化

## 即効性のある安全な削減アクション（推定 30-40 GB 回復・2026-08-06 実測）

```cmd
:: 1. 最優先・完全安全: 一時ファイル削除
del /q /f /s "%LOCALAPPDATA%\Temp\*"
for /d %p in ("%LOCALAPPDATA%\Temp\*") do rd /s /q "%p"

:: 2. npmキャッシュ
npm cache clean --force

:: 3. pipキャッシュ
pip cache purge

:: 4. Dockerクリーンアップ
docker system prune -a --volumes

:: 5. WSLディスク縮小（管理者PowerShellで実行必須）
wsl --shutdown
Optimize-VHD -Path "C:\Users\%USERNAME%\AppData\Local\Packages\CanonicalGroupLimited.UbuntuonWindows_*\LocalState\ext4.vhdx" -Mode Full

:: 6. Cursor/Claudeキャッシュクリア（アプリ内コマンド推奨、またはフォルダ削除）
:: Cursor: Ctrl+Shift+P → "Developer: Clear Cache"
:: Claude: 設定 → データ削除
:: 即時削除する場合:
rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Cursor" 2>nul
rmdir /s /q "C:\Users\%USERNAME%\AppData\Roaming\Claude" 2>nul

:: 7. ComfyUIモデルをD/Eドライブへ移動＋ジャンクション作成
robocopy "C:\Users\%USERNAME%\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\models" "D:\ComfyUI_models" /MIR /R:0 /W:0
rmdir /s /q "C:\Users\%USERNAME%\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\models"
mklink /J "C:\Users\%USERNAME%\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyGUI\ComfyUI\models" "D:\ComfyUI_models"

:: 8. VRChatCreatorCompanion削除（VRChat創作してない場合のみ）
rmdir /s /q "C:\Users\%USERNAME%\AppData\Local\VRChatCreatorCompanion" 2>nul

:: 9. Google/Perplexity/Chromeキャッシュ削除
rmdir /s /q "C:\Users\%USERNAME%\AppData\Local\Google" 2>nul
rmdir /s /q "C:\Users\%USERNAME%\AppData\Local\Perplexity" 2>nul

:: 10. uv cache 移設 + TMP/TEMP 移設（巨大パッケージDL時）
setx UV_CACHE_DIR D:\uv_cache
setx TMP D:\tmp
setx TEMP D:\tmp

:: 11. 空き容量確認
```

## 注意事項
- `.cache` / `.unsloth` / `Temp` は**完全安全**（再生成・再DL可能）
- `.rustup` / `.cargo` は再DL時間がかかるが安全
- `C:\Windows` 直下や `C:\Program Files` は**触らない**
- 削除前に `wmic logicaldisk` で空き容量確認

## Pitfall: uvのtemp展開はC:を消費する（venv先が別ドライブでも）

**症状:** `UV_CACHE_DIR` をD:/H:に設定しても、`C:\Users\<user>\AppData\Local\uv\cache\.tmp*` に書き込もうとして **No space left on device** で失敗する。

**原因:** uvはwheelの展開（extract）時に一時ファイルを`~/.cache/uv/`以下に作成する。`UV_CACHE_DIR`が別ドライブを指していても、展開中の一時ファイルはデフォルトでC:に置かれる。

**対策（3つの方法、推奨順）:**

**A. `TMP`/`TEMP` 環境変数で一時ディレクトリを変更（最も確実）**
```bash
# bash (MSYS) から実行する場合
export MSYS_NO_PATHCONV=1   # パス変換防止
export UV_CACHE_DIR="D:\\uv_cache"
export TMP="D:\\tmp"
export TEMP="D:\\tmp"
export TMPDIR="D:\\tmp"
mkdir -p /d/tmp /d/uv_cache
uv pip install 巨大パッケージ --python "D:\\venv\\Scripts\\python.exe"
```

**B. cmd.exeでセットしてから実行（MSYSのパス変換問題も回避）**
```cmd
set TMP=D:\tmp
set TEMP=D:\tmp
set UV_CACHE_DIR=D:\uv_cache
uv pip install 巨大パッケージ
```

**C. 永続設定（setx）**
```cmd
setx UV_CACHE_DIR D:\uv_cache
setx TMP D:\tmp
setx TEMP D:\tmp
```
※setxは新しいコマンドプロンプトから有効

## Pitfall: MSYS (git-bash) のパス変換（`/h/` → `C:\h\`）

**症状:** `uv venv /d/vllm-win` → `C:\d\vllm-win` に作成される（D:ではなくC:）。`UV_CACHE_DIR="/h/uv_cache"` → `C:\h\uv_cache` を参照する。

**原因:** MSYSがネイティブWindowsプログラムに引数を渡す際、`/h/xxx` を `C:\h\xxx` に自動変換する（MSYSのパス変換ルール）。

**対策:**
1. `export MSYS_NO_PATHCONV=1` を事前に設定（最も簡単）
2. Windowsネイティブパスを使う: `"H:\\venv\\Scripts\\python.exe"`
3. cmd.exeでラップ: `cmd.exe /c "uv pip install ... --python D:\venv\Scripts\python.exe"`

## 検証
```cmd
wmic logicaldisk where deviceid='C:' get size,freespace /format:value
```
空き 10 GB 以上で作業継続可能。20 GB 以上で余裕。