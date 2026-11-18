# AI Software Factory — Guia Completa

> Explicado desde cero: que es, por que cada pieza existe,
> y como inner loop + outer loop + controles empresariales
> forman una factory autonoma.

---

## Parte 0: La Analogia — Una Fabrica de Autos

Antes de hablar de agentes y pipelines, pensemos en una fabrica de autos.

```
  CLIENTE PIDE UN AUTO
         │
         ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  OFICINA DE DISEÑO (Inner Loop)                              │
  │                                                              │
  │  1. Alguien escribe los planos del auto                      │
  │  2. Un ingeniero lo construye en el taller                   │
  │  3. Un inspector de seguridad revisa los frenos              │
  │  4. Un inspector de calidad revisa el acabado                │
  │  5. Un jefe decide: "esta listo" o "arregla esto"            │
  │                                                              │
  │  Output: auto terminado listo para inspeccion oficial        │
  └──────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  LINEA DE INSPECCION (Outer Loop)                             │
  │                                                              │
  │  1. Prueba de emisiones (scanner SAST/SCA)                   │
  │  2. Crash test (tests automatizados)                         │
  │  3. Revision regulatoria (policies OPA)                      │
  │  4. Prueba en circuito (canary deploy)                       │
  │  5. Si pasa todo → se entrega al cliente (produccion)        │
  │                                                              │
  │  Output: auto en la calle o devuelto al taller               │
  └──────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  PLANOS TRANSVERSALES (Controles Empresariales)              │
  │                                                              │
  │  - ¿Quien tiene permiso de entrar al taller? (Identidad)    │
  │  - ¿Donde se guardan las llaves? (Secretos)                 │
  │  - ¿Que materiales puede usar? (Autorizacion)               │
  │  - ¿Se registra cada accion? (Observabilidad)               │
  │  - ¿Como se para todo si hay un problema? (Kill switch)     │
  │                                                              │
  │  Estos controles cruzan AMBOS loops, no viven en uno solo   │
  └──────────────────────────────────────────────────────────────┘
```

**En una software factory:**
- La oficina de diseño = **Inner Loop** (agentes de IA piensan, escriben codigo, revisan)
- La linea de inspeccion = **Outer Loop** (pipelines ejecutan, escanean, despliegan)
- Los controles = **Planos Transversales** (identidad, secretos, datos, compliance)

Ninguno funciona solo. Sin inner loop, nadie escribe el codigo.
Sin outer loop, el codigo nunca llega a produccion de forma segura.
Sin controles, cualquiera puede hacer cualquier cosa.

---

## Parte 1: ¿Por que una Software Factory?

### El problema que resuelve

Sin factory, un agente de IA recibe un prompt y "hace lo que puede":

```
  Humano: "agrega un boton de login"
                │
                ▼
  Agente de IA (solo, sin reglas, sin checks)
                │
                ▼
  Codigo que... quizas funciona? quizas rompe algo?
  quizas tiene vulnerabilidades? quizas no sigue las reglas del proyecto?
```

**Problemas concretos que hemos visto:**

| Problema | Que paso | Como lo resuelve la factory |
|----------|---------|----------------------------|
| **Frankenstein** | 12 tareas, 8 horas de autonomia, 4500 tests pasaron. La app era inutilizable — cada tarea individualmente correcta, pero juntas eran un monstruo | Spec con `how_to_demonstrate`: el agente MUESTRA que funciona, no solo que los tests pasan |
| **Repetir errores** | Un agente usa la Split key incorrecta por tercera vez porque no sabe que ya se resolvio | Brain: memoria persistente con decisiones ya tomadas |
| **Auto-aprobacion** | El mismo modelo que escribio el codigo dice "se ve bien" | Reviewers con modelo DIFERENTE y contexto limpio |
| **Vulnerabilidades** | Agente agrega SQL injection porque "funciona" | Security reviewer (pre-PR) + SAST scanner (post-PR) |
| **Deploy roto** | Codigo funciona local pero rompe en produccion | Pipeline con build, test, scan, canary deploy |

### La solucion: separar PENSAR de EJECUTAR

```
  PENSAR (Inner Loop)               EJECUTAR (Outer Loop)
  ─────────────────                 ──────────────────────

  "¿Que debemos hacer?"            "Construye el container"
  "¿El codigo es seguro?"          "Escanea con Semgrep"
  "¿Cumple la spec?"               "Despliega canary al 20%"
  "¿Apruebo o rechazo?"            "Verifica metricas"

  Agentes de IA razonan             Herramientas ejecutan
  (pueden equivocarse)              (deterministico, binario)

  Resultado: PR lista               Resultado: en produccion
```

**¿Por que separarlos?** Porque un agente puede decir "no hay vulnerabilidades"
y estar equivocado. Un scanner SAST encuentra lo que el agente no vio.
Un agente puede decir "funciona" pero el deploy falla.
El pipeline lo demuestra con tests reales en container.

---

## Parte 2: El Inner Loop — Donde los Agentes Piensan

El inner loop es donde la IA hace el trabajo cognitivo: entender que hay que hacer,
escribir codigo, revisar si esta bien, y decidir si esta listo.

### Vista general

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                         INNER LOOP                              │
  │                                                                 │
  │   Tarea ──→ Brain ──→ Spec ──→ Build ──→ Review ──→ Approve    │
  │              (lee)    Writer    (TDD)   (paralelo)   (decide)   │
  │                                  ▲         │                    │
  │                                  └── fix ──┘                    │
  │                                                                 │
  │   Output: PR lista para pipeline                                │
  └─────────────────────────────────────────────────────────────────┘
```

### Componente 1: El Brain — La Memoria de la Fabrica

**¿Que es?**
Un conjunto de archivos que guardan todo lo que la fabrica ha aprendido.
Decisiones que ya se tomaron, errores que no se deben repetir, y
patrones de codigo que ya funcionan.

**¿Por que existe?**
Sin Brain, cada agente empieza de cero. Imagina un empleado nuevo
que llega cada dia sin recordar nada — cometeria los mismos errores
una y otra vez. El Brain es el "manual de la empresa" para agentes.

```
  SIN BRAIN                              CON BRAIN
  ────────                               ─────────
  Agente: "Voy a usar la key             Agente: (lee brain)
   SPLIT_KEY directamente"               "brain/decisions.md dice:
                                           usar lazy init para Split SDK,
  → Error. Ya se resolvio                  key es HARNESS_SPLIT_KEY"
    hace 3 sesiones.
    El agente no lo sabe.                → Correcto desde el primer intento.
```

**¿Que contiene?**

```
  Brain/
  ├── decisions.md    ← "Usamos Flask, no FastAPI" (y POR QUE)
  │                      "PRs van a secops/ai-agentic-demo-main" (y POR QUE)
  │                      "Canary deploy con 1 replica" (y POR QUE)
  │
  ├── constraints.md  ← "NUNCA modificar CSS existente"
  │                      "NUNCA hardcodear MCP_SERVER_URL"
  │                      "Secretos son type:String, no SecretText"
  │
  └── patterns.md     ← "Lazy init para Split SDK: (codigo ejemplo)"
                         "MCP enrich call: (codigo ejemplo)"
                         "Agent YAML con input para maxTurns: (ejemplo)"
