---
description: Triage a GitHub issue — summarize, identify impact, propose next steps
allowed-tools: Read, Bash, Grep, mcp__github__get_issue, mcp__github__list_issues
---

Given an issue number as argument:

1. Read the issue using `mcp__github__get_issue`
2. Summarize the issue in 2-3 sentences
3. Identify potentially impacted files by searching the codebase
4. Classify severity: Critical / High / Medium / Low
5. Propose 2-3 concrete next steps
