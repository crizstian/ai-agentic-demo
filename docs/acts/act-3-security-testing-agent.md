# ACTO 3: "Security Testing Agent — Encontrar Y Remediar a Machine Speed"

## Qué hace el acto

El pipeline continúa al Security Scan stage. El Security Testing Agent despliega su arsenal: STO orquesta scanners, AI SAST detecta vulnerabilidades con confidence scoring, SCA flag la dependencia vulnerable, SCS genera el SBOM y firma el artefacto. Luego el Triage Agent prioriza por reachability real (no solo CVSS) y el Remediation Agent genera un fix validado y abre un PR.

El resultado: las vulnerabilidades de código clásicas (SQL injection, command injection, XSS, CORS) y la dependencia vulnerable se detectan y remedian. Pero las vulnerabilidades AI-specific (prompt injection, PII leak, BOLA/IDOR) NO se detectan — son problemas de lógica de negocio que SAST no puede ver. Estas sobreviven al pipeline y van a producción.

La audiencia aún no sabe esto. Lo descubrirán en el Acto 5.

---

## Por qué este contexto narrativo

**1. El Security Testing Agent es el arsenal más completo de Harness.** Este acto demuestra 6 capabilities en una sola ejecución de pipeline. Es la densidad más alta de valor en toda la demo.

**2. Establece la línea de Shift Left.** Todo lo que SAST/SCA puede detectar se detecta y remedia aquí. Esto valida que Shift Left funciona — para lo que puede funcionar.

**3. Planta la limitación honestamente.** SAST detecta patrones de código. Pero prompt injection es string concatenation (patrón normal), PII leak es una query que funciona correctamente, y BOLA/IDOR es la ausencia de auth (no la presencia de algo malicioso). Estas limitaciones son reales — no las estamos fabricando para la demo. Esto hace que el Acto 5 (Shield Right) sea genuino, no forzado.

**4. El ciclo completo se cierra aquí.** Find → Triage → Remediate → Validate → PR. De finding a fix validado en una ejecución de pipeline. Eso es el punch de "machine speed".

---

## Qué le ofrece a la audiencia

| Audiencia | Lo que se llevan | Wiring técnico |
|-----------|-----------------|----------------|
| **Developer** | "No me dan una lista de 200 findings y me dicen 'arréglalo'. Me dan 4 findings priorizados por reachability, un fix validado, y un PR listo para review. Solo apruebo y mergeo." | Triage Agent reduce ruido. Remediation Agent genera fix + valida contra pipeline + abre PR. Human in the loop. |
| **DevOps / Platform** | "El pipeline no solo detecta — remedia. Y el SBOM + attestation quedan como evidencia automática. No hay paso manual entre scan y fix." | STO orquesta scanners → Triage prioriza → Remediation genera fix → SCS firma artefacto. Pipeline continuo. |
| **Security / SecOps** | "AI SAST me da confidence scoring — no solo 'encontré algo' sino 'estoy 93% seguro que esto es real y aquí está el evidence'. Reachability me dice si vale la pena invertir tiempo. Y el SBOM me da inventario completo de dependencias." | AI SAST confidence scoring + Triage reachability analysis + SCS SBOM generation. |
| **Managers / Business** | "55 días promedio para remediar. Aquí se hizo en una ejecución de pipeline. Con evidence para auditoría." | Data point: 55 días industry avg → horas con Security Testing Agent. Attestation como evidencia. |

---

## Qué elementos se muestran y por qué

### 1. STO — Security Testing Orchestration
**Qué:** Orquesta múltiples scanners (Semgrep + scanner externo), deduplica resultados, normaliza severidades.
**Por qué:** La mayoría de empresas usan 3-5 scanners. Sin orquestación, el developer recibe resultados duplicados de cada uno. STO normaliza, deduplica, y presenta un view consolidado.

### 2. AI SAST (Harness / Qwiet)
**Qué:** SAST con AI confidence scoring. No solo detecta — te dice qué tan seguro está de que es real.
**Por qué:** 79% de reducción de falsos positivos, 93% de precisión. Esto cambia la conversación de "tenemos 200 findings" a "tenemos 4 findings confirmados con >90% de confianza". El developer deja de ignorar SAST results.

**Cómo funciona (diferenciador vs. mercado):**

| Aspecto | SAST Tradicional (Semgrep, CodeQL) | Harness AI SAST (Qwiet) |
|---------|-----------------------------------|------------------------|
| Método | Pattern matching — busca patrones de código conocidos | Data-flow analysis + ML — traza el camino del dato desde input hasta sink |
| Resultado | "Encontré algo que se parece a SQL injection" | "User input en línea 12 llega sin sanitizar a db.execute en línea 23. Confidence: 96%" |
| Falsos positivos | Alto (~40-60% en tools legacy) | 79% de reducción |
| Reachability | No — no sabe si el código se ejecuta | Sí — analiza si el path es alcanzable |

