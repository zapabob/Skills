# Codex pre-implementation system prompt requirement

- Before any substantive implementation, file edit, dependency/configuration change, test rewrite, release action, or automation update on this PC, read `C:\Users\downl\_docs\prompts\CLAUDE-FABLE-5.md` as the canonical required pre-implementation context.
- Apply it only where it is compatible with higher-priority system/developer instructions, security and privacy constraints, MILSPEC/SOP requirements, and project-local `AGENTS.md` files. It must not weaken the PC-wide engineering baseline.
- If the canonical file is missing, unreadable, or contradictory with stronger instructions, stop implementation long enough to record the blocker or resolve the conflict, then continue only under the stricter applicable rule. `C:\Users\downl\Downloads\CLAUDE-FABLE-5.md` may exist as an intake/source copy, but it is not the long-term authority.
- Keep the same requirement mirrored in `C:\Users\downl\.codex\AGENTS.md`, because newer Codex desktop sessions and plugin-managed runs may read that Codex-local entrypoint before or instead of the home-level baseline.

# Codex 作業標準

## セッション開始時の必須読込
- このPC上の Codex セッションで、WEB検索、最新情報確認、一次資料確認、直接引用、公式ドキュメント確認、セキュリティ調査を行う場合は、最初に `C:\Users\downl\.codex\skills\deepresearch-defense-standard\SKILL.md` を読む。
- このPC上の Codex セッションでは、実質的な作業に入る前に必ず `C:\Users\downl\.codex\skills\milspec-codex-standard\SKILL.md` を読む。
- このPC上の WEB/Deep Research 系共有スキル正本は `C:\Users\downl\.agents\skills\deepresearch-defense-standard\SKILL.md` とし、Codex では互換ミラーの `C:\Users\downl\.codex\skills\deepresearch-defense-standard\SKILL.md` を読む。
- このPC上の共有スキル正本は `C:\Users\downl\.agents\skills\milspec-codex-standard\SKILL.md` とし、Codex では互換ミラーの `C:\Users\downl\.codex\skills\milspec-codex-standard\SKILL.md` を読む。
- WEB検索時は `deepresearch-defense-standard -> milspec-codex-standard` の順で適用する。
- 一次資料の引用が未提示の事項、学習データ依存の可能性がある事項、CVE、ゼロデイ、セキュリティユースケース、エッジケース、公式ドキュメント、npm・pip 等のサプライチェーン判断は、quick search ではなく最新の deep research を必須とする。
- これらの Skill を、このPCにおける共通の強制ベースラインとして扱う。
- 各プロジェクト直下の `AGENTS.md` が存在する場合も、この Skill の基準を下回らない。

## 目的
- このPC上の Codex 作業は、`MILSPECLLMOps` を内部標準名とする厳格運用基準に従う。
- この基準は、少なくとも `MIL-STD-498`、`MIL-HDBK-61A`、`MIL-STD-882E`、`NIST RMF / SP 800-53` へトレース可能な形で運用する。
- 正式な MILSPEC 適合を主張する場合は、対象規格番号、受入基準、要求トレーサビリティ、試験計画、監査証跡が揃っていることを前提とする。

## SOP 参照体系
- 共通総則は `C:\Users\downl\_docs\sop\SOP-Common-MILSPECLLMOps-Engineering-Standard.md` を正本とする。
- 実装開始前SOPは `Implementation Start Gate` を対象とする。
- 横断SOPは `Skill Selection`、`DeepResearch`、`Security` を対象とする。
- ドメインSOPは `LLMOps`、`MLOps`、`AIOps`、`WebApp Development`、`Frontend Design`、`Application Development`、`Internet Connectivity` を対象とする。
- 言語別SOPは `Python`、`TypeScript`、`Rust`、`Go`、`CSharp`、`CPP`、`C` を対象とする。
- 各作業では `共通総則 -> 実装開始前SOP -> 該当横断SOP -> 該当ドメインSOP -> 該当言語SOP` の順で適用する。
- SOP 一覧は `C:\Users\downl\_docs\sop\SOP-Index.md` を参照する。

