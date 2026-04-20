---
name: tdd-orchestrator
description: AI-TDDワークフローのオーケストレーター。plan.mdの次の未実施テストに対してRed→Green→Refactorを隔離サブエージェントで直列実行し、AIの視野を狭めてTDDを規律化します。TDD実装・テスト駆動開発・plan.mdベース実装が要求された場合に使用してください。
argument-hint: [plan.md path]
disable-model-invocation: true
allowed-tools: Read Edit Task Bash
---

# TDD オーケストレーター

plan.md の次の1テストに対して Red → Green → Refactor をフェーズゲート付きで直列実行する。

## 前提条件

満たさない場合は中止し理由を報告:

1. `$ARGUMENTS` で指定された plan.md が存在する
2. plan.md に未チェック（`- [ ]`）のテスト項目がある
3. plan.md の「環境」と「対象ファイル」セクションが記入されている

## plan.md フォーマット（最小要件）

```markdown
# <feature名> テスト計画

## 環境
- テスト実行コマンド: `<例: bundle exec rspec / npx jest / pytest>`
- Lint 実行コマンド: `<例: bundle exec rubocop / npm run lint。なければ「なし」>`
- スタイル規約: `<例: .claude/conventions.md。なければ「言語標準」>`

## 対象ファイル
- 実装: <path>
- テスト: <path>

## テスト一覧
- [ ] 1. [テストの意図を1行で]
- [ ] 2. ...

## 設計メモ
- 守るべき不変条件
- 契約（入力・出力・副作用）
```

## 手順

### 1. 計画読み込み

- `$ARGUMENTS` で渡された plan.md を読む
- 「環境」からテスト/Lint コマンド・規約パスを取得
- 「テスト一覧」の最初の未チェック項目 → `current_test`
- 「対象ファイル」から spec / 実装パスを取得
- 「設計メモ」を控える（サブエージェントへ渡す用）

### 2. Red フェーズ

`Task` tool で `subagent_type: tdd-test-writer` を呼ぶ。渡す情報:

- `current_test`、spec パス、設計メモ
- **テスト実行コマンド**、**スタイル規約パス**（あれば）
- **禁止事項**: 実装ファイル本体、他テスト、類似実装

完了後:
- spec にテスト追加を確認
- 指定コマンドで**失敗確認**
- **sanity check** と報告 → Green/Refactor スキップ、plan.md チェックして完了
- それ以外でパスしている → エスカレーション

### 3. Green フェーズ

`Task` tool で `subagent_type: tdd-implementer`。渡す情報:

- 追加されたテスト、実装パス、設計メモ
- テスト・Lint コマンド、スタイル規約
- **禁止事項**: 他テスト、類似実装ファイル全体、リファクタ提案

完了後:
- spec **全pass**確認
- 失敗時リトライ。**3回連続失敗でエスカレーション**

### 4. Refactor フェーズ

`Task` tool で `subagent_type: tdd-refactorer`。渡す情報:

- 直前の実装ファイル、対応 spec
- テスト・Lint コマンド、スタイル規約
- **禁止事項**: 新機能、テスト変更、インターフェース変更

完了後:
- 全pass維持確認
- 失敗時 revert＋エスカレーション

### 5. plan.md 更新

`current_test` のチェックボックスを `- [x]` に。

### 6. 結果報告

下記の出力形式に従う。

## 警告サイン（即エスカレーション）

- サブエージェント結果に「テスト削除/無効化/skip 化」が含まれる
- 複雑なループでテストを通している
- 指定テスト以外の機能が実装されている

## 出力

```markdown
# TDD サイクル完了

## 実施テスト
[plan.md の項目]

## 結果
- ✅ Red: 追加・失敗確認（または sanity check 保持）
- ✅ Green: 最小実装・全pass（リトライ: N回）
- ✅ Refactor: [内容 または 変更なし]

## 次のテスト
[plan.md の次 または 「全完了」]

## 警告サイン
[なし または 内容]
```

## 原則

- フェーズゲート厳守
- 各サブエージェントに必要最小限のみ渡す
- 迷ったら人間を呼ぶ。粘らない
- 1サイクル1テスト
