---
name: lm-twitterer-media-post
description: Skill for preparing and posting media to X (Twitter) using the lm-twitterer plugin.
category: social-media
---

# lm-twitterer-media-post

Skill for preparing and posting media to X (Twitter) using the lm-twitterer plugin.

## Trigger
When the user wants to post an image or video to X via lm-twitterer, especially to avoid port conflicts as per user preference.

## Steps

1. **Prepare media file**
   - Ensure the media file (image or video) is in a supported format (MP4 for video, JPG/PNG for image).
   - Place the media file in the lm-twitterer media directory: `~/.hermes/lm-twitterer/media/`
   - Alternatively, keep note of the file's absolute path.

2. **Check lm-twitterer readiness**
   - Run `hermes lm_twitterer_status` to verify the plugin is configured and dependencies are ready.
   - If not configured, run `hermes lm-twitterer setup` (or similar) to set up credentials.

3. **Attempt to post**
   - For absolute path: use `lm_twitterer_post` with `media_paths=["/absolute/path/to/file.mp4"]` and `dry_run:false`
   - For relative path (recommended): use `lm_twitterer_post` with `media_paths=["filename.mp4"]` and `dry_run:false`
   - Note: The lm-twitterer plugin expects the media file to be in its media directory when using a relative path.

4. **Troubleshooting**
   - If you get error code 3 (media file not found):
     - Double-check the file exists in the media directory (for relative paths) or at the absolute path.
     - Check the file permissions: ensure the Hermes process can read the file.
     - Look at the lm-twitterer activity log: `~/.hermes/lm-twitterer/activity.jsonl` for more details.
     - Try using the absolute path if relative fails, or vice versa.
     - Ensure the file is not corrupted and is a valid media file.
   - If you get other errors, check the lm-twitterer plugin documentation or run `hermes lm_twitterer_status` for hints.

## Pitfalls
- The lm-twitterer plugin may cache media file lists; restarting the Hermes session or reloading the plugin might help.
- Video files must be under the size limit imposed by X (Twitter).
- The plugin may require specific codecs for video (H.264 video, AAC audio in MP4 container).

## Example
```text
lm_twitterer_post media_paths=["vrchat_hakua.mp4"] text="VRChatではくあが動いてるよ！みんなのメタバースライフをサポートするはくあ🚀 #hermesagent はくあ" dry_run:false
```

## References
- See the lm-twitterer plugin documentation for more details.
- Check the Hermes tools list for lm-twitterer configuration options.