```

**Reglas:**
- **Todos** los agentes lo leen antes de hacer cualquier cosa
- Solo el Approver puede agregar nuevas decisiones (despues de aprobar un cambio)
- Se versiona con git — puedes ver cuando y por que se agrego cada regla

**Analogia:** el Brain es como el reglamento interno de una empresa.
Todos lo consultan, nadie lo ignora, y se actualiza cuando se
descubre algo nuevo importante.

---

### Componente 2: El Spec Writer — El Arquitecto

**¿Que es?**
Un agente que recibe una tarea en lenguaje natural ("agrega un boton de login")
y produce un documento tecnico detallado (spec) que dice EXACTAMENTE que
debe hacer el Builder.

**¿Por que existe?**
Sin spec, el Builder interpreta la tarea a su manera. Si dices "agrega login",
el Builder podria agregar login con Google, con email, con biometricos...
nadie le dijo cual. La spec elimina la ambiguedad.

```
  SIN SPEC                               CON SPEC
  ────────                               ────────
  "Agrega login"                         spec.what_user_can_do:
                                           - "El usuario ve un form con email y password"
  Builder interpreta:                      - "Al hacer submit, se valida contra la DB"
  - ¿Google? ¿Email? ¿Ambos?
  - ¿Donde va el boton?                 spec.must_respect:
  - ¿Que pasa si falla?                   - "No modificar CSS existente"
  - ¿Validacion server-side?              - "Usar Flask-Login, no JWT"
                                           - "Ruta: /auth/login"
  Cada interpretacion del Builder
  es una decision que probablemente      spec.how_to_demonstrate:
  sera incorrecta.                         - cmd: "curl -X POST /auth/login ..."
                                             expect: "302 redirect to /dashboard"

                                         El Builder no tiene que adivinar NADA.
```

**El formato ASDD (Agent Spec Driven Development):**

ASDD nacio de un incidente real (el Frankenstein). Tiene 5 secciones
obligatorias, y la mas importante es `how_to_demonstrate`:

| Seccion | Pregunta que responde | Por que importa |
|---------|----------------------|----------------|
| `what_user_can_do` | ¿Que ve/hace el usuario final? | Define el resultado desde la perspectiva del usuario, no del developer |
| `expected_result` | ¿Que archivos se crean/modifican? ¿Que responde la API? | Resultado verificable, no ambiguo |
| `must_respect` | ¿Que reglas del Brain aplican? | Evita que el Builder viole constraints que ya conocemos |
| `how_to_demonstrate` | ¿Como DEMUESTRO que funciona? | **Anti-Frankenstein**: comandos exactos que prueban el resultado. No "test the endpoint" sino `curl -s localhost:5000/api/version` |
| `evidence` | ¿Que artefactos quedan como prueba? | Screenshots, outputs de curl, pytest results |

**Reglas del Spec Writer:**
- Lee el Brain ANTES de escribir
- NUNCA escribe codigo (solo el blueprint)
- Cada campo vacio en `must_respect` = una decision que el Builder tomara solo (y mal)
- Usa Opus (el modelo mas inteligente) porque razonar sobre requirements es complejo

---

### Componente 3: El Builder — El Constructor

**¿Que es?**
Un agente que recibe un spec aprobado y lo implementa escribiendo codigo,
siguiendo TDD (Test-Driven Development): primero el test, luego el codigo.

**¿Por que existe?**
Porque alguien tiene que escribir el codigo. Pero no "alguien que hace lo que quiere"
— un constructor que sigue planos exactos (la spec).

**¿Por que TDD?**

```
  SIN TDD                                CON TDD
  ───────                                ───────
  1. Escribe codigo                      1. Escribe test
  2. "Se ve bien"                           test_version_endpoint()
  3. Tal vez escribe un test                assert response.status == 200
     (o tal vez no)                         → FALLA (rojo) ✓ esperado
  4. No sabe si cumple la spec
                                         2. Escribe codigo minimo
                                            para que el test pase
                                            → PASA (verde) ✓

                                         3. Self-check: ejecuta
                                            TODOS los tests + los
                                            comandos de how_to_demonstrate
```

**El proceso del Builder en 5 pasos:**

```
  PASO 1: PREPARAR                 PASO 2: PROGRAMAR (TDD)
  ─────────────────                ────────────────────────
  - Leer spec + Brain              - Por cada sub-tarea:
  - Crear branch factory/SPEC-123    1. Escribir test → ROJO
  - Crear ticket en Jira             2. Escribir codigo → VERDE
  - Analizar que archivos tocar      3. Repetir

  PASO 3: VERIFICAR                PASO 4: DEMOSTRAR
  ─────────────────                ────────────────────
  - Correr TODOS los tests         - Ejecutar how_to_demonstrate
    (no solo los nuevos)             del spec (los curl, los comandos)
  - ¿Se rompio algo existente?     - Capturar evidence
                                     (screenshots, outputs)

  PASO 5: ENTREGAR
  ────────────────
  - Commit + push al branch
  - Reportar: "listo para review"
  - NO crear PR (eso lo hace el Approver)
  - NO agregar features extra
```

**Reglas criticas del Builder:**
- **NUNCA agrega features que el spec no pida.** Si el spec dice "boton de login",
  no agrega "boton de login + recuperar password + registro". Solo lo que dice el spec.
- **Si encuentra un hueco en el spec, PARA y pregunta.** No adivina.
- **No crea PR.** Eso es responsabilidad del Approver (separacion de funciones).

---

### Componente 4: Los Reviewers — Los Inspectores

**¿Que son?**
Agentes que revisan el codigo del Builder, pero con 3 propiedades especiales:

1. **Modelo diferente** al del Builder
2. **Contexto limpio** (no ven el razonamiento del Builder)
3. **Scope limitado** (cada uno revisa UNA cosa)

**¿Por que existen?**

```
  SIN REVIEWERS                          CON REVIEWERS
  ──────────────                         ──────────────
  Builder (Opus) escribe codigo          Builder (Opus) escribe codigo
  Builder (Opus) revisa su codigo           │
  Builder: "se ve bien" ← auto-sesgo       ├── Security Rev (Sonnet): "hay SQL injection"
                                            ├── Code Rev (Haiku): "viola constraint #3"
  Es como pedirle al alumno                 └── UX Rev (Sol): "el flujo no tiene sentido"
  que califique su propio examen.
                                         Modelos diferentes = perspectivas diferentes.
                                         Contexto limpio = sin sesgo del Builder.
                                         Scope limitado = cada uno es experto en lo suyo.
```

**¿Por que modelos diferentes?**

> "Si usas Opus para construir y Opus para revisar, el revisor tiende
> a 'entender' las decisiones del constructor y dejarlas pasar.
> Un modelo diferente trae una perspectiva fresca." — RSC Factory

Es como pedir una segunda opinion medica: quieres un doctor diferente,
no el mismo doctor diciendo "si, confirmo lo que dije".

**¿Por que contexto limpio?**

El reviewer NO ve el "proceso de pensamiento" del Builder. Solo ve:
- El diff (que cambio en el codigo)
- El spec (que debia hacer)
- El Brain (que reglas aplican)

Si el reviewer viera el razonamiento del Builder, tenderia a
"entender" por que tomo ciertas decisiones y dejarlas pasar,
incluso si son incorrectas.

**Los 4 reviewers (2 activos, 2 en v2):**

| Reviewer | Modelo | ¿Que revisa? | ¿Que NO revisa? | ¿Por que ese modelo? |
|----------|--------|-------------|-----------------|---------------------|
| **Security** | Sonnet | Inyecciones, bypass de auth, secrets expuestos, CVEs | Naming, estilo, UX | Sonnet es diferente a Opus, bueno en analisis de patrones |
| **Code** | Haiku | Consistencia con Brain, patrones, scope creep, DRY | Seguridad, UX | Haiku es ligero y rapido, la tarea es menos compleja |
| **UX** (v2) | Sol/Codex | Flujo de usuario, coherencia, edge cases | Codigo, seguridad | Cross-harness: perspectiva de otro proveedor |
| **UI** (v2) | Astra | Visual: screenshots, alignment, responsive | Logica, seguridad | Computer use: puede "ver" la pantalla |

**Output de cada reviewer:** JSON estructurado, no texto libre:

```json
{
  "spec_id": "SPEC-123",
  "reviewer": "security",
  "verdict": "FAIL",
  "findings": [
    {
      "severity": "HIGH",
      "type": "SQL Injection",
      "file": "app/routes/auth.py",
      "line": 42,
      "evidence": "user input concatenated directly into query",
      "fix": "use parameterized query"
    }
  ]
}
```

---

### Componente 5: El Approver — El Juez

**¿Que es?**
El agente que toma la decision final: ¿el codigo esta listo para crear PR,
o hay que mandarlo de regreso al Builder?

**¿Por que existe?**
Porque los reviewers pueden equivocarse. Uno puede encontrar un "problema"
que no es real (false positive). Otro puede flaggear algo que el spec
dice que es intencional. El Approver verifica CADA finding contra el codigo
real antes de decidir.

```
  SIN APPROVER                           CON APPROVER
  ─────────────                          ─────────────
  Reviewer dice "SQL injection!"         Reviewer dice "SQL injection!"
  → Builder arregla                      → Approver lee el codigo real
  → Pero era un false positive           → "Esto usa parameterized query,
  → Se perdio tiempo y se                   el reviewer se equivoco"
    degradó el codigo                    → FALSE_POSITIVE, descarta
                                         → No se pierde tiempo

  Reviewer dice "esta bien"              Reviewer dice "esta bien"
  → Se crea PR                           → Approver lee el codigo real
  → Pipeline encuentra el bug            → "Hay un secret hardcodeado
  → Mas caro arreglarlo aca                 en linea 89"
                                         → CONFIRMED, devuelve al Builder
                                         → Se arregla ANTES de crear PR
