# Security Demo Notes

## Intentional Vulnerabilities

This application contains intentional security vulnerabilities for Autonomous SDLC demonstration purposes.

**Do not deploy this application to production or any shared environment.**

**Coding agents stop at the PR. Harness Agents take it from there.**

| ID       | Vulnerability           | Severity | File                        | Semgrep Rule                      | Demo Purpose                               |
|----------|-------------------------|----------|-----------------------------|-----------------------------------|---------------------------------------------|
| VULN-001 | SQL Injection           | ERROR    | app/routes/accounts.py      | demo-bank-sql-injection           | Security Testing Agent — SAST capability    |
| VULN-002 | Command Injection       | ERROR    | app/routes/admin.py         | demo-bank-command-injection       | Security Testing Agent — SAST capability    |
| VULN-006 | Reflected XSS           | WARNING  | app/app.py                  | demo-bank-reflected-xss           | Security Testing Agent — SAST capability    |
| VULN-007 | Insecure CORS Wildcard  | WARNING  | app/app.py                  | demo-bank-insecure-cors           | Security Testing Agent — SAST capability    |
| VULN-008 | Prompt Injection        | ERROR    | app/routes/ai_assistant.py  | demo-bank-prompt-injection        | Runtime Protection Agent — AI Security      |
| VULN-009 | PII Leak in AI Response | WARNING  | app/routes/ai_assistant.py  | demo-bank-pii-leak-ai-response    | Runtime Protection Agent — AI Security      |
| VULN-010 | BOLA/IDOR               | ERROR    | app/routes/accounts.py      | demo-bank-bola-idor               | Runtime Protection Agent — API Security     |

### SCA Vulnerability

- `requests==2.25.1` with known CVE (CVE-2023-32681) — triggers Security Testing Agent SCA capability

### Configurable K8s Readiness Probe Bug

- Set `healthCheckPath: "/healthz"` in `deploy/k8s/demobank/values.yaml` to trigger Manifest Remediator demo
- Default is `"/health"` — working correctly

## Vulnerability Groups

### Shift Left (VULN-001, 002, 006, 007 + SCA)

Classic SAST/SCA findings detected by the Security Testing Agent in the Software Delivery Agent pipeline. These represent vulnerabilities caught before code reaches production.

### Shield Right + AI Security (VULN-008, 009, 010)

AI-specific and API threats detected by the Runtime Protection Agent. These represent runtime behavioral threats that require continuous monitoring and session-aware detection.

## Attack Chain Demo Scenario

This scenario demonstrates a multi-step breach that escalates from LOW to CRITICAL, showing why the Runtime Protection Agent's behavioral detection and session stitching matter.

| Step | Severity | Vulnerability | Description                                                              |
|------|----------|---------------|--------------------------------------------------------------------------|
| 1    | LOW      | VULN-008      | Attacker probes AI assistant with prompt injection, extracts account IDs |
| 2    | MEDIUM   | VULN-010      | Attacker uses leaked IDs to access account details via BOLA/IDOR        |
| 3    | HIGH     | VULN-009      | AI response includes raw PII (owner names, balances)                    |

**Combined = CRITICAL breach** — no single finding looks critical in isolation, but the Runtime Protection Agent's session stitching correlates the three steps into a single attack chain, elevating the combined severity to CRITICAL.

## Running the Demo Semgrep Scan

```bash
semgrep scan --config .semgrep.yml app/
```

All 7 findings should appear deterministically (3 ERROR, 4 WARNING).

## Safety Constraints

- Secrets are loaded from environment variables, with demo-only fallbacks.
- No real banking API connections.
- No real customer data.
- Default binding is localhost only.
- The app should only be run locally or in an isolated demo environment.
