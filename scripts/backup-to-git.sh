#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")/.."

git add -A

if git diff --cached --quiet; then
  echo "Nothing to back up — working tree is clean."
  exit 0
fi

SYNC_TIME=$(TZ=America/Los_Angeles date '+%l:%M:%S %p' | tr '[:upper:]' '[:lower:]' | sed 's/^ *//')
git commit -m "world sync ${SYNC_TIME} Pacific"
git push

echo "Backup pushed to GitHub."
