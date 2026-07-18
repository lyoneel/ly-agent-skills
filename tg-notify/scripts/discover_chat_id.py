#!/usr/bin/env python3
"""Discover Telegram chat ID via getUpdates API.

Usage:
    python3 scripts/discover_chat_id.py [BOT_TOKEN]

Environment:
    TELEGRAM_BOT_TOKEN  Bot token (fallback if not provided as argument)

Output:
    Prints chat ID to stdout, or error message to stderr.
"""

import json
import os
import sys
import urllib.request
import urllib.error


def discover_chat_id(bot_token):
    """Get chat ID from the latest update sent to the bot."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} - {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"ERROR: Network error - {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON response from Telegram", file=sys.stderr)
        return None

    if not data.get("ok"):
        print(f"ERROR: {data.get('description', 'Unknown error')}", file=sys.stderr)
        return None

    updates = data.get("result", [])
    if not updates:
        print("No updates found. Send a message to your bot first, then retry.", file=sys.stderr)
        return None

    latest = updates[-1]
    message = latest.get("message") or latest.get("edited_message")
    if not message:
        print("No message found in latest update.", file=sys.stderr)
        return None

    chat = message.get("chat")
    if not chat:
        print("No chat info in message.", file=sys.stderr)
        return None

    chat_id = chat.get("id")
    print(f"{chat_id}")
    return chat_id


def main():
    bot_token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TELEGRAM_BOT_TOKEN", "")

    if not bot_token:
        print("ERROR: Bot token required. Provide as argument or set TELEGRAM_BOT_TOKEN env var.", file=sys.stderr)
        sys.exit(1)

    chat_id = discover_chat_id(bot_token)
    if chat_id is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
