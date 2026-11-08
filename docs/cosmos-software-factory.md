# Cosmos + Harness: AI Software Factory

> **NOTA**: Este doc contiene el analisis inicial de la metodologia RSC Factory.
> La arquitectura final con mapeo Inner/Outer Loop esta en
> [`factory-architecture.md`](factory-architecture.md).

> Cosmos aporta los trabajadores autonomos. Harness aporta la linea de ensamble.
> Juntos forman una fabrica de software donde el humano dirige, no ejecuta.

---

## De la Teoria a la Plataforma

La metodologia de Software Factory (RSC Factory / ASDD) define un proceso
donde el trabajo entra, se transforma por agentes AI, se revisa, y sale
listo para produccion — sin que el humano sea el cuello de botella.

El problema: montar esa fabrica requiere orquestar muchas piezas.
Cosmos + Harness ya las tienen construidas.

### Mapeo: Metodologia → Plataforma

```
 METODOLOGIA (RSC Factory)              PLATAFORMA (Cosmos + Harness)
 ─────────────────────────              ──────────────────────────────

 ┌─────────────┐
 │   INPUTS    │ Sentry, GitHub         Cosmos Triggers + Automations
 │             │ issues, Slack,         (GitHub PR, Slack command,
 │             │ tareas manuales        PagerDuty, cron, webhooks)
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │   BRAIN     │ Memoria persistente    Cosmos Files + Skills + Memory
 │             │ de contexto, decisiones,  + CLAUDE.md / project docs
 │             │ arquitectura           Harness Audit Trail (historial)
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ SPEC WRITER │ Opus crea spec         Cosmos Expert: "Spec Writer"
 │             │ consultando Brain      (consulta Files/Skills antes
 │             │                          de escribir cualquier spec)
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │   BUILDER   │ Opus implementa        Cosmos Expert: "Builder"
 │             │ con TDD, en worktree,  (Environment con repo,
 │             │ consultando Brain        /goal con specs, TDD)
 └──────┬──────┘
        │
        ▼
 ┌─────────────────────────────────────────────────────┐
 │              4 REVISORES (modelos diversos)          │
 │                                                      │
 │  Seguridad    UX         UI          Codigo          │
 │  (Sol)       (Sol)     (Astra)     (Sonnet)          │
 │                                                      │
 │  Cosmos       Cosmos    Cosmos      Cosmos            │
 │  Expert       Expert    Expert      Expert            │
 │  + Harness    + Brain   + computer  + Brain           │
 │  STO/SCS      context   use         context           │
 └──────────────────┬──────────────────────────────────┘
                    │
                    ▼
 ┌─────────────┐
 │  APPROVER   │ Opus consolida         Cosmos Expert: "Approver"
 │             │ feedback, decide       (recibe 4 reviews, decide
 │             │ loop o aprobar           fix loop vs aprobar)
 └──────┬──────┘
        │
        ├── feedback negativo ──> vuelve al BUILDER
        │
        ▼
 ┌─────────────┐
 │ RISK ROUTER │ Trivial → auto-merge   Cosmos Automation + Harness OPA
 │             │ Core → humano aprueba  (policies determinan riesgo,
 │             │                          Slack notifica al humano)
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │  PIPELINE   │ Build, test, scan,     Harness CI/CD Pipeline
 │             │ quality gate, deploy   (SAST, SCA, AI Evals,
 │             │                          canary, rollback)
 └─────────────┘
```

---

## Las 3 Piezas que la Metodologia Exige

### 1. Repetible — Cada tarea sigue el mismo camino

| Requisito | Sin plataforma | Con Cosmos + Harness |
|-----------|---------------|---------------------|
| Mismo flujo siempre | Script manual, se olvidan pasos | Automation: trigger → spec → build → review → approve → pipeline |
| Paralelo | Multiples terminales | Cosmos ejecuta N tareas simultaneas, cada una en su Environment |
| Inputs diversos | Copiar/pegar entre tools | Un Trigger por fuente: Sentry → auto-issue, Slack → tarea, GitHub → PR |

### 2. Auditable — Cada paso deja rastro

