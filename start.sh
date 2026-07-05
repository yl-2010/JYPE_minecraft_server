#!/bin/zsh
cd "$(dirname "$0")"
JAVA25="/opt/homebrew/opt/openjdk@25/bin/java"
RUNNER="./scripts/run_with_discord.py"
SERVER_JAR="./Fabric Minecraft Server Launcher 26.2 0.19.3.jar"

if [[ -f "$RUNNER" ]]; then
  exec python3 "$RUNNER" "$JAVA25" -Dapple.awt.UIElement=true -Xms2G -Xmx4G -jar "$SERVER_JAR" nogui
else
  exec "$JAVA25" -Dapple.awt.UIElement=true -Xms2G -Xmx4G -jar "$SERVER_JAR" nogui
fi
