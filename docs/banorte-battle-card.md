# Banorte Battle Card — Harness vs 306 Agentes

Preparado para la reunión técnica con Olga Ceja (Dir. Innovación, Banorte).
Fecha reunión: 2026-10-27 (lunes)

---

## 1. Tabla original: Lo que Olga NO tiene

| # | Capacidad | Módulo Harness |
|---|-----------|----------------|
| 1 | Canary/Blue-Green/Rolling deploy real | CD |
| 2 | Supply Chain Security (SBOM, SLSA, attestation) | SCS |
| 3 | Artifact signing + verification | SCS |
| 4 | OPA Policy gates | Governance |
| 5 | Feature Flags progressive rollout | FME |
| 6 | AI Discovery | AI Security |
| 7 | AI Firewall (redaction + blocking) | AI Security |
| 8 | AI Evals (quality gates, 47+ métricas) | AI Evals |
| 9 | AI Budget (enforcement tiers) | CACM |
| 10 | ITSM integration (Jira/ServiceNow) | CD |
| 11 | RBAC + Audit trail | Platform |
| 12 | Secrets management | Platform |
| 13 | Freeze windows | Platform |
| 14 | Test Intelligence | CI |
| 15 | Continuous Verification | CD |
| 16 | Chaos/Resilience Risk Scan | Chaos |
| 17 | IDP Scorecards | IDP |
| 18 | SEI / DORA metrics | SEI |
| 19 | Bring Your Own Agent en pipeline | Agents |
| 20 | AI SRE (detect→remediate) | AI SRE |

---

## 2. Recalificación honesta: ¿Puede Olga replicarlo con vanilla agents?

La pregunta correcta no es "¿puede hacerlo con otra herramienta?" sino "¿puede hacerlo con puro agente + LLM + prompt + herramientas CLI/API genéricas?"

### SÍ puede (9 de 23) — Es lógica de agente

| # | Capacidad | Por qué sí |
|---|-----------|------------|
| 1 | SBOM generation | `syft`/`trivy` son CLI. Un agente puede correrlos y parsear output |
| 2 | OPA policy evaluation | Un agente puede correr `opa eval` contra policies |
| 3 | Feature flags | Un agente puede toggle flags via API/config. Es CRUD |
| 4 | AI Evals | Un agente evaluador puede correr test prompts y medir hallucination/toxicity/PII con LLM-as-judge |
| 5 | ITSM (Jira/ServiceNow) | REST API + prompt. Crear/actualizar tickets |
| 6 | Freeze windows | Checar fecha y negarse a ejecutar. Lógica trivial |
| 7 | Chaos injection | `kubectl delete pod`, `tc qdisc`, `stress-ng`. La inyección es CLI |
| 8 | IDP Scorecards | Aggregar datos de APIs y calcular score. Es ETL + display |
| 9 | DORA metrics | `git log` + timestamps. Es cálculo sobre datos existentes |

### NO puede (12 de 23) — Requiere infraestructura que un agente no puede ser

| # | Capacidad | Por qué no |
|---|-----------|------------|
| 1 | Canary/Blue-Green deploy | Requiere controller loop 24/7 con traffic splitting + health monitoring + rollback atómico. Un agente es invocación puntual, no un daemon |
| 2 | SLSA attestation | Requiere identidad criptográfica verificable por stage. Un agente no tiene identity token — su "certificación" es self-attestation sin valor probatorio |
| 3 | Artifact signing | Keyless signing necesita OIDC identity provider. ¿Con qué identidad firma el agente? Si le das una key, hardcodeaste un secret |
| 4 | OPA enforcement | Evaluar ≠ enforcar. Enforcement = el deploy NO PUEDE proceder si la policy falla. Un agente "decide" no deployar, pero no hay puerta con llave — solo un letrero de "no pasar" |
| 5 | AI Discovery | Descubrir agentes desconocidos requiere eBPF/API gateway inspection. Un agente solo ve lo que ya está inventariado. No puede descubrir lo que no sabe que no sabe |
| 6 | AI Firewall | Proxy inline entre agente y LLM con <5ms latency para redact/block. Un agente no puede interceptar tráfico HTTP de OTRO agente en runtime |
| 7 | AI Budget enforcement | Trackear tokens: sí. CORTAR acceso cuando excede budget: requiere gateway que rechace requests. Un agente puede reportar; no puede cortar la tarjeta de crédito de otro agente |
| 8 | RBAC | ¿Quién decide qué agente puede hacer qué? Un agente administrando permisos es un guardia que se imprime su propia credencial |
| 9 | Audit trail inmutable | Un agente puede escribir logs. ¿Quién garantiza que no los editó? Requiere append-only storage con integridad criptográfica |
| 10 | Secrets management | En el momento que el agente tiene el secret en su contexto, está expuesto — en el prompt, en logs del LLM, potencialmente en training data |
| 11 | Test Intelligence | Grafo de dependencias código→tests construido de miles de builds históricos + análisis estático. No es un prompt — es un compilador |
| 12 | BYOA en pipeline | Es la plataforma misma. Un agente no puede crear el runtime donde corren agentes con governance |

### Parcial (2 de 23)

| # | Capacidad | Lo que puede / lo que no |
|---|-----------|--------------------------|
| 1 | AI SRE | Puede: correr runbooks. No puede: estar escuchando alertas 24/7 (daemon) |
| 2 | Chaos (blast radius) | Puede: inyectar. No puede: contener el radio de explosión |

### Los 3 patrones que un agente NUNCA puede ser

1. **Un daemon** (proceso 24/7): Canary controller, CV, AI SRE detect
2. **Un proxy inline** (interceptor de tráfico): AI Firewall, AI Budget enforce, Secrets injection
3. **Una root of trust** (identidad criptográfica): SLSA, Signing, RBAC, Audit trail

---

## 3. Determinismo vs No-determinismo: El problema de ser 100% agéntico

