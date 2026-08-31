# ACTO 2: "Software Delivery Agent — Gobernar Cada Cambio"

## Qué hace el acto

El PR del Acto 1 dispara automáticamente el pipeline de PR Validation en Harness. El Software Delivery Agent toma el control: ejecuta CI (build + tests), aplica Test Intelligence para correr solo los tests relevantes, y el Change Advisor — un Expert Agent — analiza el PR y posta un review estructurado en GitHub. La audiencia ve cómo Harness gobierna cada cambio desde el PR, sin intervención manual.

---

## Por qué este contexto narrativo

**1. Contraste con el Acto 1.** El Acto 1 mostró velocidad — código en minutos. El Acto 2 muestra gobierno — ese código no va a ningún lado sin pasar por Harness. El contraste refuerza: "velocidad sin gobierno es riesgo."

**2. El handoff es automático.** No hubo que configurar nada, no hubo que trigger nada. El PR se creó y el pipeline ya estaba corriendo. Esto demuestra que la plataforma está siempre activa — no es un paso manual que el developer puede saltarse.

**3. Introduce a los Expert Agents.** El Change Advisor es el primer Expert Agent que la audiencia ve. No es un linter, no es un bot de CI que dice pass/fail — es un agent que razona sobre el cambio, evalúa riesgo, identifica dependencias nuevas, y genera un review estructurado. Esto prepara a la audiencia para aceptar agents más complejos en los actos siguientes (Triage Agent, Remediation Agent, Runtime Protection Agent).

---

## Qué le ofrece a la audiencia

| Audiencia | Lo que se llevan | Wiring técnico |
|-----------|-----------------|----------------|
| **Developer** | "No tuve que hacer nada. El PR se creó y el pipeline ya estaba validando. Test Intelligence solo corrió los tests que importan — no esperé 20 min por toda la suite." | PR trigger automático + Test Intelligence = feedback loop rápido. |
| **DevOps / Platform** | "Cada cambio está gobernado. No importa si vino de un coding agent o de un developer — pasa por el mismo pipeline, las mismas policies, el mismo audit trail." | Governed Orchestration Engine: policies, gates, audit trail aplican a todo source de código. |
| **Security / SecOps** | "El Change Advisor flaggeó la dependencia nueva y el endpoint que habla con un LLM. El equipo de seguridad tiene visibilidad desde el primer momento, no después del merge." | Expert Agent genera review con risk classification que incluye contexto de seguridad. |
| **Managers / Business** | "Hay un registro de cada cambio, quién lo hizo, qué validaciones pasó, quién lo aprobó. Para auditoría y compliance, esto es oro." | Audit trail nativo: quién, qué, cuándo, resultado de cada gate. |

---

## Qué elementos se muestran y por qué

### 1. Harness AI Chat Agent Extension (conversacional)
**Qué:** Extension de VS Code donde el developer pregunta por resultados del pipeline, diagnósticos, y análisis del Change Advisor — todo conversacional, sin salir del IDE.
**Por qué:** Sigue la narrativa "todo es AI y conversacional". El developer no abre un browser para ir a Harness Console. Pregunta desde donde trabaja. Esto es natural — un developer HARÍA esto: "¿qué pasó con mi pipeline?" desde el IDE.
**Diferencia vs. Harness Extension (sidebar):** La Harness Extension (sidebar) es pasiva — muestra status. El Harness AI Chat Agent es activo — conversas, preguntas, obtienes diagnósticos. Son complementarias.

### 2. Pipeline de PR Validation (auto-trigger)
**Qué:** El pipeline se ejecuta automáticamente cuando se crea el PR.
**Por qué:** Demuestra que la governance no es opcional — está embebida en el flujo. El developer no puede "saltarse" la validación.
**Cómo se muestra:** A través del Harness AI Chat Agent — el developer pregunta por el resultado, no navega a Harness Console. Opcionalmente, la Harness Extension en el sidebar muestra el status visualmente.

### 3. Test Intelligence (vía Harness AI / MCP)
**Qué:** Solo corre los tests afectados por el cambio, no la suite completa.
**Por qué:** Es AI nativa en el build process. Reduce tiempo de CI sin sacrificar cobertura.
**Cómo se muestra sin entrar a Harness:** El developer pregunta vía Harness AI Chat Agent o Claude Code + MCP: "¿cuántos tests corrieron? ¿por qué esos?". La respuesta incluye el detalle de TI. No necesitas navegar al step en Harness Console.

