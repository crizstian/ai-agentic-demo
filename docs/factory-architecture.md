# AI Software Factory — Arquitectura de 3 Sistemas

> Tres sistemas, dos loops, un Brain compartido.

---

## Los 3 Sistemas

| Sistema | Rol | Que aporta |
|---------|-----|-----------|
| **RSC Factory (metodologia)** | El proceso | Define QUE pasos seguir, en que orden, con que criterios |
| **Cosmos** | Los trabajadores | Ejecuta los pasos cognitivos (spec, code, review, approve) |
| **Harness** | La linea de ensamble | Ejecuta los pasos deterministas (build, test, scan, deploy) |

La metodologia RSC Factory (del transcript) define el flujo completo.
Cosmos y Harness se REPARTEN la ejecucion de ese flujo.
Ningun sistema lo cubre todo solo.

---

## Inner Loop vs Outer Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INNER LOOP (Cosmos)                         │
│                                                                     │
│  Trabajo COGNITIVO — agentes razonan, deciden, crean                │
│                                                                     │
│  Input ──→ Spec Writer ──→ Builder ──→ Reviewers ──→ Approver      │
│              (Opus)         (Opus)    (modelos       (Opus)         │
│                                       diversos)                     │
│                               ▲            │                        │
│                               └── fix ─────┘                        │
│                                                                     │
│  Output: PR lista para pipeline                                     │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                                     │ PR merge / push
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       OUTER LOOP (Harness)                          │
│                                                                     │
│  Trabajo DETERMINISTA — tools ejecutan, miden, despliegan           │
│                                                                     │
│  PR ──→ Build ──→ Test ──→ SAST/SCA ──→ AI Evals ──→ Deploy       │
│          (Docker)  (pytest)  (Semgrep,    (LLM         (Canary,     │
│                              OWASP)       validation)   Rolling)    │
│                                                                     │
│  Worker Agents: code_reviewer, security_analyzer, qa_ui_analyzer,  │
│                 ca_code_unit_test_generator, ca_manifest_remediation│
│                                                                     │
│  Output: Codigo en produccion (o feedback al inner loop)            │
└────────────────────────────────────┬────────────────────────────────┘
                                     │
                                     │ pipeline fail / incident
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FEEDBACK LOOP (Cosmos → Harness)                │
│                                                                     │
│  Pipeline falla ──→ Cosmos Expert "Fixer" ──→ PR con fix ──→ ...   │
│  Incidente prod ──→ Harness AI SRE ──→ Runbook auto ──→ resolved   │
└─────────────────────────────────────────────────────────────────────┘
```

### Por que dos loops?

El transcript lo explica claro: **"pasar los tests no es suficiente"**.

- El **inner loop** (Cosmos) se asegura de que el codigo tiene SENTIDO
  para el usuario. Specs verificables, review durante implementacion,
  evidencia de que funciona. Previene Frankensteins.

- El **outer loop** (Harness) se asegura de que el codigo es SEGURO y
  DESPLEGABLE. Scanners reales (no agentes opinando), quality gates
  con OPA policies, deploy con canary y rollback.

Un agente puede decir "no hay vulnerabilidades" y estar equivocado.
Un scanner SAST encuentra lo que el agente no vio.
Un agente puede decir "funciona" pero el deploy falla.
El pipeline lo demuestra con tests reales en container.

---

## Mapeo Detallado: Transcript → Cosmos → Harness

### Paso 1: Inputs (Entradas)

| Transcript dice | Cosmos hace | Harness hace |
|----------------|-------------|--------------|
| "Entran errores de Sentry, issues de GitHub, tareas de Slack" | **Triggers**: GitHub issue (label:factory), Slack command, webhook de Sentry/PagerDuty | **Triggers**: PR event, webhook, cron. NO recibe tareas cognitivas |

**Conclusion**: los inputs cognitivos ("haz esto") van a Cosmos.
Los inputs mecanicos ("PR lista, ejecuta pipeline") van a Harness.

### Paso 2: Brain (Contexto Persistente)

| Transcript dice | Cosmos hace | Harness hace |
|----------------|-------------|--------------|
| "Si la fabrica se olvida del contexto, cada tarea empieza de cero" | **Files**: Brain Bundle subido al Environment. **Skills**: patrones empaquetados. **Memory**: decisiones cross-session | **Audit Trail**: historial de ejecuciones. OPA policies: reglas codificadas |
| "Cada decision se registra en el brain" | Los Experts actualizan Files despues de cada spec/build/review | Worker agents no actualizan el brain (son efimeros) |

**Conclusion**: el Brain vive en Cosmos (Files + Memory).
Harness tiene un "brain pasivo" (audit trail, policies) pero no lo consulta activamente.
`.claude/brain/` es el bridge — consumible por ambos mundos.

### Paso 3: Spec Writer (Inner Loop — Cosmos)

| Transcript dice | Cosmos Expert |
|----------------|---------------|
| "Opus recibe la tarea y escribe una spec" | Expert "Spec Writer" (Opus) |
| "Antes de escribir, consulta el brain" | Lee Cosmos Files (brain-bundle) + repo (brain/) |
| "ASDD: que puede hacer el usuario, resultado esperado, que respetar, como demostrar" | Genera YAML en docs/specs/ con formato ASDD |

**Harness equivalente**: ninguno. Harness no escribe specs.

### Paso 4: Builder (Inner Loop — Cosmos)

| Transcript dice | Cosmos Expert |
|----------------|---------------|
| "Opus programa, crea rama, TDD" | Expert "Builder" (Opus) |
| "Consulta brain para arquitectura" | Lee brain/ + patterns.md |
| "Primero test, no pasa, luego codigo hasta que pasa" | TDD cycle en el Environment |

**Harness equivalente**: ninguno directamente. Pero Harness tiene worker agents
que TAMBIEN escriben codigo (security_analyzer, ca_manifest_remediation_v2).
La diferencia: los workers de Harness operan DENTRO del pipeline sobre un PR
existente. El Builder de Cosmos opera ANTES del pipeline para CREAR el PR.

### Paso 5: Reviewers (SPLIT entre Inner y Outer Loop)

Aqui esta la clave de la arquitectura. Los 4 reviewers del transcript
se REPARTEN entre Cosmos y Harness segun su naturaleza:

| Reviewer | Inner Loop (Cosmos) | Outer Loop (Harness) |
|----------|-------------------|---------------------|
| **Security** | Expert pre-PR: revisa diff con razonamiento, busca patrones de ataque, valida contra spec | STO post-PR: Semgrep (SAST), OWASP Dep Check (SCA), Traceable (API). Scanners reales, no opiniones |
| **Code** | Expert pre-PR: valida consistencia con Brain, patrones, arquitectura | Worker agent `code_reviewer`: revisa PR con contexto de repo. Unit test generator: `ca_code_unit_test_generator` |
| **UI** | Expert pre-PR: verifica visual contra spec (screenshot, computer use) | Worker agent `qa_ui_analyzer`: valida CSS, alignment, responsive |
| **UX** | Expert pre-PR: valida flujo de usuario, pasos, coherencia | Harness AI Evals: valida output del LLM contra expected behavior |

**Conclusion**: NO es redundancia, es **defensa en profundidad**.

```
  Inner Loop (Cosmos)              Outer Loop (Harness)
  ──────────────────              ─────────────────────
  Reviewer opina                   Scanner DETECTA
  (puede equivocarse)              (deterministico)

  Pre-PR                           Post-PR
  (antes de crear PR)              (dentro del pipeline)

  Razonamiento sobre intent        Ejecucion sobre codigo
  ("esto viola la spec")           ("CVE-2023-32681 en requests")

  Feedback al Builder              Feedback al Worker Agent
  (fix loop interno)               (security_analyzer remedia)
