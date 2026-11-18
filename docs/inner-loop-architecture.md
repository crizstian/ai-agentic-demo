# Inner Loop Agentico — Arquitectura Best-in-Class para Software Factory

> Diagrama de flujo completo para el loop cognitivo de una Software Factory autonoma.
> Sintetiza RSC Factory (metodologia), Cosmos (cloud), OpenRig (local),
> y lecciones de 25+ sesiones de DemoBank.

---

## Principios de Diseno

Antes del flujo, las 6 reglas que lo gobiernan:

| # | Principio | Anti-patron que evita |
|---|-----------|----------------------|
| 1 | **Spec antes de codigo** | Builder que inventa features no pedidas |
| 2 | **TDD estricto** | Codigo que "funciona" pero no cumple el spec |
| 3 | **Diversidad de modelos** | Auto-sesgo: Opus revisando su propio codigo |
| 4 | **Contexto limpio por revisor** | Reviewer contaminado por el razonamiento del Builder |
| 5 | **Fix loop con contexto** | Builder que pierde estado y re-inventa soluciones |
| 6 | **Demonstrate, don't just test** | El problema Frankenstein: 4500 tests pasan, app inutilizable |

### El problema Frankenstein (por que ASDD existe)

```
                    SIN ASDD                           CON ASDD
              ─────────────────                  ─────────────────
              12 specs, 8 horas                  Spec dice HOW_TO_DEMONSTRATE
              4500 tests pasan ✓                 Builder ejecuta demostracion
              App funciona? NO ✗                 Evidence: screenshots, curls
                                                 Approver verifica evidence
              "Cada spec era correcta            "No basta con pasar tests.
               individualmente, pero              El agente debe MOSTRAR
               juntas eran Frankenstein"           que el resultado funciona"
```

Cada GAP en la spec es una **decision que el Builder tomara solo — y la tomara mal**.
ASDD cierra esos gaps con `how_to_demonstrate` y `evidence`.

---

