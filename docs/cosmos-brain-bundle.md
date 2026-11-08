# DemoBank — Brain Bundle for Cosmos Experts

This document is the Brain of the AI Software Factory. Every Cosmos Expert
MUST read this before taking any action. It consolidates architectural
decisions, constraints, and patterns from 25+ development sessions.

See also: docs/factory-architecture.md for the full Inner/Outer Loop design.

---

## Demo Flow: 7 Acts

DemoBank demonstrates Harness CI/CD + AI agents through 7 acts:

| Act | What happens | Key systems |
|-----|-------------|-------------|
| 0 | Reset to STATE 0 (clean baseline) | scripts/demo-reset.sh |
| 1 | Coding agent adds AI chat assistant + intentional vulns | Claude Code / Cosmos Builder |
| 2 | Pipeline runs: build, test, SLSA provenance | Harness CI |
| 3 | Security agent auto-remediates SAST/SCA findings | security_analyzer worker agent |
| 4 | Deploy: canary → CV → rolling | Harness CD + K8s |
| 4.5 | ConfigMap bug → AI Manifest Remediator → fix PR | ca_manifest_remediation_v2 agent |
| 5 | Attacker exploits → Traceable detects (Monitor mode) | attack-chain.sh + Traceable |
| 6 | AI SRE responds to incident (12s, 6 actions) | Harness AI SRE + PagerDuty webhook |
| 7 | Block mode + AI Security (automatic remediation) | Traceable Block + security agent |

## Intentional Vulnerabilities in STATE 0

These are PRESENT by design and must NOT be removed until the appropriate Act:

- VULN-001: SQL injection — string concatenation in accounts.py
- VULN-002: Command injection — shell=True in admin.py
- VULN-006: Reflected XSS — unescaped user input in app.py
- VULN-007: CORS wildcard — origins="*" in app.py
- CSS bugs: rotated action cards (3deg), off-screen transfer button (600px margin)

Act 1 adds more:
- VULN-PROMPT-INJECTION: string concat in AI prompt
- VULN-PII-LEAK: raw financial data in API response
- VULN-SECRET-LEAK: hardcoded API key default
- VULN-REQUESTS-CVE: requests==2.28.0 (CVE-2023-32681)
- VULN-ZOMBIE-API: /api/ai/status without auth

---

## Architectural Decisions

### Identity & Auth
- Harness PAT: `harnessToken` secret (platform auth)
- GitHub PAT: `CristianGithub` secret (git operations)
- Split server-side key: `v4kvjbb2cuupu0ihed20iceumvv1m9po07bn`
- Split client-side key: `cl0bl351743733kglfasq85pr2kq8ul9rmqv`
- Jira: project HD, type Task, connector account.Harness_JIRA

### Feature Flags (Split/FME)
- `ai_chat_enabled` — frontend widget visibility
- `ai_chat_backend` — backend endpoint gate
- Backend: SDK first, REST API fallback if SDK returns "control"
- Lazy init mandatory (avoid timeout in CI)

### Branching Strategy
- `secops/ai-agentic-demo` — working branch
- `secops/ai-agentic-demo-main` — PR merge target
- `main` — DO NOT use directly for PRs
- `secops/ai-agentic-demo-deploy` — stable deploy manifests

### Pipeline
- Pipeline: `AI_SDLC_DemoBank` (inline YAML, sync via MCP before push)
- AI Evals: needs HARNESS_API_KEY + HARNESS_TOKEN in envVariables
- STO filters: `severity_codes`/`issue_types` (not `severity`/`issueType`)

### Worker Agents (5 total)
- Image: `harness/harness-ai-agent:0.1.77`
- HARNESS_TOKEN: `<+secrets.getValue("harnessToken")>`
- PLUGIN_MAX_TURNS: declared as formal input, never hardcoded
- Agents: code_reviewer, security_analyzer, ca_code_unit_test_generator, qa_ui_analyzer, ca_manifest_remediation_v2

### Kubernetes / GKE
- Cluster: `se-sandbox` (us-east1-b), namespace: demobank
- deployment.yaml: must include `harness.io/track: stable` in labels
- Canary: count 2, not percentage
- Delegate: `se-sandbox-org-delegate` (org scope)

### Application
- Response JSON keys: `response`, `financial_context`, `model`
- MCP URL: `os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")`
- OPENAI_API_KEY via ConfigMap `harnessbank-demo-end2end-config`
- CSS: only append new rules, never modify existing

---

## Hard Constraints (violating = guaranteed failure)

1. No modifying existing CSS — only append new rules
2. No creating files outside registered paths
3. No hardcoding PLUGIN_MAX_TURNS — use formal input
4. No `type: Secret` in service variables — use `type: String` + JEXL
5. No `delete_branch` via GitHub MCP — tool doesn't exist
6. No quotes in `<+input>.default()` — causes runtime errors
7. No secrets in prompts, logs, Git, Jira, or memory
8. No `git checkout` for reset — only `scripts/demo-reset.sh`
9. No running HC and GitHub pipelines simultaneously
10. No push without MCP sync when pipeline is inline

---

## Key Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/demo-reset.sh` | Reset to STATE 0 | `--db --commit --push` |
| `scripts/preflight-check.sh` | Validate demo readiness | `--full` / `--act1` / `--json` |
| `scripts/attack-chain.sh` | Act 5 attack simulation | Run after deploy |
| `scripts/smoke-test.sh` | Basic endpoint validation | Quick health check |

---

## Factory Architecture (Inner/Outer Loop)

This project runs as an AI Software Factory with two loops:

- **Inner Loop (Cosmos Experts)**: Spec Writer → Builder → Reviewers → Approver.
  Cognitive work. Output = PR ready for pipeline.
- **Outer Loop (Harness Pipeline)**: Build → Test → SAST/SCA → AI Evals → Deploy.
  Deterministic work. The 5 worker agents run here.

Reviewers are split: Cosmos Experts review pre-PR (reasoning about intent),
Harness STO scans post-PR (deterministic detection with real tools).
This is defense in depth, not redundancy.

Cosmos NEVER deploys. Experts create PRs and tickets.
Harness applies the same policies regardless of whether the PR came from
a human or an agent.

## ASDD Spec Format

Every spec written by the Spec Writer Expert MUST include:

1. **what_user_can_do** — concrete user actions, not implementation details
2. **expected_result** — observable, verifiable (status codes, JSON keys, UI states)
3. **must_respect** — constraints from this Brain that apply
4. **how_to_demonstrate** — exact commands to prove the spec is met
5. **evidence** — artifacts that must exist after implementation

A gap in the spec = a decision the Builder will make alone = Frankenstein risk.

## Harness Platform URLs

- Project: sandbox > CristianRamirez
- Pipeline: AI_SDLC_DemoBank
- App: https://demobank-e2e.selatam.harness-demo.site
- Feature Flags: Harness FME > Prod environment
