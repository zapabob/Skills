---
name: twitter-posting
description: Post tweets using Hermes Agent via lm-twitterer plugin or xurl CLI.
triggers:
  - tweet
  - twitter
  - x
  - social media
---
# Twitter Posting Skill

Post tweets using Hermes Agent via lm-twitterer plugin or xurl CLI.

## When to Use
- You need to send a tweet from Hermes Agent.
- You want to automate Twitter/X posting as part of a workflow.

## Prerequisites
- lm-twitterer plugin or xurl CLI.
- You want to automate Twitter/X posting as part of a workflow.

## Prerequisites
- lm-twitterer plugin configured with valid X (Twitter) credentials.
- xurl CLI installed and authenticated with the same account.
- Hermes Agent running with appropriate permissions.

## Steps

### 1. Verify lm-twitterer readiness
Check that the plugin is configured and credentials are set:
```bash
hermes agent run lm-twitterer-status
```
Ensure `auth_token_set` and `ct0_set` are true.

### 2. Post via lm-twitterer (preferred)
Use the lm-twitterer plugin for seamless integration:
```bash
hermes agent run lm-twitterer-post --text "Your tweet text here #hermesagent はくあ" --dry_run false
```
- Keep tweet under 140 characters (Japanese).
- Include exactly one emoji (🚀 or ✨) if desired.
- Always end with the signature "はくあ".
- Include the hashtag #hermesagent.

### 3. Fallback: Post via xurl
If lm-twitterer fails, use xurl directly:
```bash
# Ensure xurl is using the Hermes app
xurl auth default hermes
# Post the tweet
xurl post "Your tweet text here #hermesagent はくあ"
```
If you get a 401 Unauthorized error, re-authenticate:
```bash
xurl auth login   # or re-enter credentials via xurl auth apps add
```

### 4. Common Pitfalls
- **Authentication errors**: Ensure xurl default app is set to "hermes". Check with `xurl auth apps list`. If lm-twitterer shows auth errors, re-run `lm-twitterer-auth-check` and re-authenticate via the plugin's login flow.
- **Empty URL after post**: If `lm_twitterer_post` returns `{"posted": true, "url": ""}`, the tweet IS live on X — only URL extraction failed. See the `hermes-x-posting-workflows` skill reference `references/lm-twitterer-empty-url-diagnosis.md` for recovery steps (`_find_recent_tweet_url_by_text`, `without_preload_content`, or manual timeline check).
- **Duplicate tweets**: The bot may refuse to post identical content; vary wording slightly.
- **Whitelist/follower requirements**: lm-twitterer may require the target user to be followed or whitelisted for replies; for original posts, this is less restrictive.
- **Character count**: Exceeding 140 characters will cause rejection; count carefully. Use `hermes agent run tweet-length-check` or external tool to verify.
- **Emoji limit**: Use at most one emoji, either 🚀 or ✨. More than one may cause posting failures due to a known plugin bug.
- **Signature placement**: Ensure the tweet ends exactly with "はくあ". Additional trailing spaces or characters may cause rejection.
- **AttributeError: 'NoneType' object has no attribute 'group'**: This comes from `twitter-openapi-python`'s `get_client_from_cookies()` scraping X's on-demand JavaScript bundle. The JS parsing regex fails when X changes their bundle layout. **Restarting does not fix it** — the root cause is the fragile client bootstrap. The proven fix is to replace `_twitter_client(cfg)` calls in `plugins/lm-twitterer/core.py` with direct GraphQL functions that bypass `get_client_from_cookies()`:

  1. Replace the search timeline (`get_search_timeline`) with `_graphql_search_timeline_items(cfg, raw_query=..., count=...)` which calls `_placeholder_graphql_get(cfg, "SearchTimeline", ...)` and returns items compatible with `_flatten_tweet_items`.
  2. Replace `_fetch_thread(tweet_api, tweet_id)` with `_fetch_thread(None, tweet_id, cfg=cfg)` when `_fetch_thread` accepts a `cfg` parameter.
  3. Replace `_safe_post_create_tweet(post_api, ...)` with `_graphql_create_tweet(cfg, tweet_text=..., in_reply_to_tweet_id=...)` which does a direct HTTP POST to the CreateTweet GraphQL endpoint.
  4. See `_graphql_tweet_item()` in `core.py` for wrapping raw GraphQL tweet dicts into attribute-accessible objects compatible with existing helper functions (`_tweet_id`, `_tweet_text`, `_screen_name`, `_followed_by_bot`).

  If `core.py` hasn't received the fix yet, apply it as a minimal patch: the required functions (`_graphql_search_timeline_items`, `_graphql_create_tweet`, `_graphql_tweet_item`, `_graphql_tweet_detail_results`) should be added near `_flatten_tweet_items`, and the two `_twitter_client(cfg)` call sites in `reply_mentions()` and `mention_candidates()` replaced. The `_twitter_client()` definition itself can remain as dead fallback code.

