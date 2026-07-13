#!/usr/bin/env python3
"""Manage Crush CLI sessions from the command line."""

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


SCRIPT = Path(__file__).resolve()
SKILL_DIR = SCRIPT.parent
CRUSH = ["crush"]

# Resolve the Crush data directory.
# Priority: explicit env var > project .crush folder > default.
def _resolve_data_dir() -> Path | None:
    explicit = os.environ.get("CRUSH_GLOBAL_DATA")
    if explicit:
        return Path(explicit)
    # Check for project-local .crush folder walking up from cwd.
    for ancestor in [Path.cwd(), *Path.cwd().parents]:
        candidate = ancestor / ".crush"
        if candidate.is_dir():
            return candidate
    return None


_data_dir = _resolve_data_dir()
if _data_dir:
    CRUSH += ["--data-dir", str(_data_dir)]


def run(args: list[str], capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a Crush CLI subcommand."""
    return subprocess.run(
        CRUSH + args,
        capture_output=capture,
        text=True,
        check=True,
    )


def last_session() -> dict:
    """Return the latest session metadata."""
    result = run(["session", "last", "--json"])
    return json.loads(result.stdout)


def action_current(args: list[str]) -> None:
    if "--json" in args:
        print(json.dumps(last_session(), indent=2))
        return
    session = last_session()
    meta = session.get("meta", session)
    sid = meta.get("id", "unknown")
    title = meta.get("title") or "null"
    print(f"ID:    {sid}")
    print(f"Title: {title}")


def action_rename(args: list[str]) -> None:
    if len(args) == 1:
        session = last_session()
        meta = session.get("meta", session)
        sid = meta.get("id")
        run(["session", "rename", sid, args[0]])
        print(f"Renamed session {sid} to: {args[0]}")
    elif len(args) == 2:
        cmd = ["session", "rename", args[0], args[1]]
        if "--json" in args:
            cmd.append("--json")
            result = run(cmd)
            print(result.stdout, end="")
            return
        run(cmd)
        print(f"Renamed session {args[0]} to: {args[1]}")
    elif len(args) == 3 and "--json" in args:
        non_flag = [a for a in args if a != "--json"]
        if len(non_flag) == 2:
            run(["session", "rename", non_flag[0], non_flag[1], "--json"])
            return
    else:
        print("Usage: crush-session.py rename [id] <title> [--json]", file=sys.stderr)
        sys.exit(1)


def action_list(args: list[str]) -> None:
    cmd = ["session", "list"]
    if "--json" in args:
        cmd.append("--json")
    result = run(cmd)
    print(result.stdout, end="")


def action_show(args: list[str]) -> None:
    use_json = "--json" in args
    non_flag = [a for a in args if a != "--json"]
    sid = non_flag[0] if non_flag else None
    if not sid:
        session = last_session()
        meta = session.get("meta", session)
        sid = meta.get("id")
    cmd = ["session", "show", sid]
    if use_json:
        cmd.append("--json")
    result = run(cmd)
    print(result.stdout, end="")


def action_delete(args: list[str]) -> None:
    if len(args) < 1 or len(args) > 2:
        print("Usage: crush-session.py delete <id> [--json]", file=sys.stderr)
        sys.exit(1)
    use_json = "--json" in args
    sid = [a for a in args if a != "--json"][0]
    cmd = ["session", "delete", sid]
    if use_json:
        cmd.append("--json")
    result = run(cmd)
    if use_json:
        print(result.stdout, end="")
    else:
        print(f"Deleted session {sid}")


USAGE = """\
Usage: crush-session.py <action> [args...]

Actions:
  current [--json]       Show current session ID and title
  rename <title>         Rename the current session
  rename <id> <title>    Rename a specific session
  list [--json]          List all sessions
  show [id] [--json]     Show session details (defaults to current)
  delete <id> [--json]   Delete a session by ID

Notes:
  IDs can be a UUID, full hash, or hash prefix.

Examples:
  crush-session.py current --json
  crush-session.py rename "Installer Refactor"
  crush-session.py rename abc123 "Old Session"
  crush-session.py list --json
  crush-session.py show 67f94115aa19 --json
  crush-session.py delete 85590ccb-5ff3-44a9-b1f6
"""


def main() -> None:
    if len(sys.argv) < 2:
        print(USAGE)
        return

    action = sys.argv[1]
    rest = sys.argv[2:]

    actions: dict[str, Callable[..., None]] = {
        "current": action_current,
        "rename": action_rename,
        "list": action_list,
        "show": action_show,
        "delete": action_delete,
    }

    handler = actions.get(action)
    if handler is None:
        print(f"Unknown action: {action}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    handler(rest)  # type: ignore[operator]


if __name__ == "__main__":
    main()
