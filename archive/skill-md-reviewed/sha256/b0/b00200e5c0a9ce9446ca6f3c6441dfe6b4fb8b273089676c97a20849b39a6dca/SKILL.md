---
name: vrchat-voicevox-autostart
category: gaming
description: VOICEVOXとVRChat OSCを自動起動して自律エージェントを立ち上げるスキル
tags: [vrchat, voicevox, osc, autonomous]
---

# VRChat + VOICEVOX 自動起動スキル

## 使い方
1. VOICEVOXを指定パスで起動（仮想ケーブル経由）
2. VRChat OSC接続を確認
3. 自律エージェント（chatbox・avatar制御・定期報告）を開始
4. マルチモーダルキャプチャ（カメラ＋マイク＋Whisper STT）を定期実行
5. 動的データセット（重複なし）を蓄積

## 推奨Cron設定
- スケジュール: every 2m
- モデル: CodexGPT5.5low（Grok制限時のハンドオーバー）
- スキル: vrchat-voicevox-autostart, vrchat-autonomous-agent, xurl, multimodal-capture

## 起動コマンド例
```powershell
start "" "%USERPROFILE%\AppData\Local\Programs\VOICEVOX\VOICEVOX.exe"
```

## 関連スキル
- vrchat-autonomous-agent
- vrchat-osc

## 注意
- VOICEVOXは http://127.0.0.1:50021 で待機する必要がある
- VRChat側でOSCを有効化しておくこと
- 仮想ケーブルマイク（VB-Cableなど）経由で音声出力するとVRChat内で自然な声として聞こえる
- Cron + Heartbeatで永続的に動かす場合、Grokのレート制限時はCodexGPT5.5lowなどの代替モデルにハンドオーバーする
- Hermes cron の `script` は `~/.hermes/scripts/` からの相対パスで指定する。例: `vrchat_start_tts_watchdog.py`。`C:/Users/...` の絶対パスは拒否される。
- 起動検知ウォッチドッグを `no_agent=true` で使う場合、通常時は stdout を空にする。stdout が非空だと配送されるため、起動遷移・エラーなど通知したい時だけ print する。
- `--force-test` のような強制テスト後は、状態ファイルを実プロセス状態に戻す。テストで `running=true` を保存すると、次の本当の VRChat 起動遷移を取り逃がす場合がある。
- Cron から音声再生 helper を呼ぶ場合、cron の Python と対話シェルの Python が違うことがある。`sounddevice` / `soundfile` など音声依存が必要な helper は、`HAKUA_TTS_PYTHON` のような環境変数または既知の Python 実行ファイル候補で明示的に起動し、`python -m py_compile` と `--force-test` と cron 即時実行で検証する。

## 拡張パターン（このセッションで確立）
- Cronジョブ（every 2m）で定期的にchatbox報告・VOICEVOX音声・X投稿を実行
- xurlスキルと連携してVRChat活動の宣伝投稿を自動化
- 会話機能：周囲の発言を検知してchatbox/VOICEVOXで自然に応答
- モデル耐性：Grok制限時にCodexGPT5.5lowへシームレスに切り替え

## 関連ファイル
- references/virtual-cable.md — 仮想ケーブル設定の詳細
- references/cron-heartbeat-pattern.md — 永続的自律運用のCron/Heartbeat設計

## Virtual Cable Microphone Setup (重要)
User uses VOICEVOX output routed through virtual audio cable (e.g. VB-Cable) as microphone input in VRChat.
- This allows synthesized speech to be heard as the user's voice in VRChat.
- When generating audio, ensure the output device or routing sends to the virtual cable.
- Autonomous agent should prefer this routing for natural voice manifestation instead of system default speakers.
- Update playback logic in future agent scripts to target the virtual cable device when available.
