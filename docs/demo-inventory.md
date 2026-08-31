# Inventario Completo — Demo End-to-End (7 Actos)

Status legend: ✅ Existe | ⚠️ Existe parcial | ❌ Falta construir

---

## 1. CODIGO DE LA APLICACION (DemoBank)

### Componentes arquitecturales

| Componente | Descripcion | Status | Archivos |
|-----------|-------------|--------|----------|
| **App principal** | Flask app, blueprints, CORS, XSS, dashboard | ✅ | `app/app.py`, `app/server.py`, `app/config.py`, `app/db.py` |
| **API vulnerable** | Endpoints con SQL injection, command injection, BOLA/IDOR | ✅ | `app/routes/accounts.py`, `app/routes/admin.py` |
| **API Zombie** | `GET /api/ai/status` — debug endpoint sin auth, expone model name + MCP URLs | ✅ | `app/routes/ai_assistant.py:90` |
| **AI Agent (Chatbox)** | `POST /api/ai/chat` — prompt injection, PII leak, MCP tool call | ✅ | `app/routes/ai_assistant.py` |
| **MCP Financial Data Service** | Mock interno port 5001, trafic Este-Oeste dentro del cluster | ✅ | `services/mcp-financial-data/app.py` |

### Archivos de la app

| Archivo | Status | Notas |
|---------|--------|-------|
| `app/app.py` | ✅ | Flask app con CORS wildcard (VULN-007), XSS (VULN-006), blueprint registration |
| `app/db.py` | ✅ | SQLite singleton, schema `id INTEGER PRIMARY KEY` (accounts + transactions) |
| `app/config.py` | ✅ | Config module, port 3000 |
| `app/routes/accounts.py` | ✅ | SQL injection (VULN-001), BOLA/IDOR (VULN-010) |
| `app/routes/admin.py` | ✅ | Command injection (VULN-002) |
| `app/routes/ai_assistant.py` | ✅ | Prompt injection (VULN-008), PII leak (VULN-009), MCP tool call, zombie API `/status` |
| `app/routes/fx.py` | ✅ | FX rates endpoint |
| `app/routes/statements.py` | ✅ | Statements endpoint |
| `app/routes/transfers.py` | ✅ | Transfers endpoint |
| `app/server.py` | ✅ | Server entry point, auto-seed on startup si tabla accounts esta vacia |
| `requirements.txt` | ✅ | Incluye `requests==2.25.1` (CVE-2023-32681) |
| `scripts/seed.py` | ✅ | 5 demo accounts + 8 transactions, idempotente (DELETE antes de INSERT) |

### MCP Financial Data Service (servicio interno)

| Archivo | Status | Notas |
|---------|--------|-------|
| `services/mcp-financial-data/app.py` | ✅ | Flask mock, port 5001, endpoints: POST `/mcp/financial-data`, GET `/mcp/risk-profile/<id>`, GET `/health` |
| `services/mcp-financial-data/Dockerfile` | ✅ | Python 3.12-slim, installs flask, exposes 5001 |

### Vulnerabilidades plantadas

| ID | Tipo | Archivo:Linea | Detectada por SAST | Explota en Act | Status |
|----|------|--------------|-------------------|---------------|--------|
| VULN-001 | SQL Injection | `accounts.py:14` | ✅ Si | Act 3 (fix) | ✅ Existe |
| VULN-002 | Command Injection | `admin.py:18` | ✅ Si | Act 3 (fix) | ✅ Existe |
| VULN-006 | Reflected XSS | `app.py:96` | ✅ Si | Act 3 (fix) | ✅ Existe |
| VULN-007 | Insecure CORS | `app.py:31` | ✅ Si | Act 3 (fix) | ✅ Existe |
| VULN-008 | Prompt Injection | `ai_assistant.py:64` | ❌ No (pasa SAST) | Act 5 ataque, Act 7 AI Sec | ✅ Existe |
| VULN-009 | PII Leak | `ai_assistant.py:77` | ❌ No (pasa SAST) | Act 5 ataque, Act 7 AI Sec | ✅ Existe |
| VULN-010 | BOLA/IDOR | `accounts.py:36` | ❌ No (pasa SAST) | Act 5 ataque | ✅ Existe |
| SCA CVE | Dep vulnerable | `requirements.txt:5` | ✅ SCA | Act 3 (upgrade) | ✅ Existe |

### Semgrep rules

| Rule | Status | Notas |
|------|--------|-------|
| `.semgrep.yml` (7 rules) | ✅ | 7/7 detectan. sql-injection, command-injection, xss, cors, prompt-injection, pii-leak (pattern corregido), bola-idor |

### Tests

