# Git-Aware File Move

A skill that automatically moves files using `git mv` for git-tracked files to preserve history, or regular `mv` for untracked files. It handles the decision logic automatically, so there is no need to check tracking status manually.

## Features

- Automatically selects `git mv` or `mv` based on tracking status
- Python script with dry-run, verbose, force-overwrite, and JSON output modes

## Prerequisites

- Python 3 (stdlib only)

## License

See the project root LICENSE.