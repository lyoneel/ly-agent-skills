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

## How Skills Work

- **SKILL.md** is the agent's working memory. Must stay under 5000 tokens so the model can hold the full instructions in context.
- **Frontmatter** (`name`, `description`) tells Crush when to activate the skill. The `description` field is the trigger — it gets matched against the user's request.
- **References** are loaded on-demand. The SKILL.md body acts as a router: it detects the workflow, then reads only the relevant `references/` file. Never load all references at once.
- **Scripts** handle deterministic logic (parsing, validation, structure generation). The skill orchestrates; the script executes. Prefer scripts over LLM reasoning whenever the logic is rigid and repeatable.

## Key Conventions

- SKILL.md body: no emojis, no bold, no italics, no HTML. Code blocks always specify a language. Paths always relative.
- Agent names and skill names use kebab-case.
- `todos` tool tracks progress inside every skill — initialize at the start, update each step, clear on finish.
- When a skill exceeds ~500 lines or handles multiple workflows, split detailed content into `references/` with prefix-based naming: `action-`, `mode-`, `guide-`, `constraint-`.

## Git & Branching

- Default branch: `master`
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)
- GitHub/GitLab are public mirrors — all changes are force-pushed to them from the primary source.