```

### Paso 6: Approver (Inner Loop — Cosmos)

| Transcript dice | Cosmos Expert |
|----------------|---------------|
| "Recibe feedback de los 4 reviewers, consolida" | Expert "Approver" (Opus) |
| "Deduplica, decide fix o ship" | Verifica findings contra codigo real |
| "Si negativo, vuelve al builder" | Fix loop: Builder → Reviewers → Approver |

**Harness equivalente**: OPA policies + quality gates. Pero son deterministicos
("si coverage < 80% → block"), no razonan sobre el contexto.

### Paso 7: Risk Router (SPLIT)

| Transcript dice | Cosmos hace | Harness hace |
|----------------|-------------|--------------|
| "Si es trivial, auto-merge" | Approver clasifica riesgo y auto-aprueba PR | Pipeline ejecuta sin gate humano |
| "Si es core, humano aprueba" | Notifica via Slack con resumen completo | Pipeline pausa en approval stage |
| "Hooks para bloquear" | — | OPA policy: `deny` si files criticos sin approval |

**Conclusion**: el Risk Router es hibrido.
Cosmos decide el NIVEL de riesgo (cognitivo).
Harness APLICA la restriccion (deterministico, con OPA).

### Paso 8: Pipeline (Outer Loop — Harness)

| Transcript dice | Harness hace | Cosmos hace |
|----------------|-------------|-------------|
| "Llevarlo a produccion" | Build → Test → SAST → SCA → AI Evals → Deploy | Nada. Cosmos nunca deploya |
| Worker agents remediando | security_analyzer, ca_manifest_remediation_v2 | — |
| Canary → rolling | CD stage con Kubernetes | — |

**Conclusion**: el pipeline es 100% Harness. Cosmos nunca bypasea Harness.

### Paso 9: Feedback Loop (Outer → Inner)

| Evento | Quien responde | Que hace |
|--------|---------------|---------|
| Pipeline falla (test, SAST) | Harness worker agents (security_analyzer, etc.) | Remedian dentro del pipeline, crean PR con fixes |
| Pipeline falla (deploy, config) | Harness worker agent (ca_manifest_remediation_v2) | Arregla manifests, crea PR |
| Incidente en produccion | Harness AI SRE | Ejecuta runbook automatico (12s, 6 acciones) |
| Error recurrente / pattern nuevo | Cosmos Expert "Fixer" | Analiza root cause, actualiza Brain, crea spec para fix permanente |

---

## Que NO se solapa

| Capacidad | Solo Cosmos | Solo Harness |
|-----------|------------|-------------|
| Escribir specs ASDD | ✓ | — |
| TDD en worktree | ✓ | — |
| Review con modelos diversos | ✓ | — |
| Brain persistente consultable | ✓ | — |
| Risk classification cognitiva | ✓ | — |
| SAST/SCA scanning real | — | ✓ |
| OPA policy enforcement | — | ✓ |
| Container build + registry | — | ✓ |
| Canary deploy + rollback | — | ✓ |
| SLSA provenance + attestation | — | ✓ |
| AI Evals (LLM output validation) | — | ✓ |
| Supply chain security (SCS) | — | ✓ |

---

## Experts de Cosmos — Definicion Final

Basado en el mapeo anterior, estos son los Experts que pertenecen al
inner loop de Cosmos. NO incluye capabilities que Harness ya cubre.

### Expert 1: Spec Writer

```
Rol: Primer paso del factory. Recibe input, consulta Brain, escribe spec ASDD.
Modelo: Opus
Trigger: GitHub issue (label:factory), Slack, webhook
Loop: Inner (cognitivo)

