# Herdr の定期実行（ローカルの Mac）

ローカルの Mac の Herdr に登録している定期実行の置き場所と、変えるときの手順。Mac がスリープしている間は動かない。

## 一覧

今は動いている定期実行は無い。下の2つは無効にしてあり、同じ中身はスキルとして手で呼ぶ。Slack に送るボットのアプリが使えなくなり（応答は `account_inactive`）、結果を届ける先が無いため。

| 名前 | 状態 | 代わりに呼ぶスキル |
|---|---|---|
| today-plan（平日 8:00） | 無効 | `/today-plan` |
| external-info（平日 9:30） | 無効 | `/external-security`・`/external-tech` |

- スクリプト: `~/.config/herdr-automate/automations/*.luau`
- スキル: `~/.claude/skills/today-plan/`、`claude/skills/external-security/`・`claude/skills/external-tech/`
- セキュリティの依存の照合: `~/.slack/dep-audit.sh`（bundler-audit と yarn audit で lock を照合し、前回からの新しい件だけを出す）。見た件は `~/.slack/state/dep-audit-seen.txt`
- ツールの更新で載せた版: `~/.slack/state/tool-versions-seen.txt`

クラウドの定期実行（claude.ai のルーティン）は、環境が Trusted でセキュリティ系のサイトの多くに繋がらないため使わない。

## 変えるとき

- luau を変えたら再承認が要る。ユーザーが Claude の動いていないペインで次を打つ。PATH に無いのでフルパスで書き、引数には名前でなくファイルを渡す

```
/Applications/Herdr.app/Contents/MacOS/herdr-automate approve ~/.config/herdr-automate/automations/external-info.luau
```

- 承認の前に、`herdr-automate check <ファイル>` で計画を確かめる
- 有効・無効: `herdr-automate enable|disable <ファイル>`
- 手で動かす: `herdr-automate run-now <ファイル> --trigger external-tech`
- 状態と次の実行: `herdr-automate status`
