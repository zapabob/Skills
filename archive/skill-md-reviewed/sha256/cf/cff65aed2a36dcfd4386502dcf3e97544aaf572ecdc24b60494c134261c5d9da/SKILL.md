---
name: twitter-media-post
category: social-media
description: Post a tweet with media (image/audio video) using LM Twitterer and TTS.
---

# Twitter Media Post Skill

Post a tweet with media (image/audio video) using LM Twitterer and TTS (Irodori or VOICEVOX).

## When to Use
- You want to tweet a message with accompanying media (e.g., a VRChat screenshot + voice audio).
- You prefer to use Hermes' built-in TTS (Irodori first, fallback to VOICEVOX).
- You need to ensure the media file is accessible to the LM Twitterer plugin (must be under Hermes media directory).

## Prerequisites
- LM Twitterer plugin configured (auth_token, ct0 set).
- FFmpeg installed and available in PATH.
- Access to a folder with recent images (e.g., Pictures/VRChat).
- TTS servers: Irodori-TTS (preferred) or VOICEVOX running.

## Steps

1. **Obtain the latest image**
   - Determine the folder containing the target images (e.g., `%USERPROFILE%\Pictures\VRChat`).
   - List files sorted by time descending and pick the newest file.
   - Copy the image to Hermes LM Twitterer media directory (`%HERMES_HOME%\lm-twitterer\media\`) with a safe filename (e.g., `latest_vrchat.png`).

2. **Generate TTS audio**
   - Try Irodori TTS first (`aituber_onair_speak` with provider=`irodori`).
   - If Irodori fails, fallback to VOICEVOX (`aituber_onair_speak` with provider=`voicevox`).
   - Output a WAV file (e.g., `ohayo.wav`) under the Hermes workspace or media directory.

3. **Create MP4 video from image + audio**
   - Use FFmpeg to combine the image (as a static video stream) and the audio:
     ```
     ffmpeg -y -i <image> -i <audio> -c:v copy -c:a aac -shortest <output.mp4>
     ```
   - Save the MP4 in the LM Twitterer media directory.

4. **Post the tweet via LM Twitterer**
   - Call `lm_twitterer_post` with:
     - `text`: your tweet text (include desired hashtags).
     - `media_paths`: array containing the relative path to the MP4 inside the media directory (e.g., `output.mp4`).
     - `dry_run`: false to actually post.
   - The plugin will copy the media to its media directory if needed and upload with the tweet.

5. **Verify success**
   - Check the returned `url` field for the tweet link.
   - If `dry_run:true` was used, only the tweet text is generated.

## Pitfalls & Troubleshooting
- **Irodori TTS startup failures**: Often due to virtual environment mismatch. Ensure the Irodori TTS server is started with the correct venv, or fallback to VOICEVOX as done in this session.
- **FFmpeg not found**: Install FFmpeg and ensure its directory is in system PATH.
- **Media path errors**: LM Twitterer expects media files under its media directory. Copy files there before posting, or use relative paths from the media root.
- **File name issues**: Avoid spaces and special characters in filenames; use underscores or hyphens.
- **Twitter API errors**: Check auth_token and ct0 are fresh; re-login if needed.

## References
- See `references/twitter-media-post-session.md` for a detailed log of this session's execution, including error messages and fallback decisions.

## Example Usage
```
/skill twitter-media-post
# (skill provides guidance; actual execution done via tool calls)
```