## Diagrama de Flujo Principal

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                        INNER LOOP — SOFTWARE FACTORY                       ║
║                          (Cognitivo, Pre-PR)                               ║
║                                                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║   ┌─────────────────────────────────────────┐                              ║
║   │           FUENTES DE ENTRADA            │                              ║
║   │                                         │                              ║
║   │  ┌──────────┐ ┌──────┐ ┌─────────────┐ │                              ║
║   │  │  GitHub   │ │Slack │ │  Sentry /    │ │                              ║
║   │  │  Issue    │ │ Msg  │ │  PagerDuty   │ │                              ║
║   │  └────┬─────┘ └──┬───┘ └──────┬───────┘ │                              ║
║   │       │          │             │         │                              ║
║   └───────┼──────────┼─────────────┼─────────┘                              ║
║           │          │             │                                        ║
║           └──────────┼─────────────┘                                        ║
║                      │                                                      ║
║                      ▼                                                      ║
║   ┌──────────────────────────────────────────────────┐                      ║
║   │                    BRAIN                          │                      ║
║   │  ┌──────────────┐ ┌────────────┐ ┌─────────────┐ │                      ║
║   │  │ decisions.md  │ │constraints │ │ patterns.md │ │                      ║
║   │  │ (que se       │ │.md (que NO │ │ (como SI    │ │                      ║
║   │  │  decidio)     │ │ hacer)     │ │  hacerlo)   │ │                      ║
║   │  └──────────────┘ └────────────┘ └─────────────┘ │                      ║
║   │  + specs previas + codigo fuente + memoria       │                      ║
║   └──────────────────────┬───────────────────────────┘                      ║
║                          │ lectura                                          ║
║                          │ (todos los agentes consultan Brain)              ║
║                          ▼                                                  ║
║  ╔═══════════════════════════════════════╗                                  ║
║  ║  FASE 1: ESPECIFICACION              ║                                  ║
║  ║  ─────────────────────────────────── ║                                  ║
║  ║                                       ║                                  ║
║  ║  ┌────────────────────────────────┐   ║                                  ║
║  ║  │       SPEC WRITER              │   ║                                  ║
║  ║  │       Modelo: Opus             │   ║                                  ║
║  ║  │       Acceso: Read-only        │   ║                                  ║
║  ║  │                                │   ║                                  ║
║  ║  │  1. Lee Brain completo         │   ║                                  ║
║  ║  │  2. Lee specs existentes       │   ║                                  ║
║  ║  │  3. Lee codigo relevante       │   ║                                  ║
║  ║  │  4. Genera spec ASDD (YAML):   │   ║                                  ║
║  ║  │     ├─ what_user_can_do        │   ║                                  ║
║  ║  │     ├─ expected_result         │   ║                                  ║
║  ║  │     ├─ must_respect            │   ║                                  ║
║  ║  │     ├─ how_to_demonstrate ←────│───║──── CLAVE: sin esto = Frankenstein║
║  ║  │     ├─ evidence                │   ║                                  ║
║  ║  │     └─ budget (max turns)      │   ║                                  ║
║  ║  │  5. Publica para aprobacion    │   ║                                  ║
║  ║  └──────────────┬─────────────────┘   ║                                  ║
║  ║                 │                     ║                                  ║
║  ╚═════════════════╪═════════════════════╝                                  ║
║                    │                                                        ║
║                    ▼                                                        ║
║          ┌─────────────────┐                                                ║
║          │  GATE HUMANO #1 │                                                ║
║          │  Spec Review    │                                                ║
║          │                 │                                                ║
║          │  ¿Spec correcta │                                                ║
║          │   y completa?   │                                                ║
║          └────────┬────────┘                                                ║
║              ┌────┴────┐                                                    ║
║              │         │                                                    ║
║             NO        SI                                                    ║
║              │         │                                                    ║
║              ▼         ▼                                                    ║
║         Spec Writer  (continua)                                             ║
║         (re-spec)                                                           ║
║                        │                                                    ║
║  ╔═════════════════════╪═════════════════════════════════════════╗           ║
║  ║  FASE 2: IMPLEMENTACION (TDD)                                ║           ║
║  ║  ──────────────────────────────                              ║           ║
║  ║                     │                                         ║           ║
║  ║                     ▼                                         ║           ║
║  ║  ┌────────────────────────────────────────────────────────┐   ║           ║
║  ║  │                  BUILDER                                │   ║           ║
║  ║  │                  Modelo: Opus                           │   ║           ║
║  ║  │                  Acceso: Read + Write                   │   ║           ║
║  ║  │                  Aislamiento: Worktree / Branch         │   ║           ║
║  ║  │                                                        │   ║           ║
║  ║  │  ┌──────────────────────────────────────────────────┐   │   ║           ║
║  ║  │  │ PREPARE                                          │   │   ║           ║
║  ║  │  │  1. Lee spec + Brain                            │   │   ║           ║
║  ║  │  │  2. Crea branch: factory/{spec-id}              │   │   ║           ║
║  ║  │  │  3. Crea ticket Jira                            │   │   ║           ║
║  ║  │  │  4. Analiza scope: archivos a tocar             │   │   ║           ║
║  ║  │  └─────────────────────┬────────────────────────────┘   │   ║           ║
║  ║  │                        │                                │   ║           ║
║  ║  │  ┌─────────────────────▼────────────────────────────┐   │   ║           ║
║  ║  │  │ TDD CYCLE (por cada sub-tarea)                   │   │   ║           ║
║  ║  │  │                                                  │   │   ║           ║
║  ║  │  │    Escribe test ──→ ROJO (falla) ──→ Escribe    │   │   ║           ║
║  ║  │  │                                       codigo    │   │   ║           ║
║  ║  │  │                                         │       │   │   ║           ║
║  ║  │  │                                         ▼       │   │   ║           ║
║  ║  │  │                                     VERDE ✓     │   │   ║           ║
║  ║  │  │                                     (pasa)      │   │   ║           ║
║  ║  │  └─────────────────────┬────────────────────────────┘   │   ║           ║
║  ║  │                        │                                │   ║           ║
║  ║  │  ┌─────────────────────▼────────────────────────────┐   │   ║           ║
║  ║  │  │ SELF-CHECK                                       │   │   ║           ║
║  ║  │  │  1. pytest tests/ -q (TODOS, no solo nuevos)    │   │   ║           ║
║  ║  │  │  2. Ejecuta how_to_demonstrate (del spec)       │   │   ║           ║
║  ║  │  │  3. Recolecta evidence (screenshots, curls)     │   │   ║           ║
║  ║  │  │  4. Verifica: ¿cumpli must_respect?             │   │   ║           ║
║  ║  │  └─────────────────────┬────────────────────────────┘   │   ║           ║
║  ║  │                        │                                │   ║           ║
║  ║  │  ┌─────────────────────▼────────────────────────────┐   │   ║           ║
║  ║  │  │ HANDOFF                                          │   │   ║           ║
║  ║  │  │  1. Commit + push a branch                      │   │   ║           ║
║  ║  │  │  2. Reporta: branch, ticket, tests, evidence    │   │   ║           ║
║  ║  │  │  3. NO crea PR (responsabilidad del Approver)   │   │   ║           ║
║  ║  │  └─────────────────────┬────────────────────────────┘   │   ║           ║
║  ║  └────────────────────────┼────────────────────────────────┘   ║           ║
║  ║                           │                                    ║           ║
║  ╚═══════════════════════════╪════════════════════════════════════╝           ║
║                              │                                               ║
║  ╔═══════════════════════════╪════════════════════════════════════╗           ║
║  ║  FASE 3: REVIEW PARALELO (modelos diversos, contexto limpio)  ║           ║
║  ║  ──────────────────────────────────────────────────────────── ║           ║
║  ║                           │                                    ║           ║
║  ║              ┌────────────┼────────────┐                       ║           ║
║  ║              │            │            │                       ║           ║
║  ║              ▼            ▼            ▼                       ║           ║
║  ║  ┌───────────────┐ ┌───────────┐ ┌───────────────┐            ║           ║
║  ║  │ SECURITY REV  │ │ CODE REV  │ │  UX/UI REV    │            ║           ║
║  ║  │               │ │           │ │  (v2)         │            ║           ║
║  ║  │ Modelo:       │ │ Modelo:   │ │               │            ║           ║
║  ║  │  Sonnet       │ │  Haiku    │ │ Modelo:       │            ║           ║
║  ║  │  (o Codex/Sol)│ │           │ │  Astra/Sol    │            ║           ║
║  ║  │               │ │           │ │               │            ║           ║
║  ║  │ Scope:        │ │ Scope:    │ │ Scope:        │            ║           ║
║  ║  │  Injection    │ │  Brain    │ │  Flujo UX     │            ║           ║
║  ║  │  Auth bypass  │ │  Patterns │ │  Visual UI    │            ║           ║
║  ║  │  Secrets      │ │  Scope    │ │  Responsive   │            ║           ║
║  ║  │  CVEs         │ │  Coverage │ │  Accesibilidad│            ║           ║
║  ║  │  Data leaks   │ │  Naming   │ │               │            ║           ║
║  ║  │               │ │  DRY      │ │               │            ║           ║
║  ║  │ Output: JSON  │ │ Output:   │ │ Output: JSON  │            ║           ║
║  ║  │  findings[]   │ │  JSON     │ │  findings[]   │            ║           ║
║  ║  │  + verdict    │ │  findings │ │  + screenshots│            ║           ║
║  ║  │               │ │  + verdict│ │  + verdict    │            ║           ║
║  ║  └───────┬───────┘ └─────┬─────┘ └──────┬────────┘            ║           ║
║  ║          │               │              │                      ║           ║
║  ║          └───────────────┼──────────────┘                      ║           ║
║  ║                          │                                     ║           ║
║  ╚══════════════════════════╪═════════════════════════════════════╝           ║
║                             │                                                ║
║                             │ findings consolidados                          ║
║                             │                                                ║
║  ╔══════════════════════════╪═════════════════════════════════════╗           ║
║  ║  FASE 4: APROBACION + RISK ROUTING                            ║           ║
║  ║  ──────────────────────────────────                           ║           ║
║  ║                          │                                     ║           ║
║  ║                          ▼                                     ║           ║
║  ║  ┌────────────────────────────────────────────────────────┐    ║           ║
║  ║  │                    APPROVER                             │    ║           ║
║  ║  │                    Modelo: Opus                         │    ║           ║
║  ║  │                    Acceso: Read + PR create             │    ║           ║
║  ║  │                                                        │    ║           ║
║  ║  │  1. Recolecta findings de TODOS los reviewers          │    ║           ║
║  ║  │  2. Deduplica (mismo file+line de distintos reviewers) │    ║           ║
║  ║  │  3. POR CADA finding:                                  │    ║           ║
║  ║  │     ├─ Lee el codigo real (no confiar en el reviewer)  │    ║           ║
║  ║  │     ├─ Clasifica:                                      │    ║           ║
║  ║  │     │   CONFIRMED    → debe arreglarse                 │    ║           ║
║  ║  │     │   FALSE_POSITIVE → descarta con razon            │    ║           ║
║  ║  │     │   INTENTIONAL  → spec.vulnerabilities_intended   │    ║           ║
║  ║  │     │   DEFERRED     → crea ticket Jira                │    ║           ║
║  ║  │     └─ Registra decision                               │    ║           ║
║  ║  │                                                        │    ║           ║
║  ║  │  4. Decision:                                          │    ║           ║
║  ║  └──────────────┬─────────────────────────────────────────┘    ║           ║
║  ║            ┌────┴────────────────────┐                         ║           ║
║  ║            │                         │                         ║           ║
║  ║    CONFIRMED > 0                CONFIRMED = 0                  ║           ║
║  ║            │                         │                         ║           ║
║  ║            ▼                         ▼                         ║           ║
║  ║   ┌────────────────┐     ┌─────────────────────┐              ║           ║
║  ║   │  FIX LOOP      │     │  RISK ROUTER        │              ║           ║
║  ║   │                │     │                     │              ║           ║
║  ║   │  Fix list →    │     │  Clasifica:         │              ║           ║
║  ║   │  Builder       │     │                     │              ║           ║
║  ║   │  (con contexto │     │  ┌───────────────┐  │              ║           ║
║  ║   │   preservado)  │     │  │   LOW RISK    │  │              ║           ║
║  ║   │                │     │  │  CSS, docs,   │  │              ║           ║
║  ║   │  Maximo:       │     │  │  tests, UI    │  │              ║           ║
║  ║   │  3 iteraciones │     │  │      │        │  │              ║           ║
║  ║   │  Luego:        │     │  │      ▼        │  │              ║           ║
║  ║   │  → humano      │     │  │  Auto-merge   │  │              ║           ║
║  ║   └───────┬────────┘     │  │  PR creada    │  │              ║           ║
║  ║           │              │  └───────────────┘  │              ║           ║
║  ║           │              │                     │              ║           ║
║  ║           │              │  ┌───────────────┐  │              ║           ║
║  ║           │              │  │  HIGH RISK    │  │              ║           ║
║  ║           ▼              │  │  Backend, DB, │  │              ║           ║
║  ║   (Regresa a FASE 2:    │  │  Auth, API,   │  │              ║           ║
║  ║    Builder con fix list) │  │  K8s, Core    │  │              ║           ║
║  ║                          │  │      │        │  │              ║           ║
║  ║                          │  │      ▼        │  │              ║           ║
║  ║                          │  │  PR creada    │  │              ║           ║
║  ║                          │  │  + Slack/     │  │              ║           ║
║  ║                          │  │  notif humano │  │              ║           ║
║  ║                          │  └───────────────┘  │              ║           ║
║  ║                          └──────────┬──────────┘              ║           ║
║  ║                                     │                         ║           ║
║  ╚═════════════════════════════════════╪═════════════════════════╝           ║
║                                        │                                     ║
║                                        │ PR creada                           ║
║                                        │                                     ║
╠════════════════════════════════════════╪═════════════════════════════════════╣
║                                        │                                     ║
║             HANDOFF AL OUTER LOOP      │                                     ║
║             ──────────────────────     │                                     ║
║                                        ▼                                     ║
║     ┌──────────────────────────────────────────────────────────┐             ║
║     │                OUTER LOOP (Harness)                       │             ║
║     │                                                          │             ║
║     │  PR ──→ Build ──→ Test ──→ SAST/SCA ──→ Deploy          │             ║
║     │         (Docker)  (pytest)  (Semgrep)    (Canary)        │             ║
║     │                                                          │             ║
║     │  Worker agents: code_reviewer, security_analyzer,        │             ║
║     │  qa_ui_analyzer, unit_test_gen, manifest_remediation     │             ║
║     │                                                          │             ║
║     │  ┌────────────────────────┐                              │             ║
║     │  │ Si pipeline FALLA:    │                              │             ║
║     │  │  → Worker arregla     │──→ fix sencillo (patch)      │             ║
║     │  │  → O feedback al      │──→ error complejo →          │             ║
║     │  │    inner loop         │     regresa a Builder        │             ║
║     │  └────────────────────────┘                              │             ║
║     └──────────────────────────────────────────────────────────┘             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Diagrama de Secuencia Detallado

