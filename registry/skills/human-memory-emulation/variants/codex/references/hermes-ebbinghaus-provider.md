# Hermes Ebbinghaus Provider Reference

## Files

Expected provider files in `hermes-agent`:

- `plugins/memory/ebbinghaus/__init__.py`
- `plugins/memory/ebbinghaus/plugin.yaml`
- `tests/plugins/test_ebbinghaus_plugin.py`

## Config

```yaml
memory:
  provider: ebbinghaus
plugins:
  ebbinghaus:
    db_path: $HERMES_HOME/ebbinghaus_memory.db
    base_stability_days: 3.0
    decay_threshold: 0.08
    max_prefetch: 5
    min_prefetch_score: 0.16
    auto_encode_turns: false
```

## Data Model

Store one row per memory trace:

- `content`: original memory text.
- `encoded`: JSON cue encoding with summary, cue vector, cues, length.
- `cues`: flattened cue text for quick inspection.
- `tags`: comma-separated tags.
- `salience`: importance from `0.05` to `1.0`.
- `valence`: optional emotional valence from `-1.0` to `1.0`.
- `strength`: learned stability multiplier.
- `rehearsal_count` and `retrieval_count`: strengthen future retention.
- `created_at`, `last_rehearsed_at`, `last_retrieved_at`: retention anchors.

## Retrieval Score

Use a small, explainable blend:

- lexical/cue cosine overlap
- substring match bonus
- tag match bonus
- current retention
- salience
- rehearsal bonus

Return `retention`, `stability_days`, `score`, `cues`, `tags`, and count fields in results.

## Tests To Keep

Cover these behaviors:

- exponential retention curve at 0 days and after multiple stability periods
- duplicate memory reinforcement instead of duplicate rows
- recall by cues/tags
- rehearsal resets retention and increases count
- decay can prune low-retention rows
- provider tool calls and prefetch output
- provider discovery via `plugins.memory.load_memory_provider("ebbinghaus")`
