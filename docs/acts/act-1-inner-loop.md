# ACTO 1: "El Código Ya Se Escribe a Velocidad de AI"

## Qué hace el acto

Un developer usa un AI coding agent para construir un feature nuevo: un AI banking assistant para DemoBank. En minutos, el feature está listo y el PR creado. Todo parece correcto. Pero el código generado por AI contiene fallos silenciosos que no son visibles a simple vista ni detectables por SAST — son problemas de lógica de negocio y comportamiento que solo se manifiestan en runtime. La audiencia no lo sabe todavía. Lo descubrirán en los actos siguientes.

---

## Por qué este contexto narrativo

**1. Empatía inmediata.** Empezar desde el IDE con un coding task real conecta con cualquier audiencia técnica.

**2. Establece la premisa.** El código ya se escribe a velocidad de AI. El problema no es escribirlo — es gobernar, validar, y proteger lo que se escribió.

**3. Planta el conflicto silenciosamente.** El AI coding agent introduce vulnerabilidades que SAST no puede detectar: prompt injection, PII leak, BOLA/IDOR. Estas pasan el pipeline de seguridad en el Acto 3 porque no tienen un patrón de código malicioso — el código "funciona correctamente", solo hace algo que no debería. El atacante las encuentra en el Acto 5. Runtime Protection las detecta en el Acto 6. Esta es la prueba de que Shift Left solo no basta — necesitas Shield Right.

---

## Qué le ofrece a la audiencia

| Audiencia | Lo que se llevan | Wiring técnico |
|-----------|-----------------|----------------|
| **Developer** | "Con MCP y el AI Chat Agent, puedo resolver tareas más rápido porque el coding agent tiene contexto de mi pipeline, findings, y deploys — no solo el repo." | Harness MCP expone pipeline, findings, y deploys como tools. AI Chat Agent razona sobre el SDLC dentro del IDE. |
| **DevOps / Platform** | "Los coding agents de los developers están conectados a la plataforma. No trabajan en un silo." | Harness MCP es read-only self-service. El developer consulta sin depender de DevOps. |
| **Security / SecOps** | "AI genera código que PARECE correcto. No puedo depender del mismo agent para validarlo. Necesito validación independiente." | Separación de concerns: write ≠ validate. Harness valida en Actos 2-3 (SDLC) y 5-6 (runtime). |
| **Managers / Business** | "La velocidad de coding ya cambió. La pregunta es cómo gobernar lo que se produce." | El acto muestra la velocidad. Los actos siguientes muestran la governance. |

---

## Qué elementos se muestran y por qué

### 1. AI Coding Agent (Claude Code)
**Qué:** Claude Code como coding agent en el IDE. No es de Harness.
**Por qué:** Harness no compite con coding agents. Los complementa. "Usa el que quieras." Mostrar uno de terceros refuerza que Harness es agnóstico.

### 2. Harness MCP
**Qué:** El coding agent consulta datos de Harness (pipelines, findings, deploys) durante la tarea de coding.
**Por qué:** Muestra que el inner loop ya está conectado al SDLC. Sin MCP, el coding agent solo ve el repo. Con MCP, ve el contexto completo.
**Por qué no otras capabilities:** El acto es sobre el developer. Pipelines, scanners, deploys se muestran después. Mostrar demasiado aquí diluye el handoff al Acto 2.

### 3. Harness IDE Extension + AI Chat Agent
**Qué:** Sidebar con pipeline status, findings. AI Chat Agent para razonar sobre el SDLC.
**Por qué:** Demuestra que Harness vive donde el developer vive. El AI Chat Agent complementa al coding agent: uno escribe código, el otro razona sobre el SDLC.

---

## WOW del acto

> **"En 3 minutos, un feature completo — endpoint, lógica, dependencias — está escrito, testeado, y en un PR. Pero el mismo agent que lo escribió no puede validarlo. Eso es como pedirle al autor que califique su propio examen. ¿Quién lo valida? Harness."**

### Por qué es diferenciador

**vs. GitHub Copilot / GitLab Duo:** Copilot ve el repo. Duo es un agent cerrado de GitLab. Ninguno expone contexto de CD, security findings, ni deployment history a coding agents de terceros vía MCP.

**vs. Build yourself:** Construir MCP tools custom para tu CI/CD system, mantener el glue code, actualizar cuando la API cambia. Harness MCP ya lo hizo — es nativo.

