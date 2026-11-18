# Validacion Manual del Factory Loop

Guia para validar los 5 Experts uno por uno, en orden.
Usar la tarea de test: **agregar endpoint GET /api/version**.

---

## Tarea de test

```
Agrega un endpoint GET /api/version que retorne la version de la app
desde un archivo VERSION.txt en la raiz del proyecto.
Sin auth, responde JSON {"version": "1.0.0"}
```

Esta tarea es LOW RISK (sin auth, sin DB, sin backend logic critico),
lo que permite validar todo el loop sin intervenir en el Approver.

---

## Expert 1: Spec Writer

**Que hace**: recibe una tarea en lenguaje natural y produce un spec ASDD en YAML.
No escribe codigo. No crea branches. Solo el blueprint.

**Como lanzar**: abrir [Spec Writer](https://app.augmentcode.com/home?expertId=e60696ba-fdfe-4497-9acd-f017ff5fa9ae) y enviar:

```
Agrega un endpoint GET /api/version que retorne la version de la app
desde un archivo VERSION.txt en la raiz del proyecto.
Sin auth, responde JSON {"version": "1.0.0"}
```

**Que esperar**:

1. Lee el Brain primero:
   - `docs/cosmos-brain-bundle.md`
   - `.claude/brain/decisions.md`, `constraints.md`, `patterns.md`
   - `docs/specs/` (specs existentes)

2. Genera un YAML con las 5 secciones obligatorias:

```yaml
apiVersion: factory.demobank/v1
kind: Spec
metadata:
  id: SPEC-NNN
  title: "GET /api/version endpoint"

spec:
  what_user_can_do:
    - "GET /api/version retorna JSON con la version"

  expected_result:
    files_created:
      - "VERSION.txt"
    files_modified:
      - "app/app.py (registrar ruta o blueprint)"
    api_response:
      endpoint: "GET /api/version"
      status: 200
      body_keys: ["version"]

  must_respect:
    - "No modificar CSS existente (constraint #1)"
    - "No crear archivos fuera de rutas registradas (constraint #2)"

  how_to_demonstrate:
    automated:
      - cmd: "curl -s http://localhost:5000/api/version"
        expect: '{"version": "1.0.0"}'
      - cmd: "pytest tests/ -q"
        expect: "all tests pass"

  evidence:
    - "curl output del endpoint"
    - "pytest results"

  budget:
    max_agent_turns: 15
```

3. Guarda el spec en `docs/specs/SPEC-NNN.yaml` en el repo

**Criterios de PASS**:

- [ ] Leyo el Brain antes de escribir
- [ ] YAML valido con las 5 secciones (what_user_can_do, expected_result, must_respect, how_to_demonstrate, evidence)
- [ ] `must_respect` referencia constraints especificos del Brain (no generico)
- [ ] `how_to_demonstrate` tiene comandos exactos (no descripciones vagas)
- [ ] Archivo guardado en `docs/specs/`
- [ ] NO intento escribir codigo

**Criterios de FAIL**:

- Genero solo texto libre en vez de YAML
- Faltan secciones obligatorias
- `must_respect` dice "follow best practices" en vez de citar el Brain
- `how_to_demonstrate` dice "test the endpoint" en vez de dar el curl exacto
- Intento crear el endpoint (eso es trabajo del Builder)

**Accion post-validacion**: revisar el spec, ajustar si necesario, y aprobar.

---

## Expert 2: Builder

**Que hace**: recibe un spec aprobado e implementa con TDD.
Crea branch, Jira ticket, tests primero, codigo despues, self-check.
NO crea PR (eso lo hace el Approver).

**Como lanzar**: abrir [Builder](https://app.augmentcode.com/home?expertId=1c01b3ab-9cfc-4a70-a8ac-e62ff0a17422) y enviar:

```
build SPEC-NNN
```

(reemplazar SPEC-NNN con el ID real que genero el Spec Writer)

**Que esperar**:

1. Lee el spec y el Brain
2. Crea branch `factory/SPEC-NNN`
3. Crea Jira ticket en proyecto HD, tipo Task
4. TDD cycle:
   - Escribe test para `GET /api/version` → test FALLA (rojo)
   - Crea `VERSION.txt` con `1.0.0`
   - Agrega ruta o blueprint en `app/app.py`
   - Test PASA (verde)
5. Self-check:
   - `pytest tests/ -q` → todos pasan
   - `curl GET /api/version` → `{"version": "1.0.0"}`
6. Commit + push a branch `factory/SPEC-NNN`
7. Reporta "ready for review" con:
   - Branch name
   - Jira ticket ID
   - Tests passed count
   - Evidence location

**Criterios de PASS**:

- [ ] Leyo spec + Brain antes de codear
- [ ] Branch creada como `factory/SPEC-NNN`
- [ ] Jira ticket creado en HD
- [ ] Test escrito ANTES del codigo (TDD)
- [ ] `VERSION.txt` creado en raiz
- [ ] Endpoint responde `{"version": "1.0.0"}`
- [ ] Todos los tests pasan (no solo los nuevos)
- [ ] Self-check ejecutado (how_to_demonstrate)
- [ ] NO creo PR
- [ ] NO agrego funcionalidad fuera del spec

**Criterios de FAIL**:

- Escribio codigo sin test primero
- Agrego features no pedidas (auth, logging, etc.)
- Branch con nombre distinto a `factory/SPEC-NNN`
- Tests anteriores rotos
- No ejecuto self-check
- Creo PR (responsabilidad del Approver)
- Modifico archivos fuera del scope del spec

**Accion post-validacion**: anotar branch name y Jira ID para los reviewers.

---

## Expert 3: Security Reviewer

**Que hace**: revisa SOLO seguridad del diff del Builder. Contexto limpio.
Modelo diferente (Sonnet 5.5 vs Opus 5.5 del Builder). Solo lectura.

**Como lanzar**: abrir [Security Reviewer](https://app.augmentcode.com/home?expertId=f7de9a8f-0643-4888-80e4-f24b8956bcda) y enviar:

```
Review security of SPEC-NNN on branch factory/SPEC-NNN
```

**Que esperar**:

1. Lee el spec (busca `vulnerabilities_intended`)
2. Lee el diff en branch `factory/SPEC-NNN`
3. Lee `.claude/brain/constraints.md`
4. Busca vulnerabilidades:
   - Injection, auth bypass, secrets, CVEs, data leaks
5. Produce JSON estructurado:

```json
{
  "spec_id": "SPEC-NNN",
  "reviewer": "security",
  "verdict": "PASS",
  "findings": []
}
```

Para esta tarea de test (GET /api/version sin auth), el resultado
esperado es **PASS con cero findings** — no hay superficie de ataque.

Si el Builder hizo algo raro (hardconeo un secret, agrego una dependencia
vulnerable), el reviewer deberia encontrarlo.

**Criterios de PASS**:

- [ ] Solo reviso seguridad (no code style, no UX)
- [ ] Leyo el spec para identificar vulns intencionales
- [ ] Leyo el Brain (constraints de seguridad)
- [ ] Output en JSON estructurado con severity/type/file/line
- [ ] Verdict coherente con findings (PASS si 0 findings, FAIL si >0)
- [ ] NO modifico archivos
- [ ] NO dio consejos genericos ("consider adding logging")

**Criterios de FAIL**:

- Reviso code style o arquitectura (scope del Code Reviewer)
- Encontro "vulnerabilidades" genéricas sin evidencia concreta
- No leyo el spec (flaggeo vulns intencionales como findings)
- Output en texto libre en vez de JSON estructurado

**Accion post-validacion**: guardar el JSON de findings para el Approver.

---

## Expert 4: Code Reviewer

**Que hace**: revisa SOLO calidad de codigo y consistencia con el Brain.
Contexto limpio. Modelo diferente (Haiku 5.5). Solo lectura.

**Como lanzar**: abrir [Code Reviewer](https://app.augmentcode.com/home?expertId=f7fbc81a-8bc3-4ba7-ac24-3eb47332f0e7) y enviar:

```
Review code of SPEC-NNN on branch factory/SPEC-NNN
```

**Que esperar**:

1. Lee el Brain completo (decisions, constraints, patterns)
2. Lee el spec
3. Lee el diff en branch `factory/SPEC-NNN`
4. Verifica contra Brain:
   - Decisiones respetadas
   - Constraints seguidos
   - Patrones usados correctamente
5. Verifica code quality:
   - Duplicacion, naming, error handling, test coverage, scope
6. Produce JSON estructurado:

```json
{
  "spec_id": "SPEC-NNN",
  "reviewer": "code",
  "verdict": "PASS",
  "findings": []
}
```

Para esta tarea, el resultado esperado es **PASS** o PASS con findings menores
(naming, test coverage). No deberia haber violations del Brain.

**Criterios de PASS**:

- [ ] Solo reviso code quality (no seguridad)
- [ ] Leyo el Brain y cito referencias especificas
- [ ] Verifico que el Builder no agrego scope extra
- [ ] Verifico test coverage del nuevo endpoint
- [ ] Output en JSON con category/file/line/brain_reference
- [ ] Verdict coherente
- [ ] NO modifico archivos

**Criterios de FAIL**:

- Reviso seguridad (scope del Security Reviewer)
- No cito Brain references ("violates constraint" sin especificar cual)
- Output en texto libre sin estructura
- Flaggeo cosas que el spec explicitamente pide

**Accion post-validacion**: guardar el JSON de findings para el Approver.

---

## Expert 5: Approver

**Que hace**: consolida findings de ambos reviewers, verifica cada uno contra
el codigo real, decide fix loop o approve, y crea la PR.

**Como lanzar**: abrir [Approver](https://app.augmentcode.com/home?expertId=43a35b12-7470-49dc-a4ee-82a39b94e2b6) y enviar:

```
Approve SPEC-NNN on branch factory/SPEC-NNN

Security Reviewer findings:
{pegar JSON del Security Reviewer}

Code Reviewer findings:
{pegar JSON del Code Reviewer}
```

**Que esperar**:

1. Recolecta findings de ambos reviewers
2. Por cada finding, lee el codigo real y clasifica:
   - CONFIRMED → debe arreglarse
   - FALSE_POSITIVE → descarta con razon
   - INTENTIONAL → referencia spec.vulnerabilities_intended
   - DEFERRED → crea Jira ticket
3. Si hay CONFIRMED → compila fix list y rechaza (devuelve al Builder)
4. Si cero CONFIRMED → clasifica riesgo:

Para esta tarea (GET /api/version):
- Solo frontend/endpoint trivial
- Sin DB, sin auth, sin backend logic critico
- Clasificacion esperada: **LOW RISK**

5. LOW RISK → crea PR automaticamente:
   - De `factory/SPEC-NNN` a `secops/ai-agentic-demo-main`
   - Titulo con Jira ID
   - Body con summary, reviewer verdicts, evidence

6. Reporta decision:

```
## Approval Decision: SPEC-NNN

### Verdict: APPROVED

### Finding Resolution
(ninguno o tabla con findings resueltos)

### Risk: LOW
### PR: https://github.com/crizstian/ai-agentic-demo/pull/NNN
```

**Criterios de PASS**:

- [ ] Verifico cada finding contra codigo real (no rubber-stamp)
- [ ] Clasifico riesgo correctamente (LOW para esta tarea)
- [ ] PR creada hacia `secops/ai-agentic-demo-main` (NO `main`)
- [ ] PR title incluye Jira ID
- [ ] PR body tiene summary y reviewer verdicts
- [ ] Documenta razon de findings descartados (si aplica)

**Criterios de FAIL**:

- Aprobo sin verificar findings
- PR hacia `main` (viola Brain decision)
- Clasifico HIGH RISK sin razon (es un endpoint trivial sin auth)
- No creo PR despues de aprobar
- Hizo merge (solo crea PR, no hace merge)

---

## Checklist Final del Loop Completo

Despues de validar los 5 Experts individualmente:

- [ ] Spec Writer genero YAML ASDD valido
- [ ] Builder implemento con TDD en branch `factory/SPEC-NNN`
- [ ] Security Reviewer dio verdict con JSON estructurado
- [ ] Code Reviewer dio verdict con Brain references
- [ ] Approver creo PR hacia `secops/ai-agentic-demo-main`
- [ ] Jira ticket creado y actualizado con PR link
- [ ] `VERSION.txt` existe con `1.0.0`
- [ ] `GET /api/version` responde `{"version": "1.0.0"}`
- [ ] Ningun Expert salio de su scope
- [ ] Ningun Expert modifico archivos que no debia
- [ ] Pipeline de Harness se triggerea con la PR (outer loop)

## Cleanup post-test

Si la validacion fue exitosa y no quieres mantener el cambio:

```bash
# Cerrar PR sin merge
gh pr close NNN

# Borrar branch de test
git push origin --delete factory/SPEC-NNN

# Borrar spec de test
rm docs/specs/SPEC-NNN.yaml
```

Si la validacion fue exitosa y quieres probar el outer loop:
dejar la PR abierta y verificar que el pipeline de Harness corre.
