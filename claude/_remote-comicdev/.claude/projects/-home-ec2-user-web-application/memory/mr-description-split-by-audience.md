---
name: mr-description-split-by-audience
description: NutsとSpicaの両方がレビューするMRは、説明をNuts利用者(Spica)メンバー向けとNutsメンバー向けに分けて書く
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5199b579-bf95-4738-8875-c639b0d56872
  modified: 2026-08-10T05:08:04.133Z
---

Spica のコードに触る Nuts のチケットで、Spica の開発者にもレビューを頼む MR は、説明を読み手別の2節に分ける。見出しは「👀 Nuts利用者（Spica）メンバー向け」と「Nuts メンバー向け」。

Nuts利用者向けの節では Nuts の正規語を使わない。「継続課金契約」は Nuts の語で Spica の開発者には通じないので、Spica の呼び方（入会・解約）で書く。節の冒頭に一行だけ橋渡しを置く（「Nuts は入会1件を『継続課金契約』と呼ぶ。ここでは Spica の呼び方で書く」）。Nutsメンバー向けの節では正規語をそのまま使う。

**Why:** 同じ事実でも、責務の話（Nuts側の関心）と、既存挙動への影響・ロック・後続で自分のコードのどこが変わるか（Spica側の関心）で、必要な情報が違う。1つの文面に混ぜると、どちらの読み手も自分に関係ない話を読まされる。語彙を混ぜると Spica 側は用語で詰まる。

**How to apply:** Nuts利用者向けには「挙動が変わらないこと」「列名の紛れ」「後続MRで自分のコードのどこに手が入るか（ファイル名付き）」を書く。Nutsメンバー向けには責務・置き場所・正規語での説明を書く。関連: [[mr-message-use-ubiquitous-language]]（ドメイン用語は正規語）、[[nuts-words-must-exist-in-ubiquitous-language]]
