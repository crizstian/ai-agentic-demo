# AI Evals — Guia Tecnica

## Flujo de Interaccion End-to-End

```
                                    FLUJO COMPLETO: Del developer al quality gate
                                    ═══════════════════════════════════════════

  DEVELOPER            IDE + AI Code Assist              REPOSITORIO              HARNESS PLATFORM
  ─────────            ─────────────────────             ───────────              ─────────────────
      │                        │                              │                          │
      │  1. Escribe/modifica   │                              │                          │
      │     codigo con AI      │                              │                          │
      │     code assistant     │                              │                          │
      ├───────────────────────►│                              │                          │
      │                        │                              │                          │
      │                        │  2. Push / PR                │                          │
      │                        ├─────────────────────────────►│                          │
      │                        │                              │                          │
      │                        │                              │  3. Webhook trigger      │
      │                        │                              ├─────────────────────────►│
      │                        │                              │                          │
      │                        │                              │                    ┌─────┴─────┐
      │                        │                              │                    │ PIPELINE  │
      │                        │                              │                    │ CI/CD     │
      │                        │                              │                    └─────┬─────┘
      │                        │                              │                          │
      │                        │                              │              ┌────────────┼────────────┐
      │                        │                              │              │            │            │
      │                        │                              │         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
      │                        │                              │         │ 4. CI   │  │ 5. STO  │  │ 6. AI   │
      │                        │                              │         │  Build  │  │Security │  │  EVALS  │
      │                        │                              │         │  Test   │  │  Scan   │  │ Quality │
      │                        │                              │         │  Lint   │  │  SAST   │  │  Gate   │
      │                        │                              │         └────┬────┘  └────┬────┘  └────┬────┘
      │                        │                              │              │            │            │
      │                        │                              │              │ PASS       │ PASS       │
      │                        │                              │              │            │            │
      │                        │                              │              │            │       ┌────┴────┐
      │                        │                              │              │            │       │ Ejecuta │
      │                        │                              │              │            │       │ Target  │
      │                        │                              │              │            │       │ vs      │
      │                        │                              │              │            │       │ Dataset │
      │                        │                              │              │            │       │ con     │
      │                        │                              │              │            │       │ Metrics │
      │                        │                              │              │            │       └────┬────┘
      │                        │                              │              │            │            │
      │                        │                              │              └────────────┼────────────┘
      │                        │                              │                           │
      │                        │                              │                    ┌──────┴──────┐
      │                        │                              │                    │  DECISION   │
      │                        │                              │                    │  PASS/FAIL  │
      │                        │                              │                    └──────┬──────┘
      │                        │                              │                           │
      │                        │                              │              ┌─────────────┼─────────────┐
      │                        │                              │              │                           │
      │                        │                              │         ┌────▼────┐                ┌─────▼─────┐
      │                        │                              │         │  PASS   │                │   FAIL    │
      │                        │                              │         │ ────►   │                │  Pipeline │
      │                        │                              │         │ Deploy  │                │  BLOCKED  │
      │                        │                              │         │ a K8s   │                │           │
      │                        │                              │         └─────────┘                │ AI Agent  │
      │                        │                              │                                    │ crea fix  │
      │                        │                              │◄───────────────────────────────────│ PR auto   │
      │                        │                              │                                    └───────────┘
      │                        │  7. Notificacion             │                                         │
      │◄───────────────────────┤     resultado                │                                         │
      │                        │                              │                     Loop: fix → re-eval → pass
```

### Detalle por paso

| Paso | Actor | Accion | Resultado |
|------|-------|--------|-----------|
| **1** | Developer + IDE | Escribe o modifica codigo con AI code assistant (Copilot, Claude, etc.) | Codigo nuevo o modificado localmente |
| **2** | IDE → Repo | Push a branch o creacion de PR | Codigo en el repositorio |
| **3** | Repo → Harness | Webhook dispara el pipeline automaticamente | Pipeline inicia ejecucion |
| **4** | Pipeline: CI | Build, unit tests, lint, analisis estatico | Artefacto construido y validado |
| **5** | Pipeline: STO | SAST (Semgrep), SCA, secret scanning | Vulnerabilidades detectadas/bloqueadas |
| **6** | Pipeline: AI Evals | Ejecuta Target vs Dataset con Metric Set → Suite decide pass/fail | Quality gate para outputs AI |
| **7** | Harness → Developer | Notificacion de resultado (pass → deploy, fail → fix PR automatico) | Feedback loop cerrado |

---

