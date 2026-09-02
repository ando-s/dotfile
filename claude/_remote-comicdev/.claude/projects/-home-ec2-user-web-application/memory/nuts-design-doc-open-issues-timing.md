---
name: nuts-design-doc-open-issues-timing
description: Nuts設計ドキュメントの未決事項・技術的負債には「いつ解決するか」を必ず書く
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8f787f5e-6efa-4973-96ed-c4536d33b9e6
---

Nutsの設計ドキュメント（plan、ADR、PM計画書、設計メモ等）を書く・推敲するとき、未決事項・未解決・将来の意思決定・技術的負債の解消が必要な項目には、**いつ解決するか**（期日、または「本番切替後」「〜のMRマージ後」等のトリガー条件）と**追跡先**（JIRAチケット。未起票なら「起票予定」＋決定者）を必ずセットで書く。空欄や「後で」「別途検討」だけの先送りは不可。未決事項がなければ「なし」と明記。

**Why:** 解決時期のない未決事項は放置され、将来の変更者がいつ・誰が決めるか分からないまま実装が進む。

**How to apply:** planは `packs/nuts/plan/_template.md` の「未決事項・持ち越し」テーブルで担保（種別／いつ解決／追跡先の3列）。doc-reviewは `packs/nuts/.ai/references/checklists/doc-review/persuasiveness.md` の行動可能性チェックで検出。テンプレ外のドキュメント（ADR等）でも同じ3点を自分の判断で書く。編集はSSOTの `packs/nuts/.ai/` 側で行い `sync-context.py` を実行（`.claude/` はgit管理外の生成物）。
