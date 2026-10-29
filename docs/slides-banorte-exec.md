# Slides Ejecutivas — Banorte (Oct 27, 2026)

---

## SLIDE 1: Que significa operar en un mundo 100% agentico

**Titulo:** "Un caballo, un arnes, y un sistema completo"

```
  Un caballo es autonomo.
  Decide donde pisar, como sortear terreno, que ruta tomar.
  No ejecuta instrucciones paso a paso — razona y actua.

  Un AGENTE opera igual: un modelo de AI con herramientas,
  permisos y memoria. Recibe un objetivo, razona sobre el,
  decide como resolverlo, y entrega un resultado.
  Cada ejecucion puede ser distinta — porque piensa.
```

```
  Un arnes canaliza al caballo.
  No le quita autonomia — le da direccion, limites y proposito.
  La fuerza sigue siendo del caballo. El arnes define hacia donde.

  Un ARNES en AI es el wrapper del agente: system prompt,
  herramientas disponibles, permisos, scope de accion.
  Define QUE puede hacer, CON QUE, y HASTA DONDE.

  El arnes es la primera capa de GOBERNANZA:
  gobernanza del agente individual.
```

```
  Seis caballos con arnes tirando una diligencia.
  Cada uno es autonomo. Cada uno tiene su arnes.
  Pero ahora se necesita coordinacion: cual va adelante,
  como giran juntos, que pasa si uno se detiene.

  Un ARNES DE ARNESES es ese coordinador:
  routing entre agentes, seleccion de modelo (LLM para
  razonamiento complejo, CDM para decisiones rapidas,
  modelos ligeros para clasificacion), secuencia de
  ejecucion, y estrategia de fallback.

  El arnes de arneses es la segunda capa de GOBERNANZA:
  gobernanza de la coordinacion.
```

```
  Un mundo 100% agentico es una ciudad entera
  que opera con este modelo.

  No hay funciones mecanicas — cada proceso es inteligente:

  Coding         →  agente con arnes
  Code review    →  agente con arnes
  Testing        →  agente con arnes
  Security       →  agente con arnes
  Deploy         →  agente con arnes
  Monitoreo      →  agente con arnes
  Remediacion    →  agente con arnes

  Cada funcion del ciclo de vida del software razona,
  se adapta y resuelve. Los arneses de arneses coordinan
  equipos de agentes por dominio. Toda la operacion es
  inteligente de punta a punta.

  Dos capas de gobernanza operan en este modelo:
  el arnes gobierna al agente, el arnes de arneses
  gobierna la coordinacion. Pero quien gobierna
  al SISTEMA COMPLETO?
```

---

## SLIDE 2: La naturaleza de un mundo 100% agentico

**Titulo:** "Indeterminismo, determinismo, y por que se necesitan"

```
  Un caballo piensa. Por eso es valioso.
  Pero por eso mismo, dos caballos con el mismo arnes
  recorriendo la misma ruta no la recorren igual.

  Uno frena antes de la curva. El otro acelera.
  Uno esquiva por la izquierda. El otro por la derecha.
  Los dos llegan — pero el camino fue distinto cada vez.

  Eso es INDETERMINISMO.
  Mismo input, output diferente. Por diseno, no por error.
  Es la propiedad fundamental de cualquier sistema que razona.
```

```
  En un mundo 100% agentico, TODO es indeterminista:

  El agente que codea     →  puede generar dos soluciones
                              distintas al mismo problema
  El agente que revisa    →  puede priorizar seguridad hoy
                              y rendimiento manana
  El agente que testea    →  puede decidir que un caso
                              "no aplica esta vez"
  El agente que deploya   →  puede elegir una estrategia
                              diferente segun su razonamiento

  Cada funcion del SDLC piensa. Cada ejecucion puede variar.
  Eso es lo que hace poderoso al modelo agentico —
  y es tambien lo que hace que la gobernanza no pueda
  ser otro agente opinando. Tiene que ser estructura.
```

```
  Ahora compara con una via de tren.

  La via no piensa. No se adapta. No razona.
  Pero el tren que corre sobre ella hace EXACTAMENTE
  el mismo recorrido, cada vez, sin excepcion.

  Eso es DETERMINISMO.
  Mismo input, mismo output. Siempre.
  Es la propiedad fundamental de un proceso predecible.
```

```
  Un mundo 100% agentico es 100% indeterminista.
  Potente, adaptativo, inteligente.

  Un mundo 100% determinista es 100% predecible.
  Auditable, reproducible, demostrable.

  La pregunta no es cual es mejor.
  La pregunta es como obtener AMBOS:

  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │   La inteligencia del caballo                           │
  │               +                                         │
  │   La predictibilidad de la via                          │
  │               =                                         │
  │   Un sistema que razona Y que se puede gobernar         │
  │                                                         │
  │   El agente decide COMO resolver.                       │
  │   El camino define POR DONDE.                           │
  │   El resultado se VERIFICA independientemente.           │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
```

