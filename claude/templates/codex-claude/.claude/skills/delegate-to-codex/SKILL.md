---
name: delegate-to-codex
description: <project> で、アプリの実装・テスト・デプロイが必要な作業を、Herdr の別ペインで動く Codex（<project>-codex）に依頼し、終わるまで取りこぼさず見届ける手順。「Codex に頼んで」「実装して」「直して」「デプロイして」など、Claude Code の担当外（app/、tests/、デプロイ）の作業が出てきたら、スキル名を言われなくても使う。
---

# Codex への依頼

Claude Code はハーネスの整備を担当し、実装は Codex が担当する（`AGENTS.md` の「役割分担」）。依頼したまま Claude Code が終わり、Codex の完了に誰も気づかない状態を防ぐため、依頼と見届けを1組で行う。

## 手順

1. **相手を確かめる:** `herdr agent get <project>-codex` で状態を見る。見つからなければ `herdr agent list` で cwd がこのリポジトリの Codex を探し、`herdr agent rename <ペインID> <project>-codex` で名前を付ける。自分にも `<project>-claude` が付いているか確かめる。
2. **依頼を書く:** 作業の中身は `docs/progress.md` と `docs/decisions/` に先に書いておき、依頼文はそれを指す短い文にする。依頼文には必ず次を含める。
   - `AGENTS.md と docs/progress.md を読んでから作業して。`
   - 対象（progress のどの行か、どの決定記録に沿うか）
   - `終わったら、または判断が必要で止まるときは herdr agent prompt <project>-claude で知らせて。`
3. **送る:** 相手が idle か done のときに `herdr agent prompt <project>-codex "<依頼文>"` で送る。working のときは今の作業の終わりを待つ。blocked のときは送らず本人に伝える。
4. **見届けを仕掛ける:** 送った直後に、Bash の `run_in_background` で次を走らせる。

   ```sh
   scripts/watch_agent.sh <project>-codex 15 180
   ```

   状態が working のまま接続切れで進まないことがあり、`herdr agent wait` だけでは気づけない（タイムアウトも効かないことがある）。このスクリプトは状態に加えて画面の変化を見て、終了・停止・接続切れ・15分画面が変わらない・180分経過のいずれかで終わる。
5. **起こされたら:** 状態で分ける。

   | 状態 | すること |
   |---|---|
   | idle / done | `herdr agent read <project>-codex --source recent-unwrapped --lines 120` と `docs/progress.md` で結果を確かめ、`python3 scripts/check_docs.py` を実行し、本人に報告する |
   | blocked | 承認や質問に代わりに答えない。画面の内容を本人に伝える |
   | disconnected / stalled | `herdr agent read <project>-codex --source visible` で画面を確かめる。接続切れなら `herdr agent send-keys <project>-codex esc` で止め、progress.md のどこから再開するかを書いて依頼し直し、見届けを仕掛け直す |
   | timeout | 画面が動いていれば見届けを仕掛け直す。動いていなければ stalled と同じ |
   | missing | `herdr agent list` で探し直す。見つからなければ本人に伝える |

## 注意

- Codex から `<project>-claude` に届いた知らせに、返事のためだけの prompt を返さない。
- 依頼したことを本人に伝えるときは、見届けを仕掛けたことも伝える。