| Archivo | Status | Notas |
|---------|--------|-------|
| `tests/conftest.py` | ✅ | Fixtures, in-memory DB |
| `tests/test_health.py` | ✅ | Health endpoint |
| `tests/test_transfers.py` | ✅ | Transfer logic |
| `tests/test_dashboard.py` | ✅ | Dashboard rendering |
| `tests/test_k8s_manifest.py` | ✅ | K8s manifest validation |
| `tests/dashboard-layout.test.js` | ✅ | JS layout test |
| `tests/test_ai_assistant.py` | ✅ | Tests para AI assistant endpoints |
| `tests/test_accounts.py` | ✅ | Tests para accounts endpoints |
| `tests/test_admin.py` | ✅ | Tests para admin endpoints |
| `tests/test_fx.py` | ✅ | Tests para FX rates endpoint |
| `tests/test_statements.py` | ✅ | Tests para statements endpoint |
| `tests/test_seed.py` | ✅ | Tests para seed data |
| `tests/test_db.py` | ✅ | Tests para database module |
| `tests/test_config.py` | ✅ | Tests para config module |
| `tests/test_app_factory.py` | ✅ | Tests para app factory |
| ~47 tests totales | ✅ | Suficiente para TI demo (Act 2) |

### Seed data

| Dato | Status | Notas |
|------|--------|-------|
| 5 cuentas demo | ✅ | Alice Johnson ($50K checking), Bob Smith ($120K savings), Charlie Brown ($75K checking), Diana Martinez ($34.5K checking), Edward Kim ($89K savings) |
| 8 transacciones demo | ✅ | Transfers entre cuentas, incluye memos descriptivos |
| Account IDs: 1, 2, 3, 4, 5 (INTEGER) | ✅ | Alineados con Act 5 attack script. Schema usa `id INTEGER PRIMARY KEY` |
| Auto-seed on startup | ✅ | `server.py` verifica si tabla accounts esta vacia y ejecuta `seed()` automaticamente |

---

## 2. GIT BRANCHES

| Branch | Status | Proposito |
|--------|--------|-----------|
| `main` | ✅ | Branch principal |
| `demo/base` | ❌ | DemoBank SIN ai_assistant (pre-Act 1). Reset point entre demos |
| `demo/completed` | ❌ | DemoBank CON ai_assistant + vulns (post-Act 1). Fallback si Claude Code diverge |
| `demo/remediated` | ❌ | DemoBank con fixes del Remediation Agent (post-Act 3). Para demo de pipeline re-run |

---

## 3. PULL REQUESTS

| PR | Status | Proposito | Acto |
|----|--------|-----------|------|
| PR #52: "feat: add AI banking assistant" | ❌ | Claude Code genera este PR en vivo (o se usa pre-created). Trigger de pipeline | Act 1 → Act 2 |
| PR #52 updated (fix commits) | ❌ | Remediation Agent pushea fixes al mismo branch | Act 3 |

---

## 4. PROMPTS (Copiar/pegar durante la demo)

### Act 1 — Inner Loop

| # | Herramienta | Prompt | Status |
|---|-------------|--------|--------|
| 1 | Claude Code | "Use the Harness MCP tools to give me context on the DemoBank service: what's the current deployment status, any open security findings, and the last pipeline execution result." | ✅ Doc |
| 2 | Claude Code | "Create an AI banking assistant for DemoBank: - Add a new endpoint POST /api/ai/chat that accepts a customer message and returns an AI-powered response with relevant account information - The assistant should query our accounts database for context and call an external MCP financial data service for enrichment - Add a GET /api/ai/status endpoint that shows the assistant's configuration - Register the new routes in the Flask app - Add the requests library to requirements.txt for the external service call" | ✅ Doc |

### Act 2 — Software Delivery Agent

| # | Herramienta | Prompt | Status |
|---|-------------|--------|--------|
| 1 | Harness AI Chat | "Give me a summary of the current pipeline execution for PR #52. What stage is it in, did the tests pass, and how many tests did Test Intelligence select vs the full suite?" | ✅ Doc |
| 2 | Harness AI Chat | "What did the Change Advisor find on PR #52? Show me the risk assessment and recommendations." | ✅ Doc |

### Act 3 — Security Testing Agent

| # | Herramienta | Prompt | Status |
|---|-------------|--------|--------|
| 1 | Harness AI Chat | "The security scan just completed on PR #52. Give me the full findings summary: how many vulnerabilities were found, what types, what severities, and did SCA flag any dependency issues?" | ✅ Doc |
| 2 | Harness AI Chat | "Run triage on the security findings for PR #52. For each finding, show me: CVSS score, EPSS score, reachability status, and whether it's actually exploitable in production." | ✅ Doc |
| 3 | Harness AI Chat | "Trigger the Remediation Agent for the critical and high findings on PR #52. Generate fixes, validate them, and push to the feature branch." | ✅ Doc |
| 4 | Harness AI Chat | "Show me the SBOM and supply chain security summary for this build: dependencies, licenses, known CVEs, attestation status, and SLSA compliance level." | ✅ Doc |

