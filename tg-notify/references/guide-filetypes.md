# Guide: File Types, Detection, and Size Limits

tg-notify sends files through sendPhoto, sendDocument, sendAudio,
sendVideo, sendVoice, sendAnimation, and sendSticker. Type detection
is local and deterministic.

## Detection Order

1. Extension table (below), matched on the lower-case file extension.
2. MIME table (below), derived from the extension by the Go MIME
   database.
3. Fallback: document.

An explicit `--type` override replaces detection entirely.

## Extension Table (internal/telegram/filetype.go, extToType)

| Extension | Type |
|-----------|------|
| `.jpg` | photo |
| `.jpeg` | photo |
| `.png` | photo |
| `.gif` | photo |
| `.webp` | photo |
| `.bmp` | photo |
| `.mp3` | audio |
| `.m4a` | audio |
| `.aac` | audio |
| `.flac` | audio |
| `.ogg` | voice |
| `.opus` | voice |
| `.mp4` | video |
| `.webm` | video |
| `.mkv` | video |
| `.mov` | video |
| `.avi` | video |
| `.flv` | video |
| `.wmv` | video |
| `.m4v` | video |
| `.ogv` | video |

## MIME Table (internal/telegram/filetype.go, mimeToType)

| MIME type | Type |
|-----------|------|
| `image/jpeg` | photo |
| `image/png` | photo |
| `image/gif` | photo |
| `image/webp` | photo |
| `audio/mpeg` | audio |
| `audio/mp3` | audio |
| `audio/mp4` | audio |
| `audio/x-m4a` | audio |
| `audio/m4a` | audio |
| `audio/ogg` | voice |
| `audio/opus` | voice |
| `video/mp4` | video |
| `video/webm` | video |
| `video/x-matroska` | video |
| `video/quicktime` | video |
| `video/avi` | video |
| `video/x-msvideo` | video |
| `video/x-flv` | video |
| `video/mpeg` | video |
| `video/x-ms-wmv` | video |

## --type Override Values

`--type` accepts exactly these values: `photo`, `document`, `audio`,
`video`, `voice`, `animation`, `sticker`. It is required with
`--file-id`, because a file_id carries no detectable type.

## Size Limits

| Source | Limit |
|--------|-------|
| Local upload, photo, official API | 10 MB |
| Local upload, other types, official API | 50 MB |
| Local upload, all types, self-hosted via `--base-url` | 2000 MB |
| URL, photo | 5 MB (server-side) |
| URL, other types | 20 MB (server-side) |
| file-id resend | no limit |

URL limits are enforced by Telegram server-side. sendDocument by URL
works only for `.PDF` and `.ZIP` files. sendVoice by URL requires
audio/ogg and at most 1 MB.

Self-hosted caveat: the 2000 MB client-side relaxation reads the
`--base-url` flag only. Setting TELEGRAM_BASE_URL alone switches the
target server but keeps the 10 MB photo / 50 MB other client-side
check. Pass `--base-url` to lift the local check.

## Album Item Rules

Albums (`--album`) hold 2-10 items. Every item must be a photo or a
video; any other detected type is coerced to photo. All items share
one transport: all local paths, or all URLs. Mixing local paths and
URLs in one album is rejected. Local items are stat-checked before
the send. See `references/modes/mode-album.md`.
