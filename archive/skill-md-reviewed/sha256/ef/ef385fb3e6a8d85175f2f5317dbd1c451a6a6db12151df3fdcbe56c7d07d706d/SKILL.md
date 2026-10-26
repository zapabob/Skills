---
name: github-actions-ci-triage
description: Diagnose and fix failing GitHub Actions CI runs — extract failures with `gh run view --log-failed`, distinguish fork failures from upstream approval-gated runs (action_required), apply common fix patterns (subprocess stdin guard, availability-check short-circuits in tests), and verify locally before pushing.
category: devops
---

# GitHub Actions CI トリアージ

## いつ使う
- 「CIが落ちてる / オールグリーンにして / CI直して」と言われたとき
- PRやpush後にCIが赤くなったとき
- forkとupstream両方のCI状態を確認するとき

## 調査ワークフロー
1. fork（または対象repo）の最近のrunを取得:
   `gh run list --repo <owner>/<repo> --limit 15`
   fork作業時は `--repo zapabob/hermes-agent` のように明示。
2. 失敗runの詳細を抜き出す:
   `gh run view <run_id> --log-failed`
   **`--log-failed` が鍵。** 失敗ステップのトレースバック／assertだけが出る。
3. 失敗したテスト名・ソースを特定 → ローカルで再現:
   `python -m pytest <test_file> -q -o addopts=`
   `-o addopts=` は pyprojectのpytest addopts（並列化等）を無効にし、単体で速く回す。

## fork vs upstream の見極め（重要）
- `gh run list` で `action_required` ステータス = **承認待ち**（first-time contributorのワークフロー実行承認）。これは「失敗」ではなく、upstreamの他人PRに多い。直すべきは fork 側の `failure`。
- ユーザーの作業forkの `main` pushで `failure` が出ていたらそれが本命。

## よくある修正パターン

### パターンA: subprocess stdin guard（hermes-agent の convention）
`tests/tools/test_subprocess_stdin_guard.py` は `scripts/check_subprocess_stdin.py` を呼び、TUI-contextの全 `subprocess.run/Popen` に `stdin=subprocess.DEVNULL` を必須とする。
新しくsubprocess呼び出しを追加したら **必ず** `stdin=subprocess.DEVNULL` を付ける。
修正例:
```python
r = subprocess.run(
    cmd, capture_output=True, text=True, timeout=30,
    stdin=subprocess.DEVNULL,
)
```
検証: `python scripts/check_subprocess_stdin.py` → `OK: All TUI-context subprocess calls have explicit stdin=`
詳細は `references/hermes-agent-guards.md`。

### パターンB: テストで availability/setupチェックが本題のValidationより先に弾く
`run_task` 等が冒頭で `check_available()` や設定読み込みを呼び、サブモジュール不在等で先に `ValueError`／`{"ok": False, "status": "blocked", ...}` を返すと、テストしたい分岐（例: `acknowledge_side_effects` 必須）に到達しない。
修正: テスト内で setupゲートを通すようモックする。
```python
monkeypatch.setattr(module.core, "check_available", lambda: True)
```

## 検証ループ（push前）
1. 該当テストをローカルで `pytest -q -o addopts=` で全通過させる。
2. guardスクリプトがあれば直接実行して `OK` を確認。
3. `python -m py_compile <files>` + `ruff check <files>` でsyntax/lintクリア。
4. `git commit` → `git push` → `gh run watch <new_id>` で完了待ち → `success`（All required checks pass）を確認。

## Pitfalls
- `gh run view` 単体だと全ログで埋もれる。`--log-failed` を使え。
- upstreamの `action_required` を「失敗」と勘違いして直そうとしない。
- `pytest` を並列（addopts有効）で回すとsliceに分かれ失敗箇所が探しにくい。ローカル再現は `-o addopts=`。
- push前にローカル検証を省略すると同じ失敗を再度CIで消費する。
- `tests/plugins/test_*.py` のような専用テストファイルが存在しない場合、失敗元はリポジトリ全体をスキャンするルールベーステスト（例: `test_subprocess_stdin_guard.py`）の可能性が高い。修正後はガードスクリプトを直接実行して全体クリアを確認せよ。

## References
- `references/hermes-agent-guards.md` — subprocess stdin guard の詳細と check_available テストパターンの再現レシピ。
