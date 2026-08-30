# Mode: Album

Send a photo/video album (sendMediaGroup), 2-10 items.

Load on demand: `references/guide-filetypes.md`,
`references/guide-formatting.md`.

## Decision Flow

1. Items come from repeated `--album` flags, trailing positional
   arguments after `--album`, or any mix of the two.
2. Count 2-10, enforced at send time; a dry run prints any count.
3. Transport: all items local paths, or all URLs. Mixing is rejected.
4. Item type: each item must be a photo or a video; any other detected
   type is coerced to photo.
5. One caption, plus `--parse-mode`, `--reply-to`, `--silent`, attach
   to the first item only. There is no per-item caption flag.
6. Local items are stat-checked before the send, so a missing path
   fails fast.

## Local Album

```bash
tg-notify --album a.jpg --album b.jpg --album c.jpg
tg-notify --album a.jpg b.jpg c.jpg
tg-notify --album a.jpg b.jpg -c "vacation"
```

`-c` is the short form of `--caption`. The caption applies to the
first item only.

## URL Album

```bash
tg-notify --album https://example.com/a.jpg https://example.com/b.jpg
```

Do not mix local paths and URLs in one album.

## Options

```bash
tg-notify --album a.jpg b.jpg --reply-to 42
tg-notify --album a.jpg b.jpg --silent
tg-notify --album a.jpg b.jpg --json   # {"ok":true,"message_ids":[N,N]}
```

## Verification Probe

```bash
tg-notify --dry-run --album a.jpg b.jpg c.jpg
```

Exit 0 and a `dry-run: send album (3 items)` line confirm the item
count and types without sending (G13). Local items are stat-checked,
so use real paths for a true probe.