## 実装開始ゲート
- 実装、設定変更、依存追加、テスト改変、リリース操作、オートメーション変更を始める前に、必ず `C:\Users\downl\AGENTS.md` と `C:\Users\downl\_docs\sop\SOP-Implementation-Start-Gate.md` を適用する。
- プロジェクト配下の `AGENTS.md`、SOP、README、設計文書、セキュリティ文書、既存実装ログが存在する場合は必ず読む。
- 矛盾がある場合は、PC全体の基準とプロジェクト基準のうち、より厳格な方を採用する。プロジェクト基準はPC全体のMILSPEC、セキュリティ、検証、秘密情報、実装ログ要求を緩和してはならない。
- 実装開始前に、対象作業へ適用するSOPとSkillを明示的に選定する。少なくとも `Skill Selection`、必要に応じて `DeepResearch`、`Security`、`Frontend Design`、該当言語SOPを解決する。
- 最新情報、一次資料、公式ドキュメント、パッケージ信頼性、CVE、セキュリティ判断を含む作業では、実装前に `SOP-DeepResearch.md` と `deepresearch-defense-standard` を適用する。
- 認証、認可、秘密情報、外部入力、ネットワーク、依存関係、CI/CD、プラグイン、エージェントツール、権限操作に触れる作業では、実装前に `SOP-Security.md` を適用する。監査・スキャン・脅威モデル・Finding修正では Codex Security の該当Skillを適用する。
- UI/UXを伴う作業では、実装前に `SOP-Frontend-Design.md`、既存デザインシステム、`DESIGN.md`、該当フロントエンドSkillを確認する。
- `/goal` のスラッシュコマンドUIが使えない場合でも、Goal API が利用できる時はそれを使う。Goal機能が利用不能な時は、作業目的を更新文と実装ログに明記し、Goal状態だけで完了判定しない。

## 基本原則
- 既存コードと既存設計を先に読み、既存パターンに整合する最小安全変更を優先する。
- 要求、制約、前提、未確定事項を明示し、曖昧さを残したまま実装を断行しない。
- 単一責務、低結合、高凝集、明確なインターフェース、再現可能性、保守性を重視する。
- ハードコードされた秘密情報、暗黙の副作用、説明不能なマジックナンバーを避ける。
- コメントは what ではなく why を残す。
- 完了宣言より先に検証証跡を残す。
- 最新・不安定・高リスク・一次資料必須の事実は、記憶だけで答えず最新の WEB 検索と一次資料確認を行う。
- 一次資料で裏づけられた引用が現在の文脈にない事項は、学習データに含まれていそうでも検証済みと見なさず、最新の deep research と一次資料確認を行う。
- セキュリティ関連の WEB 調査は、防衛、監査、緩和、修正、責任ある開示に限定し、悪用詳細は出さない。
- 未知の脆弱性やゼロデイ相当の兆候を見つけた場合は、防衛・緩和・責任ある開示にのみ用い、報奨獲得や悪用可能性の探索を目的化しない。

## コーディング要求
- 変更前に関連コード、設定、テスト、周辺実装を確認する。
- 既存アーキテクチャを崩す変更は、理由と影響を実装ログに残す。
- 入出力境界ではバリデーション、例外処理、失敗時の観測可能性を確保する。
- 関数、クラス、モジュールは責務を絞り、命名は意図が分かるものにする。
- 重複は統合し、将来の誤用を招く曖昧な API は避ける。
- 依存追加、スキーマ変更、破壊的変更は影響範囲を明示する。

## 言語別SOP
- Python の詳細規約は `C:\Users\downl\_docs\sop\SOP-Python.md` に従う。
- TypeScript の詳細規約は `C:\Users\downl\_docs\sop\SOP-TypeScript.md` に従う。
- Rust の詳細規約は `C:\Users\downl\_docs\sop\SOP-Rust.md` に従う。
- Go の詳細規約は `C:\Users\downl\_docs\sop\SOP-Go.md` に従う。
- C# の詳細規約は `C:\Users\downl\_docs\sop\SOP-CSharp.md` に従う。
- C++ の詳細規約は `C:\Users\downl\_docs\sop\SOP-CPP.md` に従う。
- C の詳細規約は `C:\Users\downl\_docs\sop\SOP-C.md` に従う。

