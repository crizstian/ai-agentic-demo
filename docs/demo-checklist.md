# Demo Flow Checklist — AI-Native SecOps

Última verificación: 2026-09-28

---

## 1. Git State

| Check | Status | Detalle |
|---|---|---|
| Branch actual | ✅ | `secops/ai-agentic-demo` |
| Working = Target branch | ✅ | Ambos en `d2b2399` |
| Local = Remote (origin) | ✅ | Ambos branches pusheados |
| Harness Code remote | ✅ | `harness` configurado, 3 branches pusheadas |
| Uncommitted changes | ⚠️ | Solo docs untracked (no afecta demo) |

---

## 2. App Code — STATE 0

| Check | Status | Detalle |
|---|---|---|
| `ai_assistant.py` ausente | ✅ | Act 1 lo crea |
| Chat widget HTML ausente | ✅ | Act 1 lo agrega |
| Chat widget JS ausente | ✅ | Act 1 lo agrega |
| No import `ai_assistant` en `app.py` | ✅ | Act 1 lo agrega |
| VULN-001: SQL injection | ✅ | String concat en `accounts.py` |
| VULN-002: Command injection | ✅ | `shell=True` en `admin.py` |
| VULN-006: Reflected XSS | ✅ | Unescaped param en `app.py` |
| VULN-007: CORS wildcard | ✅ | `origins="*"` en `app.py` |
| No PII (email/phone) en seed | ✅ | Seed data limpia |
| DB schema TEXT ids | ✅ | Schema original |
| No `requests` en requirements.txt | ✅ | Act 1 lo agrega |
| Solo 2 test files | ✅ | `test_health.py` + `test_dashboard.py` |
| Solo 2 test functions | ✅ | 1 por archivo |

---

## 3. CSS Bugs (Visual Misalignment)

| Check | Status | Detalle |
|---|---|---|
| Cards rotadas/overlapping | ✅ | `transform: rotate()` en `styles.css:115-143` |
| Transfer button off-screen | ✅ | CSS bug en `styles.css:282` |

---

## 4. Deployment Manifest (Act 4.5 Setup)

| Check | Status | Detalle |
|---|---|---|
| `OPENAI_API_KEY` NO en `deployment.yaml` | ✅ | Coding agent lo agrega en Act 1 |
| Comment explica el mecanismo | ✅ | "OPENAI_API_KEY is added by the coding agent in Act 1" |
| ConfigMap NO tiene `OPENAI_API_KEY` | ✅ | Causa `CreateContainerConfigError` intencional |
| `healthCheckPath: "/health"` | ✅ | Normal operation (cambiar a `/healthz` para Manifest Remediator via health check) |

---

## 5. Demo Prompts (`docs/demo-prompts-consolidated.md`)

| Check | Status | Detalle |
|---|---|---|
| `splitio_client` sin `[cpphash]` | ✅ | Fix: evita fallo de build por gcc |
| CSS preservation instruction | ✅ | "IMPORTANTE: solo AGREGA reglas CSS nuevas" |
| OPENAI_API_KEY instruction | ✅ | "agrega env var para OPENAI_API_KEY que lea del ConfigMap" |

---

## 6. Kubernetes Cluster (namespace: `harnessbank-demo-end2end`)

| Check | Status | Detalle |
|---|---|---|
| Node `ai-agentic-demo` | ✅ | 1 nodo Ready |
| Deployment `harnessbank-demo-end2end` | ✅ | 1/1 Running, image `crizstian/harnessbank-demo:3` |
| Deployment `mcp-financial-data` | ✅ | 1/1 Running, image `crizstian/mcp-financial-data:3` |
| ConfigMap | ✅ | 4 keys: APP_NAME, LOG_LEVEL, MCP_SERVER_URL, OPENAI_MODEL (sin OPENAI_API_KEY) |
| Ingress | ✅ | `demobank-ingress` → `demobank-e2e.selatam.harness-demo.site` |
| Service `harnessbank-demo-end2end` | ✅ | LoadBalancer `34.139.219.217:80` |
| Service `mcp-financial-data` | ✅ | ClusterIP `5001` |
| DNS | ✅ | Resuelve a `35.227.123.79` |
| Traceable agent | ✅ | Running (agent + ebpf tracer + runner) |
| Newman traffic generator | ✅ | Running (background traffic) |
| No `OPENAI_API_KEY` env var | ✅ | Deploy limpio, Act 1 lo agrega → Act 4.5 falla intencionalmente |

---

## 7. Harness Platform — Pipelines

| Check | Status | Detalle |
|---|---|---|
| `AI_SDLC_DemoBank` | ✅ | Pipeline principal (INLINE), synced |
| `DemoBank_Reset_Deploy` | ✅ | Reset pipeline (INLINE), sin Jira/canary |
| `kubernetes-remediation` | ✅ | Pipeline K8s remediation (archivo local) |
| `maxTurns: 30` (Quality Agent) | ✅ | Suficientes turnos |

---

