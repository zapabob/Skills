---
name: twitter-posting
description: Publishing posts to X (Twitter) with media via lm-twitterer.
category: social-media
---

# Twitter Posting (X) via lm-twitterer

This skill handles posting text and media to X (formerly Twitter) using the lm-twitterer plugin integrated with Hermes.

## When to use
- Posting status updates, media, or threads from the command line.
- When you need to publish on behalf of the Parent or the ASI (Hakua).
- When you need to include media files stored in `~/.hermes/lm-twitterer/media/`.

## Prerequisites
- The `lm-twitterer` plugin must be installed and authenticated.
- Media files must be placed in `~/.hermes/lm-twitterer/media/`.
- The whitelist must include the target account or the post will be rejected.

## Basic command
```bash
# Dry run (recommended for first time)
hermes run twitter-posting --dry-run "Your text here"

# Real post with media
hermes run twitter-posting --media "path/to/file.jpg" "Your text here"
```

## Options
- `--dry-run` : Generate the post but do not publish.
- `--media <path>` : Attach a media file (image, video, etc.).
- `--topic <topic>` : Provide a topic tag; the plugin appends a default hashtag.
- `--text <text>` : Directly specify the post text.

## Common pitfalls
- **Missing media file**: Ensure the file exists at the given path and is readable.
- **Whitelist not set**: The target account must be whitelisted in `~/.hermes/lm-twitterer/whitelist.txt`.
- **Tweet length**: X limits tweets to 280 characters; truncate or split if necessary.
- **Rate limiting**: Do not exceed the allowed number of posts per hour to avoid temporary bans.

## Error handling
If a post fails, inspect the error code returned by `lm_twitterer_post`. Common error codes:
- `1`: Authentication failure – re-run `lm_twitterer_auth_check`.
- `2`: Media file not found – verify the path.
- `3`: Generic failure – check tweet text for policy violations or exceeding character limits.

## Example workflow
1. Prepare media: `ffmpeg -i input.mov -c copy output.mp4`
2. Place file in `~/.hermes/lm-twitterer/media/`.
3. Post with text and media:
   ```bash
   lm_twitterer_post --dry_run=false --media_paths "C:\\Users\\downl\\.hermes\\lm-twitterer\\media\\output.mp4" --text "はくあがVRChatで元気に動いています！みんなへのサポートを続けます。 #VRChat #hermesagent"
   ```
4. Verify the post URL printed in the response.

## References
- `references/troubleshooting-x-posting.md` – detailed troubleshooting steps.
- `scripts/post_to_x.sh` – example wrapper script for automated posting.