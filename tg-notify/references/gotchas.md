# tg-notify Gotchas (field-verified friction)

Verified against tg-notify v1.1.20260825 (the baseline version),
2026-08-27. Read this before executing operations to avoid
rediscovering failures. Every entry states the symptom and the fix.

## G1. Multi-word positional text must be quoted

An unquoted multi-word message is parsed as several positional
arguments and rejected:

```text
Failed: quote multi-word messages: tg-notify "hello world"
```

Fix: quote the message as one argument:
`tg-notify "hello world"`. The same rule applies to a positional
caption next to a file flag.

## G2. Flags work anywhere on the command line

Arguments are reordered before parsing, so flags can appear after the
positional text:

```bash
tg-notify "done" --silent --reply-to 42
```

No fix needed; this is documented behavior.

## G3. Empty parse mode is plain text

The default parse mode is empty, which sends plain text. Any reserved
MarkdownV2 character sent without `--parse-mode` arrives as a literal
character, not formatting.

Fix: add `--parse-mode MarkdownV2` or `--parse-mode HTML` and escape
the text per `references/guide-formatting.md`.

## G4. Detection order is extension table, then MIME table, then document

The extension table in the binary is consulted first; the MIME table
derived from the extension is second; any unknown type falls back to
document. A file named `report.pdf` sends as document, not photo.

Fix: force the type with `--type` when the extension is misleading.
The full tables live in `references/guide-filetypes.md`.

## G5. The single 429 retry survives --retries 0

A 429 rate limit waits `retry_after` seconds (default 5 when absent)
and retries exactly once. That one retry also happens when
`--retries 0` is set, because `--retries` governs the transient loop
only. Transient errors (timeouts, connection errors, HTTP 5xx) retry
up to 60 times by default with exponential backoff. Only `--no-retry`
makes a send fully one-shot.

Fix: pass `--no-retry` for interactive one-shot sends. Read
`references/guide-retry.md` for the full policy.

## G6. Numeric flags carry bounds and mode flags are validated

`--reply-to` and `--offset` must be >= 0; `--retries` must be >= 0;
`--base-wait` must be > 0. Flags that do not apply to the selected
mode are rejected (for example a message with `--whoami`, or
`--offset` without `--discover-chat-id`). Every failure exits 1 (G7).

Fix: remove the offending flag or correct the value; read the error
text on stderr.

## G7. Exit codes are 0 and 1 only

Success exits 0; this includes `--help` and `-v`. Every failure exits
1, including unknown flags, missing flag values, and mode conflicts.
There is no exit code 2.

Fix: treat any non-zero exit as failure and read stderr.

## G8. The bot token is scrubbed from errors

The `/bot…/` segment of Bot API URLs is masked in error output, and
request bodies are never logged. Never print the token yourself, and
never store a real token in a skill file or a recipe.

Fix: none needed; keep it that way.

## G9. Terminal stdin prints usage instead of hanging

With no `--message` and no positional text, the message is read from
stdin. On an interactive terminal there is no piped data, so the CLI
prints usage and exits 1 instead of waiting.

Fix: pipe the text (`printf 'text\n' | tg-notify`) or pass
`--message`.

## G10. The .env file only fills unset variables

A `./.env` file in the working directory is read at startup, but it
sets only variables that the real environment has not already set.
Flags still win over everything.

Fix: unset the exported variable, or pass the flag, when the file
value is ignored.

## G11. File sources are mutually exclusive

`--file`, `--url`, and `--file-id` accept exactly one source.
Combining two fails with an error.

Fix: pick one source per send.

## G12. Positional caption conflicts with --caption and --message

With a file flag present, one positional text argument becomes the
caption. It conflicts with `--caption` and `--message`, which are
rejected with an error.

Fix: use the positional text or `--caption`, never both.

## G13. --dry-run never sends

`--dry-run` prints the resolved request (method, chat ID, source,
type, size or caption length) without a network call and without the
token, and it works with `--json`. The token and chat ID must resolve,
but they are not validated.

Fix: none needed; use it as the safe verification probe.

## G14. socks5 and socks5h behave identically

The proxy library always sends the hostname to the proxy, so there is
no curl-style local DNS distinction between the two schemes.

Fix: use either scheme; expect identical behavior.

## G-stale. A stale PATH binary rejects documented flags

A PATH binary older than the baseline version can reject flags the
skill documents, with `flag provided but not defined` and exit 1.

Fix: run `tg-notify -v`, compare against the baseline version in
SKILL.md, and suggest that the user update the binary, for example
with `go install gitlab.com/lyoneel/cli-tg-notify/cmd/tg-notify@latest`
or a fresh build from the project. The skill never rebuilds or
reinstalls on its own.
