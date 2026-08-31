# ACTO 2 — Prompt Card para el SE

## Contexto

El PR del Acto 1 triggeró automáticamente el pipeline `AI_SDLC_DemoBank`.
El SE permanece en el IDE y usa Harness MCP + IDE Extension para ver qué encontró el pipeline — sin abrir browser.

## Pre-requisitos

1. PR #5 creado (resultado del Acto 1)
2. Pipeline ejecutándose o completado (auto-triggered por PR)
3. Harness IDE Extension mostrando la ejecución en el sidebar
4. Claude Code con Harness MCP conectado

---

## PASO 1 — Verificar Pipeline via IDE (t=0:00)

> **Talk Track:** "El PR se creó y Harness ya reaccionó. Sin que yo hiciera nada, el pipeline arrancó. Puedo verlo aquí en la IDE Extension. Pero quiero más detalle — voy a preguntarle al pipeline directamente."

### Prompt:

```
Use the Harness MCP tools to check the latest pipeline execution for
AI_SDLC_DemoBank in project CristianRamirez, org sandbox.
Show me: execution status, which stages ran, and how long it took.
```

### Resultado esperado:

Claude Code responde con:
- Execution #23, status: Success
- Build stage: Success (4m 39s) — PR Validation path
- Deploy DemoBank: Skipped (solo en merge)
- Deploy MCP: Skipped (solo en merge)

> **Talk Track:** "Sin abrir Harness en el browser — desde el IDE le pregunto al pipeline. Build exitoso, deploys saltados porque es un PR, no un merge. Contexto completo en segundos."

---

## PASO 2 — Obtener Security Findings (t=1:00)

> **Talk Track:** "Ahora la pregunta importante: ¿qué encontraron los security scanners?"

### Prompt:

```
Get the security scan results from the latest execution of pipeline
AI_SDLC_DemoBank. I want to know:
1. How many SAST findings and their severities
2. SCA findings count and severities
3. Secrets detection results
4. Did the Security Remediator agent run?
```

### Resultado esperado:

```
Semgrep SAST: 5 findings (all Medium)
Harness SCA: 12 findings (5 Critical, 4 High, 2 Medium, 1 Low)
Gitleaks: 0 leaks found
Security Remediator: Skipped (condition: HIGH > 0, actual: 0 HIGH)
```

> **Talk Track:** "5 SAST findings a nivel Medium, 12 en supply chain con 5 críticas — y cero secretos expuestos. Tres scanners, tres perspectivas, desde el IDE."

---

## PASO 3 — Leer el Change Advisor Review (t=1:45)

> **Talk Track:** "Los scanners deterministas encontraron patrones conocidos. Pero las vulnerabilidades más sutiles — prompt injection, PII exposure, BOLA — esas requieren razonamiento. Para eso está el Change Advisor."

### Prompt:

```
Check PR #5 on the ai-agentic-demo repo. Show me the Change Advisor
review comment — I want to see what risk factors it identified and
what its overall risk assessment was.
```

### Resultado esperado:

Claude Code muestra el comentario del Change Advisor:
- **Risk: HIGH** — 8 factores de riesgo
- `/api/ai/chat` retorna PII raw de TODAS las cuentas sin auth
- System prompt expuesto en el response body
- `/api/accounts/<id>/details` — BOLA sin autenticación
- SSRF surface via `MCP_FINANCIAL_DATA_URL`

> **Talk Track (momento clave):**
>
> *"El coding agent construyó el widget en 90 segundos. Se ve perfecto."*
>
> **[pausa — señalar la respuesta]**
>
> *"El Change Advisor — un agente independiente — dice: Risk HIGH. El endpoint /api/ai/chat devuelve datos financieros de TODOS los clientes. El system prompt completo se expone en la respuesta. Hay un endpoint BOLA."*
>
> *"¿Por qué el coding agent no detectó esto? Porque hizo lo que le pedimos — construir un widget. No auditar el backend. Es como pedirle al arquitecto que diseñe una puerta hermosa en una pared sin cerradura."*
>
> *"El que escribe el código NO puede ser el que lo valida."*

---

## PASO 4 — Consultar Governance Policies (t=2:45)

> **Talk Track:** "Y no solo agentes AI — también hay governance policies evaluando cada ejecución."

### Prompt:

```
What governance policies were evaluated in the latest pipeline
execution? Show me which ones passed and which ones flagged warnings.
```

### Resultado esperado:

```
SecOps Demo Gates (warning):
├── Block Unprotected AI Endpoints     ⚠️
├── No Critical Findings               ⚠️
├── SLSA Attestation Required          ⚠️
└── Security Scan Required             ⚠️
```

> **Talk Track:** "Cuatro policies OPA como código — verifican automáticamente si hay AI endpoints sin auth, vulnerabilidades críticas, attestation SLSA, y que los security scans se hayan ejecutado. En modo warning ahora, en producción serían blockers."

---

## PASO 5 — Cierre del Acto (t=3:30)

> **Talk Track:**
>
> *"Recapitulemos. Todo desde el IDE, sin abrir un browser:"*
>
> *"1. Vi que el pipeline se auto-triggereó con el PR"*
> *"2. Consulté los security findings: 5 SAST, 12 SCA, 0 secretos"*
> *"3. Leí el Change Advisor review: Risk HIGH, 8 factores"*
> *"4. Verifiqué las governance policies"*
>
> *"El coding agent dijo: el código está listo. El pipeline dice: hay 8 problemas de seguridad. ¿A quién le creemos? Al pipeline. Siempre."*
>
> *"Ahora la pregunta es: ¿quién corrige todo esto?"*

---

## Contingencia

Si el pipeline no ha terminado cuando llegas al Paso 1:

```
Show me the execution steps that have completed so far in the running
pipeline AI_SDLC_DemoBank. What's currently in progress?
```

Si el Change Advisor no publicó comentario en el PR:

```
Diagnose the latest execution of AI_SDLC_DemoBank — show me the
Change Advisor step logs. What did it find?
```

---

## Checklist Pre-Demo

- [ ] Pipeline `AI_SDLC_DemoBank` completado (triggered por PR del Acto 1)
- [ ] Change Advisor comment visible en PR #5
- [ ] Harness IDE Extension mostrando la ejecución
- [ ] Claude Code con Harness MCP respondiendo queries
