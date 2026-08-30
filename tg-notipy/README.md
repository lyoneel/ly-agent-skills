# Telegram Bot Notifications (Python)

A skill for sending Telegram bot notifications through a self-contained Python script (`scripts/tg_notify.py`, stdlib only, no dependencies). It maps user intent to one of its operations, loads the matching mode recipe and its cross-reference guides, and runs the command with a verification probe. Use it when sending messages, files, or albums from Crush to Telegram without installing anything. It is the lighter sibling of the [Go CLI](../tg-notify/README.md): the Go version adds a few features this script lacks, namely shell completion for bash, zsh, and fish, and socks5/socks5h proxy support. Where features overlap, both share the same structure and parameters, so at feature parity the two are interchangeable.

## Operations

- message -- send a text message or caption
- file -- send a document, photo, audio, video, voice, animation, or sticker (local file, URL, or file ID)
- album -- send a media group
- discover -- resolve a chat ID from the latest bot update
- whoami -- report the bot identity

## Guides

Operation-independent knowledge is split into guides loaded on demand:

- [Formatting](references/guide-formatting.md) -- MarkdownV2, HTML, plain text, escaping rules
- [File types](references/guide-filetypes.md) -- detection order, type tables, size limits, album item rules
- [Retry](references/guide-retry.md) -- 429 and transient retry policy and override flags
- [Configuration](references/guide-config.md) -- env vars, flag precedence, `.env`, proxy, base-url, exit codes, JSON, dry-run
- [Gotchas](references/gotchas.md) -- field-verified failure modes

## Prerequisites

- Telegram bot created via @BotFather (bot token required)
- Bot added to the target chat
- `python3` in PATH (stdlib only, no pip dependencies)
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` set in the environment

## License

See the project root LICENSE.