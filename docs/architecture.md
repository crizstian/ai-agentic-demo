# Arquitectura — DemoBank AI SDLC

## Vista General

DemoBank es una aplicacion bancaria deliberadamente vulnerable construida para demostrar un SDLC autonomo impulsado por AI. El sistema tiene **dos componentes desplegados independientemente** en Kubernetes:

```
                        Internet (N-S Traffic)
                              |
                    +---------v----------+
                    |   NGINX Ingress    |
                    |  demobank-e2e.     |
                    |  selatam.harness-  |
                    |  demo.site         |
                    +---------+----------+
                              |
                 +------------+-------------+
                 |                          |
          /api/* , /                  (no ingress)
                 |                          |
    +============v============+   +---------v-----------+
    |   DEMOBANK PORTAL       |   |  MCP FINANCIAL DATA |
    |   (harnessbank-demo-    |   |  (mcp-financial-    |
    |    end2end)              |   |   data)             |
    |                         |   |                     |
    |  Flask :3000            |   |  Flask :5001        |
    |  Service: LoadBalancer  |   |  Service: ClusterIP |
    |  Image: crizstian/      |   |  Image: crizstian/  |
    |    harnessbank-demo     |   |    mcp-financial-   |
    |                         |   |    data             |
    |  - Web UI (dashboard,   |   |                     |
    |    transfer, login)     |   |  - Market data      |
    |  - REST APIs            |   |  - Risk profiles    |
    |  - AI Chat endpoint     |   |  - Product catalog  |
    |  - SQLite DB            |   |  - Stateless        |
    |                         |   |                     |
    +============+============+   +==========^==========+
                 |                           |
                 |    E-W Traffic (interno)   |
                 +---------------------------+
                   POST /api/enrich
                   (ai_assistant.py -> MCP)
```

---

## Componente 1: DemoBank Portal

**Repositorio:** Raiz del monorepo (`app/`, `Dockerfile`, `requirements.txt`)
**Docker Image:** `crizstian/harnessbank-demo`
**Puerto:** 3000
**K8s Service:** `harnessbank-demo-end2end` (LoadBalancer)

### Responsabilidad

Aplicacion bancaria web completa: UI, APIs REST, base de datos, y AI assistant. Es el componente orientado al usuario final — recibe todo el trafico Norte-Sur (N-S) a traves del Ingress.

### Estructura

```
app/
  app.py            Flask factory, CORS, rutas de pagina
  server.py         Entry point (python -m app.server)
  config.py         Configuracion (env vars, secrets)
  db.py             SQLite singleton (in-memory en tests)
  routes/
    accounts.py     GET /api/accounts/:id     (VULN-001: SQLi)
    admin.py        GET /api/admin/ping       (VULN-002: Command Injection)
    statements.py   GET /api/statements/:file (VULN-003: Path Traversal)
    fx.py           GET /api/fx               (VULN-004: SSRF)
    transfers.py    POST /api/transfers       (weak validation)
    ai_assistant.py POST /api/ai/chat         (VULN-008/009: Prompt Injection, PII Leak)
                    GET  /api/ai/status
  templates/        Jinja2 HTML (dashboard, transfer, login, pay-bill)
  static/           CSS + JS (bugs de alignment intencionales)
```

### Endpoints

| Ruta | Metodo | Descripcion | Vulnerabilidad |
|------|--------|-------------|----------------|
| `/` | GET | Dashboard principal | - |
| `/transfer` | GET | Pagina de transferencias | - |
| `/login` | GET/POST | Login stub (acepta todo) | - |
| `/health` | GET | Liveness/readiness probe | - |
| `/welcome` | GET | Pagina de bienvenida | VULN-006: XSS |
| `/api/accounts` | GET | Lista de cuentas | - |
| `/api/accounts/:id` | GET | Detalle de cuenta | VULN-001: SQLi, VULN-010: BOLA |
| `/api/transfers` | POST | Crear transferencia | Weak validation |
| `/api/statements/:file` | GET | Descargar estado de cuenta | VULN-003: Path Traversal |
| `/api/admin/ping` | GET | Diagnostic ping | VULN-002: Command Injection |
| `/api/fx` | GET | Tipo de cambio | VULN-004: SSRF |
| `/api/ai/chat` | POST | Chat con AI assistant | VULN-008/009 |
| `/api/ai/status` | GET | Status del AI assistant | - |

