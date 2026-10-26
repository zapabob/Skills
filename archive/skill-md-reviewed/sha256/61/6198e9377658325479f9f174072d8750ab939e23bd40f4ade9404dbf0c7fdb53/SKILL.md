---
name: irodori-tts-windows-startup
description: Recover Windows TTS and verify spare-GPU synthesis.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Windows, TTS, CUDA, Diagnostics, Verification]
    category: mlops
---

# Windows音声合成の復旧とGPU余力検証

WindowsのIrodori起動障害を切り分け、既存LLMを維持しながらGPU余力で音声を生成・検証する。GPUメモリを予約する手順ではなく、全音声ワーカーの切替や音質を保証しない。既存のHermesプラグインとPowerShellハーネスを再利用し、重複する起動器や依存を増やさない。

## When to Use

- 「Irodoriが起動しない」「pydantic_coreのimportが失敗する」
- 「音声はできたのに呼び出しが戻らない」
- 「GPUの空き余力で音声合成したい」
- 「CUDA設定なのに実際はCPUで生成している」

## Prerequisites

- 正規Hermesチェックアウトと、隣接する `irodori-tts-server`。
- サーバー自身の `.venv/Scripts/python.exe` に `irodori_openai_tts` がインストール済み。
- `scripts/windows/start-irodori-tts.ps1`、`scripts/windows/invoke-irodori-tts.ps1`、`plugins/irodori_tts/core.py`。非自明な起動・文字コード・出力処理はこの既存実装を使う。
- PowerShell。GPU使用にはNVIDIAドライバーとCUDA対応PyTorch。音声検証にはFFmpeg/FFprobe。
- テスト環境変数: `PYTHONUTF8=1`、`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`。
- 既存の認証が必要ならラッパーは `IRODORI_API_KEY` を利用する。値を表示・保存せず、認証ファイルや他プロファイルを変更しない。
- GPU設定の実体: `IRODORI_MODEL_DEVICE`、`IRODORI_CODEC_DEVICE`、`IRODORI_MODEL_PRECISION`、`IRODORI_CODEC_PRECISION`、`IRODORI_PRELOAD`。

## How to Run

正規Hermesチェックアウトを作業ディレクトリとして、次を `terminal` から実行する。8089は既存CPU処理を8088に残す場合の例であり、使用前に空きポートと要求状況を確認する。

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/start-irodori-tts.ps1 -Port 8089
hermes config set tts.irodori.base_url http://127.0.0.1:8089
hermes irodori-tts status
```

Windowsのコマンド長制限でツールが拒否されたら、同じ許可範囲を `execute_code` の `pathlib` と時間制限付き `subprocess` で処理する。同じ失敗を繰り返さず、サンドボックスや承認を解除しない。

## Quick Reference

- 起動: `scripts/windows/start-irodori-tts.ps1`
- 合成: `scripts/windows/invoke-irodori-tts.ps1`
- 状態: `hermes irodori-tts status`
- 既定状態URL: `http://127.0.0.1:8088/health`
- 別ポート状態URL: `http://127.0.0.1:8089/health`
- 別ポート合成URL: `http://127.0.0.1:8089/v1/audio/speech`
- 接続設定: `tts.irodori.base_url`
- 起動引数: `-RepoDir`、`-HostName`、`-Port`、`-ModelDevice`、`-CodecDevice`、`-ModelPrecision`、`-MinimumFreeGpuMemoryMiB`
- 自動選択: GPU 0の空き6144 MiB以上、かつサーバーvenvでCUDA利用可能
- 自動精度: CUDAモデルはBF16、CPUモデルはFP32、コーデックはFP32固定
- 隔離起動: `.venv/Scripts/python.exe -I -m irodori_openai_tts`
- ログ: `%LOCALAPPDATA%/hermes/logs/irodori-tts-8089-stdout.log`、`irodori-tts-8089-stderr.log`

## Procedure

1. **失敗点と対象を記録する。** `read_file` / `search_files` で起動・合成・プラグイン経路を確認し、変更前の `git status --porcelain` を `terminal` で取得する。Python import、サーバー起動、待機キュー、合成、親プロセス終了、配送を別の判定にする。機密値を含む環境一覧は出力しない。

