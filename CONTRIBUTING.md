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

When a skill exceeds 500 lines or handles multiple workflows, split detailed content into `references/` with prefix-based naming (`action-`, `mode-`, `guide-`, `constraint-`).

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

Use [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

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