| Requisito | Sin plataforma | Con Cosmos + Harness |
|-----------|---------------|---------------------|
| Quien hizo que | Git blame parcial | Cosmos Sessions (cada turno grabado) + Harness Audit Trail |
| Que decidio el agente | Perdido en terminal | Cosmos Memory + Files persisten decisiones |
| Por que fallo | Revisar logs manual | Harness execution logs + AI Evals results |
| Evidencia de review | Comentario en PR | Cosmos Expert genera evidencia, Harness la registra como gate |

### 3. Brain — Contexto persistente y continuo

| Requisito | Sin plataforma | Con Cosmos + Harness |
|-----------|---------------|---------------------|
| Decisiones previas | En la cabeza del dev | Cosmos Files + Skills (compartidos org-wide) |
| Arquitectura | README desactualizado | CLAUDE.md + Brain docs vivos, actualizados por Experts |
| Restricciones | Tribal knowledge | Cosmos Skills (agentskills.io) empaquetan conocimiento |
| Historial de specs | Archivos sueltos | Cosmos Files + git history + Harness audit |

---

## ASDD (Agent Spec Driven Development) en Cosmos

La evolucion clave del video: el agente no solo debe pasar tests,
debe **demostrar** que cumple el requisito. Tests solos generan Frankensteins.

### Spec Format para Cosmos Experts

Cada spec que el "Spec Writer" Expert genera debe incluir:

```yaml
spec:
  id: SPEC-001
  title: "Endpoint POST /api/ai/chat"

  what_user_can_do:
    - "Enviar mensaje de chat al asistente AI"
    - "Recibir respuesta con contexto financiero"

  starting_conditions:
    - "Feature flag ai_chat_backend esta ON"
    - "MCP Financial Data service esta accesible"
    - "OpenAI API key configurada en ConfigMap"

  expected_result:
    api_response:
      status: 200
      body_contains: ["response", "financial_context", "model"]
    behavior:
      - "Concatena mensaje del usuario directo en prompt (vuln intencional)"
      - "Consulta MCP service para enriquecer contexto"

  must_respect:
    - "No modificar rutas existentes (/accounts, /admin)"
    - "No crear archivos nuevos fuera de app/routes/"
    - "Usar lazy init para Split SDK (evitar timeout en CI)"
    - "Response JSON keys exactas: response, financial_context, model"

  how_to_demonstrate:
    - "curl POST /api/ai/chat con message='hello' → 200 + JSON valido"
    - "curl POST /api/ai/chat sin flag → 403"
    - "pytest tests/ pasa sin errores"

  evidence:
    - "Screenshot o curl output del endpoint respondiendo"
    - "Test results en junit.xml"
    - "Commit hash con el cambio"
```

### Review During Implementation (no despues)

```
         ┌─────────────────────────────────────────────┐
         │        COSMOS: IMPLEMENTATION LOOP           │
         │                                              │
         │  ┌──────────┐    ┌───────────────────────┐  │
         │  │ Builder   │───>│ Self-check             │  │
         │  │ Expert    │    │ (tests, lint, compile) │  │
         │  └──────────┘    └───────────┬─────────────┘  │
         │       ▲                      │               │
         │       │              ┌───────▼──────────┐    │
         │       │              │ 4 Sub-reviewers   │    │
         │       │              │ (clean context,   │    │
         │       │              │  different models)│    │
         │       │              └───────┬──────────┘    │
         │       │                      │               │
         │       │              ┌───────▼──────────┐    │
         │       │              │ Verify findings   │    │
         │       │              │ (dedup, sort by   │    │
         │       │              │  severity, check  │    │
         │  fix  │              │  against real code)│    │
         │       │              └───────┬──────────┘    │
         │       │                      │               │
         │       │              ┌───────▼──────────┐    │
         │       └──────────────│ Approver Expert   │    │
         │        (if issues)   │ (consolidate,     │    │
         │                      │  decide: fix or   │    │
         │                      │  ship)            │    │
         │                      └───────┬──────────┘    │
         │                              │               │
         └──────────────────────────────┼───────────────┘
                                        │ approved
                                        ▼
         ┌──────────────────────────────────────────────┐
         │        HARNESS: DELIVERY PIPELINE             │
         │                                               │
         │  PR → CI → SAST/SCA → AI Evals → CD → Live  │
         └──────────────────────────────────────────────┘
```

---

## La Leccion del Frankenstein

El video cuenta un caso real: 12 specs, 8 horas de autonomia, 4500 tests
generados. Resultado: un Frankenstein. El agente:

