# Mode: File

Send one file by local path, URL, or file_id.

Load on demand: `references/guide-filetypes.md`,
`references/guide-formatting.md`.

## Decision Flow

1. Source: exactly one of `--file`, `--url`, `--file-id` (G11).
2. Type: auto-detected for local paths (G4), or forced with
   `--type`. `--type` is required with `--file-id`.
3. Caption: `--caption` or one positional text argument, never both
   (G12). Caption is 0-1024 characters.
4. Options: `--reply-to`, `--silent`, `--json`, `--dry-run`.
5. Size limits and the `--base-url` 2000 MB caveat are in
   guide-filetypes.md.

## Local File

```bash
tg-notify --file photo.jpg
tg-notify -f report.pdf --type document
tg-notify "caption text" -f photo.jpg
```

Type comes from the extension table first, the MIME table second, and
document as fallback. Force another type with `--type photo`,
`document`, `audio`, `video`, `voice`, `animation`, or `sticker`.

## URL Send

```bash
tg-notify --url https://example.com/report.pdf --type document
```

Telegram downloads the URL server-side. URL limits: 5 MB photo, 20 MB
other types; sendDocument by URL is PDF and ZIP only; sendVoice by URL
is audio/ogg and at most 1 MB (guide-filetypes.md).

## File-ID Resend

```bash
tg-notify --file-id AgACAgIAAxkDAAIB --type photo
```

A file_id resends a file already on Telegram servers. The type cannot
be auto-detected from a file_id, so `--type` is required.

## Caption Variants

```bash
tg-notify --file photo.jpg --caption "screenshot"
tg-notify "screenshot" --file photo.jpg
tg-notify --file photo.jpg --caption '*v1.1*' --parse-mode MarkdownV2
```

Escape MarkdownV2 captions per guide-formatting.md.

## Options

```bash
tg-notify --file photo.jpg --reply-to 42
tg-notify --file photo.jpg --silent
tg-notify --file photo.jpg --json     # {"ok":true,"message_id":N}
```

## Verification Probe

```bash
tg-notify --dry-run --file photo.jpg
```

Exit 0 and a `dry-run: send … file (local=photo.jpg) …` line confirm
the command shape without sending (G13). The single-file dry run does
not stat-check the path, so use a real path for a true probe.