### Act 4 — Deploy Gobernado

| # | Herramienta | Prompt | Status |
|---|-------------|--------|--------|
| 1 | Harness AI Chat | "The deploy stage just started for PR #52. What governance gates need to pass before the deployment executes? Show me SLSA verification, OPA policies, and change management status." | ✅ Doc |
| 2 | Harness AI Chat | "Show me the canary deployment progress for DemoBank. I want to see the Continuous Verification analysis -- what metrics is it comparing, what's the baseline, and what's the automated decision?" | ✅ Doc |

### Act 5 — No prompts (curls del atacante)

### Act 6 — No prompts de demo (AI SRE runbook automatico)

### Act 7 — No prompts de demo (AI Security dashboard walkthrough)

---

## 5. SCRIPTS DE DEMO

| Script | Status | Proposito | Acto |
|--------|--------|-----------|------|
| `scripts/seed.py` | ✅ | Seed data de cuentas y transacciones (5 cuentas, 8 txns, idempotente) | Setup |
| `scripts/smoke-test.sh` | ✅ | Smoke test de la app | Setup |
| `scripts/attack-chain.sh` | ✅ | Script interactivo del ataque (5 pasos con curls) | Act 5 |
| `scripts/demo-reset.sh` | ✅ | Reset entre demos: checkout demo/base, seed DB, verify MCP | Setup |
| `scripts/prompt-cards.md` | ✅ | Tarjetas con todos los prompts listos para copiar/pegar | All Acts |

---

## 6. INFRAESTRUCTURA

### Docker Images

| Imagen | Dockerfile | Status | Notas |
|--------|-----------|--------|-------|
| `demobank` | `Dockerfile` | ✅ | Python 3.12-slim, CMD `python -m app.server`, port 3000 |
| `mcp-financial-data` | `services/mcp-financial-data/Dockerfile` | ✅ | Python 3.12-slim, flask, port 5001 |
| Container registry (GAR/ECR/DockerHub) | — | ❌ Config | Para push/pull de ambas imagenes |

### Kubernetes — Topologia de despliegue

```
namespace: harnessbank-demo
├── Deployment: demobank (app principal)
│   ├── Container: demobank (port 3000)
│   └── Service: harnessbank-demo (LoadBalancer, 80→3000)
│
├── Deployment: mcp-financial-data (servicio interno)
│   ├── Container: mcp-financial-data (port 5001)
│   └── Service: mcp-financial-data (ClusterIP, 5001) ← solo trafico E-W
│
├── DaemonSet: traceable-agent (Runtime Protection Agent)
│   ├── TA_CAPTURE_EAST_WEST=true
│   ├── TA_AI_SECURITY_ENABLED=true
│   └── Secret: traceable-config (reporting-endpoint + api-token)
│
├── Ingress: demobank-ingress (nginx)
│   ├── host: demobank.app
│   └── paths: /api/accounts, /api/ai, /api/admin, /
│
└── ConfigMap: demobank-config (PORT=3000, NODE_ENV=demo)
```

### Kubernetes — Manifests

| Recurso | Archivo | Status | Notas |
|---------|---------|--------|-------|
| Namespace | `deploy/k8s/base/namespace.yaml` | ✅ | `harnessbank-demo` |
| DemoBank Deployment | `deploy/k8s/demobank/deployment.yaml` | ✅ | Helm-template con `{{ .Values.* }}`, usa `<+artifact.image>` |
| DemoBank Service | `deploy/k8s/demobank/service.yaml` | ✅ | LoadBalancer, port 80→3000 |
| ConfigMap | `deploy/k8s/base/configmap.yaml` | ✅ | PORT=3000, NODE_ENV=demo |
| Values | `deploy/k8s/demobank/values.yaml` | ✅ | replicas 1, resources, healthCheckPath toggleable |
| MCP Service Deployment | `deploy/k8s/mcp-financial-data/deployment.yaml` | ✅ | Port 5001, labels `tier: internal, component: mcp-tool` |
| MCP Service Service | `deploy/k8s/mcp-financial-data/service.yaml` | ✅ | **ClusterIP** (solo trafico E-W, no expuesto externamente) |
| Ingress | `deploy/k8s/ingress/ingress.yaml` | ✅ | nginx, host `demobank.app`, rutas /api/accounts, /api/ai, /api/admin |
| Traceable Agent DaemonSet | `deploy/k8s/traceable/traceable-agent.yaml` | ✅ | TPA con NET_RAW + NET_ADMIN, Secret para token |
| K8s cluster real | — | ❌ | Necesario para Acts 4-7 (canary deploy, CV, WAAP, AI Security) |

### Apigee API Manager

