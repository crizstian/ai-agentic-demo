---
description: Switch context to code review focus
allowed-tools: Read, Grep, Glob, Bash
---

Activate code review context profile for this session.

## Instructions

1. Detect the project's language and framework:
   - Check for `go.mod` (Go), `package.json` (JS/TS), `pyproject.toml` / `requirements.txt` (Python)
   - Identify test framework (go test, jest/vitest, pytest)
   - Identify linter (golangci-lint, biome/eslint, ruff)

2. Read the current branch diff:
   - Run `git diff --stat` to see scope of changes
   - Run `git log main..HEAD --oneline` for commit context

3. Summarize findings in 3-5 lines:
   - Language and framework detected
   - Number of files changed
   - Change categories (feature, bugfix, refactor, config)

4. Set your focus for this session:
   - Prioritize correctness, error handling, and test coverage
   - Flag security issues (injection, auth, secrets)
   - Check for Go idioms / JS best practices / Python conventions (based on detected language)
   - Suggest missing tests for changed code paths
   - Use `@code-reviewer` agent for detailed review of specific files
   - Use `@test-writer` agent to generate missing tests

5. Tell the user: "Code review context active. I've scoped to your current changes. Ready to review — point me at specific files or ask for a full diff review."
