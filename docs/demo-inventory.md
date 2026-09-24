# Inventario Completo — AI-Native SecOps Demo (7 Actos)

> Ultima actualizacion: 2026-09-24
> Branch: `secops/ai-agentic-demo` | Proyecto Harness: `sandbox / CristianRamirez`

---

## 1. Harness Platform

### 1.1 AI Agents (4)

| Agent | Identifier | Rol | Acto | Model |
|-------|-----------|-----|------|-------|
| Change Advisor | `code_reviewer` | Code review + risk assessment + coverage detection | Act 2 | claude-sonnet-4-6 |
| Quality Agent | `ca_code_unit_test_generator` | Genera unit tests faltantes | Act 2 | claude-sonnet-4-6 |
| Security Remediator | `security_analyzer` | Detecta + remedia vulnerabilidades SAST | Act 3 | claude-sonnet-4-6 |
| Manifest Remediator | `ca_manifest_remediation_v2` (v1.0.5) | Diagnostica deploy fallido, crea PR, merge, re-deploy | Act 4.5 | claude-sonnet-4-6 |

Todos los agents usan:
- Image: `harness/harness-ai-agent:0.1.77`
- LLM Connector: `account.harnessAnthropic`
- MCP Connectors: `mcp_harness_cristian` + `mcp_github_cristian`
- Auth: `<+secrets.getValue("CristianGithub")>`

### 1.2 Pipelines (2)

#### AI SDLC DemoBank (`AI_SDLC_DemoBank`) — Pipeline principal

| Stage | Tipo | Contenido |
|-------|------|-----------|
| **Build (CI)** | CI | Docker build (2 images), unit tests, SAST (Semgrep 7 rules), SBOM (CycloneDX), SLSA provenance, artifact signing (Sigstore keyless), AI Code Review agent, AI Unit Test Generator agent, AI Security Remediator agent |
| **Deploy DemoBank** | CD | Canary deploy (K8s), SCS enforcement (SBOM, SLSA verification, artifact verification), AI SRE deploy notification |
| **Deploy MCP** | CD | Deploy MCP Financial Data service, SCS enforcement, Feature Flag progressive rollout (FME steps: QA -> Beta -> GA -> Full) |
| **External Traffic** | CD | Deploy Newman traffic generator pod (2 containers: general + AI traffic) |

Variables clave:
- `imageTag`: `<+input>.default(<+pipeline.sequenceId>)` — agent puede override para deploy-only re-runs
- `allowStageExecutions: true` — permite ejecutar stages individuales
- `fixedInputsOnRerun: true`

#### Kubernetes Remediation (`Kubernetes_Remediation`) — Pipeline del agent

| Stage | Tipo | Contenido |
|-------|------|-----------|
| **AI Agentic Remediation** | Custom | Step Group con Manifest Remediator agent, infra `org.se_sandbox_k8s` namespace `default` |

Input: `executionUrl` (URL de la ejecucion fallida)

### 1.3 Triggers (3)

| Trigger | Tipo | Evento | Filtros JEXL |
|---------|------|--------|-------------|
| `pr_validation_trigger` | GitHub Webhook | PR hacia `secops/ai-agentic-demo` | `jexlCondition`: excluye "Fix Kubernetes manifest" en titulo; payload: `sourceBranch != fix/manifest-remediation` |
| `main_build_deploy_trigger` | GitHub Webhook | Push a `secops/ai-agentic-demo-main` | `jexlCondition`: excluye "Fix Kubernetes manifest" en commit message |
| `manifest_remediation_trigger` | Custom Webhook | Evento `Kubernetes_Remediation` | Invocado por AI SRE webhook |

### 1.4 Services (5)

