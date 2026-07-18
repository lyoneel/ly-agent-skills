---
name: agents-md-sync
description: Audit AGENTS.md files for duplication and correct placement. Use when syncing user-level and project-level AGENTS.md files.
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["question", "view", "bash", "todos", "crush_info"]
---

Initialize todos tool:

```json
{
  "todos": [
    {"content": "Initialize agents-md-sync operation", "status": "in_progress", "active_form": "Initializing agents-md-sync operation"},
    {"content": "Step 1 — Recommend project-level instructions for user-level promotion", "status": "pending", "active_form": "Analyzing project-level instructions for promotion"},
    {"content": "Step 2 — Detect overlaps between user-level and project-level", "status": "pending", "active_form": "Detecting overlaps between user and project levels"},
    {"content": "Step 3 — Find duplicates between AGENTS.md and enforced skills", "status": "pending", "active_form": "Finding duplicates with enforced skills"},
    {"content": "Complete agents-md-sync operation", "status": "pending", "active_form": "Completing agents-md-sync operation"}
  ]
}
```

# Audit AGENTS.md Files

All outputs are suggestions and recommendations only. Never apply changes automatically. The user has final decision on all changes.

BEGIN EXECUTION IMMEDIATELY. Do not ask the user what they want to do. Start with step 1:

## Discovery

Call `crush_info` first to detect if Crush is active and retrieve `context_paths` from the running instance. The `crush.json` file may exist without Crush being used — `crush_info` is the authoritative source.

Run `scripts/discover.py` with `CRUSH_AVAILABLE` set based on the `crush_info` result. The script outputs JSON with `user_level`, `project_level`, `nonexistent`, `warnings`, and `questions` fields.

If the `questions` array is non-empty, use the `question` tool to ask the user before proceeding. Convert each entry in `questions` into a `free_text` question:

```json
{
  "questions": [
    {
      "type": "free_text",
      "question": "AGENTS.md detection needs clarification",
      "description": "<content from discover.py questions array>"
    }
  ]
}
```

If `user_level` is empty, ask:

```json
{
  "questions": [
    {
      "type": "single_choice",
      "question": "User-level AGENTS.md not found",
      "description": "Could not locate user-level AGENTS.md. Both files are required for comparison. How should I proceed?",
      "choices": [
        {"id": "create_default", "label": "Create at default path", "description": "Create ~/.config/crush/AGENTS.md"},
        {"id": "custom_path", "label": "Create at custom path", "description": "I will specify the file location"}
      ]
    }
  ]
}
```

If `project_level` is empty, ask:

```json
{
  "questions": [
    {
      "type": "single_choice",
      "question": "Project-level AGENTS.md not found",
      "description": "Could not locate project-level AGENTS.md. Both files are required for comparison. How should I proceed?",
      "choices": [
        {"id": "create_default", "label": "Create at default path", "description": "Create <repo_root>/AGENTS.md"},
        {"id": "custom_path", "label": "Create at custom path", "description": "I will specify the file location"}
      ]
    }
  ]
}
```

If both are empty, ask:

```json
{
  "questions": [
    {
      "type": "single_choice",
      "question": "AGENTS.md files not found",
      "description": "Could not locate user-level or project-level AGENTS.md. Both files are required for comparison. How should I proceed?",
      "choices": [
        {"id": "create_default", "label": "Create at default paths", "description": "Create both files at standard locations"},
        {"id": "custom_paths", "label": "Create at custom paths", "description": "I will specify the file locations"}
      ]
    }
  ]
}
```

If the user selects "Create at custom path", follow up with:

```json
{
  "questions": [
    {
      "type": "free_text",
      "question": "Custom AGENTS.md path",
      "description": "Enter the full path for the missing AGENTS.md file. The file will be created at this location."
    }
  ]
}
```

Once all files are in place (found or created), proceed to step 1.

## Step 1 — Promote to User Level

Scan the project-level AGENTS.md for instructions that apply globally across all projects.

Recommend moving to user-level AGENTS.md when an instruction:

- Is a general convention (not project-specific)
- Would apply to any project the user works on
- Is a personal preference (writing style, formatting, tooling preferences)

Output a table:

| Instruction | Location | Reason |
|---|---|--------|
| Example | AGENTS.md:10 | General convention, applies to all projects |

## Step 2 — Detect Overlaps

After step 1, compare user-level AGENTS.md against project-level AGENTS.md.

Recommend removal from project-level when an instruction:

- Already exists in user-level AGENTS.md (exact or equivalent)
- Is covered by a user-level rule

Output a table:

| Project-level instruction | User-level equivalent | Action |
|---|---|--------|
| Example | User AGENTS.md:5 | Remove from project-level |

## Step 3 — Duplicate Skill Instructions

Check if AGENTS.md contains instructions already defined by enforced skills.

Enforced skills to cross-reference:

- gen-skill (skill creation, validation, frontmatter, token limits, references splitting)
- planner (plan structure, phases, todo tracking)
- commit (conventional commits, commit message format)

Recommend removal from AGENTS.md when an instruction:

- Is already defined in the enforced skill
- Duplicates the skill's documented behavior

Output a table:

| AGENTS.md instruction | Defined in | Action |
|---|---|--------|
| Example: SKILL.md under 5000 tokens | gen-skill | Remove from AGENTS.md |

## Report Format

After all 3 steps, output a summary:

```
## Summary

Total recommendations: N
  Promote to user-level: N
  Remove from project-level: N
  Remove (duplicated by skill): N
```

## Consolidation Rule

When promoting instructions or detecting duplicates, consolidate multiple definitions into a single well-defined instruction. Do not copy fragmented or repetitive text verbatim. Combine all relevant points into one clear, complete instruction before adding it to user-level AGENTS.md.
