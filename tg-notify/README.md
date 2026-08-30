# Telegram Bot Notifications (CLI)

A skill for sending Telegram bot notifications through the [`tg-notify` command-line tool](https://gitlab.com/lyoneel/cli-tg-notify), a Go CLI, using Bot API. It maps user intent to one of six operations (message, file, album, discover, whoami, config), loads the matching mode recipe and its cross-reference guides, and returns a ready command with a verification probe. Use it when composing or debugging tg-notify commands, or sending messages, files, and albums from within Crush. Compared with the [Python sender](../tg-notipy/README.md), the Go CLI adds a few features: shell completion for bash, zsh, and fish, and socks5/socks5h proxy support. Where features overlap, both share the same structure and parameters, so at feature parity the two are interchangeable.

## Operations

- message -- send a text message or caption
- file -- send a document, photo, audio, or video (local file, URL, or file ID)
- album -- send a media group
- discover -- resolve a chat ID
- whoami -- report the bot identity
- config -- proxy, base URL, env vars, `.env`, shell completion

## Guides

Operation-independent knowledge is split into guides loaded on demand:

- [Formatting](references/guide-formatting.md) -- MarkdownV2, HTML, plain text, escaping rules
- [File types](references/guide-filetypes.md) -- detection order, type tables, size limits, album item rules
- [Retry](references/guide-retry.md) -- 429 and transient retry policy and override flags
- [Configuration](references/guide-config.md) -- env vars, flag precedence, `.env`, proxy, base-url, exit codes, JSON, dry-run
- [Gotchas](references/gotchas.md) -- field-verified failure modes

## Prerequisites

- The `tg-notify` binary on PATH (the skill resolves it from PATH only and never installs it)
- A bot token and chat ID configured via env vars or flags

The skill's definitions track a baseline binary version documented in `SKILL.md`; when the CLI drifts from that baseline, the skill stops and asks the user to update it.

## License

See the project root LICENSE.