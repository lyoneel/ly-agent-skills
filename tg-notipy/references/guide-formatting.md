# Formatting Guide

Parse modes for message text and captions. No numeric limits live here;
character bounds come from `../assets/constant-limits.md`.

## Plain Text (default)

An empty parse mode is plain text. For machine-generated notification
text, prefer plain text (omit `--parse-mode`) or HTML; both avoid the
MarkdownV2 escape failures.

## MarkdownV2

Use `--parse-mode MarkdownV2` for full formatting support:

- Bold: `*bold*`
- Italic: `_italic_`
- Underline: `__underline__`
- Strikethrough: `~strikethrough~`
- Inline code: `` `code` ``
- Link: `[text](URL)`
- Blockquote: `> text`

Escape special characters with backslash: `_*[]()~\>#:+-=|{}.!`

Escaping applies to every reserved character, including `-` and `.`.
Telegram rejects the message with HTTP 400 naming the first unescaped
character; see `gotchas.md` G5 for the error shape and recovery.

Example (every reserved character escaped):

```bash
python3 scripts/tg_notify.py \
  --parse-mode MarkdownV2 \
  --message "*Build Success*\n\n_Pipeline_\: CI/CD\n_Branch_\: main\n_Commits_\: 3\n_Status_\: \`passed\`"
```

## HTML

Use `--parse-mode HTML` for HTML formatting:

- Bold: `<b>text</b>`
- Italic: `<i>text</i>`
- Code: `<code>code</code>`
- Link: `<a href="URL">text</a>`

Escape `<`, `>`, and `&` as `&lt;`, `&gt;`, and `&amp;`.
