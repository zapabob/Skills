---
name: obsidian-external-memory-journaling
description: Maintain Obsidian external memory, journals, and recall.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Memory, Obsidian, Git, Journaling, Recall]
---

# Obsidian External Memory and Journaling

このスキルは、Ebbinghaus内部記憶とObsidian/Git外部記憶を接続し、長期知識・日記・夢日記を保存して後から想起できるようにする。生セッションログ、認証情報、秘密情報を外部記憶へそのまま保存するものではない。Windowsでは既存のPython 3.12ランチャーと標準ライブラリ中心の検索スクリプトを使い、追加依存を前提にしない。

## When to Use

- 「外部記憶をObsidianに保存して」
- 「日記帳と夢日記を作って」
- 「ObsidianやGitから記憶を呼び出せるようにして」
- 「記憶の統合と睡眠をObsidianへ反映して」
- 「外部記憶の検索機能を追加して」

## Prerequisites

- HermesのEbbinghaus記憶ツール: `ebbinghaus_memory`
- Hermes fork: `%USERPROFILE%\Documents\New project\hermes-agent`
- 正規のGit管理Wiki: `%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki`
- WikiのGit remote: `origin` / `main`
- Windows Python 3.12ランチャー: `py -3.12`
- Git push権限

## How to Run

Hermesでは、読み取りに `read_file` / `search_files`、ファイル作成に `write_file`、既存ファイルの限定編集に `patch`、Python実行とGit操作に `terminal` を使う。記憶の統合には `ebbinghaus_memory`、永続的なユーザー設定には `memory` を使う。外部記憶を検索する場合は、Wikiルートで `terminal` から `py -3.12 tools/recall_external_memory.py "検索語"` を実行する。

## Quick Reference

- Ebbinghaus睡眠: `ebbinghaus_memory(action="sleep", prune_mode="archive")`
- Wiki root: `%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki`
- 外部記憶検索: `py -3.12 tools/recall_external_memory.py "検索語"`
- Git履歴を含む検索: `py -3.12 tools/recall_external_memory.py "検索語" --git-history`
- 日記: `diary/YYYY-MM-DD.md`
- 夢日記: `dreams/YYYY-MM-DD.md`
- 長期知識: `concepts/*.md`
- サニタイズ済みraw: `raw/memory/`
- Git確認: `git status --short` / `git diff --check`
- Push確認: `git status --branch --short`

## Procedure

1. `ebbinghaus_memory(action="stats")` で現在の記憶状態を確認する。必要なら `ebbinghaus_memory(action="sleep", prune_mode="archive", rehearse_threshold=0.45, forget_threshold=0.08, salience_keep_threshold=0.7, limit=200)` を実行する。
2. Wiki rootの存在とGit remoteを、`terminal` から確認する。正規のpush先は `ObsidianVault/Hermes-Memory-Wiki` であり、旧 `New project/llm-wiki` はpush対象にしない。
3. 外部記憶の役割分担を `concepts/external-memory-architecture.md` に記録する。Ebbinghausは内部記憶、Obsidianはサニタイズ済み長期記憶、Gitは版管理と過去想起と明記する。
4. 日記運用を `diary/README.md` に作成する。日付ごとの `diary/YYYY-MM-DD.md` に、要点・できたこと・気づき・感情・引き継ぎを記録する。
5. 夢日記運用を `dreams/README.md` に作成する。日付ごとの `dreams/YYYY-MM-DD.md` に、場面・象徴・感情・起床後の印象・解釈（仮説）を記録する。夢の内容と解釈は分離する。
6. `tools/recall_external_memory.py` をWikiに置く。現在のMarkdownを全語AND検索し、`--git-history` 指定時は `git log --all --oneline -S` で過去コミットも検索する。出力時に秘密情報、長いトークン、メールアドレスをサニタイズする。
7. `index.md` に外部記憶アーキテクチャ、日記、夢日記へのObsidian wikilinkを追加する。
8. `terminal` から次を実行して検証する。
   ```bash
   cd "%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki"
   py -3.12 tools/recall_external_memory.py "外部記憶" --git-history --limit 5
   py -3.12 -m py_compile tools/recall_external_memory.py
   ```
9. `terminal` から `git diff --check` と秘密パターン確認を行い、生成されたPythonキャッシュをコミットしない。必要なら `.gitignore` に `__pycache__/` と `*.py[cod]` を追加する。
10. ユーザーが明示的にpushを依頼した場合だけ、`terminal` から以下を実行する。
   ```bash
   git add -A
   git diff --cached --check
   git commit -m "feat(memory): add external memory diary dream journal and recall"
   git push origin main
   ```
11. push後に `git status --branch --short`、`git rev-parse --short HEAD`、`git rev-parse --abbrev-ref --symbolic-full-name '@{u}'` を実行し、cleanかつ `origin/main` と同期していることを確認する。
12. 検索・サニタイズ・Git履歴・gitignoreを確認する一時検証スクリプトが必要な場合は、`execute_code` で `tempfile` の `hermes-verify-` 接頭辞ファイルを作り、実行後に必ず削除する。正式なテストスイートの成功とは表現せず、アドホック検証の成功と報告する。

## Pitfalls

- `python` がMicrosoft StoreエイリアスになるWindows環境では、`py -3.12` を使う。
- `New project/llm-wiki/Hermes-Memory-Wiki` は旧・別コピーになり得る。`sync_memory.py` の出力絶対パスとGit remoteを確認してから編集・pushする。
- Obsidianへ生セッションログ、SQLiteダンプ、JSONL全文を保存しない。
- APIキー、token、password、Cookie、メールアドレス、長い不透明トークン、絶対ホームパスをノートへ書かない。
- `py_compile` は `__pycache__` を生成する。`.gitignore` で除外し、誤って追加した場合は削除して別コミットする。
- `git diff --check` の空欄テンプレート `- ` は末尾空白として失敗するため、`-` を使う。
- 「現在のノート検索」と「Git履歴検索」は別結果である。両方必要な場合だけ `--git-history` を指定する。
- アドホック検証はテストスイートではない。実行結果をその区別付きで報告する。

## Verification

Wiki rootで次の1コマンドを実行し、検索結果に現在のノートとGit履歴が出て、終了コード0になることを確認する。

```bash
cd "%USERPROFILE%\Documents\ObsidianVault\Hermes-Memory-Wiki" && py -3.12 tools/recall_external_memory.py "外部記憶" --git-history --limit 5
```
