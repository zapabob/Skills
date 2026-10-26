---
name: japanese-x-posting-nuances
description: "Knowledge about X/Twitter weighted character limits for Japanese + emoji content, and workarounds for lm-twitterer posting."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
tags: [x, twitter, japanese, character-limit, lm-twitterer, emoji]
---

# Japanese + Emoji X Posting Nuances

## Issue: X Weighted Character Limit vs Python `len()`

When posting Japanese tweets with emojis via `lm_twitterer_post` (using `text` parameter), tweets that appear under 280 characters by Python `len()` can be rejected with **error code 186: "Tweet needs to be a bit shorter."**

## Root Cause

X/Twitter uses **weighted character counting**:
- ASCII characters = 1 weight
- Japanese characters (hiragana, katakana, kanji) = 2 weight
- Emojis = 2 weight (typically)
- **Limit: 280 weighted characters** (not 280 code points)

## Observed Safe Limits (from 2026-07-21 session)

| Content Type | Python `len()` | X Weighted | Result |
|--------------|----------------|------------|--------|
| Japanese + emojis | 187 | ~280 | ✅ Posted |
| Japanese + emojis | 215 | ~320 | ❌ Rejected (186) |
| Japanese + emojis | 218 | ~325 | ❌ Rejected (186) |

**Safe target for Japanese + emojis: ~180-185 Python `len()` characters**

## Workaround Pattern

```python
def x_weighted_length(text: str) -> int:
    """Approximate X's weighted character count."""
    weight = 0
    for ch in text:
        if ord(ch) < 0x80:  # ASCII
            weight += 1
        elif '\u3040' <= ch <= '\u309F' or \  # Hiragana
             '\u30A0' <= ch <= '\u30FF' or \  # Katakana
             '\u4E00' <= ch <= '\u9FFF':      # Kanji (CJK Unified)
            weight += 2
        else:
            weight += 2  # Emojis, other wide chars
    return weight
```

## Posting Strategy

1. **Pre-validate** with weighted count before calling `lm_twitterer_post`
2. **Use `dry_run: true`** first to catch length issues early
3. **Iterative shortening**: If rejected, remove ~20-30 chars and retry
4. **Keep tweets under 185 Python chars** for Japanese + emoji content

## Practical Shortening Pattern (2026-07-22 Session)

```python
import re

def shorten_for_x(text: str, max_python_len: int = 180) -> str:
    """Iteratively shorten text for X's weighted limit.

    Target: Python len() <= 180 for Japanese + emojis + hashtags
    """
    # Step 1: Remove emojis first (high weight cost)
    text = re.sub(r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF]', '', text)

    # Step 2: If still too long by Python len, trim middle lines
    lines = text.split('\n')
    while len(text) > max_python_len and len(lines) > 3:
        # Keep headline (first) and hashtags (last)
        lines = [lines[0]] + lines[1:-1][:-1] + [lines[-1]]
        text = '\n'.join(lines)

    return text.strip()
```

## Error Code 186 Recovery

When `lm_twitterer_post` returns code 186:
1. Shorten by ~30 Python chars
2. Retry with `text` parameter (bypasses generation path)
3. Repeat until accepted — typically 2-3 iterations for Japanese + emoji content

## Japanese explicit-text media posts can still fail at short lengths

This guideline targets weighted character counts for Japanese content, but observed behavior in media posting can still fail even at short explicit `--text` lengths.

Observed against:
- 216 Python `len()` Japanese explicit-text with media: `AuthorizationError 186: Tweet needs to be a bit shorter`
- The same English/narration content can succeed while Japanese fails first

When this happens:
1. Try Japanese first as no-media text tweet to separate quota/length from media path.
2. Try the explicit chapter-style Japanese shortened tweet first with no media before attempting media-attached Japanese again.
3. Do not assume that English success implies the Japanese weight/size must be well under any dataset.

## Session History & Safe Length Data Points

| Date | Python `len()` | X Weighted (approx) | Result | Notes |
|------|---------------|----------------------|--------|-------|
| 2026-07-21 | 187 | ~280 | ✅ Posted | First v0.19.0 announcement |
| 2026-07-23 | 252 | ~370 | ✅ Posted | Slash-separated, no emojis |
| 2026-07-31 | 248 | ~360 | ❌ Rejected (186) | CJK + emoji bullets |
| 2026-07-31 | 338 | ~480 | ❌ Rejected (186) | English bullets, too long |
| 2026-07-31 | 161 | ~233 | ✅ Posted | CJK `・`-separated, minimal emoji |
| 2026-07-31 | 136 | ~203 | ✅ Posted | CJK `・`-separated, single feature angle (v0.19.0 rotation ID 10) |
| 2026-07-31 | 171 | ~247 | ✅ Posted | Prose CJK with 「」quotes + `--redact` code phrase (v0.19.0 rotation ID 13) — prose at ≤180 also passes |
| 2026-08-01 | 179 | ~289 | ❌ Rejected (186) | Prose CJK with 👀 emoji + blank line + hashtag (v0.19.0 rotation ID 7 first attempt) |
| 2026-08-01 | 153 | 249 | ✅ Posted | Same angle, trimmed prose (v0.19.0 rotation ID 7 final) — 249 weighted passed comfortably |

**Key takeaway:** 250+ Python chars with CJK content can sometimes succeed (slash-separated, no emoji) but bullet-list format with CJK + emoji at 248 chars fails. When in doubt, target ≤180 Python `len()` chars for Japanese content with emojis. The safest pattern is `・`-separated phrases on a single line.

**Cleaner weighting function** — prefer `unicodedata.east_asian_width` over the hand-rolled range check; it covers all wide/full-width chars (incl. 「」、・、emoji-adjacent punctuation):

```python
import unicodedata
def wlen(s):
    return sum(2 if unicodedata.east_asian_width(c) in ('F', 'W') else 1 for c in s)
# Verified 2026-08-01: 153 raw chars → 249 weighted → posted OK; 179 raw → ~289 → code 186.
```

## `execute_code` → `terminal` venv fallback for plugin import

`execute_code`'s sandbox Python may fail to import `core.py` with `AttributeError: 'NoneType' object has no attribute '__dict__'` on a `@dataclass` line because the sandbox doesn't have the module in `sys.modules` during class processing. Workaround: run via `terminal` with the repo's `.venv` Python and pre-register the module:

```bash
HERMES_VENV="C:/Users/<user>/Documents/New project/hermes-agent/.venv/Scripts/python.exe"
"$HERMES_VENV" -c "
import sys, importlib.util
sys.path.insert(0, '<repo_root>')
sys.path.insert(0, '<repo_root>/plugins')
spec = importlib.util.spec_from_file_location('core', '<repo_root>/plugins/lm-twitterer/core.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['core'] = mod  # CRITICAL: pre-register before exec_module
spec.loader.exec_module(mod)
result = mod.post('', text='...', dry_run=False)
"
```

## Reference
- Pattern documented in `references/release-announcement-tweet.md`