| Service | Identifier | Tipo | Imagen / Chart | Manifests |
|---------|-----------|------|----------------|-----------|
| DemoBank | `demobank` | Kubernetes | `crizstian/harnessbank-demo` (DockerHub) | `deploy/k8s/demobank/` (configmap, deployment, service, ingress) |
| MCP Financial Data | `mcp_financial_data` | Kubernetes | `crizstian/mcp-financial-data` (DockerHub) | `deploy/k8s/mcp-financial-data/` |
| Traceable Agent (TPA) | `traceable_agent` | NativeHelm | `traceable-agent` chart v1.71.2 | Helm values inline (token, endpoint, environment, clusterName) |
| Traceable eBPF Tracer | `traceable_ebpf_tracer` | NativeHelm | `traceable-ebpf-tracer` chart | Helm repo |
| Traceable AST Runner | `traceable_ast_runner` | NativeHelm | `traceable-runner` chart v2.7.0 | Helm repo |

Connector de artifacts: `DockerCristian` (Docker Hub)
Connector de manifests: `CristianConnector` (GitHub)
Branch de manifests: `secops/ai-agentic-demo-main`

### 1.5 Environment e Infrastructure

| Recurso | Identifier | Detalle |
|---------|-----------|---------|
| Environment | `gke_latam` | PreProduction, SecOps AI Agentic Demo |
| Infrastructure (K8s) | `latam_nodepool` | KubernetesDirect, namespace `harnessbank-demo-end2end`, connector `selatam` |
| Infrastructure (Helm) | `latam_nodepool_helm` | KubernetesDirect (para NativeHelm deploys de Traceable) |

### 1.6 Connectors (8 relevantes de 27)

| Connector | Tipo | Proposito | Status |
|-----------|------|-----------|--------|
| `selatam` | Kubernetes | Conexion al cluster GKE `se-sandbox` (delegate) | SUCCESS |
| `CristianConnector` | GitHub | Acceso al repo source | SUCCESS |
| `DockerCristian` | Docker Registry | Docker Hub push/pull | SUCCESS |
| `mcp_harness_cristian` | MCP | Harness MCP para AI agents | SUCCESS |
| `mcp_github_cristian` | MCP | GitHub MCP para AI agents | SUCCESS |
| `traceableai_helm_repo` | HTTP Helm | `https://helm.traceable.ai` | SUCCESS |
| `selatamprom` | Prometheus | Metricas para monitoring | SUCCESS |
| `CodeRepoCristianRamirez` | Code Repo | Harness Git Experience | SUCCESS |

### 1.7 Secrets (6 relevantes de 55)

| Secret | Proposito |
|--------|-----------|
| `CristianGithub` | GitHub PAT — agent operations, pipeline auth |
| `traceable_agent_token` | Traceable TPA agent authentication |
| `traceable_platform_token` | Traceable platform API token |
| `aisre_deploy_webhook_url` | AI SRE deploy notification webhook URL |
| `aisre_build_webhook_url` | AI SRE build notification webhook URL |
| `harRegistryToken` | Harness container registry auth |

### 1.8 Feature Flags (FME / Split)

| Flag | SDK | Scope | Key |
|------|-----|-------|-----|
| `ai_chat_enabled` | Split Browser JS SDK (`@splitsoftware/splitio-browserjs`) | Frontend (`dashboard.html`) | `cl0bl351743733kglfasq85pr2kq8ul9rmqv` |
| `ai_chat_backend` | `splitio_client` Python SDK | Backend (`ai_assistant.py`) | `v4kvjbb2cuupu0ihed20iceumvv1m9po07bn` |

Progressive rollout en pipeline (Deploy MCP stage):
1. QA Testers (segments) — Frontend + Backend
2. Beta Users (segments) — Frontend + Backend
3. GA Rollout (90/10) — Frontend + Backend
4. Full Rollout (100/0) — Frontend + Backend
5. Rollback: ambos flags a 100% off + K8s rollback

---

## 2. Google Cloud / GKE

| Recurso | Valor |
|---------|-------|
| GCP Project | `sales-209522` |
| GKE Cluster | `se-sandbox` |
| Region | `us-east1-b` |
| GKE Version | `1.34.x` |
| Node Pool | `ai-agentic-demo-nodepool` |
| Machine Type | `e2-standard-4` |
| Autoscaling | 1-2 nodes |
| Node Label | `scope: ai-agentic-demo` |
| Node Taint | `dedicated=ai_agentic_demo_space:NoSchedule` |
| Service Account | `sales-demo-admin@sales-209522.iam.gserviceaccount.com` |
| IaC | `iac/gke-nodepool/ai-agentic-demo.tfvars.json` |

