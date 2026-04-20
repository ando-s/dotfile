# AI と TDD を組み合わせる

Claude Code などの AI エージェントと TDD を組み合わせたワークフロー。
言語非依存。RSpec / pytest / jest 等いずれでも plan.md にコマンドを記載すれば回せる。

## なぜこの構造か

2026年時点の調査結果（Kent Beck / Addy Osmani / alexop.dev / Qiita J-SIX#3 等）から得た合意点:

- **AI自走のみの成功率は低い**: Anthropic 社内で Claude Code 初回自律実行成功率 約33%。テスト＋リトライ＋人間ゲートで補う
- **テスト無しAIは壊す**: "Without tests, the agent might blithely assume everything is fine" (Addy Osmani)
- **全体文脈を渡すと既存カオスを拡大する**: "That giant function? I just added another 20 lines to it." (Kent Beck)
- **成功パターンは共通**: 人間=設計オーナー / AIの視野を狭める / フェーズゲート / エスカレーション閾値

## 4つの原則

### 原則1: 人間が設計オーナー

テスト計画（plan.md）は人間が書く。AI は「次の1テスト」を渡されて実行するのみ。
設計判断（インターフェース・分割粒度）は人間が握る。

### 原則2: AI の視野を狭める

- テストを書く AI に実装計画を見せない
- 実装する AI にリファクタリング視点を持たせない
- 各サブエージェントは隔離コンテキストで動く

→ 既存コードへの「引きずられ」を物理的に防ぐ。

### 原則3: フェーズゲート

Red → Green → Refactor を直列実行。
前フェーズの完了条件（失敗確認 / 全pass確認）を満たすまで次へ進まない。

### 原則4: 3回連続失敗＝エスカレーション

同一テストで Green が3回連続失敗したら人間を呼ぶ。
「根本的な設計問題の可能性」があるため、AI に粘らせない。

## 関連 skill / agent

隔離コンテキストを効かせるため、統括のみ skill、実行部は agent に分けてある。

| 名前 | 種別 | 役割 |
|------|------|------|
| `tdd-orchestrator` | skill | 統括。plan.md を読んで Red→Green→Refactor を直列実行。Task ツールで各 agent を呼ぶ |
| `tdd-test-writer` | agent | Red 専用。失敗するテストを1つ書く |
| `tdd-implementer` | agent | Green 専用。最小実装でテストを通す |
| `tdd-refactorer` | agent | Refactor 専用。テスト通過維持でコード改善 |

定義場所: dotfile 内の `claude/skills/` と `claude/agents/`。`install.sh` で `~/.claude/` に symlink される。

## 運用上の注意

### agent 追加時はセッション再起動

`~/.claude/agents/` に新規 agent を追加 / 変更した後は、**Claude Code セッションを再起動しないと Task tool で認識されない**。

## plan.md のフォーマット

plan.md は feature 単位で自由な場所に置く。フォーマット:

```markdown
# <feature名> テスト計画

## 環境
- テスト実行コマンド: `<例: bundle exec rspec / npx jest / pytest>`
- Lint 実行コマンド: `<例: bundle exec rubocop / npm run lint。なければ「なし」>`
- スタイル規約: `<例: .claude/conventions.md。なければ「言語標準」>`

## 対象ファイル
- 実装: packs/xxx/app/models/yyy.rb
- テスト: packs/xxx/spec/models/yyy_spec.rb

## テスト一覧
- [ ] 1. [テストの意図を1行で]
- [ ] 2. [テストの意図を1行で]
- [ ] 3. [テストの意図を1行で]

## 設計メモ
- 守るべき不変条件
- 契約（入力・出力・副作用）
- 参照すべき設計判断
```

「テスト一覧」は Kent Beck の plan.md 方式。上から順に1つずつ消化する。
**未来のテストを先読みしない**（視野制限）。

### テスト一覧を書くときの指針（Canon TDD）