```

**El proceso del Approver:**

```
  1. RECOLECTAR          2. DEDUPLICAR           3. VERIFICAR
  ────────────           ─────────────           ───────────
  Recibe findings        Si Security y Code      Por cada finding:
  de TODOS los           encontraron lo mismo    LEE EL CODIGO REAL.
  reviewers              en file:42,             No confies en el reviewer.
                         cuenta como 1 finding   Clasifica:
                                                 - CONFIRMED: real
                                                 - FALSE_POSITIVE: error del reviewer
                                                 - INTENTIONAL: spec lo pide
                                                 - DEFERRED: real pero no urgente

  4. DECIDIR                              5. ROUTEAR
  ──────────                              ────────
  ¿Hay CONFIRMED?                         ¿Que tan riesgoso es?
     │                                       │
  ┌──┴───┐                               ┌──┴────┐
  SI     NO                              LOW    HIGH
  │      │                                │      │
  ▼      ▼                                ▼      ▼
  FIX    APROBADO                        Auto   Humano
  LOOP   → crear PR                      PR     revisa
```

**El Fix Loop:**

Si hay findings CONFIRMED, el Approver NO crea PR. En vez de eso:
1. Compila una lista de fixes: "archivo X, linea Y, arregla Z"
2. Manda la lista al Builder
3. El Builder arregla (CON CONTEXTO — recuerda lo que hizo antes)
4. Los reviewers re-revisan
5. El Approver re-evalua
6. Maximo 3 vueltas. Si despues de 3 no se resuelve → humano interviene.

**¿Por que maximo 3?** Para evitar loops infinitos donde el Builder
intenta satisfacer findings contradictorios y degrada el codigo
en cada intento.

---

### Componente 6: El Risk Router — El Semaforo

**¿Que es?**
La logica que decide si un cambio puede aprobarse automaticamente
o necesita que un humano lo vea.

**¿Por que existe?**
No todos los cambios son iguales. Cambiar un color de CSS
no es lo mismo que cambiar la logica de autenticacion.
El risk router asegura que los cambios peligrosos siempre
tengan un par de ojos humanos.

```
  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  ¿Que archivos se tocaron?                          │
  │  ¿Es frontend o backend?                            │
  │  ¿Toca base de datos, auth, API critica?            │
  │  ¿El spec dice que es LOW o HIGH risk?              │
  │                                                     │
  │              ┌──────────┐                           │
  │              │ DECISION │                           │
  │              └────┬─────┘                           │
  │           ┌───────┴───────┐                         │
  │           ▼               ▼                         │
  │     LOW RISK          HIGH RISK                     │
  │     ────────          ─────────                     │
  │     CSS, docs,        Backend,                      │
  │     tests, UI         DB, auth,                     │
  │     assets            API, K8s                      │
  │         │                 │                         │
  │         ▼                 ▼                         │
  │     PR se crea        PR se crea                    │
  │     y se puede        pero el humano                │
  │     auto-merge        DEBE aprobar                  │
  │     sin humano        antes de merge                │
  │                                                     │
  └─────────────────────────────────────────────────────┘
```

**Analogia:** es como el control de aduanas. Un paquete pequeno (bajo riesgo)
pasa rapido. Un contenedor grande (alto riesgo) se inspecciona a fondo.

---

## Parte 3: El Outer Loop — Donde las Maquinas Ejecutan

El outer loop es todo lo que pasa DESPUES de que el inner loop crea un PR.
Aqui ya no hay agentes "pensando" — hay herramientas ejecutando de forma
deterministica: o pasa o no pasa, sin opinion.

### ¿Por que existe el outer loop?

```
  "Pero si los reviewers del inner loop ya revisaron todo,
   ¿para que otro loop?"

  Porque el inner loop es COGNITIVO — opina, razona, puede equivocarse.
  El outer loop es DETERMINISTA — mide, escanea, ejecuta. No opina.

  INNER LOOP dice:                     OUTER LOOP dice:
  "Este endpoint se ve seguro"         "Semgrep encontro CVE-2023-32681
                                        en requests==2.28.0, linea 14"

  "Los tests pasan localmente"         "pytest en container Docker:
                                        3 tests fallaron por env var
                                        que no existe en el container"

  "El manifest de K8s se ve bien"      "El deploy a canary fallo:
                                        ImagePullBackOff porque el
                                        tag de la imagen no existe"

  El inner loop PREVIENE.              El outer loop DETECTA.
  Ambos son necesarios.                Ninguno es suficiente solo.
```

**Es defensa en profundidad, no redundancia.** Como tener un guardia
en la puerta (inner loop) Y camaras de seguridad (outer loop).
El guardia puede distraerse. Las camaras no.

### Vista general del Outer Loop

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                          OUTER LOOP                                  │
  │                                                                      │
  │  PR ──→ CI ──→ Security ──→ Quality ──→ Approval ──→ CD ──→ Verify  │
  │                                                                      │
  │  Cada paso es un GATE: si falla, el codigo no avanza.               │
  │  No hay "bueno, dejalo pasar". Falla = se detiene.                  │
  └──────────────────────────────────────────────────────────────────────┘
```

### Paso 1: CI — Continuous Integration (Construir y Probar)

**¿Que es?**
Se toma el codigo del PR, se construye un container Docker con el,
y se corren todos los tests automatizados dentro de ese container.

**¿Por que existe?**
Porque "funciona en mi laptop" no es lo mismo que "funciona en produccion".
El container es identico al de produccion — si falla aqui, fallaria alla.

```
  ┌────────────────────────────────────────────────────────┐
  │  CI — CONTINUOUS INTEGRATION                            │
  │                                                        │
  │  1. BUILD                                              │
  │     - Docker build del Dockerfile                      │
  │     - Instalar dependencias (requirements.txt)         │
  │     - Si no compila/no instala → FALLA, se detiene     │
  │                                                        │
  │  2. TEST                                               │
  │     - pytest dentro del container                      │
  │     - TODOS los tests, no solo los nuevos              │
  │     - Coverage report                                  │
  │     - Si algun test falla → FALLA, se detiene          │
  │                                                        │
  │  3. LINT / FORMATO (opcional)                          │
  │     - flake8, black, isort                             │
  │     - Si hay errores de formato → FALLA                │
  │                                                        │
  │  Output: container listo + tests pasaron               │
  └────────────────────┬───────────────────────────────────┘
                       │ SI pasa
                       ▼
```

**Que atrapa que el inner loop no:**
- Dependencias que no se instalan en el container
- Tests que pasan local pero fallan con env vars diferentes
- Codigo que depende de algo que solo existe en tu laptop

---

### Paso 2: Security Testing — STO (Escaneo de Seguridad)

**¿Que es?**
Scanners automatizados que buscan vulnerabilidades en el codigo
y en las dependencias. No son agentes opinando — son herramientas
que comparan contra bases de datos de vulnerabilidades conocidas.

