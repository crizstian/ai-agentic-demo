# DemoBank AI SDLC — Spec

## Problem
- Who is the user?
  - Harness field teams, sales engineers, and technical stakeholders who need to demonstrate the AI-native SDLC capabilities of the Harness platform in a realistic banking application context.
  
- What workflow is painful or what outcome is blocked?
  - Demonstrating AI-driven security scanning (SAST), manifest remediation, and Slack-based UX feedback collection requires a realistic application with known, reproducible issues. Building such an app from scratch for each demo is time-consuming and inconsistent.
  
- Why does this matter now?
  - The AI-native SDLC story is a key differentiator for Harness. A purpose-built demo application with intentional, deterministic vulnerabilities and UX issues enables consistent, repeatable demonstrations across the entire AI SDLC workflow — from development through security scanning to production feedback.

## Solution
- Proposed user experience
  - A fully functional Node.js banking demo application (DemoBank) that runs locally or in Kubernetes, with a complete set of intentional security vulnerabilities, UX issues, and manifest bugs that map 1:1 to Harness AI SDLC demo scenarios.
  
- Key behaviors and capabilities
  - **Banking UI**: Dashboard with account balances, transaction history, fund transfers, FX rates, statements download, and login (demo mode — accepts any credentials)
  - **Intentional Security Vulnerabilities**: 7 SAST findings (SQL injection, command injection, path traversal, SSRF, hardcoded secrets, reflected XSS, insecure CORS) clearly marked with `// DEMO VULNERABILITY` comments, each with a corresponding deterministic Semgrep rule in `.semgrep.yml`
  - **Intentional UX Issues**: 4 mobile viewport issues (clipped transfer button, misaligned quick action cards, overlapping transaction badge, invalid success messages) for Slack feedback demo
  - **Intentional Kubernetes Bug**: Readiness probe pointing to `/healthz` instead of `/health` to trigger Manifest Remediator demo
  - **Complete Test Suite**: 6 Jest + Supertest tests covering health, dashboard, and transfers
  - **Developer Workflow**: `npm run seed` for local data, `npm run dev` for local server, `npm run semgrep:demo` for SAST scan
  - **Documentation**: Demo story flow, security notes, and remediation guidance under `docs/`
  
- In-scope vs. out-of-scope
  - **In-scope**: Local/demo use only, SQLite database, deterministic vulnerabilities and bugs, clear documentation of intentional issues, Docker and Kubernetes deployment manifests
  - **Out-of-scope**: Production deployment, real authentication, external integrations, real credentials, database migrations beyond seed script, performance optimization

## Value
| Audience | Value |
|---|---|
| Developers | Realistic codebase with Express routes, EJS views, and SQLite integration that mirrors production patterns but in a safe, local context |
| DevOps / Platform | Complete CI/CD integration story with Dockerfile, K8s manifests, health endpoints, smoke tests, and deterministic SAST scan results |
| Security / Admins | 7 intentional vulnerabilities with 1:1 Semgrep rule mapping, demonstrating SAST detection and remediation workflows without risk |
| Executives | End-to-end AI SDLC narrative from code commit through security scanning to production feedback, showcasing platform ROI in a single demo flow |

## Metrics
| Category | Metric | Target / Direction |
|---|---|---|
| Adoption | Number of field teams using DemoBank for AI SDLC demos | 100% of Harness field teams within 1 quarter |
| Quality | Demo success rate (full flow completion without technical issues) | >95% across all demo runs |
| Reliability | SAST scan producing all 7 expected findings | 100% deterministic (no flakes) |
| Productivity | Time to set up and run a full AI SDLC demo | <10 minutes from `git clone` to live demo |

## User Stories
| As a... | I want... | So that... | Acceptance Criteria |
|---|---|---|---|
| Sales Engineer | A banking app with deterministic SAST findings | I can reliably demonstrate Harness AI-driven security scanning in every prospect meeting | `npm run semgrep:demo` produces all 7 findings; each vulnerability has a clear code location and remediation path documented |
| Field Engineer | Intentional UX issues visible on mobile viewports | I can show how Harness captures and surfaces Slack feedback for production UX problems | 4 distinct mobile viewport issues are reproducible at specific screen widths; `docs/demo-story.md` includes Slack prompt examples |
| DevOps Architect | A realistic K8s deployment with an intentional manifest bug | I can demonstrate the Manifest Remediator workflow end-to-end | K8s manifests deploy successfully; readiness probe fails due to `/healthz` vs `/health` mismatch; remediation flow is documented |
| Developer Advocate | Complete documentation of the demo story and safety constraints | I can onboard new field teams to the demo without live walkthrough | `docs/` contains demo story flow, security notes with vulnerability map, and remediation guidance; `README.md` has prominent vulnerability warning |
| Platform Admin | Local development workflow that mirrors CI | I can test changes to the demo app without deploying to shared infrastructure | `npm run seed`, `npm run dev`, `npm test` work locally; Dockerfile builds; all 6 Jest tests pass |

## Dependencies and Open Questions
- **Dependencies**
  - Node.js 20+ runtime for local development
  - SQLite for local database (no external DB required)
  - Semgrep CLI for SAST scanning (or run via CI)
  - Kubernetes cluster for manifest remediation demo (optional — local use works without K8s)
  - Harness platform with AI SDLC features enabled (SAST, Manifest Remediator, Slack integration)
  
- **Open decisions or assumptions**
  - **Assumption**: Demo users will not deploy this application to production or expose it to the internet (vulnerability warning is prominently displayed in `README.md` and PR description)
  - **Assumption**: Semgrep is the SAST tool of choice; `.semgrep.yml` rules are deterministic and produce no false positives/negatives for the 7 intentional vulnerabilities
  - **Open question**: Should the demo app support additional vulnerability types (e.g., deserialization, LDAP injection) for future SAST demo scenarios?
  - **Open question**: Should we provide a Harness pipeline YAML template as part of the demo app repository to accelerate onboarding?
