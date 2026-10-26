# De 5 a 306 Agentes: Guia de Industrializacion

> Como escalar un ecosistema de agentes AI con governance, calidad y observabilidad
> usando Harness Platform como control plane.

---

## El Problema

Construir 1 agente es un proyecto. Construir 306 es una operacion.

Un banco con expertise avanzado en agentes AI ya resolvio la parte dificil: dominio bancario
embebido en prompts, separacion System 1/System 2, modelos restringidos (CDM) para
micro-decisiones, y un meta-orquestador que coordina todo.

Lo que no resolvio — porque no es un problema de agentes — es:

| Pregunta | A 5 agentes | A 306 agentes |
|----------|------------|---------------|
| Quien hizo que? | "Yo se, fui yo" | Imposible saberlo sin audit trail |
| Cuanto cuesta? | "Poco" | $X0,000/mes sin visibilidad por agente |
| Este agente alucina? | "Lo probe manual" | No hay quality gate sistematico |
| Quien puede deployar a prod? | "Todos" | Compliance violation |
| Si falla a las 3am? | "Me levanto" | Necesita recovery automatico |
| Como sabe IT que es seguro? | "Confien en mi" | 45 dias esperando aprobacion |

**El cuello de botella no es construir agentes. Es gobernarlos.**

---

## Las 3 Capas del Delivery con Agentes

```
+================================================================+
|                    CONTROL PLANE                                |
|  Harness Platform                                               |
|                                                                 |
|  VERIFICAR · ENFORCAR · REGISTRAR · RECUPERAR                   |
|  EVALUAR · DESCUBRIR · PROTEGER · COSTEAR                       |
|                                                                 |
|  Pipeline determinista + AI Evals + SCS + RBAC + OPA +          |
|  AI Budget + Secrets + Audit Trail + AI SRE                     |
+================================================================+
|  +----------------------------------------------------------+  |
|  |              ARNES DE ARNESES                             |  |
|  |  Meta-orquestador del banco                               |  |
|  |                                                           |  |
|  |  COORDINAR · DECIDIR · RUTEAR                             |  |
|  |                                                           |  |
|  |  LLM (System 2) + CDM (constrained) + Jev (System 1)     |  |
|  |  Logica de negocio, dominio regulatorio                   |  |
|  +----------------------------------------------------------+  |
|  |  +--------+  +--------+  +--------+       +--------+     |  |
|  |  |Agent 1 |  |Agent 2 |  |Agent 3 |  ...  |Agent N |     |  |
|  |  | HACER  |  | HACER  |  | HACER  |       | HACER  |     |  |
|  |  +--------+  +--------+  +--------+       +--------+     |  |
|  +----------------------------------------------------------+  |
+================================================================+
```

**Capa 1 — Arnes:** Cada agente con su modelo, tools, prompt, permisos. El banco los construye.
**Capa 2 — Arnes de Arneses:** Orquestador que decide que agente hace que. El banco lo construye.
**Capa 3 — Control Plane:** Infraestructura independiente que VERIFICA, ENFORCA, REGISTRA y
RECUPERA. **Esto no se construye con otro agente.** Es plataforma.

---

## Ciclo de Vida del Agente AI

Un agente AI no es un microservicio normal. Tiene riesgos especificos:
alucinacion, fuga de PII, prompt injection, costo impredecible, drift de calidad.

El ciclo de vida tiene 6 fases — 3 pre-produccion, 3 post-produccion:

```
PRE-PRODUCCION                           POST-PRODUCCION
(pipeline)                               (continuo 24/7)

 CONSTRUIR ──> EVALUAR ──> DESPLEGAR ──> DESCUBRIR ──> PROTEGER ──> COSTEAR
     |             |            |              |             |           |
  CI/CD +       AI Evals    Canary +        AI           AI         AI Budget
  STO +          Suite      SCS +         Discovery    Firewall      + CCM
  Agents        Quality     Feature                    + WAAP
                 Gate       Flags
                            + RBAC

              ◄────────── El ciclo nunca termina ──────────►
```

---

## Fase 1: CONSTRUIR

> El codigo se escribe, se testea, se escanea, se firma.

### Que aporta el banco

- Prompts con dominio bancario (regulacion, productos, procesos internos)
- Logica de agente (herramientas, decision trees, CDM/Jev)
- Tests funcionales del agente (golden tests, edge cases de dominio)
- Datasets de evaluacion con datos representativos del negocio