```
  Humano   Spec Writer  Gate #1    Builder    Sec Rev   Code Rev   Approver   Harness
    │       (Opus)        │        (Opus)    (Sonnet)  (Haiku)    (Opus)     Pipeline
    │          │          │          │          │         │          │          │
    │ tarea    │          │          │          │         │          │          │
    ├─────────►│          │          │          │         │          │          │
    │          │          │          │          │         │          │          │
    │          │ lee Brain│          │          │         │          │          │
    │          │◄─────────│          │          │         │          │          │
    │          │          │          │          │         │          │          │
    │          │ spec ASDD│          │          │         │          │          │
    │          ├─────────►│          │          │         │          │          │
    │          │          │          │          │         │          │          │
    │  review  │          │          │          │         │          │          │
    │◄─────────┤──────────│          │          │         │          │          │
    │          │          │          │          │         │          │          │
    │ aprueba  │          │          │          │         │          │          │
    ├──────────┤─────────►│          │          │         │          │          │
    │          │          │          │          │         │          │          │
    │          │          │ spec     │          │         │          │          │
    │          │          ├─────────►│          │         │          │          │
    │          │          │          │          │         │          │          │
    │          │          │          │ branch   │         │          │          │
    │          │          │          │ TDD      │         │          │          │
    │          │          │          │ self-chk │         │          │          │
    │          │          │          │ push     │         │          │          │
    │          │          │          │          │         │          │          │
    │          │          │          │ diff ────┼────────►│          │          │
    │          │          │          │          │ diff    │          │          │
    │          │          │          │          ├────────►│          │          │
    │          │          │          │          │         │          │          │
    │          │          │          │          │ JSON ───┼─────────►│          │
    │          │          │          │          │         │ JSON ───►│          │
    │          │          │          │          │         │          │          │
    │          │          │          │          │         │          │ verifica │
    │          │          │          │          │         │          │ cada     │
    │          │          │          │          │         │          │ finding  │
    │          │          │          │          │         │          │          │
    │          │          │          │          │         │          │──── ¿CONFIRMED?
    │          │          │          │          │         │          │          │
    │          │          │          │ fix list │         │          │          │
    │          │          │          │◄─────────┤─────────┤──────────│ (si hay) │
    │          │          │          │          │         │          │          │
    │          │          │          │          │         │          │──── ¿0 CONFIRMED?
    │          │          │          │          │         │          │          │
    │          │          │          │          │         │          │ risk     │
    │          │          │          │          │         │          │ routing  │
    │          │          │          │          │         │          │          │
    │          │          │          │          │         │          │ PR ─────►│
    │          │          │          │          │         │          │          │
    │          │          │          │          │         │          │          │ build
    │          │          │          │          │         │          │          │ test
    │          │          │          │          │         │          │          │ scan
    │          │          │          │          │         │          │          │ deploy
    │          │          │          │          │         │          │          │
```

