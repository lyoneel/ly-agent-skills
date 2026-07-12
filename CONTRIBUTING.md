# Contributing

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

## Scripts Over Logic

Put rigid, repeatable logic in scripts — not in the agent's reasoning. The skill orchestrates; scripts execute. All scripts use Python for cross-platform compatibility.

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

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
