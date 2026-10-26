---
name: daily-vrchat-photo-tweet
description: Post a daily VRChat screenshot with Hakua voice tweet.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [SocialMedia, VRChat, Automation]
---

# Daily VRChat Photo Tweet

Post a daily VRChat screenshot with Hakua voice tweet using Hermes TTS and lm-twitterer. The skill automates capturing a random VRChat screenshot, generating speech audio, creating an MP4 video, and publishing to Twitter/X.

## When to Use
- You want to automate a daily tweet that includes a random VRChat screenshot and a spoken message in Hakua's voice.
- You have Hermes installed with the `lm-twitterer` and `irodori-tts` plugins enabled.
- You have FFmpeg available for video creation.

## Prerequisites
- Hermes agent installed and configured.
- `lm-twitterer` plugin enabled and authenticated with Twitter/X.
- `irodori-tts` plugin installed and the TTS server running on `http://127.0.0.1:8088`.
- FFmpeg installed and available in PATH.
- A directory of VRChat screenshots at `~/Pictures/VRChat` (or adjust `VRCHAT_PHOTOS_DIR` in the script).

## How to Run
Execute the script using the `terminal` tool from the Hermes root directory:
```text
python scripts/daily_vrchat_post.py
```
Or invoke via Hermes CLI:
```text
hermes run-script scripts/daily_vrchat_post.py
```

## Quick Reference
- `python scripts/daily_vrchat_post.py` – run the daily posting script
- Ensure `http://127.0.0.1:8088/health` returns `{"status":"ok"}`

## Procedure
1. **Start Irodori TTS server (if not already running)**
   Use the appropriate method for your setup; one way is to run:
   ```text
   python -m irodori_openai_tts --host 127.0.0.1 --port 8088
   ```
   from the `irodori-tts-server` directory, or use the Hermes plugin controls.

