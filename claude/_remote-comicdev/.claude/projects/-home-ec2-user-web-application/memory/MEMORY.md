# Project Memory

## JIRA
- **jira-cli** (`/usr/local/bin/jira`) を使用。JIRA MCPは廃止済み（2026-04-03削除）
- Config: `~/.config/.jira/.config.yml` (default project: NUTSAFSBPS, board: 669)
- Epics can't be children of Epics in JIRA - use ストーリー or カイゼン under Epic
- [AF移行はプロバイダ別プロジェクト](nuts-af-jira-projects-by-provider.md) — SBPS=NUTSAFSBPS / クレカ(sony_payment)=NATSCREAF。クレカ操作は `-p NATSCREAF` 明示
- [課題タイプ変更はbulk move API](jira-convert-task-to-subtask.md) — jira-cliもPUTも不可。サブタスク⇄タスク⇄エピック双方向可。移動でスプリントと親が消えるのでPUTで入れ直す。開始日=customfield_10015 / 期限=duedate
- [jira issue create が共有configで失敗](jira-cli-create-config-broken.md) — issue typeメタ欠落。JIRA_CONFIG_FILEで一時init--forceして回避

## NUTSAFSBPS Project
- Board ID: 669, 1-week sprints, avg velocity ~2 SP/sprint
- See [nutsafsbps-details.md](nutsafsbps-details.md) for detailed ticket structure

## Nuts Architecture
- Packwerk modular monolith: `packs/nuts/`
- Key components: Writer, Reader, Resolver, Policy, Controller, Restorer
- Event sourcing (ADR-008/009), Factory pattern for AF/CF merchants
- Feature flag: `app/models/nuts_feature_flag.rb` - DB-based per-store toggle
- Spica batch: `packs/orion/lib/orion/softbank_b/continue_summary.rb` - 4-step flow (Continue → DemandBilling → FixBilling → ConfirmContinue)
- ADR folder: `packs/nuts/softbank/docs/adr/` (ADR-001 to ADR-032)
- [AF SBPS 登録capture救済の切替](af-sbps-entry-capture-recovery-cutover.md) — FF排他スイッチ／ロールバック挙動／softbank2はapp経路(jobではない)／'99'はDocomo専用／Nuts↔Spicaで救済哲学逆転／本番実績はFF ON→リストア→バッチでADR-039補遺の記載と逆
- [登録capture救済 後続MR](capture-recovery-followup-mrs.md) — MR-16324状態／timeout救済追加／Spica既capture復元スクリプトの方針
- [481 plan レビュー方針決定](481-plan-review-direction.md) — order_id採番イベント(OrderIdAssigned)最小構成＋Metabase検知＋運用責務。[must]下書き(32577)未送信／m-kitanoは業務委託でMetabase不知
- [Nutsの語彙変換点は外部送信点](nuts-vocabulary-translation-at-wire.md) — プロバイダ層(Nuts::SonyPayment等)の公開I/Fも共通語彙。ベンダー語は電文組み立てのみ。固有概念は接頭辞付き
- [登録開始は契約状況側の進捗](register-start-is-status-progress.md) — RegisterStartは決済進捗(RegisterPaymentProgress)に置かない方針。ADR-047整合。MR!16667に[should]下書き済み
- [65項目4のNULL tracking 1709件は解約済み復元契約](nutssbpscf65-null-tracking-register-events.md) — MR!16719。①は出所=一括復元(2025/11)の既解約af契約(register+解約のみ、authorize/capture無し)。ゲートは④=0で①ではない。申込要求は本番未稼働
- [ADR-047申込要求コース移行のNuts↔Spica整合](adr047-shift-course-nuts-notify-consistency.md) — pagecon受け口はNuts(register_free_controller)、notify_nuts_merchant→Spica callback_nuts。RegisterEventはNutsトランザクション内なので通知失敗でロールバック＝二重課金にならない(当初の原子性ギャップ指摘は誤り)
- [ADR承認状態(Status)運用を廃止](adr-status-convention-removed.md) — マージ=可決済み。テンプレ・既存ADRからStatus削除(MR!16721)。経緯ログは保持。新規ADRにStatus節を作らない
- [ユビキタス言語表はドメイン用語限定](ubiquitous-language-table-scope.md) — 実装・アーキ・環境用語は載せない。掲載基準はStatusでなくコード確定。呼称ゆれは正規語1つ＋類語列
- [決済代行移行の実績Driveドキュメント](card-provider-migration-precedent-doc.md) — GMO→SonyPayment(AF 2025/5・CF 2025/10)の要件・当日手順・懸念・振り返り。移行は会員データ移送＋接続先切替で解約ではない
- [クレカ(e-SCOTT)外部API仕様の一次資料](escott-sonypayment-primary-source-facts.md) — Google Driveの接続仕様書で裏取り。取消/返品/金額変更あり(1Delete/1Change)、会員ID共有はAF/CF可(事業者単位)。コード不在≠仕様不在
- [決済一次資料のDriveフォルダ構成](payment-spec-drive-folder-map.md) — 決済ルート配下にプロバイダ別。SBPSは「未格納」ではなく実在（スキル表が古い）。atone/PayPayは到達不可。search_filesはDriveクエリ構文
- [追跡コードはプロバイダへ渡さない](nuts-tracking-code-not-passed-to-provider.md) — 加盟店発行識別子の交わりは20桁半角英数字。共通形式は作れない。SBPSだけ素通しでADR-020から外れている
- [AFクレカの契約追跡コードは全件埋まった](af-card-tracking-code-fully-backfilled.md) — 継続中73,656件で列が空0件／Nutsと直接一致9,783件／残63,873件。order_code起点の契約解決・復元は成立しない
- [コース移行の責務分離設計](shift-course-responsibility-split-design.md) — NUTSSBPSCF-68。Nutsに移行機能を持たせず解約+登録の組み合わせ／移行時非課金のみ／CF専用