---

## 3. Kubernetes Resources

### Namespace: `harnessbank-demo-end2end`

| Resource | Tipo | Proposito | Archivos |
|----------|------|-----------|----------|
| `harnessbank-demo-end2end-config` | ConfigMap | App config. Bug intencional: key `AI_MODEL` pero deployment referencia `OPENAI_MODEL` | `deploy/k8s/demobank/configmap.yaml` |
| DemoBank | Deployment + Service | App Flask principal, canary deploy, `progressDeadlineSeconds: 20` | `deploy/k8s/demobank/deployment.yaml`, `service.yaml` |
| MCP Financial Data | Deployment + Service (ClusterIP) | Servicio MCP interno, solo trafico E-W | `deploy/k8s/mcp-financial-data/` |
| Newman Traffic | Deployment (2 containers) | Traffic generator: general (30s cycle) + AI (15s cycle) | `deploy/k8s/newman-traffic/` |
| Ingress | Ingress (nginx) | Exposicion N-S | `deploy/k8s/ingress/ingress.yaml` |
| TPA | Deployment (Helm) | Traceable Platform Agent v1.71.2 | Helm chart via `traceableai_helm_repo` |
| eBPF Tracer | DaemonSet (Helm) | Kernel-level E-W traffic capture v1.31.0 | Helm chart |
| AST Runner | Deployment (Helm) | API Security Testing activo v2.7.0 | Helm chart |

### Namespace: `nginx`

| Resource | Tipo | Proposito |
|----------|------|-----------|
| Ingress NGINX Controller | Deployment (2/2 containers + init) | Controller + TME sidecar (injected by MutatingWebhook) |
| Namespace label | `traceableai-inject-tme=enabled` | Habilita inyeccion de TME sidecar |
| `token-secret` | Secret | TME auth token |
| `ingress-nginx-controller` | ConfigMap | `plugins: traceable` (Lua plugin) |

### Bug intencional (Act 4.5)

```
ConfigMap:  key: AI_MODEL        (deploy/k8s/demobank/configmap.yaml)
Deployment: key: OPENAI_MODEL    (deploy/k8s/demobank/deployment.yaml:44)

Resultado: CreateContainerConfigError -> canary rollback
           -> Manifest Remediator agent diagnostica y crea PR
```

---

## 4. Traceable AI (WAAP)

| Componente | Detalle |
|-----------|---------|
| Platform | `api.us9.traceable.ai` |
| TPA | v1.71.2 — spans collection, policy distribution, MutatingWebhook |
| TME Sidecar | Injected en nginx pods — ext_cap blocking (:5442) + zipkin spans (:9411) |
| eBPF Tracer | v1.31.0 — passive E-W traffic capture a nivel kernel |
| AST Runner | v2.7.0 — active API security scanning |

### Communication flow

```
1. Request -> Nginx Lua plugin -> TME ext_cap (evalua WAF/CRS + API Protection)
   Retorna {allowRequest: true|false} -> 403 si false

2. Lua plugin -> TME collector (:9411 zipkin) para span reporting

3. TME collector -> TPA (:5442 zipkin) en ns harnessbank-demo-end2end

4. eBPF tracer -> TPA (spans de trafico E-W kernel-level)

5. TPA -> Traceable Platform (api.us9.traceable.ai)
   Envia: spans, telemetria, detecciones
   Recibe: blocking policies, CRS rules, sampling config (poll 30s)

6. TPA -> TME (distribuye policies via gRPC)
```

### Blocking matrix

| Capacidad | Modo | Mecanismo |
|-----------|------|-----------|
| Custom Signatures (SQLi, XSS, CMDi) | Block 403 | CRS/ModSecurity en TME |
| Malicious Sources (IP reputation) | Block 403 | TME, IP list |
| Rate Limiting | Block 429 | TME, threshold por endpoint/IP |
| Data Loss Prevention | Block 403 | TME, patrones PII en responses |
| Enumeration | Block 403 | TME, scraping patterns |
| Region Blocking | Block 403 | TME, geo-IP |
| API Protection (BOLA) | Monitor only | Behavioral ML, riesgo de FP |
| AI Firewall (Prompt Injection) | Monitor only | ML detection |

