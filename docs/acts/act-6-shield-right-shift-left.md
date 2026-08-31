# ACTO 6: "Shield Right + Shift Left — Respuesta a Machine Speed"

## Qué hace el acto

El ataque del Acto 5 fue contenido — virtual patches activos, threat actor bloqueado. Pero el código vulnerable sigue en producción.

Este acto muestra el flujo REAL de incident response que un equipo de seguridad haría usando Harness — paso a paso, con features productizados:

1. **AI SRE** recibe la alerta de seguridad del Runtime Protection Agent → crea incidente → ejecuta runbook automáticamente
2. **Remediation Tracker** (SCS) se crea vía API desde el runbook → identifica TODOS los artifacts afectados en prod y pre-prod
3. **SBOM blast radius** — qué otros servicios usan los mismos componentes vulnerables
4. **OPA Policy** — nueva governance rule que previene que el mismo patrón vuelva a producción

Cada paso es un feature real de Harness con UI, API, y audit trail.

---

## Quién hace qué — Los 4 personas

| Persona | Qué ve | Qué hace | Herramienta Harness |
|---------|--------|----------|-------------------|
| **SRE / On-call** | Notificación en Slack + PagerDuty. Incident bridge en Zoom. | Verifica que el runbook ejecutó correctamente. Confirma virtual patches activos en WAAP. | AI SRE (incident + runbook) |
| **Security Analyst** | Remediation Tracker con lista de artifacts afectados. Blast radius con servicios en riesgo. | Revisa blast radius. Valida que la OPA policy cubra el patrón. Prioriza remediación por environment (prod primero). | SCS (Remediation Tracker + SBOM) |
| **Developer** | Jira ticket asignado con contexto del incidente + CVE. | Revisa el fix (PR generado por Remediation Agent o manual). Aprueba el PR. | Jira (creado desde Remediation Tracker) |
| **DevOps / Platform** | Pipeline triggered. Governance gates. | Verifica que el fix pase SAST, OPA, SLSA. Monitorea canary deploy. | CI/CD Pipeline + OPA |

---

## Flujo real — Paso a paso

### Paso 1: AI SRE — Incident + Runbook automático

**Qué pasa en Harness:**

El Runtime Protection Agent (WAAP) genera una alerta cuando detecta la cadena de ataque del Acto 5. Esta alerta llega a AI SRE como una **Alert Rule** configurada.

AI SRE crea un incidente automáticamente con tipo **"Security Incident"** y ejecuta un runbook pre-configurado.

```
┌─────────────────────────────────────────────────────────────────┐
│ AI SRE — INCIDENT CREATED                                       │
│                                                                 │
│ Title: "Security: Attack chain detected on DemoBank"            │
│ Type: Security Incident                                         │
│ Severity: SEV1                                                  │
│ Service: demobank-api                                            │
│ Status: Investigating                                           │
│                                                                 │
│ ─── RUNBOOK: security-incident-response ───                     │
│                                                                 │
│ Trigger: incident.severity in [SEV0, SEV1]                      │
│          AND incident.type equals "Security Incident"           │
│                                                                 │
│ Step 1: ✅ Slack: Post Message                                  │
│         → #security-incidents                                   │
│         → "🔴 Security Incident: Attack chain detected on       │
│            DemoBank. Virtual patches active. Investigating."     │
│                                                                 │
│ Step 2: ✅ Page Service                                         │
│         → security-oncall (PagerDuty)                           │
│                                                                 │
│ Step 3: ✅ Jira: Create Issue                                   │
│         → Project: SEC, Type: Incident                          │
│         → "Security incident: 3 AI-specific vulns exploited     │
│            on DemoBank. VULN-008, 009, 010."                    │
│                                                                 │
│ Step 4: ✅ HTTP Request → SCS Remediation Tracker API           │
│         → POST /v1/orgs/{org}/projects/{project}/remediations   │
│         → Component: ai_assistant module                        │
│         → Severity: CRITICAL                                    │
│         → Condition: remove versions < 2.5.1                    │
│                                                                 │
│ Step 5: ✅ Zoom: Create Meeting                                 │
│         → "Security Incident Bridge — DemoBank"                 │
│         → Participants: security-oncall, sre-oncall              │
│                                                                 │
│ Step 6: ✅ Slack: Post Message                                  │
│         → #security-incidents                                   │
│         → "Runbook complete. Remediation tracker created.        │
│            Incident bridge: {{zoom.join_url}}"                   │
│                                                                 │
│ Runbook completed in 12 seconds. 0 manual steps.                │
└─────────────────────────────────────────────────────────────────┘
```

