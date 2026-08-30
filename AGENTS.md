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

The skill inventory lives in the README.md Skills section; keep it current
when adding or removing a skill.

### README Skills Section Format

The Skills section consists of a summary table followed by one overview
section per skill.

Summary table (directly under `## Skills`):

- Three columns: `Skill`, `Description`, `README`.
- Skill column: the folder name, linked to the skill's detail anchor
  (`[<folder-name>](#<folder-name>---<display-name>)`).
- Description column: a one-line, very brief statement of what the skill
  does.
- README column: a single link whose visible text is `DOC`, wrapped in
  literal square brackets with a space inside each bracket, pointing to the
  skill's README: `[ [DOC](<folder-name>/README.md) ]`.

Detail sections (one per skill, after the table):

- Heading is the folder name followed by the display name in brackets:
  `### <folder-name> - [<Display Name>]`.
- Body is the skill's overview paragraph, copied verbatim from the opening
  paragraph of its OWN README.md (the single source of truth). It is not a
  new summary and not the skill's full README content.
- After the overview paragraph, add two links on one line:
  - an up link back to the summary table, with visible brackets and
    spaces: `[ [UP to skills table](#skills-table) ]`;
  - a more-info link to the skill's own README, with visible brackets and
    spaces: `[ [More info in README](<folder-name>/README.md) ]`.
  The table carries an anchor `#skills-table` placed directly under the
  `## Skills` heading.

## Key Conventions

- Paths always relative.
- Skill format and contribution rules: see CONTRIBUTING.md (frontmatter
  shape, sub-5000-token SKILL.md body, no markup in skill markdown, Python
  for scripts, Conventional Commits).

## Git & Branching

- Default branch: `master`
