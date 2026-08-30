# Mode: Message

Send a text message (sendMessage). Load `../guide-formatting.md`
before composing formatted text.

## Triggers

send message, notify, alert, text, announce, stdin message, reply,
silent message

## Guides

- `../guide-formatting.md` (any `--parse-mode` other than empty)
- `../guide-retry.md` (failure, timeout, or retry tuning)

## Recipes

Plain text (positional):

```bash
python3 scripts/tg_notify.py "Deployment complete"
```

Flag form:

```bash
python3 scripts/tg_notify.py --message "Deployment complete"
```

Read from stdin (trimmed by default; `--no-trim` keeps whitespace):

```bash
printf 'line one\n' | python3 scripts/tg_notify.py
printf 'keep trailing spaces   \n' | python3 scripts/tg_notify.py --no-trim
```

Formatted text: set `--parse-mode MarkdownV2` or `--parse-mode HTML`
and follow the escaping rules in `../guide-formatting.md`.

Reply, silent, and JSON output:

```bash
python3 scripts/tg_notify.py --reply-to 42 "answer"
python3 scripts/tg_notify.py --silent "quiet update"
python3 scripts/tg_notify.py --json "hello"
```

Credentials and environment overrides (flags beat env; see
`../guide-config.md` for the full chain):

```bash
python3 scripts/tg_notify.py \
  --token "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" \
  --chat-id "987654321" \
  --message "Override test"
python3 scripts/tg_notify.py --base-url https://bot-api.example.com:8081 "hello"
python3 scripts/tg_notify.py --proxy http://proxy.example.com:8080 "hello"
python3 scripts/tg_notify.py --retries 5 --base-wait 1s "flaky link update"
python3 scripts/tg_notify.py --no-retry "one-shot"
```

## Verification Probe

```bash
python3 scripts/tg_notify.py --dry-run "probe"
```

Expected: `dry-run: sendMessage to <chat-id> (5 chars)`, no network
call.

## Failure Notes

- No message source and terminal stdin prints usage to stderr, exit 1
- HTTP 400 with a parse error: see `../gotchas.md` G5
- `Failed: <reason>` on stderr, exit 1; never re-run to re-check, see
  `../gotchas.md` G3
