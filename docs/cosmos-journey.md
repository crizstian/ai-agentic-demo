# Cosmos Journey — De Devcontainer a Software Factory

Tracking document del progreso de transformacion.

---

## Estado Actual

| Setup | Estado |
|-------|--------|
| Devcontainer + Claude Code | Operativo |
| MCPs: Harness, Jira, K8s, Perplexity, Chrome, Docs | Operativo |
| Harness Pipeline + 5 Worker Agents | Operativo |
| Demo Reset Script | Operativo |
| Cosmos Account | Activo |
| Factory Architecture Doc | docs/factory-architecture.md |

## Steps Completados

### Step 1: Formalizar el Brain (2026-11-08)

**Objetivo**: consolidar conocimiento disperso (memory/, CLAUDE.md, docs/, historial)
en estructura que cualquier agente pueda consumir.

**Que se hizo**:
- Creado `.claude/brain/` con 3 archivos:
  - `decisions.md` — 25+ decisiones de arquitectura consolidadas de 25 memory files
  - `constraints.md` — 10 hard constraints, 6 soft constraints, 5 anti-patterns
  - `patterns.md` — 6 patrones validados con codigo ejemplo y razon

**Estructura final**:
```
.claude/
├── CLAUDE.md              ← reglas del proyecto (ya existia)
├── memory/                ← feedback y estado (ya existia, 25 archivos)
├── brain/                 ← NUEVO
│   ├── decisions.md       ← decisiones de arquitectura
│   ├── constraints.md     ← restricciones obligatorias
│   └── patterns.md        ← patrones validados con codigo
└── agents/                ← agent definitions (ya existia)
```

**Por que importa**: antes, un agente nuevo empezaba de cero y repetia errores
ya resueltos (Split key incorrecta, agent turns wasted, CSS roto). Ahora
cualquier agente puede leer el Brain y evitar esos errores desde el primer turn.