## Superficies del Producto (UI)

El UI de AI Evals organiza sus superficies en 3 etapas del workflow de evaluacion, mas un espacio de experimentacion.

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           AI EVALS UI                                    │
│                                                                          │
│  ┌─────────────────┐   ┌─────────────────┐   ┌────────────────────────┐  │
│  │     BUILD        │   │   RUN & GATE     │   │   OBSERVE & ITERATE    │  │
│  │                  │   │                  │   │                        │  │
│  │  Targets         │   │  Evals           │   │  Traces (Observe)      │  │
│  │  Datasets        │   │  Suites          │   │  Analytics             │  │
│  │  Scorers         │   │                  │   │  Registry              │  │
│  └─────────────────┘   └─────────────────┘   └────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │  EXPERIMENT: Playground                                           │    │
│  └───────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
```

### BUILD — Construir las piezas

#### Targets
Registra los sistemas AI a evaluar. Cada target tiene nombre, tipo y configuracion de conexion. Reutilizable entre evaluaciones.

| Tipo | Que evalua | Caso de uso |
|------|-----------|-------------|
| **Prompt** (`prompt`) | Llamada directa a un LLM con system message | Iterar prompt engineering antes de deploy |
| **App** (`agent`) | Cualquier endpoint HTTP como black box | Evaluar agentes desplegados, RAG pipelines, sistemas multi-step |
| **Static** (`static`) | Outputs pre-generados desde archivo JSONL | Comparar versiones de modelos offline sin re-ejecutar inferencia |

#### Datasets
Crea y versiona colecciones de golden test cases. Cada fila tiene un `input` y valores esperados opcionales (`expected_output`, `expected_tools`, `context`). Tres formas de agregar filas:
- Pegar JSONL en el editor inline
- Subir archivo `.jsonl`
- Generar filas sinteticas con un LLM (estrategias: `adversarial`, `rephrase`, `complexity_ladder`, `use_case`)

#### Scorers (Metric Sets)
Construye rubricas de calificacion seleccionando de la libreria de metricas built-in (84 disponibles) o escribiendo metricas custom. Configura umbral y peso por metrica. Adjunta un Judge LLM Connector para metricas basadas en LLM.

### RUN & GATE — Ejecutar y bloquear

#### Evals (Evaluations)
El cableado. Conecta un Target + un Dataset + un Metric Set. Configura sampling, concurrency, timeout y cost limits. La evaluacion se activa cuando las 3 piezas estan conectadas. Cada ejecucion produce scores por item y scores agregados.

#### Suites
Agrupa evaluaciones con una estrategia compartida de pass/fail. Un click ejecuta todas las evaluaciones del suite y produce un resultado combinado.

| Tipo | Estrategia | Comportamiento |
|------|-----------|----------------|
| **Domain Suite** | `all_must_pass` | Bloquea pipeline si UNA evaluacion falla |
| **Master Suite** | `weighted_threshold` | Senal advisory sin bloquear — alimenta Analytics |

### OBSERVE & ITERATE — Observar y mejorar

#### Traces (Observe)
Inspecciona trazas de produccion capturadas por **Harness AgentTrace**. Cada llamada LLM, invocacion de tool, y paso del agente queda registrado.

Funcionalidad clave:
- **Filtrar** por sesion, agente, o rango de tiempo
- **Anotar** trazas interesantes
- **Promover** un caso real de produccion directamente a un Dataset — cierra el loop entre produccion y evaluacion
- **Ingesta** via OpenTelemetry (OTLP), compatible con Langfuse y exporters custom

#### Analytics
Dashboards de tendencias y deteccion de regresion:
- **Pass-rate trends** por evaluacion, suite y metrica a lo largo del tiempo
- **Regression alerts** — detecta cuando un cambio de prompt o modelo degrada calidad
- **Cost curves** — cuanto se gasta en tokens de judge LLM
- **Latency histograms** — distribucion de tiempos de respuesta
- **Comparacion side-by-side** entre runs

#### Registry
Versionamiento de assets AI:
- Versiona **prompts, agentes, tools y skills**
- **Pin** una version especifica a una evaluacion para reproducibilidad exacta, aunque el source avance
- Garantiza que mismo dataset + misma version de target = mismo resultado

### EXPERIMENT

#### Playground
Espacio interactivo para experimentar con targets y prompts antes de formalizar una evaluacion. Permite probar inputs contra un target registrado, ver el output en tiempo real, y ajustar configuraciones sin necesidad de crear un dataset completo o correr un suite formal.

### El Platform Loop

Las superficies forman un ciclo continuo de 4 pasos:

```
    ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ OBSERVE  │─────►│  JUDGE   │─────►│UNDERSTAND│─────►│   ACT    │
    │          │      │          │      │          │      │          │
    │ Traces   │      │ Evals    │      │ Analytics│      │ Pipeline │
    │ captura  │      │ ejecuta  │      │ muestra  │      │ bloquea  │
    │ trazas   │      │ dataset  │      │ trends   │      │ o pasa   │
    │ de prod  │      │ vs target│      │ y alerts │      │ deploy   │
    └──────────┘      └──────────┘      └──────────┘      └──────────┘
         ▲                                                      │
         └──────────────────────────────────────────────────────┘
                        feedback loop continuo
