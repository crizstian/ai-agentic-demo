# Architecture

## Overview

DemoBank is a deliberately vulnerable demo banking application built to showcase an AI-first Autonomous SDLC. The application is intentionally simple, single-tier, and file-based to keep the demo story focused on the Autonomous SDLC workflow rather than distributed systems complexity.

The primary purpose is to demonstrate how coding agents and Harness Agents collaborate across the full software lifecycle. Coding agents stop at the PR. Harness Agents take it from there. The demo showcases both Shift Left workflows (Security Testing Agent scans code for vulnerabilities before merge) and Shield Right workflows (Runtime Protection Agent discovers, protects, and monitors APIs and AI components in production).

## Components

### Flask Application (`app/`)
- **app.py** — Flask app factory, route registration, CORS configuration, and page endpoints (dashboard, transfer, login). Contains intentional vulnerabilities VULN-006 (reflected XSS) and VULN-007 (insecure CORS wildcard).
- **server.py** — Application entry point; initializes the database and starts the Flask development server.
- **db.py** — SQLite connection singleton and schema initialization (accounts and transactions tables). Uses an in-memory database during tests.
- **config.py** — Application configuration including hardcoded demo secrets (VULN-005).

### API Routes (`app/routes/`)
Blueprints exposing RESTful JSON endpoints, each containing one or more intentional security vulnerabilities for SAST demonstration:
- **accounts.py** — Account lookup endpoint with SQL injection (VULN-001) and BOLA/IDOR endpoint (VULN-010) for attack chain demo.
- **admin.py** — Administrative ping endpoint with command injection (VULN-002).
- **statements.py** — Statement download endpoint with path traversal (VULN-003).
- **fx.py** — Foreign exchange rate endpoint with SSRF (VULN-004).
- **transfers.py** — Fund transfer creation with weak validation (allows negative amounts).
- **ai_assistant.py** — AI banking assistant endpoint with prompt injection (VULN-008) and PII leak (VULN-009). Simulates an AI chatbot consuming an external MCP tool for financial data enrichment. Creates attack surface for Runtime Protection Agent's AI Firewall and MCP monitoring.

### Frontend (`app/templates/`, `app/static/`)
- **Templates** — Jinja2 HTML templates for dashboard, transfer, login, and bill payment pages.
- **Static assets** — CSS and client-side JavaScript copied verbatim from the original Node.js version to preserve UI behavior.

### Tests (`tests/`)
- **pytest + Flask test client** — Unit and integration tests covering dashboard rendering, health checks, transfers API, and Kubernetes manifest validation.
- **JUnit XML output** — Configured via `pytest.ini` to emit `test-results/junit.xml` for Harness Test Intelligence integration.

