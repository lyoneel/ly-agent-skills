# Configuration Guide

Configuration resolution, flags, exit codes, and output shapes for
scripts/tg_notify.py. Numeric limits live in
`../assets/constant-limits.md`; this file explains semantics only.

## Configuration Resolution

The script resolves credentials via a priority chain. Config files are
not used, with one exception: a `./.env` file in the working directory
fills `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` when they are not
already set in the environment. The real environment and flags always
win. The same chain applies to all modes:

1. `--token` CLI flag, else `TELEGRAM_BOT_TOKEN` env var (or `./.env`)
2. `--chat-id` CLI flag, else `TELEGRAM_CHAT_ID` env var (or `./.env`)
3. Base URL: `--base-url` flag, else `TELEGRAM_BASE_URL`, else official API
4. Proxy: `--proxy` flag, else `TELEGRAM_PROXY`

Flags may appear anywhere on the command line; arguments are reordered
before parsing. One positional text argument is accepted (message text,
or caption when a file flag is present, or extra album items in album
mode). When no message source is given, the message is read from
stdin; with terminal stdin and no message source, the usage text prints
to stderr instead of hanging.

## Prerequisites

- Telegram bot created via @BotFather (bot token required)
- Bot added to target chat (private, group, or channel)
- `python3` available in PATH (stdlib only, no pip dependencies)
- Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the environment
  or shell profile to avoid passing `--token` and `--chat-id` on every
  invocation

## Flag Table

| Flag | Description | Required |
|------|-------------|----------|
| `--message` / `-m` | Message text (char limit from `../assets/constant-limits.md`) | One of `--message`, positional text, stdin, a file flag, or `--album` |
| (positional) | Text as first positional argument, e.g. `tg_notify.py "text"` | See above |
| `--file` / `-f` | Local file path to upload | One of `--file`, `--url`, `--file-id` for file sending; mutually exclusive |
| `--url` / `-u` | Remote file URL to send | See above |
| `--file-id` / `-F` | Telegram `file_id` to resend (requires `--type`) | See above |
| `--album` / `-a` | Repeatable; album items (photo/video; count limits from `../assets/constant-limits.md`); trailing positionals count as items too | No |
| `--type` / `-t` | Override auto-detection: `photo`, `document`, `audio`, `video`, `voice`, `animation`, `sticker` | Required with `--file-id` |
| `--caption` / `-c` | Caption text (char limit from `../assets/constant-limits.md`); positional text acts as caption with file flags | No |
| `--parse-mode` / `-p` | `MarkdownV2`, `HTML`, or empty (default: plain text) | No |
| `--reply-to` / `-r` | Message ID to reply to (>= 0) | No |
| `--silent` / `-S` | Deliver without a phone notification | No |
| `--json` / `-j` | Print machine-readable JSON instead of text | No |
| `--dry-run` / `-D` | Print the resolved request without sending | No |
| `--no-trim` | Do not trim whitespace from the stdin message | No |
| `--token` / `-T` | Bot token (overrides env var) | No |
| `--chat-id` / `-C` | Chat ID (required if `TELEGRAM_CHAT_ID` not set) | No |
| `--base-url` / `-U` | Bot API base URL for a self-hosted server | No |
| `--proxy` / `-P` | Proxy URL (http, https; socks5 is unsupported) | No |
| `--no-retry` / `-n` | Disable auto-retry on 429 and transient errors | No |
| `--retries` / `-R` | Max retries on transient errors (default from `../assets/constant-limits.md`, >= 0) | No |
| `--base-wait` / `-B` | First backoff wait on transient errors (default from `../assets/constant-limits.md`, Go duration form like `1s500ms`, must be > 0) | No |
| `--whoami` / `-w` | Print the bot identity and exit | No |
| `--discover-chat-id` / `-d` | Print the chat ID from the latest bot update | No |
| `--offset` / `-o` | Past update ID to skip in `--discover-chat-id` (>= 0) | No |
| `--version` / `-v` | Print the version (read from SKILL.md frontmatter) | No |
| `--help` / `-h` | Show usage and exit 0 | No |

Middle aliases are accepted: `--fileid`, `--chatid`, `--parsemode`,
`--noretry`, `--basewait`, `--discoverchatid`. Dash convention: one
dash only for one-letter flags; multi-letter flags take two dashes.
Mode-mismatched flags are rejected with an error.

## Exit Codes

- `0` -- success (also `--help` and `-v`)
- `1` -- failed (prints `Failed: <reason>` to stderr; a message with
  no text source and terminal stdin prints the usage text to stderr)

There is no exit code 2; flag misuse also exits 1.

## HTTP Error Codes

Error codes the script may report:

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check chat_id format, message length, or escape errors |
| 401 | Unauthorized | Verify bot token is valid and not revoked |
| 403 | Forbidden | Add bot to chat, check admin permissions for channels |
| 404 | Not Found | Chat does not exist or bot was removed |
| 429 | Too Many Requests | Script auto-retries once; if it fails again, wait and retry manually |
| 5xx | Server error | Script retries with backoff; tune `--retries`/`--base-wait` or use `--no-retry` |

## JSON Output Shapes

`--json` prints one compact JSON line on success:

- message: `{"ok":true,"message_id":N}`
- album: `{"ok":true,"message_ids":[N,N]}`
- discover: `{"ok":true,"chat_id":N}`
- whoami: `{"ok":true,"id":N,"is_bot":true,"first_name":"...","username":"..."}`

Failures still print `Failed: <reason>` to stderr and exit 1.

## Dry-Run Output

`--dry-run` prints the resolved request without any network call (works
with `--json`). Stat-check behavior differs per mode; see
`gotchas.md` G1. Examples:

```text
dry-run: sendMessage to 42 (5 chars)
dry-run: send  file (local=a.png) to 42
dry-run: send album (3 items), caption (3 chars)
```

## Machine-Readable Constants

Dump every fixed value the script enforces:

```bash
python3 scripts/tg_constants.py --dump all
```

## Testing

Run the offline stdlib test suite (no network, no token needed):

```bash
python3 scripts/test_tg_notify.py
```