### Que aporta Harness Platform

| Capacidad | Recurso Harness | Que hace |
|-----------|-----------------|----------|
| **Agent CRUD** | `agent` (create/update/delete) | Crear, versionar, gestionar agentes como entidades de plataforma |
| **Agent Templates** | `template` / `template_v1` | Patrones reutilizables: un template "security-scanner" que 20 equipos instancian |
| **Pipeline CI** | `pipeline` (stage: CI) | Build + test + scan determinista. Steps en YAML = estructuralmente imposible saltarse |
| **Test Intelligence** | `step: Test` (intelligenceMode) | Solo corre tests afectados por el cambio. A 306 agentes, ahorra horas |
| **SAST/SCA** | `step: Semgrep, HarnessSAST, Gitleaks` | Escaneo de seguridad bloqueante. El agente que escribio el codigo NO es el que lo escanea |
| **AI Agent en pipeline** | `step: Agent` | BYOA — Bring Your Own Agent. El agente del banco corre DENTRO del pipeline con governance |
| **Supply Chain** | `step: SscaOrchestration, provenance, SscaArtifactSigning` | SBOM + SLSA attestation + firma keyless. Cadena de custodia criptografica |

### Patron: Separacion de concerns

```
HACER (agente del banco)          VERIFICAR (plataforma)
  |                                 |
  Escribe codigo ──────────────> SAST escanea
  Genera tests ────────────────> Test Intelligence ejecuta
  Propone fix de seguridad ────> OPA policy gate BLOQUEA si no cumple
  |                                 |
  El que HACE no VERIFICA.          El que VERIFICA no puede ser bypaseado.
```

---

## Fase 2: EVALUAR

> Antes de que un agente llegue a produccion, pasa un examen.

### Que aporta el banco

- **Datasets de evaluacion** con queries reales del dominio bancario
- **Criterios de aceptacion** especificos del negocio (ej: "nunca recomendar producto sin disclaimers")
- **Golden responses** — respuestas esperadas validadas por expertos del dominio
- **Umbrales** por tipo de agente (un agente de fraude tiene tolerancia 0 a PII; uno de FAQ es mas flexible)

### Que aporta Harness Platform

| Capacidad | Componente AI Evals | Que hace |
|-----------|---------------------|----------|
| **Target** | Target | Define QUE se evalua: endpoint HTTP, prompt template, MCP tool, codigo |
| **Dataset** | Dataset | Casos de prueba con input/expected output. El banco provee los datos, Evals los ejecuta |
| **Scorers** | Metric Set | 47+ metricas: Hallucination, PII Detection, Toxicity, Schema Validation, Latency, Contains, Semantic Similarity, RAGAS Faithfulness... |
| **Evaluation** | Evaluation | Une Target + Dataset + Metrics. Ejecutable como unidad |
| **Suite** | Suite | Agrupa evaluaciones con estrategia de gating: `all_must_pass` o `weighted_threshold` |
| **Quality Gate** | `step: AiEval` en pipeline | Si la suite falla, el deploy se BLOQUEA. No es opinion — son metricas computadas |
| **Traces** | Traces | Cada invocacion del agente registrada: input, output, latencia, tokens, scorer results |
| **Analytics** | Analytics | Tendencias de calidad en el tiempo. Detecta drift antes de que sea problema |
| **Registry** | Registry | Catalogo de targets evaluados. Inventario vivo de todos los agentes con su score actual |

### Patron: Quality Gate pre-deploy

```yaml
# Pipeline YAML — step nativo, no script
- step:
    type: AiEval
    name: AI Quality Gate
    identifier: AI_Quality_Gate
    spec:
      suiteId: <uuid-de-la-suite>
      apiKey: <+secrets.getValue("harnessToken")>
    timeout: 10m
```

El step nativo `AiEval`:
1. Triggerea la suite (N evaluaciones en paralelo)
2. Cada evaluacion corre el dataset contra el target
3. Los scorers miden cada respuesta (hallucination, PII, schema, latency...)
4. La suite aplica la estrategia de gating (`all_must_pass` / `weighted_threshold`)
5. Si falla → pipeline BLOQUEADO. Si pasa → deploy continua

### Escalamiento: 5 → 306

