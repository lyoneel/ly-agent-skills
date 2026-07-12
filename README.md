# ly-agent-skills

A curated collection of agent skills, designed and developed using [Crush](https://github.com/charmbracelet/crush) and Qwen3.6 27B.

NOTE: GitHub and GitLab are public mirrors, every change is force-pushed here.

## Skills

- [Agent Loader](agent/README.md) — load custom agent definitions as system prompt overrides (archived, Windsurf-era)
- [AUR Package Analysis](aur-pkg-analysis/README.md) — clean up AUR packages by finding official alternatives and removal commands
- [Gen Agent](gen-agent/README.md) — scaffold new agent definition files with proper structure (archived, legacy, companion of agent-loader)
- [Git-Aware File Move](git-aware-mv/README.md) — move files with git history preservation

## Philosophy

These skills are built to be lean, fast, and reliable. Every design decision serves one goal: make agents better at their jobs.

### Split Complexity

When a skill grows beyond 500 lines or handles multiple distinct workflows, it gets split. Detailed workflows move into `references/` as separate documents (`action-create.md`, `mode-execute.md`). The SKILL.md stays as a router — overview, mode detection, and dispatch — while the heavy logic lives in focused reference files.

If the skill truly orchestrates multiple sub-skills, it coordinates without duplicating their work.

### Keep SKILL.md Lean

The SKILL.md body is the agent's working memory. It suggested size is under 5000 tokens so the model can hold the full instructions in context. Heavy content has a home, but not here:

- `references/` documentation: workflows, guides, constraints, and detailed explanations. Files use prefix-based naming (`action-`, `mode-`, `guide-`, `constraint-`) for quick identification.
- `templates/` reusable structures: YAML frontmatter, markdown skeletons, config boilerplate. Files meant to be copied or adapted, not read for guidance.
- `scripts/` executable automation: entry point scripts and internal modules for deterministic work.
- `assets/` static data: images, lookup tables, and reference data.

Context is loaded progressively. Only the reference needed for the current step is read. This keeps prompts lean and focused.

### Scripts

Scripts do the heavy lifting: If the logic is rigid and repeatable, it belongs in a script, not in the agent's reasoning.

The skill's role is to orchestrate, not to calculate. A script that parses output or validates structure costs nothing to run and never hallucinates. Shift work from the LLM to scripts whenever possible.

All Scripts uses Python for cross-platform compatibility.

### Track Progress

All skills use the `todos` tool to track progress. Todos are initialized at the start, updated as each step completes, and cleared on finish.

### No Fluff

No emojis, bold, italics, or HTML. Code blocks always specify a language. Paths always relative.

## License

MIT
