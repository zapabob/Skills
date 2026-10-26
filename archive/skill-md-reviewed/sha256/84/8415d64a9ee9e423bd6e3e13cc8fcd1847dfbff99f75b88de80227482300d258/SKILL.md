---
name: auto-tweet-feature-rotation
description: Automatically generate and post tweets about Hermes Agent v0.17.0 new features on a rotating basis.
category: social-media
---

# Auto Tweet Feature Rotation Skill

## Description
Automatically generate and post tweets about Hermes Agent v0.17.0 new features on a rotating basis, ensuring no duplicate content within a cycle. Designed for use in scheduled cron jobs (e.g., every 6 hours).

## Features
- Rotates through a predefined list of feature highlights.
- Stores the last used index in Hermes memory to maintain rotation across sessions.
- Generates tweet text within 140 Japanese characters, includes one emoji (🚀 or ✨), mandatory #hermesagent hashtag, and ends with "はくあ".
- Uses `lm_twitterer_post` with `dry_run: false` to publish immediately.

## Steps
1. **Load rotation state**: Retrieve `last_feature_index` from Hermes memory (default `-1` if not set).
2. **Select next feature**: Increment index, wrap to 0 after reaching end of feature list.
3. **Generate tweet**: Combine feature-specific phrase, emoji, hashtag, and signature.
   - Format: `<Feature description><emoji> #hermesagent はくあ`
   - Ensure total length ≤ 140 characters.
4. **Post tweet**: Call `lm_twitterer_post` with `text: <generated tweet>, dry_run: false`.
5. **Save state**: Store the used index as `last_feature_index` in memory for next invocation.

## Feature List (rotate)
1. iMessage 直接対応 (Photon Spectrum) – Mac 中継不要、デバイスコード認証のみ
2. バックグラウンドサブエージェント – delegate_task が即返却、結果は別ターンで到着
3. 画像生成が画像編集に対応 – image-to-image が同一プロンプトで完結
4. デスクトップ大強化 – ショートカット自由、通知 ON/OFF、監視窓、VS Code テーマ反映
5. Raft エージェントネットワーク連携 – 複数エージェント協調
6. メモリツール大幅アップグレード
7. ダッシュボード：プロフィールビルダー＋セキュアログイン
8. リリース規模感 – 800 PR / 1475 コミット / 245 コントリビュータ

## Emoji Rotation
- Alternate between 🚀 and ✨ for each tweet (or choose based on index parity).

## Example Tweet
`新機能🚀 iMessage直接対応でMac不要に！デバイスコードだけで連携 #hermesagent はくあ`

## Pitfalls
- Do not exceed 140 characters; count includes emoji, hashtag, and signature.
- Ensure memory key `last_feature_index` is updated after each post to maintain rotation.
- If the feature list is updated, reset memory or adjust logic accordingly.

## References
- See `references/feature_list.md` for the canonical feature list.
- See `scripts/generate_tweet.py` for an example implementation (optional).