### El cálculo de probabilidad

- Probabilidad de fallo de 1 agente en 1 ejecución: ~2% (generoso)
- Probabilidad de que al menos 1 de 306 falle: `1 - (0.98)^306 = 99.8%`
- En casi CADA ejecución, al menos un agente hace algo inesperado

### Las 7 cosas que el no-determinismo rompe

| # | Problema | Pipeline determinístico | 100% agéntico |
|---|----------|------------------------|---------------|
| 1 | **Reproducibilidad** | Mismo YAML → mismos steps → mismo log | Mismo prompt → ruta diferente cada vez |
| 2 | **Auditabilidad** | "Pasó steps 4,5,6,7. Aquí los logs" | "El agente evaluó que era seguro" — ¿basado en qué? |
| 3 | **Garantía de ejecución** | Step en YAML = se ejecuta o pipeline falla | Agente puede interpretar, saltarse, o alucinar un step |
| 4 | **Idempotencia** | Mismo input → mismo output | Puede funcionar 99 veces y fallar la 100 |
| 5 | **Costo predecible** | Steps determinísticos = $0 en tokens | CADA decisión consume tokens. × 306 × N/día |
| 6 | **Latencia** | `kubectl apply` en ms | 2-5s de inferencia LLM para decidir qué comando correr |
| 7 | **Dependencia LLM** | Si LLM se cae, solo fallan agent steps | TODO se detiene. 306 agentes = 306 puntos de falla con 1 SPOF |

### El modelo correcto: Determinístico por default, inteligente donde importa

Patrick: 69 steps, 11 AI (16%), 58 determinísticos (84%).

```
PIPELINE (determinístico)
 Build → Test → Scan → Sign → Deploy → Verify
                  │                 │
             ┌────▼────┐      ┌────▼────┐
             │ AI Agent│      │ AI Agent│
             │ Remedia │      │ Rollback│
             │ vuln    │      │ + fix   │
             └─────────┘      └─────────┘

 El pipeline GARANTIZA que los steps se ejecutan.
 Los agentes aportan INTELIGENCIA donde se necesita.
 Si el LLM se cae, solo fallan los agent steps.
```

### La analogía del avión

Un avión tiene piloto automático (determinístico) y piloto humano (inteligente). El piloto automático vuela el 90% del tiempo — predecible, confiable, auditable. El piloto interviene cuando se necesita juicio.

El arnés de arneses de Olga es un avión con 306 pilotos y cero piloto automático.

### La pregunta letal para CNBV

> "¿Puedes demostrar que el proceso que deployó a producción el martes es idéntico al que deployó el jueves?"

- Con pipeline: Sí. Mismo YAML, mismos steps, mismo orden. Aquí están los logs.
- Con 100% agentes: No. Ni siquiera puedes garantizar que se corrieron los mismos steps.

**En un banco regulado por CNBV, un compliance gap es un showstopper.**

---

## 4. Si Olga dice "ya tenemos arneses implementados" — ¿Cómo gana/pierde Harness?

### Regla #1: NUNCA atacar lo que Olga construyó

En el momento que decimos "tus arneses no sirven," ella se cierra y perdemos.

### Donde Olga GANA (reconocer, no pelear)

| # | Ventaja de Olga | Por qué es real | Cómo responder |
|---|----------------|-----------------|----------------|
| 1 | **Dominio bancario embebido** | Prompts con conocimiento CNBV, productos, procesos internos | "Por eso no reemplazamos tus agentes. Queremos que corran dentro de un pipeline con governance" |
| 2 | **Velocidad de iteración** | Cambiar comportamiento = editar prompt. Sin esperar roadmap de vendor | "Harness no toca tus prompts. Es la capa de abajo" |
| 3 | **Sin vendor lock-in en lógica** | Sus agentes son suyos. Cambian de LLM → cambian model ID | "Harness también es model-agnostic" |
| 4 | **Inversión hundida = momentum** | 306 agentes, equipo entrenado, procesos adaptados | "No les pedimos que tiren nada. BYOA = Bring Your Own Agent" |
| 5 | **Customización total** | Cada arnés hecho a medida | "Los agentes nativos de Harness complementan, no reemplazan" |

### Donde Olga PIERDE (y no puede resolver con el agente #307)

| # | Debilidad | Pregunta que expone el gap |
|---|-----------|--------------------------|
| 1 | **¿Quién orquesta al orquestador?** Si falla el meta-orquestador, fallan los 306. No hay safety net arriba | *"Si tu arnés de arneses se cae a las 3am, ¿qué pasa? ¿Tienes un arnés del arnés de arneses?"* |
| 2 | **Maintenance a escala.** 306 prompts + 306 configs + 306 permisos. ¿Versionado? ¿Rollback de prompts? | *"Si cambias el prompt del agente #187 y empieza a alucinar, ¿cómo haces rollback al prompt anterior?"* |
| 3 | **Observabilidad unificada.** ¿Dashboard de qué hacen 306 agentes ahora mismo? ¿Cuál falló? ¿Cuál gasta 10x? | *"Ahora mismo, ¿puedes decirme qué hace el agente #243? ¿Cuánto gastó? ¿Cuántas veces alucinó?"* |
| 4 | **Testing del orquestador.** ¿Tests de integración? Si agregan agente #307, ¿cómo saben que no rompe a los otros? | *"Cuando agregas un agente nuevo, ¿cómo validas que no interfiere con los demás?"* |
| 5 | **Upgrades de LLM.** GPT-5 sale → ¿migran 306 agentes? ¿Testan cada uno? ¿Qué si el modelo nuevo rompe 40? | *"Cuando OpenAI depreca un modelo, ¿cuánto tardas en migrar los 306?"* |
| 6 | **Multi-tenancy.** ¿El equipo de tarjetas puede acceder a agentes de tesorería? ¿Cómo controlan eso? | *"¿El equipo de crédito puede ver/usar los agentes de fraude?"* |
| 7 | **DR / HA.** Si muere el servidor del arnés de arneses, ¿hay réplica? ¿Failover? | *"¿Tienes HA para tu orquestador? Si la instancia muere, ¿en cuánto tiempo vuelves?"* |
| 8 | **Estandarización.** 306 arneses creados por personas diferentes = 306 snowflakes | *"¿Los 306 siguen la misma estructura? ¿Un dev nuevo entiende cualquiera sin preguntar al autor?"* |
| 9 | **La conexión a IT.** 45 días porque sus agentes no hablan con ITSM, K8s, approval gates, proceso de release | *"Tus agentes escriben código en segundos. ¿Por qué toma 45 días llegar a producción?"* |

