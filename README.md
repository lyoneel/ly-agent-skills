# ly-agent-skills

A curated collection of agent skills, designed and developed using [Crush](https://github.com/charmbracelet/crush) and Qwen3.6 27B.

> **NOTE**: GitHub and GitLab are public mirrors, every change is force-pushed here.

## Skills

- [Agent Loader](agent/README.md) — load custom agent definitions as system prompt overrides (archived, Windsurf-era)
- [AUR Package Analysis](aur-pkg-analysis/README.md) — clean up AUR packages by finding official alternatives and removal commands
- [Gen Agent](gen-agent/README.md) — scaffold new agent definition files with proper structure (archived, legacy, companion of agent-loader)
- [Git-Aware File Move](git-aware-mv/README.md) — move files with git history preservation

## Philosophy

These skills are built to be lean, fast, and reliable. Every design decision serves one goal: make agents better at their jobs.

### Keep SKILL.md Lean

The SKILL.md body is the agent's working memory — kept under 5000 tokens so the model can hold all instructions in context. Heavy content lives in `references/`, `templates/`, `scripts/`, and `assets/` subdirectories, loaded progressively at runtime.

See [CONTRIBUTING](CONTRIBUTING.md) for the full directory structure and naming conventions.

### Scripts

Rigid, repeatable logic belongs in a script, not in the agent's reasoning. Scripts parse, validate, and compute — the skill orchestrates. See [CONTRIBUTING](CONTRIBUTING.md) for details.

### Track Progress

All skills use the `todos` tool to track progress. Todos are initialized at the start, updated as each step completes, and cleared on finish.

### No Fluff

Markdown instructions go straight to the point, no fluff, no prose, just direct
language optimized for agents.

## Contributing

Contributions are welcome via PR, but not guaranteed to be accepted. See [CONTRIBUTING](CONTRIBUTING.md) for details.

## License

MIT