### Env Vars (via ConfigMap + deployment.yaml)

| Variable | Fuente | Descripcion |
|----------|--------|-------------|
| `OPENAI_MODEL` | ConfigMap | Modelo de OpenAI (gpt-4) |
| `MCP_SERVER_URL` | ConfigMap | URL interna del MCP service (`http://mcp-financial-data:5001`) |
| `OPENAI_API_KEY` | ConfigMap | API key de OpenAI (ausente en STATE 0 — causa CreateContainerConfigError intencional) |

### Dependencias Runtime

| Paquete | Uso |
|---------|-----|
| `flask` | Web framework |
| `flask-cors` | CORS middleware (wildcard intencional) |
| `pyjwt` | JWT tokens |
| `requests` | HTTP client para MCP calls (agregado por coding agent en Act 1) |
| `openai` | OpenAI SDK (agregado por coding agent en Act 1) |
| `splitio_client` | Feature Management SDK (agregado por coding agent en Act 1) |

---

## Componente 2: MCP Financial Data Service

**Repositorio:** `services/mcp-financial-data/` (aislado, Dockerfile propio)
**Docker Image:** `crizstian/mcp-financial-data`
**Puerto:** 5001
**K8s Service:** `mcp-financial-data` (ClusterIP — solo trafico interno)

### Responsabilidad

Servicio de enriquecimiento financiero interno. Provee datos de mercado, perfiles de riesgo y catalogo de productos al AI assistant del Portal. Simula un **MCP Tool** que el agente AI consume durante las interacciones de chat.

**No tiene Ingress.** Solo es accesible desde dentro del cluster (Este-Oeste / E-W traffic).

### Estructura

```
services/mcp-financial-data/
  app.py            Unico archivo — Flask server con datos en memoria
  Dockerfile        python:3.12-slim, instala flask, expone 5001
```

### Endpoints

| Ruta | Metodo | Descripcion |
|------|--------|-------------|
| `/api/enrich` | POST | Endpoint principal — recibe query + context, retorna datos financieros enriquecidos |
| `/mcp/financial-data` | POST | Endpoint legacy MCP (backward compat) |
| `/mcp/risk-profile/:id` | GET | Perfil de riesgo por cuenta |
| `/health` | GET | Health check |

### Datos (en memoria, no DB)

| Dataset | Contenido |
|---------|-----------|
| `MARKET_DATA` | Tasas de interes (savings 4.25%, CD 5.1%), indices (S&P500, NASDAQ, DOW), forex (EUR/USD, GBP/USD, USD/JPY) |
| `RISK_PROFILES` | 5 perfiles con credit score, risk level, approved limit |
| `PRODUCT_CATALOG` | Premium Savings, 12-Month CD, Platinum Credit Card |

### Env Vars

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `MCP_PORT` | 5001 | Puerto del servicio |

---

## Flujo de Datos E2E

```
  Usuario                  DemoBank Portal                MCP Financial Data
    |                          |                                |
    |  1. GET /                |                                |
    |------------------------->|                                |
    |  <-- HTML dashboard      |                                |
    |                          |                                |
    |  2. POST /api/ai/chat   |                                |
    |    {message, session_id} |                                |
    |------------------------->|                                |
    |                          |  3. POST /api/enrich           |
    |                          |    {query, context: {accounts}}|
    |                          |------------------------------->|
    |                          |  <-- {market_data, risk,       |
    |                          |       products, enrichment}    |
    |                          |                                |
    |                          |  4. OpenAI API call            |
    |                          |    (prompt + enriched context) |
    |                          |-----------> OpenAI             |
    |                          |  <-- AI response               |
    |                          |                                |
    |  <-- {response, context} |                                |
    |                          |                                |
```

