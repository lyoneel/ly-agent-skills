# Mode: Discover

Find a chat ID by polling getUpdates. Load `../guide-config.md` for
credential resolution.

## Triggers

discover, find chat id, who is chatting, get chat id, setup chat

## Guides

- `../guide-config.md` (token resolution, JSON output)

## Workflow

1. Send any message to your bot on Telegram (e.g., `/start` or "test")
2. Wait 5 seconds for Telegram to process the update
3. Run discovery:

```bash
python3 scripts/tg_notify.py --discover-chat-id
```

4. The output is your numeric chat ID
5. Save it to the `TELEGRAM_CHAT_ID` env var

The token comes from `--token` or `TELEGRAM_BOT_TOKEN`.

## Recipes

Skip updates already processed with `--offset` (past update ID, >= 0):

```bash
python3 scripts/tg_notify.py --discover-chat-id --offset 1000 --json
```

## Verification Probe

```bash
python3 scripts/tg_notify.py --discover-chat-id --json
```

Expected: `{"ok":true,"chat_id":N}` on stdout.

## Failure Notes

- Group and channel chat IDs are negative numbers (see
  `../gotchas.md` G10)
- No recent update returns `Failed:` with guidance to message the bot
  first