### 4. Change Advisor (Expert Agent)
**Qué:** Un Expert Agent que analiza el PR, clasifica el cambio, evalúa riesgo, y posta un review estructurado como comment en GitHub.
**Por qué:** Es el primer Expert Agent de Harness que la audiencia experimenta. Establece el patrón: Harness agents razonan, no solo ejecutan.
**Cómo se muestra:** Vía Harness AI Chat Agent preguntando por el análisis, O vía el PR comment en GitHub (sin salir del IDE si usas GitHub dentro de VS Code).
**Por qué no code review de otro LLM:** Un LLM haciendo code review es commoditized. El Change Advisor no hace code review — hace change analysis con contexto de plataforma: pipeline history, deployment targets, policy gates, security posture. Eso solo lo puede hacer un agent conectado al SDLC.

---

## WOW del acto

> **"El Change Advisor no te dice 'tienes un typo en la línea 42'. Te dice 'este PR introduce un endpoint que hace llamadas a un servicio externo, agrega una dependencia nueva, y no tiene tests de integración. Risk level: medium. Reviewer focus: data handling y external dependency.' Eso no es linting — es reasoning."**

### Por qué es diferenciador

**vs. GitHub Copilot Code Review:** Copilot revisa el código. El Change Advisor revisa el CAMBIO — el delta contra el estado de la plataforma. Sabe que este servicio tiene 4 findings abiertos. Sabe que el último deploy fue hace 3 días. Sabe que la policy de seguridad requiere scan antes de merge.

**vs. GitLab Duo:** Duo es un agent cerrado dentro de GitLab. No tiene contexto de CD, de runtime, ni de security findings fuera de GitLab.

**vs. Custom LLM review:** Puedes buildear un bot que llame a un LLM con el diff. Pero no tiene pipeline context, no tiene deployment history, no tiene security posture, y no tiene policy gates que puedan bloquear el merge si el riesgo es alto.

---

## Cómo conecta al Acto 3

### Transición narrativa

> *"El cambio está gobernado. El pipeline validó que compila, que los tests pasan, y el Change Advisor evaluó el riesgo. Pero gobernar no es lo mismo que securizar.*
>
> *Claude Code introdujo código nuevo — un endpoint que habla con un LLM, una dependencia nueva, queries a la base de datos. El pipeline dijo que funciona. Pero ¿es seguro?*
>
> *Aquí es donde el Security Testing Agent entra con todo su arsenal."*

### Lo que se planta para actos futuros

| Elemento plantado | Relevancia futura |
|-------------------|-------------------|
| Change Advisor flaggeó la nueva dependencia (`requests`) | En Acto 3, SCA confirma que tiene un CVE conocido |
| Change Advisor flaggeó el endpoint externo (MCP call) | En Acto 5, este endpoint es parte de la cadena de ataque |
| Change Advisor clasificó riesgo como "medium" | En Acto 5, vemos que "medium" individual se convierte en "critical" encadenado |
| Audit trail de PR validation | En Acto 6, el trail completo soporta la respuesta a incidentes |

---

## Secuencia exacta de ejecución — Timeline

