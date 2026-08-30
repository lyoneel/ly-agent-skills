#!/usr/bin/env python3
"""
Generate conventional commit messages from git changes.
Supports multiple analysis modes: default (staged + unstaged), all, unpushed, from, skill, dir.
All scopes accept repeatable --exclude <path> filters (exact file or directory prefix).
"""

import subprocess
import sys
import json
import os
import shlex
from pathlib import Path
from typing import Dict, List, Set, Tuple

def run_command(cmd: str) -> str:
    """Execute a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        return ""

def get_staged_changes() -> List[str]:
    """Get list of staged files, including both sides of renames."""
    output = run_command("git diff --cached --name-status")
    files = []
    for line in output.split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        code = parts[0]
        if ("R" in code or "C" in code) and len(parts) == 3:
            files.extend(parts[1:])
        elif len(parts) >= 2:
            files.append(parts[1])
    return files

def get_unstaged_changes() -> List[str]:
    """Get list of unstaged modified files."""
    output = run_command("git diff --name-only")
    return output.split("\n") if output else []

def get_untracked_files() -> List[str]:
    """Get list of untracked files."""
    output = run_command("git ls-files --others --exclude-standard")
    return output.split("\n") if output else []

def get_all_changes() -> List[str]:
    """Get all changes: staged, unstaged, and untracked."""
    staged = get_staged_changes()
    unstaged = get_unstaged_changes()
    untracked = get_untracked_files()
    combined = set(f for f in staged + unstaged + untracked if f)
    return sorted(list(combined))

def get_path_changes(path: str) -> List[str]:
    """Get all changed files under a path as an explicit list (staged, unstaged, untracked).

    Rename and copy entries contribute both the old and the new path so the
    executor can stage both sides. Uses a direct subprocess call (no shell, no
    stdout strip) because porcelain lines for unstaged changes start with a
    required leading space.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-uall", "--", path],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error listing changes for {path}: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    files = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        code = line[:2]
        target = line[3:]
        if ("R" in code or "C" in code) and " -> " in target:
            old, _, new = target.partition(" -> ")
            files.extend([p.strip('"') for p in (old, new) if p])
        else:
            files.append(target.strip('"'))
    return files

def parse_excludes(args: List[str]) -> Tuple[List[str], List[str]]:
    """Split argv into --exclude paths and the remaining scope arguments."""
    excludes = []
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--exclude":
            if i + 1 >= len(args):
                print("Error: --exclude requires a path", file=sys.stderr)
                sys.exit(1)
            excludes.append(args[i + 1])
            i += 2
        else:
            remaining.append(args[i])
            i += 1
    return excludes, remaining

def is_excluded(file: str, excludes: List[str]) -> bool:
    """True when a file is an excluded path or lives under an excluded directory."""
    return any(file == e or file.startswith(e + "/") for e in excludes)

def apply_excludes(files: List[str], excludes: List[str]) -> List[str]:
    """Drop excluded files from a resolved list; warn when an exclusion matches nothing."""
    if not excludes:
        return files
    normalized = [e.rstrip("/") for e in excludes]
    for e in normalized:
        if not any(is_excluded(f, [e]) for f in files):
            print(f"Warning: --exclude matched nothing: {e}", file=sys.stderr)
    return [f for f in files if not is_excluded(f, normalized)]

def get_unpushed_changes() -> List[str]:
    """Get files changed in unpushed commits."""
    try:
        branch = run_command("git rev-parse --abbrev-ref HEAD")
        if not branch or branch == "HEAD":
            return []
        
        merge_base = run_command(f"git merge-base {branch} origin/{branch} 2>/dev/null || echo {branch}")
        output = run_command(f"git diff {merge_base}..HEAD --name-only")
        return output.split("\n") if output else []
    except Exception:
        return []

def is_valid_commit_hash(ref: str) -> bool:
    """Check if the reference is a valid commit hash."""
    # Try to resolve it as a git object
    output = run_command(f"git rev-parse --verify {shlex.quote(ref)}^ 2>/dev/null || echo ''")
    return bool(output) or run_command(f"git rev-parse --verify {shlex.quote(ref)} 2>/dev/null") != ""

def find_commit_by_message(search_term: str) -> str:
    """Find commit hash by commit message (title or content)."""
    # First try to find by exact/partial title match
    output = run_command(f"git log --oneline --all -i --grep={shlex.quote(search_term)} | head -1")
    if output:
        parts = output.split(" ", 1)
        return parts[0]
    
    # Try to find by commit message content (search in full message)
    output = run_command(f"git log --all --oneline --grep={shlex.quote(search_term)} 2>/dev/null | head -1")
    if output:
        parts = output.split(" ", 1)
        return parts[0]
    
    # Try more flexible search by looking at all commits
    cmd = f"git log --all --pretty=format:'%H %s %b' | grep -i {shlex.quote(search_term)} | head -1"
    output = run_command(cmd)
    if output:
        parts = output.split()
        return parts[0] if parts else ""
    
    return ""

def get_changes_from_hash(commit_hash: str) -> List[str]:
    """Get files changed since a specific commit."""
    output = run_command(f"git diff {commit_hash}..HEAD --name-only")
    return output.split("\n") if output else []

def categorize_files(files: List[str]) -> Dict[str, List[str]]:
    """Categorize files by type."""
    categories = {
        "src": [],
        "test": [],
        "docs": [],
        "config": [],
        "other": []
    }
    
    for f in files:
        if not f:
            continue
        
        if "test" in f.lower() or "_test" in f or ".test." in f:
            categories["test"].append(f)
        elif f.endswith((".md", ".txt", ".rst")):
            categories["docs"].append(f)
        elif f.endswith((".yml", ".yaml", ".json", ".toml", ".config")):
            categories["config"].append(f)
        else:
            categories["src"].append(f)
    
    return categories

