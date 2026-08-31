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
             │ N-S (solid)                                  └────────────────────────────┘
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
  │  INGRESS -- nginx  (host: demobank.app)                                       │
  │  paths: /api/accounts  /api/ai  /api/admin  /                                │
  └──────────┬───────────────────────────────────────────────────────────────────┘
             │
  ┌──────────▼───────────────────────────────────────────────────────────────────┐
  │  K8S CLUSTER  (namespace: harnessbank-demo)                                  │
  │                                                                              │
  │  ┌────────────────────────────┐  - - E-W - - >  ┌─────────────────────────┐  │
  │  │  DemoBank Pod (:3000)      │  [BLIND SPOT]    │  MCP Financial Data    │  │
  │  │  Svc: harnessbank-demo     │  Apigee no ve    │  Pod (:5001)           │  │
  │  │  (LB 80 -> 3000)           │  trafico E-W     │  Svc: ClusterIP        │  │
  │  │                            │                   │  (internal only)       │  │
  │  │  /api/accounts  (VULN-001) │                   │                        │  │
  │  │  /api/ai/chat   (VULN-008) │                   │  /mcp/financial-data   │  │
  │  │  /api/ai/status  [ZOMBIE]  │                   │  /mcp/risk-profile     │  │
  │  │  /api/admin     (VULN-002) │                   │  /health               │  │
  │  │  /health                   │                   └─────────────────────────┘  │
  │  │                            │                                               │
  │  │  ┌───────────────┐        │                                               │
  │  │  │ SQLite        │        │                                               │
  │  │  │ demobank.db   │        │                                               │
  │  │  └───────────────┘        │                                               │
  │  └────────────────────────────┘                                               │
  │                                                                               │
  │  ┌──────────────────────────────────────────────────────────────────────────┐  │
  │  │  Traceable Agent (DaemonSet) -- Runtime Protection Agent                │  │
  │  │  Monitors: N-S + E-W traffic  |  AI Security: enabled                  │  │
  │  │  API Discovery | Behavioral Detection | Session Stitching               │  │
  │  │  Threat Scoring | Blocking | Virtual Patching                           │  │
  │  └──────────────────────────────────────────────────────────────────────────┘  │
  └───────────────────────────────────────────────────────────────────────────────┘
             ║
             ║ double: Harness integration
             ║
  ╔══════════╩═════════════════════════════════════════════════════════════════════╗
  ║  HARNESS PLATFORM                                                             ║
  ║                                                                               ║
  ║  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   ║
  ║  │ Software      │  │ Security      │  │ Runtime       │  │ Cost          │   ║
  ║  │ Delivery      │  │ Testing       │  │ Protection    │  │ Management    │   ║
  ║  │ Agent         │  │ Agent         │  │ Agent (WAAP)  │  │ Agent         │   ║
  ║  │               │  │               │  │               │  │               │   ║
  ║  │ CI/CD, TI,    │  │ STO, SAST,    │  │ API Disc.,    │  │               │   ║
  ║  │ Change Adv.   │  │ SCA, Triage   │  │ Blocking      │  │               │   ║
  ║  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   ║
  ║                                                                               ║
  ║  ┌───────┐   ┌───────┐   ┌───────────┐   ┌────────────────┐                  ║
  ║  │  STO  │   │  SCS  │   │  AI SRE   │   │  AI Security   │                  ║
  ║  │       │   │  SBOM │   │  Runbooks │   │  AIBOM, OWASP  │                  ║
  ║  └───────┘   └───────┘   └───────────┘   └────────────────┘                  ║
  ╚═══════════════════════════════════════════════════════════════════════════════╝

  Convenciones de flechas:
  ──────── Linea solida    = Trafico Norte-Sur (N-S)
  - - - -> Linea punteada  = Trafico Este-Oeste (E-W)
  ════════ Linea doble     = Conexion Harness Platform
  · · · ·  Linea de puntos = Bypass (trafico no registrado en gateway)

  [ZOMBIE]     = Endpoint no registrado en API Gateway, sin policies de seguridad
  [BLIND SPOT] = Trafico invisible para Apigee (solo visible para WAAP/Traceable)
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