| A 5 agentes | A 306 agentes |
|-------------|---------------|
| 5 suites manuales | Templates de suite por tipo de agente |
| Review manual de resultados | Analytics automatico con alertas de drift |
| "Lo probe y funciona" | Registry con score actual de cada agente |
| Eval ad-hoc | Eval en CADA pipeline run (quality gate) |

---

## Fase 3: DESPLEGAR

> No es kubectl apply. Es despliegue controlado con verificacion y rollback.

### Que aporta el banco

- Definicion de ambientes (dev/staging/prod) y sus restricciones
- Approval workflows y stakeholders (quien aprueba que)
- Runbooks de rollback especificos del dominio
- Feature flags por segmento de usuarios (QA, beta, GA)

### Que aporta Harness Platform

| Capacidad | Recurso Harness | Que hace |
|-----------|-----------------|----------|
| **Canary/Rolling** | `step: K8sCanaryDeploy, K8sRollingDeploy` | Trafico parcial + health monitoring + rollback atomico |
| **SCS Enforcement** | `step: SscaEnforcement, SlsaVerification, SscaArtifactVerification` | Verifica SBOM + SLSA + firma ANTES de deploy. Supply chain integrity |
| **OPA Policies** | `policy`, `policy_set` | Gates bloqueantes: "no deployar si tiene CVE critica / sin SBOM / sin firma" |
| **Approval Gates** | `step: JiraApproval, HarnessApproval` | ITSM integrado. Jira ticket = approval automatico. Sin correos manuales |
| **Feature Flags** | `step: FmeFlagSetIndividualTargets, FmeFlagDefaultAllocation` | Progressive rollout: QA → Beta → 90% → 100%. Rollback = toggle |
| **Environment RBAC** | `environment`, `role`, `role_assignment`, `resource_group` | Quien puede deployar a que ambiente. Granular por proyecto/org |
| **Freeze Windows** | `freeze_window`, `global_freeze` | Congelar deploys por periodo (ej: cierre fiscal, release cut) |
| **Secrets** | `secret` | Secrets inyectados por la plataforma, FUERA del contexto del agente. El agente nunca ve la llave |

### Patron: Deploy gobernado

```
                   Deploy Request
                        |
            +-----------v-----------+
            |  OPA Policy Gate      |  <-- Determinista: pass/fail
            |  "tiene SBOM?"        |
            |  "tiene firma?"       |
            |  "paso AI Evals?"     |
            +-----------+-----------+
                        |
            +-----------v-----------+
            |  SCS Verification     |  <-- Criptografico: firma valida?
            |  SBOM + SLSA + Sign   |
            +-----------+-----------+
                        |
            +-----------v-----------+
            |  Jira Approval        |  <-- Organizacional: aprobado?
            +-----------+-----------+
                        |
            +-----------v-----------+
            |  Canary 25%           |  <-- Gradual: trafico parcial
            |  Health monitoring    |
            +-----------+-----------+
                       / \
                 PASS /   \ FAIL
                     /     \
              Rolling    Rollback
              100%       atomico
                |
            Feature Flags
            QA -> Beta -> GA -> Full
```

---

## Fase 4: DESCUBRIR

> Saber que agentes tienes, que hacen, que datos tocan, que tools usan.

### Que aporta el banco

- Inventario actual de agentes (306+) con owners y responsables
- Clasificacion por dominio (credito, fraude, tesoreria, compliance...)
- Documentacion de herramientas/APIs que cada agente consume

### Que aporta Harness Platform

| Capacidad | Recurso Harness | Que hace |
|-----------|-----------------|----------|
| **Agent List** | `agent` (list, search) | Catalogo de agentes por proyecto/org/account con busqueda |
| **IDP Entity Catalog** | `idp_entity` | Catalogo de servicios (incluyendo agentes) con ownership, lifecycle, tags |
| **IDP Scorecards** | `scorecard`, `scorecard_check` | Medir madurez de cada agente: tiene tests? tiene eval suite? tiene SBOM? tiene owner? |
| **AI Evals Registry** | Registry (UI) | Todos los targets evaluados con su score actual |
| **Audit Events** | `audit_event` | Quien creo/modifico/ejecuto cada agente, cuando, desde donde |

### A 306 agentes, esto es critico