- **Asumio** decisiones no especificadas (agrego QR auth no pedido)
- **Omitio** requisitos alegando seguridad
- **Agrego** comportamientos no solicitados

**Root cause**: "pasar los tests" como unica metrica no es suficiente.

**Solucion (ASDD)**: la spec debe definir:
1. Que puede hacer el usuario (no solo que hace el codigo)
2. Como se demuestra que funciona (evidencia, no solo tests)
3. Que debe respetar (decisiones previas del Brain)
4. Review durante la implementacion (no al final)

### Como Cosmos + Harness previenen Frankensteins

| Problema Frankenstein | Prevencion |
|----------------------|-----------|
| Agente asume decisiones | Cosmos Brain (Files/Skills) registra decisiones — Expert consulta antes de actuar |
| Agente omite requisitos | Spec incluye "must_respect" — Approver Expert verifica contra spec |
| Agente agrega features no pedidas | Harness AI Evals valida output contra expected behavior |
| Tests pasan pero producto esta mal | ASDD: demostrar resultado (curl, screenshot, evidencia) |
| Decisiones se pierden | Cosmos Memory persiste + Harness Audit Trail registra |
| Un reviewer no encuentra todo | 4 Experts con modelos distintos (diversidad > redundancia) |

---

## Cosmos Experts: La Fabrica Completa

### Expert 1: Demo Reset (Cron)

```yaml
name: Demo Reset
trigger: cron (30 min antes de demo) OR Slack "/demo reset"
environment: ai-agentic-demo
capabilities: [GitHub, Slack]
model: Sonnet (tarea mecanica, no necesita Opus)

instructions: |
  1. Run scripts/demo-reset.sh --db --commit --push
  2. Validate STATE 0 invariants:
     - /api/ai/chat returns 404
     - Split flags ai_chat_enabled and ai_chat_backend are OFF
     - Database has exactly 3 seed accounts
  3. Post to Slack #demo-ops: "Demo ready. Commit: <sha>"
  4. If validation fails, post warning with details
```

### Expert 2: Code Builder (Act 1 Autopilot)

```yaml
name: Code Builder
trigger: Slack "/demo act1" OR webhook
environment: ai-agentic-demo
capabilities: [GitHub, Slack, Jira]
model: Opus (tarea de construccion compleja)

instructions: |
  1. Consulta Brain: lee docs/demo-prompts-consolidated.md, seccion 1.1
  2. Create Jira ticket in HD project
  3. Execute prompt 1.1 exactly as documented
  4. Self-check: run pytest, verify endpoint responds
  5. Push + create PR with Jira ID
  6. Post to Slack: PR URL, Jira ticket, files changed
```

### Expert 3: Pre-flight Check

```yaml
name: Pre-flight Check
trigger: Slack "/demo preflight" OR 15 min antes de demo
environment: ai-agentic-demo
capabilities: [GitHub, Slack, Web Access]
model: Sonnet (validacion, no construccion)

checks:
  - Split API connectivity + flag states
  - App health endpoint
  - MCP Financial Data service health
  - Harness secrets present
  - Pipeline last run status
  output: Slack checklist with PASS/FAIL per check
```

### Expert 4: Demo Assistant (Always-on)

```yaml
name: Demo Assistant
trigger: Slack (always listening in #demo-ops)
environment: ai-agentic-demo
capabilities: [GitHub, Slack, Jira, Web Access]
model: Sonnet (conversacional, rapido)

instructions: |
  You know the 7-act DemoBank flow.
  Commands: "que Act sigue?", "que fallo?", "prepara Act N", "status"
  Always respond in Spanish. Be concise. Include Harness UI links.
```

### Expert 5: Spec Writer (Factory mode)

```yaml
name: Spec Writer
trigger: GitHub issue labeled "factory" OR Slack "/factory <task>"
environment: ai-agentic-demo
capabilities: [GitHub, Slack]
model: Opus (razonamiento profundo para specs)

instructions: |
  1. Read the Brain (Files/Skills) for architecture decisions
  2. Write spec in ASDD format:
     - what_user_can_do, starting_conditions, expected_result
     - must_respect, how_to_demonstrate, evidence
  3. Post spec as GitHub issue comment for human review
  4. Wait for approval before triggering Builder
```

### Expert 6: Security Reviewer (Sub-reviewer)

