
<!-- ============================================================ -->
<!--  SecOps AI Agentic Demo — Executive Presentation Deck        -->
<!--  7 Acts  |  27 min  |  End-to-End Software Delivery + SecOps -->
<!-- ============================================================ -->

---

# SecOps AI Agentic Demo

```
 ____            ___                    _    ___
/ ___|  ___  ___/ _ \ _ __  ___        / \  |_ _|
\___ \ / _ \/ __| | | | '_ \/ __|      / _ \  | |
 ___) |  __/ (__| |_| | |_) \__ \     / ___ \ | |
|____/ \___|\___|\___/| .__/|___/    /_/   \_\___|
     _                |_|       _   _
    / \   __ _  ___ _ __ | |_(_) ___
   / _ \ / _` |/ _ \ '_ \| __| |/ __|
  / ___ \ (_| |  __/ | | | |_| | (__
 /_/   \_\__, |\___|_| |_|\__|_|\___|
         |___/
```

> **"El agente que escribe el codigo NO puede ser el que lo valida."**

---

## Agenda

```
  SHIFT LEFT                                    SHIELD RIGHT
  ──────────────────────────────────────────    ──────────────────────────────────
  Act 1 ─> Act 2 ─> Act 3 ─> Act 4        ──> Act 5 ─> Act 6 ─> Act 7
  Code     Review   Scan &    Deploy            Attack   Respond  Protect
  Gen      & Test   Remediate Governed          Chain    & Track  the AI
  ~4 min   ~3 min   ~5 min    ~3.5 min          ~6 min   ~3 min   ~3 min
  ──────────────────────────────────────────    ──────────────────────────────────
                                         PIVOT
                                      "Todo verde...
                                       o no?"
                                                          TOTAL: ~27 min
```

---

## Platform Overview — What Powers the Demo

```
  +-----------------------------------------------------------------------+
  |                        HARNESS PLATFORM                               |
  |                                                                       |
  |  +------------------+  +------------------+  +---------------------+  |
  |  |  CI / CD         |  |  STO             |  |  SCS                |  |
  |  |  - Pipelines     |  |  - AI SAST       |  |  - SBOM (cdxgen)   |  |
  |  |  - Test Intel.   |  |  - SCA           |  |  - SLSA L2 Attest. |  |
  |  |  - Canary Deploy |  |  - Gitleaks      |  |  - AIBOM           |  |
  |  |  - Rolling       |  |  - OPA Gates     |  |  - Remediation     |  |
  |  |  - Cont. Verif.  |  |                  |  |    Tracker         |  |
  |  +------------------+  +------------------+  +---------------------+  |
  |                                                                       |
  |  +------------------+  +------------------+  +---------------------+  |
  |  |  AI Agents       |  |  SRM             |  |  WAAP (Runtime)    |  |
  |  |  - Change Advis. |  |  - AI SRE        |  |  - API Discovery   |  |
  |  |  - Sec. Remed.   |  |  - Runbooks      |  |  - Behavioral Det. |  |
  |  |  - SW Delivery   |  |  - Incident Mgmt |  |  - Session Stitch. |  |
  |  |  - AI SRE        |  |                  |  |  - Virtual Patch   |  |
  |  +------------------+  +------------------+  +---------------------+  |
  +-----------------------------------------------------------------------+
```

**4 AI Agents en la Demo:**

| Agente | Tipo | Rol |
|--------|------|-----|
| Change Advisor | Worker | Analiza cambios del PR, clasifica riesgo, NO detecta vulns |
| Security Remediator | Worker | Auto-fix vulns tecnicas, defer vulns de logica |
| Software Delivery Agent | Orchestrator | Orquesta pipeline, deploy, governance |
| AI SRE | Responder | Incident response, runbooks, blast radius |

---

## Infrastructure

```
  +---------------------------+
  |  GitHub (crizstian/       |
  |    ai-agentic-demo)       |       Branches:
  |                           |       secops/ai-agentic-demo (vulns)
  |  PR ──webhook──> Harness  |         |
  +---------------------------+         | PR
                                        v
  +---------------------------+       secops/ai-agentic-demo-main (clean)
  |  Harness Platform         |
  |  Org: sandbox             |
  |  Project: CristianRamirez |
  |  Pipeline: AI_SDLC_       |
  |    DemoBank (INLINE)      |
  +---------------------------+
            |
            | deploy
            v
  +-------------------------------------------+
  |  GKE: se-sandbox (us-east1-b)            |
  |  Node Pool: ai-agentic-demo-nodepool     |
  |  Machine: e2-standard-4 (autoscale 1-2)  |
  |                                           |
  |  +---------------+   +----------------+  |
  |  | harnessbank-  |   | mcp-financial- |  |
  |  | demo          |   | data           |  |
  |  | (LoadBalancer) |   | (ClusterIP)    |  |
  |  | port 80       |   | port 5001      |  |
  |  +-------+-------+   +--------+-------+  |
  |          |     East-West       |          |
  |          +<────────────────────+          |
  |                                           |
  |  +-------------------------------------+ |
  |  | Traceable Agents (DaemonSet)        | |
  |  | TPA + eBPF Tracer + AST Runner     | |
  |  +-------------------------------------+ |
  +-------------------------------------------+
            |
            v
  +---------------------------+
  |  Ingress: NGINX           |
  |  demobank.selatam.        |
  |    harness-demo.site      |
  |  IP: 35.227.123.79       |
  +---------------------------+
```

---

## Pipeline Architecture

```
  +=========================================================================+
  |  AI_SDLC_DemoBank Pipeline                                              |
  |=========================================================================|
  |                                                                         |
  |  ON PR EVENT:                                                           |
  |  +-------------------------------------------------------------------+ |
  |  | STAGE 1: Build (CI) — PR Validation                               | |
  |  |                                                                   | |
  |  |  [Build Validation] -> [Test Intelligence] -> [Change Advisor]    | |
  |  |        pip install        11/47 tests           AI Expert Agent   | |
  |  |        py_compile         65% savings           Risk Assessment   | |
  |  |                                                                   | |
  |  |  [Security Scanning — PARALLEL]                                   | |
  |  |  +-------------+ +------------------+ +------------------+       | |
  |  |  | Gitleaks    | | AI SAST          | | SCA              |       | |
  |  |  | (secrets)   | | (code vulns)     | | (dependencies)   |       | |
  |  |  +-------------+ +------------------+ +------------------+       | |
  |  |                                                                   | |
  |  |  [Security Remediator]  <-- conditional: HIGH findings > 0       | |
  |  |   Auto-fix technical vulns, defer business logic                  | |
  |  +-------------------------------------------------------------------+ |
  |                                                                         |
  |  ON PUSH TO secops/ai-agentic-demo-main:                               |
  |  +-------------------------------------------------------------------+ |
  |  | STAGE 1: Build — Docker + Supply Chain                            | |
  |  |  [Docker Build x2 — PARALLEL]    [SBOM x2 — cdxgen + cosign]     | |
  |  |   harnessbank-demo                Keyless attestation             | |
  |  |   mcp-financial-data              Harness OIDC / SLSA L2         | |
  |  +-------------------------------------------------------------------+ |
  |  | STAGE 2: Deploy DemoBank                                          | |
  |  |  Canary (count: 2) -> Canary Delete -> Rolling                    | |
  |  +-------------------------------------------------------------------+ |
  |  | STAGE 3: Deploy MCP Financial Data                                | |
  |  |  Rolling Deployment (ClusterIP)                                   | |
  |  +-------------------------------------------------------------------+ |
  +=========================================================================+
```

---

## OPA Governance Policies

```
  Policy Set: secops_demo_gates
  Action: onrun | Entity: pipeline | Status: ENABLED

  +---------------------------+-------+-------------------------------------+
  | Policy                    | Act   | Rule                                |
  +---------------------------+-------+-------------------------------------+
  | no-critical-findings      | Act 3 | Block if CRITICAL or HIGH CVSS>=9  |
  | slsa-attestation-required | Act 4 | Require SLSA L2 + cosign verified  |
  | security-scan-required    | Act 4 | Require completed security stage   |
  | block-unprotected-ai-ep   | Act 6 | Block /ai/ endpoints without auth  |
  +---------------------------+-------+-------------------------------------+
```

---

<!-- ================================================================== -->
<!--                          THE 7 ACTS                                -->
<!-- ================================================================== -->

# The 7 Acts

```
     SHIFT LEFT                                          SHIELD RIGHT
     ========================                            =========================

     Act 1        Act 2        Act 3        Act 4        Act 5        Act 6        Act 7
     +-----+      +-----+      +-----+      +-----+      +-----+      +-----+      +-----+
     |     |      |     |      |     |      |     |      |     |      |     |      |     |
     | <C> |  ->  | <R> |  ->  | <S> |  ->  | <D> |  ->  | <A> |  ->  | <I> |  ->  | <P> |
     |     |      |     |      |     |      |     |      |     |      |     |      |     |
     +-----+      +-----+      +-----+      +-----+      +-----+      +-----+      +-----+
     Code         Review       Scan &       Deploy       Attack       Incident     Protect
     Generation   & Test       Remediate    Governed     Chain        Response     the AI

     Inner Loop   PR Valid.    STO + SCS    Canary+CV    WAAP         SRM + SCS    AIBOM
     AI Agent     TI + Adv.    OPA Gate     SLSA + OPA   5-step       AI SRE       AI SecTest
     ~4 min       ~3 min       ~5 min       ~3.5 min     ~6 min       ~3 min       ~3 min
```

---

# ACT 1

## El Codigo Ya Se Escribe a Velocidad de AI

```
  +===========================================================================+
  ||                                                                         ||
  ||     _____  _            _____                         _                 ||
  ||    |_   _|| |__   ___  |_   _|_ __  _ __   ___  _ __| |   ___   ___   _ __    ||
  ||      | |  | '_ \ / _ \   | | | '_ \| '_ \ / _ \| '__| |  / _ \ / _ \ | '_ \  ||
  ||      | |  | | | |  __/   | | | | | | | | |  __/| |  | |_| (_) | (_) || |_) | ||
  ||      |_|  |_| |_|\___|   |_| |_| |_|_| |_|\___||_|  |____\___/ \___/ | .__/  ||
  ||                                                                       |_|    ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~4 minutos |
| **Modulos** | Harness MCP, IDE Extension, AI Chat Agent |
| **Narrativa** | Un developer usa Claude Code para crear un AI Banking Assistant |

### Que Pasa

```
  Developer                    Claude Code                     GitHub
  +---------+                  +-----------+                   +--------+
  |         | --- "build AI    |           |                   |        |
  |  IDE    |     assistant"   |  Genera   |                   |        |
  |  + MCP  | --------------> |  codigo   | --- PR #52 -----> | secops/|
  |         |                  |  en <2min |                   | ai-... |
  +---------+                  +-----------+                   +--------+
                                    |
                                    | Introduce silenciosamente:
                                    |
                               +----+----+
                               |  3 Vulns de Logica  |
                               |  BOLA    (VULN-010) |
                               |  Prompt  (VULN-008) |
                               |  PII     (VULN-009) |
                               +---------+-----------+
                                          |
                                    + 1 dep vulnerable
                                    requests==2.25.1
```

### Momentos Clave del Demo

1. **SDLC context en un prompt** — MCP conecta al IDE con Harness
2. **Feature completa en <2 min** — el codigo se ve profesional
3. **PR auto-trigger** — la creacion del PR dispara el pipeline
4. **Tesis central**: _"El agente que escribe el codigo NO puede ser el que lo valida"_

### Las 3 Vulnerabilidades Ocultas (Sorpresa para Act 5)

| ID | Tipo | Descripcion | Por que SAST no la detecta |
|----|------|-------------|---------------------------|
| VULN-008 | Prompt Injection | Input del usuario concatenado en system prompt | Logica de negocio, no patron de codigo |
| VULN-009 | PII Exposure | Nombres, balances, URLs internas en response | Data classification, no syntax |
| VULN-010 | BOLA/IDOR | `/api/accounts/{id}/details` sin auth check | Requiere threat model, no grep |

---

# ACT 2

## Software Delivery Agent — Gobernar Cada Cambio

```
  +===========================================================================+
  ||                                                                         ||
  ||      ____           _                   _                               ||
  ||     / ___|___   __| | ___   _ __ _____   _(_) _____      __            ||
  ||    | |   / _ \ / _` |/ _ \ | '__/ _ \ \ / / |/ _ \ \ /\ / /            ||
  ||    | |__| (_) | (_| |  __/ | | |  __/\ V /| |  __/\ V  V /             ||
  ||     \____\___/ \__,_|\___| |_|  \___| \_/ |_|\___| \_/\_/              ||
  ||                                                                         ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~3 minutos |
| **Modulos** | Software Delivery Agent, Test Intelligence, Change Advisor |
| **Narrativa** | El pipeline se activa automaticamente. AI analiza, no escanea |

### Que Pasa

```
  PR Created
      |
      v
  +------------------+     +------------------+     +--------------------+
  | Build Validation |     | Test Intelligence|     | Change Advisor     |
  |                  | --> |                  | --> |                    |
  | pip install      |     | 11 / 47 tests    |     | Risk: MEDIUM       |
  | py_compile       |     | 65% time saved   |     | Flags risk areas   |
  |                  |     | ML-based select  |     | NOT specific vulns |
  +------------------+     +------------------+     +--------------------+
                                                           |
                                                           v
                                                    +--------------+
                                                    | PR Comment   |
                                                    | Structured   |
                                                    | Risk Report  |
                                                    +--------------+
```

### Change Advisor — Que Analiza vs Que NO

```
  +------------------------------+     +------------------------------+
  |  SI ANALIZA                  |     |  NO DETECTA                  |
  +------------------------------+     +------------------------------+
  |  * Nuevos endpoints          |     |  x SQL Injection             |
  |  * Procesamiento de input    |     |  x BOLA/IDOR                 |
  |  * Acceso a datos financ.    |     |  x Prompt Injection          |
  |  * Dependencias nuevas       |     |  x PII Exposure              |
  |  * Tests faltantes           |     |  x Vulnerabilidades          |
  |  * Clasificacion de riesgo   |     |    especificas               |
  +------------------------------+     +------------------------------+
         "Risk Areas"                      "Eso es trabajo de STO"
```

### Momentos Clave

1. **Zero context switching** — todo se consume desde VS Code + Harness AI Chat
2. **Test Intelligence** — ML selecciona solo tests correlacionados (11/47)
3. **Change Advisor ≠ Security Scanner** — clasifica riesgo, no identifica vulns
4. **Separacion de responsabilidades** — cada agente tiene su alcance

---

# ACT 3

## Security Testing Agent — Encontrar Y Remediar a Machine Speed

```
  +===========================================================================+
  ||                                                                         ||
  ||     ____                       _ _                                      ||
  ||    / ___|  ___  ___ _   _ _ __(_) |_ _   _                             ||
  ||    \___ \ / _ \/ __| | | | '__| | __| | | |                            ||
  ||     ___) |  __/ (__| |_| | |  | | |_| |_| |                            ||
  ||    |____/ \___|\___|\__,_|_|  |_|\__|\__, |                             ||
  ||                                      |___/                              ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~5 minutos |
| **Modulos** | STO (AI SAST + SCA + Gitleaks), OPA, SCS (SBOM + SLSA), Security Remediator |
| **Narrativa** | Escaneo completo + remediacion automatica. Pero las vulns de logica sobreviven |

### Flujo Completo

```
  +------------------+     +------------------+     +-----------------+
  |  PARALLEL SCAN   |     |  OPA POLICY      |     |  SECURITY       |
  |                  |     |  GATE             |     |  REMEDIATOR     |
  |  +-----------+   |     |                  |     |                 |
  |  | Gitleaks  |   |     |  CRITICAL or     |     |  AUTO-FIX:      |
  |  | (secrets) |   |     |  HIGH CVSS>=9?   |     |  * SQLi          |
  |  +-----------+   | --> |                  | --> |  * XSS           |
  |  +-----------+   |     |  YES = BLOCK     |     |  * Cmd Inject    |
  |  | AI SAST   |   |     |  NO  = PASS      |     |  * Dep bumps     |
  |  | (code)    |   |     |                  |     |                 |
  |  +-----------+   |     |                  |     |  DEFER:          |
  |  +-----------+   |     |                  |     |  * BOLA          |
  |  | SCA       |   |     |                  |     |  * Prompt Inj.   |
  |  | (deps)    |   |     |                  |     |  * MCP Trust     |
  |  +-----------+   |     |                  |     |  * PII Exposure  |
  +------------------+     +------------------+     +-----------------+
         |                                                   |
         v                                                   v
  +------------------+                              +-----------------+
  |  AI SAST Results |                              |  PR Comment:    |
  |                  |                              |  Auto-Remediated|
  |  SQLi     96%    |                              |  + Deferred     |
  |  CmdInj   94%    |                              +-----------------+
  |  XSS      91%    |
  |  CORS     88%    |
  |  + SCA: CVE-2023 |
  +------------------+
```

### Supply Chain Security (Post-merge)

```
  +-------------------+     +--------------------+     +------------------+
  |  Docker Build x2  |     |  SBOM Generation   |     |  SLSA L2         |
  |                   | --> |  cdxgen            | --> |  Attestation     |
  |  harnessbank-demo |     |  CycloneDX JSON    |     |  Keyless cosign  |
  |  mcp-financial-   |     |  47 dependencies   |     |  Harness OIDC    |
  |    data           |     |                    |     |                  |
  +-------------------+     +--------------------+     +------------------+
```

### Momentos Clave

1. **AI SAST confidence scoring** — 79% menos falsos positivos
2. **OPA policy gate** — bloquea pipeline automaticamente
3. **Triage**: CVSS + EPSS + reachability analysis
4. **Remediacion**: de 55 dias (industria) a minutos
5. **SBOM + attestation** — compliance para industrias reguladas
6. **Las 3 vulns de logica SOBREVIVEN** — SAST no puede detectar fallas de logica/comportamiento

---

# ACT 4

## Software Delivery Agent — Deploy Gobernado

```
  +===========================================================================+
  ||                                                                         ||
  ||     ____             _                                                  ||
  ||    |  _ \  ___ _ __ | | ___  _   _                                     ||
  ||    | | | |/ _ \ '_ \| |/ _ \| | | |                                    ||
  ||    | |_| |  __/ |_) | | (_) | |_| |                                    ||
  ||    |____/ \___| .__/|_|\___/ \__, |                                     ||
  ||               |_|            |___/                                      ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~3.5 minutos |
| **Modulos** | SCS (SLSA verification), OPA Governance, Canary + CV, Change Mgmt |
| **Narrativa** | Todo pasa. Todo verde. Las vulns de logica llegan a produccion |

### 3 Gates Pre-Deploy

```
  PR Merged to secops/ai-agentic-demo-main
      |
      v
  +=====================================================================+
  |  PRE-DEPLOY GOVERNANCE                                              |
  |                                                                     |
  |  GATE 1              GATE 2              GATE 3                     |
  |  +----------------+  +----------------+  +------------------------+ |
  |  | SLSA L2        |  | OPA Policies   |  | Change Management      | |
  |  | Verification   |  | (4 policies)   |  |                        | |
  |  |                |  |                |  | Auto-generated ticket  | |
  |  | * Provenance   |  | * No criticals |  | with evidence:         | |
  |  | * Integrity    |  | * SLSA attested|  | - Scan results         | |
  |  | * cosign       |  | * Scan done    |  | - SBOM                 | |
  |  | * Level >= 2   |  | * AI protected |  | - Attestation proof    | |
  |  |                |  |                |  |                        | |
  |  |    PASS        |  |    PASS        |  |    APPROVED            | |
  |  +----------------+  +----------------+  +------------------------+ |
  +=====================================================================+
      |
      v
  +==========================================================+
  |  DEPLOYMENT                                               |
  |                                                           |
  |  +----------+     +----------+     +------------------+   |
  |  | Canary   |     | Cont.    |     | Rolling          |   |
  |  | (2 pods) | --> | Verif.   | --> | Deployment       |   |
  |  |          |     | ML-based |     | (full rollout)   |   |
  |  |          |     |          |     |                  |   |
  |  |          |     | canary   |     |                  |   |
  |  |          |     | vs base  |     |                  |   |
  |  |          |     | PROCEED  |     |                  |   |
  |  +----------+     +----------+     +------------------+   |
  +==========================================================+
      |
      v
  +---------------------------------------------+
  |                                             |
  |   "Todo verde... o no?"                     |
  |                                             |
  |   3 vulnerabilidades de logica              |
  |   estan ahora en PRODUCCION                 |
  |                                             |
  |   BOLA + Prompt Injection + PII Exposure    |
  |                                             |
  +---------------------------------------------+
```

### Momentos Clave

1. **SLSA L2 verification** — provenance + integrity pre-deploy
2. **OPA policy-as-code** — 4 politicas evaluadas automaticamente
3. **Continuous Verification** — ML compara distribuciones estadisticas canary vs baseline
4. **La trampa narrativa** — todo se ve verde, pero las vulns de logica estan en prod

> **Este es el PIVOT entre Shift Left y Shield Right**

---

# ACT 5

## El Ataque — Los Atacantes Tambien Tienen AI

```
  +===========================================================================+
  ||                                                                         ||
  ||       _   _   _             _                                           ||
  ||      / \ | |_| |_ __ _  ___| | __                                      ||
  ||     / _ \| __| __/ _` |/ __| |/ /                                       ||
  ||    / ___ \ |_| || (_| | (__|   <                                        ||
  ||   /_/   \_\__|\__\__,_|\___|_|\_\                                       ||
  ||                                                                         ||
  ||              ___ _           _                                          ||
  ||             / __| |__   __ _(_)_ __                                     ||
  ||            | |  | '_ \ / _` | | '_ \                                   ||
  ||            | |__| | | | (_| | | | | |                                  ||
  ||             \___|_| |_|\__,_|_|_| |_|                                   ||
  ||                                                                         ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~6 minutos |
| **Modulos** | WAAP (Runtime Protection Agent) |
| **Narrativa** | Un atacante con AI explota las vulns que SAST no detecto. WAF = ciego. WAAP = ve todo |

### La Cadena de Ataque — 5 Pasos

```
  ATACANTE (con AI)
      |
      |  Step 1: Zombie API Discovery
      |  GET /api/ai/status
      |  (no auth, no docs, expone model + MCP URLs)
      |
      v
  +---+---+  N-S
  |  DemoBank  |-----------------------------+
  +---+---+                                  |
      |                                      |
      |  Step 2: Prompt Injection            |  Step 2b: E-W Call
      |  POST /api/ai/chat                   |  (triggered by injection)
      |  "Ignora instrucciones..."           |
      |                                      v
      |                               +------+------+
      |                               | MCP Financial|
      |                               | Data Service |
      |                               | (ClusterIP)  |
      |                               +------+------+
      |                                      |
      |  Step 3: PII Leak                    |
      |  Response incluye:                   |
      |  - account owners + balances         |
      |  - internal MCP URLs                 |
      |  - system prompt confirmado          |
      |                                      |
      |  Step 4: BOLA/IDOR
      |  GET /api/accounts/1/details
      |  GET /api/accounts/2/details
      |  GET /api/accounts/3/details
      |  (sin auth check)
      |
      |  Step 5: Data Exfiltration
      |  GET /api/accounts/4..10/details
      |
      v
  +----------+
  |  BLOCKED |  <-- WAAP: 403 + Virtual Patch
  |   (403)  |
  +----------+
```

### WAF vs WAAP — Scorecard

```
  +-------+----------------------------------------------------+
  | Step  | Descripcion              | WAF         | WAAP       |
  +-------+--------------------------+-------------+------------+
  |   1   | Zombie API Discovery     | invisible   | cataloged  |
  |   2   | Prompt Injection (N-S)   | JSON valid  | anomaly    |
  |  2b   | MCP Call (E-W)           | BLIND       | E-W detect |
  |   3   | PII Leak                 | 200 OK      | data viol. |
  |   4   | BOLA/IDOR                | valid GETs  | session    |
  |       |                          |             | stitching  |
  |   5   | Exfiltration             | valid GETs  | BLOCKED    |
  +-------+--------------------------+-------------+------------+
  | TOTAL | Detected                 |    0 / 5    |   5 / 5    |
  |       | Blocked                  |    0 / 5    |   1 + VP   |
  +-------+--------------------------+-------------+------------+
```

### Capacidades WAAP Demostradas

| Capacidad | Que Hace | Cuando se ve |
|-----------|----------|-------------|
| API Discovery | Cataloga endpoints automaticamente | Step 1 |
| Behavioral Baseline | Detecta anomalias vs trafico normal | Step 2 |
| E-W Visibility | Ve trafico interno (eBPF) | Step 2b |
| Data Sensitivity | Detecta PII en responses | Step 3 |
| Session Stitching | Correlaciona toda la cadena (7 dias) | Step 4 |
| Threat Scoring | 35 -> 65 -> 85 (escalation) | Steps 2-4 |
| Blocking + Virtual Patch | Bloquea y parchea sin codigo | Step 5 |

---

# ACT 6

## Shield Right + Shift Left — Respuesta a Machine Speed

```
  +===========================================================================+
  ||                                                                         ||
  ||     ____                                                                ||
  ||    |  _ \ ___  ___ _ __   ___  _ __  ___  ___                           ||
  ||    | |_) / _ \/ __| '_ \ / _ \| '_ \/ __|/ _ \                          ||
  ||    |  _ <  __/\__ \ |_) | (_) | | | \__ \  __/                          ||
  ||    |_| \_\___||___/ .__/ \___/|_| |_|___/\___|                          ||
  ||                   |_|                                                   ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~3 minutos |
| **Modulos** | AI SRE, SCS Remediation Tracker, SBOM, OPA |
| **Narrativa** | Del ataque a la respuesta coordinada en segundos |

### Flujo de Respuesta

```
  WAAP Alert
      |
      v
  +---+---+                    +---+---+
  | AI SRE |                   | Remediation Tracker |
  |        |                   |                     |
  | 12 sec |                   | Affected artifacts: |
  | runbook|                   | - prod              |
  |        |                   | - staging           |
  | * SEV1 incident            | - dev               |
  | * Slack notify             |                     |
  | * PagerDuty page           | Auto-track progress |
  | * Jira ticket              +---+---+             |
  | * Zoom bridge                  |                 |
  | * Summary                      v                 |
  +---+---+                    +---+---+             |
      |                        | SBOM Blast Radius   |
      |                        |                     |
      |                        | 8 sec analysis      |
      |                        | legacy-api also     |
      |                        | uses requests 2.25  |
      |                        +---+---+             |
      |                            |                 |
      v                            v                 |
  +-------------------------------------------------------+
  |  NEW OPA POLICY (Post-Incident Governance)            |
  |                                                       |
  |  block-unprotected-ai-endpoints.rego                  |
  |  * Block /ai/ endpoints without auth                  |
  |  * Block if prompt_injection == true in scan          |
  |                                                       |
  |  "Lo que paso una vez, no pasa dos veces"             |
  +-------------------------------------------------------+
```

### Momentos Clave

1. **12-second automated runbook** — AI SRE ejecuta 6 acciones
2. **Remediation Tracker** — tracking en vivo por artifact/environment
3. **Blast radius en 8 seg** — vs 5 dias manual
4. **Post-incident governance** — nuevo OPA policy codifica la leccion

---

# ACT 7

## AI Security — Proteger el AI que Te Protege

```
  +===========================================================================+
  ||                                                                         ||
  ||        _    ___   ____                       _ _                         ||
  ||       / \  |_ _| / ___|  ___  ___ _   _ _ __(_) |_ _   _               ||
  ||      / _ \  | |  \___ \ / _ \/ __| | | | '__| | __| | | |              ||
  ||     / ___ \ | |   ___) |  __/ (__| |_| | |  | | |_| |_| |              ||
  ||    /_/   \_\___| |____/ \___|\___|\__,_|_|  |_|\__|\__, |              ||
  ||                                                     |___/               ||
  +===========================================================================+
```

| | |
|---|---|
| **Duracion** | ~3 min + 60s cierre |
| **Modulos** | SCS (AIBOM), WAAP (AI Discovery, MCP Risk Score, AI Security Testing) |
| **Narrativa** | SBOM para software, AIBOM para AI. Proteger el AI que te protege |

### 4 Capas de AI Security

```
  LAYER 1: AIBOM (SCS)                    LAYER 2: AI Discovery (Runtime)
  +-------------------------------+        +-------------------------------+
  |  Descubre AI en SOURCE CODE   |        |  Descubre AI en LIVE TRAFFIC  |
  |                               |        |                               |
  |  * Model: GPT-4              |        |  * 2 AI APIs                  |
  |  * Library: openai SDK       |        |  * 1 MCP server               |
  |  * Tool: financial-data-svc  |        |  * 2 tools                    |
  |  * Framework: Flask          |        |  * 1 prompt                   |
  |                               |        |                               |
  |  CycloneDX format            |        |  From live East-West traffic  |
  |  File + line number          |        |                               |
  +-------------------------------+        +-------------------------------+

  LAYER 3: MCP Risk Score                  LAYER 4: AI Security Testing
  +-------------------------------+        +-------------------------------+
  |  Multi-factor scoring         |        |  OWASP LLM Top 10            |
  |                               |        |                               |
  |  Data Sensitivity:  9/10      |        |  LLM01: Prompt Injection FAIL |
  |  Exposure:          7/10      |        |  LLM02: Sensitive Data   FAIL |
  |  Auth Gaps:         8/10      |        |  LLM03: Supply Chain     PASS |
  |  Behavioral Anom.:  6/10      |        |  ...                         |
  |  ─────────────────────        |        |                               |
  |  Overall:        7.8/10 HIGH  |        |  Confirms VULN-008 / 009     |
  |                               |        |  from Act 1 / Act 5          |
  +-------------------------------+        +-------------------------------+
```

### El Circulo Se Cierra

```
  Act 1                    Act 3                    Act 5                    Act 7
  +----------+             +----------+             +----------+             +----------+
  | AI Agent |             | SAST     |             | Attacker |             | OWASP    |
  | escribe  |             | detecta  |             | explota  |             | LLM Top  |
  | VULN-008 |             | SQLi,XSS |             | BOLA,    |             | 10 test  |
  | VULN-009 | ----------> | NO logica| ----------> | Prompt   | ----------> | confirma |
  | VULN-010 |             | SOBREVIVE|             | Inj, PII |             | VULN-008 |
  +----------+             +----------+             +----------+             | VULN-009 |
                                                                             +----------+
  "El codigo se           "Las herramientas         "Los atacantes           "AIBOM + AI
   escribe solo"           tienen limites"           tambien tienen AI"       Security
                                                                              Testing"
```

---

# Cierre — 60 Segundos

```
  +=======================================================================+
  |                                                                       |
  |  "En 27 minutos vimos codigo-a-produccion-a-ataque-a-respuesta"       |
  |                                                                       |
  |  4 AI Agents:                                                         |
  |    Change Advisor .... analizo riesgo del cambio                       |
  |    Security Remediator auto-fixeo vulns tecnicas en minutos            |
  |    AI SRE ............ respondio al incidente en 12 segundos           |
  |    Software Delivery . orquesto todo el flujo                          |
  |                                                                       |
  |  Shift Left:                                                          |
  |    * Test Intelligence (65% menos tiempo)                             |
  |    * AI SAST (79% menos false positives)                              |
  |    * SBOM + SLSA L2 attestation                                       |
  |    * OPA governance-as-code                                           |
  |                                                                       |
  |  Shield Right:                                                        |
  |    * WAAP detecto 5/5 pasos (WAF: 0/5)                               |
  |    * Session Stitching correlaciono N-S + E-W                         |
  |    * Virtual Patching sin cambio de codigo                            |
  |    * Blast radius en 8 segundos                                       |
  |    * AIBOM + AI Security Testing                                      |
  |                                                                       |
  |  La pregunta no es SI tu AI va a introducir vulnerabilidades.          |
  |  La pregunta es CUANDO. Y cuando pase, necesitas la plataforma        |
  |  que gobierna todo el ciclo.                                           |
  |                                                                       |
  +=======================================================================+
```

---

## Apendice — Demo Reset (Branch Strategy)

```
  demo-baseline-v3 (tag)
       |
       +---> secops/ai-agentic-demo-main  (clean + infra)
       |         ^
       |         | PR (Act 1-3)
       |         |
       +---> secops/ai-agentic-demo  (clean + infra + Act 1 vulns)

  Reset: recrear branches desde el tag, repetir N veces
```

## Apendice — Tokens / Secrets Requeridos

| Secret | Para que | Donde se configura |
|--------|----------|-------------------|
| `account.harnessAnthropic` | AI Agents (LLM) | Harness Account Connectors |
| `mcp_github_cristian` | GitHub MCP | Harness Project Connectors |
| `mcp_harness_cristian` | Harness MCP | Harness Project Connectors |
| `traceable_agent_token` | TPA Runtime Agent | app.traceable.ai > Admin > Agent Token |
| `traceable_platform_token` | AST Runner (DAST) | app.traceable.ai > Admin > Platform Token |
| `DockerCristian` | Docker Registry | Harness Project Connectors |

