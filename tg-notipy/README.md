# Telegram Notify

A Crush agent skill that sends Telegram messages, files, and albums through the Bot API using a self-contained Python script (`scripts/tg_notify.py`, stdlib only). It mirrors the `tg-notify` CLI surface for the direct Bot API sender lineage, mapping user intent to a mode, loading the mode recipe and its cross-reference guides, and running the matching command with a verification probe.

## Operations

- message -- send a text message or caption
- file -- send a document, photo, audio, video, voice, animation, or sticker (local file, URL, or file ID)
- album -- send a media group
- discover -- resolve a chat ID from the latest bot update
- whoami -- report the bot identity

## Guides

Operation-independent knowledge is split into guides loaded on demand:

- `references/guide-formatting.md` -- MarkdownV2, HTML, plain text, escaping rules
- `references/guide-filetypes.md` -- detection order, type tables, size limits, album item rules
- `references/guide-retry.md` -- 429 and transient retry policy and override flags
- `references/guide-config.md` -- env vars, flag precedence, `.env`, proxy, base-url, exit codes, JSON, dry-run
- `references/gotchas.md` -- field-verified failure modes

## Prerequisites

- Telegram bot created via @BotFather (bot token required)
- Bot added to the target chat
- `python3` in PATH (stdlib only, no pip dependencies)
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` set in the environment

## License

See the project root LICENSE.