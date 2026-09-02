# DemoBank -- Diagramas de Arquitectura

Dos diagramas ASCII para referencia rapida de la arquitectura de despliegue
y el flujo de ejecucion de la demo de 7 actos. Ancho maximo: 120 caracteres.

---

## Diagrama 1: Arquitectura de Despliegue

```text
                            DemoBank -- Arquitectura de Despliegue

  EXTERNAL
  ┌──────────────────────────┐                              ┌────────────────────────────┐
  │   INTERNET / ATTACKER    │                              │  DEVELOPER + CLAUDE CODE   │
  │   (Act 5: recon, SQLi,   │                              │  (Act 1: inner loop)       │
  │    BOLA, prompt inj.)    │                              │                            │
  └──────────┬───────────────┘                              │  git push ──> GitHub       │
             │                                              │  MCP ═══════> Harness      │
             │ N-S                                          └────────────────────────────┘
             │
             │                [ZOMBIE] /api/ai/status
             │           · · · · BYPASS · · · · · · · · · · · · · · ┐
             │                                                       │
  ┌──────────▼──────────────────────────────────────────────┐        │
  │  API GATEWAY -- APIGEE  (N-S only)                      │        │
  │  Registered endpoints:                                  │        │
  │                                                         │        │
  │    /accounts    apikey-verify + rate-limit-100           │        │
  │    /ai/chat     apikey-verify + rate-limit-30 + 10kb    │        │
  │    /admin/ping  apikey-verify + ip-whitelist             │        │
  │    /fx          rate-limit-500 (open, no auth)           │        │
  └──────────┬──────────────────────────────────────────────┘        │
             │                                                       │
  ┌──────────▼───────────────────────────────────────────────────────▼────────────┐
  │                                                                               │
  │  GKE CLUSTER: se-sandbox                                                      │
  │                                                                               │
  │ ╔═══════════════════════════════════════════════════════════════════════════╗  │
  │ ║  NAMESPACE: nginx           label: traceableai-inject-tme=enabled        ║  │
  │ ║                                                                          ║  │
  │ ║  Deployment: ingress-nginx-controller                                    ║  │
  │ ║  ┌────────────────────────────────────────────────────────────────────┐   ║  │
  │ ║  │  Pod (2/2 containers)                                             │   ║  │
  │ ║  │                                                                   │   ║  │
  │ ║  │  ┌─────────────────────────┐    ┌──────────────────────────────┐  │   ║  │
  │ ║  │  │  controller             │    │  tme (sidecar)               │  │   ║  │
  │ ║  │  │  ingress-nginx v1.10.1  │    │  traceable-agent v1.71.2    │  │   ║  │
  │ ║  │  │                         │    │                              │  │   ║  │
  │ ║  │  │  Lua plugin: traceable  │───>│  ext_cap :5442              │  │   ║  │
  │ ║  │  │  (rewrite phase)        │ ①  │  - WAF (CRS/ModSec)        │  │   ║  │
  │ ║  │  │                         │    │  - API Protection (BOLA)    │  │   ║  │
  │ ║  │  │  Si block=true ──> 403  │<───│  - Rate Limiting           │  │   ║  │
  │ ║  │  │  Si block=false ──> app │    │  - Region Blocking         │  │   ║  │
  │ ║  │  │                         │    │                              │  │   ║  │
  │ ║  │  │  Span reporter ────────>│───>│  collector :9411 (zipkin)   │  │   ║  │
  │ ║  │  │                     ②   │    │  ──> TPA :5442 (zipkin)  ──────────>│  │
  │ ║  │  └─────────────────────────┘    └──────────────────────────────┘  │ ③ ║  │
  │ ║  │                                                                   │   ║  │
  │ ║  │  InitContainer: traceable-nginx-init (copia Lua plugin)           │   ║  │
  │ ║  │  Inyectado por: MutatingWebhook del TPA                           │   ║  │
  │ ║  └────────────────────────────────────────────────────────────────────┘   ║  │
  │ ║                                                                          ║  │
  │ ║  ConfigMap: ingress-nginx-controller (plugins: traceable)                ║  │
  │ ║  Secret: token-secret (TA_REFRESH_TOKEN para auth al platform)           ║  │
  │ ╚══════════════════════════════════════════════════════════════════════════╝  │
  │           │ request (si no bloqueado)                           ▲             │
  │           ▼                                                    │ ③           │
  │ ╔═══════════════════════════════════════════════════════════════════════════╗  │
  │ ║  NAMESPACE: harnessbank-demo-end2end                                     ║  │
  │ ║                                                                          ║  │
  │ ║  ┌────────────────────────────┐  - E-W - >  ┌────────────────────────┐   ║  │
  │ ║  │  DemoBank Pod (:3000)      │ [BLIND SPOT] │  MCP Financial Data   │   ║  │
  │ ║  │  Svc: harnessbank-demo     │  Apigee no   │  Pod (:5001)          │   ║  │
  │ ║  │  (LB 80 -> 3000)           │  ve E-W      │  Svc: ClusterIP      │   ║  │
  │ ║  │                            │               │  (internal only)     │   ║  │
  │ ║  │  /api/accounts  (VULN-001) │               │                      │   ║  │
  │ ║  │  /api/ai/chat   (VULN-008) │               │  /mcp/financial-data │   ║  │
  │ ║  │  /api/ai/status  [ZOMBIE]  │               │  /mcp/risk-profile   │   ║  │
  │ ║  │  /api/admin     (VULN-002) │               │  /health             │   ║  │
  │ ║  │  /health                   │               └──────────────────────┘   ║  │
  │ ║  │  ┌───────────────┐        │                                          ║  │
  │ ║  │  │ SQLite        │        │                                          ║  │
  │ ║  │  │ demobank.db   │        │                                          ║  │
  │ ║  │  └───────────────┘        │                                          ║  │
  │ ║  └────────────────────────────┘                                          ║  │
  │ ║                                                                          ║  │
  │ ║  ┌─────────────────────────────────────────────────────────────────────┐  ║  │
  │ ║  │  TPA: Traceable Platform Agent (Deployment, v1.71.2)               │  ║  │
  │ ║  │                                                                     │  ║  │
  │ ║  │  ← ③ Recibe spans del TME (zipkin :5442)                          │  ║  │
  │ ║  │  ← ④ Recibe spans del eBPF tracer                                 │  ║  │
  │ ║  │  → ⑤ Envia spans + telemetria al platform (api.us9.traceable.ai)  │  ║  │
  │ ║  │  ← ⑥ Recibe blocking policies del platform (poll 30s)             │  ║  │
  │ ║  │  → ⑦ Distribuye policies al TME via gRPC                          │  ║  │
  │ ║  │                                                                     │  ║  │
  │ ║  │  MutatingWebhook: inyecta TME sidecar en namespaces con            │  ║  │
  │ ║  │  label traceableai-inject-tme=enabled                              │  ║  │
  │ ║  │                                                                     │  ║  │
  │ ║  │  ConfigMap: tme-template-override (endpoint + token fix)            │  ║  │
  │ ║  │  Secret: token-secret (api token para api.us9.traceable.ai)         │  ║  │
  │ ║  └─────────────────────────────────────────────────────────────────────┘  ║  │
  │ ║                                                                          ║  │
  │ ║  ┌─────────────────────────────────────────────────────────────────────┐  ║  │
  │ ║  │  eBPF Tracer (DaemonSet, 7 pods, v1.31.0)                         │  ║  │
  │ ║  │                                                                     │  ║  │
  │ ║  │  Captura pasiva de trafico E-W en cada nodo (kernel-level)         │  ║  │
  │ ║  │  Out-of-band — NO puede bloquear, solo observa                     │  ║  │
  │ ║  │  → ④ Envia spans al TPA                                           │  ║  │
  │ ║  └─────────────────────────────────────────────────────────────────────┘  ║  │
  │ ║                                                                          ║  │
  │ ║  ┌─────────────────────────────────────────────────────────────────────┐  ║  │
  │ ║  │  AST Runner (Deployment, traceable-runner v2.7.0)                  │  ║  │
  │ ║  │  API Security Testing — scans activos de APIs descubiertas         │  ║  │
  │ ║  └─────────────────────────────────────────────────────────────────────┘  ║  │
  │ ║                                                                          ║  │
  │ ║  Newman Traffic Generator (Deployment) — trafico sintetico continuo      ║  │
  │ ╚══════════════════════════════════════════════════════════════════════════╝  │
  │                                                                               │
  └───────────────────────────────────────────────────────────────────────────────┘
             ║ ⑤⑥                                          ║
             ║ Traceable Platform                           ║ Harness Platform
             ║                                              ║
  ╔══════════╩════════════════════════════╗   ╔═════════════╩═══════════════════════╗
  ║  TRACEABLE PLATFORM                   ║   ║  HARNESS PLATFORM                   ║
  ║  app.us9.traceable.ai                 ║   ║                                     ║
  ║                                       ║   ║  ┌──────────┐  ┌──────────────────┐ ║
  ║  ┌─────────────────────────────────┐  ║   ║  │ Software │  │ Security Testing │ ║
  ║  │  Protection Policies            │  ║   ║  │ Delivery │  │ Agent            │ ║
  ║  │                                 │  ║   ║  │ Agent    │  │ STO, SAST, SCA   │ ║
  ║  │  WAF (SQLi, XSS, CMDi)         │  ║   ║  │ CI/CD,TI │  │ AI Triage        │ ║
  ║  │    → Monitor / Block            │  ║   ║  └──────────┘  └──────────────────┘ ║
  ║  │                                 │  ║   ║                                     ║
  ║  │  API Protection (BOLA, AuthZ)   │  ║   ║  ┌──────────┐  ┌──────────────────┐ ║
  ║  │    → Monitor / Block            │  ║   ║  │ AI SRE   │  │ AI Security      │ ║
  ║  │      (requiere TME inline)      │  ║   ║  │ Runbooks │  │ AIBOM            │ ║
  ║  │                                 │  ║   ║  │ Slack,PD │  │ OWASP LLM Top10  │ ║
  ║  │  AI Firewall (Prompt Inj.)      │  ║   ║  │ Jira     │  │ MCP Risk Score   │ ║
  ║  │    → Monitor only (sin Block)   │  ║   ║  └──────────┘  └──────────────────┘ ║
  ║  └─────────────────────────────────┘  ║   ║                                     ║
  ║                                       ║   ║  ┌──────────────────────────────────┐║
  ║  ┌─────────────────────────────────┐  ║   ║  │ SCS: SBOM, AIBOM, SLSA, Attest. │║
  ║  │  API Discovery + AI Security    │  ║   ║  └──────────────────────────────────┘║
  ║  │  Threat Activity (detecciones)  │  ║   ║                                     ║
  ║  │  MCP Risk Score                 │  ║   ║  Pipeline: CDSimpleKubernetesDepl.  ║
  ║  │  Behavioral Detection           │  ║   ║  (NativeHelm, despliega TPA/eBPF)   ║
  ║  └─────────────────────────────────┘  ║   ╚═════════════════════════════════════╝
  ╚═══════════════════════════════════════╝

  Convenciones:
  ──────── Linea solida    = Trafico Norte-Sur (N-S)
  - - - -> Linea punteada  = Trafico Este-Oeste (E-W)
  ════════ Linea doble     = Conexion a plataforma cloud (Traceable / Harness)
  · · · ·  Linea de puntos = Bypass (trafico no registrado en gateway)

  [ZOMBIE]     = Endpoint no registrado en API Gateway, sin policies de seguridad
  [BLIND SPOT] = Trafico invisible para Apigee (solo visible para eBPF/Traceable)

  Flujo de numeros:
  ① Lua plugin ──> TME ext_cap (req_cap: block o allow)
  ② Lua plugin ──> TME collector (span reporting via zipkin)
  ③ TME ──> TPA (spans + telemetria via zipkin/OTLP)
  ④ eBPF tracer ──> TPA (spans de trafico E-W)
  ⑤ TPA ──> Traceable Platform (analytics, deteccion, policy sync)
  ⑥ Traceable Platform ──> TPA (blocking policies, CRS rules, config)
  ⑦ TPA ──> TME (policies distribuidas via gRPC, poll 30s)
```