**Diferencia con memory/**: memory/ guarda feedback individual y estado temporal.
brain/ consolida las conclusiones permanentes en formato consumible por agentes.

---

### Step 2: Agregar Specs al Workflow (2026-11-08)

**Objetivo**: convertir prompts de texto libre a formato ASDD verificable,
para que agentes puedan auto-demostrar que cumplieron el requisito.

**Que se hizo**:
- Creado `docs/specs/` con 4 specs en formato ASDD:
  - `act0-demo-reset.yaml` — spec del reset (16 invariantes)
  - `act1-ai-assistant.yaml` — spec completa del Act 1 con 5 vulns intencionales
  - `act3-security-remediation.yaml` — spec del security_analyzer agent
  - `preflight-check.yaml` — spec del pre-flight validation

**Formato ASDD por spec**:
- `what_user_can_do` — acciones del usuario final
- `expected_result` — resultado concreto (status codes, JSON keys, archivos)
- `must_respect` — restricciones obligatorias
- `vulnerabilities_intended` — vulns intencionales con IDs y scanner
- `how_to_demonstrate` — comandos automaticos + pasos manuales
- `evidence` — artefactos que prueban que se cumplió
- `budget` — tiempo estimado y max turns

**Relacion prompt vs spec**: el prompt (1.1) es la INSTRUCCION para el agente.
La spec es la VERIFICACION de que el agente hizo lo correcto. Un agente puede
leer la spec y ejecutar `how_to_demonstrate` para auto-verificar.

---

### Step 3: Automatizar el Reset + Pre-flight (2026-11-08)

**Objetivo**: crear script de pre-flight standalone y conectarlo al reset.

**Que se hizo**:
- Creado `scripts/preflight-check.sh` con 4 categorias de checks:
  - Connectivity: App health, Split API, MCP Financial Data
  - Feature Flags: ai_chat_enabled, ai_chat_backend (act0 vs act1 mode)
  - Auth & Secrets: GitHub auth, HARNESS_API_KEY, OPENAI_API_KEY
  - Pipeline: AI_SDLC_DemoBank existence + last run status
  - STATE 0 invariants (--full): ai_assistant absent, vulns present, test count
- Modos: `--full` (incluye invariantes), `--act1` (espera flags ON), `--json` (machine-readable)
- Integrado en `demo-reset.sh`: ejecuta preflight automaticamente post-reset
- JSON output valido para consumo por Cosmos Expert o Harness pipeline

**Resultado del test**:
- Sin --full: 7/9 PASS, 0 FAIL, 2 WARN (MCP in-cluster, OPENAI_API_KEY) → READY
- Con --full: STATE 0 invariants fallan correctamente (branch tiene Act 1 code)

---

### Step 4: Factory Architecture — Inner/Outer Loop Mapping (2026-11-08)

**Objetivo**: razonar como los 3 sistemas (RSC Factory methodology, Cosmos,
Harness) se integran antes de crear ningun Expert.

**Que se hizo**:
- Creado `docs/factory-architecture.md` con mapeo completo
- Identificado 2 loops:
  - **Inner loop (Cosmos)**: trabajo cognitivo — spec, code, review, approve
  - **Outer loop (Harness)**: trabajo determinista — build, test, scan, deploy
- Mapeado cada paso del transcript a Cosmos o Harness (o ambos)
- Descubierto que los Reviewers se REPARTEN entre loops:
  - Pre-PR review (Cosmos Experts): razonamiento sobre intent
  - Post-PR scan (Harness STO + workers): deteccion determinista
- Definido 5 Experts para v1: Spec Writer, Builder, Security Reviewer,
  Code Reviewer, Approver
- Documentado 10 decisiones de arquitectura
- Worker agents de Harness NO migran a Cosmos (son efimeros, pipeline-bound)

**Documento**: `docs/factory-architecture.md`

---

## Steps Pendientes

### Step 5: Crear Environment + Experts en Cosmos
- Prompts documentados en `docs/cosmos-setup-prompts.md`
- Pre-req: cuenta Cosmos activa, integraciones GitHub + Slack + Jira
- Setup order: Environment → Spec Writer → Builder → Reviewers → Approver
- Todos empiezan con automation OFF, activar despues de test manual
- Test de validacion: tarea simple (GET /api/version)

### Step 6: Test del Factory Loop Completo
- Enviar tarea via Slack → Spec Writer → Builder → Reviewers → Approver → PR
- Validar fix loop (forzar un finding, verificar que el Builder arregla)
- Validar risk routing (low risk = auto, high risk = Slack a humano)

### Step 7: Conectar Inner → Outer Loop
- PR del Approver triggerea pipeline Harness automaticamente
- Feedback loop: pipeline fail → Cosmos Fixer Expert
- Validar e2e: tarea → spec → code → PR → pipeline → deploy

---

## Decisiones del Journey

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-11-08 | Brain en `.claude/brain/` no en docs/ | Parte de la config del agente, no documentacion del proyecto |
| 2026-11-08 | 3 archivos (decisions, constraints, patterns) | Separation of concerns: que se decidio, que no hacer, como hacerlo |
| 2026-11-08 | No migrar memory/ a brain/ | Memory es feedback temporal, Brain es conocimiento permanente consolidado |
| 2026-11-08 | Specs en YAML no Markdown | YAML es parseable por agentes, Markdown es para humanos |
| 2026-11-08 | Specs separadas del prompt | Prompt = instruccion, Spec = verificacion. El agente ejecuta el prompt y valida contra la spec |
| 2026-11-08 | 4 specs iniciales (act0, act1, act3, preflight) | Los acts mas automatizables. Acts 5-7 son mas manuales/interactivos |
| 2026-11-08 | Preflight integrado en reset (auto-run) | Detecta problemas inmediatamente despues del reset, sin paso manual extra |
| 2026-11-08 | MCP Financial Data es WARN no FAIL | Solo accesible in-cluster, no bloquea readiness desde devcontainer |
| 2026-11-08 | Steps 3+4 fusionados | Pre-flight es parte del reset automation, no necesita step separado |
| 2026-11-08 | Inner loop=Cosmos, Outer loop=Harness | Cosmos razona (cognitivo), Harness ejecuta (determinista). No se solapan |
| 2026-11-08 | Reviewers split pre-PR (Cosmos) + post-PR (Harness) | Defensa en profundidad: reviewer opina, scanner detecta. Ambos necesarios |
| 2026-11-08 | Worker agents quedan en Harness | Son efimeros, corren en container del pipeline. Su contexto es PR+findings |
| 2026-11-08 | Cosmos nunca deploya | Experts crean PRs/tickets, Harness aplica policies sin importar origen del PR |
| 2026-11-08 | Modelos diversos en reviewers | Transcript: "Opus se sesgaria revisandose a si mismo". Security=Sonnet, Code=Haiku |
| 2026-11-08 | v1 con 5 Experts, UX/UI reviewers en v2 | Validar flujo core primero, agregar reviewers especializados despues |
| 2026-11-08 | Brain en Cosmos Files, bridge via .claude/brain/ | Mismo contenido, dos puntos de acceso: Cosmos Experts y Claude Code local |