**¿Por que existe?**
El Security Reviewer del inner loop es un agente de IA que RAZONA
sobre seguridad. Puede encontrar patrones de ataque, pero tambien
puede pasar por alto un CVE conocido en una libreria de terceros.
Los scanners STO no razonan — buscan en bases de datos.

```
  ┌────────────────────────────────────────────────────────────┐
  │  STO — SECURITY TESTING ORCHESTRATION                      │
  │                                                            │
  │  1. SAST (Static Application Security Testing)             │
  │     Herramienta: Semgrep                                   │
  │     Busca: injection, XSS, auth bypass en el CODIGO        │
  │     Ejemplo: "user input en SQL query sin sanitizar"       │
  │                                                            │
  │  2. SCA (Software Composition Analysis)                    │
  │     Herramienta: OWASP Dependency Check                    │
  │     Busca: CVEs conocidos en DEPENDENCIAS                  │
  │     Ejemplo: "requests==2.28.0 tiene CVE-2023-32681"       │
  │                                                            │
  │  3. Secret Detection                                       │
  │     Busca: API keys, passwords, tokens en el codigo        │
  │     Ejemplo: "OPENAI_API_KEY hardcodeada en linea 23"      │
  │                                                            │
  │  4. Container Scanning (opcional)                          │
  │     Busca: vulnerabilidades en la imagen Docker base       │
  │                                                            │
  │  Policy: si hay CRITICAL o HIGH → BLOQUEA la PR            │
  │                                                            │
  │  Worker Agent: security_analyzer                           │
  │  - Recibe los findings CRITICAL/HIGH                       │
  │  - Intenta remediar automaticamente (upgrade lib, etc.)    │
  │  - Crea PR con el fix                                      │
  └────────────────────┬───────────────────────────────────────┘
                       │ SI pasa
                       ▼
```

**Diferencia inner loop vs outer loop en seguridad:**

| Aspecto | Inner Loop (Security Reviewer) | Outer Loop (STO/SAST/SCA) |
|---------|-------------------------------|--------------------------|
| Naturaleza | Cognitivo — razona | Deterministico — busca en DB |
| Puede fallar | Si — puede pasar por alto algo | Tambien — solo conoce CVEs reportados |
| Fortaleza | Patrones de ataque novedosos, logica de negocio | CVEs conocidos, versiones vulnerables exactas |
| Debilidad | Puede "convencerse" de que algo esta bien | No entiende la logica de negocio |
| Cuando corre | Pre-PR (antes de crear el PR) | Post-PR (dentro del pipeline) |

**Por que ambos:** el reviewer encuentra "este endpoint no valida input del usuario".
El scanner encuentra "la libreria requests que usas tiene un CVE publicado hace 3 dias".
Ninguno de los dos encontraria lo que el otro encuentra.

---

### Paso 3: AI Security (Seguridad de IA)

**¿Que es?**
Capa de seguridad especifica para aplicaciones que usan IA.
Protege contra ataques al modelo, no al codigo.

**¿Por que existe?**
Las apps con IA tienen ataques que las apps tradicionales no tienen:
prompt injection, data exfiltration via prompts, model abuse.

```
  ┌────────────────────────────────────────────────────────────┐
  │  AI SECURITY                                               │
  │                                                            │
  │  Discovery:                                                │
  │  - ¿Que endpoints de IA tiene la app?                      │
  │  - ¿Que modelos usa? ¿Que MCP servers conecta?             │
  │                                                            │
  │  Testing:                                                  │
  │  - Prompt injection: ¿puedo hacer que el modelo            │
  │    haga cosas que no deberia?                              │
  │  - Data leak: ¿el modelo revela datos sensibles            │
  │    que no deberia compartir?                               │
  │  - Guardrails: ¿los limites del modelo funcionan?          │
  │                                                            │
  │  Protection (runtime):                                     │
  │  - Monitorear requests al modelo en tiempo real            │
  │  - Bloquear prompts maliciosos antes de que lleguen        │
  │  - Alertar si el modelo responde con datos clasificados    │
  │                                                            │
  └────────────────────┬───────────────────────────────────────┘
                       │ SI pasa
                       ▼
```

---

### Paso 4: Supply Chain Security — SCS (Cadena de Suministro)

**¿Que es?**
Verificar que lo que se construyo es exactamente lo que se despliega.
Que nadie metio codigo malicioso entre el build y el deploy.

**¿Por que existe?**
Imagina que alguien reemplaza tu container por uno con un backdoor
entre que se construye y se despliega. SCS previene eso.

```
  ┌────────────────────────────────────────────────────────────┐
  │  SCS — SUPPLY CHAIN SECURITY                               │
  │                                                            │
  │  1. SBOM (Software Bill of Materials)                      │
  │     Lista EXACTA de todo lo que hay dentro del container:  │
  │     - librerias Python + versiones                         │
  │     - paquetes del SO + versiones                          │
  │     - herramientas del build                               │
  │                                                            │
  │  2. PROVENANCE (Procedencia)                               │
  │     Registro firmado de:                                   │
  │     - ¿Quien lo construyo? (que pipeline, que runner)      │
  │     - ¿De que commit viene? (SHA exacto de git)            │
  │     - ¿Cuando se construyo? (timestamp)                    │
  │                                                            │
  │  3. ATTESTATION (Certificacion)                            │
  │     Declaracion firmada de que:                            │
  │     - Los tests pasaron                                    │
  │     - Los scans de seguridad pasaron                       │
  │     - Las policies se cumplieron                           │
  │                                                            │
  │  4. VERIFICATION (en deploy)                               │
  │     Antes de desplegar, verifica:                          │
  │     - La firma del container es valida                     │
  │     - El digest (hash) coincide con el que se construyo    │
  │     - Las attestations estan presentes y son validas       │
  │                                                            │
  └────────────────────┬───────────────────────────────────────┘
                       │ SI pasa
                       ▼
```

**Analogia:** es como el sello de seguridad en un medicamento.
Si el sello esta roto, no lo tomas. SCS es el sello digital
que garantiza que nadie altero el container.

---

### Paso 5: Quality Gates — Policies (OPA)

**¿Que es?**
Reglas automaticas que deciden si un cambio puede avanzar.
No son opiniones — son reglas binarias: pasa o no pasa.

**¿Por que existen?**
Para que ninguna PR (venga de humano o agente) pueda saltarse los controles.
Las policies son iguales para todos. No hay excepciones sin aprobacion explicita.

```
  ┌────────────────────────────────────────────────────────────┐
  │  QUALITY GATES — OPA POLICIES                              │
  │                                                            │
  │  Ejemplos de policies:                                     │
  │                                                            │
  │  ✓ "Si coverage < 80% → BLOQUEAR"                         │
  │  ✓ "Si hay findings CRITICAL sin remediar → BLOQUEAR"     │
  │  ✓ "Si el PR toca archivos de K8s → requiere approval      │
  │     del equipo de infra"                                   │
  │  ✓ "Si el container no tiene SBOM → BLOQUEAR deploy"      │
  │  ✓ "Si no hay attestation de tests → BLOQUEAR"            │
  │                                                            │
  │  Estas reglas son CODIGO (Rego/OPA), no configuracion      │
  │  manual. Se versionan en git. Se testean. Se auditan.      │
  │                                                            │
  └────────────────────┬───────────────────────────────────────┘
                       │ SI pasa
                       ▼
```

**Diferencia con el Approver del inner loop:**

| Aspecto | Approver (Inner Loop) | OPA Policy (Outer Loop) |
|---------|----------------------|------------------------|
| Naturaleza | Cognitivo — razona sobre el cambio | Deterministico — regla binaria |
| Flexibilidad | Puede considerar contexto | Pasa o no pasa, sin matices |
| Ejemplo | "Este finding es un false positive porque..." | "Coverage < 80% = BLOCK. No importa por que" |
| Bypass | El humano puede aprobar con justificacion | Requiere excepcion formal en la policy |

---

### Paso 6: CD — Continuous Deployment (Despliegue)

