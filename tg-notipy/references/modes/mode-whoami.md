# Mode: Whoami

Print the bot identity (getMe). Use it to check that a token is valid
before any send; it makes one network call. Load
`../guide-config.md` for credential resolution.

## Triggers

whoami, bot identity, getme, validate token, check bot

## Guides

- `../guide-config.md` (token resolution, JSON output)

## Recipes

```bash
python3 scripts/tg_notify.py --whoami
```

Expected text output: `@botname (id: 123456789)`

```bash
python3 scripts/tg_notify.py --whoami --json
```

## Verification Probe

`--whoami` itself is the probe; exit 0 with an identity line means the
token works.

## Failure Notes

- HTTP 401 Unauthorized: the token is invalid or revoked
- `Failed:` with no network: check proxy and base-url settings in
  `../guide-config.md`
