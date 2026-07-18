# agents-md-sync

Audit AGENTS.md files for duplication and correct placement. This skill automates the review of user-level and project-level agent instruction files, identifying redundancies, misplaced conventions, and content already defined by enforced skills. All output is recommendations only — the user decides on every change.

## Overview

AI agents use AGENTS.md files at two levels:

- User-level — global conventions, writing style, formatting preferences, and tooling standards that apply across all projects
- Project-level — project-specific instructions, workflows, folder conventions, and domain-specific rules

Over time, these files drift apart. General conventions end up duplicated in every project. Project-specific rules leak into the user-level file. Instructions that belong in skills are copied into AGENTS.md as manual overrides. This skill detects all three drift patterns and recommends corrective action.

The skill runs a three-step audit pipeline:

1. Promote — finds global instructions in project-level files that belong at user-level
2. Overlap — detects duplicate or equivalent instructions between user-level and project-level
3. Skill duplicates — identifies AGENTS.md instructions already defined by enforced skills

## Features

- Three-step audit pipeline with systematic, sequential analysis
- File discovery via Crush config (`context_paths`, `initialize_as`) with filesystem fallback
- Interactive resolution when file detection is ambiguous or files are missing
- Consolidation engine that merges fragmented instructions into single recommendations
- Skill cross-reference against enforced skills (gen-skill, planner, commit)
- Suggestions-only output — no automatic changes, user retains full control
- Structured JSON output from discovery engine for machine parsing
- Progress tracking via `todos` tool during audit

## Architecture

```
agents-md-sync/
├── SKILL.md              # Execution logic and 3-step audit workflow
├── README.md             # This file
├── .gitignore            # Python and IDE artifacts
└── scripts/
    └── discover.py       # File discovery engine (Python 3, stdlib only)
```

### Discovery Engine (`scripts/discover.py`)

Resolves AGENTS.md file locations using a priority-based algorithm. It is the first component to run during any audit and provides the file paths needed for subsequent steps.

Discovery algorithm:

1. Checks `CRUSH_AVAILABLE` environment variable to determine if Crush is active
2. If Crush is active:
   - Reads `~/.config/crush/crush.json` for `context_paths` and `initialize_as`
   - Matches context paths against `initialize_as` filename (primary match)
   - Falls back to any home-based context path if no primary match
   - Detects project-level file by checking for `initialize_as` name at repo root, then falling back to `AGENTS.md`
3. If Crush is not active:
   - Uses default user-level path: `~/.config/crush/AGENTS.md`
   - Uses default project-level path: `<cwd>/AGENTS.md`
4. Outputs structured JSON with all findings

JSON output schema:

```json
{
  "user_level": ["/absolute/path/to/user/AGENTS.md"],
  "project_level": ["/absolute/path/to/project/AGENTS.md"],
  "nonexistent": ["/path/that/was/not/found"],
  "warnings": ["context_paths is missing a user-level path ending with 'AGENTS.md'"],
  "questions": ["Multiple context filenames at user level: ['AGENTS.md', 'INSTRUCTIONS.md']. Which to use?"]
}
```

Field descriptions:

- `user_level` — list of resolved user-level AGENTS.md absolute paths
- `project_level` — list of resolved project-level AGENTS.md absolute paths
- `nonexistent` — paths that were expected but not found on disk
- `warnings` — non-blocking issues detected during discovery
- `questions` — prompts requiring user clarification before proceeding

### Audit Pipeline (`SKILL.md`)

Three sequential analysis steps run after discovery resolves file paths. Each step produces a markdown table of recommendations and a count for the final summary.

| Step | Purpose | Input | Output |
|------|---------|-------|--------|
| 1 — Promote to User Level | Find global conventions in project-level files | Project AGENTS.md content | Table: instruction, location, reason |
| 2 — Detect Overlaps | Find duplicates between user-level and project-level | Both AGENTS.md files | Table: project instruction, user equivalent, action |
| 3 — Duplicate Skill Instructions | Find AGENTS.md content covered by skills | Project AGENTS.md + skill definitions | Table: instruction, skill, action |

## Quick Start

### Invocation

Invoke the skill by name:

```
/agents-md-sync
```

The skill runs the discovery engine, resolves file paths, then executes all three audit steps automatically. No configuration is required beyond having AGENTS.md files in place.

### Prerequisites

- At least one AGENTS.md file (user-level or project-level)
- Crush running with `context_paths` configured (recommended)
- No external dependencies — the discovery script uses Python stdlib only

### Discovery Fallback

If `discover.py` cannot resolve AGENTS.md files, the skill prompts the user via the `question` tool:

| Scenario | Resolution |
|----------|------------|
| User-level missing | Create at `~/.config/crush/AGENTS.md` or custom path |
| Project-level missing | Create at `<repo_root>/AGENTS.md` or custom path |
| Both missing | Create both at standard locations or custom paths |
| Multiple filenames at user level | Free-text clarification question |

Files are created rather than skipped — both files are required for meaningful comparison.

### Typical Run

A typical invocation produces output like:

```
## Summary

Total recommendations: 5
  Promote to user-level: 2
  Remove from project-level: 2
  Remove (duplicated by skill): 1
```

## How It Works

### Step 1 — Promote to User Level

Scans the project-level AGENTS.md for instructions that apply globally across all projects. An instruction qualifies for promotion when it:

- Is a general convention (not tied to a specific project)
- Would apply to any project the user works on
- Is a personal preference (writing style, formatting, tooling preferences)

