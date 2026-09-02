---
name: card-provider-migration-precedent-doc
description: 決済代行移行（GMO→SonyPayment、AF 2025/5・CF 2025/10）の実績が全部入っているDriveドキュメント
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5f20badf-964d-4298-88dd-9b6d7beeddd5
  modified: 2026-07-29T08:15:28.435Z
---

決済代行の移行を検討・計画するときの一次資料は Google Drive の「2025.1 クレカ決済関連システム状況」（fileId `1Trzt9gu_Dq_Ezv8vGIOxFvo0x-cWchqcM4TzLQ4hwto`、約15万字）。

含まれるもの: 移行PJの要件定義・機能要件・非機能要件（移行性=メンテせず機能停止せず切替）／AF・CFのリリース&データ移行計画（当日の時刻単位手順）／会員データのマージ方法と移行対象抽出条件／懸念事項（リカーリングフラグ・洗替のロス・3DSスキップ・店舗コード分割）／リリース後の定期チェック／振り返り／継続決済バッチ実行計画。

読み方: read_file_content はトークン超過で保存ファイルに落ちるので、`jq -r .fileContent` して `#` 見出し行の行番号を先に出し、python の行スライスで必要節だけ読む。

移行の実像: 解約→再登録ではなく、カード会員データを代行会社間で移送し接続先を日付で切り替える。難所はコード外（審査・料率・洗替仕様・告知）。[[escott-sonypayment-primary-source-facts]] と併せて使う。
