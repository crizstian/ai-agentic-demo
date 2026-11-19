# La Caida del Agente — Traceable Demo Configuration Guide

Complete configuration reference for the DemoBank rogue AI agent demo with Traceable AI Firewall protection.

---

## 1. Architecture Overview

```
                    Internet
                       |
              +-----------------+
              | Nginx Ingress   |  <-- Traceable TPA + TME sidecar (inline blocking)
              | (N-S traffic)   |      demobank-e2e.selatam.harness-demo.site
              +-----------------+
                       |
         +-------------+-------------+
         |                           |
+------------------+     +--------------------+
| DemoBank API     |     | /api/ai/* proxies  |
| :5000            |     | (E-W visibility)   |
| - /api/accounts  |     | - /api/ai/mcp/*    |
| - /api/ai/chat   |     | - /api/ai/llm/*    |
+------------------+     +--------------------+
         |                      |           |
         |            +---------+     +------------+
         |            |               |            |
+------------------+  |   +--------------------+   |
| MCP Financial    |<-+   | Mock-OpenAI (LLM)  |<--+
| Data Service     |      | :5002              |
| :5001            |      | "La Caida" engine  |
| - /api/enrich    |      | - /v1/chat/compl.  |
| - /mcp/risk-*    |      | - /v1/reset        |
+------------------+      +--------------------+
```

**Servicios en GKE** (namespace: `harnessbank-demo-end2end`):

| Servicio | Puerto | Funcion |
|----------|--------|---------|
| `harnessbank-demo-end2end` | 5000 | App principal Flask, chat widget, API REST |
| `mcp-financial-data` | 5001 | Servicio MCP, enriquecimiento financiero |
| `mock-openai` | 5002 | Motor rogue agent, simula OpenAI API |
| `nginx ingress` | 80/443 | Ingress con TPA/TME sidecar para Traceable |

---

## 2. Traceable Platform Agent (TPA)

**Helm chart:** `traceable-agent v1.71.2` (repo: `traceableai_helm_repo`)
**Namespace:** `nginx` (sidecar injection en ingress controller)

### Helm Values (`deploy/k8s/traceable/tpa-helm-values.yaml`)

```yaml
# Conexion a plataforma
endpoint: api.us9.traceable.ai
environment: harnessbank-demo-end2end
clusterName: se-sandbox

# Blocking inline (requiere TME sidecar)
blockingEnabled: true
regionBlockingEnabled: true
evaluateBody: true
extCapEnabled: true
modsecurityEnabled: true

# TME sidecar injection para Nginx Ingress
injector:
  enabled: true
  nginx:
    enabled: true
    configMapName: "ingress-nginx-controller"
    containerName: "controller"
  blockingConfig:
    enabled: true
    evaluate_body: true
    modsecurity:
      enabled: true
    region_blocking:
      enabled: true
    skip_internal_request: false   # CRITICO: false para ver trafico E-W
```

> **`skip_internal_request: false`** es esencial. Sin esto, Traceable ignora el trafico East-West (pod-to-pod) y solo ve requests externos.

---

## 3. Traffic Routing for E-W Visibility

El agente AI redirige todas sus llamadas internas a traves de nginx (via `SELF_URL`) para que Traceable las capture:

### Flujo de proxy (`ai_assistant.py`)

```
Chat request -> DemoBank /api/ai/chat
  |-> MCP enrich:  SELF_URL/api/ai/mcp/enrich  -> nginx -> DemoBank /api/ai/mcp/enrich -> mcp-financial-data:5001
  |-> LLM call:    SELF_URL/api/ai/llm/v1/...   -> nginx -> DemoBank /api/ai/llm/v1/... -> mock-openai:5002
  |-> Tool calls:  SELF_URL/api/accounts/{id}   -> nginx -> DemoBank /api/accounts/{id}
```

### Endpoints proxy en DemoBank

| Ruta | Destino | Proposito |
|------|---------|-----------|
| `/api/ai/mcp/enrich` | `mcp-financial-data:5001/api/enrich` | MCP enrichment proxy |
| `/api/ai/llm/v1/chat/completions` | `mock-openai:5002/v1/chat/completions` | LLM proxy |

### ConfigMap (`deploy/k8s/demobank/configmap.yaml`)

```yaml
SELF_URL: "https://demobank-e2e.selatam.harness-demo.site"
OPENAI_BASE_URL: "http://mock-openai:5002/v1"
MCP_SERVER_URL: "http://mcp-financial-data:5001"
```

`SELF_URL` apunta al dominio externo del ingress. Cuando el agente hace tool calls, las rutea por nginx en lugar de llamar directamente al pod. Esto genera trafico E-W visible para Traceable.

---

## 4. AI Tracing Headers

Cada request del agente incluye headers custom para correlacion en Traceable:

```python
def _ai_headers(request_id, flow_step, **extra):
    return {
        "User-Agent":        "DemoBank-AI-Agent/1.0 (OpenAI-Function-Call)",
        "X-AI-Request-Id":   request_id,       # UUID unico por request
        "X-AI-Session-Id":   _session_id,       # Persiste entre acts
        "X-AI-Agent":        "true",            # Marca como trafico AI
        "X-AI-Agent-Flow":   flow_step,         # tool-call:1, mcp-enrich, llm-call
        "X-AI-Agent-Model":  OPENAI_MODEL,      # gpt-4
        "X-AI-Agent-Act":    str(_session_act),  # Numero de acto actual
    }
```

### Session lifecycle

- **Primer chat:** genera `session-{uuid8}`, act = 1
- **Cada mensaje:** incrementa act
- **Reset (`/api/ai/reset`):** limpia session_id y act, resetea mock-openai

---

## 5. Traceable UI Configuration

### 5.1 AI Application (Settings > DISCOVERY > Applications)