### Matriz completa: Arnés de Arneses vs Harness Platform

| Dimensión | Arnés de Arneses | Harness Platform | Gana |
|-----------|-----------------|------------------|:---:|
| Lógica de negocio bancario | Prompts con dominio CNBV/Banorte | Genérico | **Olga** |
| Velocidad de cambio en agentes | Editar prompt | Roadmap de vendor | **Olga** |
| Inner loop (escribir código) | Agentes custom | Agentes nativos + BYOA | Empate |
| Outer loop (CI/CD/Deploy) | Agentes llamando CLI | Pipeline determinístico + agent steps | **Harness** |
| Governance (RBAC, policies) | Custom o inexistente | Nativo, granular, auditable | **Harness** |
| Security (supply chain) | Agente corriendo scanners | SBOM+SLSA+Signing integrado | **Harness** |
| Security (AI agents) | No sabe qué hacen sus agentes en runtime | AI Discovery + Firewall + Evals | **Harness** |
| Compliance (CNBV) | No puede probar reproducibilidad | Pipeline determinístico + audit trail | **Harness** |
| Cost management | No sabe cuánto gasta cada agente | AI Budget con enforcement | **Harness** |
| Observability | Custom dashboards (si existen) | Vista unificada pipelines + agentes | **Harness** |
| Secrets | Probablemente env vars o config | Vault-grade, fuera del contexto del agente | **Harness** |
| Disaster Recovery | Depende de implementación | SaaS con HA/DR built-in | **Harness** |
| Escalabilidad (306→1000) | Maintenance lineal por agente | Agentes dentro de pipeline = solo config | **Harness** |
| Time to production | 45 días (bottleneck IT) | Minutos (pipeline conecta con IT/ITSM) | **Harness** |
| Independencia de vendor LLM | Cambian model ID | Model-agnostic también | Empate |

**Score: Olga 2, Empate 2, Harness 11**

### La pregunta #9 gana la conversación

Todas las demás debilidades Olga puede argumentar "lo puedo construir" o "ya lo estoy resolviendo." Pero la #9 — la conexión a IT — es la que ya le duele. Ella misma lo dijo: 45 días.

> "Tus 306 agentes son los mejores del mundo generando código y tomando decisiones. Pero no hablan con Kubernetes, no hablan con ServiceNow, no firman artifacts, no pasan approval gates de IT. Harness es el traductor entre tu cerebro (los agentes) y el cuerpo (IT/infra/governance). Sin ese traductor, seguirán siendo 45 días."

### Manejo de conversación técnica feature-por-feature

1. **Validar:** "Tu implementación de [X] es impresionante. ¿Cuánto tiempo les tomó?"
2. **Escalar:** "Multiplica eso × 20 capacidades. ¿Cuánto tiempo y equipo?"
3. **Costo total:** "Cada capacidad custom es código que mantienes. Ya tienes equipo dedicado a maintenance de 306 agentes. ¿Quieres agregar 20 sistemas de infra custom?"
4. **ROI real:** "El tiempo que gastas construyendo infra de delivery es tiempo que NO gastas construyendo agentes de negocio. Harness te libera para enfocarte en lo que diferencia a Banorte: el conocimiento bancario"

---

## 5. Si aparece LLM vs Jev vs CDM — El espectro de inteligencia

### La arquitectura de Olga: 3 capas

| Capa | Qué es | Velocidad | Costo | Determinismo |
|------|--------|-----------|-------|:---:|
| **LLM** (System 2) | GPT-4/Claude — planificación cognitiva | 2-5s | $$$ | ~95% |
| **CDM** (Constrained) | Modelos pequeños, output forzado a schema | Rápido | $ | ~99.5% |
| **Jev** (System 1) | TypeSafe AI — choice/score/nle | 70-500ms | ¢ | ~99.9% |

### Qué argumentos DEBILITA CDM/Jev

| Argumento original | Impacto | Status |
|---|---|:---:|
| "Cada decisión consume tokens caros" | CDM/Jev son 200-400x más baratos | Debilitado |
| "Latencia 2-5s por decisión" | Jev en 70-500ms | Debilitado |
| "Output impredecible" | CDM fuerza output a lista cerrada / JSON | Parcialmente debilitado |
| "Si LLM se cae, todo para" | Solo para Capa 3; Jev/CDM siguen | Debilitado |

### Qué argumentos SIGUEN INTACTOS

- Los 12 gaps de infraestructura (daemon, proxy, root of trust)
- Reproducibilidad (99.9% ≠ 100%)
- Auditabilidad CNBV ("eligió opción A con 87% confianza" no es auditable)
- Los 45 días (CDM/Jev no tienen nada que ver con el bottleneck de IT)
- Governance de 306 agentes

### Qué argumentos EMPEORA para Olga

1. **Triple complejidad:** 306 agentes × 3 tiers = ~918+ configs (prompts + CDM training data + Jev schemas + routing logic)
2. **Triple vendor dependency:** OpenAI/Anthropic + CDM custom/vendor + TypeSafe AI (startup de 2 años — riesgo para banco regulado)
3. **Testing combinatorio:** Validar coherencia LLM↔CDM↔Jev por agente. Upgrade en una capa puede romper otra
4. **Observabilidad 3D:** ¿Falló el LLM, el CDM, o Jev? ¿En qué capa de qué agente?

