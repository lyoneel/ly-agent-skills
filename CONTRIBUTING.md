# Contributing

Contributions are accepted on a case-by-case basis. Please review the guidelines below before submitting changes.

## Skill Structure

Each skill lives in its own directory at the repo root:

```
skill-name/
  SKILL.md       # main skill file (YAML frontmatter + instructions)
  README.md      # public-facing summary
  references/    # detailed workflows, guides, constraints
  templates/     # reusable skeletons and boilerplate
  scripts/       # executable automation
  assets/        # static data, images, lookup tables
```

## README.md Format

Each skill ships a README.md as its public-facing summary, read by humans
and mirrors rather than loaded at runtime. It must not duplicate SKILL.md
or references content.

Every skill README has this shape, in order:

- H1 title (the skill's display name)
- One overview paragraph directly under the H1, no section heading. It
  explains what the skill does, the problem it solves, and when to use it.
  Written as a single, well-formed paragraph, not a features dump.
- A capability list: `## Features` (bullets of what the skill can do), or
  `## Operations` for mode-routing skills (bullets of its modes/commands)
- `## Prerequisites` -- what must exist before the skill runs
- `## License` -- "See the project root LICENSE."

The overview paragraph is the single source of truth for the main README:
it is copied verbatim into that skill's detail (overview) section under the
summary table, never into the table row. When the paragraph changes, update
the main README copy to stay in sync.

The capability list, `## Prerequisites`, and `## License` are mandatory.
`## Operations` replaces `## Features` only when the skill routes by mode;
mode-routing skills may additionally add `## Guides`:

- `## Guides` -- bullets linking to on-demand `references/` files; link the
  file as a markdown hyperlink with a human-readable label, never as bare
  inline-code paths

Other sections (`## Quick Start`, `## Configuration`, `## Architecture`,
`## Notes`, `## Technology Stack`) are allowed only when they add value to a
human reader without repeating SKILL.md or references content.

Formatting: no HTML or emojis, code blocks always specify a language,
paths relative.

## SKILL.md Format

- YAML frontmatter with `name` and `description`
- Body stays under 5000 tokens
- No emojis, bold, italics, or HTML
- Code blocks always specify a language
- Paths are always relative
- Use `todos` tool for progress tracking

## Frontmatter

```yaml
---
name: skill-name
description: One-line summary. Use when <trigger condition>.
---
```

- `name`: kebab-case identifier
- `description`: tells the agent when to activate the skill

## Splitting Skills

When a skill exceeds 500 lines or handles multiple workflows, split detailed content into `references/` with prefix-based naming (`action-`, `mode-`, `guide-`, `constraint-`). These files are loaded on demand (lazy loading): SKILL.md stays lean, pointing to the reference it needs per step, and the agent reads that file only when the step runs.

## Scripts

Put rigid, repeatable logic in scripts rather than in SKILL.md instructions. The skill orchestrates; scripts execute. All scripts use Python for cross-platform compatibility.

## Contribution Scope

Welcomed without prior discussion:

- New skills following the structure above
- Bug fixes in existing skills
- Documentation improvements

Requires prior discussion via issue:

- Major restructuring
- Changes to core conventions
- New dependencies or tools

## Issue Reporting

Use GitHub issues for bugs and feature requests. Include the following:

- Bug reports: steps to reproduce, expected behaviour, actual behaviour
- Feature requests: the problem it solves, proposed approach, affected skills

## PR Review

PRs are checked against the following before merge:

- Frontmatter has valid `name` and `description`
- SKILL.md stays under 5000 tokens
- Format matches conventions (no emojis, bold, italics, or HTML)
- Scripts use Python
- Commit messages follow Conventional Commits

## Commit Convention

Use [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification):

- `feat:` new skill or feature
- `fix:` bug fix
- `docs:` documentation changes
- `refactor:` skill restructuring
- `chore:` maintenance tasks

## Submitting Changes

1. Fork the repo
2. Create a feature branch
3. Commit with conventional messages
4. Open a PR to `master`

## License

All contributions are submitted under the MIT license.
