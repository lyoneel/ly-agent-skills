---
name: tg-notify
description: "Send Telegram messages, files, and albums via the tg-notify command-line tool. Use when composing or debugging tg-notify commands or sending messages, files, or albums through the tg-notify binary."
title: Telegram Bot Notifications (CLI)
version: "20260829-2"
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash", "glob", "grep", "view", "ls"]
system-tools: ["tg-notify"]
---

Initialize todos for tg-notify skill operation:

```json
[
  {"content": "Parse user request and detect mode", "status": "in_progress", "active_form": "Parsing user request and detecting mode"},
  {"content": "Resolve tg-notify from PATH and compare the baseline version", "status": "pending", "active_form": "Resolving tg-notify and comparing the baseline version"},
  {"content": "Load mode reference and cross-reference guides", "status": "pending", "active_form": "Loading mode reference and guides"},
  {"content": "Provide command with verification probe", "status": "pending", "active_form": "Providing command"},
  {"content": "Complete tg-notify operation", "status": "pending", "active_form": "Completing tg-notify operation"}
]
```

# Telegram Bot Notifications (CLI)

Use the tg-notify command-line tool, a Go CLI that sends
Telegram messages and files through the Bot API with a self-contained
client. Each operation maps to a mode file in `references/modes/`.
Operation-independent knowledge (text formatting, file types, retry
policy, configuration) lives in `references/guide-*.md` files that
modes load on demand. Field-verified failure modes live in
`references/gotchas.md`.

## Tool Availability and Binary Baseline

Resolve the binary from PATH only. The skill has no project fallback
and never builds or installs the binary:

```bash
command -v tg-notify >/dev/null 2>&1 || { echo "MISSING: tg-notify"; exit 1; }
tg-notify -v
```

The definitions in this skill were written against tg-notify
v1.1.20260825, the baseline version. Compare the output of
`tg-notify -v` against the baseline. If the PATH binary is older than
the baseline, or a documented flag fails with
`flag provided but not defined` (G-stale), stop and suggest that the
user update the binary, for example with
`go install gitlab.com/lyoneel/cli-tg-notify/cmd/tg-notify@latest` or
a fresh build from the project. Then resume.

Read `references/gotchas.md` before executing operations.

## Gotchas (field-verified friction)

G1: multi-word positional text must be quoted; unquoted words are
rejected with a quoting hint.
G2: flags work anywhere on the command line; arguments are reordered
before parsing.
G3: an empty parse mode is plain text, and plain text is the default.
G4: the extension table is consulted before the MIME table; unknown
types fall back to document.
G5: a 429 retries exactly once, and that one retry still happens when
`--retries 0` is set; transient errors retry up to 60 times by
default; only `--no-retry` makes a send fully one-shot.
G6: `--reply-to` and `--offset` must be non-negative, `--retries`
must be >= 0, `--base-wait` must be > 0; mode-mismatched flags are
rejected with an error.
G7: exit codes are 0 for success (also `--help` and `-v`) and 1 for
every failure, including flag misuse; there is no exit code 2.
G8: the bot token is scrubbed from error output; request bodies are
never logged.
G9: with no message source, stdin on a terminal prints usage instead
of hanging.
G10: the `./.env` file only fills variables that are not already set;
the real environment and flags win.
G11: `--file`, `--url`, and `--file-id` are mutually exclusive; use
exactly one.
G12: `--caption` and `--message` each conflict with a positional text
caption.
G13: `--dry-run` never sends anything and works with `--json`.
G14: `socks5` and `socks5h` behave identically; the hostname always
goes to the proxy.

## Mode Detection

Map user intent to a mode. Load the mode file, then load the guides in
the Guides column before composing commands.

| Trigger Keywords | Mode | Mode File | Guides |
|------------------|------|-----------|--------|
| send message, notify, alert, text, announce | Message | `references/modes/mode-message.md` | `references/guide-formatting.md` |
| send file, upload, photo, audio, video, document, url file, file-id | File | `references/modes/mode-file.md` | `references/guide-filetypes.md` |
| album, media group, multiple photos, gallery | Album | `references/modes/mode-album.md` | `references/guide-filetypes.md`, `references/guide-formatting.md` |
| discover, find chat id, who is chatting | Discover | `references/modes/mode-discover.md` | `references/guide-config.md` |
| whoami, bot identity, getme | Whoami | `references/modes/mode-whoami.md` | `references/guide-config.md` |
| proxy, base-url, self-hosted, env, .env, completion, config | Config | `references/modes/mode-config.md` | `references/guide-config.md`, `references/guide-retry.md` |

## Cross-Reference Guides

Load a guide when its trigger matches. Guides are independent of any
single operation:

| Guide | Purpose | Load Trigger |
|-------|---------|--------------|
| `references/guide-formatting.md` | MarkdownV2, HTML, and plain text, escaping rules | Any formatted text or caption |
| `references/guide-filetypes.md` | detection order, type tables, size limits, album item rules | Any file or album send |
| `references/guide-retry.md` | 429 and transient retry policy and override flags | Any failure, timeout, or long upload |
| `references/guide-config.md` | env vars, flag precedence, .env, proxy, base-url, exit codes, json, dry-run | Any configuration question or error diagnosis |

## Maintenance

The skill definitions follow the binary baseline version in the Tool
Availability section. When the project CLI changes, the
`update-tg-notify` skill, which ships with the tg-notify-cli
repository, re-syncs this skill and bumps the baseline. This skill
holds no path to the project.

## BEGIN EXECUTION IMMEDIATELY

Do not ask the user what to do. Start with step 1:

1. Detect the mode from the request using the Mode Detection table.
2. Resolve the binary from PATH and compare `tg-notify -v` against the
   baseline version. On a missing binary, stop with install guidance.
   On an older binary, stop and suggest an update to the user.
3. Load the mode file for the detected mode.
4. Load every guide listed in the mode's Guides column.
5. Read `references/gotchas.md` and apply every relevant entry.
6. Compose the command from the mode recipes and run the verification
   probe from the mode file.

> Update todos at each step. After completion, output a summary and
> clear with `todos([])`.