## 8. Harness Platform — Triggers

| Check | Status | Pipeline | Detalle |
|---|---|---|---|
| `main_build_deploy_trigger` | ✅ | `AI_SDLC_DemoBank` | Push a `secops/ai-agentic-demo-main` (excluye manifest/QA fixes) |
| `kubernetes_fix_deploy_trigger` | ✅ | `AI_SDLC_DemoBank` | Push con manifest fix o QA UI fix (JEXL match) |
| `pr_validation_trigger` | ✅ | `AI_SDLC_DemoBank` | PR abierto/sync → solo CI (requiere Jira key en título) |
| `manifest_remediation_trigger` | ✅ | `Kubernetes_Remediation` | Custom webhook — deploy falla → pasa `executionUrl` al agent |

---

## 9. Harness Platform — Worker Agents

| Agent | Status | Detalle |
|---|---|---|
| `code_reviewer` (Change Advisor) | ✅ | Evalúa PR: correctness, maintainability, test gaps |
| `ca_code_unit_test_generator` | ✅ | Genera hasta 10 unit tests, 25 max turns |
| `ca_manifest_remediation_v2` | ✅ | Fix K8s manifests, 30 max turns |
| `qa_ui_analyzer` | ✅ | Analiza UI defects de Playwright, crea PR con fix |
| `security_analyzer` | ✅ | Lee SAST+SCA findings, auto-fix top 4 CRITICAL/HIGH |

---

## 10. Harness Platform — Services

| Service | Status | Detalle |
|---|---|---|
| `demobank` | ✅ | Manifest: `CristianConnector`, Docker: `DockerCristian` |
| `mcp_financial_data` | ✅ | Manifest: `CristianConnector`, Docker: `DockerCristian` |

---

## 11. Harness Platform — Connectors

| Connector | Scope | Status | Tipo |
|---|---|---|---|
| `CristianConnector` | Project | ✅ SUCCESS | GitHub (Account) |
| `DockerCristian` | Project | ✅ SUCCESS | Docker Hub |
| `mcp_github_cristian` | Project | ✅ | MCP GitHub |
| `mcp_harness_cristian` | Project | ✅ SUCCESS | MCP Harness |
| `org.se_sandbox_k8s` | Org | ✅ SUCCESS | K8s |
| `account.Harness_JIRA` | Account | ✅ SUCCESS | Jira |
| `CodeRepoCristianRamirez` | Project | ✅ SUCCESS | Git (Harness Code) |

---

## 12. Harness Platform — Environment & Infra

| Resource | Status | Detalle |
|---|---|---|
| Environment `gke_latam` | ✅ | Configurado |
| Infrastructure `latam_nodepool` | ✅ | (verificar dentro del env) |

---

## 13. Reset Script (`scripts/demo-reset.sh`)

| Check | Status | Detalle |
|---|---|---|
| Dynamic test file cleanup | ✅ | `git diff --diff-filter=D` |
| Exclude `node_modules` in grep | ✅ | `--exclude-dir=node_modules --exclude-dir=e2e` |
| Playwright e2e preserved | ✅ | `tests/e2e/` tracked, no borrado por reset |

---

## 14. E2E Tests (Playwright)

| Check | Status | Detalle |
|---|---|---|
| `ui-alignment.spec.js` tracked | ✅ | Spec de UI alignment |
| `playwright.config.js` tracked | ✅ | Config |
| `package.json` tracked | ✅ | Dependencies |

---

## Bloqueantes para el Demo

Ninguno — todo verde. ✅

---

## Secuencia Pre-Demo

1. Ejecutar `scripts/demo-reset.sh --commit --push` — resetear código a STATE 0
2. Ejecutar `DemoBank_Reset_Deploy` pipeline — build + deploy STATE 0
3. Verificar http://demobank-e2e.selatam.harness-demo.site — dashboard con CSS bugs visibles
4. Verificar Jira project HD tiene tickets limpio / no duplicados
5. Copiar prompt de Act 1 desde `docs/demo-prompts-consolidated.md`

---

## Demo Flow (Acts 1-7)

| Act | Descripción | Trigger |
|---|---|---|
| **Act 1** | Coding agent: agrega AI assistant + chat widget + OPENAI_API_KEY env var | Manual (prompt en pipeline) |
| **Act 2** | Pipeline governs: build, test, SLSA, SCS | Auto (PR merge trigger) |
| **Act 3** | Security agent: remedia VULN-001/002/006/007 + nuevas 008/009/010 | Auto (security step en pipeline) |
| **Act 4** | Deploy: canary + CV + governance | Auto (CD stage) |
| **Act 4.5** | ConfigMap error → rollback → Manifest Remediator agent → PR | Auto (deploy failure trigger) |
| **Act 5** | Attacker exploits → Traceable detecta (Monitor mode) | Manual (attack script) |
| **Act 6** | AI SRE responde (12s, 6 actions) | Auto (webhook → runbook) |
| **Act 7** | Block mode + AI Security | Manual (Traceable config) |