El API Manager se usa para demostrar la objecion CISO #4: "Ya tengo Apigee/Kong como API Gateway". El punto de la demo es mostrar los blind spots de un API Manager tradicional.

| Recurso | Archivo | Status | Notas |
|---------|---------|--------|-------|
| API Proxy Spec | `deploy/apigee/apiproxy-spec.yaml` | ✅ | Define registered vs unregistered endpoints con policies |
| Apigee README | `deploy/apigee/README.md` | ✅ | Arquitectura, opciones de deploy (Apigee X / mock gateway), tablas de endpoints |
| Apigee X (GCP) o mock gateway | — | ❌ Config | Opcion A: Apigee X real. Opcion B: cualquier API gateway con misma config |

#### Endpoints registrados en Apigee (PROTEGIDOS)

| Endpoint | Policies | Notas |
|----------|----------|-------|
| `/accounts` | API key + rate-limit-100 | CRUD de cuentas |
| `/ai/chat` | API key + rate-limit-30 + request-size-limit | AI chat endpoint |
| `/admin/ping` | API key + IP whitelist | Health check admin |
| `/fx` | Open (rate-limit-500) | Public rates |

#### Endpoints NO registrados en Apigee (BLIND SPOTS)

| Endpoint | Por que no esta registrado | Impacto en demo |
|----------|---------------------------|-----------------|
| `/api/ai/status` | Zombie API — debug endpoint que el dev olvido quitar | **Act 5**: atacante descubre model name + MCP URLs |
| `/api/accounts/{id}/details` | Endpoint agregado post-launch, nunca registrado en gateway | **Act 5**: BOLA/IDOR sin rate limiting |

#### API Manager vs WAAP — Lo que demuestra la demo

| Capacidad | API Manager (Apigee) | WAAP (Traceable) |
|-----------|---------------------|------------------|
| Endpoints registrados | ✅ Protege | ✅ Protege |
| Endpoints NO registrados (zombie) | ❌ No ve | ✅ Auto-discovery |
| Trafico N-S (ingress) | ✅ Inspecciona | ✅ Inspecciona |
| Trafico E-W (service-to-service) | ❌ No ve | ✅ Captura (TPA DaemonSet) |
| Contenido semantico (prompt injection) | ❌ No parsea | ✅ AI content inspection |
| Correlacion de sesion (7 dias) | ❌ Request-level | ✅ Session stitching |
| Rate limiting | ✅ Per-endpoint | ✅ Behavioral + per-actor |
| API key / OAuth validation | ✅ | ❌ (complementario) |

### Observabilidad

| Recurso | Status | Notas |
|---------|--------|-------|
| Prometheus | ❌ | Metricas para Continuous Verification (Act 4) |
| Grafana dashboards | ❌ | Visual health (Act 4 — "todo verde") |
| Metric endpoints en la app | ❌ | Latency p99/p50, error rate, throughput para CV |

### Base de datos

| Recurso | Status | Notas |
|---------|--------|-------|
| SQLite (dev/demo local) | ✅ | `app/db.py` con file-based (`demobank.db`) |
| Schema: accounts (INTEGER PK) + transactions | ✅ | Creada en `init_db()` |
| Seed data | ✅ | 5 cuentas, 8 transacciones, auto-seed en startup |

---

## 7. HARNESS PLATFORM — Capabilities por Acto

### Act 1: Inner Loop

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| Harness MCP Server | MCP | ❌ Config | Conectar Claude Code a Harness via MCP tools |
| Harness IDE Extension (VS Code) | Extension | ❌ Config | Sidebar con pipeline status, findings |
| Harness AI Chat Agent (VS Code) | Extension | ❌ Config | Conversational interface en IDE |

### Act 2: Software Delivery Agent

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| Pipeline "PR-Validation" | Pipeline | ❌ | Auto-trigger on PR creation |
| Stage: CI Build | Pipeline Stage | ❌ | Checkout, build, test |
| Test Intelligence (TI) | Feature | ❌ Config | AI test selection (requiere 47+ tests) |
| Stage: Change Advisor | Pipeline Stage | ❌ | Expert Agent, risk assessment, PR comment |
| Stage: Security Scan | Pipeline Stage | ❌ | Orchestrate scanners |
| Stage: Deploy | Pipeline Stage | ❌ | Queued until security passes |
| GitHub integration | Integration | ❌ Config | PR auto-trigger, Change Advisor comments |