**El punch real:** El coding agent que escribe no puede ser el que valida. Otros LLMs pueden hacer code review vía MCP, sí — pero sería el mismo modelo revisando su propio patrón de pensamiento. Harness provee validación independiente con datos que el coding agent no tiene: reachability analysis, behavioral baselines, policy gates, runtime protection.

---

## Cómo conecta al Acto 2

### Transición narrativa

> *"El feature está listo. El PR está creado. Pero ¿puedo confiar en que está correcto? El coding agent me dice que sí — pero él lo escribió. El que escribe el código no puede ser el que lo valida.*
>
> *Harness ya está validando. El Software Delivery Agent tomó el control del PR automáticamente. Veamos qué encuentra."*

### Lo que se planta para actos futuros

El AI coding agent introdujo código que PARECE correcto pero tiene fallos silenciosos:

| Fallo silencioso | Por qué SAST no lo detecta | Dónde se descubre |
|-----------------|---------------------------|-------------------|
| **Prompt injection** (VULN-008) — user input concatenado en system prompt | El patrón es string concatenation, algo normal en código. No hay "payload malicioso" en el código mismo. | **Acto 5:** atacante lo explota. **Acto 7:** AI Firewall lo detecta |
| **PII leak** (VULN-009) — AI response incluye datos financieros raw | El código funciona correctamente. Retorna datos de la DB. SAST no sabe que esos datos son PII ni que no deberían exponerse en un AI response. | **Acto 5:** datos exfiltrados. **Acto 7:** AI Security |
| **BOLA/IDOR** (VULN-010) — endpoint sin auth check | No hay código malicioso. Solo FALTA un check de autorización. SAST no puede determinar que auth DEBERÍA estar ahí. | **Acto 5:** cadena de ataque. **Acto 6:** Remediation Agent |
| **Dependencia vulnerable** — `requests==2.25.1` | SCA SÍ lo detecta en Acto 3. Se remedia en Acto 3. Pero el blast radius se analiza en Acto 6. | **Acto 3:** SCA flag. **Acto 6:** SBOM blast radius |

**Nota narrativa:** Las 4 vulns clásicas (SQL injection, command injection, XSS, CORS) ya estaban en el codebase ANTES del Acto 1. El Security Testing Agent las detecta y remedia en el Acto 3. Las vulns AI-specific que el coding agent introduce en el Acto 1 son las que SOBREVIVEN al Acto 3 y detonan en el Acto 5.

---

## Mecanismo de repetibilidad

### Dos ramas

```
demo/base                          demo/completed
─────────                          ──────────────
DemoBank SIN el AI assistant       DemoBank CON el AI assistant
(solo las 4 vulns clásicas)        (4 clásicas + 3 AI-specific + dep vulnerable)
                                   + PR pre-creado como referencia
```

### Reset entre demos

```
1. git checkout demo/base           → estado limpio, sin AI assistant
2. Verificar MCP conectado          → Harness MCP tools disponibles en Claude Code
3. Tener prompt de coding listo     → copiar/pegar para consistencia
4. PR de demo/completed como backup → si Claude Code diverge, usar este PR
```

---

## Secuencia exacta de ejecución — Timeline

