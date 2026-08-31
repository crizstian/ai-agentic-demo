# DemoBank — Demo Story

> For the complete AI-first end-to-end demo script, see [ai-demo-script.md](ai-demo-script.md).

## Demo Modes

This repository supports two demo flows:

### 1. AI-First End-to-End (Recommended)
The primary demo flow showcasing the Autonomous SDLC with all Harness Agents.

```
AI Coding Agent (Cursor/Claude Code)
  ↓
Software Delivery Agent: PR Validation + Change Advisor
  ↓
Security Testing Agent: AI SAST + SCA + SCS + Triage + Remediation
  ↓
Software Delivery Agent: Canary Deploy + Continuous Verification
  ↓
💥 Attack Chain: Prompt Injection → BOLA/IDOR → PII Exfiltration
  ↓
Runtime Protection Agent: Behavioral Detection + Virtual Patch
  ↓
Security Testing Agent: Shift Left response (SBOM + Remediation Agent)
  ↓
Runtime Protection Agent: AI Security (3-Layer Model)
```

See [ai-demo-script.md](ai-demo-script.md) for the full script with talking points.

### 2. SDLC Pipeline (Legacy)
The original pipeline-focused demo. Use when the audience cares more about CI/CD mechanics than AI transformation.

```
PR Created
  ↓
CI: Checkout + Build + Unit Tests
  ↓
Worker Agent: Change Advisor
  ↓
STO/Semgrep Scan
  ↓
Worker Agent: Security Remediation Advisor
  ↓
Docker Build + Push
  ↓
Kubernetes Preview Deploy
  ↓
Rollout fails (set healthCheckPath to "/healthz" in deploy/k8s/demobank/values.yaml)
  ↓
Worker Agent: Manifest Remediator
  ↓
Manifest fix PR changes /healthz to /health
  ↓
Retry deployment succeeds
```

## Slack Demo Prompts

Copy these into a Slack thread to simulate user feedback:

```
The AI assistant gave me someone else's account balance when I asked about my own.
```

```
The transfer button is broken on mobile. I can barely click it.
```

```
The dashboard cards look misaligned on my screen.
```

## Claude Code / AI Coding Agent Prompt

```
Use the Harness MCP tools to get context on the latest pipeline execution
and security findings for DemoBank. Then analyze this Slack thread and the
repository. Identify the user-facing issues, propose the smallest safe fix,
update tests if needed, and open a pull request.

Include in the PR description:
- Slack feedback summary
- What changed
- Files modified
- Risk level
- Security-related concerns found during code review
```