2. **VRAMと既存要求を実測する。** `terminal` で以下を実行し、`execute_code` と `psutil` で対象ポートのLISTEN/ESTABLISHED、所有プロセスの完全なargv・作業ディレクトリを照合する。処理中なら停止せず別の空きループバックポートを選ぶ。既存LLMの割当を減らさない。

   ```text
   nvidia-smi --query-gpu=name,memory.free,memory.used,utilization.gpu --format=csv -i 0
   ```

3. **Python環境混在を再現・分離する。** IrodoriのPython 3.10がHermesのPython 3.11用パッケージを読んでいる場合、まずimport元を比較する。`PYTHONPATH` / `PYTHONHOME` の継承あり・隔離起動を比較し、親の環境を変更せず `-I` を起動境界に置く。正規Hermesチェックアウトから、次の短い診断を `terminal` で実行する。最初は継承環境、次は隔離環境を調べる。

   ```text
   ../irodori-tts-server/.venv/Scripts/python.exe -c "import sys,pydantic,pydantic_core,torch;sys.stdout.write(str((sys.version,sys.executable,pydantic.__file__,pydantic_core.__file__,torch.__version__,torch.cuda.is_available())))"
   ../irodori-tts-server/.venv/Scripts/python.exe -I -c "import sys,pydantic,pydantic_core,torch;sys.stdout.write(str((sys.version,sys.executable,pydantic.__file__,pydantic_core.__file__,torch.__version__,torch.cuda.is_available())))"
   ```

   隔離だけで正常なら、パッケージ欠落と決めつけて再インストールしない。CUDA不足時もmanifestを確認してから対応extraを選ぶ。これらはimportとCUDA可用性の診断で、実際のGPU合成や空きVRAMの証拠ではない。

4. **GPU余力判定付きで起動する。** `How to Run` の共有ランチャーを使う。自動選択は余力不足・CUDA未対応時にCPUへ移るが、明示的な `-ModelDevice cuda -CodecDevice cuda` は不足時に失敗する。6144 MiBは実測後に改訂した起動条件であり、普遍的な必要量や常時予約ではない。既存の正常サーバーは判定前に再利用するため、同じポートへの再実行でCPUからGPUへ変更されるとは考えない。

5. **合成と呼び出し終了を両方確認する。** 既存voice・モデル・認証を維持して短い試験音声を作る。`text_to_speech` には `provider="irodori"` を指定する。プラグインCLIを確認する場合は、保存済みUTF-8入力ファイルから次を `terminal` で実行する。出力名は既存成果物を上書きしないよう事前確認する。

   ```text
   hermes irodori-tts synthesize --input-path tmp/probes/input.txt --output-path output/media/irodori-smoke.wav --format wav --voice hakua
   ```

   `hakua` は既存の参照声を利用する例。別の承認済みvoiceなら維持する。入力作成には `write_file` を使い、日本語JSONをシェルの引数へ直接埋め込まない。

6. **生成済みなのに戻らない場合を切り分ける。** POST 200と成果物があるなら、モデルの遅さだけを疑わない。PowerShell終了後も常駐子が捕捉パイプを保持するとEOF待ちが起きる。共有プラグインの `tempfile.TemporaryFile()` 出力捕捉を使い、入力用 `TemporaryDirectory` 内の名前付きログは避ける。後者はWindowsの `WinError 32` を起こした。HTTP 503が待機上限由来なら、音声成功や起動障害として扱わず、既存要求の終了後に別試験として再検証する。

7. **接続先を設定し、要求単位で読み戻す。** `hermes config set tts.irodori.base_url http://127.0.0.1:8089` の後、プラグインの `settings()` と状態を確認する。共有合成ラッパーと `hermes irodori-tts start` が設定されたホスト・ポートを起動側へ渡すことも確認する。新しいHermesプロセスの標準 `tools.tts_tool.text_to_speech_tool` と、既に稼働中のデスクトップ/ワーカーを別々に試験する。出力先の未使用を確認してから、正規チェックアウトで次を `terminal` から実行する。

   ```text
   .venv/Scripts/python.exe -c "import sys;from tools.tts_tool import text_to_speech_tool;sys.stdout.write(text_to_speech_tool('こんにちは',output_path='output/media/irodori-standard-smoke.wav',provider='irodori',speed=1.0))"
   ```

   返された `success`、`provider`、実際の `file_path` を記録する。配送時に拡張子が `.ogg` へ変わる場合もあるため、指定した出力名ではなく返された実ファイルを検査する。CLI成功を、全デスクトップ/ワーカーの切替成功へ昇格しない。