### 5. Verification
After posting, you can verify by reading your timeline:
```bash
xurl timeline -n 5
```
Or check the tweet ID returned in the response (if any).

### 6. Posting a video with voiceover

To attach a video with voiceover (e.g., a slideshow with narration) to a tweet:

1. **Prepare the text** you want spoken and save it to a temporary file.
   ```bash
   cat > /tmp/tweet_text.txt <<'EOF'
   はくあだよ。RTX 5060 TiでVRChatのPCVRやってみたの。すごく快適でびっくり。しかもはくあの声、ちゃんと出てるよ。irodori-TTS、いい感じ！
   EOF
   ```

2. **Synthesize voice** using the built-in text_to_speech tool (which uses irodoriTTS by default) or invoke irodoriTTS directly.
   ```bash
   # Using Hermes text_to_speech tool (returns an .ogg file)
   hermes agent run text_to_speech --text "$(cat /tmp/tweet_text.txt)"
   # The tool outputs a MEDIA: line with the file path; note the path.
   ```
   Alternatively, use the irodoriTTS skill:
   ```bash
   hermes agent run irodori_tts_synthesize --text "$(cat /tmp/tweet_text.txt)" --output_path /tmp/hakua_voice.ogg --voice hakua
   ```

3. **Create a video slideshow** from images (e.g., VRChat screenshots) using FFmpeg.
   - Determine total audio duration (e.g., via `ffprobe`).
   - Divide by number of slides to get per-slide duration.
   - Build a concat demuxer list with each image and its duration.
   - Run ffmpeg to produce a silent video:
     ```bash
     ffmpeg -f concat -safe 0 -i slides.txt -c:v libx264 -pix_fmt yuv420p -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" silent.mp4
     ```

4. **Combine audio and video**:
   ```bash
   ffmpeg -i silent.mp4 -i /tmp/hakua_voice.ogg -c:v copy -c:a aac -b:a 128k -shortest final_with_voice.mp4
   ```

5. **Post via lm-twitterer** with the media path:
   ```bash
   hermes agent run lm-twitterer-post --text "$(cat /tmp/tweet_text.txt)" --media_paths "C:/path/to/final_with_voice.mp4" --dry_run false
   ```

**Tips**:
- Keep the final tweet text under the character limit (count after posting).
- Ensure the video meets Twitter's specifications (MP4, H.264/AAC, under 512MB, etc.).
- If the voice audio is in OGG Opus, Twitter may accept it; otherwise convert to AAC as above.
- Always verify the output with `ffprobe` before posting.
- For lm-twitterer video uploads, put MP4s under the plugin media root (default `~/.hermes/lm-twitterer/media`) or set `LM_TWITTERER_MEDIA_DIR` and place files under that root; arbitrary local paths may be rejected by the plugin's media safety guard.

## Notes
- The lm-twitterer plugin may auto-add memory links or signatures; ensure compliance with your style.
- For troubleshooting, consult `lm-twitterer-status` and check the state directory under `~/.hermes/lm-twitterer`.
- If a freshly patched plugin behaves differently through the WebUI tool than through `hermes lm-twittererred behavior through the WebUI tool than through `hermes lm-twitterer ...`, restart Hermes/Gateway so plugin code and tool schemas reload.

## References
- See `references/xurl-auth-tips.md` for detailed authentication steps.
- See `references/lm-twitterer-video-media-root.md` for the MP4 upload media-root workflow and validation probes.
- See `references/manim-irodori-video-tweet.md` for the proven Manim + Hakua/irodoriTTS + lm-twitterer video tweet workflow.
- See `templates/tweet-template.txt` for a pre-formatted tweet template.