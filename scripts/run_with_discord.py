#!/usr/bin/env python3
"""Run the Minecraft server with console I/O forwarded to Discord."""

import os
import pty
import select
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from discord_log_forwarder import (  # noqa: E402
    format_console_command,
    format_message,
    load_webhook_url,
    send_to_discord,
)


def relay_output(master_fd, webhook_url, out_buffer):
    try:
        data = os.read(master_fd, 4096)
    except OSError:
        return False, out_buffer

    if not data:
        return False, out_buffer

    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

    out_buffer += data.decode("utf-8", errors="replace")
    while "\n" in out_buffer:
        line, out_buffer = out_buffer.split("\n", 1)
        message = format_message(line)
        if message and webhook_url:
            send_to_discord(webhook_url, message)

    return True, out_buffer


def relay_input(master_fd, webhook_url, in_buffer):
    try:
        data = os.read(sys.stdin.fileno(), 4096)
    except OSError:
        return False, in_buffer, False

    if not data:
        return False, in_buffer, True

    os.write(master_fd, data)

    in_buffer += data.decode("utf-8", errors="replace")
    while "\n" in in_buffer:
        line, in_buffer = in_buffer.split("\n", 1)
        message = format_console_command(line)
        if message and webhook_url:
            send_to_discord(webhook_url, message)

    return True, in_buffer, False


def drain_output(master_fd, webhook_url, out_buffer):
    while True:
        ok, out_buffer = relay_output(master_fd, webhook_url, out_buffer)
        if not ok:
            return out_buffer


def main():
    if len(sys.argv) < 2:
        print("Usage: run_with_discord.py <command...>", file=sys.stderr)
        return 1

    cmd = sys.argv[1:]
    webhook_url = load_webhook_url()

    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        cmd,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
    )
    os.close(slave_fd)

    out_buffer = ""
    in_buffer = ""
    stdin_closed = False

    try:
        while True:
            fds = [master_fd]
            if not stdin_closed:
                fds.append(sys.stdin.fileno())

            readable, _, _ = select.select(fds, [], [])

            if master_fd in readable:
                ok, out_buffer = relay_output(master_fd, webhook_url, out_buffer)
                if not ok and proc.poll() is not None:
                    drain_output(master_fd, webhook_url, out_buffer)
                    break

            if sys.stdin.fileno() in readable:
                ok, in_buffer, eof = relay_input(master_fd, webhook_url, in_buffer)
                if eof or not ok:
                    stdin_closed = True

            if proc.poll() is not None and master_fd not in readable:
                drain_output(master_fd, webhook_url, out_buffer)
                break
    finally:
        os.close(master_fd)

    return proc.wait()


if __name__ == "__main__":
    raise SystemExit(main())
