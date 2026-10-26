---
name: vrchat-random-photo-tweet
description: Post a random VRChat photo with Hakua voice to X.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [VRChat, IrodoriTTS, Hakua, X]
---

# Random VRChat Photo Tweet

このスキルは、`Pictures/VRChat` 以下から写真をランダム選択し、Irodori TTS の `hakua` 音声で短い日本語ナレーションを作り、Twitter/X互換のMP4を生成して `lm-twitterer` のPython APIから投稿する。投稿先はXであり、画像だけの投稿やドライランで終わらせず、ユーザーが明示的に投稿を依頼した場合は実投稿結果を確認する。`hermes lm-twitterer` サブコマンドが登録されていない環境があるため、投稿はプラグインの `core.post()` を直接呼び出す。

## When to Use

- 「VRChatの写真をランダムに選んではくあの声でツイートして」
- 「VRChatのおはツイを作ってXに投稿して」
- 「irodoriTTSで写真付き動画を投稿して」
- 「VRChat写真からランダム投稿を実行して」

## Prerequisites

- Windows、Hermesリポジトリの `.venv`。
- 写真フォルダ: `C:\Users\<user>\Pictures\VRChat`（サブディレクトリを含む）。
- Irodori TTSサーバー: `http://127.0.0.1:8088`。`/health` が200で、`voices/hakua.ogg` が存在すること。
- `ffmpeg` と `ffprobe` がPATHにあること。
- `plugins/lm-twitterer/core.py` と、認証済みの `~/.hermes/.env`。認証確認には `core.auth_check()` を使う。
- lm-twittererの依存関係（`twitter-openapi-python`、`tweepy-authlib`）が投稿用Python環境に入っていること。

## How to Run

Irodori TTSサーバーの起動確認＋スクリプト実行を、`terminal` ツールで行う。

```bash
# 1. Irodoriサーバーが動いてなければ起動
curl.exe -m 5 -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:8088/health || (
  cd /c/Users/downl/Documents/New\ project/irodori-tts-server &&
  nohup ./.venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088 > /dev/null 2>&1 &
  sleep 15 # 冷起動待機
)

# 2. スクリプト起動（MSYSパス回避のためリポジトリにコピーしてから実行）
cp /c/Users/downl/.hermes/skills/social-media/vrchat-random-photo-tweet/scripts/vrchat_random_tweet.py scripts/vrchat_random_tweet_run.py
HERMES_REPO_ROOT=/c/Users/downl/Documents/New\ project/hermes-agent \
  ./.venv/Scripts/python.exe scripts/vrchat_random_tweet_run.py
```

`HERMES_REPO_ROOT` 未指定時はカレントがリポジトリルートとみなされる。実行前に投稿文と `dry_run=False` を確認する。

## Quick Reference

- 写真: `Pictures/VRChat` を再帰探索し、画像拡張子 `.png`, `.jpg`, `.jpeg`, `.webp` からランダム選択
- TTS endpoint: `POST http://127.0.0.1:8088/v1/audio/speech`
- TTS payload: `model=irodori-tts`, `voice=hakua`, `response_format=wav`
- MP4: H.264、AAC、`yuv420p`、`+faststart`
- メディア保管先: `~/.hermes/lm-twitterer/media/`
- 投稿API: `core.post("", text=..., media_paths=[filename], dry_run=False)`
- 認証確認: `core.auth_check()`

## Procedure
## Procedure

### 統合スクリプト（推奨）

1. **Irodoriサーバーを確認/起動する**。`/health` が200でなければ、バックグラウンドで起動する。
   ```bash
   cd /c/Users/downl/Documents/New\ project/irodori-tts-server
   nohup ./.venv/Scripts/python.exe -m irodori_openai_tts --host 127.0.0.1 --port 8088 > /dev/null 2>&1 &
   # 15〜30秒ほど待機し、健康応答を確認
   for i in 1 2 3; do sleep 10; curl.exe -m 3 -sS http://127.0.0.1:8088/health && break; done
   ```
   起動に失敗した場合はそこで止め、後続の処理に入らない。

2. **統合スクリプトを実行する**。MSYSパス変換を回避するため、スクリプトをリポジトリにコピーしてから `terminal` で起動する。
   ```bash
   cp /c/Users/downl/.hermes/skills/social-media/vrchat-random-photo-tweet/scripts/vrchat_random_tweet.py scripts/vrchat_random_tweet_run.py
   HERMES_REPO_ROOT=/c/Users/downl/Documents/New\ project/hermes-agent \
     ./.venv/Scripts/python.exe scripts/vrchat_random_tweet_run.py
   ```
   このスクリプトは以下を自動実行する:
   - `Pictures/VRChat` からランダムな画像を選択
   - `core.auth_check()` でX認証確認
   - Irodori `/health` 確認
   - `POST /v1/audio/speech` ではくあWAV音声生成
   - `ffmpeg` でMP4レンダリング（H.264 / yuv420p / AAC / +faststart）
   - `~/.hermes/lm-twitterer/media/` へコピー
   - `core.post("", text=..., media_paths=[filename], dry_run=False)` でX投稿