Example output:

| Instruction | Location | Reason |
|-------------|----------|--------|
| Use Oxford comma in lists | AGENTS.md:12 | General writing convention |
| Prefer scripts over inline logic | AGENTS.md:25 | Applies to all projects |
| No HTML tags in markdown files | AGENTS.md:31 | Formatting standard across all projects |

### Step 2 — Detect Overlaps

Compares user-level AGENTS.md against project-level AGENTS.md to find exact or equivalent duplicates. An instruction qualifies for removal from project-level when it:

- Already exists in user-level AGENTS.md (exact or semantically equivalent)
- Is covered by a broader user-level rule

Example output:

| Project-level instruction | User-level equivalent | Action |
|---------------------------|----------------------|--------|
| Use kebab-case for names | User AGENTS.md:8 | Remove from project-level |
| No emojis in code | User AGENTS.md:15 | Remove from project-level |
| Read files before editing | User AGENTS.md:22 | Remove from project-level |

### Step 3 — Duplicate Skill Instructions

Checks AGENTS.md content against enforced skills to find instructions that are already defined in skill documentation. An instruction qualifies for removal when it:

- Is already defined in an enforced skill's SKILL.md
- Duplicates the skill's documented behavior

Enforced skills currently checked:

| Skill | Covered Topics |
|-------|----------------|
| gen-skill | Skill creation, validation, frontmatter, token limits, references splitting |
| planner | Plan structure, phases, todo tracking |
| commit | Conventional commits, commit message format |

Example output:

| AGENTS.md instruction | Defined in | Action |
|-----------------------|------------|--------|
| SKILL.md must be under 5000 tokens | enforced-skill-a | Remove from AGENTS.md |
| Plans must have YAML frontmatter | enforced-skill-b | Remove from AGENTS.md |

### Consolidation Rule

When promoting instructions or detecting duplicates, the skill consolidates multiple definitions into a single, well-defined recommendation. Fragmented or repetitive text is not copied verbatim — all relevant points are combined into one clear instruction before recommending it for user-level AGENTS.md.

## Configuration

### Crush Config

The discovery engine reads `~/.config/crush/crush.json` when Crush is active. Relevant fields:

| Field | Description | Example |
|-------|-------------|---------|
| `options.context_paths` | List of AGENTS.md file paths | `["~/.config/crush/AGENTS.md", "~/docs/INSTRUCTIONS.md"]` |
| `options.initialize_as` | Default filename for new files | `"AGENTS.md"` |

If `context_paths` contains multiple files with different basenames, the discovery engine populates the `questions` array to request clarification.

### Environment Variables

The discovery script respects one environment variable:

| Variable | Description | Effect |
|----------|-------------|--------|
| `CRUSH_AVAILABLE` | Set to `"true"` to enable Crush config detection | When set, reads `crush.json`; when unset, uses default paths |

## Output Format

Each audit step outputs a markdown table. After all steps, the skill produces a summary with counts:

```
## Summary

Total recommendations: N
  Promote to user-level: N
  Remove from project-level: N
  Remove (duplicated by skill): N
```

The discovery engine outputs JSON (when run manually):

```json
{
  "user_level": ["/home/user/.config/crush/AGENTS.md"],
  "project_level": ["/path/to/project/AGENTS.md"],
  "nonexistent": [],
  "warnings": [],
  "questions": []
}
```

## Extensibility

### Adding New Enforced Skills

To check additional skills for duplicates, update the enforced skills list in SKILL.md (Step 3 section):

```
- skill-name (what it covers)
```

The skill will cross-reference the new skill's SKILL.md during audit.

### Custom File Paths

The discovery engine respects Crush config. To use non-standard paths:

1. Set `context_paths` in `~/.config/crush/crush.json`
2. Set `initialize_as` for custom filenames (e.g., `INSTRUCTIONS.md`)

### Platform-Agnostic Design

The skill does not depend on any Git hosting platform. AGENTS.md files follow Crush conventions and are independent of GitHub, GitLab, Gitea, or any other platform.

## Development

### Running Discovery Manually

```bash
cd agents-md-sync
CRUSH_AVAILABLE=true python3 scripts/discover.py
```

Set `CRUSH_AVAILABLE=true` to enable Crush config detection. Without it, the script falls back to default paths (`~/.config/crush/AGENTS.md` and `<cwd>/AGENTS.md`).

### Testing the Discovery Script

Run the script from different directories to verify detection:

- From a project with AGENTS.md — verifies project-level detection
- From a directory without AGENTS.md — verifies `nonexistent` output
- With a custom Crush config — verifies `context_paths` and `initialize_as` parsing

### Dependencies

The skill has no external dependencies. `discover.py` uses only Python standard library modules:

- `json` — config parsing and output serialization
- `os` — path resolution and file existence checks
- `sys` — error output handling
- `pathlib` — path manipulation

SKILL.md execution relies on Crush built-in tools:

- `crush_info` — detect active Crush instance and retrieve `context_paths`
- `question` — user prompts for file resolution
- `todos` — progress tracking
- `view` — file reading for AGENTS.md content analysis
- `bash` — running `discover.py` with environment variables

## Limitations

- Requires at least one AGENTS.md file to exist for meaningful comparison
- Semantic overlap detection relies on agent analysis, not automated string matching
- Skill cross-reference is limited to explicitly listed enforced skills — new skills must be added manually
- Does not apply changes automatically — all output is recommendations
- Does not analyze file content for formatting, syntax, or structural issues (only duplication and placement)
