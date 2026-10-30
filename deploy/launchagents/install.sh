#!/usr/bin/env bash
# Install com.jype.minecraft so the Fabric server starts at login.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LABEL="com.jype.minecraft"
SRC="$REPO/deploy/launchagents/${LABEL}.plist"
DEST="$HOME/Library/LaunchAgents/${LABEL}.plist"

if [[ ! -f "$SRC" ]]; then
  echo "missing plist: $SRC" >&2
  exit 1
fi
if [[ ! -x /opt/homebrew/opt/openjdk@25/bin/java ]]; then
  echo "openjdk@25 not found" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
cp "$SRC" "$DEST"
chmod +x "$REPO/scripts/start-server.sh"

if [[ "$REPO" != "/Users/yanlevin/github/JYPE-minecraft-server" ]]; then
  /usr/bin/sed -i '' "s|/Users/yanlevin/github/JYPE-minecraft-server|${REPO}|g" "$DEST"
fi

uid="$(id -u)"
DOMAIN="gui/${uid}"
SERVICE="${DOMAIN}/${LABEL}"

if launchctl print "$SERVICE" >/dev/null 2>&1; then
  launchctl bootout "$DOMAIN" "$DEST" 2>/dev/null || true
fi
launchctl bootstrap "$DOMAIN" "$DEST"
launchctl enable "$SERVICE" 2>/dev/null || true

echo "installed ${LABEL}"
echo "logs: /tmp/jype-minecraft.log"