8. **同一要求のGPU証拠を結び付ける。** healthの `loaded=true`、標準TTSの成功、返された実ファイル、要求時間帯の `model_device=cuda` / `codec_device=cuda` 合成ログを照合する。生成中のGPUメモリ測定を残す。生成前後の単発値だけではピーク値を主張しない。下記を `terminal` で実行して、解読可能・非無音かを確認する。非空のJSONエラー応答を音声として納品しない。

   ```text
   ffprobe -v error -show_entries format=duration,size:stream=codec_name,sample_rate,channels -of json output/media/irodori-smoke.wav
   ffmpeg -hide_banner -i output/media/irodori-smoke.wav -af volumedetect -f null -
   ```

9. **安全なコールドスタートを別検証する。** 対象が今回作成したサーバーで、argv・ポート・作業ディレクトリが一致し、処理中要求がない場合だけ、そのプロセスを停止して標準TTSの自動起動を試す。既存CPUサーバーやLLM、広いプロセスツリーを終了しない。条件を満たせなければ未検証として残す。起動済み生成時間、モデル読み込み時間、キュー待ちを混同しない。

10. **回帰と証拠の境界を保存する。** 挙動変更は再現試験を先に実行し、該当Windowsテスト・関連プラグイン・dispatch試験、構文、lint、対象差分を確認する。`_docs` に日時、ソースhash、実際の要求先、音声hash、未検証項目を記録する。過去の失敗や誤ったGPU判定を消さず、訂正を追記する。比較対象のない性能向上や、未取得レビューの合格を主張しない。

## Pitfalls

- **WDDM:** PyTorchの `mem_get_info` が他プロセス使用分を十分反映せず、NVIDIA測定より大きい空きを示す場合がある。起動予算にはドライバー側の実測を使う。
- **設定と実行は別:** CUDAのhealth、provider名、GPUと名付けたファイルだけでは実行証拠にならない。この作業でも一つの通常ツール呼び出しは旧CPU経路だった。長寿命経路が残る原因を未特定のまま、キャッシュ不具合と断定しない。
- **余力判定は予約ではない:** 他GPU処理や長い入力で需要が変わる。常時GPU使用、OOM回避、LLMへの無影響を保証しない。GPU 0とBF16という実装前提は別機種で再確認する。
- **単なるhealth成功:** `loaded=false` は起動準備のみ。合成要求や親呼び出しの成功とは別。
- **Windowsパス/文字コード:** nativeプログラムへは実Windowsパスを渡す。MSYSの `/tmp` はnative curlから読めない。UTF-8、BOMなしで保存する。
- **タイムアウト:** 成果物が存在しても、呼び出し終了や最新E2Eは未合格の場合がある。初回成功で後の503・打切りを打ち消さない。
- **レビュー失敗:** 委任停止、401、接続失敗、空のレビュー結果を「指摘なし」にしない。権限を迂回せず、未取得と記録する。
- **試験自体の障害:** fixtureの未定義変数や後処理の例外を、対象挙動の欠落を示すREDと混同しない。失敗箇所を切り分け、期待した原因で落ちる再現試験を確認してから製品側を変更する。
- **証拠範囲:** 回帰用の合成スタブは実音声や物理GPUの証拠ではない。対象テストの緑、全体CI、音質、配信、全ワーカー切替、コミット済みHEADの証拠を分ける。

## Verification

**完了判定は一つ: 同じ試験要求について、標準Hermes呼び出しが成功して戻り、返された音声が解読可能・非無音で、要求時間帯の実行ログがモデル/コーデックのCUDA使用を示すこと。** コールド起動も対象にした場合は、その経路の同じ証拠を追加する。health、設定値、ファイル名だけの確認では合格にしない。

回帰試験は正規チェックアウトで次を `terminal` から実行する。`PYTHONUTF8=1` と `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` を指定し、実際の件数と終了コードを記録する。これは物理GPU実行の代替ではない。

```text
.venv/Scripts/python.exe -m pytest -o addopts= tests/scripts/test_irodori_startup_windows_live.py tests/plugins/test_irodori_tts_plugin.py tests/plugins/test_irodori_hakua_voice.py tests/tools/test_tts_plugin_dispatch.py -q --tb=short
```