Flujo:
1. Recibe tarea (issue, error, request)
2. Lee Brain (Cosmos Files + .claude/brain/)
3. Lee specs existentes (docs/specs/) para no contradecir
4. Lee codigo fuente relevante
5. Escribe spec ASDD con las 5 secciones obligatorias:
   - what_user_can_do (acciones del usuario, no implementacion)
   - expected_result (verificable: status codes, JSON keys, UI states)
   - must_respect (constraints del Brain que aplican)
   - how_to_demonstrate (comandos exactos para probar)
   - evidence (artefactos que deben existir post-implementacion)
6. Publica spec en Slack para revision humana
7. Espera aprobacion antes de pasar al Builder

Clave: cada gap en la spec es una decision que el Builder tomara solo
— y la tomara mal. Exhaustividad en must_respect previene Frankensteins.
```

### Expert 2: Builder

```
Rol: Implementa spec aprobada usando TDD. Crea branch, tests primero, codigo despues.
Modelo: Opus
Trigger: Automation post-Spec Writer aprobado, o Slack "/factory build {spec-id}"
Loop: Inner (cognitivo)

Flujo:
1. Lee spec (docs/specs/{id}.yaml) + Brain
2. Crea branch factory/{spec-id}
3. Crea Jira ticket (project HD, type Task)
4. Por cada sub-tarea de la spec:
   a. Escribe test basado en expected_result → debe FALLAR
   b. Escribe codigo minimo para pasar el test
   c. Verifica que pasa
