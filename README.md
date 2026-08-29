# ly-agent-skills

A curated collection of agent skills, designed and developed using [Crush](https://github.com/charmbracelet/crush) and Qwen/DeepSeek models, targeting the 27B Qwen localhosted models.

> **Main repository**: https://gitlab.com/lyoneel/ly-agent-skills.
> If you are reading this on any other host, it is a mirror. Please
> open issues and merge requests on GitLab.

## Skills

- [Agent Loader](agent/README.md) — load custom agent definitions as system prompt overrides (archived, Windsurf-era)
- [Agents MD Sync](agents-md-sync/README.md) — audit AGENTS.md files for duplication and correct placement
- [AUR Package Analysis](aur-pkg-analysis/README.md) — clean up AUR packages by finding official alternatives and removal commands
- [Crush Session](crush-session/README.md) — manage Crush CLI conversation sessions
- [Gen Agent](gen-agent/README.md) — scaffold new agent definition files with proper structure (archived, legacy, companion of agent-loader)
- [Git-Aware File Move](git-aware-mv/README.md) — move files with git history preservation
- [Telegram Notify](tg-notify/README.md) — send messages to Telegram via the Bot API

## Philosophy

These skills are built to be lean, fast, and reliable. Every design decision serves one goal: make agents better at their jobs.

### Lean SKILL.md

Only essential agent configuration lives here - keep it minimal and focused.
Extended definitions live under \`references\` and are loaded on demand.

See [CONTRIBUTING](CONTRIBUTING.md) for full directory structure and naming conventions.

### Scripts

Rigid, repeatable logic belongs in a script, not in the agent's reasoning. Scripts parse, validate, and compute — the skill orchestrates. See [CONTRIBUTING](CONTRIBUTING.md) for details.

### Track Progress

All skills use the `todos` tool to track progress. Todos are initialized at the start, updated as each step completes, and cleared on finish.

### No Fluff

Markdown instructions go straight to the point, no fluff, no prose, just direct
language optimized for agents.

## Harness Compatibility

These skills are designed for Crush, and some of their tools carry over to
other harnesses. The `todos` task tracking is compatible with Codex
CLI/ChatGPT. Other harnesses may work by coincidence but are not targeted:
Claude uses its own `tasklists` tool, which may function but is not
correctly defined for these skills. Compatibility with any other harness is
untested and not guaranteed.

## Contributing

Contributions are welcome via PR, but not guaranteed to be accepted. See [CONTRIBUTING](CONTRIBUTING.md) for details.

## License



## Resources
For reference, see the Crush configuration and agent skill specifications at [Crush config](https://github.com/charmbracelet/crush#agent-skills) and [Agent Skills home](https://agentskills.io/home).

