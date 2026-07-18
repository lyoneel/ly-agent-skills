#!/usr/bin/env python3
"""Send a message to Telegram via Bot API.

Usage:
    python3 scripts/send_message.py --message "text" [options]

Environment:
    TELEGRAM_BOT_TOKEN  Bot token (required, or use --token)
    TELEGRAM_CHAT_ID    Target chat ID (required, or use --chat-id)

Options:
    --message TEXT      Message text (required, 1-4096 chars)
    --token TOKEN       Bot token (overrides env var)
    --chat-id ID        Chat ID (required, overrides env var)
    --parse-mode MODE   Formatting: MarkdownV2, HTML, or empty (default: plain text)
    --no-retry          Disable auto-retry on 429 rate limit
"""

# Bot token must always come from env var or --token

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error


def send_message(bot_token, chat_id, text, parse_mode="MarkdownV2", retry=True):
    """Send a message and return (success, error_message, message_id)."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    for attempt in range(2 if retry else 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            body = json.loads(e.read().decode())
            error_code = body.get("error_code", 0)
            description = body.get("description", str(e.reason))

            if error_code == 429 and retry and attempt == 0:
                retry_after = body.get("parameters", {}).get("retry_after", 5)
                print(f"Rate limited. Retrying after {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            return False, f"HTTP {error_code}: {description}", None
        except urllib.error.URLError as e:
            return False, f"Network error: {e.reason}", None

        if result.get("ok"):
            msg_id = result.get("result", {}).get("message_id")
            return True, None, msg_id

    return False, "Max retries exceeded", None


def main():
    parser = argparse.ArgumentParser(description="Send Telegram message via Bot API")
    parser.add_argument("--message", "-m", required=True, help="Message text (1-4096 chars)")
    parser.add_argument("--token", help="Bot token (override TELEGRAM_BOT_TOKEN)")
    parser.add_argument("--chat-id", help="Chat ID (override TELEGRAM_CHAT_ID)")
    parser.add_argument("--parse-mode", default="", help="MarkdownV2, HTML, or empty (default: plain text)")
    parser.add_argument("--no-retry", action="store_true", help="Disable auto-retry on 429")
    args = parser.parse_args()

    bot_token = args.token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")

    if not bot_token:
        print("ERROR: Bot token required. Use --token or set TELEGRAM_BOT_TOKEN env var.", file=sys.stderr)
        sys.exit(1)
    if not chat_id:
        print("ERROR: Chat ID required. Use --chat-id or set TELEGRAM_CHAT_ID env var.", file=sys.stderr)
        sys.exit(1)
    if len(args.message) > 4096:
        print(f"ERROR: Message too long ({len(args.message)} chars, max 4096)", file=sys.stderr)
        sys.exit(1)

    success, error, msg_id = send_message(
        bot_token,
        chat_id,
        args.message,
        args.parse_mode,
        retry=not args.no_retry,
    )

    if success:
        print(f"Sent (message_id: {msg_id})")
    else:
        print(f"Failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