---

## Detalle de Cada Componente

### 1. Brain — Memoria Persistente

El Brain es el **sistema nervioso** de la factory. Sin el, cada agente
empieza de cero y repite errores ya resueltos.

```
Brain
├── decisions.md     ← QUE se decidio (y por que)
├── constraints.md   ← QUE NO hacer (hard limits + anti-patterns)
├── patterns.md      ← COMO hacerlo (codigo validado con razon)
├── specs/           ← especificaciones previas (contexto historico)
└── memoria          ← feedback, estado de proyecto, referencias
```

**Reglas del Brain:**
- TODOS los agentes lo leen ANTES de actuar
- Solo el Approver puede escribir nuevas decisiones (post-aprobacion)
- El Brain se versiona con git — cambios son rastreables
- El Brain NO contiene codigo — contiene REGLAS sobre codigo

**Diferencia con documentacion:**
- Docs son para humanos. Brain es para agentes.
- El Brain es prescriptivo ("usa lazy init para Split SDK").
  Docs son descriptivos ("Split SDK esta integrado via lazy init").

### 2. Spec Writer — Opus, Read-only

| Aspecto | Valor |
|---------|-------|
| Modelo | Opus (razonamiento complejo) |
| Acceso | Read-only (no escribe codigo) |
| Input | Tarea en lenguaje natural |
| Output | YAML ASDD con 5+ secciones obligatorias |
| Contexto | Brain + specs previas + codigo fuente |