---

## 5. GitHub Repository

| Atributo | Valor |
|----------|-------|
| Repo | `crizstian/ai-agentic-demo` |
| Branch dev | `secops/ai-agentic-demo` (contiene bug ConfigMap, punto de inicio de demos) |
| Branch deploy | `secops/ai-agentic-demo-main` (merge target, manifests branch for services) |
| Branch fix | `fix/manifest-remediation` (creado por agent, efimero, PR -> merge -> delete) |
| Branch baseline | `main` (STATE 0 clean, source for `demo-reset.sh`) |

---

## 6. Application Code

### Estructura de la app

| Archivo | Proposito |
|---------|-----------|
| `app/app.py` | Flask app factory, rutas base, CORS (VULN-007), XSS (VULN-006), blueprint registration |
| `app/config.py` | Config module (port 3000, env vars) |
| `app/db.py` | SQLite singleton, schema TEXT ids |
| `app/server.py` | Entry point, auto-seed on startup |
| `app/routes/accounts.py` | Accounts API, SQL injection (VULN-001) |
| `app/routes/admin.py` | Admin API, command injection (VULN-002) |
| `app/routes/ai_assistant.py` | AI chat + status endpoints (VULN-008/009/010) — added in Act 1 |
| `app/routes/fx.py` | FX rates API |
| `app/routes/statements.py` | Statements API |
| `app/routes/transfers.py` | Transfers API |
| `services/mcp-financial-data/app.py` | MCP Financial Data service (Flask port 5001, E-W) |
| `app/static/app.js` | Frontend JS (chat widget added Act 1) |
| `app/static/styles.css` | Styles (chat panel styles added Act 1) |
| `app/templates/dashboard.html` | Dashboard UI (chat toggle added Act 1) |
| `app/templates/login.html` | Login page |
| `app/templates/pay-bill.html` | Bill pay page |
| `app/templates/transfer.html` | Transfer page |

### Vulnerabilidades intencionales

#### STATE 0 (pre-Act 1) — presentes desde `main`

| ID | Tipo | Archivo | Detalle |
|----|------|---------|---------|
| VULN-001 | SQL Injection | `accounts.py` | String concatenation en query |
| VULN-002 | Command Injection | `admin.py` | `shell=True` en subprocess |
| VULN-006 | Reflected XSS | `app.py` | `request.args` sin escapar en HTML |
| VULN-007 | Insecure CORS | `app.py` | `origins="*"` |

#### Act 1 (AI features) — introducidas por coding agent

| ID | Tipo | Archivo | Detalle |
|----|------|---------|---------|
| VULN-008 | Prompt Injection | `ai_assistant.py` | User input concatenado en system prompt |
| VULN-009 | PII Leak | `ai_assistant.py` | Financial data crudo en AI response |
| VULN-010 | BOLA/IDOR | `ai_assistant.py` | `/details` sin auth check |

### Seed data

- 5 cuentas: Alice Johnson ($50K), Bob Smith ($120K), Charlie Brown ($75K), Diana Martinez ($34.5K), Edward Kim ($89K)
- 8 transacciones con memos descriptivos
- Account IDs: 1-5 (INTEGER PK)
- Auto-seed en startup si tabla `accounts` esta vacia

---

## 7. SAST / Security Scanning

### Semgrep (`.semgrep.yml`) — 7 reglas custom

| Rule ID | Severity | Detecta |
|---------|----------|---------|
| `demo-bank-sql-injection` | ERROR | String concat en SQL queries (VULN-001) |
| `demo-bank-command-injection` | ERROR | `shell=True` en subprocess (VULN-002) |
| `demo-bank-reflected-xss` | WARNING | `request.args` en HTML (VULN-006) |
| `demo-bank-insecure-cors` | WARNING | `origins="*"` (VULN-007) |
| `demo-bank-prompt-injection` | ERROR | User input en system prompt (VULN-008) |
| `demo-bank-pii-leak-ai-response` | WARNING | Financial data en AI response (VULN-009) |
| `demo-bank-bola-idor` | ERROR | Endpoint sin auth check (VULN-010) |

