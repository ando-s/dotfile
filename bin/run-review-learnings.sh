#!/bin/bash -l
# extract-review-comment-learnings を人手なしで実行する。comicdev の cron から呼ぶ。
set -u
# cron の PATH には glab（/usr/local/bin）と claude（~/.local/bin）が入らない
export PATH=/usr/local/bin:$HOME/.local/bin:$PATH
cd /home/ec2-user/web-application || exit 1
log_dir=/home/ec2-user/review-learnings-logs
mkdir -p "$log_dir"
log=$log_dir/$(date +%Y%m%d-%H%M%S).jsonl
# スキルは本体リポジトリの手元の master から読まれるため、実行前に origin の master へ進める
if [ "$(git branch --show-current)" = master ]; then
  git pull -q --ff-only origin master || echo "$(date '+%F %T') master を更新できず、手元のスキルで実行" >> "$log_dir/runs.log"
else
  echo "$(date '+%F %T') 本体リポジトリが master でないため、手元のスキルで実行" >> "$log_dir/runs.log"
fi
claude -p "/extract-review-comment-learnings
これは cron による週次の定期実行で、対応する人はいない。質問や確認を求めず、スキルの手順どおり最後まで進めること。学びが無い週も判断記録のMRを作り、走査したMRに収集済みラベルを付ける。" \
  --allowedTools "Bash(glab mr create:*)" \
  --output-format stream-json --verbose > "$log" 2>&1
echo "$(date '+%F %T') exit=$? log=$log" >> "$log_dir/runs.log"
/home/ec2-user/bin/sync-review-learnings-mrs.py >> "$log_dir/runs.log" 2>&1