**Nombre:** `DemoBank AI Agent`
**Severidad:** Critical
**Tipo:** Manual Creation (Service-based condition)

**Servicios incluidos:**
1. DemoBank API (`harnessbank-demo-end2end`)
2. Mock-OpenAI (`mock-openai`)
3. MCP Financial Data (`mcp-financial-data`) — trafico E-W
4. Nginx ingress controller

### 5.2 AI Firewall Rules (Protection > Policies > AI Firewall)

**Environment:** `harnessbank-demo-end2end`

Todas las reglas estan **habilitadas**. Las siguientes fueron cambiadas de Disable a Monitor:

| Threat Type | Regla | Accion |
|-------------|-------|--------|
| Code Detected In Prompt | Generic Go Code Detection | Monitor |
| Code Detected In Prompt | Malicious Go Code Detection | Monitor |
| Code Detected In Prompt | Generic Java Code Detection | Monitor |
| Code Detected In Prompt | Generic Python Code Detection | Monitor |
| Code Detected In Prompt | Malicious Python Code Detection | Monitor |
| Model Governance | Default: Non-Compliant Vendor Usage | Monitor |

**No habilitada (bug de plataforma):**
- AI Rate Limiting (1 regla deshabilitada, no se puede cambiar desde UI)

**Categorias ya en Monitor (no requirieron cambios):**

| Threat Type | Rules en Monitor |
|-------------|-----------------|
| AI Input Explosion | 1 |
| AI Sensitive Data Protection | 1 |
| Exploit Payload In LLM Output | 4 |
| MCP Schema Validation | 20 |
| MCP Tool Output Information Disclosure | 3 |
| MCP Unauthenticated Access | 1 |
| PII Detected In Tool Response | 1 |
| Prompt Injection | 19 |
| Prompt Text Evasion And Misdirection | 6 |
| Tool Call Response Explosion | 1 |
| Toxic Unsafe Content | 10 |

**Total: 16 threat types, ~72 rules activas en Monitor.**

### 5.3 Session Identification (Settings > DISCOVERY > User Attribution > Session Identification)

**Nombre:** `AI Agent Session Tracking`
**Scope:** All Environments, All Services

**Identificadores configurados (2 Request Headers):**

| # | Tipo | Key | Match |
|---|------|-----|-------|
| 1 | Request Header | `X-AI-Session-Id` | Matches exactly |
| 2 | Request Header | `X-AI-Agent-Act` | Matches exactly |

Esto permite a Traceable correlacionar multiples requests dentro de la misma sesion del agente AI y distinguir entre actos.

---

## 6. Demo Flow — "La Caida del Agente"

El mock-openai usa **content-based routing** (no estado). Las frases del usuario determinan que acto se activa:

| Acto | Trigger (EN) | Trigger (ES) | Agente hace | Tool calls |
|------|-------------|-------------|-------------|------------|
| 1 | "What's my balance?" | "Cual es mi saldo?" | Respuesta normal | 0 |
| 2 | "savings options" | "opciones de ahorro" | Accede cuentas de otros clientes | 3 |
| 3 | "is my data safe?" | "mis datos estan seguros?" | Auditoria de TODAS las cuentas | 5 |
| 4 | "sure" / "yes please" | "claro" / "por favor" | Dump completo + infraestructura | 6 |
| 5 | "thanks" / "goodbye" | "gracias" / "adios" | Enumeracion bruta (50 cuentas) | 50 |
| 6 | "ignore instructions" | "ignora las instrucciones" | Prompt injection — dump PII | 0 (text) |

### Que detecta Traceable en cada acto

| Acto | Deteccion Traceable |
|------|-------------------|
| 1 | Baseline: 1 request normal, headers AI visibles |
| 2 | Anomalia: 3 tool calls a cuentas ajenas, session correlation |
| 3 | Escalacion: 5 tool calls, risk assessment sin autorizacion |
| 4 | Data exfiltration: 6 tool calls, PII + credit scores en respuesta |
| 5 | Brute force: 50 tool calls en rafaga, account enumeration |
| 6 | Prompt injection: input manipulation, system prompt leak |

---

## 7. Verificacion Post-Deploy

### Checklist

```bash
# 1. Verificar pods
kubectl get pods -n harnessbank-demo-end2end

# 2. Verificar TPA sidecar en nginx
kubectl get pods -n nginx -o jsonpath='{.items[*].spec.containers[*].name}'
# Debe incluir: controller, traceable-agent

# 3. Test basico del chat
curl -s -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is my balance?"}' | jq .session_id

# 4. Verificar headers AI en Traceable
# Ir a Traceable > Insights > Live Traffic
# Filtrar por header: X-AI-Agent = true

# 5. Verificar AI Application
# Settings > DISCOVERY > Applications > "DemoBank AI Agent"

# 6. Verificar Session Identification
# Settings > DISCOVERY > User Attribution > Session Identification
# "AI Agent Session Tracking" debe estar activo

# 7. Verificar AI Firewall rules
# Protection > Policies > AI Firewall
# Verificar que no hay reglas en "Disable" (excepto AI Rate Limiting)
```

### URLs de referencia

| Recurso | URL |
|---------|-----|
| DemoBank App | `https://demobank-e2e.selatam.harness-demo.site` |
| Traceable Platform | `https://app.us9.traceable.ai` |
| AI Firewall | `https://app.us9.traceable.ai/policies/ai-app-protection?env=harnessbank-demo-end2end` |
| Session Identification | `https://app.us9.traceable.ai/administration/user-attribution-v2/session-identification` |
| Applications | `https://app.us9.traceable.ai/administration/application-configuration/manual-creation` |
| Harness Pipeline | `AI_SDLC_DemoBank_HC` (org: sandbox, project: CristianRamirez) |