### Infrastructure
- **Dockerfile** — Python 3.12-slim image, installs runtime dependencies from `requirements.txt`, and runs the Flask server.
- **deploy/k8s/** — Kubernetes deployment and service manifests with an **intentional bug**: the readiness probe points to `/healthz` instead of `/health`. This mismatch is preserved to demonstrate the Harness Manifest Remediator agent.
- **.semgrep.yml** — Custom Semgrep rules targeting the 10 intentional vulnerabilities. Rules use Python-specific patterns (taint mode for SQLi, `subprocess.check_output` for command injection, etc.) and are designed to fire deterministically for demo reliability.

### Scripts (`scripts/`)
- **seed.py** — Populates the database with demo accounts and transactions (including one intentionally invalid negative-amount transfer for UX bug demonstration).

## Data Flow

1. **User accesses the web UI** → Flask serves Jinja2 templates with embedded account/transaction data fetched from SQLite.
2. **User submits a transfer** → Browser POSTs JSON to `/api/transfers` → Flask blueprint validates (weakly), inserts into SQLite, and returns success.
3. **Admin diagnostic request** → Browser GETs `/api/admin/ping?host=...` → Flask executes a shell command (intentionally unsafe) and returns output.
4. **Health check** → Kubernetes readiness probe (incorrectly) GETs `/healthz` → fails because the actual endpoint is `/health` → pod stays unready until manually fixed.

5. **AI assistant query** — Browser POSTs to `/api/ai/chat` → Flask calls `_query_financial_context()` (simulated RAG) and `_call_mcp_tool()` (external MCP call) → returns AI response with financial context.

All data resides in a single SQLite file (`demobank.db` by default, `:memory:` during tests). No external services or message queues.

## Dependencies

### Runtime (`requirements.txt`)
- **Flask** — Web framework and WSGI application server.
- **flask-cors** — CORS middleware (intentionally misconfigured to allow `*`).
- **requests** — HTTP client library (used in the SSRF-vulnerable FX endpoint and by AI assistant for MCP tool calls; intentionally pinned to 2.25.1 with known CVE for SCA demo).

### Development/Test (`requirements-dev.txt`)
- **pytest** — Test framework and test runner.
- **pytest-cov** — Code coverage plugin (optional).

The application deliberately avoids heavyweight dependencies (no ORM, no Redis, no message broker) to keep the attack surface small and the demo story easy to follow.

## Deployment / Infrastructure

- **Local development**: Run `python -m app.server` on `localhost:3000` after seeding the database with `python -m scripts.seed`.
- **Containerized**: Docker image built from `Dockerfile`, exposing port 3000.
- **Kubernetes**: Deployed via `deploy/k8s/demobank/deployment.yaml` with the intentional readiness probe bug that causes the first deployment to fail — triggering the Manifest Remediator demo flow.

No managed database, no cloud storage, no CDN. The application is fully self-contained and can run offline.

## Intentional Vulnerabilities

The application contains **10 deterministic security flaws** for Security Testing Agent demonstration purposes. These are not accidental — they are the core of the demo story:

| ID       | Type                  | Location                   | Semgrep Rule                   |
|----------|-----------------------|----------------------------|-------------------------------|
| VULN-001 | SQL Injection         | app/routes/accounts.py     | demo-bank-sql-injection        |
| VULN-002 | Command Injection     | app/routes/admin.py        | demo-bank-command-injection    |
| VULN-003 | Path Traversal        | app/routes/statements.py   | demo-bank-path-traversal       |
| VULN-004 | SSRF                  | app/routes/fx.py           | demo-bank-ssrf                 |
| VULN-005 | Hardcoded Secret      | app/config.py              | demo-bank-hardcoded-secret     |
| VULN-006 | Reflected XSS         | app/app.py                 | demo-bank-reflected-xss        |
| VULN-007 | Insecure CORS         | app/app.py                 | demo-bank-insecure-cors        |
| VULN-008 | Prompt Injection      | app/routes/ai_assistant.py | demo-bank-prompt-injection     |
| VULN-009 | PII Leak in AI Response | app/routes/ai_assistant.py | demo-bank-pii-leak-ai-response |
| VULN-010 | BOLA/IDOR             | app/routes/accounts.py     | demo-bank-bola-idor            |

Each vulnerability is marked with a `DEMO VULNERABILITY` comment and a warning not to fix it. The Semgrep rules in `.semgrep.yml` are tuned to detect these exact patterns without false positives.

## AI Security Demo Surface

The application demonstrates a 3-layer AI security model:

- **Layer 1: Protect AI-generated code** — Security Testing Agent performs SAST to detect vulnerabilities the coding agent introduced. This is Shift Left applied to AI-assisted development: the Security Testing Agent catches insecure patterns before they reach production.
- **Layer 2: Protect APIs that AI exposes** — Runtime Protection Agent automatically discovers and protects the `/api/ai/chat` endpoint. API discovery, threat detection, and rate limiting happen without manual configuration.
- **Layer 3: Protect AI agents and models** — Runtime Protection Agent monitors MCP tool calls and detects prompt injection attempts. The AI Firewall inspects inputs to the AI assistant, blocking adversarial prompts and preventing PII exfiltration in responses.

## Technology Migration (PR #27)

The application was originally implemented in **Node.js/Express** and migrated to **Python 3.12/Flask** while preserving:
- All 7 intentional vulnerabilities with functionally equivalent Python code.
- The intentional Kubernetes readiness probe bug (`/healthz` vs `/health`).
- UI behavior, routing, and static asset structure.
- Test coverage and assertions (9 passing tests, 1 intentional failure for the k8s bug).

**Why Python?** The migration demonstrates that the AI SDLC workflow is language-agnostic and that Harness AI agents can operate across technology stacks. The Flask implementation uses idiomatic Python patterns (blueprints, Jinja2, pytest) rather than direct Node.js translations.

## Decisions and Trade-offs

- **Single SQLite file**: Simplifies the demo setup (no external database to configure) but means the app cannot scale horizontally. Acceptable for a demo-only application.
- **Intentional bugs**: The app is not production-ready by design. Every "flaw" is load-bearing for the demo narrative.
- **No authentication**: Login is a stub (`POST /login` accepts any credentials). Real banking applications require OAuth2/OIDC; this demo omits it to keep the focus on the AI workflow.
- **Flask development server**: The app uses Flask's built-in server (`app.run()`), which is not production-grade. A real deployment would use Gunicorn or uWSGI. For a local demo, the development server is sufficient.
- **Preserved readiness probe bug**: The k8s manifests intentionally reference `/healthz` while the app exposes `/health`. This mismatch triggers a deployment failure, which the Harness Manifest Remediator agent detects and fixes — a key moment in the demo story.