**¿Que es?**
El proceso de llevar el container que paso todos los checks a produccion,
de forma gradual y segura.

**¿Por que existe?**
Porque incluso si todo pasa en tests, la realidad de produccion
puede ser diferente. El deploy gradual permite detectar problemas
antes de afectar a todos los usuarios.

```
  ┌────────────────────────────────────────────────────────────┐
  │  CD — CONTINUOUS DEPLOYMENT                                │
  │                                                            │
  │  1. APPROVAL (si HIGH RISK)                                │
  │     - Humano revisa el resumen de cambios                  │
  │     - Aprueba o rechaza el deploy                          │
  │     - Linked al commit y artefacto especificos             │
  │                                                            │
  │  2. CANARY DEPLOY                                          │
  │     - Despliega 1 replica nueva (canary) al lado           │
  │       de las replicas existentes (stable)                  │
  │     - El canary recibe ~10-20% del trafico real            │
  │     - Se monitorea: errores, latencia, CPU, memoria        │
  │                                                            │
  │  3. VERIFY (Continuous Verification)                       │
  │     - ¿El canary tiene mas errores que stable?             │
  │     - ¿La latencia aumento?                                │
  │     - ¿Hay panics, OOM, crash loops?                       │
  │     - Si algo esta mal → ROLLBACK automatico               │
  │                                                            │
  │  4. PROMOTE (Rolling Update)                               │
  │     - Si el canary esta sano, reemplazar todas las         │
  │       replicas una por una                                 │
  │     - Cada replica se verifica antes de continuar          │
  │     - Si algo falla mid-rollout → ROLLBACK                 │
  │                                                            │
  │  5. PRODUCCION                                             │
  │     - 100% del trafico en la nueva version                 │
  │     - Monitoreo continuo post-deploy                       │
  │     - Si hay incidente → AI SRE + runbooks                 │
  │                                                            │
  └────────────────────────────────────────────────────────────┘
```

**Analogia:** no abres un restaurante para 500 personas el primer dia.
Abres con 50 invitados (canary), ves que todo funciona, y entonces
abres para todos (rolling).

---

### Paso 7: Worker Agents del Outer Loop

**¿Que son?**
Agentes de IA que viven DENTRO del pipeline y se activan cuando
algo falla. Su trabajo es arreglar problemas mecanicos sin
intervencion humana.

**¿Por que existen?**
Porque muchos fallos del pipeline son arreglables automaticamente:
una dependencia vulnerable se actualiza, un manifest de K8s
le falta un env var, un test nuevo necesita un mock.

```
  ┌────────────────────────────────────────────────────────────┐
  │  WORKER AGENTS — Outer Loop                                │
  │                                                            │
  │  Diferencia con Experts del Inner Loop:                    │
  │  - Son EFIMEROS (nacen, arreglan, mueren)                  │
  │  - Viven en el PIPELINE (no en un IDE o VM)                │
  │  - Su contexto es la PR + los findings del scanner         │
  │  - No consultan el Brain (son mecanicos, no cognitivos)    │
  │                                                            │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ code_reviewer                                       │   │
  │  │ - Revisa la PR dentro del pipeline                  │   │
  │  │ - Comenta en la PR con findings                     │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                            │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ security_analyzer                                   │   │
  │  │ - Recibe findings CRITICAL/HIGH del scanner         │   │
  │  │ - Intenta fix automatico (upgrade lib, sanitize)    │   │
  │  │ - Crea commit con la remediacion                    │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                            │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ ca_code_unit_test_generator                         │   │
  │  │ - Si code_reviewer dice "falta test coverage"       │   │
  │  │ - Genera tests para las lineas no cubiertas         │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                            │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ qa_ui_analyzer                                      │   │
  │  │ - Valida CSS, alignment, responsive                 │   │
  │  │ - Usa screenshots para verificar visualmente        │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                            │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ ca_manifest_remediation_v2                          │   │
  │  │ - Si el deploy falla por config de K8s              │   │
  │  │ - Arregla: env vars, configmaps, image tags         │   │
  │  │ - Crea PR con el manifest arreglado                 │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                            │
  └────────────────────────────────────────────────────────────┘
```

**Diferencia entre Experts (inner) y Workers (outer):**

| Aspecto | Experts (Inner Loop) | Workers (Outer Loop) |
|---------|---------------------|---------------------|
| Donde viven | Cosmos / Claude Code | Pipeline de Harness |
| Duracion | Sesion larga, pueden mantener contexto | Efimeros: nacen, arreglan, mueren |
| Brain | Lo consultan siempre | No lo consultan |
| Contexto | Spec + Brain + codigo completo | PR + findings del scanner |
| Tipo de trabajo | Cognitivo: razonar, diseñar, decidir | Mecanico: parchear, upgradar, generar |
| Ejemplo | "¿Esta spec cubre todos los edge cases?" | "Actualiza requests de 2.28.0 a 2.31.0" |

---

### Paso 8: Feedback Loop — Cuando el Outer Loop Falla

**¿Que pasa cuando algo falla en el pipeline?**

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  FEEDBACK: OUTER LOOP → INNER LOOP                               │
  │                                                                  │
  │  TIPO 1: Fallo simple (Worker lo resuelve)                       │
  │  ─────────────────────────────────────────                       │
  │  Pipeline: "SAST encontro CVE en requests"                       │
  │  → Worker security_analyzer: "upgrade a 2.31.0"                  │
  │  → Crea commit, pipeline re-corre                                │
  │  → Resuelto. Inner loop no se entera.                            │
  │                                                                  │
  │  TIPO 2: Fallo complejo (regresa al Inner Loop)                  │
  │  ──────────────────────────────────────────                      │
  │  Pipeline: "Deploy falla: la app crashea al iniciar"             │
  │  → Worker no puede resolverlo (no es un patch simple)            │
  │  → Notificacion al Inner Loop: "el codigo tiene un bug"          │
  │  → Builder recibe feedback con el error                          │
  │  → Builder arregla, nueva PR, pipeline re-corre                  │
  │                                                                  │
  │  TIPO 3: Incidente en produccion                                 │
  │  ─────────────────────────────                                   │
  │  Produccion: "alerta: latencia > 5s en /api/accounts"            │
  │  → AI SRE: ejecuta runbook automatico                            │
  │  → Acciones: rollback, scale, restart, notificar                 │
  │  → Si es recurrente → Inner Loop crea spec para fix permanente   │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
```

---

## Parte 4: Planos Transversales — Los Controles que Cruzan Todo

Estos controles no viven en el inner loop ni en el outer loop.
Cruzan AMBOS. Son como la electricidad y la plomeria de un edificio —
no son un piso, cruzan todos los pisos.

### ¿Por que existen?

Sin controles transversales, tienes agentes de IA con acceso ilimitado.
En un banco, eso es inaceptable. Incluso fuera de banca,
es una receta para desastres.

```
  SIN CONTROLES                          CON CONTROLES
  ──────────────                         ──────────────
  Agente tiene acceso a todo             Agente tiene acceso SOLO a lo que necesita
  Agente usa cualquier modelo            Agente usa modelos aprobados via gateway
  Secretos en prompts y logs             Secretos inyectados al proceso, nunca al modelo
  No se sabe quien hizo que              Cada accion tiene identidad y audit trail
  Si algo sale mal, no hay freno         Kill switch: se para todo en segundos
