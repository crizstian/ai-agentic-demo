# Cobertura Demo vs RFP — Compartamos Peru

> Analisis de cobertura del demo AI-Native SecOps (6 Actos) contra las 3 matrices del RFP.
> Fecha: 2026-09-28
> Tipo: **TEC** = capacidad técnica de plataforma | **NO-TEC** = certificación, SLA, infra SaaS, proceso, contractual

---

## Resumen Ejecutivo

| Matriz | Total | TEC | NO-TEC | Demo | UI | Doc | Gap |
|---|---|---|---|---|---|---|---|
| Arquitectura Seguridad TI | 27 | 15 (56%) | 12 (44%) | 8 | 3 | 16 | 0 |
| Arquitectura TI | 98 | 70 (71%) | 28 (29%) | 39 | 11 | 47 | 1 |
| Funcional | 116 | 115 (99%) | 1 (1%) | 54 | 24 | 37 | 1 |
| **Total** | **241** | **200 (83%)** | **41 (17%)** | **101** | **38** | **100** | **2** |

### Vista tradicional (todos los requisitos)

- **Demo + UI = 139/241 = 58%**
- **Harness "Cumple" = 239/241 = 99.2%**
- **Gaps reales = 2** (Core bancario, PR templates nativas)

### Vista tecnica (solo capacidades de plataforma)

- **Demo + UI sobre TEC = 139/200 = 69.5%**
- **Faltantes TEC = 61** (DOC tecnico promotable)
- **Techo alcanzable = 200/200 = 100%**

> El 17% del RFP (41 req) son certificaciones, SLAs, specs de infra SaaS y contractual — no demostrables por ningun vendor. Se responden con `trust.harness.io` y documentacion.

### Categorias

| Categoria | Significado |
|---|---|
| **TEC** | Capacidad tecnica de plataforma: feature, pantalla, API, comportamiento demostrable |
| **NO-TEC** | Certificacion, SLA, infra inherente, spec de performance, contractual, proceso del vendor |
| **Demostrado en Vivo** | El demo flow lo ejecuta y el audience lo ve en accion |
| **Mostrable en UI** | Se puede abrir en Harness UI durante el demo (pantallas, dashboards, configs) |
| **Solo Doc** | Capacidad respaldada por documentacion/certificaciones |
| **Gap** | No cubierto o cumplimiento parcial |

---

## Matriz Funcional — Detalle (116 requisitos)

