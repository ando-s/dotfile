---
name: external-tech
description: 前の営業日の 9:30 以降の技術動向（AI エージェント、決済基盤、インフラ、普段使うツールの更新、新しく出てきたツール）を集め、業務で使えるか・何をするかをチャットに出す。「技術動向」「/external-tech」と言われたときに使う。
---

# 技術動向

技術情報を調べ、s-ando の業務で使えるか、使えるなら何をするかが一目で分かる形で、チャットに出す。質問せず最後まで進める。

## 営業日と見る期間

- 今日の日付は `TZ=Asia/Tokyo date +%Y-%m-%d` で取る
- 営業日は、土日と日本の祝日・振替休日を除いた日。祝日は `~/.claude/skills/nuts-milestone-plan/scripts/check_holidays.py` の JP_HOLIDAYS で確かめる。一覧に今日の年が無ければ自分の知識で判断する
- 見る期間: 前の営業日の 9:30（日本時間）から今回の実行まで。ユーザーが期間を指定したらそれに従う。期間内に新しいものが無い区分は、無理に古いものを載せない

## s-ando の業務（使えるかの判断に使う）

- 決済基盤 Nuts（web-application の `packs/nuts/`）の開発者。Rails・Packwerk・RSpec。継続課金・都度課金を複数の決済代行（SBPS、SonyPayment の e-SCOTT、auかんたん決済、ドコモ払い）に対応させている
- Ruby と Rails のバージョンは `~/dev/spica/web-application` の `Dockerfile-production` と `Gemfile.lock` で確かめる
- 開発では Claude Code を中心に、Codex・MCP・Herdr を使う
- 普段使うツール（更新を追う対象）: 下の「普段使うツールの更新」の表
- 監視は Sentry・Datadog・Metabase

判断の基準:

- 使える: 今の開発・運用にそのまま当てはめられる（例: 使っている Claude Code の新しい設定、決済の設計で今の課題に効く記事、使っている Rails のバージョンに入る変更）
- 参考: それ以外

## 読むもの

まず次のページを直接読む（検索より優先する）:

- AI エージェント: https://code.claude.com/docs/en/changelog 、https://www.anthropic.com/news 、https://github.com/openai/codex/releases 、https://cursor.com/changelog
- 決済基盤: https://stripe.com/blog/engineering 、https://engineering.mercari.com/blog/
- インフラ: https://aws.amazon.com/new/ 、https://aws.amazon.com/blogs/aws/ 、https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud 、https://rubyonrails.org/blog

## 普段使うツールの更新

次のツールについて、見る期間に出た新しい版を調べる。手元の版は `brew list --versions <名前>`（cask は `brew list --cask --versions <名前>`）、Claude Code は `claude --version`、npm で入れたものは `npm ls -g --depth=0` で取る。最新の版は `brew outdated --greedy` と下のリリースのページで確かめる。

| ツール | リリースのページ |
|---|---|
| Herdr | https://github.com/herdrdev/herdr/releases |
| Herdr UI（herdr-gpui） | https://github.com/penso/herdr-gpui/releases |
| Claude Code | https://code.claude.com/docs/en/changelog |
| Codex | https://github.com/openai/codex/releases |
| CodeRabbit CLI | https://docs.coderabbit.ai/changelog |
| Ghostty | https://ghostty.org/docs/install/release-notes |
| yazi | https://github.com/sxyazi/yazi/releases |
| lazygit | https://github.com/jesseduffield/lazygit/releases |
| glab | https://gitlab.com/gitlab-org/cli/-/releases |
| jira-cli | https://github.com/ankitpokhrel/jira-cli/releases |
| Playwright MCP | https://github.com/microsoft/playwright-mcp/releases |
| Obsidian | https://obsidian.md/changelog/ |
| Todoist | https://todoist.com/help/articles/whats-new |
| Raycast | https://www.raycast.com/changelog |

- 前に載せた版は `~/.slack/state/tool-versions-seen.txt` に「ツール名 版」の形で1行ずつある（無ければ空として扱う）。ここにある版は載せない
- 返答に載せた版をこのファイルに書き足す
- 版ごとに、s-ando の使い方に関わる変更（新しい機能・挙動の変更・設定の変更・壊れる変更）だけを拾う。不具合修正だけの版は、件名を「参考」に1行で載せる
- 手元の版が古く、上げる価値があるときは、やることに `brew upgrade <名前>` のような上げ方を書く。上げる操作は自分でしない

## 新しく出てきたもの

AI エージェントでの開発・ターミナルの道具・Claude Code の周辺（MCP サーバー、スキル、プラグイン）で、見る期間に出たり話題になったりした新しいツールを Web 検索で探す。s-ando の使い方（Herdr でエージェントを並べて動かす、Claude Code のスキルとフック、GitLab の MR レビュー）に当てはまるものだけを載せる。

足りない区分だけ Web 検索で補う。決済基盤は「決済 技術ブログ 冪等性」「継続課金 設計」「payments engineering idempotency」のように企業の技術ブログを狙って検索する。公開日を記事の中で確かめてから載せる。まとめサイトや転載は使わない。

## 書き方

- 一読で「使えるか」「何をするか」が分かることを優先する。記事の詳しい説明は書かず、リンクに任せる
- 事実だけを書き、強調語を使わない。確認できないことは「未確認」と書く
- Markdown で書く。リンクは `[題名](URL)`

## 返答の形

1. 1行目: 「技術動向 YYYY-MM-DD（対象期間）　使えるもの N件」
2. 「使えるもの」: 1件ずつ（最大5件）、次の3行で書く。普段使うツールの更新も含めて選ぶ。無ければ「使えるものなし」の1行だけにする
   - **題名** と参照のリンク1つ
   - どこで使えるか: 業務のどの場面に当たるかを1文で
   - やること: 1〜2個。試す・設定する・読む、など動詞で書く
3. 「参考」: 区分（AIエージェント・決済基盤・インフラ・ツールの更新・新しく出てきたもの）ごとに、1件1行で `[題名](URL)`。区分ごとに最大5件。無ければ書かない
4. 「読めなかったページ」: 接続できなかった URL（無ければ書かない）
