---
name: vrchat-hakua-slideshow
description: VRChat screenshots and hakua TTS into a narrated slideshow MP4 for intros or social posts.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [vrchat, tts, video, media, hakua]
    category: media
---

# VRChat Hakua Memory Slideshow

VRChatスクリーンショットとはくあの声でHermes-agent機能を紹介するスライドショーMP4を作成するスキル。

## When to Use

- 新機能やアップデートをVRChat写真＋はくあの声で紹介したい時
- Hermes-agentの記憶統合・Ebbinghaus機能を視覚的に説明したい時
- X/TwitterやDiscordに投稿する紹介動画が必要な時

## Prerequisites

- irodori-TTS（`irodori_tts_synthesize`）が利用可能
- VRChat screenshotsが `~/Pictures/VRChat/` に存在
- ffmpegがインストール済み（パス通っている）
- 縦長1920×1080のVRChat画像を推奨

## How to Run

### 1. 素材確認

最新VRChatショットを確認：
```bash
py -3 -c "import glob, os; files=sorted(glob.glob(os.path.expanduser('~/Pictures/VRChat/**/*.png'), recursive=True)); print(files[-1])"
```

### 2. ナレーション生成

`text_to_speech` で各セクションの音声を生成：

- オープニング（3-8秒）
- 機能説明1（8-12秒）
- 機能説明2（8-12秒）
- 設定方法（6-10秒）
- クロージング（8-12秒）

**重要**: `output_path` で `.wav` / `.ogg` を指定（本体に残留させる）。

### 3. 音声連結

```python
import subprocess, os

audios = ["01.ogg", "02.ogg", "03.ogg", "04.ogg", "05.ogg"]
with open("list.txt", "w") as f:
    for a in audios:
        f.write(f"file '{a}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", "list.txt", "-c", "copy",
    "combined.ogg"
], check=True)
```

### 4. 動画生成（ffmpegスライドショー）

```python
import subprocess, os

images = [...]  # 画像パスのリスト（jpg化推奨）
durations = [7.8, 10.9, 11.7, 8.9, 10.2]  # 各音声の秒数

# 各セグメント生成
for i, (img, dur) in enumerate(zip(images, durations), 1):
    seg = f"seg_{i:02d}.mp4"
    vf = f"zoompan=z='min(1.12,1+0.12*on/({dur}*30))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p"
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", img, "-t", str(dur),
        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-an", seg
    ], check=True)

# 連結
with open("concat.txt", "w") as f:
    for seg in segments:
        f.write(f"file '{seg}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", "concat.txt", "-i", "combined.ogg",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-shortest", "output.mp4"
], check=True)
```

## Quick Reference

| ステップ | 内容 | 所要時間 |
|---------|------|---------|
| 素材確認 | 最新VRChat画像取得 | 5秒 |
| 音声生成 | text_to_speech×N | 各3-5秒 |
| 音声連結 | ffmpeg concat | 1秒 |
| セグメント生成 | ffmpeg zoompan×N | 各8-20秒 |
| 最終結合 | ffmpeg concat+aac | 3秒 |

## Pitfalls

- **Voice source:** `text_to_speech` and `irodori_tts_synthesize` can ignore the `tts.irodori.voice` config and return a non-Hakua voice even when the setup looks correct. For Hakua-voiced MP4s, use `aituber_onair_speak(provider="irodori", voice="hakua", play=false, output_path="<absolute .wav>")` as the canonical audio source. This is the only confirmed path that actually returns the Hakua voice profile in this environment.
- **音声の`.wav`化**: 上記 canonical 呼び出しでも `output_path` の拡張子を `.wav` にすると実ファイルが得やすい。`.ogg` で `text_to_speech` を呼ぶと本体生成が不定になることがある。
- **画像形式**: PNGのままでもffmpegは読めるが、jpg化してから使うと安定。
- **音声長と画像表示時間**: 各セグメントの秒数は対応する音声の実際のDurationに合わせる（`ffmpeg -i audio.wav`で確認）。
- **動画バックエンド**: `video_generate` はバックエンド未設定だと失敗するため、ffmpeg直接が確実。
- **出力先**: `~/.hermes/x_posts/` で生成し、投稿前に `~/.hermes/lm-twitterer/media/` へコピーする。lm-twittererはmedia dir配下しか受け付けない。
- **lm-twitterer投稿**: `dry_run=true` でテキストとmedia acceptanceを確認してから `dry_run=false` で投稿する。

## Voice intelligibility and duration control

- ユーザーが「早口で不明瞭」と感じた場合は、まず `aituber_onair_speak(provider="irodori", voice="hakua", play=false, output_path="<absolute .wav>")` を正規経路として使い、発話速度を少し下げる。既存WAVを `atempo=0.84` で処理する方法は、ピッチを保ったまま迅速に改善版を作る代替手段。
- ただし、単純にスロー化すると90秒制限を超える。90秒以内が要件なら、発話速度を元に戻すのではなく、`silenceremove` で長い無音区間だけを短縮する。実例では `stop_silence=0.08`、`stop_duration=0.22`、`-35dB` 閾値で、約107秒のスロー音声を約89.8秒へ収めた。
- 音声だけでなく、最終MP4も必ず `ffprobe` で検証する。`-shortest` だけでは動画側のフレーム境界により音声より少し長くなることがあるため、厳密な上限がある場合は `-t 89.80` のように安全余裕を持って指定する。
- 仕上がりの報告は、尺、速度調整、無音短縮の有無、解像度、音声形式を短く明示し、完成ファイルへのリンクを最優先する。ユーザーが聞き取りやすさを指摘した場合、長い手順説明より修正版を先に提示する。

### 90秒以内の音声整形例

```bash
# 速度を落としたWAVを、無音の長い間だけ短縮
ffmpeg -y -i hakua-slow.wav \\
  -af "silenceremove=start_periods=1:start_duration=0.22:start_threshold=-35dB:stop_periods=-1:stop_duration=0.22:stop_threshold=-35dB:stop_silence=0.08" \\
  -ar 48000 -ac 1 hakua-90s.wav

# 音声の実測値を確認してから映像と結合
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 hakua-90s.wav
ffmpeg -y -stream_loop -1 -i source-video.mp4 -i hakua-90s.wav \\
  -map 0:v:0 -map 1:a:0 -c:v libx264 -crf 20 -pix_fmt yuv420p \\
  -c:a aac -b:a 192k -t 89.80 -movflags +faststart output.mp4
```

## Verification

```bash
# 動画・音声ストリームと尺を確認
ffprobe -v error -show_entries format=duration:stream=codec_name,codec_type,sample_rate,channels,width,height -of default=nw=1 output.mp4

# 厳密な尺の確認（90秒未満であること）
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 output.mp4
```

## Notes

- VRChat写真は `~/Pictures/VRChat/` に日付フォルダで蓄積
- はくあの声は `provider: "irodori"`, `voice: "hakua"` が標準
- x投稿用MP4のテンプレートとして再利用可能
