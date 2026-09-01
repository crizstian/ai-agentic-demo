# ACTO 6 — Prompt Card para el SE

## Contexto

El ataque del Acto 5 fue detectado por Traceable en Monitor mode — toda la cadena registrada, pero nada bloqueado. El código vulnerable sigue en producción. Ahora el equipo de seguridad necesita responder.

**Cambio de tono:** De atacante a defensor. El SE cambia del terminal del hacker al dashboard de Harness. La audiencia ve cómo AI SRE orquesta la respuesta a un incidente de seguridad en segundos — no horas.

**Split screen:**
- Browser izquierda: Harness Platform (AI SRE + SCS)
- VS Code derecha: Claude Code + Harness IDE Extension

## Pre-requisitos

1. Harness Platform accesible con AI SRE habilitado
2. Runbook "Security Incident Response" configurado (Slack + Jira)
3. Jira connector configurado en Project Settings → Third-Party Integrations (AI SRE)
4. Pipeline con SBOM generation del Acto 3
5. Claude Code + Harness MCP disponibles
6. Traceable dashboard mostrando detecciones del Acto 5
7. Script `scripts/traceable-to-aisre.sh` listo para simular webhook

---

## PASO 1 — AI SRE: Incident + Runbook automático (t=0:00)

> **Talk Track:** "Traceable detectó toda la cadena de ataque. Pero detectar no es suficiente — alguien tiene que responder. En la mayoría de las empresas, eso toma horas. Con AI SRE: 12 segundos."

### Demostración (live):

**Paso 1a — Trigger el incidente:**

Ejecutar el script de simulación (Traceable → AI SRE):

```bash
./scripts/traceable-to-aisre.sh
```

> **Talk Track:** *"Traceable detectó el ataque y envía la alerta a Harness AI SRE."*

**Paso 1b — Mostrar el resultado en AI SRE UI:**

1. **Alerts tab** → nueva alerta P1: Critical de "Traceable Security Alerts"
2. **Incidents tab** → incidente auto-creado: "Attack Chain Detected: DemoBank API"
   - Severity: SEV1, Type: Security Incident
3. **Runbook timeline** → "Security Incident Response" ejecutado con 4 acciones automáticas:
   - Slack: `#security-incidents` notificado con contexto del ataque
   - Slack: canal `sec-inc-{ID}` creado para respuesta coordinada
   - Slack: contexto detallado posteado en el canal del incidente
   - Jira: ticket creado con severity, attack summary, next steps

**Paso 1c — Mostrar Slack y Jira:**

4. **Slack** → mostrar notificación en `#security-incidents` + canal creado
5. **Jira** → mostrar ticket con título `[SEV1] Security: Attack Chain Detected...`

### Prompt (para enriquecer con contexto):

```
Use Harness MCP to check the current incident status for the
DemoBank service. What incidents are open? What was the
last runbook execution?

Also check: what security findings exist for the DemoBank
pipeline? I want to correlate the runtime attack we just
demonstrated with the SAST findings from Act 3.
```

### Resultado esperado:

Claude Code via MCP muestra el estado del incidente y correlaciona con los findings del pipeline — conectando el ataque runtime (Act 5) con los findings de SAST (Act 3).

> **Talk Track:** *"AI SRE no es solo para pods caídos. Reacciona a ALERTAS de seguridad. 12 segundos. 4 acciones automáticas. El SRE llega al Slack y ya tiene: el incidente, el contexto del ataque, un canal de coordinación, y un ticket Jira — sin crear NADA manualmente."*

---

## PASO 2 — SCS Blast Radius: ¿Qué artifacts están en riesgo? (t=0:45)

> **Talk Track:** "El incidente está abierto, el Jira está creado. Ahora necesito entender el blast radius — ¿cuántos artifacts tienen riesgo OSS y qué componentes son los más críticos? Esto lo hago directo desde mi IDE con un prompt."

### Prompt (Claude Code + Harness MCP):

