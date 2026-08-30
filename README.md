# ly-agent-skills

A curated collection of agent skills, designed and developed using [Crush](https://github.com/charmbracelet/crush) and Qwen/DeepSeek models, targeting the 27B Qwen localhosted models.

> **Main repository**: https://gitlab.com/lyoneel/ly-agent-skills.
> If you are reading this on any other host, it is a mirror. Please
> open issues and merge requests on GitLab.

## Skills

<a id="skills-table"></a>

| Skill | Description | README |
|-------|-------------|--------|
| [agent](#agent---agent-loader) | Load and activate custom agent definitions as system prompt overrides (archived, Windsurf-era). | [ [DOC](agent/README.md) ] |
| [agents-md-sync](#agents-md-sync---agents-md-sync) | Audit AGENTS.md files for duplication and correct placement. | [ [DOC](agents-md-sync/README.md) ] |
| [aur-pkg-analysis](#aur-pkg-analysis---aur-package-analysis) | Clean up AUR packages by finding official alternatives and removal commands. | [ [DOC](aur-pkg-analysis/README.md) ] |
| [crush-session](#crush-session---crush-session) | Manage Crush CLI conversation sessions: rename, list, inspect, delete. | [ [DOC](crush-session/README.md) ] |
| [gen-agent](#gen-agent---gen-agent) | Scaffold agent definition files with proper structure (archived, legacy). | [ [DOC](gen-agent/README.md) ] |
| [git-aware-mv](#git-aware-mv---git-aware-file-move) | Move files with git history preserved automatically. | [ [DOC](git-aware-mv/README.md) ] |
| [tg-notify](#tg-notify---tg-notify-cli-reference) | Reference for the tg-notify CLI: messages, files, albums, config. | [ [DOC](tg-notify/README.md) ] |
| [tg-notipy](#tg-notipy---telegram-notify) | Send Telegram messages, files, and albums via the Bot API. | [ [DOC](tg-notipy/README.md) ] |

### agent - [Agent Loader]

Loads and activates a custom agent definition from the `agents` folder as a system prompt override for the session. Originally built for Windsurf, it works in Crush too but was never adapted for it. Kept as an archived reference with one example agent.

[ [UP to skills table](#skills-table) ] [ [More info in README](agent/README.md) ]

### agents-md-sync - [Agents MD Sync]

Runs a three-step audit of AGENTS.md files. It promotes global instructions to user level, detects overlaps between levels, and finds duplicates already defined by enforced skills. Output is suggestions only. The user decides every change.

[ [UP to skills table](#skills-table) ] [ [More info in README](agents-md-sync/README.md) ]

### aur-pkg-analysis - [AUR Package Analysis]

Walks through every installed AUR package one by one. For each package it reports what it does, what depends on it, whether an official alternative exists (Flatpak, official repo, pip, Go, Cargo), whether upstream is maintained, and how to remove it. For periodic system cleanup.

[ [UP to skills table](#skills-table) ] [ [More info in README](aur-pkg-analysis/README.md) ]

### crush-session - [Crush Session]

Wraps the `crush session` CLI to get the current session ID, rename conversations, list all sessions, inspect details, and delete sessions by ID. Supports JSON output for machine-readable results.

[ [UP to skills table](#skills-table) ] [ [More info in README](crush-session/README.md) ]

### gen-agent - [Gen Agent]

Scaffolds new agent definition files with the correct structure and metadata. Guides through name, purpose, constraints, category, role, mission, and output format. Legacy companion to the Agent Loader skill, kept for reference.

[ [UP to skills table](#skills-table) ] [ [More info in README](gen-agent/README.md) ]

### git-aware-mv - [Git-Aware File Move]

Moves files so history is preserved. Uses `git mv` for tracked files and regular `mv` for untracked ones. Includes a Python script with dry-run, verbose, force-overwrite, and JSON output modes.

[ [UP to skills table](#skills-table) ] [ [More info in README](git-aware-mv/README.md) ]

### tg-notify - [tg-notify CLI Reference]

Serves as the reference for the tg-notify command-line tool, a Go CLI that sends Telegram messages, files, and albums. Maps user intent to a mode, loads the mode recipe and its guides, and returns a ready command with a verification probe.

[ [UP to skills table](#skills-table) ] [ [More info in README](tg-notify/README.md) ]

### tg-notipy - [Telegram Notify]

Sends Telegram messages, files, and albums through the Bot API using a stdlib-only Python script. Mirrors the tg-notify CLI surface for the direct Bot API sender lineage.

[ [UP to skills table](#skills-table) ] [ [More info in README](tg-notipy/README.md) ]

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