---

## SLIDE 3: El Control Plane

**Titulo:** "La via sobre la que corren los caballos"

```
  La ciudad de caballos es potente, adaptativa, inteligente.
  Pero la ciudad tambien necesita que cada caballo llegue
  a destino. Siempre. Sin excepciones. Demostrable ante
  quien lo pida.

  No alcanza con que el caballo sea bueno.
  Se necesita la VIA — la estructura sobre la que opera.
```

**Que es un control plane:**

```
  Es la capa INDEPENDIENTE que no ejecuta el trabajo,
  pero garantiza que el trabajo se ejecuto correctamente.

  No es otro agente. No es otro arnes. No es otro caballo.
  Es INFRAESTRUCTURA.

  La diferencia es fundamental:

  Un agente puede EJECUTAR un health check.
  No puede SER un daemon que monitorea 24/7 sin detenerse.

  Un agente puede LLAMAR una API.
  No puede SER un proxy inline que intercepta todo el trafico.

  Un agente puede FIRMAR un archivo.
  No puede SER una root of trust con identidad criptografica
  que sobrevive al agente mismo.

  Hay funciones que requieren infraestructura, no inteligencia.
  El control plane ES esa infraestructura.
```

**Por que es importante — que resuelve:**

```
  En la ciudad de caballos, quien garantiza que:

  ¿La ruta se cumplio?
  El caballo razona y elige su camino. El control plane
  define las estaciones obligatorias. No se puede saltar
  una estacion — esta en la estructura, no en la decision.

  ¿El resultado es correcto?
  El caballo entrega la carga. El control plane verifica
  con mediciones independientes, no con la opinion del
  caballo que la entrego.

  ¿Se puede demostrar que ocurrio?
  El caballo no escribe su propio registro de entrega.
  El control plane registra de forma inmutable, independiente
  de quien ejecuto. El agente no puede alterar el audit trail.

  ¿Si un caballo falla a mitad de camino?
  El control plane detecta la falla, ejecuta un plan
  de contingencia, y notifica. No espera a que otro
  caballo se de cuenta.
```

**Como lo hace — las 3 capas del sistema completo:**

```
  ┌─────────────────────────────────────────────────────────────┐
  │                                                             │
  │  CONTROL PLANE                                              │
  │  Define el camino (determinista). Enforcea las estaciones   │
  │  obligatorias. Verifica resultados con metricas, no con     │
  │  opiniones. Registra todo de forma inmutable. Recupera      │
  │  si algo falla. Opera 24/7 como infraestructura.            │
  │                                                             │
  │  No reemplaza a ningun agente — es la capa donde            │
  │  los agentes corren con confianza enterprise.               │
  │                                                             │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  ARNES DE ARNESES (orquestacion)                            │
  │  Coordina agentes: routing, seleccion de modelo,            │
  │  secuencia, fallback. El cerebro indeterminista             │
  │  que decide COMO se resuelve cada tarea.                    │
  │                                                             │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  AGENTES + TOOLS (ejecucion)                                │
  │  Los caballos. Codean, testean, escanean, deployan,         │
  │  diagnostican, remedian. Cada uno con su arnes.             │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘

  Los agentes aportan la inteligencia (indeterminista).
  El control plane aporta la garantia (determinista).
  Los arneses de arneses coordinan entre ambos.

  Juntos: un sistema que razona Y que se puede gobernar.
```

**El control plane completa al sistema agentico:**

```
  Los agentes aportan          El control plane aporta

  Creatividad                  Reproducibilidad
  Adaptacion                   Auditabilidad
  Razonamiento                 Enforcement estructural
  Velocidad                    Verificacion independiente
  Resolucion autonoma          Continuidad operativa 24/7
                               Identidad criptografica
                               Registro inmutable

  No son fuerzas opuestas — son complementarias.
  Cada una cubre lo que la otra no puede.
```

**El nombre lo dice:**

```
  "Harness" = arnes.

  Un arnes no reemplaza al caballo.
  Canaliza su fuerza hacia un destino confiable.

  El control plane no reemplaza a los agentes.
  Es la via sobre la que corren — con governance,
  auditoria, seguridad y confianza enterprise.
```

---

## SLIDE 4: Harness como Control Plane — La tercera capa de gobernanza

**Titulo:** "Gobernanza del agente, de la coordinacion, y del sistema"

