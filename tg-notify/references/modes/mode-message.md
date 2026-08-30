# Mode: Message

Send a text message (sendMessage). Message text is 1-4096 characters.

Load on demand: `references/guide-formatting.md`.

## Decision Flow

1. Text source: `--message`, one positional argument, or stdin when
   neither is given (G9).
2. Multi-word text must be one quoted argument (G1).
3. Formatting: plain text by default (G3); `--parse-mode MarkdownV2`
   or `HTML` with escaping per guide-formatting.md.
4. Options: `--reply-to`, `--silent`, `--json`, `--dry-run`.
5. A positional text argument conflicts with `--message` (G12).

## Basic Send

```bash
tg-notify "hello"
tg-notify --message "hello"
```

## Formatted Send

```bash
tg-notify --message '*bold* _italic_' --parse-mode MarkdownV2
tg-notify --message '<b>done</b>' --parse-mode HTML
```

Escape reserved characters in MarkdownV2 (guide-formatting.md).

## Stdin Pipe

```bash
printf 'line one\n' | tg-notify
printf 'keep trailing spaces   \n' | tg-notify --no-trim
```

Stdin text is trimmed unless `--no-trim` is set. On a terminal with
no pipe, the CLI prints usage and exits 1 instead of hanging (G9).

## Reply, Silent, JSON

```bash
tg-notify --reply-to 42 "answer"
tg-notify --silent "quiet update"
tg-notify --json "hello"      # {"ok":true,"message_id":N}
```

## Verification Probe

```bash
tg-notify --dry-run "hello"
```

Exit 0 and a `dry-run: sendMessage …` line confirm the command shape
without sending anything (G13).
