# Plan: Migración Demo Flow a Harness Code

Crear un set paralelo de pipelines, triggers, services y agents que usen el repo de Harness Code en lugar de GitHub. El setup actual de GitHub NO se modifica.

## Repo Harness Code

- **URL git:** `https://git.harness.io/EeRjnXTnS4GrLG5VNNJZUw/sandbox/CristianRamirez/ai-agentic-demo.git`
- **Remote local:** `harness` (configurado, sin credenciales en URL)
- **Branches:** `main`, `secops/ai-agentic-demo`, `secops/ai-agentic-demo-main`

## Recursos existentes (listos para usar)

| Recurso | ID | Tipo | Status |
|---|---|---|---|
| Git Connector | `CodeRepoCristianRamirez` | Git (Account) | SUCCESS |
| MCP Connector | `mcp_harness_cristian` | MCP | SUCCESS |
| Secret (git auth) | `CodeRepoToken` | String | Configurado |
| Secret (API key) | `harnessToken` | String | Configurado |

## Recursos a crear

### 1. Pipeline `ai_sdlc_demobank_hc`

Clon de `ai-sdlc-demobank` con estos cambios:

| Campo | GitHub (actual) | Harness Code (nuevo) |
|---|---|---|
| `connectorRef` | `CristianConnector` | `CodeRepoCristianRamirez` |
| `repoName` | `ai-agentic-demo` | `ai-agentic-demo` |
| MCP servers (agents) | `mcp_github_cristian` | `mcp_harness_cristian` |
| Git push URL (L219) | `https://github.com/crizstian/ai-agentic-demo.git` | `https://git.harness.io/EeRjnXTnS4GrLG5VNNJZUw/sandbox/CristianRamirez/ai-agentic-demo.git` |
| Git credentials (L220) | `https://x-access-token:%s@github.com` | `https://code_token_vfJto:%s@git.harness.io` |
| Git token secret (L238) | `CristianGithub` | `CodeRepoToken` |
| SCS repo URL (L427) | `https://github.com/crizstian/ai-agentic-demo` | `https://git.harness.io/EeRjnXTnS4GrLG5VNNJZUw/sandbox/CristianRamirez/ai-agentic-demo` |
| SCS token (L445) | `CristianGithub` | `CodeRepoToken` |

Agents inline afectados (4):
- Coding Agent — `mcp_github_cristian` → `mcp_harness_cristian`
- Security Agent — `mcp_github_cristian` → `mcp_harness_cristian`
- QA UI Analyzer — `mcp_github_cristian` → `mcp_harness_cristian`
- Quality Agent — `mcp_github_cristian` → `mcp_harness_cristian`

### 2. Pipeline `DemoBank_Reset_Deploy_HC`

Clon de `DemoBank_Reset_Deploy` con `connectorRef: CodeRepoCristianRamirez`.

### 3. Pipeline `kubernetes_remediation_hc`

Clon de `kubernetes-remediation` con:
- `mcp_github_cristian` → `mcp_harness_cristian`
- `CristianGithub` → `CodeRepoToken`
- Referencia al agent `manifest-remediator-hc`

### 4. Agent `manifest-remediator-hc`

Clon de `manifest-remediator` con cambios en el prompt:

| Campo | GitHub (actual) | Harness Code (nuevo) |
|---|---|---|
| `Repo:` (L20) | `crizstian/ai-agentic-demo` | `ai-agentic-demo` |
| Fallback (L27) | `GitHub MCP fallback` | `Harness MCP` |
| MCP servers (L72-73) | `mcp_github_cristian` | `mcp_harness_cristian` |
| Secret (L60) | `CristianGithub` | `CodeRepoToken` |

Branches en el prompt no cambian:
- `fix/manifest-remediation from secops/ai-agentic-demo` (igual)
- `Create PR to secops/ai-agentic-demo-main` (igual)

### 5. Services

| Service nuevo | Clon de | Cambio |
|---|---|---|
| `demobank_hc` | `demobank` | Manifest `connectorRef: CodeRepoCristianRamirez` |
| `mcp_financial_data_hc` | `mcp_financial_data` | Manifest `connectorRef: CodeRepoCristianRamirez` |

Docker images (`DockerCristian`, `docker.io/crizstian/*`) NO cambian.

### 6. Triggers (4)

| Trigger | Tipo | Pipeline target |
|---|---|---|
| `main_build_deploy_hc` | Harness Code push | `ai_sdlc_demobank_hc` |
| `pr_validation_hc` | Harness Code PR | `ai_sdlc_demobank_hc` |
| `kubernetes_fix_deploy_hc` | Harness Code push (QA fix) | `ai_sdlc_demobank_hc` |
| `manifest_remediation_hc` | Harness Code PR (manifest fix) | `kubernetes_remediation_hc` |

Los triggers de Harness Code son nativos (no webhooks externos) — no requieren configuración de webhook en el repo.

## No cambia (se reusa)

- **Environments:** `gke_latam` / `latam_nodepool`
- **Connectors:** `DockerCristian`, `org.se_sandbox_k8s`, `account.Harness_JIRA`
- **K8s namespace/deployments:** mismo `demobank`, mismo namespace
- **Branch names:** `secops/ai-agentic-demo`, `secops/ai-agentic-demo-main`, `main`
- **OPA policies**
- **Demo prompts** (`docs/demo-prompts-consolidated.md`)
- **Reset script** (`scripts/demo-reset.sh`) — usa git local, no depende del remote

## Notas importantes

1. **No correr ambos pipelines simultáneamente** — ambos despliegan al mismo Deployment en K8s. Canary/rolling colapsarían si corren en paralelo.
2. **Sincronizar repos** — después de cada reset, hacer `git push harness <branch>` además de `git push origin <branch>`. El reset script solo pushea a `origin` (GitHub).
3. **El reset script necesitaría un flag `--push-harness`** para pushear al remote de Harness Code automáticamente.
4. **Credenciales** — el remote `harness` no tiene credenciales en la URL. Para push se necesita PAT inline o configurar credential helper.