Sin discovery automatizado:
- "Tenemos 306" → Realmente son 340 (34 shadow agents que nadie trackea)
- "Agente #187 usa GPT-4" → Alguien lo cambio a GPT-4o sin avisar
- "Todos nuestros agentes estan evaluados" → 120 nunca pasaron por AI Evals

Con Harness IDP + Scorecards:

```
Scorecard: "AI Agent Maturity"

  [ ] Tiene owner asignado                    (check: catalog ownership)
  [ ] Tiene AI Eval suite configurada         (check: API query)
  [ ] Paso quality gate en ultimo deploy      (check: pipeline execution)
  [ ] Tiene SBOM generado                     (check: SCS artifact)
  [ ] Cost tracking habilitado                (check: CCM AI perspective)
  [ ] Esta en catalogo IDP                    (check: entity exists)

  Score: 4/6 = 67% maturity
```

---

## Fase 5: PROTEGER

> En runtime. Detectar amenazas y proteger agentes en produccion.

### Que aporta el banco

- Conocimiento de vectores de ataque especificos del dominio bancario
- Clasificacion de datos sensibles (PII regulatorio vs PII interno)
- Politicas de retencion y compliance (CNBV, PCI-DSS)
- Respuesta a incidentes (playbooks, escalation, comunicacion)

### Que aporta Harness Platform

| Capacidad | Componente | Que hace |
|-----------|-----------|----------|
| **AI SRE** | Webhooks + Runbooks | Monitor 24/7. Detecta anomalia → ejecuta runbook automatico (Slack, PagerDuty, Jira, zoom bridge, remediacion) en ~12 segundos |
| **Pipeline Rollback** | `rollbackSteps` | Rollback transaccional: canary delete + Jira update + notification + re-deploy |
| **Remediation Pipeline** | Pipeline custom + trigger | Deploy falla → webhook → agent diagnostica → PR → merge → re-deploy. Autonomo |
| **Chaos Engineering** | `chaos_experiment`, `chaos_fault_template` | Validar resiliencia: que pasa si el MCP server muere? Si latencia sube 10x? Si el LLM responde basura? |

### Proteccion runtime con Traceable (complementario)

| Capacidad | Que protege |
|-----------|------------|
| AI Discovery | Descubre agentes desconocidos via eBPF/API inspection |
| AI Firewall | Proxy inline: bloquea prompt injection, redacta PII, valida schema MCP |
| WAAP Custom Signatures | Bloquea SQLi/XSS/CMDi en endpoints del agente |
| Rate Limiting | Protege endpoints AI de abuso |
| AIBOM | Bill of Materials de componentes AI: modelos, tools, datos |

---

## Fase 6: COSTEAR

> Saber cuanto gasta cada agente, por modelo, por sesion, por equipo.

### Que aporta el banco

- Presupuestos por area/equipo/proyecto
- Thresholds de alerta por volumen de uso
- Politicas de aprobacion para override de budget

### Que aporta Harness Platform

| Capacidad | Recurso Harness | Que hace |
|-----------|-----------------|----------|
| **AI Budget** | `ai_budget` (CRUD) | Caps de gasto LLM por equipo/proyecto. Enforcement real: excede budget → requests rechazados |
| **Budget Override** | `ai_budget_override_request` (create/approve/reject) | Solicitud temporal de aumento. Workflow de aprobacion |
| **Budget Overview** | `ai_budget_overview` | Spend actual vs cap por budget |
| **My Consumption** | `ai_budget_consumption` | Cuanto llevo gastado yo (authenticated user) |
| **CCM AI Perspectives** | `cost_perspective` | 13 vistas: por provider, modelo, agente, trace, sesion, principal |
| **SEI AI Metrics** | `sei_ai_usage`, `sei_ai_adoption`, `sei_ai_impact`, `sei_ai_raw_metric` | Metricas de productividad: lineas sugeridas, aceptadas, impacto en PR velocity, adoption por equipo |

### AI Budget: Cap con enforcement

```
Budget: "Equipo Credito"
  Cap: $5,000/mes
  Alert: 80% ($4,000)
  Enforcement: SOFT (alert) o HARD (reject requests)
  Override: Requiere aprobacion de Director

Budget: "Agentes Fraude"
  Cap: $15,000/mes
  Alert: 90%
  Enforcement: HARD
  Override: Requiere CISO approval
```

