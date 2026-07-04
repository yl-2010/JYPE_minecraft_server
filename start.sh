#!/bin/zsh
cd "$(dirname "$0")"
JAVA25="/opt/homebrew/opt/openjdk@25/bin/java"
FORWARDER="./scripts/discord_log_forwarder.py"
SERVER_JAR="./Fabric Minecraft Server Launcher 26.2 0.19.3.jar"

if [[ -x "$FORWARDER" ]]; then
  "$JAVA25" -Dapple.awt.UIElement=true -Xms2G -Xmx4G -jar "$SERVER_JAR" nogui 2>&1 | tee >(python3 "$FORWARDER")
else
  exec "$JAVA25" -Dapple.awt.UIElement=true -Xms2G -Xmx4G -jar "$SERVER_JAR" nogui
fi