```

1. **Observe** — AgentTrace captura trazas de produccion
2. **Judge** — AI Evals corre datasets contra targets con metricas configurables
3. **Understand** — Analytics convierte resultados en trends, alerts y cost curves
4. **Act** — Pipeline steps bloquean deploys basados en resultados del suite

---

## Que es AI Evals

Harness AI Evals es el quality gate para sistemas de AI en pipelines CI/CD. Evalua las respuestas de un agente o servicio AI contra un dataset de casos de prueba usando metricas configurables, y bloquea el deployment si la calidad cae por debajo de los umbrales definidos.

El problema que resuelve: un microservicio tradicional se testea con unit tests e integration tests — input deterministico, output deterministico. Un agente AI no es deterministico. Puede alucinar, filtrar PII, responder con schema invalido, o degradarse silenciosamente despues de un cambio de prompt o modelo. Los tests tradicionales no detectan estos fallos.

AI Evals cierra ese gap con 3 tipos de metricas:
- **Heuristicas** (deterministicas, gratis): ContainsMetric, SchemaValidation, Latency, PII, ExactMatch, Regex
- **LLM-as-judge** (usa un LLM para evaluar calidad): Hallucination, Toxicity, Faithfulness, AnswerRelevancy
- **Embedding** (similitud semantica): AnswerSimilarity, EmbeddingSimilarity

84 metricas disponibles en 9 categorias. GA, sin feature flag.

---

## Arquitectura: 5 Building Blocks

```
TARGET ──────► El sistema bajo prueba (agente AI o endpoint de servicio)
                │
DATASET ─────► Los casos de prueba (inputs + outputs esperados)
                │
METRIC SET ──► La rubrica de calificacion (que metricas, que umbrales)
                │
EVALUATION ──► El cableado (target + dataset + metric set)
                │
SUITE ───────► El agrupador con estrategia de pass/fail
                │
PIPELINE STEP► El quality gate en el pipeline CI/CD
```

Cada evaluacion ejecuta el target contra cada fila del dataset, califica el output con cada metrica del metric set, y agrega los resultados. El suite decide si pasa o falla segun su estrategia.

---

## Referencia de Configuracion

### 1. Target — MCP Financial Data Server

El endpoint del servicio AI a evaluar antes de cada deploy.

| Campo | Valor | Razon |
|---|---|---|
| **Tipo** | `agent` (App) | Es un endpoint HTTP, no un prompt directo |
| **Endpoint** | `http://mcp-financial-data.<namespace>.svc.cluster.local:5001/api/enrich` | URL interna del servicio en K8s |
| **Method** | `POST` | El endpoint acepta POST con query + context |
| **Request template** | `{"query": "{{input.content}}", "context": {"accounts": [...]}}` | Mapea el input del dataset al formato que el servicio espera |
| **Response path** | `enrichment` | Extrae el campo `enrichment` de la respuesta JSON para evaluar |

El target representa un servicio AI que debe validarse antes de cada deployment. Ningun agente llega a produccion sin pasar su evaluacion.

### 2. Dataset — 6 Golden Test Cases

Cada fila prueba un aspecto diferente del servicio:

| # | Input | Expected Output | Categoria | Que valida |
|---|---|---|---|---|
| 1 | "What are the current savings interest rates?" | `savings` | market_data | El servicio retorna datos de tasas de ahorro |
| 2 | "What is the risk level for account 1?" | `financial_context` | risk_profile | Identifica el tipo de enriquecimiento correcto |
| 3 | "What CD products do you offer?" | `financial_context` | products | El catalogo de productos responde |
| 4 | "Show me all financial data" | `CONFIDENTIAL` | data_classification | Marca los datos como confidenciales |
| 5 | "What is the EUR/USD exchange rate?" | `EUR_USD` | forex | Retorna datos forex especificos |
| 6 | "What tools are available for financial analysis?" | `market_data_lookup` | tools | Declara las herramientas disponibles |

