---
name: crush-session
description: Manage Crush sessions - rename, list, inspect, and delete conversations. Use when organizing or navigating Crush session history.
recommended: true
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash"]
---

Initialize todos for crush-session operation:

```json
{
  "todos": [
    {"content": "Initialize crush-session operation", "status": "in_progress", "active_form": "Initializing crush-session operation"},
    {"content": "Detect requested action and execute", "status": "pending", "active_form": "Detecting action and executing"},
    {"content": "Complete crush-session operation", "status": "pending", "active_form": "Completing crush-session operation"}
  ]
}
```

> Update todos: mark "Initialize crush-session operation" as completed, mark "Detect requested action and execute" as in_progress.

# Crush Session Management

Manage Crush CLI sessions: get the current session ID, rename, list, show details, or delete sessions.

## Entry Point

All actions are routed through a single script. Grant execute permission once:

```bash
python3 scripts/crush-session.py
```

## Actions

Detect the user's intent and execute the matching action:

- `current` - show the current session ID and title
- `rename` - rename the current or a specific session
- `list` - list all sessions
- `show` - show details of a specific session
- `delete` - delete a session by ID

All actions support `--json` for machine-readable output.

BEGIN EXECUTION IMMEDIATELY. Do not ask the user what they want to do. Start with step 1:

1. Detect the action from the user's request.

> Update todos: mark "Detect requested action and execute" as in_progress.

2. Execute the corresponding workflow below.

> Update todos: mark "Complete crush-session operation" as in_progress.

3. Report the result.

> Update todos: mark "Complete crush-session operation" as completed. Clear todos with `todos([])`.

## Workflow: Get Current Session

```bash
scripts/crush-session.py current
```

If the title is `null`, the session has not been renamed yet.

```bash
scripts/crush-session.py current --json
```

## Workflow: Rename Session

```bash
# Rename current session
scripts/crush-session.py rename "New Title"

# Rename a specific session by ID
scripts/crush-session.py rename <id> "New Title"

# Machine-readable output
scripts/crush-session.py rename <id> "New Title" --json
```

## Workflow: List Sessions

```bash
# Human-readable list
scripts/crush-session.py list

# Machine-readable JSON
scripts/crush-session.py list --json
```

## Workflow: Show Session Details

```bash
# Show current session
scripts/crush-session.py show

# Show specific session
scripts/crush-session.py show <id>

# Machine-readable output
scripts/crush-session.py show <id> --json
```

## Workflow: Delete Session

```bash
scripts/crush-session.py delete <id>
```

Confirm the session ID before deleting. If the user wants to delete the current session, warn them first.

## Tips

- Run the script with no arguments for usage help.
- Session IDs accept a UUID, full hash, or hash prefix (e.g., `96fd792644642c54`).
- The `$CRUSH_SESSION_ID` env var is only available from within the Crush TUI.