### CI/CD — Integracion y Despliegue Continuo (74 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 1 | Templates reutilizables versionados en Git | TEC | UI | Template Library en Harness |
| 2 | Variables/expresiones del trigger | TEC | DEMO | `<+trigger.sourceBranch>`, `<+codebase.commitMessage>` en pipeline |
| 3 | Triggers nativos (PR, push, webhook, cron) | TEC | DEMO | PR trigger (Act 2), push trigger (Act 4), webhook (Manifest Remediator) |
| 4 | Ejecucion manual por UI | TEC | UI | Pipeline Run button |
| 5 | Parametros de entrada por UI | TEC | DEMO | `imageTag` como runtime input con default |
| 6 | Parametros por API | TEC | DOC | REST API documentada |
| 7 | Ejecucion por API | TEC | DOC | POST /pipeline/api/pipeline/execute |
| 8 | Input Sets versionados | TEC | UI | Input Sets en Pipeline Studio |
| 9 | Pipeline como YAML en Git | TEC | DEMO | Pipeline YAML visible en IDE todo el demo |
| 10 | Templates globales centralizadas | TEC | UI | Account/Org/Project templates |
| 11 | Extensiones y conectores | TEC | DEMO | DockerCristian, K8s, Jira, MCP connectors |
| 12 | Cobertura y quality gates | TEC | DEMO | Test Intelligence con JUnit reports (Act 2) |
| 13 | Gates de seguridad/calidad | TEC | DEMO | Semgrep HIGH > 0 trigger, Jira CAB Approval |
| 14 | Ejecucion condicional (when/expressions) | TEC | DEMO | `when` en Jira steps, Supply Chain, Build conditions |
| 15 | Matrix/parallelism | TEC | DEMO | SAST+SCA+Secrets parallel, SBOM+SLSA+Signing parallel |
| 16 | Pipeline visual + YAML editor | TEC | DEMO | Pipeline Studio visible en Harness UI |
| 17 | Anotaciones/metadata ejecuciones | TEC | UI | Annotations, Execution Tags |
| 18 | Timeout, re-run selectivo de stages | TEC | DEMO | Manifest Remediator re-ejecuta solo Deploy stages |
| 19 | Validaciones/aprobaciones manuales | TEC | DEMO | Jira CAB Approval Gate (Act 4) |
| 20 | Templates multi-repo | TEC | UI | Remote Templates |
| 21 | Templates versionados multi-repo | TEC | UI | Version Labels (Stable) |
| 22 | Catalogo de templates | TEC | UI | Template Library |
| 23 | Cache inteligente de dependencias | TEC | DEMO | `caching: enabled: true` en CI stage |
| 24 | Infra de build flexible (Cloud/K8s/VM) | TEC | DEMO | Harness Cloud runners en CI |
| 25 | Agentes Mac | TEC | DOC | Harness Cloud macOS M1 |
| 26 | Agentes Linux | TEC | DEMO | Build en Linux Amd64 |
| 27 | Aislamiento por build (contenedor efimero) | TEC | DEMO | Harness Cloud VMs efimeras |
| 28 | Monitoreo de agentes | TEC | UI | Delegates page con heartbeat |
| 29 | Logs de ejecucion almacenados | TEC | DEMO | Console View con drill-down en cada step |
| 30 | Integracion artifact repos (Docker, JFrog) | TEC | DEMO | Build and Push a Docker Hub x2 |
| 31 | Herramientas de build (Maven, pip, npm) | TEC | DEMO | pip install en CI |
| 32 | Multi-lenguaje | TEC | DEMO | Python backend, JS frontend |
| 33 | Runners como pods en K8s | TEC | DEMO | Delegates en GKE |
| 34 | Test Intelligence (ML) | TEC | DEMO | `intelligenceMode: true` en Test step |
| 35 | Dashboard eficiencia pipelines | TEC | UI | Pipeline Insights |
| 36 | Performance testing (k6/JMeter) | TEC | DOC | Resilience Testing module |
| 37 | RCA automatico con AI | TEC | DEMO | Manifest Remediator diagnostica + AIDA |
| 38 | Paso de datos entre steps | TEC | DEMO | JIRA_ID output variable CI a CD |
| 39 | Cache de dependencias por lenguaje | TEC | DEMO | Cache Intelligence auto-detect |
| 40 | Control ejecuciones concurrentes | TEC | UI | Concurrent pipeline limits |
| 41 | Failure strategies granulares | TEC | DEMO | StageRollback, MarkAsSuccess, Retry en healthcheck |
| 42 | Status checks en PR | TEC | DEMO | Pipeline status check bloquea/permite merge |
| 43 | Container step (cualquier imagen) | TEC | DEMO | Supply Chain stepGroupInfra K8s |
| 44 | Docker Layer Caching | TEC | DEMO | `caching: true` en Build and Push steps |
| 45 | K8s deploy (Manifests/Helm/Kustomize) | TEC | DEMO | K8s Canary + Rolling con manifests |
| 46 | Deployment Templates custom | TEC | DOC | Custom Deployment Templates |
| 47 | GitOps (Argo CD) | TEC | UI | GitOps module en Harness |
| 48 | Approval gates con Jira/ServiceNow | TEC | DEMO | JiraApproval CAB gate (Act 4) |
| 49 | Loop, Parallelism, Matrix | TEC | DEMO | Parallel en multiples step groups |
| 50 | Politicas OPA bloquean deploy | TEC | DEMO | OPA policy creada en Act 6 |
| 51 | Secrets injection sin exposicion en logs | TEC | DEMO | `secrets.getValue("CristianGithub")` enmascarado |
| 52 | Bovedas externas (Vault, KMS) | TEC | UI | Secret Manager configs |
| 53 | Canary deployment declarativo | TEC | DEMO | K8sCanaryDeploy, healthcheck, delete, rolling |
| 54 | Analisis automatico de Canary (CV/ML) | TEC | UI | Continuous Verification module |
| 55 | Monitoreo post-deploy (APMs) | TEC | UI | CV integrations (Datadog, Prometheus, etc.) |
| 56 | Rollback automatico ante fallo | TEC | DEMO | Canary falla, rollbackSteps ejecutan |
| 57 | Rollback manual | TEC | UI | Post Deployment Rollback |
| 58 | Multi-ambiente multi-cloud | TEC | DEMO | Deploy a GKE (infra definitions) |
| 59 | Deployment Freeze Windows | TEC | UI | Freeze config en Harness (config rapida) |
| 60 | Trazabilidad completa del artefacto | TEC | DEMO | SBOM + SLSA + Artifact Signing + Chain of Custody |
| 61 | Release orchestration multi-servicio | TEC | DOC | Release Orchestration module |
| 62 | Ambientes efimeros | TEC | DOC | IDP Environment Management |
| 63 | Promocion ordenada (Dev-QA-Prod) | TEC | DOC | Propagate Service, artifact copy |
| 64 | Visualizacion grafica en tiempo real | TEC | DEMO | Pipeline execution graph en UI |
| 65 | IaC provisioning (Terraform, CDK) | TEC | DOC | IaCM module |
| 66 | Resource Constraints | TEC | DOC | Auto-enabled en stages |
| 67 | HTTP step nativo | TEC | DEMO | Portal Healthcheck (GET + retry) |
| 68 | Event Listener (esperar evento externo) | TEC | DOC | Event Listener Step |
| 69 | ITSM bidireccional (Jira/ServiceNow) | TEC | DEMO | Jira Create (Act 1), Update, Approval, Done/Rejected |
| 70 | OIDC tokens efimeros | TEC | DOC | AWS/Azure/GCP OIDC |
| 71 | Auto-cancelacion pipelines redundantes | TEC | DOC | Auto-abort Previous Execution |
| 72 | Multi-arch builds | TEC | DOC | PLUGIN_PLATFORM multi-arch |
| 73 | Pipeline Chaining | TEC | DEMO | Webhook trigger a Kubernetes_Remediation pipeline |
| 74 | CLI oficial | TEC | DOC | Harness CLI |