### El espectro de decisiones

```
Determinístico ◄──────────────────────────────► No-determinístico

Pipeline step      Jev/CDM            LLM
(YAML/JEXL)        (constrained)      (generativo)
$0, 0ms            $0.001, 70ms       $0.10, 3s
100% reproducible  99.9%              ~95%

     ▲                                    ▲
   Harness                          Agentes de Olga
   usa esto                         todo vive aquí
```

CDM/Jev son un intermedio inteligente entre LLM y determinismo. Pero: ¿para qué el intermedio si puedes tener determinismo puro para lo que no necesita inteligencia?

### Manejo de conversación

1. **Validar:** "La separación System 1/System 2 es exactamente Kahneman. Están años adelante de la mayoría"
2. **Reframear:** "La pregunta no es si CDM/Jev es mejor que LLM — claramente lo es. Es: ¿por qué usar un modelo probabilístico para decisiones que pueden ser determinísticas?"
3. **Converger:** "Donde SÍ necesitas AI, tus agentes con LLM+CDM+Jev corren DENTRO de nuestro pipeline. Lo mejor de ambos mundos"

### Línea de cierre LLM/CDM/Jev

> "Construiste inteligencia en 3 niveles. Eso resuelve COSTO y VELOCIDAD. No resuelve CONFIANZA. Un CDM que elige con 99.9% sigue siendo una apuesta — y un banco no apuesta en producción. Harness te da el 100%: lo determinístico es determinístico. Lo que necesita inteligencia, usa tus agentes."

### Preguntas que exponen gaps

- *"¿Tienen CI/CD para sus CDMs? ¿Cómo testan un CDM nuevo antes de ponerlo en 306 agentes?"*
- *"TypeSafe AI tiene 2 años. ¿Plan de contingencia si cierra en 2028?"*
- *"Cuando un agente falla, ¿saben si fue el LLM, el CDM, o Jev?"*
- *"¿Cuántas decisiones que hoy pasan por Jev podrían ser un if/else determinístico?"*

---

## 6. Inner Loop vs Outer Loop — Dónde juega Harness

### El SDLC tiene 2 mitades

```
INNER LOOP (Plan + Code)              OUTER LOOP (Delivery)
Developer en su IDE                    Todo después del git push

 Planear → Escribir → Test local       Build → Test → Scan → Sign →
                                       Deploy → Verify → Monitor →
                                       Incident → Rollback → Remediate

 ◄── Olga juega fuerte ──►             ◄──── Harness juega aquí ────►
 (Harness NO compite)                  (Olga CREE que también)
```

### "Ya tengo agentes de delivery" — HACER vs SER

| Agente de Olga | Harness |
|---|---|
| LLAMA a docker build | ES el build system |
| LLAMA a kubectl apply | ES el deployment controller |
| LLAMA a trivy scan | ES el security pipeline |
| LLAMA a API de Jira | ES el approval workflow |
| CORRE pytest | ES el test orchestrator |
| HACE curl al health check | ES el verification engine |

Un agente que LLAMA kubectl apply no es un deployment controller. Es un usuario de kubectl — como un developer en su terminal.

### 10 cosas que separan "llamar herramienta" de "ser la plataforma"

1. **Estado persistente** — Agente muere al terminar. Harness recuerda qué está deployado dónde, qué versión, qué artifact
2. **Concurrencia** — 2 agentes deployando al mismo ambiente = race condition. Harness tiene queue + environment locking
3. **Transaccionalidad** — Agente falla en paso 3: ¿quién deshace pasos 1-2? Harness hace rollback transaccional
4. **Ejecución garantizada** — Agente DECIDE qué steps correr (puede saltarse uno). Pipeline YAML = estructuralmente imposible saltarse
5. **Continuidad 24/7** — Agente se invoca y se va. Harness está corriendo siempre (CV, monitoring, alertas)
6. **Environment management** — ¿Quién controla qué cluster es dev/staging/prod? ¿Quién puede deployar a prod? Harness: RBAC por environment
7. **Artifact lineage** — ¿Qué commit produjo qué imagen? ¿Quién firmó? Harness mantiene cadena de custodia completa
8. **Failure recovery** — Agente crash = estado desconocido. Harness: retry policies, failure strategies, resume from failed stage
9. **Versioning del proceso** — Delivery process en 40 prompts distribuidos vs 1 YAML en git con PR review y rollback
10. **Blast radius control** — Agente + credenciales de prod + alucinación = `kubectl delete namespace production`. Harness: OPA + RBAC + approval gates

### La pirámide de delivery

```
                 ┌─────────────┐
                 │  DECISIÓN   │ ← AI: "remedia esta vuln"
                 ├─────────────┤
                 │ ORQUESTACIÓN│ ← PLATAFORMA: pipeline, gates, locks
                 ├─────────────┤
                 │ EJECUCIÓN   │ ← INFRAESTRUCTURA: K8s controller,
                 │             │   traffic, health, signing
                 └─────────────┘

Olga:   [DECISIÓN ✅] [ORQUESTACIÓN ❌] [EJECUCIÓN ❌]
Harness:[DECISIÓN ✅] [ORQUESTACIÓN ✅] [EJECUCIÓN ✅]
```

Olga tiene la punta de la pirámide. Le faltan los 2 pisos de abajo.

### Outer loop fase por fase