```yaml
name: Security Reviewer
trigger: invoked by Approver Expert (not standalone)
environment: ai-agentic-demo
capabilities: [GitHub, Web Access]
model: different from Builder (diversidad de perspectiva)

instructions: |
  Review ONLY security aspects of the PR diff.
  Check: injection, auth bypass, secret exposure, dependency CVEs.
  Return structured findings with severity and evidence.
  Do NOT review code style or UX — other reviewers handle that.
```

---

## Risk Router: Quien Aprueba

```
  Cambio detectado
       │
       ▼
  ┌──────────────────────┐
  │  Cosmos Expert:       │
  │  Risk Classifier      │
  │                       │
  │  Evalua:              │
  │  - Archivos tocados   │
  │  - Backend vs frontend│
  │  - DB migrations?     │
  │  - Security findings? │
  │  - Lines of code      │
  └──────────┬────────────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
  LOW RISK        HIGH RISK
  (CSS, copy,     (backend, DB,
   docs)           auth, core)
     │               │
     ▼               ▼
  Auto-merge      Slack → humano
  via Harness     aprueba PR
  Pipeline        manualmente
     │               │
     └───────┬───────┘
             │
             ▼
  Harness Pipeline
  (SAST, SCA, AI Evals,
   canary deploy)
```

La clave: **Cosmos nunca bypasea Harness.** Los Experts crean PRs y tickets,
nunca deployean directo. Harness aplica las mismas politicas sin importar
si el PR vino de un humano o de un agente.

---

## Prompt para Cosmos Advisor

Copiar y pegar en el Advisor para configurar el Environment + Experts:

```
I need to set up an AI Software Factory for a demo environment
following the ASDD (Agent Spec Driven Development) methodology.

Project: DemoBank — a Flask banking app used to demonstrate
Harness CI/CD, security scanning, and AI agents.
Repo: github.com/crizstian/ai-agentic-demo (branch: secops/ai-agentic-demo)
Language: Python 3.12, Flask, SQLite

Environment name: ai-agentic-demo
Environment variables needed:
  HARNESS_API_KEY, SPLIT_SDK_KEY, GH_TOKEN,
  JIRA_API_KEY, JIRA_URL, JIRA_EMAIL

Integrations: GitHub, Slack, Jira

Create these Experts:

1. "Demo Reset" — cron trigger + Slack "/demo reset".
   Runs reset script, validates STATE 0, notifies Slack. Model: Sonnet.

2. "Code Builder" — Slack "/demo act1".
   Reads prompt card from docs, creates Jira, writes code,
   pushes, creates PR. Model: Opus.

3. "Pre-flight Check" — Slack "/demo preflight".
   Validates connectivity, flags, secrets, pipeline. Model: Sonnet.

4. "Demo Assistant" — always-on Slack listener.
   Helps presenter during live demos. Knows the 7-act flow.
   Responds in Spanish. Model: Sonnet.

5. "Spec Writer" — GitHub issue trigger (label: factory).
   Writes ASDD specs consulting Brain/Files. Model: Opus.

6. "Security Reviewer" — invoked as sub-reviewer.
   Reviews only security aspects with a different model for diversity.

Deploy all automations turned off — I'll arm after testing.
The Brain/Files should contain the project's CLAUDE.md and
docs/demo-prompts-consolidated.md as persistent context.
```

---

## Metricas de la Fabrica

| Metrica | Sin Factory | Con Factory (Cosmos + Harness) |
|---------|------------|-------------------------------|
| Tiempo de prep pre-demo | 15-30 min manual | 0 min (cron Expert) |
| Riesgo de fallo en vivo | Alto (MCP, flags, auth) | Bajo (pre-flight automatico) |
| Tiempo Act 1 en vivo | 3-5 min (Claude Code) | 2-3 min (Expert pre-calentado) |
| Diagnostico de fallos | Manual (logs, UI, kubectl) | 30s (Demo Assistant) |
| Recovery de estado corrupto | 5-10 min | 2 min (reset Expert) |
| Conocimiento del demo | En la cabeza del presenter | En el Brain (Files + Skills) |
| Frankensteins generados | Frecuente (tests no bastan) | Prevenido (ASDD + 4 reviewers) |
| Decisiones perdidas | Siempre | Nunca (Memory + Audit Trail) |