```
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │          HARNESS — TERCERA CAPA DE GOBERNANZA (control plane)            │
  │          Gobernanza del sistema completo: determinista,                   │
  │          independiente, estructural                                       │
  │                                                                          │
  │  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
  │    QUIEN puede hacer QUE                                               │
  │  │                                                                     │  │
  │    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
  │  │ │ AI Governance  │  │  AI Evals      │  │  AI Budget     │         │  │
  │    │ (OPA)          │  │                │  │                │         │
  │  │ │ Que modelos,   │  │  El output del │  │  Cuanto gasta  │         │  │
  │    │ que tools,     │  │  agente es     │  │  cada agente,  │         │
  │  │ │ que permisos   │  │  correcto?     │  │  por modelo,   │         │  │
  │    │ puede usar     │  │  Alucinacion?  │  │  por ejecucion │         │
  │  │ │ cada agente    │  │  PII? Calidad? │  │                │         │  │
  │    └────────────────┘  └────────────────┘  └────────────────┘         │
  │  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
  │                                                                          │
  │  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
  │    QUE hay y de DONDE viene                                            │
  │  │                                                                     │  │
  │    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
  │  │ │ Security       │  │  Supply Chain  │  │  Audit Trail   │         │  │
  │    │ Testing (STO)  │  │  Security(SCS) │  │                │         │
  │  │ │ SAST, SCA,     │  │  SBOM, AIBOM,  │  │  Registro      │         │  │
  │    │ Secrets, DAST  │  │  firma, SLSA   │  │  inmutable de  │         │
  │  │ │ — detecta y    │  │  attestation   │  │  cada paso,    │         │  │
  │    │ bloquea        │  │  — que AI hay  │  │  cada agente,  │         │
  │  │ │                │  │  en produccion │  │  cada decision │         │  │
  │    └────────────────┘  └────────────────┘  └────────────────┘         │
  │  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
  │                                                                          │
  │  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
  │    PIPELINE — la via determinista                                      │
  │  │                                                                     │  │
  │    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌───────────────┐    │
  │  │ │  BUILD   │──▶│  TEST    │──▶│  SECURE  │──▶│  DEPLOY       │    │  │
  │    │          │   │  + EVAL  │   │  + SIGN  │   │               │    │
  │  │ └──────────┘   └──────────┘   └──────────┘   │ Feature Flags │    │  │
  │                                                  │ Canary        │    │
  │  │  Agentes corriendo DENTRO de la via:          │ CV (ML)       │    │  │
  │                                                  │ AI Evals Live │    │
  │  │  ┌────────┐ ┌────────┐ ┌────────┐            │ Rolling       │    │  │
  │    │ Coding │ │ Review │ │Securit│            └───────────────┘    │
  │  │ │ Agent  │ │ Agent  │ │ Agent │                                 │  │
  │    └────────┘ └────────┘ └────────┘                                │
  │  │                                                                 │  │
  │    Cualquier modelo: Claude, GPT, Gemini, Llama, propios           │
  │  │ Cualquier orquestador: tu arnes de arneses coordina dentro      │  │
  │  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
  │                                                                          │
  │  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
  │    RUNTIME — gobernanza 24/7 (infraestructura, no agentes)             │
  │  │                                                                     │  │
  │    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
  │  │ │ AI Firewall    │  │ AI Discovery   │  │ AI SRE Agent   │         │  │
  │    │ Proteccion de  │  │ Inventario     │  │ Diagnostico y  │         │
  │  │ │ APIs AI en     │  │ automatico de  │  │ remediacion    │         │  │
  │    │ tiempo real    │  │ agentes, MCP   │  │ autonoma en    │         │
  │  │ │ (daemon 24/7)  │  │ servers, tools │  │ produccion     │         │  │
  │    └────────────────┘  └────────────────┘  └────────────────┘         │
  │  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
```

```
  Las 3 capas de gobernanza, juntas:

  CAPA 1  El arnes gobierna al agente individual
          (que puede hacer, con que, hasta donde)

  CAPA 2  El arnes de arneses gobierna la coordinacion
          (routing, secuencia, modelo, fallback)

  CAPA 3  El control plane gobierna al sistema completo
          (enforcement, verificacion, registro, continuidad,
           seguridad, supply chain, costos)

  Cada capa complementa a la anterior.
  Juntas: un sistema agentico con gobernanza enterprise.
```

```
  Demo en vivo sobre:

  DemoBank           App bancaria real (Python/Flask)
  MCP Financial Data Servicio de enriquecimiento AI (MCP Protocol)
  GKE                Kubernetes en produccion
  Prometheus         Metricas en tiempo real
  GitHub             Repositorio + PRs
  Traceable          API Security en runtime
```