| Fase | Agente de Olga | Harness | Gana |
|------|---------------|---------|:---:|
| Build | `docker build` CLI | Build con cache, layer optimization, multi-arch | **Harness** |
| Unit Test | `pytest` CLI | Test Intelligence — solo tests afectados | **Harness** |
| SAST/SCA | Scanner CLI + sugiere fix | Step nativo + AI remediator + gate bloqueante | Empate |
| Artifact | `docker push` | Push + sign + SBOM + attestation + lineage | **Harness** |
| Approval | Llama API Jira/Slack | Approval group + RBAC + timeout + escalation | **Harness** |
| Deploy | `kubectl apply` (all-or-nothing) | Canary 25→50→100% + health verification + rollback atómico | **Harness** |
| Verify | `curl /health` (puntual) | Continuous Verification: estadística pre/post durante bake time | **Harness** |
| Rollback | `kubectl rollout undo` | Rollback transaccional + remediación + Jira + notification | **Harness** |
| Incident | Lee alerta, ejecuta runbook | AI SRE: monitor 24/7 → detect → correlate → remediate → verify | **Harness** |
| Governance | No tiene / custom frágil | OPA + RBAC + Freeze + Audit + Secrets | **Harness** |

### Línea de cierre

> "Tus agentes de delivery son USUARIOS de herramientas. Harness ES la herramienta. No competimos con tus agentes — los complementamos. Tus agentes DECIDEN. Harness EJECUTA, VERIFICA y GARANTIZA."

---

## 7. Estrategia de reunión — 60 minutos

### Situación

Entramos con una detractora técnica avanzada. Olga no evalúa — defiende su territorio. Tiene 306 agentes, arquitectura System 1/2, CDM/Jev, y su posición es "mis agentes + GitLab ya cubren delivery." Ya vio slides de Harness en la primera sesión.

El bottleneck real no es técnico — es organizacional. Sus agentes generan en segundos pero IT tarda 45 días porque no puede auditar ni controlar lo que los agentes hacen.

### Objetivo

Que Olga entienda:
- Sus agentes y arnés de arneses operan en DECISIÓN y ORQUESTACIÓN
- No existe CONTROL PLANE en su ecosistema — la tercera capa
- Esa capa ausente causa los 45 días
- No se construye con más agentes — es infraestructura
- Harness es esa capa, y sus 306 agentes operan DENTRO sin perder nada

### Lo que NO es el objetivo

- No convencerla de que Harness es mejor que sus agentes
- No hacerle tour de features
- No cerrar venta ni hablar pricing
- No demostrar que su arquitectura está mal

### Los 3 mensajes que tienen que aterrizar

1. Hay 3 capas en delivery: arnés, arnés de arneses, y control plane. Tú tienes 2 de 3
2. Los 45 días existen porque IT no puede auditar ni controlar lo que tus agentes hacen. La capa que falta le da esa confianza a IT
3. Esa capa no se construye con otro agente. Es infraestructura. Es la carretera, no otro caballo

### Flujo completo

```
FASE 1         FASE 2              FASE 3        FASE 4
CONEXIÓN       FRAMEWORK           DEMO          CONVERGENCIA
10 min         10 min              30 min        10 min
Ella habla     3 capas + gap       Evidencia     Siguiente paso
                                   en vivo
                                   (ciclo de vida + separación
                                   de concerns integrados
                                   en narración)
```

Plan B (si Olga dice "muéstrame directo"):
- Comprimir Fase 2 a 3 min (solo dibujar 3 capas, sin tabla)
- Integrar separación de concerns y ciclo de vida como narración durante el demo
- Misma Fase 1 y 4

---

### FASE 1 — CONEXIÓN (10 min)

Objetivo: Que Olga sienta que estamos en su nivel técnico y que no venimos a vender.

Apertura:

> "Olga, sabemos que tienen un ecosistema de más de 300 agentes con separación System 1 / System 2, CDMs para micro-decisiones, y un meta-orquestador que coordina todo. Antes de entrar en Harness, nos gustaría entender cómo fluye un cambio — desde que un developer lo inicia hasta que llega a producción. ¿Nos puedes caminar por ese flujo?"

Por qué funciona:
- Mencionamos CDM, System 1/2 — demuestra que hicimos tarea
- Le damos el micrófono. Ella habla de lo que construyó — baja la guardia
- La pregunta end-to-end la fuerza a recorrer inner loop (donde brilla) Y outer loop (donde están los gaps)
- Cuando llegue a "y luego IT tarda en aprobar," el dolor se expone solo

Preguntas de profundización (SIN corregir, solo preguntar):
- "¿Y si el deploy falla fuera de horario?"
- "¿Cómo saben qué agente hizo qué cambio?"
- "¿Quién verifica que el security scan efectivamente se corrió?"

No señalar gaps. Solo preguntar. Ella misma nota dónde las respuestas son débiles.

---

### FASE 2 — FRAMEWORK: LAS 3 CAPAS (10 min)

Objetivo: Establecer UN concepto — la tercera capa — que haga que todo el demo tenga sentido. Sin esto, el demo es "otro CI/CD." Con esto, el demo es evidencia de una capa que Olga no tiene.

Todo se DIBUJA en vivo (whiteboard, papel, pantalla compartida). No slides. Se construye como si estuvieras procesando lo que ella dijo.

**Paso 1 — Reflejar lo que escuchamos (2 min):**

> "Olga, déjame verificar que entendí. Veo 2 capas en lo que describiste:"

Dibujar:

> "Capa 1: Cada agente tiene su arnés — su modelo, sus tools, su prompt, sus permisos. 306 de estos. Esto responde: ¿qué puede hacer ESTE agente?"

> "Capa 2: Arriba está el arnés de arneses — el orquestador que decide qué agente hace qué, cuándo, con qué modelo. Esto responde: ¿quién hace qué y en qué orden?"

> "¿Estoy entendiendo bien?"

Pausa. Olga confirma, corrige, agrega. Ahora es SU diagrama.

**Paso 2 — La pregunta que abre el gap (3 min):**

> "OK. Hay una tercera pregunta que ninguna de estas dos capas responde: ¿se hizo correctamente? ¿Fue autorizado? ¿Se puede probar? ¿Qué pasa si falla?"

