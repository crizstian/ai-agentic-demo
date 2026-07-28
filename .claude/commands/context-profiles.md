---
description: List available context profiles and explain context engineering strategy
allowed-tools: Read
---

Show the user the available context profiles for this project:

## Context Profiles

This project uses **lazy-load context engineering** — different tasks load different instructions and focus on different file scopes. This reduces irrelevant context and improves AI accuracy.

### How It Works

1. **System-level routing** — CLAUDE.md acts as a router. Each `/system:command` loads only that system's instructions
2. **Agent-level scoping** — Each agent in `.claude/agents/` has `allowedTools` restrictions (least-privilege) and a focused system prompt
3. **Command-level focus** — Slash commands like `/create-pr` and `/triage-issue` scope the task

### Available Profiles

| Profile | Trigger | Focus Areas | Best For |
|---------|---------|-------------|----------|
| **CI/CD** | `/context:cicd` or work on pipeline files | `.harness/`, `Taskfile.yml`, `scripts/`, `.github/` | Pipeline configs, build automation, deploy scripts |
| **Code Review** | `/context:code-review` or use `@code-reviewer` | `src/`, `internal/`, `pkg/`, `lib/`, `app/` | Reviewing changes, code quality, test coverage |
| **Infrastructure** | Use `@k8s-debugger` or work on infra files | `terraform/`, `k8s/`, `helm/`, `deploy/` | Kubernetes debugging, Terraform plans, infrastructure |
| **Research** | Use `@researcher` | Web search, docs, codebase-wide search | Lookups, documentation, fact-finding |
| **Refactoring** | Use `@refactorer` | All source files (full write access) | Cross-file refactoring, module restructuring |

### Model Tiers

Each profile maps to an appropriate model tier:

| Tier | Model | Cost | Profiles |
|------|-------|------|----------|
| **Standard** | sonnet | 1x | researcher, pr-preparer, code-reviewer, architecture-reviewer, test-writer, k8s-debugger |
| **Deep** | opus | 5x | refactorer, complex architecture decisions |

### Tips

- For most tasks, use agents (`@agent-name`) — they automatically scope tools and model tier
- For pipeline/deploy work, run `/context:cicd` to prime the session focus
- For code review, run `/context:code-review` to prime the session focus
- The context profile is a session-level hint, not a hard constraint
