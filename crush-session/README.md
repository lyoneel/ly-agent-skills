# Crush Session

Manages Crush CLI conversation sessions. It wraps the `crush session` CLI to get the current session ID, rename conversations, list all sessions, inspect session details, and delete sessions by ID. Supports `--json` output for machine-readable results.

## Features

- Get the current session ID and title
- Rename sessions (current or by ID)
- List all sessions
- Show session details
- Delete sessions by ID
- JSON output for all actions

## Quick Start

All actions route through a single Python script:

```bash
python3 scripts/crush-session.py current
python3 scripts/crush-session.py rename "New Title"
python3 scripts/crush-session.py list
python3 scripts/crush-session.py show <id>
python3 scripts/crush-session.py delete <id>
```

Add `--json` to any command for machine-readable output.

## Configuration

The script auto-detects the Crush data directory in this order:

1. `$CRUSH_GLOBAL_DATA` env var (highest priority)
2. Project-local `.crush` folder (walked up from cwd)
3. Default Crush data directory

## Prerequisites

- Python 3.10+ (stdlib only, no external dependencies)

## Notes

- Session IDs accept a UUID, full hash, or hash prefix
- Run with no arguments for usage help
- `$CRUSH_SESSION_ID` is only available from within the Crush TUI

## License

See the project root LICENSE.