**Formato ASDD obligatorio:**

```yaml
apiVersion: factory/v1
kind: Spec
metadata:
  id: SPEC-NNN
  title: "descripcion corta"
  risk: LOW | HIGH
  budget:
    max_agent_turns: 30

spec:
  what_user_can_do:
    - "Accion visible del usuario final"

  starting_conditions:
    - "Estado actual antes de implementar"

  expected_result:
    files_created: [...]
    files_modified: [...]
    api_response:
      endpoint: "GET /api/example"
      status: 200
      body_keys: ["key1", "key2"]

  must_respect:
    - "constraint #N: descripcion exacta del Brain"

  vulnerabilities_intended:            # solo si aplica
    - id: "VULN-001"
      type: "SQL Injection"
      scanner: "Semgrep"
      reason: "demo de security scanning"

  how_to_demonstrate:                  # ANTI-FRANKENSTEIN
    automated:
      - cmd: "curl -s http://localhost:5000/api/example"
        expect: '{"key1": "value"}'
      - cmd: "pytest tests/ -q"
        expect: "all tests pass"
    manual:
      - "Abrir browser en /example y verificar X"

  evidence:
    - "Screenshot de la UI"
    - "Output del curl"
    - "pytest results"
```

**Regla critica:** cada campo vacio en `must_respect` es un gap que el
Builder llenara con su propia interpretacion — y se equivocara.

### 3. Builder — Opus, Read+Write, Worktree

