# tg-notify

**tg-notify** is a Crush agent skill that sends messages to Telegram chats via the Bot API. Built with Python stdlib only — no pip packages, no virtual environments, no config files. Supports MarkdownV2 and HTML formatting, auto-retry on rate limits, and chat ID discovery.


### Features

- **Two formatting modes**: MarkdownV2 (full formatting) and HTML
- **Auto-retry on rate limits**: handles Telegram 429 responses with one automatic retry
- **Chat ID discovery**: find your chat ID without manual API calls
- **Flexible configuration**: resolve credentials via CLI flags or environment variables
- **Zero dependencies**: Python stdlib only — no pip, no venv, no config files
- **Portable**: runs on any system with Python 3

### Quick Start

1. Create a bot via [@BotFather](https://t.me/BotFather) and note the token
2. Add the bot to your target chat (private, group, or channel)
3. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="<your-bot-token>"
   export TELEGRAM_CHAT_ID="<your-chat-id>"
   ```
4. Send a message:
   ```bash
   python3 scripts/send_message.py --message "Hello from tg-notify"
   ```

### Requirements

- **Python 3** (stdlib only — no external packages required)
- A Telegram bot token from @BotFather
- A target chat ID (private, group, or channel)

### Prerequisites for Seamless Use

Set the following environment variables once to avoid passing `--token` and `--chat-id` on every invocation. Add them to your shell profile (e.g., `~/.bashrc`, `~/.zshrc`) or your session configuration:

```bash
export TELEGRAM_BOT_TOKEN="<your-bot-token>"
export TELEGRAM_CHAT_ID="<your-chat-id>"
```

With these set, the scripts resolve credentials automatically. CLI flags (`--token`, `--chat-id`) override the environment variables when provided.

To find your chat ID, see [Chat ID Discovery](#discover-chat-id).

## Architecture

```
tg-notify/
├── SKILL.md              # Crush skill definition and execution workflow
├── README.md             # This file
├── .gitignore
└── scripts/
    ├── send_message.py   # Main message sender with retry logic
    └── discover_chat_id.py  # Chat ID discovery helper
```

### Scripts

#### send_message.py

Primary message sender. Resolves configuration via a priority chain:

1. `--token` CLI flag (bot token override)
2. `TELEGRAM_BOT_TOKEN` environment variable
3. `--chat-id` CLI flag (chat ID override)
4. `TELEGRAM_CHAT_ID` environment variable

Supports MarkdownV2 and HTML parse modes, auto-retry on 429 rate limits, and validates message length (max 4096 characters).

#### discover_chat_id.py

Finds the chat ID by polling the `getUpdates` API. Useful when you do not know your chat ID:

1. Send any message to your bot on Telegram (e.g. `/start`)
2. Wait 5 seconds for Telegram to process the update
3. Run the discovery script (token from positional argument or `TELEGRAM_BOT_TOKEN` env var):
4. The output is your numeric chat ID

For group and channel chats, the chat ID is a negative number (e.g. `-1001234567890`).

## Usage

### Basic message

```bash
python3 scripts/send_message.py --message "Build completed successfully"
```

### Formatted message (MarkdownV2)

```bash
python3 scripts/send_message.py \
  --parse-mode MarkdownV2 \
  --message "*Build Success*\n\n_Pipeline_: CI/CD\n_Branch_: main\n_Commits_: 3\n_Status_: \`passed\`"
```

### Formatted message (HTML)

```bash
python3 scripts/send_message.py \
  --parse-mode HTML \
  --message "<b>Build Success</b><br><br><i>Pipeline</i>: CI/CD"
```

### Override credentials via flags

```bash
python3 scripts/send_message.py \
  --token "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" \
  --chat-id "987654321" \
  --message "Override test"
```

### Disable auto-retry

```bash
python3 scripts/send_message.py \
  --message "No retry on failure" \
  --no-retry
```

### Discover chat ID

```bash
python3 scripts/discover_chat_id.py "$TELEGRAM_BOT_TOKEN"
```

## Message Formatting

### MarkdownV2

Use `--parse-mode MarkdownV2` for full formatting support:

| Style | Syntax |
|-------|--------|
| Bold | `*bold*` |
| Italic | `_italic_` |
| Underline | `__underline__` |
| Strikethrough | `~strikethrough~` |
| Inline code | `` `code` `` |
| Link | `[text](URL)` |
| Blockquote | `> text` |

Escape special characters with backslash: `_*[]()~\>#:+-=|{}.!`

### HTML

Use `--parse-mode HTML` for HTML formatting:

| Style | Syntax |
|-------|--------|
| Bold | `<b>text</b>` |
| Italic | `<i>text</i>` |
| Code | `<code>text</code>` |
| Link | `<a href="URL">text</a>` |

Escape `<`, `>`, `&` as `&lt;`, `&gt;`, `&amp;`.

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes (or use `--token`) |
| `TELEGRAM_CHAT_ID` | Target chat ID | Yes (or use `--chat-id`) |

### CLI Flags

| Flag | Description | Required |
|------|-------------|----------|
| `--message` / `-m` | Message text (1-4096 chars) | Yes |
| `--token` | Bot token (overrides env var) | No |
| `--chat-id` | Chat ID (overrides env var) | No |
| `--parse-mode` | `MarkdownV2`, `HTML`, or empty (default: plain text) | No |
| `--no-retry` | Disable auto-retry on 429 | No |

## Error Handling

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Message sent successfully |
| `1` | Failed (error printed to stderr) |

### Telegram API Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 400 | Bad Request | Check chat ID format, message length, or escape errors |
| 401 | Unauthorized | Verify bot token is valid and not revoked |
| 403 | Forbidden | Add bot to chat, check admin permissions for channels |
| 404 | Not Found | Chat does not exist or bot was removed |
| 429 | Too Many Requests | Script auto-retries once with `retry_after` delay |

### Rate Limits

- Default limit: 30 messages per second
- On 429 error: script reads `retry_after` from the response and waits before retrying
- Maximum one automatic retry per message
- Disable auto-retry with `--no-retry`

## Extensibility

### Adding new features

The scripts use Python stdlib exclusively. To add features:

1. **Media support**: Extend `send_message.py` to call `sendPhoto`, `sendDocument`, etc.
2. **Keyboard buttons**: Add `reply_markup` parameter support for inline and reply keyboards
3. **Message editing**: Add an `edit_message` script calling `editMessageText`
4. **Message deletion**: Add a `delete_message` script calling `deleteMessage`

All Telegram Bot API endpoints follow the same pattern:

```
https://api.telegram.org/bot<TOKEN>/<METHOD>
```

### Integration with other tools

The script outputs a single line on success (`Sent (message_id: <id>)`) making it easy to parse in shell scripts:

```bash
if output=$(python3 scripts/send_message.py --message "test" 2>/dev/null); then
  msg_id=$(echo "$output" | grep -oP 'message_id: \K\d+')
  echo "Message sent with ID: $msg_id"
fi
```

## Tech Stack

- **Language**: Python 3 (stdlib only)
- **API**: Telegram Bot API (sendMessage, getUpdates)
- **Dependencies**: None (no pip packages)
- **Config**: Environment variables and CLI flags only

## License

See the project root LICENSE file.

## Related

- [Telegram Bot API Reference](https://core.telegram.org/bots/api)
- [@BotFather](https://t.me/BotFather) — create and manage Telegram bots
