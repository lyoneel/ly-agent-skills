# Gotchas

Field-verified friction for tg-notipy. Read before executing operations.
Numeric limits come from `../assets/constant-limits.md`; never re-list
them here.

G1: a file dry run does not stat-check the local path; an album dry run
does stat-check every local item. A missing file fails fast only in
album mode and at real send time.

G2: stdout and stderr can appear out of order when output is captured.
stderr is unbuffered; stdout is block-buffered when piped. Interleaved
output looks alarming but is not failure.

G3: never re-run a send to re-check its exit status. `Sent
(message_id: <id>)` on stdout is terminal success, and a re-run
re-delivers the content as a duplicate. Verify status from the same
invocation only.

G4: a 429 rate limit retries exactly once after the server
`retry_after` (default 5 when absent). This single retry still happens
with `--retries 0`; only `--no-retry` makes a send one-shot.

G5: MarkdownV2 rejects the message with HTTP 400 naming the first
unescaped reserved character (example: `can't parse entities:
Character '-' is reserved and must be escaped with the preceding '\'`).
Escaping applies to every reserved character, including `-` and `.`.
Escape the named character and resend, or prefer plain text or HTML.

G6: `sendDocument` by URL works only for PDF and ZIP files. Other
document types by URL fail server-side.

G7: URL-based sends have Telegram server-side limits not enforced or
listed by this skill: 5 MB for photos, 20 MB for other types, 1 MB for
`sendVoice`. Local upload limits in `../assets/constant-limits.md` do
not apply to URL sends.

G8: the local upload limit relaxes to the self-hosted value in
`../assets/constant-limits.md` only with the `--base-url` flag.
Setting `TELEGRAM_BASE_URL` alone does not relax the limit.

G9: positional text acts as the caption when a file flag is present,
not as a second message. `--caption` conflicts with a positional text
caption.

G10: group and channel chat IDs are negative numbers (example:
`-1001234567890`). Discovery returns the sign as Telegram reports it.

G11: the former scripts `send_message.py`, `send_file.py`, and
`discover_chat_id.py` were removed. `scripts/tg_notify.py` is the
single entry point: messages via `--message`/`-m`, positional text, or
stdin; files via `--file`/`--url`/`--file-id`; albums via `--album`;
discovery via `--discover-chat-id`; bot identity via `--whoami`.

G12: bot tokens are scrubbed from all error output. Request bodies are
never logged.

G13: fixed values (limits, retry defaults, file type maps) live in
`../assets/constant-limits.md` and `../assets/constant-filetypes.md`.
The script and the agent read the same files via
`scripts/tg_constants.py`. Update a value there only; prose never
re-lists it.