| Aspecto | Valor |
|---------|-------|
| Modelo | Opus (implementacion compleja) |
| Acceso | Read + Write (git, filesystem) |
| Aislamiento | Branch `factory/{spec-id}` o worktree |
| Input | Spec ASDD aprobada |
| Output | Branch con codigo, tests, evidence |
| Proceso | TDD: test primero → rojo → codigo → verde |

**5 fases del Builder:**

```
  PREPARE ──→ TDD ──→ SELF-CHECK ──→ DEMONSTRATE ──→ HANDOFF
     │          │          │              │               │
  Lee spec   Escribe    Ejecuta       Ejecuta          Commit
  Lee Brain  test       TODOS los    how_to_           Push
  Crea       (rojo)     tests        demonstrate       Reporta
  branch     Escribe    (no solo      del spec          "ready
  Crea       codigo     los nuevos)                     for
  ticket     (verde)                                    review"
```

**Restricciones:**
- NUNCA agrega features fuera del spec
- Si encuentra un gap en el spec → PARA y pregunta
- NO crea PR (eso lo hace el Approver)
- Maximo `budget.max_agent_turns` del spec
- NO modifica el Brain

### 4. Reviewers — Modelos Diversos, Contexto Limpio

**Por que modelos diversos:**
> "Opus se sesgaria revisando su propio codigo. Un modelo diferente
> trae una perspectiva fresca, sin los sesgos del razonamiento
> del Builder." — RSC Factory transcript

**Por que contexto limpio:**
> El reviewer NO ve el proceso de pensamiento del Builder. Solo ve
> el diff y el spec. Esto evita que "entienda" por que el Builder
> hizo algo mal y lo deje pasar.

| Reviewer | Modelo | Scope | Output |
|----------|--------|-------|--------|
| Security | Sonnet (o Codex/Sol) | Solo seguridad: injection, auth, secrets, CVEs | JSON findings[] con severity/file/line |
| Code | Haiku | Solo calidad: Brain consistency, patterns, scope, DRY | JSON findings[] con brain_reference |
| UX | Sol (v2) | Solo flujo usuario: pasos, coherencia, edge cases | JSON findings[] + flow diagram |
| UI | Astra (v2) | Solo visual: screenshots, alignment, responsive | JSON findings[] + screenshots |

**Reglas para reviewers:**
- NUNCA revisan fuera de su scope (Security no opina de naming)
- NUNCA modifican codigo (read-only)
- Siempre producen JSON estructurado (no texto libre)
- Cross-ref con `spec.vulnerabilities_intended` (no flaggear vulns intencionales)
- Verdict coherente: PASS si 0 findings, FAIL si >0

### 5. Approver — Opus, Gate Final

| Aspecto | Valor |
|---------|-------|
| Modelo | Opus (decision critica requiere razonamiento) |
| Acceso | Read + PR create |
| Input | Findings JSON de todos los reviewers |
| Output | APPROVED + PR, o REJECTED + fix list |

**Proceso del Approver:**

```
  Recolectar ──→ Deduplicar ──→ Verificar ──→ Decidir ──→ Routear
     │               │              │             │           │
  Findings de    Mismo file+      Lee codigo    ¿CONFIRMED   LOW → auto-PR
  TODOS los      line de          real para      findings     HIGH → PR +
  reviewers      distintos        cada finding   > 0?         notif humano
                 reviewers                        │
                                              SI → FIX LOOP
                                              (max 3 iteraciones)
```

**Clasificacion de findings:**

| Clasificacion | Significado | Accion |
|---------------|-------------|--------|
| CONFIRMED | Finding real, verificado contra codigo | Builder debe arreglar |
| FALSE_POSITIVE | Reviewer se equivoco | Descarta con razon documentada |
| INTENTIONAL | Spec dice que es intencional | Descarta con referencia a spec |
| DEFERRED | Real pero no urgente | Crea ticket Jira, no bloquea |

### 6. Risk Router — Clasificacion de Riesgo

```
                    ┌───────────────────────┐
                    │    RISK ROUTER        │
                    │                       │
                    │  Analiza:             │
                    │  - Archivos tocados   │
                    │  - Tipo de cambio     │
                    │  - Superficie de      │
                    │    ataque             │
                    │  - spec.risk          │
                    │                       │
                    └───────────┬───────────┘
                           ┌────┴────┐
                           │         │
                     ┌─────▼──┐  ┌───▼──────┐
                     │  LOW   │  │  HIGH    │
                     │  RISK  │  │  RISK    │
                     └────┬───┘  └────┬─────┘
                          │           │
                          ▼           ▼
                     Auto-merge   PR creada
                     PR creada    Notificacion
                     (sin gate    a humano via
                      humano)     Slack/email
                          │           │
                          │       ┌───▼────┐
                          │       │ GATE   │
                          │       │ HUMANO │
                          │       │ #2     │
                          │       └───┬────┘
                          │           │
                          └─────┬─────┘
                                │
                                ▼
                          OUTER LOOP
                          (Harness Pipeline)
```