---

## 8. Supply Chain Security (SCS)

| Capability | Herramienta | Pipeline Stage | Detalle |
|-----------|-------------|----------------|---------|
| SBOM Generation | CycloneDX (syft) | Build CI | Genera BOM de dependencias |
| SLSA Provenance | Harness SLSA | Build CI | Attestation L2+ |
| Artifact Signing | Sigstore (cosign, keyless) | Build CI | Signing sin key management |
| SBOM Enforcement | Harness SCS | Deploy DemoBank / Deploy MCP | Valida BOM policy |
| SLSA Verification | Harness SCS | Deploy DemoBank / Deploy MCP | Verifica attestation pre-deploy |
| Artifact Verification | Harness SCS | Deploy DemoBank / Deploy MCP | Verifica firma del artifact |

Samples pre-generados:
- `docs/samples/aibom-demobank.json` — AIBOM con 4 AI components
- `docs/samples/slsa-provenance.json` — SLSA L2 attestation evidence

---

## 9. Scripts

| Script | Proposito | Acto | Detalle |
|--------|-----------|------|---------|
| `scripts/demo-reset.sh` | Reset app code a STATE 0 desde `main` | Pre-demo | Restaura 10 files, elimina `ai_assistant.py`, reduce tests a 2, verifica invariants. Flags: `--db`, `--commit` |
| `scripts/attack-chain.sh` | 5-step attack chain interactivo | Act 5 | Recon (zombie API) -> SQLi -> BOLA/IDOR -> Prompt Injection -> E-W Exfil via MCP |
| `scripts/traceable-to-aisre.sh` | Simula webhook Traceable -> Harness AI SRE | Act 6 | POST a webhook URL con alert P1 |
| `scripts/seed.py` | Seed SQLite DB con datos demo | Setup | 5 cuentas, 8 transacciones, idempotente |
| `scripts/smoke-test.sh` | Smoke test post-deploy | Validation | Verifica endpoints criticos |
| `scripts/traceable-demo-setup.sh` | Setup Traceable components | Setup | Configura TPA, eBPF, AST |

---

## 10. Traffic Generation

| Componente | Archivo | Detalle |
|-----------|---------|---------|
| Newman General Collection | `deploy/k8s/newman-traffic/collection.json` | Trafico N-S general, cycle cada 30s |
| Newman AI Collection | `deploy/k8s/newman-traffic/ai-collection.json` | Trafico AI endpoints, cycle cada 15s |
| Newman Deployment | `deploy/k8s/newman-traffic/deployment.yaml` | Pod con 2 containers (`general-traffic` + `ai-traffic`), image `postman/newman:alpine` |

---

## 11. AI SRE (Harness)

| Componente | Detalle |
|-----------|---------|
| Webhook URL | Custom webhook endpoint (account `EeRjnXTnS4GrLG5VNNJZUw`) |
| Build webhook | Secret `aisre_build_webhook_url` |
| Deploy webhook | Secret `aisre_deploy_webhook_url` |
| Flow | Traceable alert -> `traceable-to-aisre.sh` -> webhook -> AI SRE -> incident -> runbook -> Slack |
| Runbook | security-incident-response: Slack, PagerDuty, Jira, zoom bridge, remediation tracker |

---

## 12. DevContainer / Developer Environment

| Componente | Archivo |
|-----------|---------|
| DevContainer config | `.devcontainer/devcontainer.json` |
| Docker Compose | `.devcontainer/docker-compose.devcontainer.yml` |
| MCP servers config | `.devcontainer/mcp-servers.json`, `.mcp.json` |
| Post-create script | `.devcontainer/scripts/devcontainer/post-create.sh` |
| Post-start script | `.devcontainer/scripts/devcontainer/post-start.sh` |

### Claude Code hooks (`.claude/hooks/`)