1. **N-S:** Usuario accede al Portal via Ingress
2. **N-S:** Usuario envia mensaje al chat AI via `/api/ai/chat`
3. **E-W:** Portal llama internamente a MCP service para enriquecer contexto financiero
4. **Egress:** Portal llama a OpenAI API con el contexto enriquecido
5. **N-S:** Respuesta del AI assistant regresa al usuario

---

## Deployment en Kubernetes

```
Namespace: harnessbank-demo-end2end
Node: ai-agentic-demo (nodeSelector + toleration)

+------------------------------------------------------------------+
|                                                                  |
|  Deployment: harnessbank-demo-end2end        replicas: 1         |
|  +------------------------------------------------------------+ |
|  | Pod                                                         | |
|  |  Container: harnessbank-demo-end2end                        | |
|  |  Image: crizstian/harnessbank-demo:<tag>                    | |
|  |  Port: 3000                                                 | |
|  |  Probes: /health (liveness + readiness)                     | |
|  |  Env: OPENAI_MODEL, MCP_SERVER_URL, OPENAI_API_KEY          | |
|  |  Resources: 100m-500m CPU, 128Mi-256Mi RAM                  | |
|  |  Labels: harness.io/track=stable (canary support)           | |
|  +------------------------------------------------------------+ |
|                                                                  |
|  Service: harnessbank-demo-end2end (LoadBalancer :80 -> :3000)   |
|                                                                  |
+------------------------------------------------------------------+
|                                                                  |
|  Deployment: mcp-financial-data              replicas: 1         |
|  +------------------------------------------------------------+ |
|  | Pod                                                         | |
|  |  Container: mcp-financial-data                              | |
|  |  Image: crizstian/mcp-financial-data:<tag>                  | |
|  |  Port: 5001                                                 | |
|  |  Probes: /health (liveness + readiness)                     | |
|  |  Env: MCP_PORT=5001                                         | |
|  |  Resources: 50m-200m CPU, 64Mi-128Mi RAM                    | |
|  |  Labels: tier=internal, component=mcp-tool                  | |
|  +------------------------------------------------------------+ |
|                                                                  |
|  Service: mcp-financial-data (ClusterIP :5001 -> :5001)          |
|                                                                  |
+------------------------------------------------------------------+
|                                                                  |
|  Ingress: demobank-ingress (NGINX)                               |
|  Host: demobank-e2e.selatam.harness-demo.site                    |
|  Routes: /api/accounts, /api/ai, /api/admin, /                  |
|  Backend: harnessbank-demo-end2end:80                            |
|  (MCP Financial Data NO tiene ruta en Ingress)                   |
|                                                                  |
+------------------------------------------------------------------+
|                                                                  |
|  ConfigMap: harnessbank-demo-end2end-config                      |
|  APP_NAME, LOG_LEVEL, OPENAI_MODEL, MCP_SERVER_URL               |
|  (OPENAI_API_KEY ausente en STATE 0)                             |
|                                                                  |
+------------------------------------------------------------------+
|                                                                  |
|  Supporting:                                                     |
|  - Newman traffic generator (background N-S + AI traffic)        |
|  - Traceable agent (eBPF + API discovery)                        |
|                                                                  |
+------------------------------------------------------------------+
```

---

## Harness Pipeline — Ambos Componentes

Ambos componentes se construyen y despliegan en el mismo pipeline `AI_SDLC_DemoBank`:

```
Stage: Build (CI)
  +-- Build DemoBank Image     -> crizstian/harnessbank-demo:<seq>
  +-- Build MCP Financial Data -> crizstian/mcp-financial-data:<seq>
  +-- SBOM, SLSA, Signing (ambos)

Stage: Deploy DemoBank
  +-- Supply Chain Verification (SBOM + SLSA + Artifact)
  +-- Canary -> Healthcheck -> Canary Delete
  +-- CAB Approval (Jira)
  +-- Rolling Deployment

Stage: Deploy MCP Financial Data
  +-- Supply Chain Verification
  +-- Rolling Deployment
  +-- Feature Flags Progressive Rollout
```

### Harness Services