**Criterios de clasificacion:**

| Categoria | LOW RISK | HIGH RISK |
|-----------|----------|-----------|
| Frontend | CSS, templates, static assets | — |
| Backend | — | API endpoints, business logic |
| Database | — | Schema, migrations, queries |
| Auth | — | Cualquier cambio de autenticacion |
| Config | .gitignore, README | K8s manifests, env vars, secrets |
| Tests | Nuevos tests | Modificar test helpers/fixtures |
| Docs | Cualquier documentacion | — |

---

## Ejecucion Paralela de Tareas

Una factory best-in-class no procesa una tarea a la vez.
Multiples tareas corren en paralelo, cada una en su branch aislada:

```
  Tarea A ──→ Spec Writer A ──→ Builder A ──→ Reviewers A ──→ Approver A ──→ PR A
  Tarea B ──→ Spec Writer B ──→ Builder B ──→ Reviewers B ──→ Approver B ──→ PR B
  Tarea C ──→ Spec Writer C ──→ Builder C ──→ Reviewers C ──→ Approver C ──→ PR C
                                    │
                                    │ (todas en branches separadas,
                                    │  sin conflictos entre si)
```

**Prerequisitos para paralelismo:**
- Aislamiento de branches (worktree o branch por tarea)
- Brain compartido pero read-only durante implementacion
- Reviewers stateless (contexto limpio = naturalmente paralelizable)
- Approver puede procesar PRs independientemente

**Limites:**
- El Brain se actualiza DESPUES de aprobar (no durante build)
- Si dos tareas tocan el mismo archivo → merge conflict en PR
  → el segundo Approver detecta y re-routea al Builder

---

## Fix Loop — Detalle

El fix loop es critico para quality sin intervencion humana.

```
                    Builder
                       │
                       ▼
                   Reviewers ──→ findings
                       │
                       ▼
                   Approver
                       │
              ┌────────┴────────┐
              │                 │
          CONFIRMED          APPROVED
              │                 │
              │                 ▼
              │             (sale del loop)
              │
              ▼
  ┌─────────────────────┐
  │    FIX ITERATION    │
  │                     │
  │  Builder recibe:    │
  │  - Fix list         │
  │  - CONFIRMED        │
  │    findings con     │
  │    file:line        │
  │                     │
  │  Builder DEBE:      │
  │  - Mantener         │
  │    contexto         │◄──── CRITICO: el Builder debe recordar
  │    (no re-analizar  │      lo que ya hizo. Sin persistencia,
  │     desde cero)     │      re-inventa soluciones.
  │  - Solo arreglar    │
  │    los CONFIRMED    │
  │  - Re-ejecutar      │
  │    self-check       │
  │  - Push al mismo    │
  │    branch           │
  └──────────┬──────────┘
             │
             ▼
         Reviewers ──→ nueva ronda de findings
             │
             ▼
         Approver
             │
      ┌──────┴──────┐
      │              │
  CONFIRMED       APPROVED
  (iteracion 2)      │
      │              ▼
      │          (sale del loop)
      │
      ▼
  ¿Iteracion > 3?
      │
  ┌───┴───┐
  │       │
  NO     SI
  │       │
  ▼       ▼
 Fix    ESCALATE
 Loop   → Gate humano
        (el agente no puede resolver)
```

**Maximo 3 iteraciones automaticas.** Despues → humano. Esto evita:
- Loops infinitos de fix→review→fix
- Builder degradando el codigo intentando satisfacer findings conflictivos
- Consumo de tokens sin convergencia

---

## Implementacion por Plataforma

### Cosmos (Augment Code)

```
Platform: Cloud VMs efimeras
Experts: 5 (Spec Writer, Builder, Security Rev, Code Rev, Approver)
Handoff: Manual (copy/paste entre sesiones) o Workers (Expert→Expert)
Triggers: GitHub issue, Slack mention, webhook, cron
Brain: Files en Environment + repo .claude/brain/

Ventajas:
  + Cloud auto-scale (multiples tareas paralelas)
  + Triggers nativos (GitHub, Slack, PagerDuty)
  + Audit trail (sesiones grabadas)
  + Aislamiento de seguridad (cada Expert en su VM)

Limitaciones:
  - VM efimera (Builder pierde contexto entre sesiones → fix loop debil)
  - Solo modelos Augment (no Codex/Sol/Astra para reviewers)
  - Handoff manual entre Experts (sin evento "Expert termino")
  - Overhead de VM por cada invocacion de reviewer/worker
```