```

### Vista general

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                        │
  │                     PLANOS TRANSVERSALES                               │
  │                     ───────────────────                                │
  │                                                                        │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │  1. IDENTIDAD — ¿Quien eres?                                     │  │
  │  │     Cada agente tiene identidad unica, owner humano, expiracion  │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │                                                                        │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │  2. AUTORIZACION — ¿Que puedes hacer?                            │  │
  │  │     Permisos minimos. El Builder no puede deployar.              │  │
  │  │     El Reviewer no puede escribir codigo.                        │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │                                                                        │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │  3. SECRETOS — ¿Donde estan las llaves?                          │  │
  │  │     Nunca en prompts, logs, git, o Jira.                         │  │
  │  │     Inyectados al proceso, no al modelo.                         │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │                                                                        │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │  4. DATOS — ¿Que informacion puedes ver?                         │  │
  │  │     Clasificacion, minimizacion, redaccion.                      │  │
  │  │     El agente ve lo minimo necesario.                            │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │                                                                        │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │  5. OBSERVABILIDAD — ¿Que esta pasando?                          │  │
  │  │     Tracing de cada accion. Costo. Tokens. Tool calls.          │  │
  │  │     Si algo sale mal, se puede reconstruir que paso.             │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │                                                                        │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │  6. LIMITES — ¿Cuando paras?                                     │  │
  │  │     Timeout, presupuesto de tokens, max iterations.              │  │
  │  │     Kill switch: detener todo en segundos.                       │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
```

### Control 1: Identidad — ¿Quien eres?

**El problema:** si todos los agentes usan la misma cuenta, no sabes
quien hizo que. Si un agente hace algo mal, no sabes cual fue.

**La solucion:** cada agente tiene su propia identidad tecnica, como
cada empleado tiene su propio badge de acceso.

```
  ┌──────────────────────────────────────────────────────────┐
  │  IDENTIDAD                                               │
  │                                                          │
  │  Cada agente tiene:                                      │
  │  - Identidad unica (no comparte credenciales)            │
  │  - Owner humano (alguien es responsable de el)           │
  │  - Fecha de expiracion (no vive para siempre)            │
  │  - Alcance definido (builder, reviewer, deployer)        │
  │                                                          │
  │  Stack:                                                  │
  │  ┌───────────────┐  Lifecycle de identidades             │
  │  │   midPoint     │  (alta, baja, recertificacion)       │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Autenticacion                        │
  │  │   Keycloak     │  (federar con directorio corp)       │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Identidad de workload                │
  │  │  SPIFFE/SPIRE  │  (atestacion de que el agente        │
  │  └───────────────┘   es quien dice ser)                  │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

### Control 2: Autorizacion — ¿Que puedes hacer?

**El problema:** sin autorizacion, el Builder podria decidir
hacer deploy directo a produccion, o el Reviewer podria
modificar codigo.

**La solucion:** permisos minimos por rol. Cada agente solo puede
hacer lo que su rol permite.

```
  ┌──────────────────────────────────────────────────────────┐
  │  AUTORIZACION                                            │
  │                                                          │
  │  Spec Writer: puede LEER codigo y Brain                  │
  │               NO puede escribir codigo                   │
  │               NO puede crear PRs                         │
  │                                                          │
  │  Builder:     puede LEER y ESCRIBIR codigo               │
  │               puede crear branches                       │
  │               NO puede crear PRs                         │
  │               NO puede hacer deploy                      │
  │                                                          │
  │  Reviewer:    puede LEER codigo y diff                   │
  │               NO puede escribir codigo                   │
  │               NO puede crear PRs                         │
  │                                                          │
  │  Approver:    puede LEER todo + CREAR PRs                │
  │               NO puede hacer deploy                      │
  │               NO puede merge (eso lo hace el pipeline)   │
  │                                                          │
  │  Stack:                                                  │
  │  ┌───────────────┐  Relaciones de acceso                 │
  │  │   OpenFGA      │  ("agente X puede leer repo Y")      │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Policies contextuales                │
  │  │    OPA         │  ("solo si el cambio es LOW RISK")    │
  │  └───────────────┘                                       │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

### Control 3: Secretos — ¿Donde estan las llaves?

**El problema:** un agente de IA recibe un prompt. Si el prompt contiene
un API key o password, el modelo lo "ve" y podria filtrarlo en sus
respuestas, logs, o commits.

**La solucion:** los secretos NUNCA llegan al modelo. Se inyectan
al proceso (el runtime que ejecuta el agente), no al prompt.

```
  ┌──────────────────────────────────────────────────────────┐
  │  SECRETOS                                                │
  │                                                          │
  │  MALO:                                                   │
  │  prompt: "usa esta API key: sk-abc123 para..."           │
  │  → el modelo VE el secreto                               │
  │  → puede filtrarlo en output, logs, commits              │
  │                                                          │
  │  BUENO:                                                  │
  │  prompt: "usa la API key de variable OPENAI_API_KEY"     │
  │  runtime: OPENAI_API_KEY=sk-abc123 (inyectada al proceso)│
  │  → el modelo NUNCA ve el valor real                      │
  │  → solo sabe que existe una variable                     │
  │                                                          │
  │  Stack:                                                  │
  │  ┌───────────────┐  Gestion de secretos                  │
  │  │  1Password     │  Vaults separados por dominio         │
  │  └───────────────┘  Rotacion automatica                  │
  │                     Inyeccion al proceso, no al modelo   │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

### Control 4: Datos — ¿Que informacion puedes ver?

**El problema:** un agente que trabaja en la UI del dashboard
no necesita ver datos de cuentas bancarias. Si los ve, puede
filtrarlos (accidental o por prompt injection).

**La solucion:** minimizacion de datos. El agente ve lo minimo
necesario para su tarea. Los datos sensibles se redactan antes
de llegar al modelo.

```
  ┌──────────────────────────────────────────────────────────┐
  │  GOBIERNO DE DATOS                                       │
  │                                                          │
  │  1. Clasificacion: ¿que datos son sensibles?             │
  │     - PUBLICO: nombre del producto                       │
  │     - INTERNO: metricas de rendimiento                   │
  │     - CONFIDENCIAL: saldos de cuentas                    │
  │     - RESTRINGIDO: datos PII de clientes                 │
  │                                                          │
  │  2. Minimizacion: el agente ve lo MINIMO                 │
  │     - Si trabaja en UI → ve templates, no datos reales   │
  │     - Si trabaja en API → ve esquema, no registros       │
  │                                                          │
  │  3. Redaccion: antes de enviar al modelo                 │
  │     - "Juan Perez, cuenta 1234" → "[NOMBRE], [CUENTA]"  │
  │     - Presidio para detectar y redactar PII              │
  │                                                          │
  │  Stack:                                                  │
  │  ┌───────────────┐  Catalogo y clasificacion             │
  │  │ OpenMetadata   │                                      │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Enforcement                          │
  │  │ Apache Ranger  │  (o controles nativos de la DB)      │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Deteccion y redaccion de PII         │
  │  │  Presidio      │                                      │
  │  └───────────────┘                                       │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

### Control 5: Observabilidad — ¿Que esta pasando?

**El problema:** si un agente toma una mala decision y no hay registro,
no puedes entender que paso ni prevenirlo en el futuro.

**La solucion:** registrar TODA accion del agente: que modelo uso,
cuantos tokens consumio, que herramientas llamo, que archivos toco.