### Act 3: Security Testing Agent

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| STO (Security Testing Orchestration) | Feature | ❌ Config | Orquesta Semgrep + AI SAST |
| AI SAST (Qwiet) | Scanner | ❌ Config | Confidence scoring, data-flow analysis |
| Semgrep scanner | Scanner | ⚠️ | `.semgrep.yml` existe (7/7 rules detecting), necesita step en pipeline |
| SCA | Scanner | ❌ Config | Dependency CVE detection |
| SCS (Supply Chain Security) | Feature | ❌ Config | SBOM generation (CycloneDX/SPDX) |
| SLSA Attestation | Feature | ❌ Config | Cosign signing, SLSA Level 2 |
| Triage Agent | Expert Agent | ❌ Config | CVSS + EPSS + reachability |
| Remediation Agent | Worker Agent | ❌ Config | Fix generation, validation, PR push |
| OPA Policy: "No critical findings" | Policy | ❌ | Pipeline gate que bloquea con findings critical |

### Act 4: Deploy Gobernado

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| SLSA Verification (pre-deploy) | Feature | ❌ Config | Verifica attestation antes de deploy |
| OPA Policies (4 policies) | Policies | ❌ | security-scan-required, slsa-attestation-required, deploy-window-check, approval-requirements |
| Change Management | Integration | ❌ Config | ServiceNow o Jira auto-ticket |
| Canary Deployment | Strategy | ❌ Config | 10% → 25% → 100% |
| Continuous Verification | Feature | ❌ Config | ML comparison canary vs baseline |
| Metric provider integration | Integration | ❌ Config | Prometheus/Datadog/New Relic |

### Act 5: El Ataque (Shield Right)

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| Runtime Protection Agent (WAAP) | Agent | ❌ Config | Traceable integration |
| API Discovery | Feature | ❌ Config | Auto-discover endpoints + zombie APIs |
| Behavioral Baseline Detection | Feature | ❌ Config | N-S + E-O anomaly detection |
| Session Stitching | Feature | ❌ Config | 7-day correlation window |
| Threat Scoring | Feature | ❌ Config | Risk escalation (35 → 65 → 85) |
| Blocking Policies | Feature | ❌ Config | Auto-block threat actors |
| Virtual Patching | Feature | ❌ Config | Protection policies sin cambio de codigo |
| Data Protection (PII) | Feature | ❌ Config | Detect PII in responses |

### Act 6: Shield Right + Shift Left

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| AI SRE | Feature | ❌ Config | Incident management + runbooks |
| AI SRE Runbook "security-incident-response" | Runbook | ❌ | 6 steps: Slack, PagerDuty, Jira, HTTP Request (Remediation Tracker API), Zoom, Slack |
| Alert Rule (WAAP → AI SRE) | Alert | ❌ Config | Trigger: security incident from Runtime Protection Agent |
| Remediation Tracker (SCS) | Feature | ❌ Config | Track artifacts across environments |
| Remediation Tracker API | API | ❌ Config | `POST /v1/orgs/{org}/projects/{project}/remediations` |
| SBOM Analysis (blast radius) | Feature | ❌ Config | Cross-service dependency analysis |
| SBOM Policy (deny list) | Policy | ❌ | Deny list: `requests < 2.31.0` |
| OPA Policy: "block-unprotected-ai-endpoints" | Policy | ❌ | Blocks AI endpoints sin auth |

### Act 7: AI Security

| Capability | Tipo | Status | Notas |
|-----------|------|--------|-------|
| AIBOM (AI Bill of Materials) | Feature | ❌ Config | SCS capability, v1.65.0 (Jul 2026) |
| AI Discovery | Feature | ❌ Config | Runtime Protection Agent — AI APIs + MCP assets |
| MCP Risk Score | Feature | ❌ Config | Multi-factor risk scoring per AI asset |
| AI Security Testing (Beta) | Feature | ❌ Config | OWASP LLM Top 10 testing |
| AI Security Dashboard | Dashboard | ❌ Config | Centralized AI security posture view |

---

## 8. INTEGRACIONES EXTERNAS

| Integracion | Usada en Act | Status | Notas |
|------------|-------------|--------|-------|
| **GitHub** | 1, 2, 3 | ⚠️ | Repo existe (`luisredda/ai-agentic-demo`). Necesita PR trigger config en Harness |
| **Slack** | 6 | ❌ Config | Canal `#security-incidents` para AI SRE runbook |
| **PagerDuty** | 6 | ❌ Config | Service `security-oncall` para AI SRE runbook |
| **Jira** | 6 | ❌ Config | Project `SEC` para AI SRE runbook + Remediation Tracker |
| **Zoom** | 6 | ❌ Config | Incident bridge para AI SRE runbook |
| **ServiceNow** | 4 | ❌ Config | Change Management auto-ticket (o Jira alternativa) |
| **Prometheus** | 4 | ❌ Config | Metrics provider para Continuous Verification |
| **Container Registry** | 3, 4 | ❌ Config | Docker Hub / GAR / ECR para artifacts |
| **Claude Code** | 1 | ✅ | Coding agent (external, already available) |
| **Harness MCP** | 1 | ❌ Config | MCP server conectando Claude Code → Harness |
| **Traceable (WAAP)** | 5, 7 | ⚠️ | Manifest del agent existe (`deploy/k8s/traceable/traceable-agent.yaml`). Falta: token, cuenta Traceable, config |
| **Apigee / API Gateway** | 5 | ⚠️ | Proxy spec existe (`deploy/apigee/apiproxy-spec.yaml`). Falta: deploy en Apigee X o mock gateway |