---

## Diagrama 1b: Traceable — Flujo de Blocking Inline

```text
                    Flujo de Blocking: Request Path con TME Sidecar

   ATTACKER                 NGINX INGRESS (ns: nginx)                    DEMOBANK
      │                          Pod (2/2)                                  │
      │         ┌─────────────────────────────────────────────┐             │
      │         │                                             │             │
      │  HTTP   │  ┌──────────────┐     ┌──────────────────┐  │             │
      │ request │  │  controller  │     │  tme (sidecar)   │  │             │
      ├────────>│  │              │     │                  │  │             │
      │         │  │  Lua plugin  │ ──> │  ext_cap         │  │             │
      │         │  │  (rewrite)   │ ①   │  /v1/req_cap     │  │             │
      │         │  │              │     │                  │  │             │
      │         │  │              │ <── │  {allowRequest:  │  │             │
      │         │  │              │     │   true|false}    │  │             │
      │         │  │              │     │                  │  │             │
      │         │  │  if false:   │     │  Policies from:  │  │             │
      │  403    │  │  ngx.exit    │     │  ┌────────────┐  │  │             │
      │<────────│  │  (403)       │     │  │ WAF (CRS)  │  │  │             │
      │ Access  │  │              │     │  │ API Prot.  │  │  │             │
      │Forbidden│  │  if true:    │     │  │ Rate Limit │  │  │             │
      │         │  │  proxy_pass ─│─────│──│ Region Blk │──│──────────────>│
      │         │  │  to backend  │     │  └────────────┘  │  │             │
      │         │  │              │     │                  │  │             │
      │         │  │  (log phase) │     │  collector       │  │             │
      │         │  │  span report─│ ──> │  :9411 (zipkin)  │  │             │
      │         │  │          ②   │     │  batch + export  │──│──> TPA ③    │
      │         │  └──────────────┘     └──────────────────┘  │             │
      │         └─────────────────────────────────────────────┘             │
      │                                                                     │

  Blocking Matrix (Act 7):
  ┌──────────────────────────┬───────────┬──────────────────────────────────┐
  │ Threat                   │ Action    │ Enforcement Point                │
  ├──────────────────────────┼───────────┼──────────────────────────────────┤
  │ Custom Signatures (WAF)  │ Block 403 │ TME ext_cap (CRS/ModSecurity)   │
  │ Malicious Sources (IP)   │ Block 403 │ TME ext_cap (IP reputation)     │
  │ Rate Limiting            │ Block 429 │ TME ext_cap (threshold)         │
  │ DLP (PII filtering)      │ Block 403 │ TME ext_cap (response filter)   │
  │ Enumeration              │ Block 403 │ TME ext_cap (scraping detect)   │
  │ Region Blocking (geo)    │ Block 403 │ TME ext_cap (geo-IP)            │
  │ BOLA (API Protection)    │ Monitor   │ Plataforma (behavioral ML)      │
  │                          │           │ Riesgo FP — no auto-block       │
  │ Prompt Injection (AI FW) │ Monitor   │ Plataforma (ML detection)       │
  │                          │           │ Mitigacion: code fix (Act 3)    │
  └──────────────────────────┴───────────┴──────────────────────────────────┘

  Traceable Out-of-Band vs Inline:
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  eBPF Tracer (DaemonSet)          │  TME Sidecar (en Nginx pod)        │
  │  ─────────────────────────────    │  ──────────────────────────────    │
  │  Deployment: DaemonSet (7 nodos)  │  Inyectado por MutatingWebhook    │
  │  Posicion: out-of-band (kernel)   │  Posicion: inline (request path)  │
  │  Captura: pasiva (copia trafico)  │  Captura: activa (intercepta)     │
  │  Trafico: E-W (pod-to-pod)        │  Trafico: N-S (ingress)           │
  │  Blocking: NO                     │  Blocking: SI (403/429)           │
  │  Latencia: 0ms (no impacta)       │  Latencia: ~1-3ms por request     │
  │  Caso: visibilidad E-W, API disc. │  Caso: enforcement, virtual patch │
  └──────────────────────────────────────────────────────────────────────────┘
```

