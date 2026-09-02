---
name: natscreaf-cc-review-campaign
description: NATSCREAF-1 クレカMRスタックの順次レビュー計画（順序・引き継ぎ事項）
metadata: 
  node_type: memory
  type: project
  originSessionId: ab689872-50c3-4497-8a14-24683c49cfe2
---

2026-07-10 開始。`Request Code Review(Nuts)` 付きのクレカ(NATSCREAF-1)MRをスタック下から順にレビューする。基盤の [[nuts-vocabulary-translation-at-wire]] / SBPS実装と突き合わせ、指摘は失敗経路で裏付け、[[review-comment-drafting-style]] に従い `post_review_comment` で下書きのみ（送信・resolve・ラベルはしない）。MRごとにworktree。

レビュー順（スタック下→上、Spica切替は最後）:
1. 16723 sonypayment-api（外部API完全再実装／ラベル未付与だが最下段。16683で議論した設計の着地先）
2. 16684 register（3DS戻り・authorize→capture→register同期）
3. 16685 token（会員登録+3DS発行）
4. 16686 submit（遷移先分岐）
5. 16688 registered-card（登録済カード照会）
6. 16690 confirm（3DSスキップ同期登録）
7. 16689 core-submit-urls（→master・独立・小）
8. 16694 spica-switch（AFクレカ入会をNuts経由に切替・FF本番切替＝最高リスク・最後）

16683（基盤・マージ済 fe4e71f443）からの引き継ぎ確認事項:
- errors.rb は「今後使う」判断で残置 → 16723以降で実際に使われるか
- 失敗/timeout正規化・Result異常系（ResponseCd nil / JSON.parse rescue）→ 対応 or 後続据え置きか
- 送信前ログ（16683で実装済）との整合

レビュー方針（ユーザー指示 2026-07-13）: **設計・アーキテクチャに関わるクリティカルな指摘を最優先**する。真実源/Spica↔Nuts境界・整合性、状態遷移・決済整合性(二重/過少課金)、セキュリティ(認証・改ざん・オープンリダイレクト)、マイグレーション整合、責務境界を優先。命名・テスト作法・局所実装nitは軽く扱うか省略し下書きを絞る。手本=free1(過少課金)/Spica→Nuts同期/SecureResultCode(誤成功)。

🔴 標準チェック（毎MR必須）: **Spica `UserSonyPaymentAccount`(及びSpicaモデル)を Nuts lib層以外(controller/model)から直接参照するのは絶対禁止**。grepで機械的に全MR確認。該当: register16684(note33647)/token16685:52(33648)/confirm16690:52(33649)/registered_card16688(33645)/submit16686(33640)。lib内(secure3d_certification generate!)はOK。
**根本原因=kaiin_passがNutsに無いこと**。ソニペAPIは kaiin_id+kaiin_pass 必須→Nutsに無いのでcontrollerがUserSonyPaymentAccountをlib外参照せざるを得ない。是正=**kaiin_passをNutsのmember_registeredイベント(sp_kaiin_idと対)に保存**しNutsデータのみで賄う。kaiin_passは自前生成の会員パスワード(PAN非該当・既存も平文)なので暗号化/PCIの追加懸念なし＝Nuts保存してよい(ユーザー明言)。※以前の「既存保持でよい/Nuts二重保存不要」は誤り。

レビュー中に確定した設計判断:
- **登録済カード"判定"はSpica→Nuts同期の上でNutsデータ(member_registered)で行う**（[must]、submit 16686 note=33640）。現状 submit_controller#card_registered? が既存 user_sony_payment_accounts（Spica側）直参照。SBPSの ActiveSubscriptionAgreementResolver 相当の復元を挟む。理由=整合性・変更容易性・最終形はNutsのみ参照。
- **責務/境界[must]（stack横断）**: card の controller 群が Spica/アプリ側モデル（User, UserSonyPaymentAccount, PointSetting, UserAnimePayment 等）を直接参照し、package_todo.yml で Packwerk違反を抑制している（CLAUDE.md禁止「境界越え直接参照」）。SBPSは Nuts::Core::Repositories::Spica::*（reader/resolver）で隔離。card も repository/resolver 境界へ隔離すべき。registered_card(16688) は指摘対象（当初「指摘しない」は誤り）。kaiin_pass の値自体は既存 UserSonyPaymentAccount 保持でよい(Nuts二重保存不要=ユーザー判断)が、アクセスは repository 経由にする。register/confirm/submit/token も同型。

進捗チェックポイント(2026-07-13):
- 16723 sonypayment-api: マージ済(下書き未送信で消滅。SecureResultCode nil→SUCCESSはmaster未修正→follow-up要否)
- 16736(別MR)マージ済=根本原因是正(member_credential+sp_kaiin_pass)がmaster入り。これでスタックが壊れた
- 16689 core-submit-urls: LGTM(唯一の指摘=success_url/error_urlもHTTPS検証、内部API・利用者責任なので[should]止まり。下書き未作成)
- 未送信下書き: 16684(33638 free1[must]/33639 count_up[should]/33647 境界[must]) / 16685(33648 境界+token署名) / 16688(33645 境界) / 16690(33649 境界)。submit16686は境界[must]送信済(公開)
- **律速=16684(register)**: マージ連鎖の土台。rebase待ち
- **残り(16684/85/86/88/90/16694)は"次以降"=rebase後にまとめてレビュー**。token16685は member_registered! 旧署名で確実に壊れる
- 再開時: 各MRをmaster rebase後、UserSonyPaymentAccount直参照→member_credential乗換を確認。rebaseで下書きは落ちるので再作成前提

campaign完了後はこのメモリを削除する。
