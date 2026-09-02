---
name: payment-spec-drive-folder-map
description: 決済一次資料の Drive フォルダ構成。SBPS は「未格納」ではなく実在する
metadata: 
  node_type: memory
  type: reference
  originSessionId: 50b60256-444f-4a96-8edc-70427849caa2
  modified: 2026-08-17T09:46:15.095Z
---

決済プロバイダの一次資料は Drive の決済ルート `1F_SqM6rtaX5SjsXjrWy7FJC0zxQtXRJB` 配下にプロバイダ別フォルダで置かれている。

| プロバイダ | フォルダID |
|---|---|
| SonyPayment | `1eY_Eg6la5wsUq11j8y5yzMJGA8wJYcnN` |
| SBPS（ソフトバンクまとめて支払い（B）） | `1N0zcD60TMhyK-OOkB21VrQRj8hjJNZ3Z` |
| auかんたん決済 | `1DeIMD2BYRp8s9Ov7tgoeToHf0AtXLcei` |
| d払い | `189gMVNm8YQI4snHDvT4cengN81FuFpU8` |
| Atone | `1N6P2I1-VHlnAbZuOt7hiuM2AgVQ9fcoa` |
| Paypay | `1kcrCvnpgcgkSDAWjPB6vE5Y9dqfi7duS` |
| GMO | `1-6eWGfinThCMVdvg-PplKLe9ZiKkPvUM` |

**`ask-payment-provider-spec` スキルのマッピング表は「SBPS は Drive 未格納・対象外」と書いているが、実際には SBPS フォルダがある。** その中の「SBPS補足ドキュメント」から `99.Softbank（B）[SBPS]仕様` フォルダ `15I-C9Ui_PS_74x1cWzfIQZWYPBz7HOkN` に辿れ、C001〜C007 のリンク型システム仕様書と D202 の API 型仕様書が揃っている。スキル表の更新候補。

一次資料に到達できないもの:

- **Atone**: フォルダの中身は Web マニュアル（`manual.atone.be`）の URL とログイン情報の在り処（Pass管理表_Festa_決済関連）だけ。仕様書そのものは未格納
- **Paypay**: フォルダが空

Drive の `search_files` は Drive クエリ構文で渡す。`fullText contains 'atone'` や `parentId = '<id>'` は通り、`name contains` や裸のキーワードは `Unsupported query field` で失敗する。

大きな PDF の `read_file_content` は出力が保存ファイルに落ちるので、python か jq で該当語の周辺だけ抜き出す。

関連: [[escott-sonypayment-primary-source-facts]] [[nuts-tracking-code-not-passed-to-provider]]