5. Self-check: ejecuta TODOS los tests + how_to_demonstrate
6. Recolecta evidence
7. Commit + push + notifica Slack
8. Pasa a fase de review

Restricciones:
- NUNCA agrega funcionalidad fuera de la spec
- NUNCA modifica archivos fuera del scope
- Si encuentra gap en spec → PARA y pregunta via Slack
- Budget: max_agent_turns de la spec (default 30)
```

### Expert 3: Security Reviewer

```
Rol: Reviewer independiente. Solo seguridad. Contexto limpio. Modelo diferente al Builder.
Modelo: Sonnet (diversidad de perspectiva vs Opus del Builder)
Trigger: Automation post-Builder
Loop: Inner (pre-PR review)

Scope: SOLO seguridad. No code style, no UX, no UI.
Complementa (no reemplaza) Harness STO que corre en el outer loop.

Checks: injection, auth bypass, secrets, dependency CVEs, data leaks.
Cross-ref con spec.vulnerabilities_intended (no flaggear vulns intencionales).
Output: findings estructurados con severity/file/line/evidence/fix.
Verdict: PASS o FAIL.
```

### Expert 4: Code Reviewer

```
Rol: Reviewer independiente. Solo consistencia de codigo con Brain. Contexto limpio.
Modelo: Haiku (tarea menos compleja, modelo ligero)
Trigger: Automation post-Builder
Loop: Inner (pre-PR review)

Scope: SOLO code quality y consistencia arquitectural.
Complementa Harness worker agent code_reviewer que corre en el outer loop.

Checks: patrones del Brain, decisiones respetadas, duplicacion, naming, test coverage.
Output: findings con category/file/line/brain_reference/fix.
Verdict: PASS o FAIL.
```

### Expert 5: Approver

```
Rol: Decision final del inner loop. Consolida reviewers, decide fix loop o approve.
Modelo: Opus (decision critica)
Trigger: Automation cuando todos los reviewers terminan
Loop: Inner (gate cognitivo)

Flujo:
1. Recolecta findings de todos los reviewers
2. Deduplica y ordena por severidad
3. Verifica cada finding contra codigo real (false positive check)
4. Decide por finding: CONFIRMED → fix, FALSE_POSITIVE → descarta, DEFERRED → Jira
5. Si hay CONFIRMED: devuelve al Builder (fix loop)
6. Si cero CONFIRMED: clasifica riesgo y routea:
   - LOW RISK (frontend, docs, tests) → auto-merge PR
   - HIGH RISK (backend, DB, auth, core) → Slack al humano