```
══════════════════════════════════════════════════════════════════════════════════
  ACTO 2 — TIMELINE DE EJECUCIÓN                              Duración: ~3 min
══════════════════════════════════════════════════════════════════════════════════

  CONTEXTO DE ENTRADA:
  Seguimos en VS Code. El Acto 1 terminó con el PR creado.
  La Harness Extension en el sidebar ya muestra: 🔄 Running
  NO salimos del IDE. Todo el Acto 2 es conversacional.

  HERRAMIENTAS EN JUEGO:
  ┌────────────────────────────┬──────────────────────────────────────────┐
  │ Herramienta                │ Rol en este acto                         │
  ├────────────────────────────┼──────────────────────────────────────────┤
  │ Harness Extension (sidebar)│ Visual — muestra status del pipeline     │
  │ Harness AI Chat Agent      │ Conversacional — preguntas, diagnóstico │
  │ Claude Code + MCP          │ Alternativa — queries vía MCP tools      │
  └────────────────────────────┴──────────────────────────────────────────┘


  t=0:00              PASO 1: EL PIPELINE YA ESTÁ CORRIENDO
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "El coding agent se detuvo en el PR. Pero Harness no se
  │   detuvo. Miren el sidebar — el Software Delivery Agent
  │   ya tomó el control. El pipeline está corriendo."
  │
  │  🖥️ ACCIÓN:
  │  Señalar la Harness Extension en el sidebar de VS Code.
  │  NO abrir browser. NO ir a Harness Console.
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ VS CODE                                                 │
  │  │ ┌──────────┐ ┌──────────────────────────────────────┐  │
  │  │ │ Explorer  │ │                                      │  │
  │  │ │           │ │  (código del Acto 1 todavía visible) │  │
  │  │ │ ───────── │ │                                      │  │
  │  │ │ 🔶HARNESS │ │                                      │  │
  │  │ │ EXTENSION │ │                                      │  │
  │  │ │           │ │                                      │  │
  │  │ │ Pipeline: │ │                                      │  │
  │  │ │ PR-Val    │ │                                      │  │
  │  │ │ #848      │ │                                      │  │
  │  │ │ 🔄Running │ │                                      │  │
  │  │ │           │ │                                      │  │
  │  │ │ Trigger:  │ │                                      │  │
  │  │ │ PR #52    │ │                                      │  │
  │  │ └──────────┘ └──────────────────────────────────────┘  │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK:
  │  "El developer no tuvo que abrir nada. No configuró nada.
  │   El PR se creó y la plataforma reaccionó sola. Pero en
  │   lugar de ir a Harness Console, le voy a preguntar
  │   directamente qué está pasando."
  │
  │  ⭐ WOW: Auto-trigger visible sin salir del IDE.
  │
  ▼

  t=0:30        PASO 2: PREGUNTAR POR LA EJECUCIÓN (HARNESS AI)
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Voy a preguntarle a Harness AI — sin salir del IDE —
  │   qué está pasando con mi pipeline y qué encontró."
  │
  │  🖥️ ACCIÓN:
  │  Abrir el Harness AI Chat Agent panel en VS Code.
  │  Escribir el prompt:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO — Harness AI Chat Agent:              │
  │  │                                                         │
  │  │ Give me a summary of the current pipeline execution     │
  │  │ for PR #52. What stage is it in, did the tests pass,    │
  │  │ and how many tests did Test Intelligence select vs      │
  │  │ the full suite?                                         │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  📎 PROMPT ALTERNATIVO — Claude Code + MCP:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ Use the Harness MCP tools to get the execution summary  │
  │  │ for pipeline PR-Validation on PR #52. Show me the       │
  │  │ Test Intelligence results: how many tests were in the   │
  │  │ suite, how many were selected, and why those were       │
  │  │ chosen.                                                 │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 HARNESS AI RESPONSE                                 │
  │  │                                                         │
  │  │ Pipeline PR-Validation #848 is currently running.       │
  │  │                                                         │
  │  │ ✅ CI Build stage completed (42s):                      │
  │  │   • Build: successful                                   │
  │  │   • Tests: 11 of 47 selected by Test Intelligence       │
  │  │   • Tests skipped: 36 (not correlated to changes)       │
  │  │   • Time saved: ~65%                                    │
  │  │                                                         │
  │  │ 🧠 Test Intelligence selection:                         │
  │  │   Changed files: ai_assistant.py, app.py,               │
  │  │   requirements.txt                                      │
  │  │   Correlated tests: test_routes.py, test_app.py,        │
  │  │   test_ai_assistant.py                                  │
  │  │   Model confidence: 94%                                 │
  │  │                                                         │
  │  │ 🔄 Security Scan stage: in progress                     │
  │  │ ⏳ Deploy stage: queued                                  │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK (señalando la respuesta):
  │  "Sin abrir Harness Console, sin navegar dashboards: en un
  │   prompt tengo el resumen completo. Test Intelligence analizó
  │   qué archivos cambiaron — ai_assistant.py, app.py,
  │   requirements.txt — y solo corrió los 11 tests correlacionados.
  │
  │   De 47 tests, corrió 11. 65% de ahorro en tiempo. En una
  │   suite real de 2000 tests, eso es la diferencia entre esperar
  │   45 minutos o 8. No es skip tests — es AI que entiende la
  │   correlación entre código y tests, y mejora con cada build."
  │
  │  ⭐ WOW:
  │  "Todo conversacional. El developer pregunta, Harness AI
  │   responde con datos reales del pipeline. Sin context
  │   switching. Sin navegar UI. AI everything."
  │
  ▼

  t=1:30       PASO 3: CHANGE ADVISOR — PREGUNTAR POR EL REVIEW
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Ahora el Software Delivery Agent activó un Expert Agent —
  │   el Change Advisor. No es un linter. No busca typos. Es un
  │   agent que razona sobre lo que CAMBIÓ. Veamos qué encontró."
  │
  │  🖥️ ACCIÓN:
  │  Escribir en Harness AI Chat Agent:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO — Harness AI Chat Agent:              │
  │  │                                                         │
  │  │ What did the Change Advisor find on PR #52?             │
  │  │ Show me the risk assessment and recommendations.        │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  📎 PROMPT ALTERNATIVO — Claude Code + MCP:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ Use the Harness MCP tools to get the Change Advisor     │
  │  │ analysis for PR #52. What risk factors did it identify   │
  │  │ and what is its recommendation?                         │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 HARNESS AI RESPONSE                                 │
  │  │                                                         │
  │  │ 📋 Change Advisor Report for PR #52                     │
  │  │                                                         │
  │  │ Classification:                                         │
  │  │   Type: Feature addition                                │
  │  │   Risk: ⚠️ MEDIUM                                       │
  │  │                                                         │
  │  │ What changed:                                           │
  │  │   • New endpoint: POST /api/ai/chat                     │
  │  │   • New endpoint: GET /api/ai/status                    │
  │  │   • New dependency: requests (pinned 2.25.1)            │
  │  │   • External service call to MCP financial data         │
  │  │   • Database queries for account data                   │
  │  │                                                         │
  │  │ Risk factors:                                           │
  │  │   ⚠️ New external dependency added                      │
  │  │   ⚠️ Endpoint processes user input for LLM context      │
  │  │   ⚠️ Database queries return financial data             │
  │  │   ⚠️ No integration tests for new endpoint              │
  │  │                                                         │
  │  │ Recommendation:                                         │
  │  │   Review with attention — AI endpoint with external     │
  │  │   service integration and financial data access         │
  │  │                                                         │
  │  │ PR Comment: Posted to GitHub PR #52                     │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK (señalando la respuesta):
  │  "Miren lo que identificó: endpoint que procesa user input
  │   para un LLM, dependencia nueva pinneada a versión específica,
  │   queries que retornan datos financieros, sin integration tests.
  │
  │   Esto no es 'tu código tiene un error en la línea 42'.
  │   Esto es: 'este cambio introduce una superficie de ataque
  │   nueva y te digo exactamente dónde mirar.'
  │
  │   Y noten algo — flaggeó que el endpoint procesa user input
  │   para contexto de LLM. Eso es exactamente donde está la
  │   prompt injection que todavía no descubrimos. El Change
  │   Advisor no tiene SAST — no puede detectar la vulnerabilidad.
  │   Pero te dice: 'aquí hay riesgo, revisa.'
  │
  │   Y todo esto — sin salir del IDE. Conversacional."
  │
  │  ⭐ WOW:
  │  "No es un linter. No es code review. Es change ANALYSIS
  │   con contexto de plataforma. Sabe que es un feature nuevo
  │   con acceso a datos financieros y un LLM. ¿Qué otro CI
  │   tool te da esto? Y lo estamos consumiendo desde el IDE,
  │   conversacionalmente, sin abrir un solo dashboard."
  │
  ▼

  t=2:15                    PASO 4: TRANSICIÓN AL ACTO 3
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "El cambio está gobernado. El pipeline validó que compila,
  │   que los tests pasan, y el Change Advisor evaluó el riesgo.
  │   Todo desde el IDE, todo conversacional, todo registrado
  │   para compliance y auditoría.
  │
  │   Pero gobernar no es lo mismo que securizar.
  │
  │   Claude Code introdujo un endpoint que habla con un LLM,
  │   una dependencia nueva, queries a la base de datos. El
  │   Change Advisor dijo 'review with attention'.
  │
  │   ¿Pero tiene vulnerabilidades reales? ¿La dependencia
  │   tiene CVEs conocidos? ¿El endpoint es explotable?
  │
  │   Aquí es donde el Security Testing Agent entra con todo
  │   su arsenal."
  │
  │  🖥️ ACCIÓN:
  │  Señalar en el sidebar de Harness Extension que el
  │  Security Scan stage cambió a "Running".
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🔶 HARNESS EXTENSION (sidebar)                         │
  │  │                                                         │
  │  │ Pipeline: PR-Validation #848                            │
  │  │                                                         │
  │  │  ✅ CI Build         42s                                │
  │  │  ✅ Change Advisor   14s                                │
  │  │  🔄 Security Scan    running...                         │
  │  │  ⏳ Deploy            queued                             │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW:
  │  "Mismo pipeline, mismo flujo. Build → Change Advisor →
  │   Security. No son herramientas separadas. Es una plataforma
  │   orquestando agents especializados en secuencia."
  │
  ▼
  ║
  ║  ═══════════════════════════════════════════════════════════
  ║   → TRANSICIÓN DIRECTA AL ACTO 3
  ║     Security Testing Agent toma el control del pipeline
  ║  ═══════════════════════════════════════════════════════════
  ║


══════════════════════════════════════════════════════════════════════════════════
  RESUMEN DEL ACTO 2
══════════════════════════════════════════════════════════════════════════════════

  TIEMPO TOTAL: ~3 minutos
  CONTEXT SWITCHING: CERO — todo en VS Code

  PASOS:
  ┌────────┬────────────────────────────┬──────────┬───────────────────────────┐
  │ Paso   │ Qué pasa                   │ Duración │ WOW                       │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 1      │ Sidebar muestra pipeline   │ 30s      │ Auto-trigger, sin salir   │
  │        │ corriendo                  │          │ del IDE                   │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 2      │ Harness AI: resumen de     │ 60s      │ TI: 11/47 tests, 65%     │
  │        │ ejecución + TI results     │          │ ahorro. Conversacional.   │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 3      │ Harness AI: Change Advisor │ 45s      │ Risk assessment con       │
  │        │ analysis                   │          │ contexto de plataforma    │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 4      │ Transición al Acto 3       │ 30s      │ Mismo pipeline, fluido    │
  └────────┴────────────────────────────┴──────────┴───────────────────────────┘

  PROMPTS UTILIZADOS:
  ┌─────┬───────────────────────┬─────────────────────────────────────────────┐
  │ #   │ Herramienta           │ Prompt                                      │
  ├─────┼───────────────────────┼─────────────────────────────────────────────┤
  │ 1   │ Harness AI Chat Agent │ "Give me a summary of the current pipeline │
  │     │                       │  execution for PR #52. What stage is it in, │
  │     │                       │  did the tests pass, and how many tests did │
  │     │                       │  Test Intelligence select vs the full       │
  │     │                       │  suite?"                                    │
  ├─────┼───────────────────────┼─────────────────────────────────────────────┤
  │ 2   │ Harness AI Chat Agent │ "What did the Change Advisor find on        │
  │     │                       │  PR #52? Show me the risk assessment and    │
  │     │                       │  recommendations."                         │
  └─────┴───────────────────────┴─────────────────────────────────────────────┘

  CAPABILITIES DEMOSTRADAS:
  ┌──────────────────────────────┬─────────────────────────────────────────────┐
  │ Capability                   │ Qué demostró                                │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Software Delivery Agent      │ Pipeline orquestado end-to-end              │
  │   — Builds                   │ CI: checkout, build, tests                  │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Test Intelligence            │ 11/47 tests seleccionados por correlación   │
  │                              │ de código, 65% ahorro en tiempo             │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Change Advisor               │ Risk assessment estructurado con contexto   │
  │ (Expert Agent)               │ de plataforma — change analysis, no code    │
  │                              │ review                                      │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Harness AI Chat Agent        │ Consumo conversacional de datos de pipeline │
  │                              │ sin context switching                       │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Governed Orchestration       │ Auto-trigger, policy evaluation, audit      │
  │ Engine                       │ trail completo                              │
  └──────────────────────────────┴─────────────────────────────────────────────┘

  SEÑALES PLANTADAS PARA ACTOS FUTUROS:
  ┌──────────────────────────────────┬────────────────────────────────────────┐
  │ Señal                            │ Dónde paga                             │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Change Advisor: "new dependency  │ Acto 3: SCA confirma CVE-2023-32681   │
  │ requests v2.25.1"               │ en requests                            │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Change Advisor: "endpoint        │ Acto 5: prompt injection explota       │
  │ processes user input for LLM"    │ exactamente ese user input             │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Change Advisor: "queries return  │ Acto 5: PII leak — esos datos         │
  │ financial data"                  │ financieros se exfiltran               │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Risk: MEDIUM                     │ Acto 5: individual = medium,           │
  │                                  │ encadenado = critical                  │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Audit trail de toda la ejecución │ Acto 6: soporta respuesta a incidente │
  └──────────────────────────────────┴────────────────────────────────────────┘
```
