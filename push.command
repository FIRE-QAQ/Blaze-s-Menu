#!/bin/bash
cd "$(dirname "$0")" || exit 1
echo "=========================================="
echo "  烈火家今天的饭 · 推送到 GitHub"
echo "=========================================="
echo

git add -A
if git diff --cached --quiet; then
  echo "· 没有新的文件改动"
else
  git commit -m "更新菜单 $(date '+%Y-%m-%d %H:%M')" >/dev/null
  echo "· 已提交新改动"
fi

N=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
echo "· 待推送提交：$N 个"
echo

push_try () {
  echo "--- 尝试推送（$1）---"
  git -c http.postBuffer=524288000 -c http.version="$2" push origin main
}

if push_try "HTTP/1.1" HTTP/1.1; then
  OK=1
else
  echo
  echo "!! 第一次失败，换 HTTP/2 再试一次…"
  echo
  push_try "HTTP/2" HTTP/2 && OK=1
fi

echo
if [ "$OK" = 1 ]; then
  echo "=========================================="
  echo "  推送成功"
  echo "  1-2 分钟后打开："
  echo "  https://fire-qaq.github.io/Blaze-s-Menu/"
  echo "=========================================="
else
  echo "=========================================="
  echo "  推送失败 — 把上面的报错整段发给 Claude"
  echo "=========================================="
fi
echo
read -n 1 -s -r -p "按任意键关闭…"
