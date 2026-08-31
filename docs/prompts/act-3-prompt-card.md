# ACTO 3 — Prompt Card para el SE

## Contexto

El pipeline encontró vulnerabilidades. El Change Advisor dijo Risk HIGH.
El SE usa Claude Code desde el IDE para remediar — informado por los findings concretos del pipeline.
La diferencia clave: en el Acto 1 el coding agent trabajó sin contexto de seguridad.
Ahora trabaja CON findings específicos.

## Pre-requisitos

1. Acto 2 completado — findings visibles
2. Claude Code con Harness MCP conectado
3. Branch `secops/ai-agentic-demo` checked out
4. PR #5 abierto

---

## PASO 1 — Pedir Findings Detallados al Pipeline (t=0:00)

> **Talk Track:** "El pipeline encontró los problemas. Ahora en vez de mandar al developer a leer logs manualmente, le pedimos a Claude Code que extraiga los findings y nos diga exactamente qué corregir."

### Prompt:

```
Use the Harness MCP tools to get the detailed security findings from
the latest execution of AI_SDLC_DemoBank. Cross-reference the SAST
findings with the Change Advisor review on PR #5.

Give me a prioritized remediation plan: which vulnerabilities are
the most critical, what files are affected, and what the fix should be.
```

### Resultado esperado:

Claude Code consolida:
- SAST findings (5 Medium) + Change Advisor (8 risk factors, HIGH)
- Prioriza: VULN-009 (PII Critical), VULN-010 (BOLA Critical), VULN-008 (Prompt Injection High)
- Identifica archivos: `app/routes/ai_assistant.py`, `app/routes/accounts.py`
- Propone plan de remediación

> **Talk Track:** "Sin salir del IDE: findings del SAST, del SCA, y del Change Advisor — consolidados y priorizados. El agente no está adivinando qué corregir. Tiene findings concretos."

---

## PASO 2 — Remediar las Vulnerabilidades (t=1:00)

> **Talk Track:** "Ahora le pedimos que corrija. Pero con instrucciones específicas basadas en los findings — no un vago 'hazlo seguro'."

### Prompt:

```
Based on the security findings from the pipeline, remediate the
following vulnerabilities in the codebase:

1. VULN-008 (Prompt Injection) in app/routes/ai_assistant.py:
   The user input is concatenated directly into the system prompt.
   Fix: sanitize input (strip control chars, limit to 500 chars),
   and separate user input from system prompt with clear delimiters.

2. VULN-009 (PII Exposure) in app/routes/ai_assistant.py:
   The _query_financial_context() function returns ALL account records
   including owner names and balances. The response includes
   financial_context and system_prompt_used fields.
   Fix: remove financial_context and system_prompt_used from the
   client response JSON. Only return response and session_id.

3. VULN-010 (BOLA/IDOR) in app/routes/accounts.py:
   The /<id>/details endpoint returns sensitive account data without
   any authorization check.
   Fix: add an X-Account-Owner header check — if the header doesn't
   match the account owner, return 403 Forbidden.

Update the DEMO VULNERABILITY comments to say "[REMEDIATED]" so
it's clear these were intentional vulnerabilities that were fixed.
Keep the code functional — the chat widget must still work.
```

### Resultado esperado (~60 segundos):

Claude Code modifica 2 archivos:
- `app/routes/ai_assistant.py` — input sanitization + response cleanup
- `app/routes/accounts.py` — auth check en details endpoint

> **Talk Track:**
>
> *"60 segundos. Tres vulnerabilidades corregidas. Pero la diferencia con el Acto 1 es crucial: este agente no está adivinando. Tiene findings del SAST que dicen 'línea 64, prompt injection'. Tiene el Change Advisor que dice 'PII exposure en el response body'."*
>
> *"AI informada por findings concretos es exponencialmente más precisa que AI trabajando a ciegas."*

---

## PASO 3 — Verificar las Correcciones (t=2:00)

> **Talk Track:** "Antes de commitear, le pedimos que verifique su propio trabajo contra los findings originales."

### Prompt:

```
Review the changes you just made against the original security findings.
For each vulnerability (VULN-008, VULN-009, VULN-010), confirm:
1. Is the vulnerability actually fixed?
2. Does the fix break any existing functionality?
3. Are there any edge cases the fix doesn't cover?
```

### Resultado esperado:

Claude Code revisa cada fix y confirma:
- VULN-008: Input sanitized, delimiters added ✅
- VULN-009: Response only returns `response` + `session_id` ✅
- VULN-010: 403 if X-Account-Owner doesn't match ✅
- Functionality: chat widget still works ✅

> **Talk Track:** "Self-review rápido. Pero recuerden — la verdadera validación viene del pipeline, no del mismo agente que escribió el fix."

---

## PASO 4 — Commit, Push y Re-trigger (t=2:30)

> **Talk Track:** "Commiteamos las correcciones. El pipeline se va a re-disparar automáticamente."

### Prompt:

```
Commit these security fixes and push to the PR branch. Use the message:
"fix(security): remediate VULN-008, VULN-009, VULN-010 — prompt injection,
PII exposure, BOLA from pipeline security findings"
```

### Resultado esperado:

- Commit pushed al branch del PR
- Pipeline re-triggered automáticamente
- Harness IDE Extension muestra la nueva ejecución

> **Talk Track:**
>
> *"Commit, push, y el pipeline ya se re-disparó. Los mismos scanners, el mismo Change Advisor, las mismas policies — pero sobre el código corregido."*
>
> *"Esto es un closed-loop: AI construye → pipeline valida → AI corrige → pipeline re-valida. Sin salir del IDE."*

---

## PASO 5 — Verificar Re-validación (t=3:30)

> **Talk Track:** "Esperemos que el pipeline termine y verifiquemos que las correcciones pasaron."

### Prompt (cuando el pipeline termine):

```
Check the latest pipeline execution for AI_SDLC_DemoBank.
Compare the security findings with the previous execution —
were the vulnerabilities we fixed resolved? Did any new issues appear?
```

### Resultado esperado:

Claude Code compara:
- Ejecución anterior: 5 SAST Medium, Change Advisor HIGH
- Ejecución nueva: findings reducidos, Change Advisor risk reduced

> **Talk Track (cierre):**
>
> *"Tres actos, tres agentes AI, cada uno con un rol:"*
> *"Acto 1 — el coding agent construye."*
> *"Acto 2 — el pipeline valida independientemente."*
> *"Acto 3 — otro agente corrige, informado por findings."*
>
> *"Ninguno confía ciegamente en el otro. El que escribe no valida. El que valida no corrige. El que corrige se re-valida."*
>
> *"Y todo desde el IDE."*

---

## Contingencia

Si Claude Code genera correcciones incorrectas:

```
The fixes don't look right. Let me show you the exact code in
app/routes/ai_assistant.py lines 47-87. Re-read the file and
fix only the specific vulnerabilities without changing the
overall structure.
```

Si el pipeline no se re-triggerea:

```
The pipeline didn't trigger automatically. Use the Harness MCP tools
to manually trigger AI_SDLC_DemoBank with the current PR branch.
```

---

## Checklist Pre-Demo

- [ ] Acto 2 completado — findings disponibles
- [ ] Claude Code respondiendo con Harness MCP
- [ ] Familiarizado con los 3 VULNs y sus archivos
- [ ] Branch limpio, sin conflictos