```
══════════════════════════════════════════════════════════════════════════════════
  ACTO 1 — TIMELINE DE EJECUCIÓN                              Duración: ~4 min
══════════════════════════════════════════════════════════════════════════════════


  t=0:00                         PASO 1: CONTEXTO
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Todo developer hoy está usando algún tipo de AI coding agent —
  │   Claude Code, Copilot, Codex. El código ya se escribe
  │   a velocidad de AI. Vamos a ver cómo se ve eso en la práctica."
  │
  │  🖥️ ACCIÓN:
  │  Abrir VS Code con Claude Code extension y el repo DemoBank.
  │  Asegurarse que la Harness IDE Extension sea visible en sidebar.
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ VS CODE + CLAUDE CODE                                  │
  │  │ ┌──────────┐ ┌──────────────────────────────────────┐  │
  │  │ │ Explorer  │ │  app/                                │  │
  │  │ │ ├─ app/   │ │    routes/                           │  │
  │  │ │ ├─ k8s/   │ │      accounts.py                     │  │
  │  │ │ ├─ tests/ │ │      admin.py                        │  │
  │  │ │           │ │                                      │  │
  │  │ │ ───────── │ │                                      │  │
  │  │ │ 🔶HARNESS │ │                                      │  │
  │  │ │ Pipeline: │ │                                      │  │
  │  │ │  ✅ Pass  │ │                                      │  │
  │  │ │ Findings: │ │                                      │  │
  │  │ │  ⚠️ 4     │ │                                      │  │
  │  │ └──────────┘ └──────────────────────────────────────┘  │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW: Ninguno — estamos haciendo setup.
  │
  ▼

  t=0:30                      PASO 2: EL REQUERIMIENTO
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Tenemos un nuevo requerimiento de negocio: DemoBank quiere
  │   ofrecer un AI banking assistant — un chatbot donde los clientes
  │   pregunten sobre sus cuentas en lenguaje natural. El developer
  │   lo va a construir con su AI coding agent."
  │
  │  🖥️ ACCIÓN:
  │  Mostrar ticket brevemente (Jira, Slack, o verbal).
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📋 JIRA-4521: Add AI Banking Assistant                 │
  │  │                                                         │
  │  │ As a DemoBank customer, I want to ask questions about   │
  │  │ my account using natural language so I can get instant   │
  │  │ answers without navigating the app.                     │
  │  │                                                         │
  │  │ Acceptance:                                              │
  │  │ • POST /api/ai/chat endpoint                            │
  │  │ • Query account data for context                        │
  │  │ • Connect to external financial data service            │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW: Ninguno — establecemos el problema de negocio.
  │
  ▼

  t=1:00               PASO 3: HARNESS MCP — CONTEXTO DEL SDLC
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Antes de codear, el developer tiene algo que otros no tienen:
  │   contexto del SDLC en su IDE. El coding agent está conectado
  │   a Harness vía MCP. No trabaja a ciegas."
  │
  │  🖥️ ACCIÓN:
  │  Escribir en Claude Code (chat panel o terminal):
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO (copiar/pegar):                       │
  │  │                                                         │
  │  │ Use the Harness MCP tools to give me context on the     │
  │  │ DemoBank service: what's the current deployment         │
  │  │ status, any open security findings, and the last        │
  │  │ pipeline execution result.                              │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 CLAUDE CODE RESPONSE                                │
  │  │                                                         │
  │  │ Here's the current state of DemoBank:                   │
  │  │                                                         │
  │  │ 📦 Deployment: v2.4.1 deployed to production (healthy)  │
  │  │                                                         │
  │  │ 🔒 Security Findings (4 open):                          │
  │  │   • CRITICAL: SQL Injection in accounts.py:L23          │
  │  │   • CRITICAL: Command Injection in admin.py:L18         │
  │  │   • MEDIUM: Reflected XSS in app.py:L45                 │
  │  │   • LOW: Insecure CORS configuration                    │
  │  │                                                         │
  │  │ 🔄 Last Pipeline: PR-Validation #847 — ✅ Passed        │
  │  │    Duration: 3m 42s | Tests: 12/12 passed               │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW:
  │  "En un solo prompt, el developer tiene el contexto completo:
  │   qué está deployado, qué vulnerabilidades hay, cómo fue el
  │   último pipeline. Sin abrir browser, sin navegar dashboards,
  │   sin preguntarle a DevOps. Eso es Harness MCP."
  │
  ▼

  t=2:00            PASO 4: AI CODING AGENT CONSTRUYE EL FEATURE
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Ahora el developer le pide al coding agent que construya
  │   el AI banking assistant. Vean la velocidad."
  │
  │  🖥️ ACCIÓN:
  │  Escribir en Claude Code:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO (copiar/pegar):                       │
  │  │                                                         │
  │  │ Create an AI banking assistant for DemoBank:            │
  │  │ - Add a new endpoint POST /api/ai/chat that accepts     │
  │  │   a customer message and returns an AI-powered response │
  │  │   with relevant account information                     │
  │  │ - The assistant should query our accounts database for  │
  │  │   context and call an external MCP financial data       │
  │  │   service for enrichment                                │
  │  │ - Add a GET /api/ai/status endpoint that shows the      │
  │  │   assistant's configuration                             │
  │  │ - Register the new routes in the Flask app              │
  │  │ - Add the requests library to requirements.txt for the  │
  │  │   external service call                                 │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  El coding agent genera 3 cambios en ~90 segundos:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 CLAUDE CODE WORKING...                               │
  │  │                                                         │
  │  │ ✅ Created: app/routes/ai_assistant.py                  │
  │  │    • POST /api/ai/chat — accepts message, queries DB,  │
  │  │      calls external MCP service, returns AI response    │
  │  │    • GET /api/ai/status — returns config/health         │
  │  │                                                         │
  │  │ ✅ Modified: app/app.py                                 │
  │  │    • Registered ai_assistant_bp at /api/ai              │
  │  │                                                         │
  │  │ ✅ Modified: requirements.txt                           │
  │  │    • Added requests==2.25.1                             │
  │  │                                                         │
  │  │ Summary: New AI banking assistant with database context │
  │  │ and external service integration. Ready for review.     │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ❗ LO QUE LA AUDIENCIA NO SABE (y no debe saber todavía):
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ El código se ve CORRECTO. Se ve profesional. Pero:      │
  │  │                                                         │
  │  │ ⚠️ system_prompt = "..." + message  → Prompt Injection  │
  │  │   (parece string concatenation normal)                  │
  │  │                                                         │
  │  │ ⚠️ SELECT * FROM accounts → PII Leak                   │
  │  │   (parece una query normal)                             │
  │  │                                                         │
  │  │ ⚠️ /<id>/details sin auth → BOLA/IDOR                  │
  │  │   (parece un endpoint REST normal)                      │
  │  │                                                         │
  │  │ ⚠️ requests==2.25.1 → CVE conocido                     │
  │  │   (parece una dep normal)                               │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK (después de que el agent termina):
  │  "En menos de 2 minutos: un endpoint completo, con conexión
  │   a base de datos, integración con servicio externo, y
  │   registro en la aplicación. El código se ve bien. Se ve
  │   profesional. Un developer experimentado lo revisaría y
  │   diría 'esto está correcto'."
  │
  │  🎤 PAUSA DRAMÁTICA:
  │  "Pero... ¿realmente está correcto? Vamos a ver."
  │
  │  ⭐ WOW: La VELOCIDAD. Feature completo en <2 min.
  │     El WOW real viene cuando descubran que estaba MAL.
  │
  │  📝 NOTA PARA EL SE:
  │  Si el coding agent diverge significativamente, hacer
  │  checkout del PR pre-creado en demo/completed y decir:
  │  "El coding agent generó este PR, veamos qué contiene."
  │
  ▼

  t=3:00                       PASO 5: PR CREADO
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "El coding agent crea el PR automáticamente con descripción
  │   completa: qué cambió, por qué, y cómo validarlo."
  │
  │  🖥️ ACCIÓN:
  │  El coding agent crea el PR (o mostrar PR pre-creado).
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🔀 Pull Request #52                                    │
  │  │ feat: add AI banking assistant endpoint                 │
  │  │                                                         │
  │  │ ## Summary                                              │
  │  │ Added AI-powered banking assistant that allows          │
  │  │ customers to query account information via natural      │
  │  │ language. Integrates with external MCP financial         │
  │  │ data service for enrichment.                            │
  │  │                                                         │
  │  │ ## Changes                                              │
  │  │ • New: app/routes/ai_assistant.py (+87 lines)           │
  │  │ • Modified: app/app.py (+2 lines)                       │
  │  │ • Modified: requirements.txt (+1 line)                  │
  │  │                                                         │
  │  │ Files changed: 3  Additions: +90  Deletions: 0         │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW: No es el PR — es lo que viene.
  │
  ▼

  t=3:30                      PASO 6: EL HANDOFF
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK (este es el momento clave del acto):
  │
  │  "El feature está listo. El PR está creado. El coding agent
  │   hizo su trabajo en minutos."
  │
  │  [pausa]
  │
  │  "Pero aquí hay algo fundamental:
  │   ¿Puedo confiar en que este código es correcto?"
  │
  │  "El coding agent me dice que sí — pero él lo escribió.
  │   Si le pregunto al mismo modelo '¿tu código es seguro?',
  │   me va a decir que sí. Siempre. Porque él lo generó."
  │
  │  "El que escribe el código NO puede ser el que lo valida.
  │   Necesitas un validador independiente — uno que no tenga
  │   el bias del que escribió, que evalúe con criterios de
  │   plataforma, con datos de pipeline, con análisis de
  │   seguridad que el coding agent no tiene."
  │
  │  "Eso es exactamente lo que hace Harness. Y ya empezó."
  │
  │  🖥️ ACCIÓN:
  │  Señalar la Harness IDE Extension en el sidebar.
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🔶 HARNESS EXTENSION                                   │
  │  │                                                         │
  │  │ Pipeline: PR-Validation #848                            │
  │  │ Status:  🔄 Running...                                  │
  │  │ Trigger: PR #52 (auto)                                  │
  │  │                                                         │
  │  │ Stages:                                                 │
  │  │  ▶ CI Build          🔄 in progress                     │
  │  │  ○ Security Scan     ⏳ queued                          │
  │  │  ○ Deploy            ⏳ queued                          │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW:
  │  "No hubo que hacer nada. No hubo que configurar nada.
  │   El PR se creó y Harness automáticamente empezó a validar.
  │   El coding agent se detuvo en el PR. Harness Agents
  │   tomaron el control. Veamos qué encuentran."
  │
  ▼
  ║
  ║  ═══════════════════════════════════════════════════════
  ║   → TRANSICIÓN DIRECTA AL ACTO 2
  ║     Software Delivery Agent toma el control del PR
  ║  ═══════════════════════════════════════════════════════
  ║


══════════════════════════════════════════════════════════════════════════════════
  RESUMEN DEL ACTO 1
══════════════════════════════════════════════════════════════════════════════════

  TIEMPO TOTAL: ~4 minutos

  PASOS:
  ┌────────┬────────────────────────────┬──────────┬───────────────────────────┐
  │ Paso   │ Qué pasa                   │ Duración │ WOW                       │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 1      │ Abrir IDE + Extension      │ 30s      │ —                         │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 2      │ Mostrar requerimiento      │ 30s      │ —                         │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 3      │ MCP context query          │ 60s      │ Contexto SDLC completo    │
  │        │                            │          │ en 1 prompt               │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 4      │ Coding agent genera feat.  │ 90s      │ Feature completo en <2min │
  │        │                            │          │ (fallos silenciosos)      │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 5      │ PR creado                  │ 30s      │ —                         │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 6      │ Handoff a Harness          │ 30s      │ Pipeline auto-trigger     │
  │        │ "write ≠ validate"         │          │ "write ≠ validate"        │
  └────────┴────────────────────────────┴──────────┴───────────────────────────┘

  ARTEFACTOS GENERADOS:
  ┌─────────────────────────────────┬──────────────────────────────────────────┐
  │ Artefacto                       │ Destino                                  │
  ├─────────────────────────────────┼──────────────────────────────────────────┤
  │ app/routes/ai_assistant.py      │ VULN-008, 009, 010 → explotan en Acto 5 │
  │ app/app.py (modificado)         │ Blueprint registrado                     │
  │ requirements.txt (modificado)   │ CVE en requests → SCA detecta en Acto 3 │
  │ PR #52                          │ Trigger de pipeline → Acto 2             │
  └─────────────────────────────────┴──────────────────────────────────────────┘

  VULNERABILIDADES PLANTADAS:
  ┌────────────┬───────────────────┬───────────────┬──────────────────────────┐
  │ ID         │ Tipo              │ ¿SAST la ve?  │ ¿Dónde detona?           │
  ├────────────┼───────────────────┼───────────────┼──────────────────────────┤
  │ VULN-008   │ Prompt Injection  │ ❌ NO         │ Acto 5 → Acto 7          │
  ├────────────┼───────────────────┼───────────────┼──────────────────────────┤
  │ VULN-009   │ PII Leak          │ ❌ NO         │ Acto 5 → Acto 7          │
  ├────────────┼───────────────────┼───────────────┼──────────────────────────┤
  │ VULN-010   │ BOLA/IDOR         │ ❌ NO         │ Acto 5 → Acto 6          │
  ├────────────┼───────────────────┼───────────────┼──────────────────────────┤
  │ SCA CVE    │ Dep. vulnerable   │ ✅ SÍ (SCA)  │ Acto 3 (se remedia)      │
  └────────────┴───────────────────┴───────────────┴──────────────────────────┘
```
