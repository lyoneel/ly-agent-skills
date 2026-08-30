# Mode: Album

Send a photo/video album (sendMediaGroup). Load
`../guide-filetypes.md` for item rules and `../guide-formatting.md`
for captions.

## Triggers

album, media group, gallery, multiple photos, photo batch

## Guides

- `../guide-filetypes.md` (item count bounds, mixing rules, coercion,
  caption attachment)
- `../guide-formatting.md` (caption formatting)

## Recipes

Local items (repeated `--album` flags plus trailing positionals):

```bash
python3 scripts/tg_notify.py --album a.jpg b.jpg -c "vacation"
```

URL items:

```bash
python3 scripts/tg_notify.py --album https://x/a.jpg https://x/b.jpg
```

Mixed flag and positional items:

```bash
python3 scripts/tg_notify.py --album a.jpg --album b.jpg c.jpg
```

## Verification Probe

```bash
python3 scripts/tg_notify.py --dry-run --album a.jpg b.jpg -c "cap"
```

Expected: `dry-run: send album (2 items), caption (3 chars)`. Album
dry runs stat-check local items, so a missing path fails here (see
`../gotchas.md` G1).

## Failure Notes

- Item count bounds and the 2-10 style enforcement come from
  `../assets/constant-limits.md`, enforced at send time
- Mixing local paths and URLs in one album is rejected
- Non-photo/video items are coerced to photo
- Success prints `Sent album (N messages)`; `--json` prints
  `{"ok":true,"message_ids":[...]}`
