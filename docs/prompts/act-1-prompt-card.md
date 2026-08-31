# ACTO 1 — Prompt Card para el SE

## Estado Inicial (Reset Point)

El codebase tiene:
- DemoBank funcionando con accounts, transfers, statements, admin, fx
- Backend AI assistant (`app/routes/ai_assistant.py`) con rutas `/api/ai/chat` y `/api/ai/status` — **ya existen pero SIN interfaz visual**
- 3 vulnerabilidades silenciosas plantadas en el backend (VULN-008, 009, 010)
- 4 vulnerabilidades clásicas pre-existentes (SQL injection, command injection, XSS, CORS)
- Dependencia vulnerable `requests==2.25.1`
- **NO hay chat widget en el dashboard** — esto es lo que el developer construye

## Pre-requisitos

1. VS Code abierto con Claude Code extension
2. Harness IDE Extension visible en sidebar
3. Branch `secops/ai-agentic-demo` checked out
4. Harness MCP conectado (verificar con un query rápido)

---

## PASO 1 — Contexto SDLC via Harness MCP (t=0:30)

> **Talk Track:** "Antes de codear, el developer tiene algo que otros coding agents no tienen: contexto del SDLC completo. No solo ve el repo — ve pipelines, findings, deploys."

### Prompt MCP:

```
Use the Harness MCP tools to give me context on the DemoBank service:
what's the current deployment status, any open security findings,
and the last pipeline execution result.
```

> **Talk Track post-respuesta:** "En un solo prompt, sin abrir browser, sin preguntarle a DevOps: qué está deployado, qué vulnerabilidades existen, cómo fue el último pipeline. Eso es Harness MCP."

---

## PASO 2 — AI Coding Agent Construye el Feature (t=1:30)

> **Talk Track:** "El negocio quiere que DemoBank tenga un AI banking assistant — un chat donde los clientes pregunten sobre sus cuentas en lenguaje natural. Ya tenemos el backend API listo. Ahora el developer necesita construir la interfaz. Vean la velocidad."

### Prompt Principal:

```
Necesito agregar un AI Chat Assistant widget al dashboard de DemoBank.
Revisa la aplicación Flask actual — el dashboard está en
app/templates/dashboard.html, los estilos en app/static/styles.css,
y el JS en app/static/app.js.

Requerimientos:
1. Un botón flotante en la esquina inferior derecha del dashboard
   con icono de chat (puede ser emoji o SVG simple)
2. Al hacer click, abre un panel de chat con:
   - Header con título "AI Banking Assistant" y botón de cerrar
   - Área de mensajes con scroll
   - Input de texto con botón de enviar
3. Los mensajes del usuario aparecen alineados a la derecha (azul)
   y las respuestas del AI a la izquierda (gris)
4. Al enviar un mensaje, hacer POST a /api/ai/chat con
   { "message": "...", "session_id": "web-client" }
   y mostrar el campo "response" de la respuesta JSON
5. Mostrar un mensaje de bienvenida al abrir el chat:
   "Hello! I'm your AI banking assistant.
   Ask me about your accounts, transactions, or exchange rates."
6. El widget debe verse profesional, integrado con el diseño
   existente del dashboard (colores: #1a2332, #3182ce, #63b3ed)
```

### Resultado esperado (~90 segundos):

Claude Code modifica 3 archivos:
- `app/templates/dashboard.html` — agrega el widget HTML
- `app/static/styles.css` — agrega estilos del chat widget
- `app/static/app.js` — agrega lógica de chat (fetch a `/api/ai/chat`)

### Lo que la audiencia NO sabe:

El widget se conecta a `/api/ai/chat` que tiene 3 vulnerabilidades silenciosas:
- **VULN-008 (Prompt Injection):** el input del usuario se concatena directo al system prompt
- **VULN-009 (PII Leak):** la respuesta incluye datos financieros raw de TODOS los clientes
- **VULN-010 (BOLA/IDOR):** endpoint `/api/accounts/<id>/details` sin auth check

El coding agent construye un widget perfecto que se conecta a un backend vulnerable. No cuestiona la seguridad del API al que se conecta. Es como construir una puerta bonita en una pared sin cerradura.

> **Talk Track post-build:** "En menos de 2 minutos: un chat widget completo, integrado visualmente, conectado al backend. El código se ve profesional. Se ve correcto. Un developer experimentado lo revisaría y diría 'esto está bien'."

---

## PASO 3 — Crear el PR (t=3:00)

> **Talk Track:** "El developer crea el PR. El coding agent genera una descripción completa."

### Prompt PR:

```
Create a PR for these changes. Title: "feat: add AI banking assistant
chat widget to dashboard". Include a summary of what was added and
how to test it.
```

### Resultado esperado:

PR creado con:
- Título: `feat: add AI banking assistant chat widget to dashboard`
- 3 archivos modificados
- Descripción con instrucciones de test

---

## PASO 4 — El Handoff (t=3:30)

> **Talk Track (momento clave):**
>
> *"El feature está listo. El PR está creado. El coding agent hizo su trabajo en minutos."*
>
> **[pausa]**
>
> *"Pero aquí hay algo fundamental: ¿Puedo confiar en que este código es correcto?"*
>
> *"El coding agent me dice que sí — pero él lo escribió. Si le pregunto al mismo modelo '¿tu código es seguro?', me va a decir que sí. Siempre."*
>
> *"El que escribe el código NO puede ser el que lo valida. Necesitas un validador independiente."*
>
> *"Eso es exactamente lo que hace Harness. Y ya empezó."*

Señalar la Harness IDE Extension: el pipeline ya se triggeó automáticamente con el PR.

---

## Contingencia

Si Claude Code genera algo muy diferente a lo esperado o tarda demasiado:

```bash
# Checkout del branch con el feature pre-construido
git checkout demo/completed -- app/templates/dashboard.html app/static/styles.css app/static/app.js
```

> **Talk Track de recovery:** "El coding agent generó este PR. Veamos qué contiene."

---

## Checklist Pre-Demo

- [ ] Branch `secops/ai-agentic-demo` limpio (sin chat widget)
- [ ] `app/templates/dashboard.html` sin widget de chat
- [ ] DemoBank corriendo en `http://demobank-e2e.selatam.harness-demo.site`
- [ ] Newman generando tráfico (E-W + N-S)
- [ ] Traceable agents conectados y descubriendo APIs
- [ ] Harness MCP tools respondiendo en Claude Code
- [ ] Harness IDE Extension mostrando pipeline status
- [ ] PR trigger configurado en pipeline `AI_SDLC_DemoBank`
