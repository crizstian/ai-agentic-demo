# Architectural Decisions

Decisiones tomadas que cualquier agente (Claude Code, Cosmos Expert, Worker Agent)
debe conocer y respetar. Actualizadas conforme se toman nuevas decisiones.

---

## Identity & Auth

- **Harness PAT**: `harnessToken` secret para platform auth (MCP, agents, API)
- **GitHub PAT**: `CristianGithub` secret para git push y PR operations
- **Split server-side key**: `v4kvjbb2cuupu0ihed20iceumvv1m9po07bn` (Python backend)
- **Split client-side key**: `cl0bl351743733kglfasq85pr2kq8ul9rmqv` (browser JS)
- **Jira**: project HD, issue type Task, connector `account.Harness_JIRA`

## Feature Flags (Split/FME)

- `ai_chat_enabled` — frontend widget visibility (client-side SDK)
- `ai_chat_backend` — backend endpoint gate (server-side SDK)
- Backend flag check: SDK primero, fallback a REST API si SDK devuelve "control"
- Split SDK en Python: lazy init obligatorio (evitar timeout en CI)
- Pipeline activa/desactiva flags en paralelo por fase (QA, Beta, GA, Full, Rollback)

## Branching Strategy

- `secops/ai-agentic-demo` — branch de trabajo (base/reset source)
- `secops/ai-agentic-demo-main` — merge target para PRs
- `main` — NO se usa directamente
- PRs siempre a `secops/ai-agentic-demo-main`, NUNCA a `main`
- Push solo al remote que el usuario pide (github vs harness, no ambos)

## Pipeline

- Pipeline `AI_SDLC_DemoBank` es INLINE — sync via MCP despues de editar YAML local
- Sync MCP ANTES de push (evitar trigger con YAML viejo)
- AI Evals step necesita `HARNESS_API_KEY` + `HARNESS_TOKEN` en envVariables
- AI Evals `expected_output` debe ser string plano, no dict
- STO filter keys: `severity_codes` y `issue_types` (no `severity`/`issueType`)

## Worker Agents

- Image: `harness/harness-ai-agent:0.1.77` (via connector `account.harnessImage`)
- `HARNESS_TOKEN`: usar `<+secrets.getValue("harnessToken")>` (no CristianGithub)
- `PLUGIN_MAX_TURNS`: declarar como input formal, no hardcodear
- GitHub MCP no tiene `delete_branch` — nunca intentar borrar branches
- Agents fallan "Not logged in" en webhook triggers — necesita executor identity
- 5 agents: code_reviewer, security_analyzer, ca_code_unit_test_generator,
  qa_ui_analyzer, ca_manifest_remediation_v2

## Kubernetes / GKE

- Cluster: `se-sandbox` (us-east1-b), namespace: demobank
- deployment.yaml debe incluir `harness.io/track: stable` en labels y selector
- Canary: `count: 2` (pods efimeros), no porcentaje
- Delegate: `se-sandbox-org-delegate` (org scope)

## Application Code

- Response JSON keys exactas: `response`, `financial_context`, `model`
- MCP Financial Data URL: `os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")`
- OPENAI_API_KEY via ConfigMap `harnessbank-demo-end2end-config`
- CSS: solo agregar reglas nuevas al final, nunca modificar existentes
- `<+input>.default()` sin quotes en CD stages

## Reset & Demo

- SIEMPRE usar `scripts/demo-reset.sh --db --commit --push`, nunca git checkout manual
- Reset preserva: docs/, deploy/, .harness/, scripts/, policies/
- Reset borra: app/routes/ai_assistant.py
- Reset restaura desde main: app/*.py, templates, static, requirements.txt
- Harness Code pipeline (`_HC`) y GitHub pipeline no correr simultaneamente

## Supply Chain & Security

- SCS/SLSA: todos los steps keyless (Harness OIDC, cosign keyless)
- Harness secret vars: `type: String` + JEXL expression, NUNCA `type: Secret`
- HC payload paths: `pull_req` (no `pull_request`), actions `Create/Update/Reopen`
- Harness pipeline schema: github.com/harness/harness-schema
