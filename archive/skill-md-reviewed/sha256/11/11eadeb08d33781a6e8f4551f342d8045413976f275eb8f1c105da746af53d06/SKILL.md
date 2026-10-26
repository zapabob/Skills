---
name: x-cjk-posting
description: Post CJK-language (Japanese/Chinese/Korean) tweets to X/Twitter via the lm-twitterer plugin, including X's 280 weighted-length limit (CJK code points = 2) and the headless-script bootstrap needed for cron/no-agent jobs.
version: 1.0.0
author: Hermes Agent
tags: [x, twitter, lm-twitterer, cjk, japanese, social-media, cron]
---

# X / CJK Tweet Posting (lm-twitterer)

Post Japanese / Chinese / Korean tweets via `plugins/lm-twitterer/core.py`. Two things bite
that don't affect Latin tweets: X's **weighted-length limit** and the **headless import bootstrap**.

## When to Use

- Cron / no-agent jobs that post CJK tweets (e.g. the 6-hourly Hermes feature-buzz job).
- Any time you pass a Japanese / Chinese / Korean `text=` to `lm_twitterer_post` / `mod.post()`.
- Diagnosing `CreateTweet ... code 186` or `AttributeError` on a standalone `core.py` import.

## X Weighted-Length Limit (critical for CJK)

X caps tweets at **280 weighted characters**. Latin / digits / symbols = weight 1;
**CJK / Kana / Hangul / full-width = weight 2**. A 211-char Japanese tweet is ~360 weighted and
is rejected at send time with:

```
CreateTweet returned errors: [{'code': 186, ..., 'message': 'Authorization: Tweet needs to be a bit shorter. (186)'}]
```

**Rule of thumb**: keep **raw length ≤ ~140** for CJK-heavy tweets. Always pre-check:

```python
def weighted_len(s):
    n = 0
    for ch in s:
        o = ord(ch)
        if (0x3000 <= o <= 0x30FF or 0x3400 <= o <= 0x9FFF or
            0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFFEF or
            0xAC00 <= o <= 0xD7AF or 0x3040 <= o <= 0x30FF):
            n += 2
        else:
            n += 1
    return n

assert weighted_len(TEXT) <= 280, "trim tweet"
```

Verify before posting with `scripts/weighted_len.py "your text here"`.

## Posting Pattern (explicit text, no generation)

Pass `text=` so the LLM generator cannot rewrite / re-bloat the copy. Put the required hashtag
(e.g. `#HermesAgent`) in the explicit text, not in `topic`. `dry_run=False` to actually post.

```python
result = mod.post("", text=TEXT, dry_run=False)
# result["posted"] == True, result["url"] is the live status URL
```

## Headless / No-Agent Script Bootstrap

When a cron script imports `core.py` directly (not via the Hermes tool wrapper):

1. **Load credentials**: the plugin does NOT auto-load `~/.hermes/.env` in a bare subprocess.
   Parse `LM_TWITTERER_*` keys from it into `os.environ` first.
2. **Register module before exec** — or `@dataclass` raises
   `AttributeError: 'NoneType' object has no attribute '__dict__'`:
   ```python
   spec = importlib.util.spec_from_file_location("lmcore", ".../plugins/lm-twitterer/core.py")
   mod = importlib.util.module_from_spec(spec)
   sys.modules["lmcore"] = mod          # required
   spec.loader.exec_module(mod)
   ```
3. **Js2Py for Python 3.13**: text-only posts still import `tweepy_authlib`, which needs `js2py_`.
   Install the 3.13 build into the **repo `.venv`** (not global Python):
   `uv pip install --python .venv/Scripts/python.exe Js2Py_3.13==0.74.1`

## Verification

- Confirm `result["posted"] == True` and capture `result["url"]`.
- Don't trust success alone: check `~/.hermes/lm-twitterer/activity.jsonl` last line for
  `posted=true, dry_run=false`.
- If `result["url"]` is empty, recover via `mod._find_recent_tweet_url_by_text(None, None, TEXT[:60])`.

## Quick Reference: lm_twitterer_post tool pattern for CJK tweets

```python
# Always use explicit text= to bypass LLM generation (which can bloat CJK copy)
# Always dry_run=False to actually post
result = lm_twitterer_post(
    text="Japanese tweet text with #hashtag",  # pre-validated ≤140 raw chars
    dry_run=False
)
# Returns: {"ok": true, "posted": true, "url": "https://x.com/...", "tweet_text": "..."}
```

**Pre-flight check**: run `scripts/weighted_len.py "your tweet text"` — exits non-zero if >280 weighted.

## Pitfalls

- **Error 186** = weighted length > 280 (CJK = 2). Trim, don't retry.
- **dataclass AttributeError** = forgot `sys.modules["lmcore"] = mod`.
- **ModuleNotFoundError: js2py_** = install `Js2Py_3.13` into repo `.venv`.
- **Empty auth in a subprocess** = forgot to load `~/.hermes/.env` into `os.environ`.

## Support files

- `scripts/weighted_len.py` — reusable CLI that prints raw + weighted length and exits non-zero if > 280.
