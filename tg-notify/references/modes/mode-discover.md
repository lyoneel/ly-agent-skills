# Mode: Discover

Find a chat ID from the latest bot update (getUpdates).

Load on demand: `references/guide-config.md`.

## When to Use

Use when the target chat ID is unknown. Precondition: a user must
already have sent the bot a message, so an update exists. If the
update list is empty, open the bot in Telegram, send `/start` and any
message, then retry.

## Basic Discover

```bash
tg-notify --discover-chat-id
```

The token comes from `--token` or `TELEGRAM_BOT_TOKEN`. Plain output
is the numeric chat ID only. Group IDs are negative. Channel posts
also produce updates.

## Offset

```bash
tg-notify --discover-chat-id --offset 100
```

`--offset` skips updates with an ID at or below the given value; it
must be non-negative (G6).

## JSON Output

```bash
tg-notify --discover-chat-id --json
# {"ok":true,"chat_id":N}
```

## Follow-Up

Store the discovered ID in `TELEGRAM_CHAT_ID` and send normally:

```bash
export TELEGRAM_CHAT_ID="<discovered chat id>"
tg-notify "hello"
```

## Verification Probe

A successful discover run is its own probe: exit 0 plus a numeric
chat ID. No message is sent in this mode.
