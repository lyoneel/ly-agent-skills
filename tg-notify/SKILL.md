---
name: tg-notify
description: Send messages to Telegram chats via Bot API. Use when sending notifications, alerts, or messages from Crush to Telegram.
recommended: true
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash"]
kaizen:
  sources:
    telegram-api: https://core.telegram.org/bots/api#sendmessage
  targets:
    telegram-api: Monitor for API changes and new endpoints
---

Initialize todos for tg-notify operation:

```json
{
  "todos": [
    {"content": "Initialize tg-notify operation", "status": "in_progress", "active_form": "Initializing tg-notify operation"},
    {"content": "Verify configuration (bot token and chat ID)", "status": "pending", "active_form": "Verifying configuration"},
    {"content": "Send message via scripts/send_message.py", "status": "pending", "active_form": "Sending message via send_message.py"},
    {"content": "Handle response and errors", "status": "pending", "active_form": "Handling response and errors"},
    {"content": "Complete tg-notify operation", "status": "pending", "active_form": "Completing tg-notify operation"}
  ]
}
```

# Telegram Notify

Send messages to Telegram via the Bot API using Python scripts. Supports MarkdownV2 and HTML formatting, auto-retry on rate limits, and chat ID discovery.

## Prerequisites

- Telegram bot created via @BotFather (bot token required)
- Bot added to target chat (private, group, or channel)
- `python3` available in PATH (stdlib only, no pip dependencies)

## Configuration Resolution

The scripts resolve configuration via a priority chain. Config files are NOT used.

### scripts/send_message.py

Resolves bot token and chat ID in this order:

1. `--token` CLI flag (bot token override)
2. `TELEGRAM_BOT_TOKEN` env var
3. `--chat-id` CLI flag (chat ID override)
4. `TELEGRAM_CHAT_ID` env var

### scripts/discover_chat_id.py

Resolves bot token in this order:

1. Positional CLI argument
2. `TELEGRAM_BOT_TOKEN` env var

## Chat ID Discovery

If you do not know your chat ID:

1. Send any message to your bot on Telegram (e.g., `/start` or "test")
2. Wait 5 seconds for Telegram to process the update
3. Run the discovery script:
   ```bash
   python3 scripts/discover_chat_id.py "$TELEGRAM_BOT_TOKEN"
   ```
4. The output is your numeric chat ID
5. Save it to `TELEGRAM_CHAT_ID` env var

For group/channel chats, the chat ID will be a negative number (e.g., `-1001234567890`).

## Execution Steps

BEGIN EXECUTION IMMEDIATELY. Do not ask the user what they want to do. Start with step 1:

### Step 1: Verify Configuration

1. Check `TELEGRAM_BOT_TOKEN` is set in environment. If not, ask user to provide it.
2. Check `TELEGRAM_CHAT_ID` is set in environment. If not, provide it via `--chat-id` flag.

Update todos: mark configuration verification as completed, mark send message as in_progress.

### Step 2: Send Message

Run the script via bash:

```bash
python3 scripts/send_message.py \
  --message "$MESSAGE_TEXT" \
  --parse-mode "$PARSE_MODE"
```

Script options:

| Flag | Description | Required |
|------|-------------|----------|
| `--message` / `-m` | Message text (1-4096 chars) | Yes |
| `--token` | Bot token (overrides env var) | No |
| `--chat-id` | Chat ID (required if `TELEGRAM_CHAT_ID` not set) | No |
| `--parse-mode` | `MarkdownV2`, `HTML`, or empty (default: plain text) | No |
| `--no-retry` | Disable auto-retry on 429 | No |

Exit codes:
- `0` -- message sent successfully (prints `Sent (message_id: <id>)`)
- `1` -- failed (prints error to stderr)

Update todos: mark send message as completed, mark handle response as in_progress.

### Step 3: Handle Response

The script handles errors internally:

- On success: prints `Sent (message_id: <id>)` to stdout
- On 429 rate limit: waits `retry_after` seconds, retries once automatically
- On other errors: prints `Failed: <reason>` to stderr, exits with code 1

Error codes the script may report:

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check chat_id format, message length, or escape errors |
| 401 | Unauthorized | Verify bot token is valid and not revoked |
| 403 | Forbidden | Add bot to chat, check admin permissions for channels |
| 404 | Not Found | Chat does not exist or bot was removed |
| 429 | Too Many Requests | Script auto-retries once; if it fails again, wait and retry manually |

Update todos: mark handle response as completed, mark complete operation as in_progress.

### Step 4: Complete

Confirm delivery status. If retry was needed, report the final outcome. Clear todos.

## Message Formatting

### MarkdownV2

Use `--parse-mode MarkdownV2` for full formatting support:

- Bold: `*bold*`
- Italic: `_italic_`
- Underline: `__underline__`
- Strikethrough: `~strikethrough~`
- Inline code: `` `code` ``
- Link: `[text](URL)`
- Blockquote: `> text`

Escape special characters with backslash: `_*[]()~\>#:+-=|{}.!`

### HTML

Use `--parse-mode HTML` for HTML formatting:

- Bold: `<b>text</b>`
- Italic: `<i>text</i>`
- Code: `<code>text</code>`
- Link: `<a href="URL">text</a>`

Escape `<`, `>`, `&` as `&lt;`, `&gt;`, `&amp;`.

## Rate Limits

- Default: 30 messages per second
- On 429 error: script reads `retry_after` and waits before retrying
- Maximum one automatic retry per message

## Usage Examples

### Basic plain text message

```bash
python3 scripts/send_message.py --message "Deployment complete"
```

### Formatted message with MarkdownV2

```bash
python3 scripts/send_message.py \
  --parse-mode MarkdownV2 \
  --message "*Build Success*\n\n_Pipeline_: CI/CD\n_Branch_: main\n_Commits_: 3\n_Status_: \`passed\`"
```

### Override token and chat ID via flags

```bash
python3 scripts/send_message.py \
  --token "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" \
  --chat-id "987654321" \
  --message "Override test"
```
