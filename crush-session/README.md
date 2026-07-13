# crush-session

Agent Skill for managing Crush CLI conversation sessions. Wraps the `crush session` CLI to get the current session ID, rename conversations, list all sessions, inspect session details, and delete sessions by ID. Supports `--json` output for machine-readable results.

## Features

- Get the current session ID and title
- Rename sessions (current or by ID)
- List all sessions
- Show session details
- Delete sessions by ID
- JSON output support for all actions

## Quick Start

All actions are routed through a single Python script:

```bash
python3 scripts/crush-session.py
```

### Get Current Session

```bash
python3 scripts/crush-session.py current
python3 scripts/crush-session.py current --json
```

### Rename Session

```bash
# Rename current session
python3 scripts/crush-session.py rename "New Title"

# Rename a specific session by ID
python3 scripts/crush-session.py rename <id> "New Title"
```

### List Sessions

```bash
python3 scripts/crush-session.py list
python3 scripts/crush-session.py list --json
```

### Show Session Details

```bash
python3 scripts/crush-session.py show
python3 scripts/crush-session.py show <id>
python3 scripts/crush-session.py show <id> --json
```

### Delete Session

```bash
python3 scripts/crush-session.py delete <id>
```

## Technology Stack

- Python 3.10+ (type hints, union syntax)
- Standard library only (json, os, subprocess, sys, pathlib, collections.abc)
- No external dependencies

## Configuration

The script auto-detects the Crush data directory:

1. `$CRUSH_GLOBAL_DATA` env var (highest priority)
2. Project-local `.crush` folder (walks up from cwd)
3. Default Crush data directory

## Notes

- Session IDs accept a UUID, full hash, or hash prefix
- The `--json` flag enables machine-readable output
- Run with no arguments for usage help
- `$CRUSH_SESSION_ID` is only available from within the Crush TUI