```
Use Harness MCP to assess the blast radius for the DemoBank
security incident:

1. Get the project-level OSS risk summary — how many artifacts
   have risks? How many EOL, unmaintained, or outdated components?
2. Check the artifact security posture for the harnessbank-demo
   container image — what vulnerabilities exist?
3. List the SBOM components for the latest harnessbank-demo
   artifact — show me direct dependencies and any with known
   vulnerabilities

I need to understand: how deep is the risk? Are there
components that need immediate remediation?
```

### Resultado esperado:

Claude Code via MCP muestra:
- **OSS Risk Summary**: 36 artifacts escaneados, 270 EOL components, 2155 unmaintained, 3296 outdated
- **harnessbank-demo image**: 3 derived-EOL components, 5 outdated, 3 unmaintained
- **SBOM components**: lista de dependencias directas con vulnerability counts
- Componentes que necesitan upgrade urgente

> **Talk Track:** *"Desde mi IDE, con un prompt, hice un análisis de blast radius via MCP — sin salir del código. 36 artifacts escaneados, 270 componentes end-of-life en el proyecto. Para DemoBank específicamente: 3 componentes EOL y 5 outdated. Esto no es un spreadsheet — es data real del SBOM generado en el pipeline."*

---

## PASO 3 — Componente vulnerable: buscar, remediar, crear PR (t=1:30)

> **Talk Track:** "El SBOM que generamos en el Acto 3 paga su inversión aquí. Voy a buscar un componente vulnerable, ver qué versión es segura, y crear un PR de remediación — todo desde Claude Code."

### Prompt:

```
Use Harness MCP to find and remediate a vulnerable component
in the DemoBank artifact:

1. Search across all artifacts: does "requests" appear in any
   SBOM? (use cross-artifact component search)
2. For any match, check the OSS risk enrichment — is it
   outdated? end-of-life? What's the latest safe version?
3. Get the remediation suggestion — what version should we
   upgrade to? What dependencies change?

If a safe upgrade exists, show me the recommended version
and what would change.
```

### Resultado esperado:

Claude Code via MCP ejecuta el flujo completo:
- **Cross-artifact search**: encuentra el componente en N artifacts
- **OSS enrichment**: muestra si está outdated/EOL, latest version
- **Remediation suggestion**: versión segura + dependency changes
- (Opcional) Crear un Remediation PR desde el mismo prompt

> **Talk Track:** *"SBOM del Acto 3 paga aquí. Un prompt: busqué el componente en todos los artifacts, verifiqué su riesgo OSS, y obtuve la versión segura con el análisis de impacto. Puedo crear un PR de remediación directo desde aquí — sin abrir Jira, sin abrir GitHub, sin salir de mi IDE. Sin SBOM: 2-5 días de auditoría manual. Con SBOM + MCP: 8 segundos."*

---

## PASO 4 — OPA Policy: Que no vuelva a pasar (t=2:15)

> **Talk Track:** "El bombero apagó el fuego. El inspector revisó el edificio. Ahora necesitamos un nuevo código de construcción — una regla que prevenga que el mismo patrón vuelva a producción."

### Prompt:

```
I need to create an OPA policy for our Harness pipelines
that prevents AI endpoints without authentication from
reaching production.

The policy should:
1. Check security scan results in the pipeline
2. Block if prompt injection vulnerability is detected
3. Block if any /api/ai/* endpoint lacks authentication
4. Apply org-wide to all pipelines

Write the Rego policy and explain how it integrates with
Harness pipeline governance.
```

### Resultado esperado:

Claude Code genera el policy .rego:

```rego
package pipeline

deny[msg] {
  input.step.type == "SecurityTests"
  findings := input.step.output.findings
  count([f | f := findings[_];
    f.category == "prompt-injection"]) > 0
  msg = "Prompt injection vulnerability detected.
         Pipeline blocked per SEC-POL-042."
}

deny[msg] {
  input.step.type == "SecurityTests"
  findings := input.step.output.findings
  count([f | f := findings[_];
    f.category == "missing-auth";
    contains(f.endpoint, "/api/ai/")]) > 0
  msg = "AI endpoint without authentication detected.
         All /api/ai/* endpoints require auth. SEC-POL-042."
}
```

