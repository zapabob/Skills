---
name: local-avatar-tts-pipeline
description: Local TTS audio pipeline for avatar/streaming use cases — buffer synthesized audio, zip on threshold, and route to WebSocket clients without live push.
version: 0.1.0
author: Hermes Agent
tags: [tts, irodori, aituber, avatar, pipeline, zip, buffer]
---

# Local Avatar TTS Pipeline

Canonical pattern for buffering locally synthesized TTS audio, packaging it on threshold, and feeding avatar frameworks without forcing live WebSocket delivery.

## When to Use

- irodoriTTS で CPU 合成した音声を後段（AITuber OnAir / SillyTavern / VRChat）に渡したい。
- 音声ファイルがある一定数を超えたら zip に固めたい。
- `audio_ws` などの即時 push 配信を使わず、バッファ优先＋zip 納品にしたい。
- ローカル Linux/Windows で外部クラウド TTS を使わずに音声資産を蓄積したい。

## What This Skill Covers

- `plugins/irodori_tts/audio_buffer.py` を使った WAV バッファ運用
- `aituber_onair` の `synthesize_speech()` 前段／後段への最小差分介入
- `sillytavern` サブモジュールの状態確認と橋渡し
- zip 閾値の設計指針

## What This Skill Does NOT Cover

- irodoriTTS サーバーの起動／CPU フォールバック（ → `irodori-tts-windows-startup` skill）
- VRChat OSC 音声配信（ → `vrchat-voicevox-autostart` skill）
- クラウド TTS プロバイダの選択（fishaudio / OpenAI 等）

## Prerequisites

- irodoriTTS サーバーが起動している（`irodori-tts-windows-startup` skill 参照）。
- `plugins/irodori_tts`, `plugins/aituber_onair` / `plugins/sillytavern` が登録済み。
- Python 3.12+ と `zipfile` 標準ライブラリ。

## Quick Reference

```text
plugins/irodori_tts/
  audio_buffer.py       # AudioBuffer / add_audio() / maybe_zip() / buffer_status()
  __init__.py           # irodori_tts_buffer_add / buffer_zip / buffer_status ツール

plugins/aituber_onair/core.py
  synthesize_speech()   # 合成後に audio_buffer へ追加 + maybe_zip() + audio_ws_push_wav()
```

## Procedure

### 1. バッファの初期化と確認

```bash
# Hermes の tool として実行
irodori_tts_buffer_status
# → {"buffer_dir": ".../audio-buffer", "files": N, "bytes": N, ...}
```

バッファ先は `~/.hermes/workspace/irodori-tts/audio-buffer`。
閾値は環境変数で変更可能:
- `HERMES_IRODORI_BUFFER_MAX_FILES` (default 100)
- `HERMES_IRODORI_BUFFER_MAX_BYTES` (default 200MB)
- `HERMES_IRODORI_BUFFER_MAX_AGE` (default 3600s)

### 2. 手動追加と手動 zip

```bash
irodori_tts_buffer_add path=/tmp/some.wav
irodori_tts_buffer_zip
```

### 3. aituber_onair を介した自動経路

`aituber_onair_speak` は以下を実行する:
1. `_synthesize_irodori()` / `_synthesize_voicevox()` で WAV を生成
2. `audio_buffer.add_audio(file_path)` でバッファに追加
3. `audio_buffer.maybe_zip()` で閾値超過時に zip 化
4. `audio_ws_push_wav(file_path)` で WebSocket 配信（zip はpushしない）

ユーザーが `バッファzipはaudio_wsでpushしない` を指示した場合、
`zip_result.get("zipped")` が真なら audio_ws broadcast をスキップする実装に切替える。

### 4. SillyTavern サブモジュールの状態確認

```bash
sillytavern_status
# → source_present, git_head, node_modules_present, healthy
```

サブモジュールは `vendor/SillyTavern/`。pin されたリビジョンが `package.json` + `node_modules` と一致していることを確認。

## Pitfalls

- **PowerShell env var override**: irodori サーバーの CPU フォールバックはプロセスレベル env var で上書きする。`.env` の `auto` / `true` をファイル編集するより、launch 側の export で制御する。
- **Preload crash**: `IRODORI_PRELOAD=true` はサーバー起動時に SIGSEGV を引き起こす。`false` にして lazy load にさせる。
- **audio_ws の broadcast spoof**: zip ファイルは WAV バイナリではないので、audio_ws 配信前に MIME 判定を入れる。`synthesize_speech()` は zip 生成後に通常 WAV だけを push する。
- **SillyTavern の process control**: `plugins.entries.sillytavern.allow_process_control: true` と `allow_network: true` が必要。
- **Buffer dir の cross-profile 干渉**: `get_hermes_home()` はアクティブ profile に依存する。複数 profile から同じ buffer を触ると競争が起きるので、運用上は single-writer を守る。

## Invariants

- zip 化後も個別 WAV は削除しない（`maybe_zip()` は zip 生成のみ行う）。
- `synthesize_speech()` の戻り値 `result["file_path"]` は常に最终合成 WAV を指す。
- `plugins/irodori_tts/audio_buffer.py` は `plugins/irodori_tts/__init__.py` からツールとして再エクスポートされる。

## Related Skills

- `irodori-tts-windows-startup` — irodori サーバー起動と CPU フォールバック
- `vrchat-voicevox-autostart` — VRChat + VOICEVOX 音声配信
- `vrchat-autonomy` — VRChat アバター自律制御（OSC / chatbox）