**CI/CD: 42 DEMO (57%) | 17 UI | 15 DOC | TEC=74, NO-TEC=0**

---

### Repositorios de Codigo (19 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 1 | Repo Git centralizado | TEC | DOC | Harness Code (demo usa GitHub) |
| 2 | Git LFS | TEC | DOC | CODE_GIT_LFS_ENABLED |
| 3 | Sparse checkout / shallow clone | TEC | DOC | sparseCheckout en pipeline |
| 4 | Branch protection + tagging | TEC | DEMO | Branch `secops/ai-agentic-demo-main` protegida |
| 5 | Block force push | TEC | DOC | Branch rules |
| 6 | Merge strategies (squash, rebase) | TEC | DOC | 4 estrategias configurables |
| 7 | Merge Queues | TEC | DOC | Merge Queue nativa |
| 8 | Code Owners | TEC | DOC | CODEOWNERS file |
| 9 | Block unresolved comments | TEC | DOC | Branch rule |
| 10 | Code suggestions inline | TEC | DOC | Suggestion blocks en PRs |
| 11 | Dismiss stale approvals | TEC | DOC | Branch rule |
| 12 | Draft PRs | TEC | DOC | Create draft PR |
| 13 | PR templates | TEC | GAP | Cumple parcial (AI PR Summary, no templates nativos) |
| 14 | Trazabilidad deploys desde PR | TEC | DEMO | Status checks visibles en PR |
| 15 | Gitspaces (cloud dev envs) | TEC | DOC | Gitspaces |
| 16 | Status checks obligatorios | TEC | DEMO | Pipeline CI bloquea merge si falla |
| 17 | Repository templates (IDP) | TEC | DOC | IDP Workflows scaffolding |
| 18 | Reglas globales (org/account) | TEC | DOC | Rules a 4 niveles de scope |
| 19 | SCIM sync accesos | TEC | DOC | SCIM provisioning |

**Repos: 3 DEMO (16%) | 0 UI | 15 DOC | 1 GAP | TEC=19, NO-TEC=0**

