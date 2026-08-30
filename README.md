# ly-agent-skills

A curated collection of agent skills, designed and developed using [Crush](https://github.com/charmbracelet/crush) and Qwen/DeepSeek models, targeting the 27B Qwen localhosted models.

> **Main repository**: https://gitlab.com/lyoneel/ly-agent-skills.
> If you are reading this on any other host, it is a mirror. Please
> open issues and merge requests on GitLab.

## Philosophy

These skills are built to be lean, fast, and reliable. Every design decision serves one goal: make agents better at their jobs.

- Lean SKILL.md — only essential agent configuration lives here
- Lazy loading — detailed guides and workflows live in `references/` and are loaded on demand, keeping them out of the context window until needed
- Split when needed — skills over 500 lines or handling multiple workflows split details into `references/`
- Scripts — rigid, repeatable logic belongs in a script, not in the agent's reasoning; all scripts are Python for cross-platform compatibility
- Track progress — all skills use the `todos` tool, initialized at start and cleared on finish
- No fluff — markdown instructions go straight to the point, optimized for agents

See [CONTRIBUTING](CONTRIBUTING.md) for full directory structure and naming conventions.

## Skills

<a id="skills-table"></a>

| Skill | Description | README |
|-------|-------------|--------|
| [agent](#agent-loader---agent) | Load and activate custom agent definitions (archived). | [ [DOC](agent/README.md) ] |
| [agents-md-sync](#agents-md-sync---agents-md-sync) | Audit AGENTS.md files for duplication and placement. | [ [DOC](agents-md-sync/README.md) ] |
| [aur-pkg-analysis](#aur-package-analysis---aur-pkg-analysis) | Clean up AUR packages with alternatives and removal commands. | [ [DOC](aur-pkg-analysis/README.md) ] |
| [commit](#git-commit-executor---commit) | Commit files with explicit staging and conventional message generation. | [ [DOC](commit/README.md) ] |
| [crush-session](#crush-session---crush-session) | Manage Crush CLI conversation sessions. | [ [DOC](crush-session/README.md) ] |
| [gen-agent](#gen-agent---gen-agent) | Scaffold agent definition files (legacy, archived). | [ [DOC](gen-agent/README.md) ] |
| [git-aware-mv](#git-aware-file-move---git-aware-mv) | Move files while preserving git history. | [ [DOC](git-aware-mv/README.md) ] |
| [tg-notify](#telegram-bot-notifications-cli---tg-notify) | Send telegram messages using [command line tool written in Go](https://gitlab.com/lyoneel/cli-tg-notify), using Bot API. | [ [DOC](tg-notify/README.md) ] |
| [tg-notipy](#telegram-bot-notifications-python---tg-notipy) | Send telegram messages using a script written in Python, no dependencies, using Bot API. | [ [DOC](tg-notipy/README.md) ] |

### Agent Loader - [agent]

A skill for loading custom agent definitions and activating them as system prompt overrides. Originally designed for Windsurf, it lets you define specialized agent personas in Markdown files and activate them as system prompt overrides for the current session. It can be used in Crush as well, though it was never adapted specifically for it.

[ [UP to skills table](#skills-table) ] [ [More info in README](agent/README.md) ]

### Agents MD Sync - [agents-md-sync]

Audits AGENTS.md files across user-level and project-level to find duplication and misplaced instructions, and reports recommendations for moving them to the right place. It detects three drift patterns: global instructions stuck in project files, overlaps between the two levels, and instructions already covered by enforced skills. All output is suggestions only; the user decides every change.

[ [UP to skills table](#skills-table) ] [ [More info in README](agents-md-sync/README.md) ]

### AUR Package Analysis - [aur-pkg-analysis]

A skill for cleaning up AUR packages on Arch Linux. It walks every installed AUR package one by one and reports what each one does, what depends on it, whether an official alternative exists, and how to remove it. It is meant for periodic system cleanup.

[ [UP to skills table](#skills-table) ] [ [More info in README](aur-pkg-analysis/README.md) ]

### Git Commit Executor - [commit]

A skill for executing git commits with explicit file control and conventional commit message generation. Files are staged one at a time and the executor verifies the staged set equals the explicit list before committing, so out-of-scope work never slips into a commit. It supports scoped resolution (staged, all, unpushed, from a commit ref, a whole skill folder, or a directory), repeatable exclusions, mandatory logical-commit splitting, message-only generation, dry-run, and an optional push after the commit.

[ [UP to skills table](#skills-table) ] [ [More info in README](commit/README.md) ]

### Crush Session - [crush-session]

Manages Crush CLI conversation sessions. It wraps the `crush session` CLI to get the current session ID, rename conversations, list all sessions, inspect session details, and delete sessions by ID. Supports `--json` output for machine-readable results.

[ [UP to skills table](#skills-table) ] [ [More info in README](crush-session/README.md) ]

### Gen Agent - [gen-agent]

A legacy skill for generating new agent definition files with proper structure and metadata. It guides you through creating specialized agent definitions step by step, then generates and validates the file.

[ [UP to skills table](#skills-table) ] [ [More info in README](gen-agent/README.md) ]

### Git-Aware File Move - [git-aware-mv]

A skill that automatically moves files using `git mv` for git-tracked files to preserve history, or regular `mv` for untracked files. It handles the decision logic automatically, so there is no need to check tracking status manually.

[ [UP to skills table](#skills-table) ] [ [More info in README](git-aware-mv/README.md) ]

### Telegram Bot Notifications (CLI) - [tg-notify]

A skill for sending Telegram bot notifications through the [`tg-notify` command-line tool](https://gitlab.com/lyoneel/cli-tg-notify), a Go CLI, using Bot API. It maps user intent to one of six operations (message, file, album, discover, whoami, config), loads the matching mode recipe and its cross-reference guides, and returns a ready command with a verification probe. Use it when composing or debugging tg-notify commands, or sending messages, files, and albums from within Crush. Compared with the [Python sender](../tg-notipy/README.md), the Go CLI adds a few features: shell completion for bash, zsh, and fish, and socks5/socks5h proxy support. Where features overlap, both share the same structure and parameters, so at feature parity the two are interchangeable.

[ [UP to skills table](#skills-table) ] [ [More info in README](tg-notify/README.md) ]

### Telegram Bot Notifications (Python) - [tg-notipy]

A skill for sending Telegram bot notifications through a self-contained Python script (`scripts/tg_notify.py`, stdlib only, no dependencies). It maps user intent to one of its operations, loads the matching mode recipe and its cross-reference guides, and runs the command with a verification probe. Use it when sending messages, files, or albums from Crush to Telegram without installing anything. It is the lighter sibling of the [Go CLI](../tg-notify/README.md): the Go version adds a few features this script lacks, namely shell completion for bash, zsh, and fish, and socks5/socks5h proxy support. Where features overlap, both share the same structure and parameters, so at feature parity the two are interchangeable.

[ [UP to skills table](#skills-table) ] [ [More info in README](tg-notipy/README.md) ]

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