2. **Place the script**
   Save the following Python script as `scripts/daily_vrchat_post.py` in your Hermes working directory:
   ```python
   #!/usr/bin/env python3
   """
   Daily VRChat Photo Post with Hakua Voice
   Picks a random VRChat screenshot from Pictures/VRChat,
   generates Hakua's voice via Hermes aituber-onair speak,
   creates an MP4 video,
   and posts to X via LM Twitterer (hermes cli) with media upload.
   """
   import os
   import random
   import shutil
   import subprocess
   import sys
   from pathlib import Path
   from datetime import datetime

   # Configuration (adjust for your OS if needed)
   VRCHAT_PHOTOS_DIR = Path(r"%USERPROFILE%\Pictures\VRChat")
   OUTPUT_DIR = Path(r"%USERPROFILE%\Documents\New project\hermes-agent\output\daily_posts")

   HAKUA_MORNING_TEXTS = [
       "おはようございます、はくあです。VRChatの思い出写真と共に、今日も良い一日になりますように。",
       "おはよう、ボブにゃん！昨日のVRChatの思い出、綺麗に残ってるね。今日も無理なく、安全に、ひとつずつ前へ。",
       "はくあから朝のご挨拶。VRChatの世界で過ごした時間が、こうやって映像になって蘇るのって素敵だね。良い一日を。",
       "朝だよ、ボブにゃん。VRChatの写真を見返すと、アバターの着せ替えやフレンドとの雑談、ワールド巡り……全部「その場にいた」証拠として残ってる。今日も楽しみだね。",
       "おはようございます。はくあより、VRChatの思い出コレクションからランダムに一枚。今日の君にも、良い出会いがありますように。",
   ]

   def pick_random_photo() -> Path | None:
       extensions = (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
       photos = []
       for ext in extensions:
           photos.extend(VRCHAT_PHOTOS_DIR.rglob(f"*{ext}"))
       if not photos:
           print("No VRChat photos found!", file=sys.stderr)
           return None
       return random.choice(photos)

   def generate_tts_via_hermes(text: str, output_path: Path) -> bool:
       """Use hermes aituber-onair speak to generate wav file."""
       hermes_cmd = "hermes"
       try:
           subprocess.run([hermes_cmd, "--version"], capture_output=True, check=True)
       except (FileNotFoundError, subprocess.CalledProcessError):
           hermes_cmd = [sys.executable, "-m", "hermes"]
       args = [
           "aituber-onair", "speak",
           "--output-path", str(output_path),
           "--text", text
       ]
       if isinstance(hermes_cmd, list):
           cmd = hermes_cmd + args
       else:
           cmd = [hermes_cmd] + args
       print(f"Running: {' '.join(cmd)}")
       try:
           result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
           if result.returncode == 0:
               print(f"TTS generated via Hermes: {output_path}")
               return True
           else:
               print(f"Hermes TTS failed: {result.stderr}", file=sys.stderr)
               return False
       except Exception as e:
           print(f"Error running Hermes TTS: {e}", file=sys.stderr)
           return False

   def create_mp4(image_path: Path, audio_path: Path, output_path: Path) -> bool:
       cmd = [
           "ffmpeg", "-y",
           "-loop", "1", "-i", str(image_path),
           "-i", str(audio_path),
           "-c:v", "libx264", "-tune", "stillimage",
           "-c:a", "aac", "-b:a", "192k",
           "-pix_fmt", "yuv420p",
           "-shortest",
           str(output_path),
       ]
       try:
           result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
           if result.returncode == 0:
               print(f"MP4 created: {output_path}")
               return True
           else:
               print(f"ffmpeg failed: {result.stderr}", file=sys.stderr)
               return False
       except Exception as e:
           print(f"MP4 creation failed: {e}", file=sys.stderr)
           return False

   def post_via_hermes_lm_twitterer(media_path: Path, tweet_text: str) -> bool:
       # Ensure media is in LM Twitterer's media directory (as required by the plugin)
       lm_twitterer_media_dir = Path.home() / ".hermes" / "lm-twitterer" / "media"
       lm_twitterer_media_dir.mkdir(parents=True, exist_ok=True)
       dst_media_path = lm_twitterer_media_dir / media_path.name
       shutil.copy2(media_path, dst_media_path)
       print(f"Copied media to LM Twitterer media dir: {dst_media_path}")

       # Build the hermes command
       hermes_cmd = "hermes"
       try:
           subprocess.run([hermes_cmd, "--version"], capture_output=True, check=True)
       except (FileNotFoundError, subprocess.CalledProcessError):
           hermes_cmd = [sys.executable, "-m", "hermes"]
       args = [
           "lm_twitterer_post",
           f"--media_paths={dst_media_path}",
           f"--text={tweet_text}",
           "--dry_run=false"
       ]
       if isinstance(hermes_cmd, list):
           cmd = hermes_cmd + args
       else:
           cmd = [hermes_cmd] + args
       print(f"Running: {' '.join(cmd)}")
       try:
           result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
           if result.returncode == 0:
               print(f"Tweet posted successfully via Hermes LM Twitterer.")
               return True
           else:
               print(f"Hermes LM Twitterer failed: {result.stderr}", file=sys.stderr)
               return False
       except Exception as e:
           print(f"Error running Hermes LM Twitterer: {e}", file=sys.stderr)
           return False

   def main():
       OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
       photo = pick_random_photo()
       if not photo:
           return 1
       print(f"Selected photo: {photo}")
       tweet_text = random.choice(HAKUA_MORNING_TEXTS) + " #hermesagent"
       print(f"Tweet text: {tweet_text}")
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       audio_path = OUTPUT_DIR / f"hakua_{timestamp}.wav"
       mp4_path = OUTPUT_DIR / f"hakua_{timestamp}.mp4"
       if not generate_tts_via_hermes(tweet_text, audio_path):
           return 1
       if not create_mp4(photo, audio_path, mp4_path):
           return 1
       if not post_via_hermes_lm_twitterer(mp4_path, tweet_text):
           return 1
       print("Daily post completed successfully!")
       return 0

   if __name__ == "__main__":
       sys.exit(main())
   ```

3. **Make the script executable (optional)**
   ```text
   chmod +x scripts/daily_vrchat_post.py
   ```

4. **Run the script**
   From the Hermes root directory:
   ```text
   python scripts/daily_vrchat_post.py
   ```

## Verification
After running, verify that a tweet with media appears on your Twitter/X timeline and that the console output shows successful TTS generation, MP4 creation, and tweet posting.

## Pitfalls
- If the Irodori TTS server is not reachable, the TTS step will fail. Ensure the server is running and accessible at `http://127.0.0.1:8088`.
- The `lm-twitterer` plugin requires valid Twitter/X credentials; authentication errors will appear in the Hermes log.
- FFmpeg must be installed and in your PATH; otherwise the MP4 creation step will fail.
- The script assumes a Windows path for `VRCHAT_PHOTOS_DIR` and `OUTPUT_DIR`; adjust these constants if you run on Linux/macOS.