> Nota: El demo usa GitHub como SCM, no Harness Code. Los 15 requisitos de repo son capacidades de Harness Code documentadas. Para demos futuros, migrar a Harness Code cubriria 10+ adicionales.

---

### Plataforma (17 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 1 | Templates versionados | TEC | UI | Template Library |
| 2 | Gobierno de templates (OPA enforce) | TEC | DEMO | Act 6 crea politica OPA |
| 3 | Sobrescritura dinamica por contexto | TEC | UI | Service Overrides |
| 4 | Tags globales | TEC | UI | Tags en pipelines/services |
| 5 | Secrets management integrado | TEC | DEMO | `secrets.getValue()` en pipeline |
| 6 | Jerarquia de politicas (Account>Org>Project) | TEC | UI | OPA Policy hierarchy |
| 7 | OPA multi-entidad | TEC | DEMO | OPA en pipelines, connectors |
| 8 | Webhooks entrantes/salientes | TEC | DEMO | AI SRE webhooks, Manifest Remediator trigger |
| 9 | Pipeline Chaining (padre-hijo) | TEC | DEMO | Deploy falla, webhook, Kubernetes_Remediation |
| 10 | CLI oficial | TEC | DOC | Harness CLI |
| 11 | MCP Server | TEC | DEMO | Harness MCP usado en todos los actos |
| 12 | Notificaciones multicanal | TEC | DEMO | AI SRE notifications (build + deploy) |
| 13 | SSO/SCIM | TEC | DOC | SAML + SCIM |
| 14 | Audit Trail + SIEM | TEC | UI | Audit Trail page |
| 15 | Custom RBAC | TEC | UI | RBAC config screens |
| 16 | IDE Extension | TEC | DEMO | VS Code + Harness Extension + Claude Code |
| 17 | HA/SLA 99.9% | NO-TEC | DOC | SaaS architecture |

**Plataforma: 8 DEMO (47%) | 6 UI | 2 DOC TEC | 1 DOC NO-TEC | TEC=16, NO-TEC=1**

---

### Migracion y Adopcion (6 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 1 | Migracion desde ADO | TEC | DOC | harness-migrate CLI + Import Repos |
| 2 | Traduccion de templates | TEC | DOC | Container Steps, Plugin Steps |
| 3 | Coexistencia hibrida | TEC | DOC | Webhooks bidireccionales |
| 4 | K8s Runners | TEC | DEMO | Delegates como pods en GKE |
| 5 | Gestion agentes heterogeneos | TEC | UI | Delegates 3.0 management |
| 6 | Extensions equivalentes | TEC | DOC | Container Steps |

**Migracion: 1 DEMO (17%) | 1 UI | 4 DOC | TEC=6, NO-TEC=0**

---

## Totales Matriz Funcional

| Seccion | Total | TEC | NO-TEC | Demo | UI | Doc | Gap |
|---|---|---|---|---|---|---|---|
| CI/CD | 74 | 74 | 0 | 42 (57%) | 17 | 15 | 0 |
| Repos | 19 | 19 | 0 | 3 (16%) | 0 | 15 | 1 |
| Plataforma | 17 | 16 | 1 | 8 (47%) | 6 | 3 | 0 |
| Migracion | 6 | 6 | 0 | 1 (17%) | 1 | 4 | 0 |
| **Total** | **116** | **115 (99%)** | **1 (1%)** | **54 (47%)** | **24 (21%)** | **37 (32%)** | **1 (1%)** |

### Cobertura sobre capacidades tecnicas funcionales

| Metrica | Valor |
|---|---|
| Capacidades tecnicas | 115 |
| Demostradas (DEMO+UI) | 78 |
| **% cobertura tecnica** | **68%** |
| Faltantes TEC en DOC | 36 |
| Faltantes TEC en GAP | 1 |

---

## Requisitos de Mayor Impacto para Banca (cubiertos)

Estos son los requisitos que un banco regulado valora mas, y que el demo demuestra:

