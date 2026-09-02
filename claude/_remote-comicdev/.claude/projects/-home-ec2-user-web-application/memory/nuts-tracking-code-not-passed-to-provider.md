---
name: nuts-tracking-code-not-passed-to-provider
description: 契約追跡コードは各プロバイダの識別子に流せない。交わりは20桁半角英数字
metadata: 
  node_type: memory
  type: project
  originSessionId: 50b60256-444f-4a96-8edc-70427849caa2
  modified: 2026-08-17T09:46:57.908Z
---

継続課金契約追跡コードの形式を決めるとき、「全決済手段で通用する共通形式」を目標にしてはいけない。加盟店が発行する識別子の制約を一次資料で突き合わせると、**交わりが 20 桁の半角英数字**になる（auかんたん決済の加盟店管理番号 0〜20桁半角英数字、ドコモの加盟店注文番号 20桁半角英数）。記号が使えず桁数も足りないため、追跡コードをそのまま送る設計は成立しない。

**Why:** ADR-020 は「決済システムごとの追跡コードには Nuts で変換する」と決めており、クレカとauかんたん決済はその通り Nuts が独立採番している。SBPS だけが追跡コードをそのまま購入ID として送っていて、そこが例外。SBPS の素通しが「追跡コードは31文字以内」という制約を生んでいる（購入ID上限38桁 − 継続課金決済の接尾辞7文字）。

**How to apply:** 追跡コードは Nuts利用者と Nuts の間の識別子として設計する。プロバイダへ送る識別子は決済手段ごとに Nuts が独立採番する。SBPS の素通しを直すのは稼働中契約の購入ID に触るため、解約の Nuts 切り替え（NATSCREAF-50）の後。より短い桁数の決済代行を追加するときはそれより先に判断する。

決定は ADR-055（MR !17148）。採番は `sub_` + ULID の 30 文字にした。ULID を選んだのは 26 文字が SBPS の 31 文字制約に収まる唯一の候補だったため。UUID版7 は 36 文字で入らない。

atone と PayPay は一次資料に到達できず上限が未確認。実績は atone 26 文字・PayPay 36 文字で、どちらも 20 桁より緩いので交わりを狭めない。

関連: [[payment-spec-drive-folder-map]] [[nuts-vocabulary-translation-at-wire]] [[nuts-requirements-provider-agnostic]]