A 306 agentes sin budget enforcement:
- Agente #47 descubre que puede mejorar accuracy con 10x mas tokens → $50K/mes sin que nadie se entere
- 5 equipos experimentando con GPT-4o → factura de $200K sin visibilidad

---

## Patrones de Escalamiento

### Pattern 1: Agent Templates

El banco tiene 12 tipos de agentes. No crear 306 desde cero — crear 12 templates.

```
Template: "security-scanner"
  Version: 1.2.0
  LLM: claude-sonnet-4-6
  MCP Connectors: harness, github
  Rules: scan-only, no-modify, report-findings
  Eval Suite: security-agent-quality-gate
  Budget: $500/mes

Instancias:
  security_scanner_credito    (project: Credito)
  security_scanner_fraude     (project: Fraude)
  security_scanner_tesoreria  (project: Tesoreria)
  ...
```

Harness `template_v1` permite versionar, compartir a nivel org/account, y actualizar N instancias.

### Pattern 2: Pipeline con BYOA

Los agentes del banco corren DENTRO del pipeline de Harness:

```yaml
- step:
    type: Agent
    name: Agente de Credito (BYOA)
    spec:
      agentName: banco_credito_analyzer
      agentSettings:
        llmConnector: account.bankAnthropic
        mcpConnectors:
          - mcp_harness
          - mcp_core_banking
          - mcp_jira
        modelName: claude-sonnet-4-6
        maxTurns: "30"
```

El agente del banco mantiene su logica, su prompt, su dominio. Harness provee:
- Runtime container con MCP connectivity
- Audit trail de cada accion
- Timeout y failure strategies
- RBAC sobre quien puede ejecutarlo
- Budget tracking por invocacion

### Pattern 3: Evaluacion por tipo de agente

No todos los agentes necesitan las mismas metricas:

| Tipo de Agente | Metricas Criticas | Threshold |
|----------------|-------------------|-----------|
| **Customer-facing** (chat, FAQ) | Hallucination, Toxicity, PII, Latency | Strict: all_must_pass |
| **Code generation** (SAST fix, tests) | Schema Validation, Contains, Correctness | Strict: all_must_pass |
| **Analysis** (fraud, risk) | Faithfulness, Semantic Similarity, PII | Weighted: 90% threshold |
| **Operations** (deploy, remediation) | Schema Validation, Latency, Idempotency | Strict: all_must_pass |
| **Internal tools** (reporting, ETL) | Contains, Latency | Relaxed: 80% threshold |

Cada tipo tiene su suite template en AI Evals. Nuevo agente → hereda suite de su tipo.

### Pattern 4: Governance por scope

```
Account (banco completo)
  |
  |-- OPA Policies: "todo agente debe tener SBOM"
  |-- AI Budget: cap global $500K/mes
  |-- Freeze: no deploys en cierre fiscal
  |-- Secrets: LLM API keys centralizadas
  |
  +-- Org: Banca Retail
  |     |-- RBAC: solo prod con approval
  |     |-- AI Budget: $100K/mes
  |     +-- Project: Credito
  |     |     |-- 15 agentes
  |     |     |-- Eval Suite: credit-agent-quality
  |     |     +-- Budget: $20K/mes
  |     +-- Project: Fraude
  |           |-- 25 agentes
  |           |-- Eval Suite: fraud-agent-quality
  |           +-- Budget: $35K/mes
  |
  +-- Org: Tesoreria
        |-- RBAC: mas restrictivo (datos sensibles)
        +-- ...
```

Harness RBAC, OPA Policies, AI Budget, y Freeze Windows operan a 3 niveles:
account → org → project. Los agentes del banco heredan governance automaticamente.

---

## Lo que cada parte aporta