| # | Requisito | Demo |
|---|---|---|
| 69 | ITSM bidireccional Jira | Jira Create, Update, Approval, Done/Rejected |
| 19 | Aprobaciones manuales (CAB) | JiraApproval gate con timeout |
| 48 | Approval gates Jira/ServiceNow | JiraApproval en Deploy stage |
| 53 | Canary deployment | K8sCanaryDeploy con healthcheck |
| 56 | Rollback automatico | rollbackSteps con Jira notification |
| 50 | Politicas OPA | Policy creada en Act 6 |
| 60 | Trazabilidad de artefactos | SBOM + SLSA + Signing |
| 51 | Secrets sin exposicion | Secrets enmascarados en logs |
| 42 | Status checks en PR | Branch protection |
| 34 | Test Intelligence | ML-based test selection |
| 13 | Gates de seguridad | SAST HIGH trigger |
| 41 | Failure strategies | StageRollback, Retry, MarkAsSuccess |

---

## Gaps Reales y Mitigacion

| Gap | Requisito | Tipo | Mitigacion |
|---|---|---|---|
| PR Templates (#13 Repos) | Templates nativos de PR | TEC | AI PR Summary + CODEOWNERS como alternativa |
| Core Bancario (#2.13 ArqTI) | Conector a core bancario | TEC | Delegate + HTTP step + VPN — narrativa |

---

## Faltantes de Demostrar — Consolidado (61 capacidades tecnicas)

### Por matriz

| Matriz | TEC Total | TEC DEMO+UI | TEC DOC | TEC GAP | % Cobertura TEC |
|---|---|---|---|---|---|
| Seguridad TI | 15 | 11 | 4 | 0 | 73% |
| Arquitectura TI | 70 | 50 | 19 | 1 | 71% |
| Funcional | 115 | 78 | 36 | 1 | 68% |
| **Total** | **200** | **139** | **59** | **2** | **69.5%** |

### Los 41 NO-TEC (no demostrables por ningun vendor)

| Categoria | Cant | Ejemplos |
|---|---|---|
| Certificaciones | 8 | ISO 27001, SOC2, ISO 22301, ISO 42001 |
| Contractual/comercial | 5 | SLAs, soporte, facturacion, licensing modular |
| Proceso del vendor | 3 | Pentesting, auditorias, politica no-training |
| Infra SaaS inherente | 19 | Cifrado, TLS, HA, DR, replicas, hardware, region, backups |
| Specs de performance | 6 | Latencia, tiempos respuesta, concurrencia, ancho banda |
| **Total** | **41** | Se responden con `trust.harness.io` + docs |

### Faltantes TEC promotables — Funcional (37)

#### CI/CD (15 DOC)

| # | Requisito | Promocion | Que mostrar/agregar |
|---|---|---|---|
| 6 | Parametros por API | UI | API Explorer → endpoint pipeline/execute |
| 7 | Ejecucion por API | UI | API Explorer → POST execute |
| 25 | Agentes Mac | UI | Harness Cloud → build infra → macOS runners |
| 36 | Performance testing | UI | Resilience Testing module overview |
| 46 | Deployment Templates custom | UI | Template Library → Deployment templates |
| 61 | Release orchestration | UI | Release Orchestration module |
| 62 | Ambientes efimeros | UI | IDP → Environment Management |
| 63 | Promocion ordenada | UI | Service Propagation config |
| 65 | IaC provisioning | UI | IaCM module overview |
| 66 | Resource Constraints | UI | Stage config → Resource Constraints |
| 68 | Event Listener | UI | Step Library → Event Listener |
| 70 | OIDC tokens efimeros | UI | Connector → OIDC config |
| 71 | Auto-cancelacion pipelines | UI | Pipeline → Advanced Settings → auto-abort |
| 72 | Multi-arch builds | DOC | PLUGIN_PLATFORM config (narrativa) |
| 74 | CLI oficial | UI | `harness --help` en terminal |

#### Repos (15 DOC + 1 GAP)

| # | Requisito | Promocion | Que mostrar/agregar |
|---|---|---|---|
| 1 | Repo Git centralizado | UI | Harness Code → Repos overview |
| 2 | Git LFS | DOC | Config flag (narrativa) |
| 3 | Sparse checkout | DOC | Pipeline codebase config (narrativa) |
| 5 | Block force push | UI | Harness Code → Branch Rules |
| 6 | Merge strategies | UI | Harness Code → Merge settings |
| 7 | Merge Queues | UI | Harness Code → Merge Queue config |
| 8 | Code Owners | UI | Harness Code → CODEOWNERS |
| 9 | Block unresolved comments | UI | Harness Code → Branch Rules |
| 10 | Code suggestions inline | UI | Harness Code → PR → Suggestion blocks |
| 11 | Dismiss stale approvals | UI | Harness Code → Branch Rules |
| 12 | Draft PRs | UI | Harness Code → Create PR → Draft toggle |
| 13 | PR templates | GAP | Mitiga: AI PR Summary + CODEOWNERS |
| 15 | Gitspaces | UI | Gitspaces module overview |
| 17 | Repository templates | UI | IDP → Workflows → scaffolding |
| 18 | Reglas globales | UI | Harness Code → Account-level rules |
| 19 | SCIM sync accesos | UI | Access Control → SCIM |

#### Plataforma (2 DOC)

| # | Requisito | Promocion | Que mostrar/agregar |
|---|---|---|---|
| 10 | CLI oficial | UI | `harness --help` en terminal |
| 13 | SSO/SCIM | UI | Authentication settings + SCIM providers |

#### Migracion (4 DOC)

| # | Requisito | Promocion | Que mostrar/agregar |
|---|---|---|---|
| 1 | Migracion desde ADO | UI | harness-migrate CLI docs + Import Repos screen |
| 2 | Traduccion templates | DOC | Container Steps equivalence table (narrativa) |
| 3 | Coexistencia hibrida | DOC | Webhooks + dual-run config (narrativa) |
| 6 | Extensions equivalentes | DOC | Container Steps catalog (narrativa) |

### Faltantes TEC promotables — Seguridad TI (4)

| # | Requisito | Promocion | Que mostrar |
|---|---|---|---|
| 4 | Retencion y eliminacion segura | UI | Entity Retention config + Audit Trail date filter |
| 14 | Ciclo de vida accesos (SCIM) | UI | SCIM Providers en Access Control |
| 15 | OAuth 2.0 / OIDC | UI | Authentication settings (SAML/OAuth) |
| 19 | Retencion logs 30+ dias | UI | Audit Trail → filtrar 6+ meses |

### Faltantes TEC promotables — Arquitectura TI (20)

> Ver detalle completo en `cobertura-arquitectura-ti.md` seccion "Faltantes de Demostrar"

| Esfuerzo | Cant | Items |
|---|---|---|
| Facil (UI, ~2 min) | 13 | 1.2, 2.2, 2.3, 2.5, 2.15, 2.17, 3.9, 3.16, 4.8, 4.10, 5.6, 5.10, 5.29 |
| Medio (micro-add) | 6 | 1.12, 2.8, 2.18, 3.2, 3.11, 3.15 |
| GAP a cerrar | 1 | 2.13 (Core Bancario) |

---

## Quick Wins para Subir Cobertura

| Accion | Tiempo | Requisitos que cubre | Matrices |
|---|---|---|---|
| Navegar Authentication settings | 2 min | Seg #15, Func Plat #13 | SegTI + Funcional |
| Navegar SCIM Providers | 2 min | Seg #14, ArqTI #2.15, #5.10, Func Plat #13, Repos #19 | Todas |
| Navegar Template Library | 2 min | Func CI #1,10,22,46 | Funcional |
| Navegar Audit Trail + date filter | 2 min | Seg #4,19, ArqTI #4.8 | SegTI + ArqTI |
| Navegar Entity Retention | 2 min | ArqTI #4.10 | ArqTI |
| Navegar apidocs.harness.io | 2 min | ArqTI #1.2, #2.5, #2.17 | ArqTI |
| Navegar IaCM module | 2 min | ArqTI #5.6, Func CI #65 | ArqTI + Funcional |
| Mostrar Harness Code screens | 10 min | Func Repos #1,5-12,18 | Funcional |
| Config Deployment Freeze | 5 min | Func CI #59 (ya UI) | Funcional |
| Reclasificar 2.18 Rate Limiting | 0 min | ArqTI #2.18 (ya en Act 7) | ArqTI |
| `kubectl get hpa` en Act 4 | 1 min | ArqTI #1.12 | ArqTI |

**Impacto total quick wins: ~30 min de prep cubre ~25 requisitos adicionales.**
