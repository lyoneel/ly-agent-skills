#!/usr/bin/env python3
"""Discover AGENTS.md files from Crush config or fallback defaults."""

import json
import os
import sys
from pathlib import Path


def is_crush_agent() -> bool:
    """Check if crush_info tool is available."""
    return os.environ.get("CRUSH_AVAILABLE") == "true"


def expand_path(path: str) -> str:
    """Expand ~ and environment variables in a path."""
    return os.path.expandvars(os.path.expanduser(path))


def is_home_based(path: str) -> bool:
    """Check if a path is based on $HOME."""
    expanded = expand_path(path)
    home = os.path.expanduser("~")
    return expanded.startswith(home)


def get_crush_config() -> tuple[list[str], str]:
    """Read context_paths and initialize_as from Crush config."""
    config_path = Path.home() / ".config" / "crush" / "crush.json"
    if not config_path.is_file():
        return [], "AGENTS.md"
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        paths = config.get("options", {}).get("context_paths", [])
        filename = config.get("options", {}).get("initialize_as", "AGENTS.md")
        return paths, filename
    except (json.JSONDecodeError, KeyError):
        return [], "AGENTS.md"


def discover(crush: bool, cwd: str) -> dict:
    """Discover agent context files based on priority rules."""
    result = {
        "user_level": [],
        "project_level": [],
        "nonexistent": [],
        "warnings": [],
        "questions": []
    }

    if crush:
        paths, filename = get_crush_config()
        if not paths:
            print("Error: crush detected but context_paths not found", file=sys.stderr)
            sys.exit(1)

        # Priority 1: find files matching initialize_as name
        user_matches = []
        other_user = []
        for path in paths:
            expanded = expand_path(path)
            if is_home_based(path):
                if path.endswith(filename):
                    if os.path.isfile(expanded):
                        user_matches.append(expanded)
                    else:
                        result["nonexistent"].append(path)
                else:
                    if os.path.isfile(expanded):
                        other_user.append({"path": expanded, "name": os.path.basename(expanded)})
                    else:
                        result["nonexistent"].append(path)

        # User-level: prefer initialize_as name matches
        if user_matches:
            result["user_level"] = user_matches
        elif other_user:
            result["user_level"] = [u["path"] for u in other_user]

        # Check for multiple different names at user-level
        all_user_names = set()
        for path in paths:
            if is_home_based(path):
                all_user_names.add(os.path.basename(expand_path(path)))

        has_primary = any(p.endswith(filename) for p in paths if is_home_based(p))

        if len(all_user_names) > 1:
            if has_primary:
                result["questions"].append(
                    f"Multiple context filenames at user level: {sorted(all_user_names)}. "
                    f"Primary is '{filename}' from initialize_as. What is the purpose of each?"
                )
            else:
                result["questions"].append(
                    f"Multiple context filenames at user level: {sorted(all_user_names)}, "
                    f"none matches '{filename}' (initialize_as). Which to use, and what is the purpose of each?"
                )

        # Project-level: check for initialize_as name first, then fallback to AGENTS.md
        project_path = os.path.join(cwd, filename)
        if os.path.isfile(project_path):
            result["project_level"].append(project_path)
        else:
            # Fallback: check for AGENTS.md at project root
            fallback = os.path.join(cwd, "AGENTS.md")
            if os.path.isfile(fallback):
                result["project_level"].append(fallback)
            else:
                result["nonexistent"].append(filename)

        # Consistency check
        if not any(p.endswith(filename) for p in paths):
            result["warnings"].append(
                f"context_paths is missing a user-level path ending with '{filename}' (initialize_as value)"
            )
    else:
        # Fallback: assume AGENTS.md
        home = os.path.expanduser("~")
        user_path = os.path.join(home, ".config", "crush", "AGENTS.md")
        project_path = os.path.join(cwd, "AGENTS.md")
        if os.path.isfile(user_path):
            result["user_level"].append(user_path)
        else:
            result["nonexistent"].append(user_path)
        if os.path.isfile(project_path):
            result["project_level"].append(project_path)
        else:
            result["nonexistent"].append(project_path)

    return result


def main() -> None:
    crush = os.environ.get("CRUSH_AVAILABLE") == "true"
    cwd = os.getcwd()
    result = discover(crush, cwd)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