### Claude Code + OpenRig (Local)

```
Platform: tmux sessions locales
Agents: 5+ (mismos roles, agentes persistentes)
Handoff: rig send / rig queue (comunicacion directa agente→agente)
Triggers: Manual o scripts
Brain: .claude/brain/ (filesystem local)

Ventajas:
  + Agentes persistentes (Builder mantiene contexto → fix loop fuerte)
  + Cross-harness (Claude + Codex + cualquier modelo)
  + Comunicacion directa (rig send, sin overhead de VM)
  + Open-source, sin vendor lock-in

Limitaciones:
  - Limitado al hardware local (no auto-scale)
  - Sin triggers nativos (GitHub/Slack requieren scripts custom)
  - Sin audit trail empresarial
  - Filesystem compartido (sin aislamiento de seguridad nativo)
```

### Hibrido (Best-in-Class)

```
Brain layer:     .claude/brain/ (versionado en git, compartido)
Spec layer:      Cosmos Expert o Claude Code local (Opus)
Build layer:     Claude Code local con worktree (persistencia + TDD)
Review layer:    OpenRig cross-harness (Codex/Sol para security, Haiku para code)
Approve layer:   Cosmos Expert (audit trail + Slack notifications)
Execute layer:   Harness Pipeline (deterministic, never bypassed)
```

---

## Metricas de la Factory

Para medir si el inner loop funciona:

| Metrica | Target | Que indica |
|---------|--------|-----------|
| Spec-to-PR time | < 30 min (LOW), < 2h (HIGH) | Velocidad del loop |
| Fix loop iterations | < 2 promedio | Calidad del Builder |
| False positive rate | < 20% | Precision de reviewers |
| Frankenstein rate | 0% | Efectividad de ASDD |
| Pipeline fail post-inner-loop | < 10% | Inner loop atrapa lo que debe |
| Human intervention rate | < 30% (LOW RISK = 0%) | Nivel de autonomia |
| Brain update frequency | 1 decision/semana | El sistema aprende |

---

## Anti-Patrones a Evitar

| Anti-patron | Consecuencia | Solucion |
|-------------|-------------|----------|
| Spec vaga ("agregar feature X") | Builder inventa detalles | ASDD con how_to_demonstrate |
| Builder sin worktree | Contamina main branch | Branch `factory/{spec-id}` |
| Mismo modelo para builder y reviewer | Auto-sesgo, falsos PASS | Diversidad: Opus/Sonnet/Haiku |
| Reviewer con contexto del Builder | "Entiendo por que lo hiciste" → deja pasar | Contexto limpio por reviewer |
| Fix loop sin limite | Loop infinito, tokens desperdiciados | Max 3 iteraciones → escalate |
| Approver rubber-stamp | Findings no verificados pasan | Leer codigo real por cada finding |
| Auto-merge de HIGH RISK | Cambios criticos sin revision humana | Risk router + gate humano |
| Brain desactualizado | Agentes repiten errores resueltos | Approver actualiza post-approval |
| Tests sin demostracion | Frankenstein: tests pasan, app rota | ASDD: how_to_demonstrate + evidence |
| Reviewers sin scope | Todos opinan de todo, ruido | Scope estricto por reviewer |

---

## Relacion Inner Loop ↔ Outer Loop

```
  INNER LOOP                           OUTER LOOP
  (Cognitivo, Pre-PR)                  (Determinista, Post-PR)
  ────────────────────                 ────────────────────────

  Agentes RAZONAN                      Tools EJECUTAN
  (puede equivocarse)                  (deterministico)

  Previene errores                     Detecta errores
  (proactivo)                          (reactivo)

  Output: PR lista                     Input: PR
  Input: tarea humana                  Output: deploy o fail

  Modelos: Opus, Sonnet, Haiku         Scanners: Semgrep, OWASP, SCS
  (diversos, cognitivos)               (deterministicos, sin opinion)

  Brain: decisions, constraints        Policies: OPA, quality gates
  (flexible, contextual)               (rigido, binario)

  Fix loop: Builder↔Approver           Fix loop: Worker agents
  (razonamiento)                       (patch mecanico)

  ┌─────────────────────────────────────────────────────────┐
  │ NO ES REDUNDANCIA — ES DEFENSA EN PROFUNDIDAD          │
  │                                                         │
  │ Inner loop: "este endpoint no valida input"            │
  │ Outer loop: "CVE-2023-32681 en requests==2.28.0"       │
  │                                                         │
  │ Ambos necesarios. Ninguno suficiente solo.              │
  └─────────────────────────────────────────────────────────┘
```
