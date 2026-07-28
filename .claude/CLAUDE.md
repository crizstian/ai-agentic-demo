# ai-agentic-demo — AI Development Environment

## Shared Rules

- **Parallel tool calls:** COMPULSORY for independent operations
- **Edit vs Write:** Edit if <30% of file changes. Write for new files or major rewrites (>30%)
- **Read before Write:** ALWAYS read existing file before overwriting
- **Terse communication:** Direct, action-first, no fluff. No trailing summaries unless asked
- **TodoWrite first:** For any task with 3+ steps, ALWAYS call TodoWrite before touching any file
- **Memory:** Save feedback corrections, user workflow preferences, and environment-specific notes to memory. Check memory at session start for prior context

## Tool Selection

1. **MCP tools first** — prefer `mcp__harness__*`, `mcp__github__*`, `mcp__kubernetes__*` over CLI equivalents
2. **CLI second** — `gh`, `kubectl`, `gcloud` when MCP doesn't cover the operation
3. **REST last** — direct API calls only when MCP and CLI both fail

## Context Profiles

This project uses lazy-load context engineering. Switch focus with context commands:

| Command | Focus | When to Use |
|---------|-------|-------------|
| `/context-profiles` | List all profiles | Overview of available contexts |
| `/context:cicd` | Pipelines, builds, deploys | Working on CI/CD configs |
| `/context:code-review` | Source code, tests, quality | Reviewing changes |
| `/context:infra` | Kubernetes, Terraform, Helm | Infrastructure work |

Specialized agents (`@agent-name`) also scope context automatically — see `.claude/agents/`.

## Web Search

- Use `mcp__perplexity__perplexity_ask` for quick factual questions
- Use `mcp__perplexity__perplexity_research` for deep multi-source research (slow, 30s+)
- Use `mcp__perplexity__perplexity_reason` for complex analysis requiring step-by-step logic
- Include "Sources:" section with URLs after any web-grounded response

## GitHub Workflow

- Use `mcp__github__*` tools for PR creation, issue management, code search
- Use `gh` CLI for operations not covered by MCP (e.g., `gh run view`, `gh api`)
- NEVER use raw `curl` to GitHub API when `gh` or MCP tools are available