---

## 9. OPA POLICIES (.rego files)

| Policy | Acto | Status | Proposito |
|--------|------|--------|-----------|
| `no-critical-findings.rego` | 3 | ✅ | Bloquea pipeline si hay findings SAST critical |
| `security-scan-required.rego` | 4 | ✅ | Requiere security scan antes de deploy |
| `slsa-attestation-required.rego` | 4 | ✅ | Requiere SLSA attestation en artifact |
| `block-unprotected-ai-endpoints.rego` | 6 | ✅ | Bloquea AI endpoints sin auth o con prompt injection |

---

## 10. AI SRE RUNBOOK

| Componente | Status | Notas |
|-----------|--------|-------|
| Runbook: "security-incident-response" | ❌ | 6 steps |
| Trigger: `incident.severity in [SEV0, SEV1] AND incident.type == "Security Incident"` | ❌ | CEL expression |
| Step 1: Slack → `#security-incidents` | ❌ | Post message con incident details |
| Step 2: PagerDuty → `security-oncall` | ❌ | Page service |
| Step 3: Jira → Project SEC, Type Incident | ❌ | Create issue |
| Step 4: HTTP Request → SCS Remediation Tracker API | ❌ | `POST /v1/.../remediations` |
| Step 5: Zoom → Create meeting | ❌ | Incident bridge |
| Step 6: Slack → `#security-incidents` | ❌ | Post resumen con zoom URL |

---

## 11. DEMO ENVIRONMENT SETUP

### Full Requirements (Demo Completo)

