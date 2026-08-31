# Arquitectura e Infraestructura — Checklist de Setup

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          HARNESS PLATFORM (SaaS)                               │
│                     Account: EeRjnXTnS4GrLG5VNNJZUw                           │
│                     Org: sandbox | Project: CristianRamirez                    │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                          CONNECTORS                                       │ │
│  │                                                                           │ │
│  │  [account] GCP_Sales_Admin ───── GCP provider (IACM, GCR)          ✅   │ │
│  │  [org]     Cristian_GH ───────── GitHub public (luisredda repos)   ✅   │ │
│  │  [project] AdvisrDev ──────────  GitHub (terraform modules)        ✅   │ │
│  │  [project] sesandboxcrr ───────  K8s cluster (delegate)            ✅   │ │
│  │  [project] DockerCristian ─────  Docker Registry (push/pull)       ✅   │ │
│  │  [project] selatamprom ────────  Prometheus (CV metrics)           ⏳   │ │
│  │  [project] CodeRepoCristianRamirez ── Harness Code Repo            ✅   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────┐                                                         │
│  │       IACM        │  ◄── FASE 1: Infraestructura                            │
│  │                   │                                                         │
│  │  Workspace:       │                                                         │
│  │  ai_agentic_demo  │                                                         │
│  │  _nodepool    ✅  │                                                         │
│  │                   │                                                         │
│  │  Pipeline:        │                                                         │
│  │  IACMterraform    │                                                         │
│  │  infraworkflow ✅ │                                                         │
│  │                   │                                                         │
│  │  TF Module:       │                                                         │
│  │  terraform-gcp-   │                                                         │
│  │  gke (AdvisrDev)  │                                                         │
│  │  v0.1.4.1     ✅  │                                                         │
│  │                   │                                                         │
│  │  Tfvars:          │                                                         │
│  │  iac/gke-nodepool/│                                                         │
│  │  ai-agentic-demo  │                                                         │
│  │  .tfvars.json ✅  │                                                         │
│  └─────────┬─────────┘                                                         │
│            │ provision                                                          │
│            ▼                                                                    │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐          │
│  │    CD / SDA       │  │    STO / STA      │  │    Governance     │          │
│  │                   │  │                   │  │                   │          │
│  │  Service:         │  │  SAST: Semgrep    │  │  OPA Policy Set:  │          │
│  │  demobank     ✅  │  │              ✅  │  │  secops_demo      │          │
│  │                   │  │                   │  │  _gates       ✅  │          │
│  │  Environment:     │  │  SCA:             │  │                   │          │
│  │  gke_latam    ✅  │  │  OWASP SCA    ✅  │  │  4 policies:      │          │
│  │                   │  │                   │  │  - no-crit    ✅  │          │
│  │  Infra Def:       │  │  SCS:             │  │  - slsa-req   ✅  │          │
│  │  latam_       ✅  │  │  SBOM/SLSA    ✅  │  │  - scan-req   ✅  │          │
│  │  nodepool         │  │  (keyless cosign) │  │  - ai-block   ✅  │          │
│  │                   │  │  AI Security:     │  │                   │          │
│  │  Pipeline:        │  │  Traceable    ⏳  │  │                   │          │
│  │  AI_SDLC_     ✅  │  │                   │  │  Triggers:        │          │
│  │  DemoBank         │  │                   │  │  PR + Push    ✅  │          │
│  └────────┬──────────┘  └───────────────────┘  └───────────────────┘          │
│           │ deploy                                                              │
│           │            ◄── FASE 2: Plataforma (despues de infra completa)       │
└───────────┼─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       GCP Project: sales-209522                                │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                GKE Cluster: se-sandbox (us-east1-b)  ✅                   │ │
│  │                K8s version: 1.31.x                                        │ │
│  │                                                                           │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │       Node Pool: ai-agentic-demo-nodepool  ⏳ (pipeline running)    │ │ │
│  │  │       Machine: e2-standard-4 | Autoscaling: 1-2 nodes              │ │ │
│  │  │       Taint: dedicated=ai_agentic_demo_space:NoSchedule             │ │ │
│  │  │       Labels: scope=ai-agentic-demo, owner=cristian-ramirez         │ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌───────────────────────────────────────────────────────────────┐ │ │ │
│  │  │  │        Namespace: harnessbank-demo  ⏳                        │ │ │ │
│  │  │  │                                                               │ │ │ │
│  │  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │ │ │ │
│  │  │  │  │  DemoBank    │ │ MCP Finance  │ │  Traceable Agent     │ │ │ │ │
│  │  │  │  │  (Deploy) ⏳ │ │ (Deploy) ⏳  │ │  (DaemonSet) ⏳     │ │ │ │ │
│  │  │  │  │              │ │              │ │                      │ │ │ │ │
│  │  │  │  │  Port: 3000  │ │  Port: 5001  │ │  NET_RAW/ADMIN      │ │ │ │ │
│  │  │  │  │  Flask+SQLite│ │  Flask mock  │ │  eBPF capture        │ │ │ │ │
│  │  │  │  │  10 vulns    │ │  E-W traffic │ │  AI Security         │ │ │ │ │
│  │  │  │  │              │ │  ClusterIP   │ │                      │ │ │ │ │
│  │  │  │  └──────┬───────┘ └──────┬───────┘ └──────────┬───────────┘ │ │ │ │
│  │  │  │         │                │                     │             │ │ │ │
│  │  │  │         │     E-W ◄──────┘       monitors ◄────┘             │ │ │ │
│  │  │  │         │                                                    │ │ │ │
│  │  │  │  ┌──────┴─────────────────────────────────────────────────┐ │ │ │ │
│  │  │  │  │            NGINX Ingress  ✅  (ns: nginx, shared pool) │ │ │ │ │
│  │  │  │  │       External IP 35.227.123.79 → :80 → :3000         │ │ │ │ │
│  │  │  │  └────────────────────────────────────────────────────────┘ │ │ │ │
│  │  │  └───────────────────────────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                           │ │
│  │  (otros node pools: se-latam-nodepool, etc.)                              │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  GCS Bucket: crizstian-terraform (IACM state backend)  ✅                      │
│  GCR/Docker: crizstian/harnessbank-demo  ⏳                                    │
│  GCR/Docker: crizstian/mcp-financial-data  ⏳                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            REPOSITORIOS                                         │
│                                                                                 │
│  GitHub (luisredda) — via org.Cristian_GH                                       │
│  └── ai-agentic-demo [branch: secops/ai-agentic-demo]  ✅                     │
│      ├── app/                    ← Codigo DemoBank (Flask + 10 vulns)    ✅    │
│      ├── services/mcp-financial-data/ ← MCP service mock                 ✅    │
│      ├── deploy/k8s/             ← Manifiestos K8s (con tolerations)     ✅    │
│      ├── deploy/apigee/          ← API proxy spec                        ✅    │
│      ├── iac/gke-nodepool/       ← Tfvars + workspace.tf                 ✅    │
│      ├── policies/               ← 4 OPA policies                       ✅    │
│      ├── tests/                  ← 50 tests                             ✅    │
│      ├── scripts/                ← attack-chain.sh, demo-reset.sh        ✅    │
│      └── docs/                   ← 7 acts, diagrams, inventory           ✅    │
│                                                                                 │
│  GitHub (crizstian) — via AdvisrDev connector                                   │
│  └── terraform-gcp-gke [tag: v0.1.4.1]  ✅                                    │
│      └── templates/node-pool-only/ ← Terraform module (.tf files)              │
│                                                                                 │
│  Traceable (SaaS)                                                               │
│  └── app.traceable.ai  ⏳           ← Runtime protection dashboard             │
│                                                                                 │
│  Apigee (GCP)                                                                   │
│  └── sales-209522  ⏳               ← API management                           │
└─────────────────────────────────────────────────────────────────────────────────┘

