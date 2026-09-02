---
name: escott-sonypayment-primary-source-facts
description: クレカ(Sony Payment/e-SCOTT)の外部API仕様はGoogle Drive一次資料で裏取り。取消/返品/金額変更あり、会員ID共有はAF/CF可
metadata: 
  node_type: memory
  type: reference
  originSessionId: a6d832b3-7c52-4950-a139-9ad72d0646c8
---

クレカ（Sony Payment / 決済代行e-SCOTT Smart）の外部API仕様の一次資料はGoogle Driveにある。Spicaのクライアントコードに無い＝仕様に無い、ではない（コード不在≠仕様不在）。外部APIの有無はこの一次資料で裏取りする。

**一次資料（Google Drive）**
- 接続仕様書: 「e-SCOTT Smart 接続仕様書（クレジットカード決済サービス編）2_5_8版」（Google Doc fileId `1hhIGRmuKbgINNd1EjFTrZc-DKZD5deeZTGJoTPuR-TM`。約12万字で1回で全文返らない）
- 会員ID共有: 「ソニーペイメントにおける複数店舗間の会員ID共有仕様」（fileId `1RZSbM0M4OvRNLvhdqEQOunC_hf2ke0gBRyjZ6BvxP9I`）
- 別冊: EMV3Dセキュア編 / トークン決済編 / ファイル伝送編 / レスポンスコード一覧 等が同フォルダにある

**確認済み事実（一次資料に明記）**
- 取消・返品・金額変更をAPIがサポート: 取引種別「取消」`1Delete`、「利用額変更」`1Change`。締め前=取消、締め後=返品（マイナス売上を自動生成）。いずれも`1Delete`で実行。取引電文は7ヶ月で削除され以降は後続処理不可。
  - 注意: 「オンライン返金APIが無い」はコードだけ見た誤り。Spicaのmerchantコードが呼んでいないだけで、返金UIはNuts側(`app/controllers/admins/nuts/*_refunds_controller.rb`)にある。
- 会員ID共有: 複数店舗（テナント）間で同一会員IDを共有しカード決済可能。SPSV公式回答でAnimeFesta/ComicFesta間の共有も確認済み。条件は「カード情報保持=事業者単位契約」（マーチャントIDがユニークキー）。→ [[nuts-af-jira-projects-by-provider]] のクレカ(sony_payment)前提。

**トークン化済みカードの性質（別冊：トークン決済サービス編 1_4_3版、第2章「トークン」。fileId `1MeJm7P5yfKJ1GovRAFGKLJsnidnxaA5m`）**
- 「発行されたトークンは発行から一定時間経過(30 分)、または 1 度使用されると利用できなくなります」。使用済みは`KI2`、期限切れは`KI3`。
- **消費に数えない使用**: `1TokenSearch`(トークンステータス参照) / `4MemRefToken`(トークン会員参照) / `3Secure`(3Dセキュア認証)。つまりNutsの 3DS 経由フローでは 3DS 通過ではトークンが死なず、会員新規(`4MemAdd`)で消費される。
- 発行単位は事業者単位または店舗単位。同一事業者内なら他店舗発行のトークンも利用可。
- トークン取引データは1ヶ月で削除。
- ログに平文で残ったトークンの再利用可能性を論じるときの根拠はここ。

**セキュリティ/コンプラの前提（設計ドキュメント fileId `1Trzt9gu_Dq_Ezv8vGIOxFvo0x-cWchqcM4TzLQ4hwto` で確認）**
- クレカの採用方針は「非通過型」＝カード番号を自社サーバーに通さず保持しない。ブラウザ→Sony直接送信＋トークン化（カスタマイズ型トークン決済）。カードはSony側「カード情報保持機能」で保持。
- **PCI DSSは準拠しない立て付け**: 契約シートに「非保持ゆえ準拠予定なし」。要件は「PCI DSS準拠」ではなく「非保持/非通過」。取り違え注意。
- 3DSは新規カード登録時のみ（都度課金/再入会はスキップ）。
- 割賦販売法・クレジットカード・セキュリティガイドライン・実行計画は読んだ全資料で0件（法令根拠は一次資料外＝一般論扱い）。責任分界（保護を誰が負うか）も全資料に記述なし＝要件化するなら未決事項。

**未確認**: 取消の一部/全額可否、継続課金固有の取消差分、店舗間の3Dセキュア要否は読んだ範囲で明示なし。