**¿Por qué no hay AI SCA?** SCA es un lookup de CVEs contra manifiestos de dependencias — el CVE existe o no. La "inteligencia" en SCA está en la priorización, que es exactamente lo que hace el Triage Agent con EPSS + reachability. La detección de SCA no necesita AI — necesita una base de datos actualizada.

### 3. SCA — Software Composition Analysis
**Qué:** Detecta dependencias con CVEs conocidos. En la demo: `requests==2.25.1` con CVE-2023-32681.
**Por qué:** Conecta directamente con el Acto 1 — Claude Code introdujo esta dependencia. El Change Advisor del Acto 2 ya la flaggeó como risk factor. Ahora SCA confirma que tiene un CVE real.

### 4. SCS — Supply Chain Security
**Qué:** SBOM generation + attestation (firma digital) + policy gates de compliance.
**Por qué:** Para industrias reguladas (banca, salud, gobierno), SCS es uno de los punches más fuertes de Harness.

**Valor para industrias reguladas:**

| Capability | Qué resuelve | Para quién |
|-----------|-------------|-----------|
| **SBOM (SPDX/CycloneDX)** | Inventario completo de cada dependencia, versión, licencia — auditable | Reguladores, compliance, CISO |
| **Attestation (SLSA L2)** | Firma digital que prueba: quién buildeó, qué inputs usó, qué scans pasó | Auditoría, cadena de custodia del artefacto |
| **Policy gates** | OPA policies que evalúan automáticamente si el artefacto cumple con las reglas de la org | Platform engineering, governance |
| **Blast radius (Acto 6)** | "¿Qué otros servicios usan esta dependencia vulnerable?" — respuesta en segundos | Incident response, zero-day triage |

**Talk track para audiencia regulada:**
> *"Cuando el regulador pregunte '¿qué componentes tiene este sistema?', la respuesta es el SBOM. Cuando pregunte '¿cómo sé que este artefacto no fue manipulado?', la respuesta es attestation. Cuando pregunte '¿cómo garantizan que no se deployea algo no conforme?', la respuesta son las policy gates. Todo automatizado, todo en el pipeline."*

### 5. Triage Agent (Expert Agent)
**Tipo:** Expert Agent — razona y analiza, genera un veredicto priorizado.
**Qué:** Combina CVSS + EPSS + reachability analysis para dar un veredicto: "esto es explotable, esto no".
**Por qué:** La diferencia entre "tienes 47 CVEs" y "tienes 4 explotables" es la diferencia entre un equipo paralizado y uno que actúa.
**Analogía:** Como un triage nurse en emergencias — no atiende por orden de llegada, atiende por urgencia real.

### 6. Remediation Agent (Worker Agent)
**Tipo:** Worker Agent — ejecuta una acción concreta: genera código, valida, abre PR.
**Qué:** Genera el fix, lo valida contra el pipeline (no rompe el build), pushea al branch.
**Por qué:** Cierra el ciclo: find → triage → fix → validate. El developer solo aprueba.

**¿Qué pasa si no hay fix disponible?**

| Situación | Remediation Agent hace | Developer hace |
|-----------|----------------------|----------------|
| Fix claro y disponible | Genera fix, valida, pushea | Revisa y aprueba |
| Fix rompe tests | Genera fix, reporta fallo | Ajusta manualmente |
| Zero-day sin patch | Reporta: no hay remediación disponible | Runtime Protection Agent aplica virtual patch (Acto 6) |
| Requiere refactor | Reporta: fix requiere cambio de arquitectura | Planifica el refactor |

> *Talk track:* "Si no hay fix — como en un zero-day — el Runtime Protection Agent aplica virtual patching en producción mientras el equipo trabaja en la solución. Lo veremos en el Acto 6."

---

## Flujo de PR — Remediation Agent

**Decisión de diseño:** El Remediation Agent pushea commits al MISMO branch del PR original. No abre un PR nuevo. El PR #52 se actualiza con los fixes y el pipeline re-corre.

```
FLUJO DE PR EN LA DEMO:

PR #52 (Claude Code)              Remediation Agent
─────────────────────             ─────────────────
feat: add AI assistant      ───▶  Pipeline corre
                            ───▶  Security scan: 5 findings
                            ───▶  Policy gate: BLOCKED (critical)
                            ───▶  Remediation Agent genera fixes
                            ───▶  Pushea commits al MISMO branch ←─── clave
                            ───▶  PR #52 se actualiza automáticamente
                            ───▶  Pipeline RE-CORRE
                            ───▶  Security scan: 0 SAST findings*
                            ───▶  Policy gate: PASSED
                            ───▶  Ready to merge → Acto 4

* Las vulns AI-specific (008, 009, 010) no fueron detectadas
  por SAST. No bloquearon el pipeline. Sobreviven a producción.
```

