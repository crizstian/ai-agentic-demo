---
description: Switch context to CI/CD and pipeline focus
allowed-tools: Read, Grep, Glob, Bash
---

Activate CI/CD context profile for this session.

## Instructions

1. Read the project's pipeline configuration files:
   - Look for `.harness/` directory (Harness pipelines)
   - Look for `.github/workflows/` (GitHub Actions)
   - Look for `Taskfile.yml` (task automation)
   - Look for `scripts/` directory

2. Summarize what you found in 3-5 lines:
   - Pipeline tool (Harness / GitHub Actions / both)
   - Number of pipelines/workflows
   - Key stages (build, test, deploy)
   - Any infrastructure-as-code (Terraform, Helm)

3. Set your focus for this session:
   - Prioritize Harness MCP tools (`mcp__harness-docs__*`) for pipeline questions
   - When editing pipeline files, validate YAML structure
   - For Taskfile changes, ensure `task --list-all` still works
   - Use `@k8s-debugger` for deployment-related investigation

4. Tell the user: "CI/CD context active. I'll focus on pipeline configs, build automation, and deploy scripts. Ask me anything about your pipelines."