def extract_scope(files: List[str]) -> str:
    """Extract common scope/module from files."""
    if not files:
        return ""
    
    # Try to find common directory prefix
    paths = [Path(f).parts for f in files]
    if not paths:
        return ""
    
    common_parts = []
    for parts in zip(*paths):
        if len(set(parts)) == 1:
            common_parts.append(parts[0])
        else:
            break
    
    if common_parts:
        scope = "/".join(common_parts)
        # Limit scope length
        return scope[:20] if len(scope) <= 20 else ""
    
    return ""

def get_change_type(files: List[str]) -> Tuple[str, str]:
    """Determine commit type and scope."""
    categories = categorize_files(files)
    
    # Determine type based on categories
    if categories["src"]:
        commit_type = "feat"  # Default to feature, could be refined
        scope = extract_scope(categories["src"])
    elif categories["test"]:
        commit_type = "test"
        scope = extract_scope(categories["test"])
    elif categories["docs"]:
        commit_type = "docs"
        scope = ""
    elif categories["config"]:
        commit_type = "chore"
        scope = "config"
    else:
        commit_type = "chore"
        scope = ""
    
    return commit_type, scope

def generate_subject(files: List[str], commit_type: str) -> str:
    """Generate commit subject line."""
    categories = categorize_files(files)
    
    file_count = len([f for f in files if f])
    
    if commit_type == "feat":
        if file_count == 1:
            module = Path(files[0]).stem.replace("_", " ")
            return f"add {module} functionality"
        else:
            return "add new features"
    elif commit_type == "fix":
        return "fix issues"
    elif commit_type == "test":
        return "add tests"
    elif commit_type == "docs":
        return "update documentation"
    elif commit_type == "style":
        return "format code"
    elif commit_type == "refactor":
        return "refactor code"
    elif commit_type == "perf":
        return "improve performance"
    elif commit_type == "chore":
        return "update dependencies"
    else:
        return "update code"

def generate_commit_message(files: List[str]) -> str:
    """Generate a full conventional commit message."""
    if not files or all(not f for f in files):
        return "chore: update files"
    
    # Clean up file list
    files = [f for f in files if f]
    
    # Determine type and scope
    commit_type, scope = get_change_type(files)
    
    # Generate subject
    subject = generate_subject(files, commit_type)
    
    # Build message
    if scope:
        message = f"{commit_type}({scope}): {subject}"
    else:
        message = f"{commit_type}: {subject}"
    
    # Add body if multiple files
    if len(files) > 3:
        message += f"\n\nChanges:\n"
        categories = categorize_files(files)
        for category, category_files in categories.items():
            if category_files:
                message += f"\n{category.title()}:\n"
                for f in category_files[:5]:  # Limit to first 5
                    message += f"  - {f}\n"
                if len(category_files) > 5:
                    message += f"  ... and {len(category_files) - 5} more\n"
    
    return message

def main():
    """Main entry point."""
    mode = "staged-unstaged"
    files = []
    excludes, argv = parse_excludes(sys.argv[1:])
    
    if len(argv) < 1:
        # Default: use staged and unstaged changes
        files = get_staged_changes() + get_unstaged_changes()
        mode = "staged-unstaged"
    else:
        mode_arg = argv[0].lower()
        
        if mode_arg == "all":
            files = get_all_changes()
            mode = "all"
        elif mode_arg == "skill":
            mode = "skill"
            if len(argv) < 2:
                print("Error: 'skill' scope requires a skill name", file=sys.stderr)
                sys.exit(1)
            skill_dir = Path(argv[1])
            if not (skill_dir / "SKILL.md").is_file():
                print(f"Error: not a skill folder: {skill_dir} (missing SKILL.md)", file=sys.stderr)
                sys.exit(1)
            files = get_path_changes(str(skill_dir))
        elif mode_arg == "dir":
            mode = "dir"
            if len(argv) < 2:
                print("Error: 'dir' scope requires a path", file=sys.stderr)
                sys.exit(1)
            dir_path = Path(argv[1])
            if not dir_path.is_dir():
                print(f"Error: directory not found: {dir_path}", file=sys.stderr)
                sys.exit(1)
            files = get_path_changes(str(dir_path))
        elif mode_arg == "unpushed":
            files = get_unpushed_changes()
            mode = "unpushed"
        elif mode_arg == "from":
            # Handle "from" mode with hash, title, or content
            mode = "from"
            if len(argv) < 2:
                print("Error: 'from' mode requires a commit hash or message", file=sys.stderr)
                sys.exit(1)
            
            commit_ref = " ".join(argv[1:])  # Join remaining args for message search
            
            # Try as hash first (most specific)
            if is_valid_commit_hash(commit_ref):
                files = get_changes_from_hash(commit_ref)
            else:
                # Try as commit message (title or content)
                commit_hash = find_commit_by_message(commit_ref)
                if commit_hash:
                    files = get_changes_from_hash(commit_hash)
                else:
                    print(f"Error: Could not find commit matching '{commit_ref}'", file=sys.stderr)
                    sys.exit(1)
        else:
            # Default to staged + unstaged
            files = get_staged_changes() + get_unstaged_changes()
    
    # Clean and deduplicate
    files = [f for f in files if f]
    files = list(dict.fromkeys(files))  # Remove duplicates while preserving order
    files = apply_excludes(files, excludes)
    
    if not files:
        print("No changes found", file=sys.stderr)
        sys.exit(1)
    
    # Generate message
    message = generate_commit_message(files)
    
    # Output as JSON for skill integration
    output = {
        "message": message,
        "files": files,
        "mode": mode,
        "file_count": len(files)
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
