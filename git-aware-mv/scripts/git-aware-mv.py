#!/usr/bin/env python3
"""Git-aware file move: uses git mv for tracked files, regular mv for untracked."""

import argparse
import json
import os
import shutil
import subprocess
import sys


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
    )
    return result.returncode == 0


def is_git_tracked(path: str) -> bool:
    """Check if a path is tracked by git."""
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        capture_output=True,
    )
    return result.returncode == 0


def validate_params(source: str, destination: str) -> list[str]:
    """Validate source and destination parameters. Return list of errors."""
    errors = []
    if not source:
        errors.append("Source is required")
    if not destination:
        errors.append("Destination is required")
    if source and not os.path.exists(source):
        errors.append(f"Source '{source}' does not exist")
    if destination and os.path.exists(destination):
        errors.append(f"Destination '{destination}' already exists (use --force to overwrite)")
    return errors


def move_file(
    source: str,
    destination: str,
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    """Move a file, using git mv for tracked files."""
    result = {
        "source": source,
        "destination": destination,
        "git_tracked": False,
        "command": "",
        "success": False,
        "error": "",
    }

    # Validate
    errors = validate_params(source, destination)
    if errors:
        result["error"] = "; ".join(errors)
        return result

    # Create destination directory if needed
    dest_dir = os.path.dirname(destination)
    if dest_dir and not os.path.isdir(dest_dir):
        if verbose:
            print(f"Creating destination directory: {dest_dir}")
        os.makedirs(dest_dir, exist_ok=True)

    # Determine move method
    in_git_repo = is_git_repo()
    if in_git_repo and is_git_tracked(source):
        result["git_tracked"] = True
        command = ["git", "mv", source, destination]
    else:
        if in_git_repo and verbose:
            print("Info: Source is not git-tracked, using regular mv")
        command = ["mv", source, destination]

    result["command"] = " ".join(command)

    if verbose:
        print(f"Source: {source}")
        print(f"Destination: {destination}")
        print(f"Git tracked: {result['git_tracked']}")
        print(f"Command: {result['command']}")

    if dry_run:
        print(f"[DRY-RUN] Would execute: {result['command']}")
        result["success"] = True
        return result

    # Execute
    if force and os.path.exists(destination):
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        else:
            os.remove(destination)

    try:
        if result["git_tracked"]:
            subprocess.run(command, check=True)
        else:
            shutil.move(source, destination)
        result["success"] = True
        if verbose:
            print("Success: File moved successfully")
    except subprocess.CalledProcessError as e:
        result["error"] = f"git mv failed: {e.stderr.decode() if e.stderr else str(e)}"
    except Exception as e:
        result["error"] = str(e)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Git-aware file move")
    parser.add_argument("source", help="Source file or directory path")
    parser.add_argument("destination", help="Destination path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing destination")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    result = move_file(
        source=args.source,
        destination=args.destination,
        force=args.force,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(result, indent=2))

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
