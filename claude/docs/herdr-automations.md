# Herdr の定期実行（ローカルの Mac）

ローカルの Mac の Herdr で動かしている定期実行の置き場所と、変えるときの手順。Mac がスリープしている間は動かない。

## 一覧

| 名前 | 時刻 | 中身 |
|---|---|---|
| today-plan | 平日 8:00 | スキル today-plan で、今日やることを Slack の自分宛て DM に送る |
| external-info（external-security） | 平日 9:30 | セキュリティの情報を集めて DM に送る |
| external-info（external-tech） | 平日 9:30 | 技術動向、普段使うツールの更新、新しく出てきたツールを集めて DM に送る |

- スクリプト: `~/.config/herdr-automate/automations/*.luau`
- 依頼文: `~/.config/herdr-automate/prompts/external-security.md`・`external-tech.md`。営業日の判定と送信は依頼文の中で行う。営業日は check_holidays.py の JP_HOLIDAYS で判定する
- 送信: `~/.slack/send-thread.sh <ディレクトリ>` で、親の投稿とスレッドの返信を送る
- 記録: `~/.slack/logs/external-*.log`
- セキュリティの依存の照合: `~/.slack/dep-audit.sh`（bundler-audit と yarn audit で lock を照合し、前回からの新しい件だけを出す）。見た件は `~/.slack/state/dep-audit-seen.txt`
- ツールの更新で送った版: `~/.slack/state/tool-versions-seen.txt`

クラウドの定期実行（claude.ai のルーティン）は、環境が Trusted でセキュリティ系のサイトの多くに繋がらないため使わない。

## 変えるとき

- 依頼文（prompts）を変えたときは、再承認は要らない
- luau を変えたら再承認が要る。ユーザーが Claude の動いていないペインで次を打つ。PATH に無いのでフルパスで書き、引数には名前でなくファイルを渡す

```
/Applications/Herdr.app/Contents/MacOS/herdr-automate approve ~/.config/herdr-automate/automations/external-info.luau
```

- 承認の前に、`herdr-automate check <ファイル>` で計画を確かめる
- 手で動かす: `herdr-automate run-now <ファイル> --trigger external-tech`
- 状態と次の実行: `herdr-automate status`
