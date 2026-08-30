# Agents MD Sync

Audits AGENTS.md files across user-level and project-level to find duplication and misplaced instructions, and reports recommendations for moving them to the right place. It detects three drift patterns: global instructions stuck in project files, overlaps between the two levels, and instructions already covered by enforced skills. All output is suggestions only; the user decides every change.

## Features

- Three-step audit: promote to user level, detect overlaps, find skill duplicates
- File discovery via Crush config with filesystem fallback
- Suggestions-only output, no automatic changes
- Structured JSON output from the discovery engine for machine parsing
- Progress tracking via the `todos` tool

## Architecture

- `scripts/discover.py` -- resolves user-level and project-level AGENTS.md paths (Python 3, stdlib only)
- `SKILL.md` -- runs the three-step audit after discovery

## Prerequisites

- At least one AGENTS.md file (user-level or project-level)
- No external dependencies; the discovery script uses Python stdlib only

## License

See the project root LICENSE.