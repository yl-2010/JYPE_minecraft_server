#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")/.."

git add -A

if git diff --cached --quiet; then
  echo "Nothing to back up — working tree is clean."
  exit 0
fi

git commit -m "Backup $(date '+%Y-%m-%d %H:%M')"
git push

echo "Backup pushed to GitHub."
