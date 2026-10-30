#!/usr/bin/env bash
# Start the Fabric server with the Discord console forwarder.
# If a copy is already running, wait for it to exit, then start one.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

JAVA="/opt/homebrew/opt/openjdk@25/bin/java"
PYTHON="/opt/homebrew/bin/python3"
JAR="./Fabric Minecraft Server Launcher 26.3 0.19.5.jar"

if [[ ! -x "$JAVA" ]]; then
  echo "java not found at $JAVA" >&2
  exit 1
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "python3 not found at $PYTHON" >&2
  exit 1
fi
if [[ ! -f "$JAR" ]]; then
  echo "missing launcher jar in $ROOT" >&2
  exit 1
fi

server_running() {
  ps -axo command | awk 'index($0, "openjdk@25/bin/java") && index($0, "Fabric Minecraft Server Launcher") { found=1 } END { exit found ? 0 : 1 }'
}

while server_running; do
  sleep 15
done

exec "$PYTHON" "$ROOT/scripts/run_with_discord.py" \
  "$JAVA" \
  -Dapple.awt.UIElement=true \
  -Xms2G \
  -Xmx4G \
  -jar "$ROOT/Fabric Minecraft Server Launcher 26.3 0.19.5.jar" \
  nogui
