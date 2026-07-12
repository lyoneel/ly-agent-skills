---
name: gen-agent
description: Generate new agent definition files with proper structure and metadata. Use when creating new specialized agents for task-specific behaviors or when scaffolding agent templates.
---

# Generate Agent Definition

Initialize todos tool:

```json
[
  {"content": "Gather agent requirements", "status": "in_progress", "active_form": "Gathering agent requirements"},
  {"content": "Determine agent category", "status": "pending", "active_form": "Determining agent category"},
  {"content": "Structure agent definition", "status": "pending", "active_form": "Structuring agent definition"},
  {"content": "Generate agent file", "status": "pending", "active_form": "Generating agent file"},
  {"content": "Validate generated agent", "status": "pending", "active_form": "Validating generated agent"}
]
```

This skill generates new agent definition files following the established agent structure and best practices observed in the agents folder.

## Purpose

Create well-structured agent definition files that can be loaded by the agent skill. Agents define specialized behaviors, constraints, and instructions for focused task execution.

## Agent Structure Patterns

Based on existing agents, there are several common patterns:

1. Role-based agents: Define a specific role and expertise area
2. Task-focused agents: Optimize for specific workflows or operations
3. Meta-agents: Agents that create or manage other agents
4. Domain experts: Specialized knowledge in a particular field

## Step-by-Step Instructions

1. Gather agent requirements from the user:
   - Agent name (lowercase with hyphens, will be the filename)
   - Primary purpose and role
   - Target domain or task type
   - Specific constraints or requirements
   - Output format preferences
   - Relevant documentation URLs

> Update todos: mark "Gather agent requirements" as completed, mark "Determine agent category" as in_progress.

2. Determine agent category:
   - Coder: Programming language or framework specialist
   - Writer: Content creation or analysis
   - Meta: Agent design or prompt engineering
   - Expert: Domain-specific knowledge specialist

> Update todos: mark "Determine agent category" as completed, mark "Structure agent definition" as in_progress.

3. Structure the agent definition with these sections:
   - Opening statement: Clear role definition
   - Mission: What the agent does and how it operates
   - Constraints: Technical limits, required tools, documentation sources
   - Style: Communication tone and reasoning approach
   - Forbidden behaviors: What the agent must not do
   - Failure modes and recovery: How to handle errors
   - Output format: Expected response structure

4. For coding agents, include:
   - Language version and tooling
   - Preferred libraries (native vs third-party)
   - Code quality standards
   - Documentation references

5. For meta-agents, include:
   - Target LLM optimizations if applicable
   - Prompt engineering techniques
   - Self-critique mechanisms
   - Verification loops

> Update todos: mark "Structure agent definition" as completed, mark "Generate agent file" as in_progress.

6. Generate the agent file:
   - Create file at `agents/{agent-name}.md`
   - Use clear, directive language
   - Avoid hedge words like "try to" or "you may want to"
   - Include specific examples when relevant
   - Reference authoritative documentation URLs

> Update todos: mark "Generate agent file" as completed, mark "Validate generated agent" as in_progress.

7. Validate the generated agent:
   - Check for clarity and completeness
   - Ensure all sections are present
   - Verify documentation links are included
   - Confirm output format is specified

## Usage Examples

Generate a new coding agent:
```bash
/gen-agent
Agent name: coder-rust
Purpose: Rust programming assistance with focus on safety and performance
```

Generate a specialized meta-agent:
```bash
/gen-agent
Agent name: prompt-optimizer
Purpose: Refine and improve existing system prompts for clarity and effectiveness
```

## Agent File Location

Agent definitions are created in the `agents/` directory relative to the skill location. Each agent is a single Markdown file named `{agent-name}.md`.

## Common Agent Components

Role definition:
```markdown
You are [Name] — a specialized agent whose purpose is to [primary function].
```

Constraints with documentation:
```markdown
Constraints:
- Use only [technology/framework]
- Base all work on up-to-date documentation: [URL]
- Produce [quality standard] output
```

Output format specification:
```markdown
Output Format:
Always structure responses as:
[specific format with examples]
```

## Notes

- Agent names should be descriptive and use kebab-case
- Always include authoritative documentation URLs
- Be specific about versions and tooling when applicable
- Define clear failure modes and recovery strategies
- Use directive, high-agency language
- Avoid casual chat or explanatory fluff unless the agent role requires it
- For coding agents, emphasize compilable, runnable code
- For meta-agents, include self-critique and verification loops

> Update todos: mark "Validate generated agent" as completed. Clear todos with `todos([])`.
