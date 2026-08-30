# tg-notify

A Crush agent skill that serves as the reference for the `tg-notify`
command-line tool, a Go CLI that sends Telegram messages, files, and
albums through the Bot API with a self-contained client.

This skill documents the CLI surface, not a script. It maps user intent
to a mode, loads the mode recipe and its cross-reference guides, and
returns a ready command with a verification probe.

## Operations

- **message** -- send a text message or caption
- **file** -- send a document, photo, audio, or video (local file, URL, or file ID)
- **album** -- send a media group
- **discover** -- resolve a chat ID
- **whoami** -- report the bot identity
- **config** -- proxy, base URL, env vars, `.env`, shell completion

## Guides

Operation-independent knowledge is split into guides loaded on demand:

- `references/guide-formatting.md` -- MarkdownV2, HTML, plain text, escaping rules
- `references/guide-filetypes.md` -- detection order, type tables, size limits, album item rules
- `references/guide-retry.md` -- 429 and transient retry policy and override flags
- `references/guide-config.md` -- env vars, flag precedence, `.env`, proxy, base-url, exit codes, JSON, dry-run
- `references/gotchas.md` -- field-verified failure modes

## Prerequisites

- The `tg-notify` binary on PATH (the skill resolves it from PATH only and never installs it)
- A bot token and chat ID configured via env vars or flags

The skill's definitions track a baseline binary version documented in
`SKILL.md`; when the CLI drifts from that baseline, the skill stops and
asks the user to update it.

## License

See the project root LICENSE.