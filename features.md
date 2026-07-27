# Features — DemoBank AI SDLC

## Banking Application

- Dashboard with fake account balances and recent transaction history
- Transfer funds form with intentional weak validation (accepts negative/zero amounts)
- Login page (demo mode — accepts any credentials)
- FX rates page with mock exchange rate data
- Statements download endpoint

## Intentional UX Issues (for Slack feedback demo)

- Transfer button partially clipped on mobile viewports
- Quick action cards misalign at narrow screen widths
- Transaction status badge overlaps amount column at small sizes
- Transfer form shows success message even for invalid amounts

## Intentional Security Vulnerabilities (for SAST demo)

| ID | Type | Location |
|---|---|---|
| VULN-001 | SQL Injection | `src/routes/accounts.js` |
| VULN-002 | Command Injection | `src/routes/admin.js` |
| VULN-003 | Path Traversal | `src/routes/statements.js` |
| VULN-004 | SSRF | `src/routes/fx.js` |
| VULN-005 | Hardcoded Secrets | `src/config.js` |
| VULN-006 | Reflected XSS | `src/app.js` |
| VULN-007 | Insecure CORS Wildcard | `src/app.js` |

## Semgrep SAST Rules

- 7 deterministic demo rules in `.semgrep.yml` mapping 1:1 to the vulnerabilities above
- `npm run semgrep:demo` produces all 7 findings reliably in CI

## Kubernetes Manifests

- Namespace, ConfigMap, Deployment, Service under `k8s/`
- Intentional readiness probe bug: `/healthz` instead of `/health` — triggers the Manifest Remediator demo

## CI/CD Integration

- `Dockerfile` using `node:20-alpine`, exposes port 3000
- Health endpoint at `GET /health` for liveness probe
- Jest + Supertest test suite (6 tests)
- Seed script for local SQLite demo data
- Smoke test shell script

## Documentation

- `docs/demo-story.md` — full AI SDLC demo flow and Slack prompt examples
- `docs/security-demo-notes.md` — vulnerability map and safety constraints
- `docs/remediation-guidance.md` — expected fixes for each vulnerability
