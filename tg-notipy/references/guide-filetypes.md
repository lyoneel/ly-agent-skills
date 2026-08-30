# File Types Guide

Detection order, limit semantics, and album item rules for file and
album sends. The detection maps and every numeric limit live in
`../assets/constant-filetypes.md` and `../assets/constant-limits.md`;
this file never re-lists them. Dump current values with
`python3 scripts/tg_constants.py --dump all`.

## Auto-Detection Order

When `--type` is not specified, the script detects the type from the
file extension first, then the MIME type (extension map before MIME
map). Any extension or MIME type absent from both maps falls back to
`document`. `--type` overrides detection entirely; valid overrides:
`photo`, `document`, `audio`, `video`, `voice`, `animation`,
`sticker`.

## Size Limits: Which Apply When

Three sources carry different limits, and only one applies per send:

1. Local uploads (`--file`): the script enforces the per-type limits in
   `../assets/constant-limits.md` before the send and rejects oversized
   files with the exact MB values in the error message.
2. URL-based (`--url`): limits are enforced server-side by Telegram and
   are stricter than the local limits; see `gotchas.md` G6 and G7 for
   the server-side facts (photo limit, general limit, voice limit, and
   the PDF/ZIP-only `sendDocument` restriction).
3. File ID (`--file-id`): no size limits; the file already lives on
   Telegram servers.

## Self-Hosted Limit Relaxation

With the `--base-url` flag (self-hosted Bot API server), the local
upload limit for all types relaxes to the self-hosted value in
`../assets/constant-limits.md`. Setting `TELEGRAM_BASE_URL` alone does
not relax the limit; the flag is required (see `gotchas.md` G8).

## Album Item Rules

Albums (sendMediaGroup) follow these rules:

- Items are the repeated `--album` flags plus any trailing positional
  arguments; the count bounds come from
  `../assets/constant-limits.md` and are enforced at send time; a dry
  run prints any count
- All items must be local paths, or all URLs; mixing is rejected
- Any detected type other than photo or video is coerced to photo
- One caption, `--parse-mode`, `--reply-to`, and `--silent` attach to
  the first item only; there is no per-item caption flag
- Local items are stat-checked before the send, so a missing path
  fails fast, even in dry run (see `gotchas.md` G1)
- Success prints `Sent album (N messages)`; `--json` prints
  `{"ok":true,"message_ids":[...]}`