```
+------------------------------------------+------------------------------------------+
|         EL BANCO APORTA                  |      HARNESS PLATFORM APORTA             |
+------------------------------------------+------------------------------------------+
|                                          |                                          |
|  Dominio bancario en prompts             |  Pipeline determinista (YAML)            |
|  306 agentes funcionando                 |  Agent CRUD + Templates                  |
|  Separacion System 1/2                   |  AI Evals (47+ metricas)                 |
|  CDM/Jev para micro-decisiones           |  Quality gate pre-deploy (AiEval step)   |
|  Datasets de evaluacion del negocio      |  Supply chain (SBOM+SLSA+Signing)        |
|  Golden responses validadas              |  OPA policy enforcement                  |
|  Clasificacion de datos sensibles        |  RBAC granular (account/org/project)     |
|  Approval workflows del negocio          |  AI Budget con enforcement               |
|  Runbooks especificos del dominio        |  Secrets management                      |
|  Conocimiento regulatorio (CNBV)         |  Audit trail inmutable                   |
|                                          |  Canary/Rolling deploy                   |
|  INNER LOOP                              |  Feature Flags progressive rollout       |
|  (Plan + Code + Test local)              |  AI SRE (monitor 24/7 + runbooks)        |
|                                          |  Freeze windows                          |
|                                          |  IDP Scorecards                          |
|                                          |  SEI AI metrics                          |
|                                          |  Test Intelligence                       |
|                                          |                                          |
|                                          |  OUTER LOOP                              |
|                                          |  (Build → Deploy → Verify → Monitor)     |
|                                          |                                          |
+------------------------------------------+------------------------------------------+
|                                          |                                          |
|  Los agentes HACEN y DECIDEN             |  La plataforma VERIFICA, ENFORCA,        |
|  El arnes de arneses COORDINA            |  REGISTRA, RECUPERA, EVALUA,             |
|                                          |  DESCUBRE, PROTEGE, y COSTEA             |
|                                          |                                          |
+------------------------------------------+------------------------------------------+
```

---

## Modelo de Madurez

| Nivel | Nombre | Descripcion | Que tiene el banco |
|:-----:|--------|-------------|-------------------|
| **1** | **Artesanal** | Agentes construidos ad-hoc. Sin estandar. Cada equipo hace lo suyo | Ya superado |
| **2** | **Estructurado** | Templates, nomenclatura, ownership definido. Inner loop maduro | **← Aqui esta** |
| **3** | **Gobernado** | Quality gates, RBAC, OPA, audit trail, budget enforcement. Outer loop maduro | Objetivo con Harness |
| **4** | **Observable** | AI Evals continuo, drift detection, cost optimization, IDP scorecards | Harness + datos del banco |
| **5** | **Autonomo** | Self-healing (AI SRE), auto-scaling budget, progressive rollout automatico | Vision a 12 meses |

El banco esta en **Nivel 2** — expertise excepcional en construccion de agentes,
pero sin el control plane que habilita los niveles 3-5.

Harness no mueve al banco del Nivel 1 al 5. Lo mueve del **2 al 3** — governance —
que es exactamente lo que IT necesita para confiar en el proceso y eliminar los 45 dias.

---

## Checklist: Primer Agente en Harness

Para llevar 1 agente del banco al pipeline de Harness:

```
[ ] 1. Crear agent en Harness (agent create con spec YAML)
[ ] 2. Configurar MCP connectors (herramientas que el agente necesita)
[ ] 3. Crear AI Eval target (endpoint del agente)
[ ] 4. Subir dataset de evaluacion (golden tests del dominio)
[ ] 5. Configurar metric set (metricas relevantes para este tipo de agente)
[ ] 6. Crear evaluation + suite con quality gate
[ ] 7. Agregar step AiEval en pipeline (pre-deploy)
[ ] 8. Agregar step Agent (BYOA) en pipeline
[ ] 9. Configurar AI Budget para el proyecto
[ ] 10. Crear IDP scorecard para tracking de madurez
```

Tiempo estimado: 2-3 horas para el primer agente. 15-30 minutos para cada siguiente
(reutilizando templates).

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| Harness reemplaza los agentes del banco? | **NO.** Los agentes corren DENTRO de Harness (BYOA) |
| Harness reemplaza el arnes de arneses? | **NO.** El orquestador sigue coordinando. Harness agrega governance |
| Que resuelve Harness? | La capa 3: verificar, enforcar, registrar, recuperar, evaluar, descubrir, proteger, costear |
| Por que no se construye con otro agente? | Porque es infraestructura: daemon (24/7), proxy (inline), root of trust (criptografico). Un agente no puede SER ninguna de estas cosas |
| Cual es el impacto inmediato? | IT confia en el proceso → aprueba → los 45 dias se eliminan |
| Por donde empezar? | 1 agente critico → pipeline con BYOA + AI Evals quality gate → POC 2 semanas |
