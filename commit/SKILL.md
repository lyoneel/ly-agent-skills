---
name: commit
description: Execute git commits with explicit file control and conventional message generation. Use when committing files, generating a conventional commit message, or both, including whole-skill and whole-folder commits with optional exclusions, from staged, unpushed, or from-ref changes.
title: Execute git commits
version: "20260830-1"
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash"]
---

# Git Commit Executor

Execute git commits with explicit file specification and conventional commit message generation. Message generation (absorbed from the former commit-msg skill) is a mode of this skill.

## Purpose

This skill ensures safe, intentional commits by requiring explicit file listing. Files are staged explicitly, one file at a time (`git add <file>`, deletions via `git add -u <file>`), never with blanket staging or directory paths, and the executor verifies the staged set equals the explicit list exactly before committing. When no message is supplied, the skill analyzes the resolved change set and generates a conventional commit message per `references/message-format.md`. The `message` mode generates and prints a message without committing. `--push` pushes after a successful commit; `--dry-run` stages and verifies without committing.

## BEGIN EXECUTION IMMEDIATELY

Do not ask the user what they want to do. Start with step 1.

Mandatory: Initialize todos tool before any operation

Create initial todo list with all major workflow steps:

```json
{
  "todos": [
    {"content": "Parse commit arguments", "status": "in_progress", "active_form": "Parsing commit arguments"},
    {"content": "Resolve file list", "status": "pending", "active_form": "Resolving file list"},
    {"content": "Split into logical commits", "status": "pending", "active_form": "Splitting into logical commits"},
    {"content": "Resolve commit messages", "status": "pending", "active_form": "Resolving commit messages"},
    {"content": "Execute git commits", "status": "pending", "active_form": "Executing git commits"},
    {"content": "Report results", "status": "pending", "active_form": "Reporting results"}
  ]
}
```

Update todos after each step: mark completed, set next to in_progress.

### Step 1: Parse Arguments

Examine the command parameters:

- `message`: generate-only mode; resolve files, generate the message, print it, and do not commit
- scope: `all`, `unpushed`, `from <ref>` (commit hash, commit title, or full commit content), `skill <name>` (all changes in a skill folder), or `dir <path>` (all changes in a directory). No scope = default (staged changes)
- Exclusions: items may be excluded in natural language ('except the tests', 'skip SKILL.md') or as explicit paths; each exclusion is resolved to a concrete file or directory path from the resolved list and passed to the resolver as `--exclude <path>` (repeatable)
- `--msg "message"`: commit mode only; use the provided message directly
- `--push`: push after a successful commit
- `--dry-run`: stage and verify, do not commit
- `--files file1 file2 file3` or `-- file1 file2 file3`: explicit file list, combined with any scope's files

> Update todos: mark "Parse commit arguments" as completed, set "Resolve file list" to in_progress.

### Step 2: Resolve the File List

Vague requests define their own boundaries: when the user says "commit changes" without naming a scope, infer the boundary from context (the work just done) and pick the matching scope or an explicit file list. The executor's equality guard then enforces exactly that set.

1. Resolve the scope's files: if a scope is present, from the repository root, run `python3 scripts/generate_message.py <scope> [--exclude <path>]...` and take the `files` value from its JSON output. The `skill <name>` and `dir <path>` scopes expand a whole skill folder or directory into an explicit file list, including both sides of renames; use `skill <name>` when the user names a whole skill and `dir <path>` for any other folder or directory. A folder is never a commit unit: the commit always receives the expanded file list.
2. Resolve exclusions: natural-language exclusions ('commit the folder except the templates') are mapped to concrete file or directory paths from the expanded list and passed as `--exclude <path>` (repeatable). When a term matches several paths, pass all matches. The resolver warns when an `--exclude` path matches nothing; that is a mapping error: re-resolve the term against the expanded list.
3. Combine: the final file list is the union of the scope's files and any explicit list (`--files` or `--`), deduplicated. Scope only, explicit only, or both are all valid.
4. Empty file list: stop with "no changes found"; do not commit.

> Update todos: mark "Resolve file list" as completed, set "Split into logical commits" to in_progress.

### Step 3: Split into Logical Commits (Mandatory)

Commit mode only; message mode produces one message for the resolved set.

After determining the file list, split into logical commits. Splitting is mandatory unless the user explicitly states "do not split" or "no split":

- Split by domain/concern: files touching unrelated features, modules, or domains go into separate commits
- Split by repository: changes across multiple repos are committed separately per repo
- Split by content type: docs, code, config, tests go into separate commits when mixed
- Never split skill changes: when files belong to a single skill (e.g., all under `agent-skills/<skill-name>/`), commit as one unit regardless of file count or change types
- One commit per skill: a skill's changes must be committed together - no partial skill commits across multiple commits
- Exception: if the user explicitly states "do not split", "no split", or `--nosplit`, commit all files as a single unit
- If splitting is warranted (default): create sub-groups of files and proceed through Steps 4-5 for each group independently
- If user requested no split: proceed with all files as a single commit

> Update todos: mark "Split into logical commits" as completed, set "Resolve commit messages" to in_progress.

### Step 4: Resolve the Message

