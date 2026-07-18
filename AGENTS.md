# AGENTS.md

Repository for AI agent skill definitions. The content is Markdown-based instruction files consumed by [Crush](https://github.com/charmbracelet/crush) at runtime — there is no build system, no source code, and no test suite.

## Project Type

Markdown-only repository. Each top-level subdirectory is one skill. Skills are loaded by name into Crush's context window as system prompt extensions.

## Repository Structure

```
skill-name/
  SKILL.md       # YAML frontmatter + step-by-step instructions (the skill)
  README.md      # public-facing summary (consumed by humans / mirrors)
  references/    # detailed guides and workflow docs (loaded progressively)
  templates/     # copyable skeletons and boilerplate
  scripts/       # executable automation (bash, python, etc.)
  assets/        # static data, images, lookup tables
```

Current skills: `agent`, `aur-pkg-analysis`, `gen-agent`, `git-aware-mv`.

## Key Conventions

- Paths always relative.

## Git & Branching

- Default branch: `master`
