---
name: tg-notipy
description: Send messages, files, and albums to Telegram chats via the Bot API. Use when sending notifications, alerts, media, or albums from Crush to Telegram, discovering chat IDs, or checking bot identity.
title: Telegram Notify
version: "20260829-3"
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash"]
---

Initialize todos for tg-notipy operation:

```json
{
  "todos": [
    {"content": "Parse user request and detect mode", "status": "in_progress", "activeForm": "Parsing user request and detecting mode"},
    {"content": "Verify configuration (bot token and chat ID)", "status": "pending", "activeForm": "Verifying configuration"},
    {"content": "Load mode reference and cross-reference guides", "status": "pending", "activeForm": "Loading mode reference and guides"},
    {"content": "Execute operation via scripts/tg_notify.py", "status": "pending", "activeForm": "Executing operation via tg_notify.py"},
    {"content": "Handle response and errors", "status": "pending", "activeForm": "Handling response and errors"},
    {"content": "Complete tg-notipy operation", "status": "pending", "activeForm": "Completing tg-notipy operation"}
  ]
}
```

# Telegram Notify

Reference for the tg-notipy CLI. One Python script
(`scripts/tg_notify.py`, stdlib only) sends messages, files, and
albums to Telegram via the Bot API, with MarkdownV2 and HTML
formatting, auto-retry on rate limits and transient errors, chat ID
discovery, bot identity checks, JSON output, dry-run verification, and
proxy or self-hosted base URL support. Flags may appear anywhere on the
command line; one positional text argument is accepted (message text,
or caption when a file flag is present, or extra album items in album
mode). When no message source is given, the message is read from
stdin. Each operation maps to a mode file in `references/modes/`.
Operation-independent knowledge lives in `references/guide-*.md` files
that modes load on demand. Field-verified failure modes live in
`references/gotchas.md`.

## Single Source of Truth

All fixed values (message and caption char limits, upload size limits,
album item bounds, retry defaults, extension and MIME type maps) live
in `assets/constant-limits.md` and `assets/constant-filetypes.md`. The
script loads them at startup via `scripts/tg_constants.py`; the agent
reads the same files. Prose references the constant files and never
re-lists a value. Dump current values:

```bash
python3 scripts/tg_constants.py --dump all
```

## Prerequisites

- Telegram bot created via @BotFather (bot token required)
- Bot added to target chat (private, group, or channel)
- `python3` available in PATH (stdlib only, no pip dependencies)

Full environment setup and flag reference:
`references/guide-config.md`.

## Configuration Resolution

1. `--token` CLI flag, else `TELEGRAM_BOT_TOKEN` env var (or `./.env`)
2. `--chat-id` CLI flag, else `TELEGRAM_CHAT_ID` env var (or `./.env`)
3. Base URL: `--base-url` flag, else `TELEGRAM_BASE_URL`, else official API
4. Proxy: `--proxy` flag, else `TELEGRAM_PROXY`

A `./.env` file fills token and chat ID only when they are not already
set in the environment. Details: `references/guide-config.md`.

## Gotchas (field-verified friction)

Read `references/gotchas.md` before executing operations. Top entries:

- G3: never re-run a send to re-check its exit status; re-running
  re-delivers the content as a duplicate
- G5: MarkdownV2 rejects the first unescaped reserved character with
  HTTP 400 naming it; prefer plain text or HTML for generated text
- G8: the local upload limit relaxes for self-hosted servers only with
  the `--base-url` flag, not `TELEGRAM_BASE_URL` alone

## Mode Detection

Map user intent to a mode. Load the mode file, then load the guides in
the Guides column before composing commands.

| Trigger Keywords | Mode | Mode File | Guides |
|------------------|------|-----------|--------|
| send message, notify, alert, text, announce, stdin, reply, silent | Message | `references/modes/mode-message.md` | `references/guide-formatting.md` |
| send file, upload, screenshot, photo, document, audio, video, voice, url file, file-id | File | `references/modes/mode-file.md` | `references/guide-filetypes.md`, `references/guide-formatting.md` |
| album, media group, gallery, multiple photos | Album | `references/modes/mode-album.md` | `references/guide-filetypes.md`, `references/guide-formatting.md` |
| discover, find chat id, setup chat | Discover | `references/modes/mode-discover.md` | `references/guide-config.md` |
| whoami, bot identity, validate token | Whoami | `references/modes/mode-whoami.md` | `references/guide-config.md` |

## Cross-Reference Guides

Load a guide when its trigger matches. Guides are independent of any
single operation:

| Guide | Purpose | Load Trigger |
|-------|---------|--------------|
| `references/guide-config.md` | Env vars, flag table, precedence, exit codes, JSON shapes, dry-run, testing | Any configuration question or error diagnosis |
| `references/guide-filetypes.md` | Detection order, limit semantics, self-hosted relaxation, album item rules | Any file or album send |
| `references/guide-formatting.md` | MarkdownV2, HTML, plain text, escaping rules | Any formatted text or caption |
| `references/guide-retry.md` | 429 and transient retry policy and override flags | Any failure, timeout, or retry tuning |

## Response Handling

On success the script prints `Sent (message_id: <id>)`, `Sent album
(N messages)`, the chat ID (discover), or `@username (id: N)`
(whoami) to stdout; with `--json` it prints `{"ok":true,...}` shapes.
On failure it prints `Failed: <reason>` to stderr and exits 1. HTTP
error codes and actions: `references/guide-config.md`.

## BEGIN EXECUTION IMMEDIATELY

Do not ask the user what to do. Start with step 1:

1. Detect the mode from the request using the Mode Detection table.
2. Verify configuration: `TELEGRAM_BOT_TOKEN` is set (else ask the
   user), and `TELEGRAM_CHAT_ID` or `--chat-id` is available for send
   modes. Run `--whoami` first when the token validity is unknown.
3. Load the mode file for the detected mode.
4. Load every guide listed in the mode's Guides column.
5. Read `references/gotchas.md` and apply every relevant entry.
6. Run the command from the mode recipes and run the verification
   probe from the mode file. Handle the response per the mode file.

> Update todos at each step. After completion, output a summary and
> clear with `todos([])`.
