# Mode: File

Send one file: local upload (`--file`), remote URL (`--url`), or
resend by Telegram `file_id` (`--file-id`). Load
`../guide-filetypes.md` before composing the command.

## Triggers

send file, upload, screenshot, photo, document, audio, video, voice,
sticker, url file, resend file, file-id

## Guides

- `../guide-filetypes.md` (detection, limits, self-hosted relaxation)
- `../guide-formatting.md` (formatted captions)
- `../gotchas.md` (G6, G7, G8, G9)

## Recipes

Local image (auto-detected type):

```bash
python3 scripts/tg_notify.py -f /path/to/screenshot.png
```

Local document with caption via positional text (see `../gotchas.md`
G9):

```bash
python3 scripts/tg_notify.py "Monthly report" -f /path/to/report.pdf --parse-mode MarkdownV2
```

Remote file by URL (server-side limits apply, see `../gotchas.md` G7):

```bash
python3 scripts/tg_notify.py \
  --url https://example.com/document.pdf \
  --type document \
  --caption "Reference document"
```

Resend a file already on Telegram servers by `file_id` (`--type` is
required):

```bash
python3 scripts/tg_notify.py \
  --file-id AgACAgIAAxkBAAIBZK... \
  --type photo \
  --caption "Resending previous photo"
```

`--type` overrides auto-detection when the extension or MIME type is
wrong; valid values are listed in `../guide-filetypes.md`.

## Verification Probe

```bash
python3 scripts/tg_notify.py --dry-run -f /path/to/file -c cap
```

Expected: `dry-run: send  file (local=/path/to/file) to <chat-id>`.
Note the file dry run does not stat-check the path (see
`../gotchas.md` G1).

## Failure Notes

- Oversized local upload: rejected before the send with the exact MB
  values; limits live in `../assets/constant-limits.md`
- `--file`, `--url`, and `--file-id` are mutually exclusive; use
  exactly one
- `--file-id` without `--type` fails with an error
