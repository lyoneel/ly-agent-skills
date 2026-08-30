# Git Commit Executor

A skill that executes git commits with explicit file control and [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/#specification) message generation. Nothing reaches a commit unless you named it, and nothing else can slip in behind your back.

## Features

- Explicit staging discipline: every file is staged one at a time with `git add <file>`. Directories, globs, and the blanket flags (`git add .`, `git add -A`, `git add --all`, `git commit -a`) are forbidden and rejected by the executor. Whole-folder requests expand to a concrete file list before staging.
- Staged-set equality guard: before committing, the executor compares the staged set against the explicit list and aborts on any mismatch, so out-of-scope staged work can never ride along.
- Conventional Commit messages generated from the resolved change set (type, scope, imperative subject), with the spec referenced in `references/message-format.md`.
- File scopes: staged (default), `all`, `unpushed`, `from <ref>` (hash, title, or content), `skill <name>`, `dir <path>`, each combinable with an explicit file list.
- Repeatable `--exclude <path>` filters and natural-language exclusions ("commit the folder except the templates").
- Automatic splitting of a change set into logical commits, on by default (see Commit Splitting below).
- Safety valves: `message` mode only prints a draft, `--dry-run` stages and verifies without committing, `--push` runs only after a successful commit, and the executor refuses to run while `GIT_INDEX_FILE` is set.

## Commit Splitting

A resolved file list is rarely one commit. By default the skill splits it into logical commits before writing anything, each getting its own message and its own staged-set check:

1. By domain or concern: files touching unrelated features, modules, or domains go into separate commits.
2. By repository: changes spread over multiple repos become one commit per repo, run from each repository root.
3. By content type: docs, code, config, and tests are separated when they are mixed in one request.
4. Never split a skill: all files of a single skill commit as one unit, whatever their count or type.

To keep everything in one commit, say "do not split" or "no split", or pass `--nosplit`:

```text
/commit all --nosplit
```

## Usage

```text
/commit [message] [all|unpushed|from "<ref>"|skill <name>|dir <path>] [--msg "message"] [--push] [--dry-run] [--exclude <path>]... [--files|--] file1 file2 ...
```

## Examples

Commit named files with an explicit message:

```text
/commit --msg "feat(api): add user endpoint" -- src/api.go src/handler.go
```

Commit staged changes with a generated message:

```text
/commit -- src/main.go src/config.go
```

Commit a whole skill folder (expanded to an explicit file list, always one commit):

```text
/commit skill commit
```

Commit a directory except a subfolder:

```text
/commit dir commit --exclude commit/references
```

Commit everything since a given commit, found by hash or by message text:

```text
/commit from abc123 -- internal/core.go
/commit from "feat: add authentication" -- src/auth.go
```

Draft a message without committing:

```text
/commit message all
```

The executor stages each file, verifies the staged set equals the list, commits, and reports the short hash and full message:

```text
Done (`7a3f2e1`):
feat(skills): add defold skill for Defold game engine support

Adds comprehensive skill covering Defold Lua scripts, collections,
game objects, materials, shaders, and project configuration.
```

## Prerequisites

- Git
- Python 3 (stdlib only)

## License

See the project root LICENSE.