| Componente | Necesario para | Priority |
|-----------|---------------|----------|
| Harness account con STO, SCS, CI, CD, SRM (AI SRE), WAAP | Todos los actos | P0 |
| K8s cluster con 3+ nodes | Acts 4-7 | P0 |
| Prometheus + CV configurado | Act 4 | P1 |
| Traceable (WAAP) agent en K8s | Acts 5, 7 | P0 |
| Apigee X o mock API gateway | Act 5 (CISO #4 objection) | P1 |
| MCP Financial Data Service mock | Acts 1, 5, 7 | ✅ Codigo listo |
| Slack workspace con canal + Harness integration | Act 6 | P1 |
| PagerDuty service | Act 6 | P2 (puede simularse) |
| Jira project SEC | Act 6 | P1 |
| Zoom integration | Act 6 | P2 (puede omitirse) |
| ServiceNow o Jira para Change Mgmt | Act 4 | P2 (puede simularse) |
| Container registry (GAR/ECR/DockerHub) | Acts 3-4 | P0 |
| Claude Code con MCP configurado | Act 1 | P0 |
| VS Code con Harness Extension + AI Chat Agent | Acts 1-4 | P0 |
| 47+ tests en el repo (para TI demo) | Act 2 | ✅ Listo |

> **Unico fallback**: si un componente no esta disponible en vivo, mostrar grabaciones de runs previos de la demo. No hay modo parcial — la demo se ejecuta completa o se usa video de un run anterior.

---

## 12. ARTEFACTOS DE DEMO (assets estaticos)

| Artefacto | Status | Proposito | Acto |
|-----------|--------|-----------|------|
| Jira ticket mockup (JIRA-4521) | ❌ | Screenshot o card del requerimiento | Act 1 |
| SBOM sample (CycloneDX JSON) | ❌ | SBOM pre-generado con 47 deps para mostrar | Act 3 |
| SLSA attestation sample | ✅ | Evidence de SLSA L2 para mostrar (`docs/samples/slsa-provenance.json`) | Act 4 |
| Change ticket mockup (CHG-2024-08271) | ❌ | Screenshot o card de auto-generated ticket | Act 4 |
| WAAP dashboard screenshots | ❌ | Fallback si WAAP no esta live | Act 5 |
| AI SRE runbook screenshots | ❌ | Fallback si AI SRE no esta live | Act 6 |
| Remediation Tracker screenshots | ❌ | Fallback si SCS no esta live | Act 6 |
| AIBOM sample (CycloneDX JSON) | ✅ | AIBOM pre-generado con 4 AI components (`docs/samples/aibom-demobank.json`) | Act 7 |
| AI Security Dashboard screenshots | ❌ | Fallback si AI Security no esta live | Act 7 |

---

## 13. DOCUMENTACION DE DEMO

| Doc | Status | Proposito |
|-----|--------|-----------|
| `docs/acts/act-1-inner-loop.md` | ✅ | Guia completa Act 1 |
| `docs/acts/act-2-software-delivery-agent.md` | ✅ | Guia completa Act 2 |
| `docs/acts/act-3-security-testing-agent.md` | ✅ | Guia completa Act 3 |
| `docs/acts/act-4-deploy-gobernado.md` | ✅ | Guia completa Act 4 |
| `docs/acts/act-5-el-ataque-shield-right.md` | ✅ | Guia completa Act 5 (incluye CISO #4 Apigee objection) |
| `docs/acts/act-6-shield-right-shift-left.md` | ✅ | Guia completa Act 6 |
| `docs/acts/act-7-ai-security-proteger-el-ai.md` | ✅ | Guia completa Act 7 |
| `docs/ai-demo-storyline.md` | ✅ | Storyline master con arco narrativo |
| `docs/demo-story.md` | ✅ | Demo story original |
| `docs/demo-inventory.md` | ✅ | Este documento |
| `docs/architecture-diagrams.md` | ✅ | Diagramas de arquitectura |
| `docs/infrastructure-requirements.md` | ✅ | Requisitos de infraestructura |
| `scripts/prompt-cards.md` | ✅ | Todos los prompts listos para copiar/pegar |
| `docs/demo-setup-guide.md` | ❌ | Guia de setup del ambiente completo |
| `docs/demo-reset-checklist.md` | ❌ | Checklist de reset entre demos |

---

## 14. RESUMEN EJECUTIVO — QUE HAY vs QUE FALTA

### ✅ Lo que EXISTE (listo para usar)

1. **App DemoBank completa** — Flask, SQLite, 10 vulnerabilidades plantadas, 5 cuentas seed, auto-seed on startup
2. **4 componentes arquitecturales** — App principal, API vulnerable, API Zombie (`/api/ai/status`), AI Agent Chatbox (`/api/ai/chat`)
3. **MCP Financial Data Service** — Mock completo (Flask port 5001) con Dockerfile y K8s manifests (ClusterIP para trafico E-W)
4. **Semgrep rules** — 7/7 rules custom detectando (pattern PII leak corregido)
5. **K8s manifests completos** — namespace, deployment, service, configmap, values, ingress, MCP service, Traceable agent DaemonSet
6. **Apigee API proxy spec** — Registered vs unregistered endpoints, policies, README con arquitectura
7. **Traceable agent manifest** — DaemonSet con E-W capture + AI Security enabled
8. **Docker images** — Dockerfiles para DemoBank y MCP Financial Data Service
9. **7 guias de actos** — documentacion completa con talk tracks, prompts, timelines
10. **Storyline master** — arco narrativo de 7 actos
11. **CISO #4 objection (Apigee)** — Integrada en Act 5 con tabla comparativa API Manager vs WAAP
12. **DevContainer config** — para desarrollo local
13. **Attack script** — `scripts/attack-chain.sh` con 5 pasos interactivos de ataque (Act 5)
14. **47 tests** — cobertura completa para Test Intelligence demo (Act 2)
15. **4 OPA policies** — `policies/` directory: no-critical-findings, security-scan-required, slsa-attestation-required, block-unprotected-ai-endpoints
16. **Prompt cards** — `scripts/prompt-cards.md` con todos los prompts listos para copiar/pegar
17. **Demo reset script** — `scripts/demo-reset.sh` para reset entre demos
18. **AIBOM sample** — `docs/samples/aibom-demobank.json` con 4 AI components (Act 7)
19. **SLSA attestation sample** — `docs/samples/slsa-provenance.json` evidence de SLSA L2 (Act 4)
20. **Architecture diagrams** — `docs/architecture-diagrams.md` con diagramas de la arquitectura
21. **Infrastructure requirements** — `docs/infrastructure-requirements.md` con requisitos de infraestructura

### ❌ Lo que FALTA (debe construirse)

#### Priority 0 — Sin esto no corre la demo

| # | Que | Esfuerzo estimado | Status anterior |
|---|-----|-------------------|----------------|
| 1 | **Git branches** (`demo/base`, `demo/completed`) | 1 hora | ❌ |
| 2 | **Pipeline "PR-Validation"** en Harness (CI Build + Security Scan + Deploy) | 4-6 horas | ❌ |
| 3 | **Harness MCP config** para Claude Code | 1 hora | ❌ |
| 4 | **K8s cluster** con DemoBank + MCP service + Traceable agent deployados | 2-3 horas | ❌ |
| 5 | **Container registry** + Docker image build (2 images: demobank + mcp-financial-data) | 1-2 horas | ❌ |
| 6 | **Traceable (WAAP)** token + cuenta + config en cluster | 2-4 horas | ❌ |

#### Priority 1 — La demo funciona pero pierde impacto sin esto

| # | Que | Esfuerzo estimado | Status anterior |
|---|-----|-------------------|----------------|
| 7 | **STO config** (Semgrep + AI SAST en pipeline) | 2-3 horas | ❌ |
| 8 | **SCS config** (SBOM + attestation en pipeline) | 2-3 horas | ❌ |
| 9 | **AI SRE runbook** "security-incident-response" | 2-3 horas | ❌ |
| 10 | **Prometheus + CV config** | 2-3 horas | ❌ |
| 11 | **Jira project SEC** + Harness integration | 1-2 horas | ❌ |
| 12 | **Slack integration** para AI SRE | 1 hora | ❌ |
| 13 | **Apigee X o mock API gateway** deploy | 2-3 horas | ❌ |
| 14 | **VS Code Extension + AI Chat Agent** config | 1 hora | ❌ |

#### Priority 2 — Nice to have, puede simularse

| # | Que | Esfuerzo estimado | Status anterior |
|---|-----|-------------------|----------------|
| 15 | **PagerDuty integration** | 1 hora | ❌ |
| 16 | **Zoom integration** | 1 hora | ❌ |
| 17 | **ServiceNow** change management | 2-3 horas | ❌ |
| 18 | **Screenshot pack** (WAAP, AI Security, AI SRE, Remediation Tracker) | 2-3 horas | ❌ |
| 19 | **Demo setup guide** doc | 2 horas | ❌ |

### Items COMPLETADOS en esta iteracion

| # | Que | Era P0 |
|---|-----|--------|
| ~~9~~ | ~~Account ID alignment~~ (seed.py → IDs numericos 1-5, schema INTEGER) | Si |
| ~~2~~ | ~~MCP Financial Data Service mock~~ (app.py + Dockerfile + K8s manifests) | Si |
| — | **Semgrep PII leak rule fix** (7/7 rules detecting) | — |
| — | **Seed data expansion** (3→5 cuentas, 5→8 txns, idempotente, auto-seed) | — |
| — | **K8s Ingress manifest** (nginx, host demobank.app) | — |
| — | **Traceable agent DaemonSet manifest** (E-W + AI Security) | — |
| — | **Apigee API proxy spec** (registered vs unregistered endpoints) | — |
| — | **CISO #4 objection** (API Manager blind spots, integrada en Act 5) | — |
| — | **Act 7 completo** (AI Security — 4 steps, mockups, talk tracks) | — |
| ~~7~~ | **Attack script** (`scripts/attack-chain.sh`) — 5 pasos interactivos | Si (P0) |
| ~~8~~ | **47 tests** — cobertura completa para Test Intelligence demo | Si (P1) |
| ~~9~~ | **4 OPA policies** — no-critical-findings, security-scan-required, slsa-attestation-required, block-unprotected-ai-endpoints | Si (P1) |
| ~~17~~ | **Prompt cards** (`scripts/prompt-cards.md`) | Si (P1) |
| ~~18~~ | **Demo reset script** (`scripts/demo-reset.sh`) | Si (P1) |
| ~~23~~ | **AIBOM sample** (`docs/samples/aibom-demobank.json`) | Si (P2) |
| ~~26~~ | **SLSA attestation sample** (`docs/samples/slsa-provenance.json`) | Si (P2) |
| — | **Architecture diagrams** (`docs/architecture-diagrams.md`) | — |
| — | **Infrastructure requirements** (`docs/infrastructure-requirements.md`) | — |

### Esfuerzo total estimado (actualizado)

| Priority | Items | Esfuerzo |
|----------|-------|----------|
| P0 | 6 items | ~11-16 horas |
| P1 | 8 items | ~13-19 horas |
| P2 | 5 items | ~8-11 horas |
| **Total** | **19 items** | **~32-46 horas** |

### Orden de construccion sugerido

```
FASE 1: Fundacion (P0, ~2-3 dias)
├── Git branches (demo/base, demo/completed)
├── Container registry + build 2 Docker images (demobank + mcp-financial-data)
├── K8s cluster + deploy: DemoBank, MCP service, Ingress
├── Traceable (WAAP) agent deploy + config
├── Harness MCP config para Claude Code
└── Pipeline basico (CI Build)

FASE 2: Pipeline completo (P1, ~3 dias)
├── Pipeline stages (Security Scan, Deploy)
├── STO config (Semgrep + AI SAST)
├── SCS config (SBOM + attestation)
├── Prometheus + CV
└── VS Code Extension config

FASE 3: Shield Right + Integraciones (P1, ~2 dias)
├── AI SRE runbook
├── Alert Rule (WAAP → AI SRE)
├── Slack + Jira integrations
└── Apigee X o mock gateway deploy

FASE 4: Polish (P2, ~2 dias)
├── Screenshot pack (fallbacks)
├── Demo setup guide
└── ServiceNow / PagerDuty / Zoom (optional)
```