- **振る舞いで書く、実装詳細を混ぜない**: 「`calculate_total(items)` が `Integer` を返す」ではなく「カート合計は購入品の合計額になる」。メソッド名・データ構造・クラス分割は Green フェーズで決まる
- **順序は重要なスキル**: 基本ケース → 境界条件 → 複雑なパスの順で並べる。簡単なものから始めて段階的に複雑化させると、各 Green で必要な実装量が小さく保たれる
- **アサーションの無いテスト項目は書かない**: 「〇〇を確認する」ではなく「〇〇の結果が△△になる」という検証可能な文で書く

## 使い方

### 起動例

```
/tdd-orchestrator path/to/plan.md
```

または

```
tdd-orchestrator で path/to/plan.md やって
```

### 内部フロー

1. **Red**: `tdd-test-writer` が次の未チェックテストを1つ書く → 失敗確認
   - 例外: 意図が明確に新規かつ既存実装で通る場合は **sanity check として保持**。Green/Refactor はスキップし plan.md のみ更新
2. **Green**: `tdd-implementer` が最小実装を書く → 全pass 確認
3. **Refactor**: `tdd-refactorer` が改善または「変更なし」判定 → 全pass 維持確認
4. plan.md の該当項目を `- [x]` に更新
5. 人間に報告

#### sanity check の扱い（Canon TDD との折衷）

「パスする Red は失敗」が原則だが、Uncle Bob の bowling kata の「all ones」のような **先行テストと明確に異なる入力パターンで既存実装を確認するテスト** は、TDD として正統で価値がある。test-writer は以下の2ケースを区別する:

| ケース | 判定 | 対応 |
|---|---|---|
| 意図が新規・入力パターンが先行テストと異なる | sanity check | テスト保持、Green/Refactor スキップ |
| 先行テストと重複 / 実装を覗いて書いた疑い | 引きずられ | テスト破棄、書き直し |

## エスカレーション条件

以下いずれかで即 orchestrator が停止し、人間に判断を渡す:

- Green が同一テストで3回連続失敗
- AI の提案に「テストを削除/skip/無効化」が含まれる（Kent Beck 警告サイン③）
- テストを通すために複雑なループが生成される（Kent Beck 警告サイン①）
- 指定テスト以外の機能が実装される（Kent Beck 警告サイン②）

## アンチパターン

### ❌ 後書きテスト

実装後に「動くこと」を確認するテストを書くのは TDD ではない。
BSWEN 引用: "Tests written after implementation rarely drive design. They just confirm what I already built."

### ❌ 一度に複数テスト書かせる

視野が広がり、既存実装への引きずられが発生する。**必ず1テストずつ**。

### ❌ 全体文脈を渡す

「このパッケージ全部読んでからテスト書いて」は原則2違反。
必要最小限のファイルだけ渡す。

### ❌ AI がテストを通すためにテストを消す

Kent Beck が指摘する最大のリスク。Green 失敗時にテスト変更の提案が出たら即エスカレーション。

### ❌ Refactor で新機能追加

Refactor は振る舞いを変えない。新機能は次のテストで導入する。

## 参考

- [Kent Beck『Augmented Coding: Beyond the Vibes』](https://tidyfirst.substack.com/p/augmented-coding-beyond-the-vibes)
- [Kent Beck『Augmented Coding & Design』](https://tidyfirst.substack.com/p/augmented-coding-and-design)
- [Kent Beck『Canon TDD』](https://tidyfirst.substack.com/p/canon-tdd)
- [Addy Osmani『My LLM coding workflow going into 2026』](https://addyosmani.com/blog/ai-coding-workflow/)
- [alexop.dev『Forcing Claude Code to TDD』](https://alexop.dev/posts/custom-tdd-workflow-claude-code-vue/)
- [Qiita『TDD × Claude Code 自律実行』](https://qiita.com/SeckeyJP/items/a9dc743a14977686adbf)
