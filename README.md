# DemoBank AI SDLC

> **WARNING: This application is intentionally vulnerable. It must only be used in a local or isolated demo environment. Do not deploy to production. Do not connect to real banks, payment systems, or customer data.**

A demo banking application built to showcase an AI-native SDLC using Cursor, Claude Code, Slack feedback, Harness Pipelines, Harness Worker Agents, Semgrep/SAST, and Kubernetes deployment remediation.

## What is this?

DemoBank AI SDLC is a deliberately imperfect Python (Flask) banking app that supports a live demo story:

1. Users report UX bugs in Slack.
2. Cursor analyzes the thread and opens a PR.
3. Harness runs CI and a Worker Agent (Change Advisor) reviews the PR.
4. Semgrep/SAST detects intentional vulnerabilities.
5. A Security Remediation Advisor proposes fixes.
6. The app deploys to Kubernetes — but the readiness probe is intentionally wrong.
7. A Manifest Remediator Agent fixes the probe and the retry succeeds.

See `docs/demo-story.md` for the full flow.

## Running Locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m scripts.seed
python -m app.server
```

The app starts on http://localhost:3000.

## Running Tests

```bash
pytest
```

Tests emit a JUnit XML report to `test-results/junit.xml` for Harness Test Intelligence.

## Running the Demo Semgrep Scan

Requires [Semgrep](https://semgrep.dev/docs/getting-started/) to be installed.

```bash
semgrep scan --config .semgrep.yml app/
```

Expected findings: SQL injection, command injection, reflected XSS, insecure CORS.

## Building the Docker Image

```bash
docker build -t harnessbank-demo:latest .
docker run -p 3000:3000 harnessbank-demo:latest
```

## Deploying to Kubernetes

```bash
kubectl apply -f deploy/k8s/base/namespace.yaml
kubectl apply -f deploy/k8s/base/configmap.yaml
kubectl apply -f deploy/k8s/demobank/deployment.yaml
kubectl apply -f deploy/k8s/demobank/service.yaml
```

Note: The initial deployment will fail because the readiness probe points to `/healthz` instead of `/health`. This is intentional — the Manifest Remediator Agent demonstrates the fix.

## Project Structure

```
.
├── app/
│   ├── app.py            # Flask app factory, routes, CORS
│   ├── server.py         # Entry point
│   ├── db.py             # SQLite setup
│   ├── config.py         # App config (intentional hardcoded secrets)
│   ├── routes/           # accounts, transfers, statements, admin, fx
│   ├── templates/        # Jinja2 templates
│   └── static/           # CSS and client JS
├── tests/                # pytest + Flask test client
├── scripts/              # seed.py, smoke-test.sh
├── deploy/              # Deployment configs (k8s, apigee)
├── docs/                 # Demo story, security notes, remediation guidance
├── requirements.txt      # Runtime dependencies
├── requirements-dev.txt  # Dev/test dependencies
├── pytest.ini            # pytest + JUnit report config for Harness TI
├── .semgrep.yml          # Deterministic demo Semgrep rules
├── Dockerfile
└── CHANGELOG.md
```

## Intentional Vulnerabilities

| ID       | Type                  | Severity | Location                   |
|----------|-----------------------|----------|----------------------------|
| VULN-001 | SQL Injection         | ERROR    | app/routes/accounts.py     |
| VULN-002 | Command Injection     | ERROR    | app/routes/admin.py        |
| VULN-006 | Reflected XSS         | WARNING  | app/app.py                 |
| VULN-007 | Insecure CORS         | WARNING  | app/app.py                 |

These vulnerabilities exist for SAST demonstration purposes only. See `docs/security-demo-notes.md` and `docs/remediation-guidance.md`.

## License

MIT
