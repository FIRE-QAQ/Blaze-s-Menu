#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "== 烈火家今天的饭 · 推送到 GitHub =="
git add -A
if git diff --cached --quiet; then
  echo "没有变化，无需推送。"
else
  git commit -m "更新菜单 $(date '+%Y-%m-%d %H:%M')"
fi
git push origin main && echo && echo "完成。一两分钟后刷新：https://fire-qaq.github.io/Blaze-s-Menu/"
echo
read -n 1 -s -r -p "按任意键关闭…"