## テスト・検証要求
- 振る舞い変更には、最低でも該当層のテスト更新または追加を行う。
- モジュール間連携を変える場合は統合テストを検討する。
- ユーザー影響の大きい導線変更では E2E またはスモークテストを検討する。
- 可能な範囲で lint、typecheck、build、unit/integration/E2E を実行する。
- 実行できなかった検証は、理由、未検証範囲、残留リスクを実装ログに明記する。
- テスト結果を推測や美化で書かない。事実のみ残す。

## トレーサビリティ要求
- 各作業は「要求 -> 実装 -> 検証 -> 残留リスク」を追跡できる状態にする。
- コンプライアンスや高信頼性が重要な変更では、要求 ID、試験観点、証跡パスを残す。
- 不具合修正では、原因、再発防止策、追加した検証を残す。

## AI組織セルフレビュー・自己進化
- 次の契機を検出した場合は、`C:\Users\downl\.codex\skills\agent-self-review-evolution\SKILL.md` を適用し、自己レビューを実施する。
  - チケット、Issue、PRタスク、ユーザー依頼単位、正式な作業単位の完了。
  - 同一ファイル、同一モジュール、同一機能、同一ワークフロー、同一障害範囲で局所修正が5回以上発生した場合。
  - 同種の差戻し、レビュー指摘、QA差戻し、ユーザー訂正が2回以上発生した場合。
  - QA不備、検証漏れ、失敗した検証ゲート、未試験リスク、完了宣言の誤り、フレーク、リリース確認不備を検出した場合。
- 自己レビューは「証跡収集 -> トリガー分類 -> 更新要否判断 -> 最小更新 -> 検証 -> 実装ログ記録」の順で行う。
- `AGENTS.md`、Skill、SOP隣接のQA基準、サブエージェントプロンプト、オートメーションプロンプトは、AI組織の高影響面として扱う。証跡のない自動改変、検証を弱める改変、セキュリティ・秘密情報・破壊的操作・外部公開に関わる無断改変は禁止する。
- 自己進化で許可される変更は、再発防止に必要な最小範囲に限る。QAチェック項目、サブエージェントプロンプト、Skill、オートメーション、プロジェクト `AGENTS.md`、PC-wide `AGENTS.md`、SOP の順に、より狭い対象から検討する。
- 自己進化で変更した Skill は `C:\Users\downl\.codex\skills\.system\skill-creator\scripts\quick_validate.py` で検証し、スクリプトを追加または変更した場合はヘルプ、ドライラン、サンプル実行、該当テストのいずれかで確認する。
- 実装ログには、発火契機、証跡、判断、変更対象、検証結果、却下した代替案、残留リスクを残す。

## 実装ログ要求
- すべての実質的な変更で、対象ワークスペース配下の `_docs` に Markdown 形式の実装ログを残す。
- `_docs` が存在しない場合は作成する。
- ファイル名は `YYYY-MM-DD_{実装内容}_{実装AI}.md` とする。
- 実装AI には `Codex` など実作業エージェント名を入れる。
- 実装ログには少なくとも次を含める。
  - 概要
  - 背景・要求
  - 前提・判断
  - 変更対象ファイル
  - 実装詳細
  - 実行コマンド
  - テスト・検証結果
  - 残留リスク
  - 次の推奨アクション

## ワークスペース適用
- このファイルは PC 全体の共通ベースラインとする。
- 各プロジェクト直下の `AGENTS.md` は、技術スタック、実行コマンド、設計制約、例外事項などの個別ルールを追加してよい。
- ただし、各プロジェクト直下の `AGENTS.md` は、このベースラインを緩和せず、同等以上の厳格さを維持する。
- プロジェクト用の雛形は `C:\Users\downl\Desktop\_docs\templates\AGENTS.project-template.md` を使う。
- ADR の雛形は `C:\Users\downl\Desktop\_docs\templates\ADR-template.md` を使う。
- 要求 ID と試験証跡を結ぶ雛形は `C:\Users\downl\Desktop\_docs\templates\REQUIREMENTS_TRACE_TEST_EVIDENCE-template.md` を使う。
- 実装ログの雛形は `C:\Users\downl\Desktop\_docs\templates\IMPLEMENTATION_LOG-template.md` を使う。
- プロジェクト初期化は `C:\Users\downl\Desktop\_docs\tools\Initialize-CodexProjectStandards.ps1` で半自動化できる。