```
  ┌──────────────────────────────────────────────────────────┐
  │  OBSERVABILIDAD                                          │
  │                                                          │
  │  Por cada accion del agente:                             │
  │  - ¿Que modelo se uso? (Opus, Sonnet, Haiku)             │
  │  - ¿Cuantos tokens consumio? (input + output)           │
  │  - ¿Que herramientas llamo? (git, read, write, MCP)     │
  │  - ¿Que archivos toco? (read/write/create/delete)       │
  │  - ¿Cuanto tardo? (latencia por step)                   │
  │  - ¿Cual fue el resultado? (exitoso/fallido)            │
  │                                                          │
  │  Para auditar:                                           │
  │  - ¿Quien pidio la tarea? (Jira ID, humano responsable) │
  │  - ¿Que identidad uso el agente? (SPIFFE ID)            │
  │  - ¿Que secretos accedio? (referencia, no valor)         │
  │  - ¿Que datos vio? (clasificacion, no contenido)        │
  │                                                          │
  │  Stack:                                                  │
  │  ┌───────────────┐  Trazas AI (prompts, completions)     │
  │  │ Langfuse /     │  (SANITIZADAS: sin secretos/PII)     │
  │  │ Phoenix        │                                      │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Metricas y alertas infra             │
  │  │ Prometheus /   │                                      │
  │  │ Grafana        │                                      │
  │  └───────────────┘                                       │
  │  ┌───────────────┐  Eventos de seguridad                 │
  │  │  SIEM          │                                      │
  │  └───────────────┘                                       │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

### Control 6: Limites — ¿Cuando paras?

**El problema:** un agente sin limites puede correr para siempre,
consumir tokens ilimitados, o entrar en un loop infinito.

**La solucion:** cada mision tiene timeout, presupuesto, y kill switch.

```
  ┌──────────────────────────────────────────────────────────┐
  │  LIMITES Y KILL SWITCH                                   │
  │                                                          │
  │  Por mision:                                             │
  │  - Timeout: max 2 horas (configurable por tarea)         │
  │  - Presupuesto de tokens: max 500K tokens                │
  │  - Max tool calls: max 200 llamadas a herramientas       │
  │  - Max fix loop iterations: 3                            │
  │  - Max agent turns: spec.budget.max_agent_turns          │
  │                                                          │
  │  Kill switch:                                            │
  │  - Detener UN agente: revoca su identidad/token          │
  │  - Detener TODA la factory: kill switch global           │
  │  - Rollback: revertir el ultimo deploy en segundos       │
  │                                                          │
  │  Escalamiento:                                           │
  │  - Si el agente excede su presupuesto → PARA y notifica  │
  │  - Si el fix loop llega a iteracion 3 → humano decide    │
  │  - Si el canary muestra degradacion → rollback auto      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

---

## Parte 5: El Contrato de Mision — TaskContract

**¿Que es?**
Un documento que acompaña CADA tarea que entra a la factory.
Define los limites exactos de lo que el agente puede hacer.

**¿Por que existe?**
Sin contrato, el agente decide su propio alcance.
Con contrato, el sistema valida ANTES de cada accion
si el agente tiene permiso.

**Analogia:** cuando contratas a alguien para remodelar tu baño,
firmas un contrato que dice: "puede trabajar en el baño,
con estas herramientas, en este plazo, con este presupuesto.
NO puede tocar la cocina." El TaskContract es lo mismo para agentes.

```
  ┌──────────────────────────────────────────────────────────┐
  │  TASKCONTRACT                                            │
  │                                                          │
  │  jira_key: "HD-301"                                      │
  │  owner: "cristian.ramirez"                               │
  │  purpose: "Agregar endpoint /api/version"                │
  │                                                          │
  │  scope:                                                  │
  │    repos: ["ai-agentic-demo"]                            │
  │    paths_allowed: ["app/", "tests/", "VERSION.txt"]      │
  │    paths_forbidden: ["k8s/", ".harness/", "scripts/"]    │
  │                                                          │
  │  tools_allowed: ["git", "pytest", "curl"]                │
  │  tools_forbidden: ["kubectl", "docker push"]             │
  │                                                          │
  │  environments:                                           │
  │    allowed: ["dev", "sandbox"]                           │
  │    forbidden: ["prod", "staging"]                        │
  │                                                          │
  │  data_classification_max: "INTERNAL"                     │
  │                                                          │
  │  budget:                                                 │
  │    max_time: "2h"                                        │
  │    max_tokens: 500000                                    │
  │    max_tool_calls: 200                                   │
  │                                                          │
  │  review: "required — independent reviewer"               │
  │  approval: "required for HIGH RISK changes"              │
  │                                                          │
  │  expiration: "2026-11-09T18:00:00Z"                      │
  │  rollback: "git revert + pipeline re-deploy"             │
  │  kill_switch: "revoke SPIFFE identity"                   │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

---

## Parte 6: Gateways — Model Gateway y Tool Gateway

### Model Gateway — LiteLLM

**¿Que es?**
Un proxy entre los agentes y los modelos de IA. Todos los agentes
pasan por el gateway para hablar con Opus, Sonnet, Haiku, etc.

**¿Por que existe?**
Sin gateway, cada agente llama directamente al modelo con su propia
API key. No hay control de presupuesto, no hay routing, no hay audit.

```
  SIN GATEWAY                            CON GATEWAY
  ───────────                            ───────────
  Builder → Opus (directo)               Builder → LiteLLM → Opus
  Reviewer → Sonnet (directo)            Reviewer → LiteLLM → Sonnet
  Approver → Opus (directo)              Approver → LiteLLM → Opus
                                                      │
  - No hay control de costo              - Budgets por agente y tarea
  - No hay routing inteligente           - Fallback: si Opus falla → Sonnet
  - No hay audit de tokens               - Audit: quien gasto cuanto
  - No hay lista de modelos              - Solo modelos aprobados
    aprobados                            - Rate limiting por agente
```

### Tool Gateway — AgentGateway

**¿Que es?**
Un proxy entre los agentes y las herramientas (git, kubectl, APIs, MCP).
Valida que el agente tiene permiso antes de ejecutar cada herramienta.

**¿Por que existe?**
Sin tool gateway, un agente podria llamar a `kubectl delete pod` en produccion
o hacer `git push --force` a main. El gateway valida cada llamada contra
el TaskContract y la autorizacion.

```
  SIN GATEWAY                            CON GATEWAY
  ───────────                            ───────────
  Builder llama kubectl                  Builder llama kubectl
  directamente → ¿tiene permiso?         → Tool Gateway valida:
  No se sabe.                               ¿Esta en tools_allowed?
                                            ¿El namespace es dev?
                                            ¿El TaskContract lo permite?
                                            → SI: ejecuta
                                            → NO: bloquea + log + alerta
