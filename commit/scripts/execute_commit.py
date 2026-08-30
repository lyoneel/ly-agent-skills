#!/usr/bin/env python3
"""
Execute explicit git commits with precise file control.
Pure executor: requires an explicit message and an explicit file list.

Stages each listed file explicitly (new/modified files via git add, deletions
via git add -u), verifies the staged set equals the list exactly, then commits.
Directories and globs are rejected: lists must contain explicit files, including
both sides of renames. --dry-run stages and verifies without committing;
--push pushes after a successful commit.
"""

import os
import shlex
import subprocess
import sys
from typing import List, Optional, Tuple

def run_command(cmd: str) -> Tuple[int, str, str]:
    """Execute a shell command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def usage() -> None:
    """Print usage and exit."""
    print("Usage: execute_commit.py --msg <message> [--push] [--dry-run] -- <file1> [file2 ...]", file=sys.stderr)
    sys.exit(1)

def in_git_repo() -> bool:
    """Check whether the current directory is inside a git repository."""
    returncode, _, _ = run_command("git rev-parse --show-toplevel")
    return returncode == 0

def parse_arguments() -> Tuple[Optional[str], List[str], bool, bool]:
    """
    Parse command arguments.
    Returns: (message, files, push, dry_run)
    """
    message = None
    files: List[str] = []
    push = False
    dry_run = False
    separator_seen = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if separator_seen:
            files.append(arg)
            i += 1
        elif arg == "--msg":
            if i + 1 >= len(sys.argv):
                print("Error: --msg requires a message", file=sys.stderr)
                usage()
            message = sys.argv[i + 1]
            i += 2
        elif arg == "--push":
            push = True
            i += 1
        elif arg == "--dry-run":
            dry_run = True
            i += 1
        elif arg == "--":
            separator_seen = True
            i += 1
        else:
            print(f"Error: unknown argument '{arg}'", file=sys.stderr)
            usage()

    return message, files, push, dry_run

def stage_files(files: List[str]) -> Optional[str]:
    """Stage each listed file explicitly; returns an error string on failure."""
    for f in files:
        if os.path.isdir(f):
            return f"directory not accepted: {f} (list explicit files; use the skill or dir scope to expand)"
        if os.path.lexists(f):
            returncode, stdout, stderr = run_command(f"git add -- {shlex.quote(f)}")
            action = "staging"
        else:
            returncode, stdout, stderr = run_command(f"git add -u -- {shlex.quote(f)}")
            action = "deletion staging"
            if returncode != 0 and f in get_staged_set():
                returncode, stdout, stderr = 0, "", ""
        if returncode != 0:
            return f"{action} failed for {f}: {stderr or stdout}"
    return None

def get_staged_set() -> set:
    """Get the set of currently staged paths, including both sides of renames.

    Uses --name-status because --name-only omits the old path of fully
    staged renames (git mv).
    """
    returncode, stdout, _ = run_command("git diff --cached --name-status")
    if returncode != 0:
        return set()
    paths = set()
    for line in stdout.split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        code = parts[0]
        if ("R" in code or "C" in code) and len(parts) == 3:
            paths.update(parts[1:])
        elif len(parts) >= 2:
            paths.add(parts[1])
    return paths

def main() -> None:
    if not in_git_repo():
        print("Error: not inside a git repository", file=sys.stderr)
        sys.exit(1)

    if os.environ.get("GIT_INDEX_FILE"):
        print("Error: GIT_INDEX_FILE is set; this skill commits only through the repository's own index. Unset it and retry.", file=sys.stderr)
        sys.exit(1)

    message, files, push, dry_run = parse_arguments()

    if not message:
        print("Error: --msg is required", file=sys.stderr)
        usage()

    if not files:
        print("Error: at least one file is required after --", file=sys.stderr)
        usage()

    error = stage_files(files)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    expected = set(files)
    staged = get_staged_set()
    missing = sorted(expected - staged)
    extra = sorted(staged - expected)
    if missing:
        print(f"Error: no changes to commit for: {missing}", file=sys.stderr)
        sys.exit(1)
    if extra:
        print(f"Error: staged files outside the explicit list: {extra}", file=sys.stderr)
        print("Unstage them (git restore --staged <file>) or include them in the list.", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        print("DRY RUN: staged and verified, no commit made")
        print(f"Message: {message}")
        print(f"Files ({len(files)}):")
        for f in sorted(files):
            print(f"  - {f}")
        sys.exit(0)

    returncode, stdout, stderr = run_command(f"git commit -m {shlex.quote(message)}")
    if returncode != 0:
        print(f"Commit failed: {stderr or stdout}", file=sys.stderr)
        sys.exit(1)

    _, short_hash, _ = run_command("git rev-parse --short HEAD")
    print(stdout)
    print(f"Committed {short_hash} with {len(files)} file(s)")

    if push:
        returncode, stdout, stderr = run_command("git push")
        if returncode != 0:
            print(f"Push failed: {stderr or stdout}", file=sys.stderr)
            sys.exit(1)
        print("Pushed")
        print(stdout)

if __name__ == "__main__":
    main()