**Lo que es REAL aquí:**
- AI SRE runbooks con trigger por incident type + severity: **documentado**
- Actions: Slack, PagerDuty (Page Service), Jira, HTTP Request, Zoom: **todas documentadas**
- HTTP Request action llamando a la API de Remediation Tracker: **API real** (`POST /v1/.../remediations`)
- Mustache variables (`{{incident.title}}`, `{{incident.severity}}`): **documentado**
- Incident types incluyen "Security Incident": **documentado**

**Talk track del SE:**

> *"AI SRE no es solo para pods caídos. Reacciona a ALERTAS — cualquier alerta. Aquí, el Runtime Protection Agent detectó un ataque y generó una alerta de seguridad. AI SRE creó el incidente y ejecutó el runbook en 12 segundos.*
>
> *6 pasos automáticos: notificó en Slack, paginó al equipo de seguridad, creó el ticket en Jira, creó un Remediation Tracker en SCS para trackear qué artifacts están afectados, abrió el incident bridge en Zoom, y posteó el resumen.*
>
> *¿Cuánto toma su proceso de incident response? ¿Minutos? ¿Horas? Aquí fueron 12 segundos. Y el runbook lo pueden ver, editar, y auditar — no es un script escondido."*

---

### Paso 2: Remediation Tracker — "¿Qué artifacts están afectados?"

**Qué pasa en Harness:**

El Remediation Tracker fue creado automáticamente por el runbook (Step 4). Ahora SCS escanea todos los artifacts deployed y muestra cuáles usan el componente vulnerable.

```
┌─────────────────────────────────────────────────────────────────┐
│ SCS — REMEDIATION TRACKER                                       │
│                                                                 │
│ Tracker: SEC-RT-001                                             │
│ Status: In-Progress                                             │
│ Component: ai_assistant (demobank)                              │
│ Severity: CRITICAL                                              │
│ Condition: Remove versions < 2.5.1                              │
│ Target date: 2026-09-01                                         │
│ Contact: security-team@demobank.com                              │
│                                                                 │
│ ─── AFFECTED ARTIFACTS ───                                      │
│                                                                 │
│ Artifact                    │ Environment │ Status    │ Ticket   │
│ ────────────────────────────┼─────────────┼───────────┼──────── │
│ demobank-api:v2.5.0         │ prod        │ ⏳ Pending │ SEC-421 │
│ demobank-api:v2.5.0         │ staging     │ ⏳ Pending │ —       │
│ demobank-api:v2.5.0-rc1     │ dev         │ ⏳ Pending │ —       │
│                                                                 │
│ Total artifacts: 1                                              │
│ Total environments: 3 (1 prod, 1 pre-prod, 1 dev)              │
│ Pending: 3 | Remediated: 0                                      │
│                                                                 │
│ [Create Ticket] [Exclude Artifact]                              │
│                                                                 │
│ Remediation Progress: ██░░░░░░░░ 0%                             │
└─────────────────────────────────────────────────────────────────┘
```

**Lo que es REAL aquí:**
- Remediation Tracker escanea artifacts deployed automáticamente: **documentado**
- Muestra environments (prod/pre-prod): **documentado**
- Status Pending/Remediated con tracking real-time: **documentado**
- Crea Jira tickets por artifact: **documentado**
- Se cierra automáticamente cuando todos los environments están patcheados: **documentado**
- Detecta nuevos deploys del artifact afectado (marca "new"): **documentado**

**Talk track del SE:**

