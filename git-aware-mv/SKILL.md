---
description: Automatically moves files using git mv for git-tracked files to preserve history, or regular mv for untracked files. Use when moving or renaming files in a git repository.
name: git-aware-mv
title: Git-Aware File Move
recommended: true
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash"]
---

# Git-Aware File Move

Initialize todos tool:

```json
[
  {"content": "Validate parameters", "status": "in_progress", "active_form": "Validating parameters"},
  {"content": "Check git tracking status", "status": "pending", "active_form": "Checking git tracking status"},
  {"content": "Execute file move", "status": "pending", "active_form": "Executing file move"},
  {"content": "Report results", "status": "pending", "active_form": "Reporting results"}
]
```

This skill automatically moves files using git mv for tracked files or regular mv for untracked files.

## Usage

Invoke this skill when you need to move or rename files in a git repository. The skill will:

1. Check if the source file is git-tracked
2. Use `git mv` if tracked (preserves history)
3. Use `mv` if not tracked (standard filesystem move)
4. Create destination directories if needed
5. Handle errors gracefully

## Parameters

The script accepts the following arguments:

- `source` (required, positional): AbsPath to the source file or directory to move
- `destination` (required, positional): AbsPath to the destination
- `--force` (optional): Overwrite existing destination
- `--dry-run` (optional): Preview what would happen without executing
- `--verbose` / `-v` (optional): Show detailed information
- `--json` (optional): Output result as JSON for machine parsing

> Update todos: mark "Validate parameters" as completed, mark "Check git tracking status" as in_progress.

## When to Use

- Moving or renaming any file in a git repository
- Relocating files between directories
- Moving configuration files
- Organizing project structure
- Any file move where git history should be preserved

## Implementation

Execute the entry point script with parameters:

```bash
python3 scripts/git-aware-mv.py <source> <destination> [--force] [--dry-run] [--verbose] [--json]
```

Script outputs JSON with `--json` flag for machine parsing. Fields: `source`, `destination`, `git_tracked`, `command`, `success`, `error`.

> Update todos: mark "Check git tracking status" as completed, mark "Execute file move" as in_progress.

## Examples

### Basic Move

Move a tracked file (uses git mv automatically):

```bash
python3 scripts/git-aware-mv.py plugins/which-key.lua plugins-disabled/which-key.lua
```

### Dry Run

Preview what would happen:

```bash
python3 scripts/git-aware-mv.py plugins/which-key.lua plugins-disabled/which-key.lua --dry-run
```

### Verbose Output

Show detailed information:

```bash
python3 scripts/git-aware-mv.py plugins/which-key.lua plugins-disabled/which-key.lua --verbose
```

### Force Overwrite

Overwrite existing destination:

```bash
python3 scripts/git-aware-mv.py plugins/which-key.lua plugins-disabled/which-key.lua --force
```

### JSON Output

Machine-parseable result:

```bash
python3 scripts/git-aware-mv.py plugins/which-key.lua plugins-disabled/which-key.lua --json
```

> Update todos: mark "Execute file move" as completed, mark "Report results" as in_progress.

## Edge Cases

### File in Staging Area

If the file has staged changes, `git mv` will move both the file and preserve the staged state.

### Renamed but Not Committed

If a file was renamed via `git mv` but not yet committed, another `git mv` will work correctly.

### Untracked File in Git Repo

Files that exist in a git repo but are not tracked (new files, gitignored files) will use regular `mv`.

### Moving Outside Git Repository

If the destination is outside the git repository, `git mv` will fail and fall back to regular `mv`.

### Destination Directory Doesn't Exist

The skill automatically creates the destination directory using `mkdir -p`.

## Benefits Over Manual Execution

- Automatic git tracking detection
- Automatic git history preservation
- No manual command execution required
- Error handling and validation
- Dry-run mode for previewing
- Verbose mode for debugging
- Automatic directory creation
- Force overwrite option
- Clear error messages

## Rationale

- Preserves git history for tracked files
- Enables `git log --follow` to trace file history across renames
- Avoids accidental history loss
- Reduces user error by automating the decision
- Provides safety features (dry-run, verbose, force)

> Update todos: mark "Report results" as completed. Clear todos with `todos([])`.
