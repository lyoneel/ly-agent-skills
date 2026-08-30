# Mode: Whoami

Print the bot identity (getMe).

Load on demand: `references/guide-config.md`.

## When to Use

Use to check that a bot token is valid before any send. The call
makes one network request and prints the bot identity: username and
numeric ID.

## Recipe

```bash
tg-notify --whoami
# @botname (id: 123456789)
```

The token comes from `--token` or `TELEGRAM_BOT_TOKEN`.

## JSON Output

```bash
tg-notify --whoami --json
# {"ok":true,"id":N,"is_bot":true,"first_name":"…","username":"…"}
```

## Notes

- Dry run does not apply here: whoami validates the token with a real
  getMe call. Run it only with a token the user expects to use.
- Exit 0 confirms the token works; exit 1 with an API error on stderr
  names the problem.

## Verification Probe

The whoami call is its own probe: exit 0 plus the identity line.