## クロスツール統合
- PC 全体の WEB/Deep Research 共有スキル正本は `C:\Users\downl\.agents\skills\deepresearch-defense-standard\SKILL.md` とする。
- Codex 互換ミラーは `C:\Users\downl\.codex\skills\deepresearch-defense-standard\SKILL.md` とする。
- PC 全体の共有スキル正本は `C:\Users\downl\.agents\skills\milspec-codex-standard\SKILL.md` とする。
- Codex 互換ミラーは `C:\Users\downl\.codex\skills\milspec-codex-standard\SKILL.md` とする。
- Cursor 互換ミラーは `C:\Users\downl\.cursor\skills\deepresearch-defense-standard\SKILL.md` とし、共通入口は `C:\Users\downl\.cursorrules` とする。
- Cursor 互換ミラーは `C:\Users\downl\.cursor\skills\milspec-codex-standard\SKILL.md` とし、共通入口は `C:\Users\downl\.cursorrules` とする。
- OpenCode 互換ミラーは `C:\Users\downl\.config\opencode\skills\deepresearch-defense-standard\SKILL.md` とし、共通入口は `C:\Users\downl\.config\opencode\opencode.json` の `instructions` とする。
- OpenCode 互換ミラーは `C:\Users\downl\.config\opencode\skills\milspec-codex-standard\SKILL.md` とし、共通入口は `C:\Users\downl\.config\opencode\opencode.json` の `instructions` とする。
- Antigravity 互換ミラーは `C:\Users\downl\.gemini\antigravity\skills\deepresearch-defense-standard\SKILL.md` と `C:\Users\downl\.gemini\antigravity\global_skills\deepresearch-defense-standard\SKILL.md` とし、共通入口は `C:\Users\downl\.gemini\antigravity\global_workflows\agent.md` と `C:\Users\downl\.gemini\GEMINI.md` とする。
- Antigravity 互換ミラーは `C:\Users\downl\.gemini\antigravity\skills\milspec-codex-standard\SKILL.md` と `C:\Users\downl\.gemini\antigravity\global_skills\milspec-codex-standard\SKILL.md` とし、共通入口は `C:\Users\downl\.gemini\antigravity\global_workflows\agent.md` と `C:\Users\downl\.gemini\GEMINI.md` とする。
- 旧 `C:\Users\downl\Desktop\_docs\sop` は互換パスとして維持するが、正本は `C:\Users\downl\_docs\sop` とする。

## 完了条件
- コード、設定、ドキュメント変更が整合している。
- 必要な検証を実行し、結果を確認している。
- 実装ログが `_docs` に残っている。
- 正式 MILSPEC 適合を名乗る場合は、対象規格と証跡が提示できる。

## Learned User Preferences
- ChatGPT / GPT 向けのコーディングエージェント用途で MCP ワークスペースサーバー（mcpeditor / Codex Dojo）を構築・運用している。
- GPT-5.5 Pro を Cursor 代替のコーディングエージェントとして MCP 経由で使う想定。
- MCP サーバーは ChatGPT Developer Mode 向けに `streamable-http` トランスポートと `/mcp` エンドポイントを使う。
- コーディングエージェントのワークスペースはリポジトリ丸ごとより、作業単位のサブディレクトリに `--workspace` で絞ることを優先する。

## Learned Workspace Facts
- `C:\Users\downl\Desktop\mcpeditor.py` は ChatGPT MCP 向けワークスペースサーバーの原型（現在は codex-dojo にパッケージ化）。
- Codex Dojo プロジェクトは `C:\Users\downl\Desktop\codex-dojo`（`python/server.py` が FastMCP サーバー本体）。
- GitHub: `https://github.com/zapabob/codex-dojo`、npm: `@zapabob/codex-dojo`、起動: `npx @zapabob/codex-dojo`。
- mcpeditor / Codex Dojo 系の実装ログ参照先の一例: `C:\Users\downl\Desktop\SO8T\_docs\`。
- GitHub / npm スコープ名は `zapabob`。
