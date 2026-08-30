# Guide: Configuration, Precedence, and Output

## Environment Variables and Flag Overrides

| Variable | Flag override | Purpose |
|----------|---------------|---------|
| `TELEGRAM_BOT_TOKEN` | `--token` / `-T` | bot token |
| `TELEGRAM_CHAT_ID` | `--chat-id` / `-C` | chat ID, passed as a string so large and negative group IDs work |
| `TELEGRAM_BASE_URL` | `--base-url` / `-U` | Bot API base URL for a self-hosted server |
| `TELEGRAM_PROXY` | `--proxy` / `-P` | proxy URL: `http`, `https`, `socks5`, `socks5h` |

Every send, discover, and whoami run resolves the token first from the
flag, then from the environment variable. The chat ID resolves the
same way.

Middle aliases exist for the multi-word flags and behave identically
to the long form: `--fileid` (--file-id), `--chatid` (--chat-id),
`--parsemode` (--parse-mode), `--noretry` (--no-retry), `--basewait`
(--base-wait), and `--discoverchatid` (--discover-chat-id).

## Precedence Chain

Flag beats environment variable. Environment variable beats `./.env`
file. The `./.env` file is read at startup and fills only variables
that are not already set in the environment. File format: one
`KEY=VALUE` per line; blank lines and lines starting with `#` are
skipped; surrounding whitespace is trimmed. A missing file is not an
error.

## Proxy

Supported schemes: `http`, `https`, `socks5`, `socks5h`. The two
SOCKS schemes behave identically: the hostname always goes to the
proxy. An invalid proxy URL aborts before any network call. Read
`references/guide-retry.md` before testing through a broken proxy: a
refused connection is a transient error and retries up to 60 times by
default.

## Self-Hosted Base URL

`--base-url` (or `TELEGRAM_BASE_URL`) targets a self-hosted Bot API
server. Caveat: the client-side upload limit relaxes to 2000 MB only
when the `--base-url` flag is set. `TELEGRAM_BASE_URL` alone switches
the server but keeps the official 10 MB photo / 50 MB other
client-side check. See `references/guide-filetypes.md`.

## Exit Codes

| Exit code | Meaning | Examples |
|-----------|---------|----------|
| 0 | success | any successful send; `--help`; `-v` |
| 1 | every failure | bad token, unknown flag, missing flag value, mode conflict, empty stdin message, API error, terminal stdin usage fallback |

There is no exit code 2. Scripts must treat any non-zero exit as
failure and read stderr for the cause.

## JSON Output

`--json` prints one line of machine-readable JSON:

- send success: `{"ok":true,"message_id":N}`
- album success: `{"ok":true,"message_ids":[N,N,...]}`
- discover: `{"ok":true,"chat_id":N}`
- whoami: `{"ok":true,"id":N,"is_bot":true,"first_name":"…","username":"…"}`

## Dry Run

`--dry-run` prints the resolved request without any network call and
without the token. The token and chat ID must resolve, but they are
not validated. It works with `--json`:

- message: `{"ok":true,"dry_run":true,"method":"sendMessage","chat_id":"…","text_length":N,...}`
- file: `{"ok":true,"dry_run":true,"method":"sendFile","chat_id":"…","source":"local","type":"…","caption_length":N,...}`
- album: `{"ok":true,"dry_run":true,"method":"sendMediaGroup","chat_id":"…","item_count":N,"types":[...],...}`

Difference in validation: a single-file dry run does NOT stat-check
the local path. An album dry run DOES stat-check local items, so a
missing album path fails fast even in dry run.

## Version

`-v` (`--version`) prints the version: a build-time stamp when
present, otherwise the module version or the VCS revision from the
embedded build info. `--help` (`-h`) prints the usage text; both exit
0.