**Por qué esta opción y no un PR nuevo:**
- Un solo PR = flujo limpio para la demo
- El developer ve un solo PR con feature + fixes
- No hay confusión de "¿cuál mergeo primero?"
- El audit trail muestra: PR creado → scan failed → auto-remediated → scan passed

---

## Cómo se entera el developer (sin salir del IDE)

```
CANALES DE NOTIFICACIÓN — SIN CONTEXT SWITCHING

1. Harness Extension (sidebar) ──── PASIVO
   • Pipeline status: Running → ⛔ Policy Gate → ✅ Passed
   • Badge con count de findings
   • El developer lo VE sin preguntar

2. Harness AI Chat Agent ────────── ACTIVO/CONVERSACIONAL
   • "¿Qué encontró el security scan?"
   • "¿Cuáles son explotables?"
   • "Genera fixes y valida"
   • Respuestas con datos reales del pipeline

3. Claude Code + MCP ────────────── ALTERNATIVA
   • Mismos datos vía Harness MCP tools
   • Para quienes prefieren terminal

4. GitHub PR ────────────────────── PASIVO
   • Commits del Remediation Agent aparecen en el PR
   • El developer ve la actividad en su PR review normal
```

---

## Catálogo de prompts del developer

```
PROMPTS PARA EXPLOTAR EL SECURITY TESTING AGENT

# Findings overview
"What did the security scan find on my PR? Show severities
and confidence scores."

# Deep dive en un finding
"Explain the SQL injection finding in accounts.py. Show me
the data flow path from user input to the vulnerable function."

# Triage
"Which of these findings are actually exploitable in production?
Show reachability analysis."

# Remediation
"Generate fixes for the critical findings, validate them
against the pipeline, and push to my branch."

# SBOM
"Show me the SBOM for this build. How many dependencies, any
license issues, and known CVEs?"

# Comparación
"Compare the security posture of this PR vs main. Are we
introducing new risk?"

# Para audiencia regulada
"Show me the attestation and compliance evidence for this
artifact. What SLSA level does it meet?"
```

---

## WOW del acto

> **"En una sola ejecución de pipeline: escaneamos con múltiples herramientas, deduplificamos, priorizamos por reachability real — no por CVSS score que dice 'critical' pero nadie puede explotar — generamos un fix validado, y abrimos un PR. Lo que normalmente toma 55 días, el Security Testing Agent lo hizo en esta ejecución. Y el SBOM y la attestation ya quedaron como evidencia para auditoría."**

### Por qué es diferenciador

**vs. Snyk / Checkmarx / SonarQube:** Detectan. No remedian. No priorizan por reachability. No generan fixes validados. No firman artefactos. El developer recibe una lista y tiene que arreglarlo manualmente.

**vs. GitHub Advanced Security:** Detecta con CodeQL. No tiene Triage Agent con reachability. No tiene Remediation Agent que genere y valide fixes. No tiene SCS con attestation.

**vs. GitLab SAST:** Scanner integrado pero sin AI confidence scoring, sin reachability-based triage, sin remediation agent, sin supply chain security.

**El punch real:** No es "encontramos vulnerabilidades" — eso lo hacen todos. Es "encontramos, priorizamos por riesgo real, corregimos, validamos, y firmamos. En una ejecución."

---

## Cómo conecta al Acto 4

### Transición narrativa

> *"Las vulnerabilidades de código están remediadas. El fix está validado y en un PR. El SBOM está generado, el artefacto está firmado.*
>
> *Shift Left hizo su trabajo — atrapó todo lo que podía atrapar: patrones de código, CVEs conocidos, configuraciones inseguras.*
>
> *Pero hay una pregunta que SAST no puede responder: ¿qué pasa con la lógica de negocio? ¿Qué pasa con un endpoint que funciona correctamente pero no valida autorización? ¿Qué pasa con un AI assistant que construye su system prompt con user input — algo que el código hace de forma técnicamente correcta?*
>
> *Eso solo se descubre en runtime. Pero primero, deployemos."*

### Lo que se planta para actos futuros

| Elemento plantado | Relevancia futura |
|-------------------|-------------------|
| SBOM con inventario completo de dependencias | Acto 6: blast radius analysis — "¿qué otros servicios usan esta dep?" |
| Attestation del artefacto | Acto 6: evidence para la respuesta al incidente |
| Las vulns AI-specific NO fueron detectadas (008, 009, 010) | Acto 5: el atacante las explota. Acto 6: Shield Right las detecta |
| Remediation Agent PR — human in the loop | Acto 6: el mismo Remediation Agent genera fix para las vulns de runtime |
| "Shift Left caught what it could" | Acto 5-6: "Shield Right catches what Shift Left can't" |

