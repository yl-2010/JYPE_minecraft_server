#!/usr/bin/env python3
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEBHOOK_FILE = os.path.join(ROOT_DIR, ".discord-webhook-url")

LOG_RE = re.compile(r"^\[(?P<time>\d{2}:\d{2}:\d{2})\] \[[^\]]+\]: (?P<message>.*)$")

EVENT_PATTERNS = [
    re.compile(r"^Done \([^)]+\)! For help, type \"help\"$"),
    re.compile(r"^Server empty for \d+ seconds, pausing$"),
    re.compile(r"^[A-Za-z0-9_]{3,16} joined the game$"),
    re.compile(r"^[A-Za-z0-9_]{3,16} left the game$"),
    re.compile(r"^[A-Za-z0-9_]{3,16} lost connection: .+$"),
    re.compile(r"^[A-Za-z0-9_]{3,16} has made the advancement \[.+\]$"),
    re.compile(r"^[A-Za-z0-9_]{3,16} has reached the goal \[.+\]$"),
    re.compile(r"^[A-Za-z0-9_]{3,16} has completed the challenge \[.+\]$"),
    re.compile(r"^<[^>]+> .+$"),
]

DEATH_HINTS = (
    " was slain ",
    " was shot ",
    " was blown up",
    " was killed",
    " was fireballed",
    " was impaled",
    " was squashed",
    " was poked ",
    " hit the ground too hard",
    " fell ",
    " drowned",
    " burned ",
    " went up in flames",
    " tried to swim in lava",
    " discovered the floor was lava",
    " suffocated in a wall",
    " starved to death",
    " froze to death",
    " withered away",
    " died",
)


def load_webhook_url():
    env_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if env_url:
        return env_url

    try:
        with open(WEBHOOK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def important_event(message):
    if any(pattern.search(message) for pattern in EVENT_PATTERNS):
        return True

    lower_message = message.lower()
    return any(hint in lower_message for hint in DEATH_HINTS)


def format_message(line):
    match = LOG_RE.match(line)
    if not match:
        return None

    timestamp = match.group("time")
    message = match.group("message")

    if not important_event(message):
        return None

    if message.startswith("Done "):
        return f"[{timestamp}] Minecraft server is ready"

    return f"[{timestamp}] {message}"


def send_to_discord(webhook_url, content):
    payload = json.dumps({"content": content[:2000]}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "minecraft-server-discord-log-forwarder",
        },
        method="POST",
    )

    for _ in range(3):
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                reset_after = response.headers.get("X-RateLimit-Reset-After")
                remaining = response.headers.get("X-RateLimit-Remaining")
                if remaining == "0" and reset_after:
                    time.sleep(float(reset_after))
                return True
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                try:
                    body = json.loads(exc.read().decode("utf-8"))
                    retry_after = body.get("retry_after", retry_after)
                except Exception:
                    pass
                time.sleep(float(retry_after or 1) + 0.1)
                continue
            return False
        except Exception:
            return False

    return False


def main():
    webhook_url = load_webhook_url()
    if not webhook_url:
        for _ in sys.stdin:
            pass
        return 0

    for raw_line in sys.stdin:
        line = raw_line.rstrip("\n")
        message = format_message(line)
        if message:
            send_to_discord(webhook_url, message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
