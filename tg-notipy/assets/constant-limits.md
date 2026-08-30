# Constant: tg-notipy limits

Telegram Bot API published limits and tg_notify.py defaults. Read by
scripts/tg_constants.py and referenced by the agent prose; never
re-listed elsewhere. Update here only, when the API or script defaults
change.

```text
message_max_chars: 4096
caption_max_chars: 1024
photo_upload_max_mb: 10
other_upload_max_mb: 50
self_hosted_upload_max_mb: 2000
backoff_cap_seconds: 60
default_retries: 60
default_base_wait_seconds: 2
album_min_items: 2
album_max_items: 10
rate_limit_messages_per_second: 30
```

Units: `*_mb` values are megabytes; the loader multiplies by 1024 * 1024
for byte checks. `rate_limit_messages_per_second` is the Telegram
default budget; the script does not enforce it, the server answers 429.

See `../references/guide-filetypes.md`, `../references/guide-retry.md`,
and `../references/gotchas.md` for semantics and decision rules.
