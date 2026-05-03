# ly-agent-skills

A collection of agent skills iterated over time. No specific purpose beyond doing one thing well.

## Philosophy

These skills follow a clean-code approach applied to agent tooling. Two core principles:

### 1. Single Responsibility

Each skill does one thing and does it well. No bloated multi-purpose skills. If it sounds like it should be two skills, it is.

### 2. Script the Deterministic

If the logic is rigid and repeatable, it belongs in a script — not in the agent's reasoning.

| | Script | LLM Reasoning |
|---|---|---|
| Speed | Fast | Slow |
| Cost | Near-zero tokens | Expensive |
| Reliability | Deterministic | Non-deterministic |

The skill's role is to **orchestrate**, not to calculate. Shift work from the LLM to scripts whenever possible.

### 3. Compose Over Monolith

When a workflow is too complex for a single skill, break it down into smaller, focused skills and create an orchestrator to coordinate them. One skill, one job — even the orchestrator's job is just orchestration.

### 4. Track State Explicitly

All skills follow the [agentskills.io spec](https://agentskills.io) and enforce the use of task-tracking tools (e.g. `todos`). This ensures:

- **Capable models** stay within context limits by having a clear progress checkpoint.
- **Less capable models** have the best possible chance of reaching the goal through structured, step-by-step execution.

### 5. Reference Over Inline

Context is loaded via `references/` files, not baked into the skill body. Only the context needed for the current step is loaded — keeping prompts lean and focused.