- If `--msg` is provided (commit mode): use that message directly
- Otherwise generate a conventional commit message following `references/message-format.md`: read the actual changes (`git diff -- <file>` for tracked files, file content for new files), choose the type and scope, write the description in imperative mood, and add a body or footers only when they add context
- `scripts/generate_message.py` output includes a deterministic `message` draft (type, scope, subject) that can be used as-is or refined; it is the fallback for non-interactive runs

> Update todos: mark "Resolve commit messages" as completed, set "Execute git commits" to in_progress.

### Step 5: Execute Git Commit

Commit mode, for each commit group, from the repository root:

```bash
python3 scripts/execute_commit.py --msg "<message>" [--push] [--dry-run] -- <file1> <file2>
```

The script preflights the git repository, stages each listed file explicitly, verifies the staged set equals the list exactly (aborts on out-of-scope staged work), and commits. It rejects directories, globs, and unknown arguments. For multi-repo splits, run the script from each affected repository's root; one commit per repo.

Message mode: print the generated message in a code block for review and modification. Do not run execute_commit.py.

Capture the output. Then retrieve the short hash and commit message for reporting.

> Update todos: mark "Execute git commits" as completed, set "Report results" to in_progress.

### Step 6: Report Results

Report the commit result using the output from Step 5. Show the short commit hash (7 chars) and the complete commit message (subject line + body if present). In message mode, the printed message block from Step 5 is the result.

Format:

```text
Done (`<short_hash>`):
<commit_subject_line>

<commit_body_if_any>
```

Example output:

```text
Done (`7a3f2e1`):
feat(skills): add defold skill for Defold game engine support

Adds comprehensive skill covering Defold Lua scripts, collections,
game objects, materials, shaders, and project configuration.
```

- Retrieve the short hash (e.g., `git rev-parse --short HEAD`)
- Retrieve the full message (e.g., `git log -1 --format='%s%n%n%B'`)
- Include the body only if one exists (skip blank body lines)

> Update todos: mark "Report results" as completed. All todos now completed.
> Then output summary of completed todos as text, and pass empty array to clear: `todos([])`.

## Examples

Commit with explicit message and files:

```text
/commit --msg "feat(api): add user endpoint" -- src/api.go src/handler.go
```

Commit with generated message from staged changes:

```text
/commit -- src/main.go src/config.go
```

Commit with generated message from all changes:

```text
/commit all -- src/main.go tests/main_test.go
```

Commit the whole skill (the skill scope expands to an explicit file list):

```text
/commit skill commit
```

Commit the whole folder (the dir scope expands to an explicit file list):

```text
/commit dir commit/scripts
```

Commit the whole folder except a subfolder (exclusions are repeatable paths; natural-language exclusions are resolved to paths first):

```text
/commit dir commit --exclude commit/references
```

Commit from specific commit point (by hash):

```text
/commit from abc123 -- internal/core.go
```

Commit from specific commit point (by title):

```text
/commit from "feat: add authentication" -- src/auth.go
```

Commit from specific commit point (by content):

```text
/commit from "add authentication module with JWT support" -- src/auth.go
```

Generate-only: print the message for staged changes, do not commit:

```text
/commit message
```

Generate-only from all changes:

```text
/commit message all
```

## Syntax Guide

Message must be provided via `--msg` (commit mode) or generated from the resolved changes. Files come from a named scope, an explicit list, or both (combined, deduplicated):

```text
/commit [message] [all|unpushed|from "<ref>"|skill <name>|dir <path>] [--msg "message"] [--push] [--dry-run] [--exclude <path>]... [--files|--] file1 file2 ...
```

The `from <ref>` parameter accepts:

- Commit hash: `from abc123` or `from abc123def456789`
- Commit title: `from "feat: add feature"`
- Commit content: `from "description of what was done in that commit"`

FORBIDDEN: Do not use `git add .`, `git add -A`, `git add --all`, or `git commit -a` patterns. New files MUST be staged explicitly with `git add <file>`. All file lists MUST be explicit or derived from a named scope. Directories and globs are rejected by the executor; whole-folder requests MUST be expanded to file lists first (the skill and dir scopes do this). Committing through an alternate index is FORBIDDEN: never set or honor `GIT_INDEX_FILE` (or any temporary or side index) to route a commit around the staged-set equality guard; the executor aborts while `GIT_INDEX_FILE` is set.

## Safety Guarantees

- No implicit file selection (no `git add .`, `git add -A`, or `git add --all`; new files staged with explicit paths)
- Explicit file listing prevents accidental commits
- A named scope and an explicit list are additive: the final file set is their union, deduplicated
- Staged-set equality guard: the commit proceeds only when the staged set equals the explicit list exactly; out-of-scope staged work aborts the run
- No alternate-index bypass: the executor refuses to run while `GIT_INDEX_FILE` is set, because committing through a side index leaves the repository index stale against the new HEAD and creates phantom staged reverts that a later plain `git commit` would silently execute
- When the equality guard aborts on unrelated staged work, the only permitted resolutions are committing that staged work as its own logical commit or asking the user to unstage or finish it and retry; never unstage user-staged entries without explicit per-entry approval
- Directories and globs are rejected; whole-folder requests resolve to explicit file lists via the skill or dir scope
- `--push` runs only after a successful commit; `--dry-run` stages and verifies without committing
- The `all` scope includes untracked files and is the riskiest scope
- Message mode never commits
- Message generation follows `references/message-format.md` (Conventional Commits v1.0.0)