```

---

## Parte 7: Diagrama Completo — Todo Junto

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║                        AI SOFTWARE FACTORY — VISTA COMPLETA                        ║
║                                                                                    ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  FUENTES                                                                           ║
║  ───────                                                                           ║
║  Jira Issue │ GitHub Issue │ Slack │ Sentry │ PagerDuty                             ║
║       │            │          │        │         │                                  ║
║       └────────────┴──────────┴────────┴─────────┘                                  ║
║                              │                                                      ║
║                              ▼                                                      ║
║                    ┌─────────────────────┐                                          ║
║                    │   INTAKE SERVICE    │                                          ║
║                    │                     │                                          ║
║                    │ Valida:             │                                          ║
║                    │ - TaskContract      │                                          ║
║                    │ - Owner humano      │                                          ║
║                    │ - Riesgo            │                                          ║
║                    │ - Autorizacion      │                                          ║
║                    └──────────┬──────────┘                                          ║
║                               │                                                     ║
║  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┼─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  ║
║  │ PLANOS TRANSVERSALES       │                                                 │  ║
║  │                            │                                                 │  ║
║  │ Identidad (midPoint/Keycloak/SPIRE) │ Autorizacion (OpenFGA/OPA)             │  ║
║  │ Secretos (1Password)                │ Datos (OpenMetadata/Presidio)           │  ║
║  │ Observabilidad (Langfuse/SIEM)      │ Limites (timeout/budget/kill switch)    │  ║
║  │ Model Gateway (LiteLLM)             │ Tool Gateway (AgentGateway)             │  ║
║  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┼─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  ║
║                               │                                                     ║
║                               │ (estos controles cruzan AMBOS loops)                ║
║                               │                                                     ║
║  ╔════════════════════════════╪═══════════════════════════════════════════════════╗  ║
║  ║  INNER LOOP (Cognitivo)    │                                                  ║  ║
║  ║                            ▼                                                  ║  ║
║  ║  Brain ──→ Spec Writer ──→ Gate ──→ Builder ──→ Reviewers ──→ Approver        ║  ║
║  ║            (Opus,          Humano   (Opus,      (Sonnet,      (Opus,          ║  ║
║  ║             read-only)     aprueba   TDD,        Haiku,        verifica,      ║  ║
║  ║                            spec      branch)     contexto      risk route)    ║  ║
║  ║                                       ▲          limpio)   │                  ║  ║
║  ║                                       └── fix loop ────────┘                  ║  ║
║  ║                                                                               ║  ║
║  ║  Output: PR lista                                                             ║  ║
║  ╚═══════════════════════════════════════════════════╪════════════════════════════╝  ║
║                                                      │ PR                           ║
║  ╔═══════════════════════════════════════════════════╪════════════════════════════╗  ║
║  ║  OUTER LOOP (Determinista)                        │                           ║  ║
║  ║                                                   ▼                           ║  ║
║  ║  CI ──→ STO ──→ AI Security ──→ SCS ──→ Policies ──→ CD                      ║  ║
║  ║  Build   SAST    Prompt          SBOM    OPA          Canary                  ║  ║
║  ║  Test    SCA     Injection       Prov.   Quality      Rolling                 ║  ║
║  ║          Secrets Data Leak       Attest. Gates        Verify                  ║  ║
║  ║                                                                               ║  ║
║  ║  Worker Agents: security_analyzer, code_reviewer, manifest_remediation        ║  ║
║  ║  (efimeros, mecanicos, dentro del pipeline)                                   ║  ║
║  ║                                                                               ║  ║
║  ║  Output: en produccion (o feedback al inner loop)                             ║  ║
║  ╚═══════════════════════════════════════════════════╪════════════════════════════╝  ║
║                                                      │                              ║
║                                                      ▼                              ║
║                                               PRODUCCION                            ║
║                                             + Monitoreo                              ║
║                                             + AI SRE                                 ║
║                                             + Runbooks auto                          ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

---

## Parte 8: Niveles de Autonomia

No todos los agentes ni tareas tienen el mismo nivel de libertad.
La factory define 5 niveles:

```
  ┌────────────────────────────────────────────────────────────┐
  │  NIVELES DE AUTONOMIA                                      │
  │                                                            │
  │  A0: INVESTIGACION                                         │
  │      Solo lee. Documentos, codigo, logs.                   │
  │      Sin efectos externos.                                 │
  │      Ejemplo: "¿como funciona el modulo de auth?"          │
  │                                                            │
  │  A1: CODIGO EN SANDBOX                                     │
  │      Lee + escribe codigo. PR obligatoria.                 │
  │      Review independiente antes de merge.                  │
  │      Ejemplo: "agrega endpoint /api/version"               │
  │                                                            │
  │  A2: CAMBIOS NONPROD                                       │
  │      Puede tocar ambientes dev/staging.                    │
  │      Cambios acotados y reversibles.                       │
  │      Ejemplo: "actualiza config de staging"                │
  │                                                            │
  │  A3: INFRA Y DATOS SENSIBLES                               │
  │      K8s, DB, datos de clientes.                           │
  │      Autorizacion humana PREVIA a cada accion.             │
  │      Ejemplo: "migra schema de la tabla accounts"          │
  │                                                            │
  │  A4: PRODUCCION CRITICA                                    │
  │      Pagos, IAM, criptografia.                             │
  │      SIN ejecucion autonoma. Humano siempre presente.      │
  │      Ejemplo: "cambia logica de transferencias"            │
  │                                                            │
  │  ⚠ Los niveles se asignan POR TAREA, no por agente.       │
  │    Un Builder puede ser A1 para CSS y A3 para DB.          │
  │    El TaskContract define el nivel para cada mision.       │
  │                                                            │
  └────────────────────────────────────────────────────────────┘
```

---

## Parte 9: Flujo End-to-End con Ejemplo

Veamos como se mueve una tarea real a traves de TODA la factory:

**Tarea:** "Agrega endpoint GET /api/version"

```
  PASO 1: INTAKE
  ──────────────
  - Humano crea issue en Jira: HD-301
  - Intake valida: owner, scope, riesgo
  - TaskContract generado:
    repos: [ai-agentic-demo]
    paths: [app/, tests/, VERSION.txt]
    budget: 30 turns, 200K tokens
    risk: LOW

  PASO 2: SPEC (Inner Loop)
  ─────────────────────────
  - Spec Writer lee Brain
  - Genera ASDD YAML:
    what_user_can_do: "GET /api/version → JSON"
    how_to_demonstrate: "curl localhost:5000/api/version"
  - Humano aprueba spec ✓

  PASO 3: BUILD (Inner Loop)
  ──────────────────────────
  - Builder lee spec + Brain
  - Crea branch factory/SPEC-301
  - TDD: test → rojo → codigo → verde
  - Self-check: curl + pytest ✓
  - Push a branch

  PASO 4: REVIEW (Inner Loop)
  ───────────────────────────
  - Security Rev (Sonnet): PASS, 0 findings
  - Code Rev (Haiku): PASS, 0 findings

  PASO 5: APPROVE (Inner Loop)
  ────────────────────────────
  - Approver: 0 CONFIRMED findings
  - Risk: LOW → auto-create PR
  - PR #42 creada → secops/ai-agentic-demo-main

  PASO 6: CI (Outer Loop)
  ───────────────────────
  - Docker build ✓
  - pytest (38 tests) ✓
  - Coverage: 82% ✓

  PASO 7: SECURITY (Outer Loop)
  ─────────────────────────────
  - SAST (Semgrep): 0 CRITICAL/HIGH ✓
  - SCA (OWASP): 0 CVEs nuevos ✓
  - Secret scan: 0 secrets ✓

  PASO 8: SUPPLY CHAIN (Outer Loop)
  ──────────────────────────────────
  - SBOM generado ✓
  - Provenance firmada ✓
  - Attestation de tests + scans ✓

  PASO 9: POLICIES (Outer Loop)
  ─────────────────────────────
  - OPA: coverage > 80% ✓
  - OPA: 0 CRITICAL findings ✓
  - OPA: SBOM presente ✓

  PASO 10: DEPLOY (Outer Loop)
  ────────────────────────────
  - LOW RISK → no requiere approval humano
  - Canary deploy: 1 replica
  - Verify: latencia OK, 0 errores
  - Promote: rolling update
  - 100% trafico en nueva version ✓

  RESULTADO:
  GET /api/version → {"version": "1.0.0"} ✓
  Tiempo total: ~20 min
  Intervencion humana: solo aprobar spec
```

---

## Parte 10: Resumen Visual

```
  ┌──────────────────────────────────────────────────────────────┐
  │                     SOFTWARE FACTORY                         │
  │                                                              │
  │                          ¿POR QUE?                           │
  │                                                              │
  │  Brain:        Para no repetir errores                       │
  │  Spec Writer:  Para no dejar que el Builder adivine          │
  │  ASDD:         Para no crear Frankensteins                   │
  │  Builder TDD:  Para que el codigo cumpla la spec             │
  │  Reviewers:    Para atrapar lo que el Builder no vio         │
  │  Diversidad:   Para evitar que el modelo se auto-apruebe     │
  │  Ctx limpio:   Para que el reviewer no se contamine          │
  │  Approver:     Para filtrar false positives                  │
  │  Fix loop:     Para corregir sin intervencion humana         │
  │  Risk router:  Para que humanos solo vean lo critico         │
  │  CI:           Para probar en container real                 │
  │  SAST/SCA:     Para encontrar CVEs que el agente no vio      │
  │  AI Security:  Para proteger contra ataques al modelo        │
  │  SCS:          Para garantizar que nadie altero el artefacto │
  │  OPA:          Para que las reglas se apliquen siempre       │
  │  Canary:       Para no afectar a todos si hay un bug         │
  │  Workers:      Para arreglar fallos simples automaticamente  │
  │  Identidad:    Para saber quien hizo que                     │
  │  Autorizacion: Para que nadie haga lo que no debe            │
  │  Secretos:     Para que el modelo nunca vea las llaves       │
  │  Datos:        Para que el agente vea lo minimo necesario    │
  │  Observabilidad: Para poder reconstruir que paso             │
  │  Kill switch:  Para parar todo si algo sale mal              │
  │  TaskContract: Para que cada mision tenga limites claros     │
  │  Gateways:     Para controlar que modelos y tools se usan    │
  │                                                              │
  │  Cada pieza existe porque SIN ELLA algo sale mal.            │
  │  Ninguna es opcional. Ninguna es redundante.                 │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```