## Review Campaigns
- [NATSCREAF クレカMR順次レビュー](natscreaf-cc-review-campaign.md) — 16723→684→685→686→688→690→689→694の順。基盤16683はマージ済。引き継ぎ事項あり

## Workflow
- [E2Eの進め方はAIがMRで変えない](e2e-process-changes-need-team-agreement.md) — 改善メモに書いてチーム相談後に反映。実装バグ修正のMRは対象外
- [1つの開発環境を触るエージェントは1つ（案・未決定）](one-agent-per-dev-environment.md) — ポート取り合いで環境が落ち、二重調査で食い違う報告が残る。決定ではない
- [クレカ設計の決定事項12.3は誤り](card-token-name-logging-decision-12-3.md) — トークンと名義を伏せる決定を撤回。MR!17219はクローズ、記述側を直す
- [Playwright MCPはブラウザ未インストールで落ちる](playwright-mcp-browser-install.md) — chrome-for-testing の要求ビルドが上がると突然失敗。install-browser で解消
- [EC2のheadlessブラウザはdevアプリとe-SCOTTテストに到達する](e2e-browser-reachability-from-ec2.md) — カード系E2Eのブラウザ通しはClaude側で実行可能。.env読取は拒否されるのでdocker inspectで取る
- [内部APIではfilter_parametersが効かない](internal-api-client-skips-parameter-filter.md) — routes.callでenv_configを通らずParametersログは無フィルタ。lograge/Sentryは一覧を直接読むので効く
- [DB実値はMetabaseで引く](verify-db-values-via-metabase.md) — FF値・件数を「未確認」で済ませない。nuts_feature_flags の key/is_enabled をMetabase MCPで確認
- [本番リリース済みかは実データ＋デプロイ記録の2段で確認](verify-production-release-of-change.md) — 本番デプロイはmasterパイプラインでなくproductionブランチ(cron・30分刻み)。deploy_production:on_pipeline の区間と値の変化時刻を突き合わせる
- [Nuts要件はプロバイダ非依存で書く](nuts-requirements-provider-agnostic.md) — 要件定義.mdはNutsの要件でありSony仕様書でない。固有語(洗替使用区分/1Check/K79/表番号)は実現方法。他社切替で作り直しになる。責務はNuts提供とNuts利用者で分ける
- [force-pushはユーザーが打つ](force-push-user-runs-it.md) — Claudeはforce-push実行しない(feature含む)。clean内容をtempブランチに通常push→force-pushコマンドをユーザーに渡す。target変更等force不要API操作はClaude可
- [worktree検証はブランチコードに対して](worktree-verify-branch-code.md) — 本体repo(master)でrspec/rubocop実行するとブランチ変更を検査できずCIで初めて失敗が出る
- [worktreeのdockerテスト手順](worktree-docker-test-setup.md) — setup-worktree-docker.sh を使う。自前でcompose project名/volumeをいじらない
- [worktreeのブラウザ確認は公開ホストで](worktree-browser-verify-public-host.md) — 80番を取る。APP_HOST_NAMEはwebpackにも渡し3035を公開。Coreはhttps限定。DBはボリュームコピー
- [MRレビューコメントへ勝手に返信しない](no-auto-reply-mr-comments.md) — 指摘対応はコード修正までに留める
- [[ask]は返信で答える](ask-comments-reply-not-fix.md) — [ask]はコード修正でなく回答。マーカーで対応種別を切り分け
- [出力にジャーゴンを使わない](plain-language-no-jargon.md) — 「緑」等の内輪語禁止。誰でも分かる言葉で書く
- [日本語説明文は認知リズム規範を併用](cognitive-rhythm-writing-norm.md) — 話題テスト（状況か文書か）・拍・未回収の緊張。k16shikano の gist。チャット返答には適用しない
- [「正典」は使わない](no-canonical-jargon.md) — 馴染みのない専門ぶった言い換え語。指す事実を平易に書く
- [Nutsの語はユビキタス言語と突き合わせる](nuts-words-must-exist-in-ubiquitous-language.md) — 「口座」「長寿命」は表に無い。無い語は使わず、実装済みで未掲載なら追加を提案（会員・顧客コードが未掲載だった）
- [最小限を口実にテストを削らない](minimalism-not-skip-tests.md) — 境界値・分岐は入れる。決済等は厚く
- [共有部品の変更は影響最小を既定に](shared-component-change-minimize-blast.md) — 模倣元の挙動を共有structにコピーしない。所有構造を先に確認
- [【TODO】16370マージ後にレビュー学び重複を整理](pending-review-learnings-dedup.md) — 16370と16376で学びが二重/矛盾。追加コミットでcode-review-patterns.mdに集約
- [概念整理が済んだらドキュメント化](domain-first-then-document.md) — 設計議論はドメインレベルを先に固め、区切りで md にまとめてから詳細へ
- [レビュー指摘は失敗経路で裏付ける](review-ground-findings-in-behavior.md) — 挙動が問題ない点に意図確認を投げない。具体的な失敗経路がある時だけ指摘
- [packwerk緑でもNuts→Spica依存は隠れる](packwerk-green-hides-spica-dependency.md) — package_todo.ymlの越境記録でpackwerkは通る。レビューでdiff確認。クレカAPIはADR-045でNuts再実装(Payment::SonyPayment直接流用は却下案)
- [Nutsのフローはcontrollerに置く](nuts-orchestration-in-controller-not-lib.md) — リクエスト駆動のオーケストレーションはユースケース層=controller。libにサービスクラスは置かない。SBPSはcontrollerでTX組立
- [レビューコメント下書きの文面ルール](review-comment-drafting-style.md) — 方針のみ・依頼形・「十分です」等の判定語と対象外フローの否定説明を入れない。詳細は末尾の提案メモへ
- [レビュー学び収集の仕組み](extract-review-comment-learnings-skill.md) — 旧名harvest-review-learnings。当初個人運用→MR!16668でチーム共有化(packs/nuts/.ai/skills/)。週次永久loop(session only固定、cloud勧誘は聞かない)、マージ済み+ラベル方式
- [学び収集の重複チェックは深く](extract-review-comment-learnings-dedup-check-depth.md) — 見出しでなく箇条書き内部まで確認。単発の実装トリビアはパターン化しない
- [daily-reviewのloop運用](daily-review-loop-operation.md) — OS cron未登録・セッション内CronCreate(毎朝9:20 JST)で実行。7日失効・セッション終了で消える
- [レビュー依頼MR監視loop](mr-review-watch-loop.md) — 両ラベルMRを平日9-18時JST15分ごと監視しSlack DM通知。6日ごと自己更新cronで永久化(ジョブ072706ef内)
- [memory-retrospectiveの週次運用](memory-retrospective-operation.md) — 毎週月曜9:33 JSTにメモリーを棚卸し、スキル・ルール昇格候補を提案。提案のみ・反映は承認後
- [MR作成後はURLを単独行で出力](mr-url-bare-line.md) — コピー用に素のURL1行。PostToolUse(Bash)フック notify-url.py（旧mr-url.py汎用化）が MR作成(glab/push/ラッパー/create_mr.sh)＋draft_notes下書きを検知。session_id単位で重複除外
- [MR作成は本人名義にする](mr-created-as-spica-token.md) — glab(個人PAT認証)でglab mr create。create_mr.shはspica-token名義になるため作成には使わない
- [glabは-Rでbase repo明示](glab-needs-explicit-repo-flag.md) — 複数リモートで対話プロンプトに固まる。mr create/list/updateに-R comic-festa-group/web-application(+createは--yes)
- [レビューエージェントは発火対象とチェック観点を整合](review-agent-whitelist-checklist-alignment.md) — 対象範囲にチェック観点が見たいファイルが無いと適用前に対象外で見逃す。ディレクトリを主シグナルに・SKILLに対象範囲を重複列挙しない。実差分検証で炙り出す(NUTSKAIZEN-662)
- [Herdr設定が黙って効かない2原因](herdr-config-misplaced-keys-silent.md) — remote接続では[keys]は接続元マシン側／誤配置項目は無警告で破棄。reload-configのappliedは反映の根拠にならない
- [Herdrペインでclaudeエージェントを立てる手順](herdr-pane-claude-agent-workflow.md) — 「paneで」の合図。兄弟ペインを--no-focus分割→pane runでclaude起動→idle待ち→タスク投入→done/idle待ち→recent-unwrapped読み
- [herdr-reviewrの対象リポジトリ](herdr-reviewr-usage.md) — 開いた時のペインcwdで固定。ワークツリーに入った後にopenし直す。herdr updateはherdrの外から
- [設計は可逆性で判断する](reversibility-over-upfront-structure.md) — 後で変えやすい依存は許容、変えにくい点(参照の向き/FK喪失/型名のデータ化)だけ議論。未要件の構造は先回りせずplanに記録
- [手戻り中はチケット案・ADRに引きづられない](tickets-adrs-not-binding-during-rework.md) — チケットは問題説明として読み、設計は要件と現状コードから組み直す。外れた点は理由付きでMR説明へ
- [レビュー依頼ラベルを勝手に付けない](no-auto-review-request-label.md) — MR作成は作成まで。Request Code Review(Nuts)等の付与はユーザーが手動で行う
- [MR返信は明示依頼でも絶対下書き](no-auto-reply-mr-comments.md) — publishしない。reply_review_commentで下書き作成まで。送信・resolveはユーザー
- [MR文面はユビキタス言語を使う](mr-message-use-ubiquitous-language.md) — 平易化で言い換えない。backfill等の英語ジャーゴンのみ平易化、ドメイン用語は正規語
- [MR説明は読み手別に節を分ける](mr-description-split-by-audience.md) — Nuts利用者(Spica)向けとNutsメンバー向け。「継続課金契約」はSpicaに通じないので入会と書く
- [文末の「だ」「である」を足さない](no-redundant-copula-endings.md) — 「〜だからだ。」→「〜だから。」。書いたらgrepで拾う
- [外向き文面に会話文脈を持ち込まない](outward-text-no-conversation-context.md) — 「2ステップ」「案3b」等、相手が知らない相談中の枠組み語を消す。文面単体で意味が通るように
- [draft note PUTはpositionが消える](draft-note-put-drops-position.md) — GitLab下書きをnoteだけ更新すると行紐付けが落ちる。position込みで再PUTし単体GETで確認
- [設計ドキュメントの未決事項は解決時期を書く](nuts-design-doc-open-issues-timing.md) — plan/ADR/計画書の未決・技術的負債に「いつ解決するか(期日/トリガー)＋追跡先」を必須。テンプレとdoc-reviewチェックで担保
- [未決事項は持ち越さずaskで潰す](no-carryover-force-decision.md) — plan の持ち越し表に逃がさない。その場で選択肢を出して判断を迫る
- [着手前に選択肢を比較する](compare-options-before-implementing.md) — 指摘に即着手しない。原典特定→選択肢3つ→推奨提示。前提が崩れたら比較に戻る
- [安全策は前例を数えてから足す](safety-measures-check-repo-precedent.md) — lock_timeoutは446移行中0件だったので外した。usersは635万行でも素のadd_column
- [移行運用の状況説明はテーブル有無だけで語る](migration-state-talk-by-table-existence.md) — DBの種類(comicfesta/animefesta/id)を出さない。spicaは単一DBでAF/CF両方を扱う。rename判断は旧/新テーブルの有無のみ
- [worktreeのフルmigrateはpackのschema.rbを壊す](worktree-full-migrate-corrupts-pack-schema.md) — db:drop/create/migrateでpackテーブルがダンプ欠落。migration検証は隔離up/down、schema.rbは手で最小差分＋git diffで確認
- [自律loopはユーザー判断で止めない](autonomous-loop-no-decision-stops.md) — 定期実行/cronはAskUserQuestion禁止。事前安全ポリシーで自動進行、曖昧は危険側に倒さずスキップ。worktree掃除cronは「MERGED＋変更なしのみ削除」。CronCreateはsession-only(resume復活せず)・クラウドはローカルworktree不可視
- [nutsのバッチ監視は現状維持](nuts-batch-monitoring-stay-as-is.md) — spicaの受動通知に乗せない理由と、乗せるなら未実行・未完了だけ
- [ワークツリー削除はroot所有ファイルで半端に終わる](worktree-removal-root-owned-files.md) — git登録は外れるがファイルは残る。sudo での削除はユーザー実行
- [修正を外す検証はstashでなく直接編集](verify-fix-by-editing-not-stash.md) — 空stash pushの直後のpopは他セッションのstashを取る。復旧はfsck+stash store