### Split narrativo: qué se resolvió vs qué sobrevive

```
  DESPUÉS DEL ACTO 3:

  ✅ RESUELTAS (Shift Left funcionó):
  ├── VULN-001: SQL Injection ─────── Remediation Agent fix
  ├── VULN-002: Command Injection ─── Remediation Agent fix
  ├── VULN-006: Reflected XSS ─────── Remediation Agent fix
  ├── VULN-007: Insecure CORS ─────── Remediation Agent fix
  └── SCA: requests CVE ──────────── Dependency upgrade

  ❌ SOBREVIVEN (SAST no puede verlas):
  ├── VULN-008: Prompt Injection ──── lógica, no patrón
  ├── VULN-009: PII Leak ──────────── business logic
  └── VULN-010: BOLA/IDOR ─────────── ausencia de auth

  MENSAJE: "Shift Left atrapó lo que pudo.
            Shield Right atrapa lo que Shift Left no puede."
```

---

## Secuencia exacta de ejecución — Timeline

```
══════════════════════════════════════════════════════════════════════════════════
  ACTO 3 — TIMELINE DE EJECUCIÓN                              Duración: ~5 min
══════════════════════════════════════════════════════════════════════════════════

  CONTEXTO DE ENTRADA:
  Seguimos en VS Code. El Acto 2 terminó con el Security Scan
  stage cambiando a "Running" en el sidebar de Harness Extension.
  NO salimos del IDE. Todo conversacional vía Harness AI / MCP.

  NOTA: Este acto tiene un MOMENTO DE TENSIÓN — el pipeline se
  detiene por policy gate. Y un MOMENTO DE VELOCIDAD — el
  Remediation Agent genera y valida el fix en vivo.

  DECISIÓN DE FORMATO: En este acto SI mostramos Harness Console
  brevemente para los security findings (la visualización es
  importante para la audiencia). Pero el consumo principal sigue
  siendo conversacional.


  t=0:00        PASO 1: SECURITY SCAN COMPLETO — PREGUNTAR RESULTADOS
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "El Security Testing Agent terminó su análisis. Vamos a ver
  │   qué encontró. Le pregunto directamente."
  │
  │  🖥️ ACCIÓN:
  │  Escribir en Harness AI Chat Agent:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO — Harness AI Chat Agent:              │
  │  │                                                         │
  │  │ The security scan just completed on PR #52. Give me     │
  │  │ the full findings summary: how many vulnerabilities     │
  │  │ were found, what types, what severities, and did        │
  │  │ SCA flag any dependency issues?                         │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  📎 PROMPT ALTERNATIVO — Claude Code + MCP:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ Use the Harness MCP tools to get the security scan      │
  │  │ results for the latest pipeline execution on PR #52.    │
  │  │ Show me all SAST and SCA findings with severities       │
  │  │ and confidence scores.                                  │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 HARNESS AI RESPONSE                                 │
  │  │                                                         │
  │  │ Security scan completed. Here's the summary:            │
  │  │                                                         │
  │  │ 📊 SAST Findings (4):                                   │
  │  │  🔴 CRITICAL  SQL Injection — accounts.py:23            │
  │  │               Confidence: 96%                           │
  │  │  🔴 CRITICAL  Command Injection — admin.py:18           │
  │  │               Confidence: 94%                           │
  │  │  🟡 MEDIUM    Reflected XSS — app.py:45                 │
  │  │               Confidence: 91%                           │
  │  │  🟢 LOW       Insecure CORS config — app.py:12          │
  │  │               Confidence: 88%                           │
  │  │                                                         │
  │  │ 📦 SCA Findings (1):                                    │
  │  │  🟡 MEDIUM    requests==2.25.1                          │
  │  │               CVE-2023-32681 (HTTP header injection)    │
  │  │               Fix available: upgrade to 2.31.0+         │
  │  │                                                         │
  │  │ 🔒 SCS:                                                 │
  │  │  ✅ SBOM generated (47 dependencies cataloged)          │
  │  │  ⏳ Attestation pending (post-remediation)              │
  │  │                                                         │
  │  │ ⛔ Policy gate: TRIGGERED                               │
  │  │    Rule: "No critical findings in production builds"    │
  │  │    Pipeline PAUSED — awaiting remediation               │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK (señalando la respuesta):
  │  "Cuatro findings de SAST, uno de SCA. Pero noten algo
  │   diferente: cada finding tiene un confidence score. 96%,
  │   94%, 91%. Esto no es 'encontré algo que se parece a un
  │   pattern'. Es 'estoy 96% seguro que esta SQL injection es
  │   real'. 79% de reducción de falsos positivos. 93% de
  │   precisión. El developer deja de ignorar los resultados
  │   de SAST porque ahora confía en ellos.
  │
  │   Y SCA confirmó lo que el Change Advisor flaggeó: la
  │   dependencia requests que Claude Code introdujo tiene
  │   un CVE conocido. Fix disponible: upgrade a 2.31.0+."
  │
  │  ⭐ WOW:
  │  "AI SAST con confidence scoring. No es 'encontré 200
  │   cosas y arréglalo'. Es '4 findings con >88% de
  │   confianza y aquí está el evidence'."
  │
  ▼

  t=1:00           PASO 2: POLICY GATE — EL PIPELINE SE DETUVO
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Y el pipeline se detuvo. Miren: policy gate triggered.
  │   La policy dice: 'no se permite deployer con findings
  │   críticos'. Hay dos SQL injection y un command injection
  │   marcados critical. El pipeline no avanza.
  │
  │   Esto es governance real. No importa quién escribió el
  │   código — un developer, un coding agent, un contractor.
  │   Si tiene vulnerabilidades críticas, no pasa."
  │
  │  🖥️ ACCIÓN:
  │  Señalar en el sidebar de Harness Extension el status:
  │  ⛔ Policy Gate — Pipeline Paused
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🔶 HARNESS EXTENSION (sidebar)                         │
  │  │                                                         │
  │  │ Pipeline: PR-Validation #848                            │
  │  │                                                         │
  │  │  ✅ CI Build         42s                                │
  │  │  ✅ Change Advisor   14s                                │
  │  │  ⛔ Security Scan    POLICY GATE                        │
  │  │     Reason: Critical findings detected                  │
  │  │  ⏳ Deploy            blocked                            │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW:
  │  "El pipeline se detuvo solo. No fue un humano quien lo
  │   bloqueó. Fue una OPA policy evaluando los findings.
  │   Governance automatizada."
  │
  ▼

  t=1:30              PASO 3: TRIAGE AGENT — PRIORIZACIÓN REAL
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Tenemos 5 findings. ¿Pero cuáles son realmente
  │   explotables? El CVSS score dice 'critical' para dos
  │   de ellos. Pero ¿la función vulnerable se llama
  │   realmente en producción? Veamos qué dice el Triage
  │   Agent."
  │
  │  🖥️ ACCIÓN:
  │  Escribir en Harness AI Chat Agent:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO — Harness AI Chat Agent:              │
  │  │                                                         │
  │  │ Run triage on the security findings for PR #52.         │
  │  │ For each finding, show me: CVSS score, EPSS score,      │
  │  │ reachability status, and whether it's actually           │
  │  │ exploitable in production.                              │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 HARNESS AI — TRIAGE AGENT RESULTS                   │
  │  │                                                         │
  │  │ ┌──────────────┬──────┬──────┬─────────────┬──────────┐ │
  │  │ │ Finding      │ CVSS │ EPSS │ Reachable?  │ Action   │ │
  │  │ ├──────────────┼──────┼──────┼─────────────┼──────────┤ │
  │  │ │ SQL Inject.  │ 9.8  │ 0.87 │ ✅ YES      │ FIX NOW  │ │
  │  │ │ Cmd Inject.  │ 9.1  │ 0.72 │ ✅ YES      │ FIX NOW  │ │
  │  │ │ XSS          │ 6.1  │ 0.34 │ ✅ YES      │ FIX      │ │
  │  │ │ CORS         │ 3.7  │ 0.08 │ ⚠️ PARTIAL  │ REVIEW   │ │
  │  │ │ requests CVE │ 5.3  │ 0.41 │ ✅ YES      │ UPGRADE  │ │
  │  │ └──────────────┴──────┴──────┴─────────────┴──────────┘ │
  │  │                                                         │
  │  │ Summary: 4 of 5 findings are reachable and exploitable. │
  │  │ CORS is partially reachable (context-dependent).        │
  │  │                                                         │
  │  │ Reachability path (SQL Injection):                      │
  │  │   POST /api/accounts/transfer                           │
  │  │   → accounts.py:23 → db.execute(query)                 │
  │  │   → User input reaches SQL query without sanitization   │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK:
  │  "El Triage Agent no priorizó solo por CVSS. Combinó CVSS
  │   con EPSS — la probabilidad real de explotación — y
  │   reachability analysis: ¿el código vulnerable se ejecuta
  │   realmente en producción?
  │
  │   Miren la SQL injection: CVSS 9.8, EPSS 0.87, y es
  │   reachable — el user input llega directamente a la query
  │   sin sanitización. Eso es 'fix now'.
  │
  │   La diferencia entre tener 47 CVEs y saber cuáles
  │   realmente importan. Eso es Triage Agent."
  │
  │  ⭐ WOW:
  │  "CVSS + EPSS + reachability. No es un score — es un
  │   veredicto: 'esto es explotable, aquí está el path,
  │   arréglalo ahora.' La diferencia entre noise y signal."
  │
  ▼

  t=2:30         PASO 4: REMEDIATION AGENT — FIX VALIDADO + PR
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Sabemos qué está mal y por qué importa. Ahora la
  │   pregunta: ¿quién lo arregla? El developer tiene 4
  │   findings. Normalmente toma 55 días promedio para
  │   remediar una vulnerabilidad. Veamos qué hace el
  │   Remediation Agent."
  │
  │  🖥️ ACCIÓN:
  │  Escribir en Harness AI Chat Agent:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO — Harness AI Chat Agent:              │
  │  │                                                         │
  │  │ Trigger the Remediation Agent for the critical and      │
  │  │ high findings on PR #52. Generate fixes, validate       │
  │  │ them, and push to the feature branch.                   │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 HARNESS AI — REMEDIATION AGENT (Worker Agent)       │
  │  │                                                         │
  │  │ Generating fixes for 5 findings...                      │
  │  │                                                         │
  │  │ ✅ SQL Injection (accounts.py:23)                       │
  │  │    Fix: parameterized query with placeholders           │
  │  │    Validation: tests pass ✅                             │
  │  │                                                         │
  │  │ ✅ Command Injection (admin.py:18)                      │
  │  │    Fix: replaced os.system with subprocess.run          │
  │  │    + input sanitization                                 │
  │  │    Validation: tests pass ✅                             │
  │  │                                                         │
  │  │ ✅ Reflected XSS (app.py:45)                            │
  │  │    Fix: HTML entity encoding on user input              │
  │  │    Validation: tests pass ✅                             │
  │  │                                                         │
  │  │ ✅ Insecure CORS (app.py:12)                            │
  │  │    Fix: restricted origins to allowed domains           │
  │  │    Validation: tests pass ✅                             │
  │  │                                                         │
  │  │ ✅ requests CVE (requirements.txt)                      │
  │  │    Fix: upgraded requests==2.25.1 → requests==2.32.3    │
  │  │    Validation: tests pass ✅                             │
  │  │                                                         │
  │  │ 📌 Pushed 5 fix commits to feature branch               │
  │  │    PR #52 updated — pipeline will re-run                │
  │  │    Status: Ready for human review                       │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK:
  │  "El Remediation Agent no te sugiere un fix. Lo GENERA.
  │   Lo valida contra el pipeline — confirma que los tests
  │   siguen pasando. Y pushea los commits al MISMO branch.
  │
  │   No abre un PR nuevo — actualiza el PR original. El
  │   developer ve un solo PR con su feature + los fixes.
  │   El pipeline re-corre automáticamente. Revisa y aprueba.
  │   Human in the loop — AI does the work.
  │
  │   De finding a fix validado: minutos. El promedio de la
  │   industria: 55 días. Con el Remediation Agent: minutos.
  │
  │   Y si no hay fix disponible — como en un zero-day — el
  │   Runtime Protection Agent aplica virtual patching en
  │   producción. Lo veremos en el Acto 6."
  │
  │  ⭐ WOW:
  │  "55 días → minutos. Fix validado, pusheado al branch,
  │   pipeline re-corre. Un solo PR. Human in the loop."
  │
  ▼

  t=3:30              PASO 5: SCS — SUPPLY CHAIN SECURITY
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Mientras el Remediation Agent trabajó, Supply Chain
  │   Security hizo lo suyo: generó el SBOM — un inventario
  │   completo de cada dependencia, cada versión, cada licencia.
  │   Y attestation va a firmar el artefacto digitalmente.
  │
  │   Para quienes están en industrias reguladas — banca,
  │   salud, gobierno — esto es fundamental: cuando el
  │   regulador pregunte '¿qué componentes tiene este sistema?',
  │   la respuesta es el SBOM. '¿Cómo sé que el artefacto no
  │   fue manipulado?' Attestation con SLSA Level 2. '¿Cómo
  │   garantizan compliance?' Policy gates automáticas."
  │
  │  🖥️ ACCIÓN:
  │  Preguntar por el SBOM y attestation vía Harness AI:
  │
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 📎 PROMPT EXACTO — Harness AI Chat Agent:              │
  │  │                                                         │
  │  │ Show me the SBOM and supply chain security summary      │
  │  │ for this build: dependencies, licenses, known CVEs,     │
  │  │ attestation status, and SLSA compliance level.          │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  👁️ RESULTADO ESPERADO:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🤖 HARNESS AI RESPONSE                                 │
  │  │                                                         │
  │  │ 📦 SBOM (SPDX format):                                  │
  │  │   Total dependencies: 47                                │
  │  │   Direct: 4 (flask, flask-cors, pyjwt, requests)        │
  │  │   Transitive: 43                                        │
  │  │   License issues: 0                                     │
  │  │   Known CVEs: 0 (requests upgraded by Remediation)      │
  │  │                                                         │
  │  │ 🔐 Attestation:                                         │
  │  │   Status: Will sign on next successful build            │
  │  │   Type: SLSA Level 2                                    │
  │  │   Evidence attached:                                    │
  │  │     • Build provenance (who, when, what inputs)         │
  │  │     • Scan results (SAST, SCA, all passed)              │
  │  │     • Policy evaluation (OPA rules satisfied)           │
  │  │                                                         │
  │  │ 📋 Compliance:                                           │
  │  │   SLSA Level 2: ✅ Met                                   │
  │  │   SBOM generated: ✅                                     │
  │  │   Artifact signed: ⏳ (on merge)                         │
  │  │   Audit trail: ✅ Complete                               │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  🎤 TALK TRACK:
  │  "47 dependencias catalogadas — directas y transitivas.
  │   Zero CVEs conocidos después de la remediación. Attestation
  │   firmará el artefacto con SLSA Level 2 cuando hagamos merge.
  │
  │   Pero esto no es solo para compliance. Cuando caiga el
  │   próximo zero-day — y va a caer — este SBOM nos va a decir
  │   en SEGUNDOS si estamos afectados y en qué servicios. No
  │   en días de auditoría manual. Lo veremos en el Acto 6."
  │
  │  ⭐ WOW:
  │  "Para audiencia regulada: SBOM + attestation + audit trail
  │   automatizado. Para todos: blast radius en segundos cuando
  │   caiga el próximo zero-day."
  │
  ▼

  t=4:00                    PASO 6: TRANSICIÓN AL ACTO 4
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │
  │  🎤 TALK TRACK:
  │  "Las vulnerabilidades de código están remediadas. El fix
  │   está validado y en un PR. El SBOM está generado.
  │
  │   Shift Left hizo su trabajo — atrapó todo lo que podía
  │   atrapar. Patrones de código, CVEs conocidos, configs
  │   inseguras. Todo corregido.
  │
  │   Pero hay una pregunta que SAST no puede responder:
  │   ¿qué pasa con la lógica de negocio? Un endpoint que
  │   funciona correctamente pero no valida autorización.
  │   Un AI assistant que construye su system prompt con
  │   user input — algo técnicamente correcto.
  │
  │   Eso solo se descubre en runtime. Pero primero —
  │   deployemos este fix."
  │
  │  🖥️ ACCIÓN:
  │  Señalar PR #52 actualizado con los fix commits.
  │  El sidebar muestra pipeline re-run passed.
  │
  │  👁️ EN PANTALLA:
  │  ┌─────────────────────────────────────────────────────────┐
  │  │ 🔶 HARNESS EXTENSION (sidebar)                         │
  │  │                                                         │
  │  │ Pipeline: PR-Validation #848 (re-run)                   │
  │  │  ✅ CI Build                                            │
  │  │  ✅ Change Advisor                                      │
  │  │  ✅ Security Scan — 0 critical/high findings            │
  │  │  ⏳ Deploy (ready — pending merge)                      │
  │  │                                                         │
  │  │ 🔀 PR #52 — feat: add AI banking assistant              │
  │  │    Updated: +5 fix commits by Remediation Agent         │
  │  │    Status: Ready for review                             │
  │  └─────────────────────────────────────────────────────────┘
  │
  │  ⭐ WOW:
  │  "Un solo PR: feature + fixes. Pipeline re-corrió, policy
  │   gate pasó. El developer revisa una vez y aprueba todo.
  │   Ahora toca deployar."
  │
  ▼
  ║
  ║  ═══════════════════════════════════════════════════════════
  ║   → TRANSICIÓN AL ACTO 4
  ║     Merge del fix PR → Deploy gobernado
  ║  ═══════════════════════════════════════════════════════════
  ║


══════════════════════════════════════════════════════════════════════════════════
  RESUMEN DEL ACTO 3
══════════════════════════════════════════════════════════════════════════════════

  TIEMPO TOTAL: ~5 minutos
  CONTEXT SWITCHING: Mínimo — todo vía Harness AI desde VS Code

  PASOS:
  ┌────────┬────────────────────────────┬──────────┬───────────────────────────┐
  │ Paso   │ Qué pasa                   │ Duración │ WOW                       │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 1      │ Security findings summary  │ 60s      │ AI SAST confidence        │
  │        │ vía Harness AI             │          │ scoring: 96%, 94%...      │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 2      │ Policy gate: pipeline      │ 30s      │ Pipeline se detuvo solo   │
  │        │ PAUSED por critical        │          │ — governance automatizada │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 3      │ Triage Agent: CVSS + EPSS  │ 60s      │ Reachability: noise vs    │
  │        │ + reachability             │          │ signal                    │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 4      │ Remediation Agent: fix     │ 60s      │ 55 días → minutos.       │
  │        │ validado + PR              │          │ Human in the loop.        │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 5      │ SCS: SBOM + attestation    │ 30s      │ Planta para Acto 6       │
  ├────────┼────────────────────────────┼──────────┼───────────────────────────┤
  │ 6      │ Transición al Acto 4       │ 30s      │ "Shift Left hizo su      │
  │        │                            │          │ trabajo. Pero..."        │
  └────────┴────────────────────────────┴──────────┴───────────────────────────┘

  PROMPTS UTILIZADOS:
  ┌─────┬───────────────────────┬─────────────────────────────────────────────┐
  │ #   │ Herramienta           │ Prompt                                      │
  ├─────┼───────────────────────┼─────────────────────────────────────────────┤
  │ 1   │ Harness AI Chat Agent │ "The security scan just completed on        │
  │     │                       │  PR #52. Give me the full findings          │
  │     │                       │  summary: how many vulnerabilities were     │
  │     │                       │  found, what types, what severities, and    │
  │     │                       │  did SCA flag any dependency issues?"       │
  ├─────┼───────────────────────┼─────────────────────────────────────────────┤
  │ 2   │ Harness AI Chat Agent │ "Run triage on the security findings for   │
  │     │                       │  PR #52. For each finding, show me: CVSS   │
  │     │                       │  score, EPSS score, reachability status,   │
  │     │                       │  and whether it's actually exploitable     │
  │     │                       │  in production."                           │
  ├─────┼───────────────────────┼─────────────────────────────────────────────┤
  │ 3   │ Harness AI Chat Agent │ "Trigger the Remediation Agent for the     │
  │     │                       │  critical and high findings on PR #52.     │
  │     │                       │  Generate fixes, validate them, and push   │
  │     │                       │  to the feature branch."                   │
  ├─────┼───────────────────────┼─────────────────────────────────────────────┤
  │ 4   │ Harness AI Chat Agent │ "Show me the SBOM and supply chain         │
  │     │                       │  security summary for this build:          │
  │     │                       │  dependencies, licenses, known CVEs,       │
  │     │                       │  attestation status, and SLSA compliance   │
  │     │                       │  level."                                   │
  └─────┴───────────────────────┴─────────────────────────────────────────────┘

  CAPABILITIES DEMOSTRADAS:
  ┌──────────────────────────────┬─────────────────────────────────────────────┐
  │ Capability                   │ Qué demostró                                │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ STO (Security Testing        │ Orquestación de múltiples scanners,         │
  │ Orchestration)               │ deduplicación, normalización                │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ AI SAST                      │ Confidence scoring: 79% menos falsos        │
  │ (Harness / Qwiet)            │ positivos, 93% precisión                    │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ SCA                          │ Dependency CVE detection, fix available     │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ SCS (Supply Chain Security)  │ SBOM generation, attestation, SLSA L2      │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Triage Agent                 │ CVSS + EPSS + reachability = priorización  │
  │                              │ por riesgo real, no por score               │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Remediation Agent            │ Fix generado + validado + PR abierto.       │
  │                              │ 55 días → minutos. Human in the loop.       │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Policy Gate (OPA)            │ Pipeline se detuvo automáticamente por      │
  │                              │ critical findings. Governance real.         │
  ├──────────────────────────────┼─────────────────────────────────────────────┤
  │ Harness AI Chat Agent        │ Consumo conversacional de security          │
  │                              │ findings, triage, remediation sin           │
  │                              │ context switching                           │
  └──────────────────────────────┴─────────────────────────────────────────────┘

  SEÑALES PLANTADAS PARA ACTOS FUTUROS:
  ┌──────────────────────────────────┬────────────────────────────────────────┐
  │ Señal                            │ Dónde paga                             │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ SBOM con 47 deps catalogadas     │ Acto 6: blast radius — "¿qué otros    │
  │                                  │ servicios usan esta dep?"             │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Attestation del artefacto        │ Acto 6: evidence para respuesta       │
  │                                  │ a incidente + compliance              │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ VULN-008/009/010 NO detectadas   │ Acto 5: el atacante las explota       │
  │ (la audiencia no lo sabe)        │ Acto 6: Shield Right las detecta      │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ Remediation Agent pattern        │ Acto 6: mismo Remediation Agent       │
  │ (find → fix → validate → PR)     │ genera fix para las vulns de runtime  │
  ├──────────────────────────────────┼────────────────────────────────────────┤
  │ "Shift Left caught what it       │ Acto 5-6: "Shield Right catches       │
  │ could"                           │ what Shift Left can't"               │
  └──────────────────────────────────┴────────────────────────────────────────┘
```