> *"El Remediation Tracker no es un spreadsheet. Es un tracker que escanea TODOS los artifacts deployed y te muestra exactamente dónde está el componente vulnerable — en qué environment, en qué versión.*
>
> *Aquí: DemoBank v2.5.0 está en prod, staging, y dev. Cada uno necesita remediación. Puedo crear un Jira ticket por artifact directamente desde el tracker. Y cuando el fix se deploye, el tracker se actualiza automáticamente — cuando todos los environments estén patcheados, se cierra solo."*

---

### Paso 3: SBOM Blast Radius — "¿Qué otros servicios están en riesgo?"

**Qué pasa en Harness:**

El SBOM generado en el Acto 3 (47 dependencias catalogadas en pipeline #849) se usa para analizar blast radius. El Security Analyst revisa qué otros servicios usan los mismos componentes.

```
┌─────────────────────────────────────────────────────────────────┐
│ SCS — SBOM ANALYSIS                                             │
│                                                                 │
│ Source: DemoBank v2.5.0 (SBOM generated pipeline #849)          │
│                                                                 │
│ ─── DEPENDENCY: requests ───                                    │
│                                                                 │
│ DemoBank:          v2.32.3 ✅ (upgraded in Act 3)               │
│ payment-service:   v2.32.3 ✅ Safe                              │
│ notification-svc:  v2.32.3 ✅ Safe                              │
│ legacy-api:        v2.25.1 ⚠️ CVE-2023-32681 (HTTP header inj) │
│                                                                 │
│ ─── SBOM QUALITY SCORE ───                                      │
│                                                                 │
│ DemoBank v2.5.0: 7.2/10                                         │
│ Categories: Completeness ✅ | Licensing ⚠️ | Supplier info ✅    │
│                                                                 │
│ ─── SBOM POLICY VIOLATIONS ───                                  │
│                                                                 │
│ Deny list match: requests < 2.31.0                              │
│   → legacy-api violates policy                                  │
│   → Action: create separate Remediation Tracker for legacy-api  │
│                                                                 │
│ Components analyzed: 47                                          │
│ Time: 8 seconds                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Lo que es REAL aquí:**
- SBOM generation en pipeline con quality scoring (0-10): **documentado**
- SBOM Policy Enforcement con deny lists por versión/componente: **documentado**
- SBOM drift detection: **documentado**
- Formatos CycloneDX y SPDX: **documentado**
- Se puede crear un Remediation Tracker adicional para legacy-api: **documentado**

**Talk track del SE:**

> *"El SBOM del Acto 3 paga su inversión aquí. 47 dependencias catalogadas. En 8 segundos sabemos que legacy-api todavía usa requests 2.25.1 — el mismo CVE que corregimos en DemoBank.*
>
> *Y miren: la SBOM policy tiene una deny list que dice 'requests menor a 2.31.0 está prohibido.' Legacy-api la viola. Desde aquí puedo crear otro Remediation Tracker directamente para ese servicio.*
>
> *Sin SBOM: esto toma 2-5 días de auditoría manual. Con SBOM y SBOM policies: 8 segundos."*

---

### Paso 4: OPA Policy — "Que no vuelva a pasar"

**Qué pasa en Harness:**

El Security Analyst crea o activa una OPA policy que evalúa los scan results del pipeline. Si un artefacto tiene AI endpoints sin auth o vulnerabilidades de prompt injection, el pipeline se bloquea.

```
┌─────────────────────────────────────────────────────────────────┐
│ HARNESS — OPA POLICY                                            │
│                                                                 │
│ Policy: block-unprotected-ai-endpoints                          │
│ Scope: Organization-wide                                        │
│ Enforcement: Error (blocks pipeline)                            │
│                                                                 │
│ # block_unprotected_ai_endpoints.rego                           │
│                                                                 │
│ package pipeline                                                │
│                                                                 │
│ deny[msg] {                                                     │
│   input.step.type == "SecurityTests"                            │
│   findings := input.step.output.findings                        │
│   count([f | f := findings[_];                                  │
│     f.category == "prompt-injection"]) > 0                      │
│   msg = "Prompt injection vulnerability detected.               │
│          Pipeline blocked per SEC-POL-042."                     │
│ }                                                               │
│                                                                 │
│ deny[msg] {                                                     │
│   input.step.type == "SecurityTests"                            │
│   findings := input.step.output.findings                        │
│   count([f | f := findings[_];                                  │
│     f.category == "missing-auth";                               │
│     contains(f.endpoint, "/api/ai/")]) > 0                     │
│   msg = "AI endpoint without authentication detected.           │
│          All /api/ai/* endpoints require auth. SEC-POL-042."    │
│ }                                                               │
│                                                                 │
│ Applied to: 12 pipelines across 3 projects                      │
│ Enforcement starts: next pipeline execution                     │
└─────────────────────────────────────────────────────────────────┘
```

**Lo que es REAL aquí:**
- OPA policies que evalúan scan results del pipeline: **documentado**
- Enforcement modes (Error/Warning): **documentado**
- Scope org-wide: **documentado**
- Rego language para policies: **documentado**

**Talk track del SE:**

> *"Virtual patching protege ahora. El Remediation Tracker trackea el progreso. Pero ¿cómo evitamos que otro developer — o otro coding agent — commita el mismo error?*
>
> *OPA policy. Si un security scan detecta prompt injection o un AI endpoint sin auth, el pipeline se bloquea. No llega a producción.*
>
> *Esto es post-incident governance: aprender del incidente y codificarlo en una policy. No es un documento que se olvida — es una regla que se ejecuta en CADA pipeline run."*

---

## El ciclo completo — Qué hace cada persona y cuándo

```
TIMELINE REAL DE INCIDENT RESPONSE

t=0        WAAP detecta cadena de ataque (Act 5)
           → Virtual patches aplicados automáticamente
           → Alerta enviada a AI SRE

t+12seg    AI SRE RUNBOOK EJECUTA:
           ├── Slack: #security-incidents notificado
           ├── PagerDuty: security-oncall paginado
           ├── Jira: SEC-421 creado
           ├── SCS: Remediation Tracker SEC-RT-001 creado
           ├── Zoom: incident bridge abierto
           └── Slack: resumen posteado

           → SRE llega al Slack channel.
             Ya tiene: evidencia, tickets, tracker, bridge.
             No tuvo que crear NADA manualmente.

t+1min     SECURITY ANALYST revisa:
           ├── Remediation Tracker: 1 artifact, 3 environments
           ├── SBOM blast radius: legacy-api también afectado
           ├── Crea Remediation Tracker adicional para legacy-api
           └── Crea/activa OPA policy contra el patrón

t+5min     DEVELOPER recibe Jira ticket SEC-421:
           ├── Contexto: qué vulns, qué endpoints, qué pasó
           ├── Revisa fix PR (Remediation Agent o manual)
           └── Aprueba PR

t+15min    DEVOPS/PIPELINE:
           ├── Pipeline re-corre: SAST ✅, OPA ✅, SLSA ✅
           ├── Canary deploy + CV: healthy
           └── Fix deployed: DemoBank v2.5.1

t+16min    SCS REMEDIATION TRACKER se actualiza automáticamente:
           ├── prod: ✅ Remediated (v2.5.1 deployed)
           ├── staging: ⏳ Pending (siguiente deploy)
           └── Progress: ██████░░░░ 33%

t+30min    Staging y dev deployados.
           Tracker: ██████████ 100% → Status: DONE
           Virtual patches removidos (protección ahora del código).
```

---

## WOW del acto

> **"AI SRE respondió a un ataque de SEGURIDAD — no un pod caído, un ATAQUE — en 12 segundos. 6 acciones automáticas: Slack, PagerDuty, Jira, Remediation Tracker, Zoom, resumen.**
>
> **El Remediation Tracker identificó automáticamente que DemoBank v2.5.0 está en 3 environments. Cuando el fix se deploya, el tracker se actualiza solo. Cuando todos los environments están patcheados, se cierra solo.**
>
> **SBOM blast radius: 8 segundos para saber que legacy-api tiene el mismo CVE. OPA policy: ningún AI endpoint sin auth vuelve a pasar a producción.**
>
> **Cada paso es un feature real de Harness. Cada paso tiene UI, API, y audit trail. Nada es aspiracional. Todo se puede demostrar."**

---

## Diferenciación competitiva

| Capability | Harness | Palo Alto/Wiz | Snyk | Salt/Noname |
|-----------|---------|---------------|------|-------------|
| AI SRE runbook (security trigger) | ✅ Documentado | ❌ | ❌ | ❌ |
| Remediation Tracker (track across environments) | ✅ Con Live Tracking | ❌ | Parcial | ❌ |
| SBOM blast radius + policy enforcement | ✅ Con quality scoring | Parcial | ✅ | ❌ |
| OPA policy (org-wide pipeline governance) | ✅ Rego policies | ❌ | ❌ | ❌ |
| Virtual patching (protection policies) | ✅ WAAP | ❌ | ❌ | ❌ |
| All on ONE platform | ✅ | ❌ (need multiple) | ❌ (need multiple) | ❌ |

---

## Armadura contra CISOs hostiles

### CISO: "Ya tenemos incident response."

> *"¿Cuántos pasos son manuales? AI SRE ejecutó 6 pasos en 12 segundos: Slack, PagerDuty, Jira, Remediation Tracker, Zoom, resumen. Cero manuales. Y el Remediation Tracker sigue trackeando automáticamente hasta que todos los environments estén patcheados — sin que nadie lo actualice manualmente."*

### CISO: "No necesito otro tracker. Tengo Jira."

> *"El Remediation Tracker no reemplaza Jira — lo complementa. Jira trackea el TRABAJO (quién hace qué). El Remediation Tracker trackea el ESTADO REAL: ¿el artifact vulnerable ya se removió de producción? ¿Y de staging? ¿Y de dev? Se actualiza automáticamente con cada deploy. Jira no hace eso."*

### CISO: "Virtual patching es un parche temporal."

> *"Correcto. Y eso es exactamente lo que necesitas PRIMERO. El Remediation Tracker trackea cuándo el fix real se deploya. Cuando se completa, las protection policies se ajustan. El parche no es permanente — es protección temporal con fecha de expiración automatizada."*

---

## Cómo conecta al Acto 7

> *"Shift Left corrigió el código. Shield Right protegió las APIs. AI SRE orquestó la respuesta. El Remediation Tracker confirmó que todos los environments están patcheados.*
>
> *Pero DemoBank tiene un AI assistant que usa un modelo, hace llamadas a un MCP tool, y procesa datos financieros. ¿Quién monitorea los prompts? ¿Quién descubre qué AI components tenemos?*
>
> *En Julio 2026, Harness lanzó AIBOM — AI Bill of Materials. Igual que el SBOM descubre dependencias de software, AIBOM descubre modelos, frameworks, agents, datasets, y herramientas MCP. Automáticamente. En CycloneDX format.*
>
> *El código está securizado. Las APIs están securizadas. Ahora: ¿qué hay del AI mismo?"*

---

## Nota para el SE: AIBOM como teaser del Acto 7

El AIBOM (AI Bill of Materials) lanzado en Julio 2026 descubre automáticamente:
- **Models**: qué modelos usa la app (GPT-4, Claude, etc.)
- **Frameworks**: LangChain, CrewAI, AutoGen, LlamaIndex, Haystack, LangGraph
- **Agents**: AI agents definidos en el código
- **Datasets**: datasets referenciados
- **MCP tools**: integraciones MCP

Formato: CycloneDX. Incluye PURL, provider, occurrences con archivo y línea.

Esto es el "SBOM para AI" — y la transición natural al Acto 7: "Si el SBOM me dice qué dependencias de software tengo, el AIBOM me dice qué dependencias de AI tengo. ¿Y quién gobierna esas dependencias?"

---

## Secuencia exacta de ejecución — Timeline

```
══════════════════════════════════════════════════════════════════
  ACTO 6 — TIMELINE DE DEMO                   Duración: ~3 min
══════════════════════════════════════════════════════════════════

  t=0:00     PASO 1: AI SRE — INCIDENT + RUNBOOK         ~45s
  ─────────────────────────────────────────────────────────────
  Mostrar: AI SRE incident created + runbook execution
  (6 steps, all ✅, 12 seconds)

  Talk track: "AI SRE para seguridad, no solo infra.
  12 segundos. 6 acciones. 0 manuales."

  t=0:45     PASO 2: REMEDIATION TRACKER                  ~45s
  ─────────────────────────────────────────────────────────────
  Mostrar: SCS → Remediation Tracker → artifacts afectados
  (1 artifact, 3 environments, Jira ticket linked)

  Talk track: "Trackea artifacts en TODOS los environments.
  Se cierra automáticamente cuando todos están patcheados."

  t=1:30     PASO 3: SBOM BLAST RADIUS                    ~45s
  ─────────────────────────────────────────────────────────────
  Mostrar: SBOM analysis → legacy-api con mismo CVE
  + SBOM policy violation

  Talk track: "SBOM del Acto 3 paga aquí. 8 seg vs 5 días.
  SBOM policy dice: requests < 2.31.0 está prohibido."

  t=2:15     PASO 4: OPA POLICY                           ~30s
  ─────────────────────────────────────────────────────────────
  Mostrar: OPA policy .rego → blocks AI endpoints sin auth

  Talk track: "Bombero → Inspector → Código de construcción.
  Ningún AI endpoint sin auth pasa a producción."

  t=2:45     TRANSICIÓN AL ACTO 7                         ~15s
  ─────────────────────────────────────────────────────────────
  Talk track: "Código securizado. APIs protegidas.
  Pero el AI mismo — modelos, agents, MCP tools —
  ¿quién los gobierna? AIBOM + AI Security."

══════════════════════════════════════════════════════════════════
  RESUMEN
══════════════════════════════════════════════════════════════════

  TIEMPO: ~3 minutos
  FEATURES MOSTRADOS: AI SRE + Remediation Tracker + SBOM + OPA
  TODO ES REAL: API documentada, UI productizada, audit trail

  ┌─────────┬────────────────────────────┬─────────────────────┐
  │ Paso    │ Feature                    │ WOW                 │
  ├─────────┼────────────────────────────┼─────────────────────┤
  │ AI SRE  │ Runbook (security trigger) │ 12 seg, 0 manual    │
  ├─────────┼────────────────────────────┼─────────────────────┤
  │ Tracker │ SCS Remediation Tracker    │ Auto-track + close  │
  ├─────────┼────────────────────────────┼─────────────────────┤
  │ SBOM    │ SCS SBOM + Policies        │ 8 seg vs 5 días     │
  ├─────────┼────────────────────────────┼─────────────────────┤
  │ OPA     │ Pipeline governance        │ Previene recurrencia│
  └─────────┴────────────────────────────┴─────────────────────┘
```

---

## Validación — Las 5 preguntas de Cristian

```
1. ¿Es repetible N veces sin parecer scripted?
   ✅ SÍ. AI SRE runbook execution es determinístico.
   Remediation Tracker muestra datos reales. SBOM analysis
   es consistente. OPA policy es un file. Todo preparable.

2. ¿El claim tiene wiring técnico demostrable?
   ✅ SÍ. CADA feature es productizado:
   • AI SRE runbooks con Slack/Jira/PagerDuty/Zoom: documentado
   • HTTP Request → Remediation Tracker API: API real
   • Remediation Tracker con Live Tracking: documentado
   • SBOM generation + policy enforcement: documentado
   • OPA policies en pipelines: documentado

3. ¿Un equipo de seguridad real haría esto?
   ✅ SÍ. El flujo es NIST SP 800-61:
   Containment (virtual patching) → Analysis (SBOM blast radius)
   → Eradication (remediation tracker) → Post-incident (OPA policy).
   La diferencia: está automatizado en una plataforma.

4. ¿Estamos vendiendo governance post-code, no governance del coding?
   ✅ SÍ. AI SRE ORQUESTA — no codifica. Remediation Tracker
   TRACKEA — no arregla. SBOM ANALIZA — no modifica. OPA
   PREVIENE — no escribe. Harness gobierna el proceso.

5. ¿Se puede demostrar de forma consistente?
   ✅ SÍ. AI SRE runbook en UI o mockup. Remediation Tracker
   en UI real (si configurado) o screenshot. SBOM en pipeline
   execution. OPA policy es un .rego file. Todo es demostrable.
```