Despues de aprobar:
- Registra decisiones en Brain
- Output: PR lista para el outer loop (Harness pipeline)
```

### Reviewers FUTUROS (no en v1)

```
UX Reviewer: valida flujo de usuario contra spec. Modelo diferente.
UI Reviewer: valida visual con computer use. Modelo tipo Astra.
Estos se agregan cuando los primeros 5 esten validados.
```

---

## Harness Worker Agents — Outer Loop (ya existentes)

Estos ya estan configurados en .harness/agents/ y corren DENTRO del pipeline:

| Agent | Rol en Outer Loop | Trigger |
|-------|------------------|---------|
| `code_reviewer` | Review de PR post-merge request | PR event en pipeline |
| `security_analyzer` | Remedia findings SAST/SCA (hasta 4 CRITICAL/HIGH) | Post SAST/SCA scan |
| `ca_code_unit_test_generator` | Genera tests faltantes que code_reviewer flaggeo | Post code review |
| `qa_ui_analyzer` | Valida CSS, alignment, responsive | Post build |
| `ca_manifest_remediation_v2` | Arregla manifests K8s (configmap, env vars) | Deploy fail |

Estos agents NO necesitan migrar a Cosmos. Son parte del pipeline
determinista de Harness y su contexto es la PR + findings del scanner.

---

## Flujo Completo End-to-End

```
  HUMANO                    INNER LOOP (Cosmos)                 OUTER LOOP (Harness)
  ──────                    ───────────────────                 ────────────────────

  "Agrega feature X"
       │
       ▼
  [Slack / GitHub issue]
       │
       ▼
  ┌─────────────┐
  │ Spec Writer  │──── consulta Brain
  │ (Opus)       │──── lee specs previas
  └──────┬───────┘     lee codigo
         │
         ▼
  [Spec ASDD en Slack]
       │
  HUMANO aprueba ←──────┐
       │                 │ (o modifica)
       ▼                 │
  ┌─────────────┐        │
  │ Builder      │──── consulta Brain
  │ (Opus, TDD)  │──── crea branch
  └──────┬───────┘     commit + push
         │
         ├──────────────────────┐
         ▼                      ▼
  ┌──────────────┐    ┌──────────────┐
  │ Security Rev  │    │ Code Rev      │
  │ (Sonnet)      │    │ (Haiku)       │
  └──────┬────────┘    └──────┬────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
            ┌──────────────┐
            │ Approver      │
            │ (Opus)        │
            └──────┬────────┘
                   │
          ┌────────┴────────┐
          │                 │
     CONFIRMED          APPROVED
          │                 │
          ▼                 ├── LOW RISK ──→ auto-merge PR
     Builder              │
     (fix loop)            └── HIGH RISK ──→ Slack a HUMANO
                                    │
                               HUMANO aprueba
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ Harness Pipeline  │
                           ├─────────────────┤
                           │ Build (Docker)    │
                           │ Test (pytest)     │
                           │ SAST (Semgrep)    │
                           │ SCA (OWASP)       │
                           │ AI Evals          │
                           │ code_reviewer     │◄── Worker agents
                           │ security_analyzer │◄── del outer loop
                           │ qa_ui_analyzer    │◄──
                           ├─────────────────┤
                           │ Deploy (Canary)   │
                           │ Verify (CV)       │
                           │ Promote (Rolling) │
                           └────────┬──────────┘
                                    │
                               ┌────┴────┐
                               │         │
                            SUCCESS    FAIL
                               │         │
                               ▼         ▼
                          Produccion  ┌────────────┐
                                      │ Worker agent│ (outer loop fix)
                                      │ O           │
                                      │ Cosmos Fixer│ (inner loop fix
                                      │             │  si es root cause)
                                      └─────────────┘
```

---

## Decisiones de Arquitectura

| # | Decision | Razon |
|---|----------|-------|
| 1 | Inner loop en Cosmos, outer loop en Harness | Cosmos razona (cognitivo). Harness ejecuta (deterministico). No se solapan. |
| 2 | Reviewers pre-PR (Cosmos) + scanners post-PR (Harness) | Defensa en profundidad. El reviewer opina, el scanner detecta. Ambos necesarios. |
| 3 | Worker agents quedan en Harness, no migran a Cosmos | Son efimeros, corren en container dentro del pipeline. Su contexto es la PR + findings. |
| 4 | Brain vive en Cosmos Files, bridge via .claude/brain/ | Cosmos Experts consultan Files. Claude Code local consulta .claude/brain/. Mismo contenido, dos puntos de acceso. |
| 5 | Approver hace risk routing, Harness aplica con OPA | Separacion: decision cognitiva (Cosmos) vs enforcement deterministico (Harness). |
| 6 | Cosmos nunca deploya | Los Experts crean PRs y tickets. Harness aplica las mismas policies sin importar si el PR vino de humano o agente. |
| 7 | Modelos diversos en reviewers | Transcript: "el modelo Opus se sesgaria de utilizarse a si mismo para revisar". Security=Sonnet, Code=Haiku, Builder=Opus. |
| 8 | Fix loop dentro del inner loop | Si un reviewer encuentra issue, el Builder arregla ANTES de crear PR. El pipeline no deberia encontrar errores que el inner loop pudo prevenir. |
| 9 | Feedback loop outer→inner para root cause | Worker agents arreglan sintomas (patch CVE, fix manifest). Cosmos Expert "Fixer" analiza causas raiz y actualiza Brain. |
| 10 | v1 con 5 Experts, UX/UI reviewers en v2 | Validar el flujo core primero. Agregar reviewers especializados cuando el loop basico funcione. |