> **Talk Track:** *"Post-incident governance: aprender del incidente y codificarlo en una regla. Si un security scan detecta prompt injection o un AI endpoint sin auth, el pipeline se bloquea. No es un documento que se olvida — es una regla que se ejecuta en CADA pipeline run. Bombero → Inspector → Código de construcción."*

---

## PASO 5 — Cierre: De la detección a la prevención (t=2:45)

> **Talk Track:**

> *"Recapitulemos: Traceable DETECTÓ toda la cadena de ataque en Monitor mode. AI SRE RESPONDIÓ en 12 segundos — 4 acciones automáticas: Slack notificado, canal de incidente creado, contexto posteado, Jira ticket creado. El Remediation Tracker IDENTIFICA todos los artifacts afectados en todos los environments. SBOM muestra el BLAST RADIUS — qué otros servicios tienen la misma vulnerabilidad. Y OPA PREVIENE que el mismo patrón vuelva a producción.*
>
> *Todo esto — detección, respuesta, tracking, análisis, prevención — en una plataforma. Cada paso tiene UI, API, y audit trail.*
>
> *Pero hay una pregunta pendiente: el código está securizado, las APIs están monitoreadas... ¿pero qué hay del AI mismo? Los modelos, los MCP tools, los prompts — ¿quién los gobierna?"*

---

## Contingencia

**Si AI SRE no responde al webhook:**
Ejecutar el script con debug: `bash -x ./scripts/traceable-to-aisre.sh` y verificar HTTP status. Si devuelve 200 pero no crea alerta, verificar que la integración "Traceable Security Alerts" y la alert rule estén activas.

**Si Jira no crea ticket:**
Verificar el Jira connector en Project Settings → Third-Party Integrations (AI SRE). El runbook execution log muestra el error específico. Continuar con Slack-only y mencionar Jira narrativamente.

**Si AI SRE no está configurado**, usar el flujo narrativo:

```
Based on the attack chain we just executed in Act 5,
walk me through what an ideal incident response would
look like using Harness AI SRE, Remediation Tracker,
SBOM analysis, and OPA policies.

Format each step as:
- What triggers it
- What it does automatically
- What the human reviews
- Time saved vs manual process
```

**Si el Remediation Tracker no está disponible via MCP**, mostrar el SBOM del pipeline (que sí se generó en Acto 3) y la OPA policy como archivo .rego.

---

## Checklist Pre-Demo

- [ ] Harness Platform accesible
- [ ] AI SRE habilitado con alert rule para "Traceable Security Alerts"
- [ ] Runbook "Security Incident Response" configurado: Slack (3 actions) + Jira (1 action)
- [ ] Jira connector configurado en Project Settings → Third-Party Integrations (AI SRE)
- [ ] `scripts/traceable-to-aisre.sh` probado y funcionando (HTTP 200/201)
- [ ] SBOM del Acto 3 disponible en pipeline results
- [ ] OPA policy .rego preparado
- [ ] Claude Code + Harness MCP respondiendo
- [ ] Harness IDE Extension visible en VS Code

---

## Transición al Acto 7

> **Talk Track:**
>
> *"Shift Left corrigió el código. Shield Right detectó el ataque. AI SRE respondió. El Remediation Tracker confirma que los environments se van patcheando. OPA previene recurrencia.*
>
> *Pero estamos en Monitor mode — Traceable VE todo pero no BLOQUEA nada. Y DemoBank tiene un AI assistant con un modelo, un MCP tool, y datos financieros. ¿Quién activa la protección? ¿Quién descubre los AI components? ¿Quién los gobierna?*
>
> *Acto 7: activamos Block mode y conocemos AIBOM — AI Bill of Materials."*
