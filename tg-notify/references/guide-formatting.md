# Guide: Text Formatting (parse modes)

tg-notify passes `--parse-mode` through to the Bot API
`parse_mode` field. Three values exist: empty (plain text, the
default), `MarkdownV2`, and `HTML`. No other parse mode exists;
Telegram rejects anything else with HTTP 400.

## Plain Text (default)

```bash
tg-notify "Build finished at 2026-08-27 14:00"
```

No `--parse-mode` flag. Every character arrives as-is. Use plain text
for machine-generated output with symbols, paths, or error text,
because nothing needs escaping.

## MarkdownV2

```bash
tg-notify --message '*bold* and _italic_' --parse-mode MarkdownV2
```

Entity syntax:

| Entity | Syntax |
|--------|--------|
| bold | `*text*` |
| italic | `_text_` |
| underline | `__text__` |
| strikethrough | `~text~` |
| spoiler | `\|\|text\|\|` |
| inline link | `[text](http://example.com/)` |
| inline code | `` `text` `` |
| code block | triple backticks around a block |
| block quotation | `>` at line start |

Reserved characters: every one of the following must be escaped with a
preceding backslash in all places outside entity syntax: `_`, `*`,
`[`, `]`, `(`, `)`, `~`, backtick, `>`, `#`, `+`, `-`, `=`, `|`, `{`,
`}`, `.`, `!`, and backslash itself. Telegram rejects the message
with HTTP 400 and names the first unescaped character. Inside
`code` and code block entities, only backtick and backslash need
escaping. Inside the `(…)` part of an inline link, only `)` and
backslash need escaping.

Rule of thumb: escape every reserved character in machine-generated
text before sending. A version string like `v1.1.20260825` contains
dots, which are reserved.

## HTML

```bash
tg-notify --message '<b>bold</b> and <i>italic</i>' --parse-mode HTML
```

Supported tags: `b`, `strong`, `i`, `em`, `u`, `ins`, `s`, `strike`,
`del`, `span class="tg-spoiler"`, `tg-spoiler`, `a href`, `code`,
`pre`, `blockquote` (with optional `expandable`), `tg-emoji`,
`tg-time`. Three characters must be replaced with HTML entities when
they are not part of a tag: `<` becomes `&lt;`, `>` becomes `&gt;`,
`&` becomes `&amp;`.

## Recommendation

Use plain text (no flag) for machine-generated text, or HTML when
formatting is required. HTML escaping is three characters, and the
error messages name the problem clearly. MarkdownV2 needs the widest
escaping and is the most error-prone for generated text.