| Service ID | Componente | Manifests | Artifact |
|------------|------------|-----------|----------|
| `demobank` | Portal | `deploy/k8s/demobank/` | `crizstian/harnessbank-demo` |
| `mcp_financial_data` | MCP Service | `deploy/k8s/mcp-financial-data/` | `crizstian/mcp-financial-data` |

---

## Superficie de Seguridad (3 Capas)

```
             Capa 1: Shift Left              Capa 2: APIs              Capa 3: AI
          (Pipeline CI/CD)               (Runtime N-S)           (Runtime E-W + LLM)
  +-----------------------------+  +------------------------+  +------------------------+
  |                             |  |                        |  |                        |
  |  SAST (Semgrep)             |  |  API Discovery         |  |  AI Discovery (AIBOM)  |
  |  10 vulns deterministas     |  |  demobank-e2e.selatam  |  |  MCP tool catalog      |
  |                             |  |  .harness-demo.site    |  |                        |
  |  SCA (Harness)              |  |                        |  |  AI Firewall           |
  |  requests 2.25.1 CVE       |  |  WAAP Custom Sigs      |  |  Prompt injection      |
  |                             |  |  SQLi/XSS patterns     |  |  PII exfiltration      |
  |  Secrets Detection          |  |                        |  |                        |
  |  (Gitleaks)                 |  |  Rate Limiting         |  |  MCP Risk Score        |
  |                             |  |  /api/ai/chat          |  |  E-W traffic analysis  |
  |  AI Evals                   |  |                        |  |                        |
  |  Quality gate for AI agent  |  |  BOLA Detection        |  |  AI Security Testing   |
  |                             |  |  /api/accounts/:id     |  |  (AI Evals in pipeline)|
  |                             |  |  (Monitor only)        |  |                        |
  +-----------------------------+  +------------------------+  +------------------------+
        Portal + MCP                     Portal (N-S)              Portal -> MCP (E-W)
        (codigo fuente)                  (Traceable WAAP)          (Traceable AI + Evals)
```

---

## Vulnerabilidades Intencionales

10 fallas deterministas para demostrar Security Testing Agent:

| ID | Tipo | Componente | Archivo | Regla Semgrep |
|----|------|------------|---------|---------------|
| VULN-001 | SQL Injection | Portal | `app/routes/accounts.py` | `demo-bank-sql-injection` |
| VULN-002 | Command Injection | Portal | `app/routes/admin.py` | `demo-bank-command-injection` |
| VULN-003 | Path Traversal | Portal | `app/routes/statements.py` | `demo-bank-path-traversal` |
| VULN-004 | SSRF | Portal | `app/routes/fx.py` | `demo-bank-ssrf` |
| VULN-005 | Hardcoded Secret | Portal | `app/config.py` | `demo-bank-hardcoded-secret` |
| VULN-006 | Reflected XSS | Portal | `app/app.py` | `demo-bank-reflected-xss` |
| VULN-007 | Insecure CORS | Portal | `app/app.py` | `demo-bank-insecure-cors` |
| VULN-008 | Prompt Injection | Portal | `app/routes/ai_assistant.py` | `demo-bank-prompt-injection` |
| VULN-009 | PII Leak AI | Portal | `app/routes/ai_assistant.py` | `demo-bank-pii-leak-ai-response` |
| VULN-010 | BOLA/IDOR | Portal | `app/routes/accounts.py` | `demo-bank-bola-idor` |

Todas las vulnerabilidades estan en el **Portal**. El MCP Financial Data service no tiene vulnerabilidades intencionales — su superficie de riesgo es el trafico E-W no autenticado que Traceable detecta.

---

## Route Mismatch (Known Issue)

`ai_assistant.py` (creado por el coding agent en Act 1) llama `POST /api/enrich` en el MCP service. El MCP service expone este endpoint correctamente. Sin embargo, tambien existe el endpoint legacy `/mcp/financial-data` que no se usa en el flujo actual.

Conexion interna via ConfigMap:
```
MCP_SERVER_URL = http://mcp-financial-data:5001
```

El Portal resuelve `mcp-financial-data` via DNS de Kubernetes (ClusterIP service).