---

## Diagrama 2: Secuencia de Ejecucion (7 Actos)

```text
                          DemoBank -- Secuencia de Ejecucion (7 Actos)

    DEV       CLAUDE     GITHUB    HARNESS      K8S     ATTACKER    WAAP      AI-SRE    AI-SEC
     |          |          |          |          |          |          |          |          |
 ---- ACT 1: Inner Loop (~5 min) -----------------------------------------------------------------
     |          |          |          |          |          |          |          |          |
     | Add AI   |          |          |          |          |          |          |          |
     | assistant|          |          |          |          |          |          |          |
     |--------->|          |          |          |          |          |          |          |
     |          | PR #52   |          |          |          |          |          |          |
     |          |--------->|          |          |          |          |          |          |
     |          |          |          |          |          |          |          |          |
 ---- ACT 2: Software Delivery Agent (~3 min) ----------------------------------------------------
     |          |          |          |          |          |          |          |          |
     |          |          | trigger  |          |          |          |          |          |
     |          |          |--------->|          |          |          |          |          |
     |          |          |          |[TI 11/47]|          |          |          |          |
     |          |          |  Change  |          |          |          |          |          |
     |          |          |  Advisor |          |          |          |          |          |
     |          |          |<---------|          |          |          |          |          |
     |          |          |          |          |          |          |          |          |
 ---- ACT 3: Security Testing Agent (~4 min) -----------------------------------------------------
     |          |          |          |          |          |          |          |          |
     |          |          |          |[STO scan]|          |          |          |          |
     |          |          |          |[7 SAST  ]|          |          |          |          |
     |          |          |          |[+1 SCA  ]|          |          |          |          |
     |          |          |          |[Triage  ]|          |          |          |          |
     |          |          |  Remed.  |          |          |          |          |          |
     |          |          |  fixes   |          |          |          |          |          |
     |          |          |<---------|          |          |          |          |          |
     |          |          |          |[Re-scan ]|          |          |          |          |
     |          |          |          |[4 fixed ]|          |          |          |          |
     |          |          |          |[3 remain]|          |          |          |          |
     |          |          |          |          |          |          |          |          |
 ---- ACT 4: Deploy Gobernado (~3 min) -----------------------------------------------------------
     |          |          |          |          |          |          |          |          |
     |          |          |          |[OPA gate]|          |          |          |          |
     |          |          |          | canary   |          |          |          |          |
     |          |          |          | 10>25>100|          |          |          |          |
     |          |          |          |--------->|          |          |          |          |
     |          |          |          | CV ML    |          |          |          |          |
     |          |          |          | baseline |          |          |          |          |
     |          |          |          |--------->|          |          |          |          |
     |          |          |          |          |          |          |          |          |
 ---- ACT 5: El Ataque - Shield Right (~5 min) ---------------------------------------------------
     |          |          |          |          |          |          |          |          |
     |          |          |          |          | recon    |          |          |          |
     |          |          |          |          |<---------|          |          |          |
     |          |          |          |          | SQLi     |          |          |          |
     |          |          |          |          |<---------|          |          |          |
     |          |          |          |          | BOLA     |          |          |          |
     |          |          |          |          |<---------|          |          |          |
     |          |          |          |          |prompt inj|          |          |          |
     |          |          |          |          |<---------|          |          |          |
     |          |          |          |          |      captured       |          |          |
     |          |          |          |          |-------------------->|          |          |
     |          |          |          |          |          |          |threat 35 |          |
     |          |          |          |          |          |          |threat 65 |          |
     |          |          |          |          |          |          |threat 85 |          |
     |          |          |          |          |          |          |auto-block|          |
     |          |          |          |          |          |          |          |          |
 ---- ACT 6: Shield Right + Shift Left (~3 min) --------------------------------------------------
     |          |          |          |          |          |          |          |          |
     |          |          |          |          |          |          | incident |          |
     |          |          |          |          |          |          |--------->|          |
     |          |          |          |          |          |          |          |[runbook] |
     |          |          |          |          |          |          |          | Slack    |
     |          |          |          |          |          |          |          | PagerDuty|
     |          |          |          |          |          |          |          | Jira     |
     |          |          |          |          |          |          |          | Zoom     |
     |          |          |          |<-----------remediation--------------------|          |
     |          |          |          |          |          |          |          |          |
 ---- ACT 7: AI Security (~3 min) ----------------------------------------------------------------
     |          |          |          |          |          |          |          |          |
     |          |          |          |[AIBOM]   |          |          |          |          |
     |          |          |          |          |          |          |          |          |[discovery]
     |          |          |          |          |          |          |          |          |[MCP risk]
     |          |          |          |          |          |          |          |          |[OWASP]
     |          |          |          |          |          |          |          |          |[dashboard]
     |          |          |          |          |          |          |          |          |
     =          =          =          =          =          =          =          =          =

  Leyenda:
  |--------->|  Flecha derecha     = Actor izquierdo envia a actor derecho
  |<---------|  Flecha izquierda   = Actor derecho envia a actor izquierdo
  |[text]    |  Bloque en columna  = Accion interna del actor (self-action)
  |--- ... ->|  Flecha larga       = Atraviesa multiples columnas

  Actores:
  DEV        = Desarrollador (demo presenter)
  CLAUDE     = Claude Code (AI coding agent)
  GITHUB     = GitHub (repositorio, PRs)
  HARNESS    = Harness Platform (CI/CD, STO, SCS, Deploy)
  K8S        = Kubernetes cluster (namespace harnessbank-demo)
  ATTACKER   = Threat actor externo (Act 5)
  WAAP       = Runtime Protection Agent / Traceable (WAAP)
  AI-SRE     = Harness AI SRE (incident response, runbooks)
  AI-SEC     = Harness AI Security (AIBOM, OWASP LLM Top 10, dashboard)

  Duracion total estimada: ~29 minutos (5+3+4+3+5+3+3+buffer)
```