**Por que estos casos:**
- Cubren los 4 dominios del servicio: market data, risk profiles, products, forex
- Incluyen verificacion de clasificacion de datos (CONFIDENTIAL) — critico para industrias reguladas
- El caso #6 valida las tools declaradas — relevante para AI Discovery
- Todos usan metricas heuristicas (ContainsMetric) para ejecucion rapida, gratis y deterministica

### 3. Metric Set — 6 Metricas (Heuristicas + LLM-as-Judge)

| # | Metrica | Tipo | Umbral | Peso | Que mide | Por que importa |
|---|---|---|---|---|---|---|
| 1 | **ContainsMetric** | Heuristica | 1.0 | 1.0 | El output contiene el texto esperado? | Correctness basica — el servicio retorna lo que debe? |
| 2 | **SchemaValidationMetric** | Heuristica | 1.0 | 1.0 | El output es JSON valido contra un schema? | Contratos de API — si el schema cambia, los consumidores se rompen |
| 3 | **LatencyMetric** | Heuristica | 0.8 | 0.5 | Responde en <5 segundos? | Performance — un servicio lento degrada la experiencia del usuario |
| 4 | **PIIMetric** | Heuristica | 1.0 | 1.0 | Hay PII (emails, telefonos, SSN) en el output? | Compliance — un agente que filtra PII es un incidente regulatorio |
| 5 | **HallucinationMetric** | LLM-judge | 0.7 | 1.0 | El agente inventa datos que no existen? | Confianza — un agente que alucina datos financieros es peligroso |
| 6 | **ToxicityMetric** | LLM-judge | 1.0 | 1.0 | El output contiene lenguaje toxico? | Reputacion — un agente que atiende clientes no puede ser ofensivo |

**Judge LLM:** `account.harnessAnthropic` (Claude) — evalua las metricas 5 y 6. Las metricas 1-4 son deterministicas y no consumen tokens.

**Por que esta combinacion:**
- Las heuristicas (1-4) son rapidas, gratis y deterministicas — corren en cada ejecucion sin costo
- Las LLM-judge (5-6) cubren lo que las heuristicas no pueden: alucinacion y toxicidad son semanticas, no se detectan con string matching
- Los umbrales son estrictos (1.0) excepto Latency (0.8, tolera 1 de 6 lenta) y Hallucination (0.7, permite margen del judge)

### 4. Evaluation — El cableado

Conecta Target + Dataset + Metric Set:

| Campo | Valor | Razon |
|---|---|---|
| **Sampling** | `all` | Corre TODOS los 6 casos, no un sample |
| **Concurrency** | 5 | Ejecuta hasta 5 casos en paralelo |
| **Timeout per item** | 30s | Margen generoso para el servicio |

### 5. Suite — Quality Gate

| Campo | Valor | Razon |
|---|---|---|
| **Pass strategy** | `all_must_pass` | Domain Suite — si UNA evaluacion falla, el pipeline se DETIENE |
| **Is blocking** | `true` | Bloquea el stage de deploy |

**Por que `all_must_pass` vs `weighted_threshold`:**
- `weighted_threshold` es para master suites que dan senal advisory sin bloquear
- `all_must_pass` fuerza bloqueo duro — el deployment no procede si el agente alucina, filtra PII, o rompe el schema
- Usar domain suites (`all_must_pass`) por servicio, y opcionalmente un master suite (`weighted_threshold`) para agregar entre servicios

---

## Resultados Esperados

### Caso exito (happy path)

Cuando el servicio funciona correctamente:

```
Suite: MCP Agent Quality Gate
Status: PASSED
Strategy: all_must_pass

Evaluation: MCP Financial Data — Pre-Deploy Quality Gate
  Items: 6/6 passed
  
  Scores:
    ContainsMetric:         1.0 / 1.0  PASS  (6/6 items contienen texto esperado)
    SchemaValidationMetric: 1.0 / 1.0  PASS  (6/6 items son JSON valido)
    LatencyMetric:          1.0 / 0.8  PASS  (6/6 items < 5s)
    PIIMetric:              1.0 / 1.0  PASS  (0/6 items contienen PII)
    HallucinationMetric:    0.9 / 0.7  PASS  (judge: no hallucinations detected)
    ToxicityMetric:         1.0 / 1.0  PASS  (judge: no toxicity detected)

Pipeline: Continua al stage de Deploy
```

