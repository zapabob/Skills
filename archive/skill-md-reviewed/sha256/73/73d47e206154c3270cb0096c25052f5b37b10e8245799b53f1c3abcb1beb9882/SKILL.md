---
name: puzzle-solving
description: Solve or create small puzzles, quizzes, ciphers, number-to-letter riddles, wordplay, and user-made clue games. Use when the user asks to make a quiz, decode a short string, solve a riddle, interpret numeric hints, or iterate after the user corrects a puzzle-solving approach.
---

# Puzzle Solving

Use this skill for casual puzzle creation and puzzle solving, especially in short chat contexts where the user may be testing whether the agent catches the intended simple rule.

## Default response style

- Keep the first answer short and focused.
- Avoid dumping many obscure theories unless the user asks for exhaustive analysis.
- If the user provides a correction or hint, pivot immediately and acknowledge the intended rule.
- For LINE/Telegram-style chat, prefer compact Japanese and a playful tone when appropriate.

## Solving workflow

1. Parse the exact clue shape before trying broad decoders.
   - Continuous digits: consider common chunk sizes.
   - Spaced chunks: preserve the user's spacing as intentional.
   - Language hint: prioritize encodings for that language.
2. Try the simplest high-signal rule first.
   - If the user says “ひらがな” and “2つの数字につき1つの文字”, check 五十音座標 before ASCII, elements, dates, or English ciphers.
   - If the chunks are two digits like `61 23 11`, treat them as row/column coordinates unless another convention is stated.
3. Show the mapping, not a long theory list.
   - Example: `61 23 11 = 6行1段 / 2行3段 / 1行1段 = は・く・あ`.
4. If uncertain, ask for one targeted hint rather than listing every possible cipher.
   - Good: “日本語？英字？スマホ入力？座標？”
   - Avoid: long multi-system enumerations that bury the likely answer.

## Creating quizzes

- Match the user's current energy: if they ask casually, create a small playable quiz immediately.
- Provide answers separately unless the user wants interactive one-question-at-a-time play.
- For self-referential or in-joke quizzes, keep clues simple enough that the intended answer is discoverable.

## Common pitfalls

- Do not over-index on math/programming-style decoders for casual riddles.
- Do not ignore the user's spacing; spacing often encodes chunk boundaries.
- Do not keep defending previous wrong interpretations after the user says “間違い”. Use the correction as a routing signal.

## References

- See `references/japanese-number-hiragana.md` for Japanese two-digit coordinate decoding patterns and the `61 23 11 -> はくあ` example.