3. **結果を確認する**。スクリプト出力のJSONに `posted: true` と `url` が含まれていること、再生可能な動画ファイルが生成されていることを確認する。

### 手動実行（代替）

統合スクリプトを使わず、一つずつ実行する場合の手順。

1. **写真を選ぶ**。`Pictures/VRChat` 以下から拡張子 `.png`, `.jpg`, `.jpeg`, `.webp` の画像をランダムに選ぶ。

2. **Hakua音声を生成する**。Irodoriへ次のJSONをPOSTしてWAVとして保存する。
   ```json
   {"input":"おはようございます。今日もVRChatで素敵な時間を過ごしましょう。","model":"irodori-tts","voice":"hakua","response_format":"wav","speed":1.0}
   ```
   `irodori_tts_synthesize` が利用できる場合も `voice="hakua"`, WAV出力, `model="irodori-tts"` で実行してよい。

3. **MP4を生成する**。`terminal` で `ffmpeg` を実行する。
   ```bash
   ffmpeg -y -loop 1 -i "selected_photo" -i "hakua.wav" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -movflags +faststart -shortest "output.mp4"
   ```
   Twitter/X互換にはH.264、AAC、`yuv420p`、偶数サイズ、0.5秒以上のdurationが必要。

4. **動画をメディアディレクトリへ配置する**。最終MP4を `~/.hermes/lm-twitterer/media/` 直下へコピーする。`media_paths` には絶対パスではなくファイル名だけを渡す。

5. **Xへ投稿する**。`plugins/lm-twitterer/core.py` を動的importして次を呼ぶ。
   ```python
   result = core.post(
       "",
       text="おはようございます。今日もVRChatで素敵な時間を過ごしましょう。 #hermesagent はくあ",
       media_paths=["hakua_YYYYMMDD_HHMMSS.mp4"],
       dry_run=False,
   )
   ```
   投稿文は短く、秘密情報・パス・Cookieを含めず、`#hermesagent` を含める。返却JSONの `posted: true` と `url` で成功を確認する。

## Pitfalls

- `hermes lm-twitterer post ...` が `invalid choice: 'lm-twitterer'` になる環境では失敗する。直接importした `core.post()`を使う。
- lm-twittererのメディアガードは `~/.hermes/lm-twitterer/media/` 外のファイルを拒否する。コピー後はファイル名だけを渡す。
- **MSYS2パス二重変換**: git-bash上で `./.venv/Scripts/python.exe "$HOME/.hermes/..."` とすると、`$HOME` が `/c/Users/downl` に展開されたあと、MSYSが実行ファイル（ネイティブWindowsバイナリ）の引数とみなしてさらに `C:\c\Users\...` に変換する。回避策として、スクリプトをリポジトリ以下にコピーしてから実行するか、引数にWindowsネイティブパス（末尾バックスラッシュなし）を渡す。
- `python` では別のシステムPythonが選ばれ、終了コード49になることがある。Windowsでは `./.venv/Scripts/python.exe` を明示する。
- Xは短すぎる動画を拒否することがある。音声を含む動画が少なくとも0.5秒以上あることを `ffprobe` で確認する。
- Twitter/X互換性のため、動画は必ずH.264、音声はAAC、画素形式は `yuv420p` とする。偶数サイズも必要。
- Irodoriの冷起動や合成は120秒を超える場合がある。短いforeground待機で諦めず、`terminal(background=true, notify_on_complete=true)` と `process(action='wait')` を使う。
- Irodori TTSが止まっているとスキルスクリプトがエラー終了する。事前に `/health` を確認し、止まっていれば起動してからスクリプトを実行する。
- `core.auth_check()` の `v11_verify_credentials_http_status: 404` は、GraphQL認証が有効なら必ずしも投稿失敗を意味しない。`auth_valid` と、実投稿の `posted` を優先する。
- `hermes -z ... --cli` による文面生成がタイムアウトした場合は、固定の短い安全な文面にフォールバックする。タイムアウトだけで写真選択や投稿全体を失敗扱いにしない。
- 秘密情報、認証Cookie、環境変数はログ・投稿文・レポートに出さない。

## Verification

`terminal` ツールで次を実行し、`posted: true`、URL、動画のcodec・画素形式・durationを同時に確認する。

```bash
latest=$(find "$HOME/.hermes/lm-twitterer/media" -maxdepth 1 -type f -name 'hakua_*.mp4' -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-); ffprobe -v error -show_entries format=duration,size:stream=codec_name,codec_type,width,height,pix_fmt -of default=noprint_wrappers=1 "$latest"
```

実投稿のJSONで `"posted": true` と `"url": "https://x.com/..."` が確認できない限り、投稿成功とは断定しない。