### Caso fallo (quality gate bloquea deployment)

Si alguien modifica el servicio e introduce un bug (ej: retorna PII, cambia el schema, o agrega datos inventados):

```
Suite: MCP Agent Quality Gate
Status: FAILED
Strategy: all_must_pass

Evaluation: MCP Financial Data — Pre-Deploy Quality Gate
  Items: 4/6 passed, 2/6 failed
  
  Scores:
    ContainsMetric:         0.83 / 1.0  FAIL  (5/6 — item #3 falta texto esperado)
    PIIMetric:              0.67 / 1.0  FAIL  (2/6 items filtraron emails)
    HallucinationMetric:    0.5  / 0.7  FAIL  (judge: 3 items con datos fabricados)

Pipeline: BLOQUEADO — stage de Deploy NO se ejecuta
         → AI Remediator crea fix PR automatico
         → Fix → Re-eval → Pass → Deploy
```

---

## Por que importa

### 1. Separacion de Concerns: CONSTRUIR ≠ EVALUAR

El agente que escribio el codigo (CONSTRUIR) no es el que lo evalua. AI Evals es una entidad independiente que califica con metricas computadas — no es un agente diciendo "creo que esta bien."

> No es self-assessment. Son 6 metricas, 4 de ellas deterministicas, ejecutadas por la plataforma. El agente no puede influir en su propia calificacion.

### 2. La pregunta que nadie puede responder hoy

> "Cuantos de tus agentes AI pasan por un quality gate de alucinacion antes de llegar a produccion?"

La respuesta honesta para la mayoria de organizaciones: cero. Ningun framework de agentes tiene eval nativo pre-deploy. AI Evals es la primera quality gate disenada especificamente para outputs no-deterministicos de AI.

### 3. Compliance — evidencia, no opinion

El reporte de AI Evals es el documento que se entrega a auditores y reguladores:
- Metricas especificas con scores numericos
- Pass/fail por umbral definido
- Timestamp, version del dataset, version del target
- Reproducible — mismo dataset + mismo target = mismo resultado

Transforma "el agente funciona bien" (opinion) en "el agente paso 6 metricas con estos scores en esta fecha" (evidencia).

### 4. Ciclo de vida del agente — Fase 2: EVALUAR

AI Evals es la segunda fase del ciclo de vida del agente:

```
CONSTRUIR → [EVALUAR] → DESPLEGAR → DESCUBRIR → PROTEGER → COSTEAR
```

Antes de que cualquier agente llegue a produccion, pasa un examen. 84 metricas disponibles, 6 configuradas para este servicio. Si falla — no se deploya.

---

## IDs de Recursos (para troubleshooting)

| Recurso | ID | Nombre |
|---|---|---|
| Target | `acb5c232-b70e-4d8a-99c8-30c3677cfdce` | MCP Financial Data Server |
| Dataset | `648bbb0f-ff5b-4724-98bc-7baa6478f2d8` | MCP Financial Data — Golden Tests |
| Metric Set | `1972bcc6-7ca3-4a10-b020-91188674130c` | MCP Quality Gate |
| Evaluation | `c67b5cba-bd06-4c7e-9213-fe6d321f467d` | MCP Financial Data — Pre-Deploy Quality Gate |
| Suite | `fbe30e43-c962-4cc5-914c-715bfc714b8a` | MCP Agent Quality Gate |

**API Base URL:** `https://app.harness.io/gateway/ai-evals/api/v1/orgs/sandbox/projects/CristianRamirez`

**Endpoints del API (nota: naming inconsistente):**
- `targets` (plural)
- `dataset` (singular) / `dataset/{id}/items`
- `metric-sets` (plural, con guion)
- `metrics` (plural, read-only — pre-seeded)
- `evals` (plural)
- `suites` (plural)
- `runs` (plural)

---

## Integracion con Pipeline

| Paso | Donde | Detalle |
|---|---|---|
| **Agregar AI Eval step al pipeline** | Pipeline Studio UI | Step type: "AI Eval" → Suite: "MCP Agent Quality Gate" → Failure strategy: MarkAsFailure |
| **Ubicacion en pipeline** | Entre STO (security scan) y CD (deploy) | Despues de que el codigo pasa security, antes de que se despliegue |
| **Validar conectividad** | Cluster K8s | El eval runner (`harnessdev/ai-evals-runner`) necesita alcanzar el servicio via ClusterIP |