Leyenda:  ✅ Completado  |  ⏳ Pendiente  |  ❌ Bloqueado
```

---

## Checklist por Fases

### FASE 1: Infraestructura (en progreso)

**Objetivo**: Node pool provisionado, cluster listo para recibir workloads.

#### Repositorio

- [x] Repo `luisredda/ai-agentic-demo` — branch `secops/ai-agentic-demo` pusheado
- [x] Codigo DemoBank con 10 vulnerabilidades (7 SAST + 3 AI-specific)
- [x] MCP Financial Data service (`services/mcp-financial-data/`)
- [x] 50 tests passing
- [x] Manifiestos K8s con tolerations/nodeSelector
- [x] Tfvars (`iac/gke-nodepool/ai-agentic-demo.tfvars.json`)

#### Connectors

| Connector | Scope | Tipo | Status |
|-----------|-------|------|--------|
| `GCP_Sales_Admin` | Account | GCP | ✅ |
| `Cristian_GH` | Org | GitHub | ✅ |
| `AdvisrDev` | Project | GitHub | ✅ |
| `selatam` | Project | K8s Cluster | ✅ |
| `DockerCristian` | Project | Docker Registry | ✅ |
| `CodeRepoCristianRamirez` | Project | Harness Code | ✅ |
| `traceableai_helm_repo` | Project | Helm Repo | ⏳ As-code (`.harness/connectors/`) |
| `selatamprom` | Project | Prometheus | ⏳ Pendiente |

#### IACM

- [x] Workspace `ai_agentic_demo_nodepool` creado
- [x] Module repo: `terraform-gcp-gke` tag `v0.1.4.1` path `templates/node-pool-only`
- [x] Provider connector: `account.GCP_Sales_Admin`
- [x] Tfvars en repo DemoBank: `iac/gke-nodepool/ai-agentic-demo.tfvars.json`
- [ ] Workspace `terraform_variable_files` → apuntar a `ai-agentic-demo` via `org.Cristian_GH`
- [x] Env vars: GOOGLE_PROJECT, GOOGLE_REGION, backend GCS
- [x] Pipeline `IACMterraforminfraworkflow` ejecutado (run #90)
- [ ] Pipeline IACM completado exitosamente
- [ ] Node pool `ai-agentic-demo-nodepool` activo en GKE

#### GKE / Kubernetes

- [x] Cluster `se-sandbox` existe (`sales-209522`, `us-east1-b`)
- [ ] Node pool activo con taint `dedicated=ai_agentic_demo_space:NoSchedule`
- [ ] Labels: `scope=ai-agentic-demo`, `owner=cristian-ramirez`
- [ ] Namespace `harnessbank-demo` creado
- [ ] ConfigMap aplicado

#### Networking

- [x] NGINX Ingress Controller operativo (ns: `nginx`, shared pool `se-sandbox-pool-01`, v1.10.1)
- [x] External IP: `35.227.123.79` (LoadBalancer, ports 80/443)
- [ ] Ingress resource aplicado (manifest `deploy/k8s/ingress/ingress.yaml`)
- [ ] DNS configurado (opcional)

#### Docker Images

- [ ] `crizstian/harnessbank-demo:latest` — build y push
- [ ] `crizstian/mcp-financial-data:latest` — build y push

#### Harness As-Code (`.harness/`)

- [x] Environment `gke-latam` (PreProduction) — `.harness/environments/demo.yaml`
- [x] Infra `latam-nodepool` (Kubernetes, ns: harnessbank-demo) — `.harness/infrastructure/latam-nodepool.yaml`
- [x] Infra `latam-nodepool-helm` (NativeHelm, ns: `<+input>`) — `.harness/infrastructure/latam-nodepool-helm.yaml`
- [x] Connector `traceableai_helm_repo` (HttpHelmRepo) — `.harness/connectors/traceableai-helm-repo.yaml`
- [x] Service `demobank` (Kubernetes) — `.harness/services/demobank.yaml`
- [x] Service `mcp-financial-data` (Kubernetes) — `.harness/services/mcp-financial-data.yaml`
- [x] Service `traceable-agent` (NativeHelm) — `.harness/services/traceable-agent.yaml`
- [x] Service `traceable-ebpf-tracer` (NativeHelm) — `.harness/services/traceable-ebpf-tracer.yaml`
- [x] Service `traceable-ast-runner` (NativeHelm) — `.harness/services/traceable-ast-runner.yaml`

#### Workloads K8s (deploy via pipeline CDSimpleKubernetesDeployment)

- [ ] DemoBank Deployment + Service (port 3000)
- [ ] MCP Financial Data Deployment + Service (port 5001, ClusterIP)
- [ ] Traceable TPA (Helm, ns: traceableai)
- [ ] Traceable eBPF Tracer (Helm, ns: traceableai)
- [ ] Traceable AST Runner (Helm, ns: traceableai)

---

### FASE 2: Plataforma Harness (despues de infra completa)

**Objetivo**: Pipelines de CI/CD, security scanning, y governance configurados.

#### Harness CD / Software Delivery Agent

- [x] Service `demobank` (K8s, artifact Docker via `DockerCristian`) — as-code
- [x] Service `mcp-financial-data` (K8s, artifact Docker via `DockerCristian`) — as-code
- [x] Environment `gke-latam` (PreProduction) — as-code
- [x] Infra `latam-nodepool` (K8s Direct, connector `selatam`, ns `harnessbank-demo`) — as-code
- [x] Infra `latam-nodepool-helm` (NativeHelm, connector `selatam`, ns runtime) — as-code
- [x] Pipeline `AI_SDLC_DemoBank` synced a Harness (INLINE) — CI + Deploy DemoBank + Deploy MCP
- [x] Triggers: PR Validation (Open/Reopen/Sync → main) + Main Branch Build and Deploy (push → main)
- [x] Canary count: 2 (ephemeral pods, not percentage)
- [ ] Recursos as-code creados en Harness (services, env, infra — push YAML)

#### Harness STO / Security Testing Agent

- [x] Semgrep config (`.semgrep.yml`) — 7 SAST findings esperados
- [x] SAST step en pipeline (Semgrep orchestration)
- [x] Secrets Detection step en pipeline (Gitleaks)
- [x] SCA step en pipeline (OWASP Dependency Check)
- [x] SCS steps: 2 SBOM (cdxgen, CycloneDX) + keyless cosign attestation (Harness OIDC)

#### Harness Governance (OPA)

- [x] Policy files en repo (`.harness/policies/` — 4 .rego files)
- [x] Policy `no_critical_findings` creada en Harness (severity: error)
- [x] Policy `slsa_attestation_required` creada en Harness (severity: error)
- [x] Policy `security_scan_required` creada en Harness (severity: error)
- [x] Policy `block_unprotected_ai_endpoints` creada en Harness (severity: warning)
- [x] Policy Set `secops_demo_gates` — 4 policies, type: pipeline, action: onrun, enabled

#### Traceable / API Security

- [x] Services as-code: TPA, eBPF tracer, AST Runner (NativeHelm)
- [x] Connector `traceableai_helm_repo` as-code
- [ ] Token Agent de Traceable obtenido (app.traceable.ai > Administration)
- [ ] Token Platform de Traceable obtenido (para AST Runner)
- [ ] Secrets creados en Harness
- [ ] Deploy via pipeline (ns: traceableai)
- [ ] APIs descubiertas en Traceable dashboard
- [ ] Behavioral baseline establecido (~5 min trafico)

#### Apigee / API Management

- [ ] API proxy configurado (project `sales-209522`)
- [ ] OAuth2 policy en proxy
- [ ] Ruteo correcto al ingress de DemoBank

---

### FASE 3: Validacion End-to-End (despues de plataforma completa)

**Objetivo**: Todo funciona, demo lista para ejecutar.

- [ ] `/health` responde 200
- [ ] Dashboard carga en `/`
- [ ] `/api/accounts/` responde con data
- [ ] `/api/ai/chat` responde
- [ ] MCP E-W traffic funciona (DemoBank → mcp-financial-data:5001)
- [ ] Attack chain (`scripts/attack-chain.sh`) ejecuta los 5 pasos
- [ ] Traceable detecta APIs y trafico
- [ ] Pipeline CI/CD ejecuta scan + deploy + CV
- [ ] OPA policies evaluan correctamente
- [ ] Demo reset script (`scripts/demo-reset.sh`) funciona