Dibujar espacio vacío:

> "Tus agentes deciden. Tu orquestador coordina. ¿Pero quién GARANTIZA?"

Preguntas que integran separación de concerns (NO como bloque separado — como parte del ejercicio de las 3 capas):

> "Cuando el agente 47 dice 'ya corrí el scan' — ¿quién verifica que se corrió? ¿Es el mismo agente o es independiente?"

> "Si un agente quiere saltarse un paso — ¿quién lo impide? ¿Otro agente?"

> "El audit trail — ¿lo escriben los propios agentes? En tu banco, ¿el cajero audita su propia transacción?"

La analogía bancaria sale NATURAL aquí — no como lección, sino como espejo de lo que ella ya sabe. Es SU expertise aplicada a SU problema.

NO respondemos. Dejamos que Olga responda.

- Si dice "el arnés de arneses" → "¿Quién controla al arnés de arneses?"
- Si dice "tenemos logs" → "¿Los escriben los propios agentes?"
- Si dice "no lo tenemos" → perfecto, descubrió el gap
- Si dice "GitLab" → "GitLab es un tool. ¿Quién gobierna a los agentes mientras lo usan?"

**Paso 3 — Completar el framework (3 min):**

Dibujar la tercera capa:

> "Hay una tercera capa que no es agente ni orquestador. Es infraestructura independiente."

La tabla que aterriza:

| | Arnés | Arnés de Arneses | Control Plane |
|---|---|---|---|
| **Qué es** | Wrapper de 1 agente | Orquestador de N agentes | Infraestructura de delivery |
| **Pregunta** | ¿Qué puede hacer? | ¿Quién hace qué? | ¿Se hizo bien? ¿Es auditable? |
| **Analogía** | Rienda de un caballo | Cochero de la carreta | Carretera + leyes + patrulla |
| **¿Se construye con más agentes?** | — | Sí | **NO** |

> "El cochero dirige los caballos. Pero no construye la carretera, no pone semáforos, no patrulla, no emite licencias. Son funciones de infraestructura que existen independientemente del cochero."

**Paso 4 — Transición directa al demo (2 min):**

> "Los 45 días existen porque IT no tiene esa tercera capa. No hay cómo verificar, enforcar, registrar, ni recuperar de forma independiente. Eso es lo que vamos a ver ahora — funcionando en vivo."

NO explicar el ciclo de vida del agente aquí. Se presenta como narración DURANTE el demo (ver Bloques 1-4).

---

### FASE 3 — DEMOSTRACIÓN (30 min)

Objetivo: Mostrar el control plane y el ciclo de vida del agente funcionando. Cada momento del demo mapea directamente a las 3 capas. El ciclo de vida del agente (Construir → Evaluar → Desplegar → Descubrir → Proteger → Costear) se introduce como narración durante los bloques, NO como concepto previo.

Transición:

> "Voy a llevar un agente AI — un MCP server financiero — desde código hasta producción. En cada paso quiero que notes dos cosas: quién toma la decisión, y quién GARANTIZA que se hizo bien."

#### Bloque 1 — CONSTRUIR + VERIFICAR (8 min)

Narración de ciclo de vida al inicio del bloque:

> "Fase 1 del ciclo de vida de un agente AI: CONSTRUIR. El código se escribe, se testea, se escanea. Pero a diferencia de un microservicio normal, un agente AI tiene riesgos específicos — secrets hardcodeados, supply chain comprometida, vulnerabilidades que un agente no debería encontrar."

| Momento | Función | Qué se ve | Narración |
|---|---|---|---|
| AI escribe feature + push | HACER | Agente genera código, abre PR | "Esto es inner loop. Tus agentes hacen esto" |
| Pipeline arranca auto | — | Build + tests corren | "Los steps están en YAML. No un agente decidiendo — la estructura del proceso" |
| SAST encuentra vuln crítica | VERIFICAR | Pipeline se DETIENE | "VERIFICAR es independiente de HACER. El agente que escribió el código no es el que lo escanea. Y el scan no recomienda parar — la policy BLOQUEA" |
| AI remediator crea fix | HACER | Agente propone PR con fix | "Otro agente HACE el fix. Pero no puede aplicar su propio fix — necesita approval. Separación de funciones — como en un banco" |

**Punchline:** "El que hace no verifica. El que verifica no puede ser bypaseado."

#### Bloque 2 — EVALUAR (AI Evals quality gate) (5 min)

Narración de ciclo de vida:

> "Fase 2: EVALUAR. Antes de que este agente llegue a producción, pasa un examen. ¿Alucina? ¿Filtra PII? ¿Responde con el schema correcto? ¿Es lo suficientemente rápido? Un microservicio normal no tiene estos riesgos — un agente AI sí."

| Momento | Función | Qué se ve | Narración |
|---|---|---|---|
| AI Eval suite corre pre-deploy | EVALUAR | Quality gate: alucinación, PII, schema, latency | "47 métricas disponibles. Si falla — no se deploya. No es opinión de un agente, son métricas computadas" |
| Eval results | REGISTRAR | Scores por métrica, pass/fail | "Esto es el reporte que le entregas a compliance. Evidencia, no self-assessment" |

**Punchline:** "¿Cuántos de tus 306 agentes pasan por un quality gate de alucinación antes de llegar a producción?"

#### Bloque 3 — DESPLEGAR + RECUPERAR (7 min)

Narración de ciclo de vida:

> "Fase 3: DESPLEGAR. Pero no es kubectl apply — es despliegue controlado con canary, verificación continua, y rollback automático. Si falla, RECUPERAR es inmediato — sin esperar a que alguien invoque un agente a las 3am."

