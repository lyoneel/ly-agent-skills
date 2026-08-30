# Mode: Config

Environment setup, proxy, self-hosted base URL, shell completion, and
config probes.

Load on demand: `references/guide-config.md`,
`references/guide-retry.md`.

## Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="<bot token>"
export TELEGRAM_CHAT_ID="<chat id>"
```

Use placeholder values in recipes; never write a real token or chat
ID into a file. Flags override these variables, and the environment
overrides the `./.env` file (guide-config.md).

## .env File

A `./.env` file in the working directory fills variables that the
environment has not already set. Format: one `KEY=VALUE` per line;
blank lines and `#` comment lines are skipped.

```text
TELEGRAM_BOT_TOKEN=<bot token>
TELEGRAM_CHAT_ID=<chat id>
```

## Proxy

```bash
tg-notify --proxy http://proxy.example.com:8080 "hello"
tg-notify --proxy socks5://proxy.example.com:1080 "hello"
tg-notify --proxy socks5h://proxy.example.com:1080 "hello"
```

`socks5` and `socks5h` behave identically (G14). Read
guide-retry.md before testing through a broken proxy: a refused
connection is a transient error and retries up to 60 times unless
`--no-retry` is set.

## Self-Hosted Base URL

```bash
tg-notify --base-url https://bot-api.example.com:8081 "hello"
```

The 2000 MB client-side upload limit applies only with the `--base-url`
flag; `TELEGRAM_BASE_URL` alone keeps the official 10/50 MB local
check (guide-filetypes.md).

## Shell Completion

```bash
tg-notify --completion bash
tg-notify --completion zsh
tg-notify --completion fish
```

Each prints a completion script for the named shell and exits 0. An
unsupported shell name exits 1.

## Verification Probes

Both probes need a resolvable token and chat ID (presence only, not
validated, for dry run):

```bash
tg-notify --dry-run "ping"
```

Exit 0 plus a dry-run line confirms the config resolves, without any
network call (G13).

```bash
tg-notify --whoami
```

Exit 0 confirms the token is valid. This makes a network call; run it
only with a token the user expects to use.
