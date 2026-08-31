---
description: Create a pull request from current branch changes
allowed-tools: Read, Bash, mcp__github__create_pull_request, mcp__github__get_pull_request
---

Gather context for creating a PR:

1. Run `git branch --show-current` to get the current branch
2. Run `git status --short` to see changed files
3. Run `git diff --stat` to see change summary
4. Run `git log main..HEAD --oneline` to see commits

Then create a PR using `mcp__github__create_pull_request` with:
- A concise title (under 70 chars)
- A body with ## Summary (bullet points) and ## Test plan
- Base branch: main
- Head branch: current branch