| Momento | Función | Qué se ve | Narración |
|---|---|---|---|
| Supply chain | REGISTRAR | SBOM + firma criptográfica + attestation SLSA | "El artifact se firmó con identidad del pipeline. El agente nunca vio la llave. Cadena de custodia" |
| Canary deploy 25% | DESPLEGAR | Tráfico parcial + health monitoring | "No es kubectl apply. Es tráfico controlado con verificación continua" |
| Canary falla → rollback | RECUPERAR | Rollback atómico automático | "Nadie decidió rollback. El platform comparó métricas pre/post y ejecutó. No es opinión — es estadística" |
| AI remedia → re-deploy | HACER + VERIFICAR | Fix → PR → approval → re-deploy exitoso | "El ciclo: falla → análisis AI → fix → approval → re-deploy. Todo bajo governance" |
| Jira automático | REGISTRAR | Ticket: Created → In Progress → Done | "IT tiene visibilidad completa sin que nadie mande un correo" |

**Punchline:** "RECUPERAR no es un agente que alguien invoca. Es un proceso persistente que responde solo."

#### Bloque 4 — DESCUBRIR + PROTEGER + COSTEAR (5 min)

Narración de ciclo de vida:

> "Fases 4, 5 y 6: lo que pasa DESPUÉS del deploy. Construir, evaluar y desplegar son pre-producción. Descubrir, proteger y costear son 24/7 — el ciclo nunca termina."

| Momento | Función | Qué se ve | Estado | Narración |
|---|---|---|---|---|
| CCM AI Cost perspectives | COSTEAR | 13 vistas: costo por provider, modelo, agente, trace, sesión | **EN VIVO** | "Esto es cuánto gasta cada agente, por modelo, por sesión. ¿Sabes cuánto gastan tus 306?" |
| AI Discovery | DESCUBRIR | MCP server descubierto con tools, datos, risk score | **ROADMAP** (requiere Traceable) | "Con Traceable conectado, descubre tus agentes automáticamente. Qué modelos usan, qué datos tocan, qué tools llaman. Para 306 agentes, esto es crítico" |
| AI Firewall policies | PROTEGER | 14 tipos de amenazas: prompt injection, PII, MCP schema | **ROADMAP** (requiere Kong/Istio) | "En runtime. Si alguien hace prompt injection a tu agente o si tu agente va a enviar PII — se bloquea antes de que llegue al LLM" |

Transparencia sobre roadmap:

> "CCM AI Cost está funcionando ahora. AI Discovery y AI Firewall requieren integrar Traceable — la capacidad existe en GA, la integración con tu infraestructura es un paso adicional. Te muestro las policies y la UI para que veas exactamente qué vas a tener."

**Punchline:** "El ciclo de vida completo: Construir → Evaluar → Desplegar → Descubrir → Proteger → Costear. Pre-deploy + post-deploy, continuo."

#### Bloque 5 — AUDIT TRAIL (5 min) — fusionar con cierre de Bloque 3 si hay presión de tiempo

Abrir la UI de Harness en la ejecución que acaba de terminar:

| Momento | Función | Qué se ve | Narración |
|---|---|---|---|
| Execution log completo | REGISTRAR | Cada step, quién, cuándo, qué input, qué output, qué permiso | "Esto lo escribió el platform. Ningún agente puede editarlo. Aquí está quién hizo qué, cuándo, con qué resultado" |
| Pipeline YAML en git | ENFORCAR | El proceso versionado, con PR review e historial | "Tu proceso de delivery en 1 archivo. Versionado en git. ¿Quieres ver cómo era hace 3 meses? Aquí está el diff" |

**Pregunta de cierre del demo:**

> "Esto es lo que ve IT cuando el control plane existe. Cada paso registrado, cada decisión trazable, cada agente operando dentro de reglas que no puede cambiar. Esto es lo que convierte 45 días en minutos — no velocidad, sino confianza."

---

### FASE 4 — CONVERGENCIA (10 min)

Objetivo: Que Olga conecte los puntos y proponga el siguiente paso.

**Paso 1 — Recapitular con el diagrama de las 3 capas:**

Volver al dibujo de Fase 2. Ahora completarlo con lo que vimos:

```
╔══════════════════════════════════════════════════════╗
║  CONTROL PLANE (lo que acabamos de ver)               ║
║  VERIFICAR · ENFORCAR · REGISTRAR · RECUPERAR         ║
║  + EVALUAR · DESCUBRIR · PROTEGER · COSTEAR           ║
╠══════════════════════════════════════════════════════╣
║  ┌──────────────────────────────────────────────────┐     ║
║  │  ARNÉS DE ARNESES (Olga)                      │     ║
║  │  COORDINAR · ORQUESTAR                        │     ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │     ║
║  │  │ Agente 1 │ │ Agente 2 │ │Agente 306│      │     ║
║  │  │  HACER   │ │  HACER   │ │  HACER   │      │     ║
║  │  └──────────┘ └──────────┘ └──────────┘      │     ║
║  └──────────────────────────────────────────────┘     ║
╚══════════════════════════════════════════════════════╝
```

> "Tus 306 agentes HACEN. Tu arnés de arneses COORDINA. Harness VERIFICA, ENFORCA, REGISTRA, RECUPERA, EVALÚA, DESCUBRE, PROTEGE, y COSTEA. Nadie pierde nada. Se agrega la capa que falta."

**Paso 2 — Pregunta abierta:**

> "Si pudieras operar tus 306 agentes dentro de esto — tus agentes, tus prompts, tu lógica, pero con el control plane — ¿por dónde empezarías?"

Si responde con interés → POC concreto:

| Si dice... | Propón... |
|---|---|
| "El deploy" | POC: Pipeline canary para 1 servicio. 2 semanas |
| "La seguridad de los agentes" | POC: AI Discovery sobre sus agentes. 1 semana |
| "Los 45 días" | POC: Pipeline e2e conectado a su ITSM. 3 semanas |
| "BYOA" | POC: 3 de sus agentes en pipeline Harness. 2 semanas |
| "AI Evals" | POC: Eval suite para 5 agentes críticos. 2 semanas |
| "El costo" | POC: CCM conectado a sus providers LLM. 1 semana |