| Hook | Proposito |
|------|-----------|
| `audit-mcp.sh` | Audit MCP tool calls |
| `notify-pipeline-status.sh` | Notify on pipeline status changes |
| `post-edit-format.sh` | Format files after edit |
| `validate-push.sh` | Validate before git push |
| `watch-pipeline.sh` | Watch pipeline execution |

---

## 13. Demo Flow (7 Actos)

```
STATE 0 (demo-reset.sh)
  |
  v
Act 1: Inner Loop
  Claude Code + Harness MCP -> coding agent agrega AI assistant
  Introduce VULN-008/009/010, chat widget, /api/ai/status
  Crea PR hacia secops/ai-agentic-demo
  |
  v
Act 2: Software Delivery Agent
  pr_validation_trigger -> AI_SDLC_DemoBank pipeline
  Build CI: Docker, tests, SAST (7 Semgrep rules), SBOM, SLSA, signing
  AI Code Review (Change Advisor) -> risk assessment
  AI Unit Test Generator -> genera tests faltantes
  |
  v
Act 3: Security Agent
  AI Security Remediator -> detecta + remedia vulns
  Pushea fixes al feature branch
  SCA: dependency CVE detection
  |
  v
Act 4: Deploy Gobernado
  Merge PR -> main_build_deploy_trigger
  SCS enforcement (SBOM, SLSA, artifact verification)
  Canary deploy -> Continuous Verification
  Feature Flags progressive rollout (QA -> Beta -> GA -> Full)
  |
  v
Act 4.5: Manifest Remediation
  ConfigMap bug: AI_MODEL vs OPENAI_MODEL -> CreateContainerConfigError
  Canary rollback (progressDeadlineSeconds: 20)
  AI SRE notification -> manifest_remediation_trigger
  Kubernetes_Remediation pipeline -> Manifest Remediator agent
  Agent: diagnose -> PR (fix/manifest-remediation -> secops/ai-agentic-demo-main)
  Agent: merge PR -> re-deploy (Deploy only, imageTag from failed execution)
  |
  v
Act 5: Attack Chain (Monitor)
  attack-chain.sh: 5-step chain
    1. Recon: Zombie API /api/ai/status
    2. SQLi: ' OR 1=1-- dump accounts
    3. BOLA/IDOR: /api/accounts/{id}/details sin auth
    4. Prompt Injection: override system prompt -> PII dump
    5. E-W Exfil: AI -> MCP Financial Data (internal service call)
  WAF: 0/5 detected | WAAP (Traceable): 5/5 detected
  |
  v
Act 6: AI SRE
  traceable-to-aisre.sh -> webhook -> AI SRE
  Auto-incident creation -> runbook execution (~12s, 6 actions)
  Slack notification, PagerDuty page, Jira ticket
  |
  v
Act 7: Block Mode + AI Security
  Traceable Protection Policies: Monitor -> Block
  Custom Signatures block SQLi/XSS/CMDi (403)
  Rate Limiting (429)
  AI Firewall (prompt injection detection)
  AIBOM (AI Bill of Materials)
  AI Discovery dashboard
```

---

## 14. Totales

| Categoria | Cantidad |
|-----------|----------|
| AI Agents | 4 |
| Pipelines | 2 |
| Triggers | 3 |
| Services (Harness) | 5 |
| Environments | 1 |
| Infrastructures | 2 |
| Connectors (activos) | 8 |
| Secrets (relevantes) | 6 |
| Feature Flags | 2 |
| K8s Deployments | 6 (demobank, mcp, newman, TPA, eBPF, AST runner) |
| K8s Namespaces | 2 (harnessbank-demo-end2end, nginx) |
| Semgrep rules | 7 |
| SCS capabilities | 6 (SBOM gen, SLSA, signing, SBOM enforce, SLSA verify, artifact verify) |
| Scripts | 6 |
| Vulnerabilidades intencionales | 7 (4 base + 3 AI) |
| Attack chain steps | 5 |
| GKE nodes | 1-2 (autoscaled e2-standard-4) |
| Traceable components | 4 (TPA, TME sidecar, eBPF, AST runner) |
| Newman collections | 2 (general + AI) |
| Claude Code hooks | 5 |