Si sigue escéptica → no forzar. Dejar demo environment abierto, proponer sesión hands-on.

### Anti-patrones

- NO abrir con slides (ya los vio)
- NO comparar feature por feature (ella gana en inner loop)
- NO decir "somos mejores" ni "te falta algo"
- NO hablar de pricing
- NO criticar CDM/Jev
- NO correr demo sin Fase 2 previa — el demo sin conceptos es "otro CI/CD"
- NO cerrar con pitch. Cerrar con pregunta abierta
- NO enviar deck de follow-up. Enviar el doc de 3 capas como referencia técnica
- NO presentar AI Discovery/Firewall como "ya funcionando" — ser transparente: "la capacidad está GA, la integración con Traceable es un paso adicional"

---

## 8. Configuración técnica del demo — Estado actual

### Ya funciona (solo destacar en narración)

| Capacidad | Cómo se demuestra |
|---|---|
| 5 AI Agents en pipeline | Change Advisor, Test Gen, Security Remediator, QA Analyzer, Manifest Remediator |
| SCS completo | SBOM (CycloneDX) + SLSA attestation + signing keyless + verification + enforcement |
| STO | Gitleaks + HarnessSAST + Semgrep |
| AI SRE | Webhooks build + deploy → detección + runbook |
| Feature Flags | Progressive rollout: QA → Beta → 90% → 100% |
| CCM AI Cost (13 vistas) | GenAI Cost by Provider, Model, Principal, Traces. Vistas Anthropic, OpenAI, GCP AI |
| Jira ITSM | Ticket automático: Created → In Progress → Done |

### Configurado (listo para demo)

| Capacidad | Estado | Detalle |
|---|---|---|
| **AI Evals quality gate** | ✅ Configurado | Target (MCP server endpoint) + Dataset (6 golden tests) + Metric Set (6 métricas: Contains, Schema, Latency, PII, Hallucination, Toxicity) + Evaluation + Domain Suite (`all_must_pass`). Judge LLM: `account.harnessAnthropic` |
| **MCP server funcional** | ✅ Corregido | Endpoint `/api/enrich` alineado con consumer. Acepta `query` + `context`, retorna market data + risk profiles + products + tools. Backward-compatible con `/mcp/financial-data` |

### Pendiente antes del lunes

| Capacidad | Qué falta | Esfuerzo |
|---|---|---|
| **AI Eval step en pipeline** | Agregar step "AI Eval" en Pipeline Studio → suite "MCP Agent Quality Gate" | Bajo — UI, 5 min |
| **Audit trail walkthrough** | Preparar navegación en UI post-ejecución | Bajo — ya existe |
| **Dry run completo** | Ejecutar demo-reset.sh + pipeline e2e + verificar todos los bloques | Medio — 30 min |

### Presentar como roadmap (requiere Traceable)

| Capacidad | Qué necesita | Cómo se presenta |
|---|---|---|
| AI Discovery | Traceable tracing agent (eBPF/Kong/Istio) + TPA v1.65+ | Screenshots + narrativa: "descubre tus 306 automáticamente" |
| AI Firewall | Kong AI Gateway (redaction+blocking) o Istio (blocking) | UI de policies: 14 threat types incluyendo MCP-specific |
| AI Security Testing | Traceable agent | OWASP LLM Top 10 scan contra endpoints AI |
| AI Budget enforcement | Permisos/entitlement en account | Mostrar vistas CCM existentes + explicar enforcement tiers |

### El MCP server como "Agente #307"

Estado actual: Flask REST mock, datos hardcoded, endpoints desalineados con consumer.

Para el demo: representa el ciclo de vida completo de un agente AI en Harness:
1. CONSTRUIR — Pipeline CI lo build, testea, escanea, firma (ya funciona)
2. EVALUAR — AI Evals quality gate pre-deploy (configurar)
3. DESPLEGAR — Canary deploy con CV (ya funciona)
4. DESCUBRIR — AI Discovery lo encuentra (Traceable / screenshots)
5. PROTEGER — AI Firewall policies (screenshots)
6. COSTEAR — CCM AI Cost perspectives (ya funciona, 13 vistas)

Narración: "Esto es UN agente. Imagina esto con tus 306."

---

## Contexto de la cuenta

- **Olga Ceja** — Dir. Innovación, Banorte. Construyó "arnés de arneses" con 306 agentes, capacidad ~1,000
- **Claudia Ignacio** — Directora Adjunta (jefa de Olga). Tiene budget. Habla con CISO
- **Dolor real**: 45 días para llegar a producción (IT/ITSM controla ambientes)
- **Mindset de Olga**: Defensiva. Se cree autosuficiente. Solo en la reunión porque su jefa la mandó
- **Riesgo**: Si mostramos "nuestros agentes son mejores" → se cierra
- **Oportunidad**: Las 12+ cosas que son infraestructura, no lógica — imposibles con agentes

### Narrativa central

> "Los 45 días existen porque IT no puede auditar ni controlar lo que tus agentes hacen. Harness hace que sea auditable y controlable. Cuando IT confía en el proceso, aprueba. Cuando aprueba, llegas a producción."

### Framework central

5 funciones del delivery, separadas por diseño:
- HACER → Agentes de Olga
- COORDINAR → Arnés de arneses de Olga
- VERIFICAR + ENFORCAR + REGISTRAR + RECUPERAR + EVALUAR + DESCUBRIR + PROTEGER + COSTEAR → Harness Platform (control plane)

### Línea de cierre

> "Tus 306 agentes HACEN. Tu arnés de arneses COORDINA. Harness VERIFICA, ENFORCA, REGISTRA, RECUPERA, EVALÚA, DESCUBRE, PROTEGE, y COSTEA. Nadie pierde nada. Se agrega la capa que falta."
