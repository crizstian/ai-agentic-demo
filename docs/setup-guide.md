# Setup Guide — SecOps AI Agentic Demo

Guia paso a paso para levantar el ambiente completo de la demo de 7 actos.
Cada fase tiene su checklist. Marcar `[x]` conforme se complete cada paso.

> **Branch**: `secops/ai-agentic-demo`
> **Proyecto Harness**: `sandbox` / `CristianRamirez`
> **Account**: `EeRjnXTnS4GrLG5VNNJZUw`

---

## Fase 0: Repositorio y Branch ✅

**Objetivo**: Tener el codigo fuente listo en el branch correcto.

- [x] Clonar el repo y cambiar al branch de la demo
  ```bash
  git clone https://github.com/luisredda/ai-agentic-demo.git
  cd ai-agentic-demo
  git checkout secops/ai-agentic-demo
  ```
- [x] Verificar estructura del monorepo
  ```bash
  ls app/ deploy/ docs/ iac/ policies/ scripts/ services/ tests/
  ```
- [x] Ejecutar tests para validar integridad
  ```bash
  pip install -r requirements.txt -r requirements-dev.txt
  python -m pytest tests/ -v
  # Resultado: 50 passed
  ```
- [ ] Hacer push del branch al remote
  ```bash
  git push -u origin secops/ai-agentic-demo
  ```

---

## Fase 1: Infraestructura — GKE Node Pool via IACM

**Objetivo**: Provisionar el node pool dedicado con taint para aislar workloads de la demo.

### 1.1 Verificar workspace IACM

- [x] Verificar que el workspace `ai_agentic_demo_nodepool` existe en Harness
  - URL: https://app.harness.io/ng/account/EeRjnXTnS4GrLG5VNNJZUw/module/iacm/orgs/sandbox/projects/CristianRamirez/workspaces/ai_agentic_demo_nodepool
  - Status: `inactive` (creado, pendiente de provision)

### 1.2 Tfvars

- [x] Tfvars disponible en el repo DemoBank: `iac/gke-nodepool/ai-agentic-demo.tfvars.json`
  - El workspace IACM apunta a `platform-gitops` para el tfvars (path: `Harness-Demo/Sandbox/iac/gcp-gke-nodepool/project/sales/se-sandbox/ai-agentic-demo.json`)
  - **Accion requerida**: sincronizar el tfvars de este repo al path de `platform-gitops` si el workspace lo requiere, o actualizar el workspace para apuntar a este repo directamente

### 1.3 Ejecutar pipeline IACM — Provision

Pipeline: [IACM - terraform-infra-workflow](https://app.harness.io/ng/account/EeRjnXTnS4GrLG5VNNJZUw/module/iacm/orgs/sandbox/projects/CristianRamirez/pipelines/IACMterraforminfraworkflow/pipeline-studio/?storeType=INLINE)

**Prompt para ejecutar via MCP o CLI:**

```
Ejecuta el pipeline IACMterraforminfraworkflow en org sandbox, project CristianRamirez con estos inputs:

- workspace (stage provision): ai_agentic_demo_nodepool
- backendType: gcs
- type: apply
```

**Via CLI:**
```bash
harness pipeline execute \
  --org sandbox \
  --project CristianRamirez \
  --pipeline IACMterraforminfraworkflow \
  --inputs '{
    "workspace": "ai_agentic_demo_nodepool",
    "backendType": "gcs",
    "type": "apply"
  }'
```

**Via Harness MCP (Claude Code / Cursor):**
```
Usa harness_execute para correr el pipeline IACMterraforminfraworkflow
en org=sandbox, project=CristianRamirez con action=run e inputs:
  - stage provision > workspace: ai_agentic_demo_nodepool
  - variable backendType: gcs
  - variable type: apply
```

- [ ] Pipeline ejecutado exitosamente (stage provision: plan aprobado)
- [ ] Budget check pasado (o approval en Jira completado)
- [ ] Stage apply completado — node pool creado

### 1.4 Verificar node pool en GKE

- [ ] Verificar node pool existe
  ```bash
  gcloud container node-pools list \
    --cluster=se-sandbox \
    --zone=us-east1-b \
    --project=sales-209522 \
    --filter="name=ai-agentic-demo-nodepool"
  ```
- [ ] Verificar taint activo
  ```bash
  kubectl get nodes -l scope=ai-agentic-demo -o json | \
    jq '.items[].spec.taints'
  # Esperado: [{"key":"dedicated","value":"ai_agentic_demo_space","effect":"NoSchedule"}]
  ```
- [ ] Verificar labels
  ```bash
  kubectl get nodes -l scope=ai-agentic-demo --show-labels
  # Esperado: owner=cristian-ramirez, scope=ai-agentic-demo, purpose=demobank-demo
  ```

---

## Fase 2: Kubernetes — Namespace y Servicios Base

**Objetivo**: Crear el namespace y los recursos base antes de que el pipeline de CD despliegue la app.

- [ ] Crear namespace
  ```bash
  kubectl apply -f deploy/k8s/base/namespace.yaml
  ```
- [ ] Aplicar configmap
  ```bash
  kubectl apply -f deploy/k8s/base/configmap.yaml
  ```
- [ ] Verificar namespace existe
  ```bash
  kubectl get ns harnessbank-demo
  ```

---

## Fase 3: Harness Platform — Servicios, Environments, Pipelines

**Objetivo**: Configurar los recursos de Harness necesarios para el pipeline de CD.

### 3.1 Connectors

| Connector | Tipo | Scope | Status | Uso |
|-----------|------|-------|--------|-----|
| `GCP_Sales_Admin` | GCP | Account | ✅ Existe | IACM provider, GCR push |
| `AdvisrDev` | GitHub | Project | ✅ Existe | Terraform modules repo |
| `CodeRepoCristianRamirez` | Git (Harness Code) | Project | ✅ Existe | Platform-gitops tfvars |
| `CristianConnector` | GitHub | Project | ✅ Existe | Source code repo |
| `sesandboxcrr` | K8s Cluster | Project | ✅ Existe | K8s deploy target |
| `DockerCristian` | Docker Registry | Project | ✅ Existe | Docker image push/pull |

- [ ] Verificar todos los connectors con status SUCCESS
  ```
  Prompt: "Lista los connectors del project CristianRamirez en org sandbox
  y muestra cuales tienen status FAILURE"
  ```

### 3.2 Service (Harness CD)

- [ ] Crear o verificar service `demobank` en Harness
  ```
  Prompt: "Verifica si existe un service llamado demobank en org sandbox,
  project CristianRamirez. Si no existe, crea uno de tipo Kubernetes
  con artifact source Docker usando el connector DockerCristian
  y el image path crizstian/harnessbank-demo"
  ```

### 3.3 Environment

- [ ] Crear o verificar environment `demo` tipo PreProduction
  ```
  Prompt: "Verifica si existe un environment llamado demo en org sandbox,
  project CristianRamirez. Si no existe, crea uno tipo PreProduction"
  ```

### 3.4 Infrastructure Definition

- [ ] Crear infra definition apuntando al cluster con namespace `harnessbank-demo`
  ```
  Prompt: "Crea una infrastructure definition llamada ai-agentic-demo-infra
  en environment demo, org sandbox, project CristianRamirez.
  Tipo: KubernetesDirect, connector: sesandboxcrr, namespace: harnessbank-demo"
  ```

### 3.5 Pipeline de CD

- [ ] Crear o verificar pipeline de deploy para DemoBank
  ```
  Prompt: "Verifica si existe un pipeline de deploy para el service demobank
  en project CristianRamirez. Si no, sugiere crear uno con:
  - Stage Canary: 20% → 50% → 100%
  - Continuous Verification con Prometheus (connector selatamprom)
  - Rollback automatico si CV falla"
  ```

---

## Fase 4: Traceable / API Security

**Objetivo**: Configurar la proteccion runtime (Acts 5-7).

- [ ] Obtener token de Traceable Platform
  - URL: https://app.traceable.ai → Settings → Agent Token
- [ ] Crear secret en Harness o K8s
  ```bash
  kubectl create secret generic traceable-config \
    --namespace=harnessbank-demo \
    --from-literal=reporting-endpoint=https://app.traceable.ai \
    --from-literal=api-token=<TU_TOKEN_TRACEABLE>
  ```
- [ ] Verificar el DaemonSet esta ready para deploy
  ```bash
  # El manifiesto ya tiene tolerations para el tainted node pool
  cat deploy/k8s/traceable/traceable-agent.yaml | grep -A4 tolerations
  ```
- [ ] Desplegar Traceable agent
  ```bash
  kubectl apply -f deploy/k8s/traceable/traceable-agent.yaml
  ```
- [ ] Verificar pods running en el nodo tainted
  ```bash
  kubectl get pods -n harnessbank-demo -l app=traceable-agent -o wide
  ```

---

## Fase 5: MCP Financial Data Service

**Objetivo**: Levantar el servicio MCP interno para trafico East-West (Act 5-6).

- [ ] Build de la imagen Docker
  ```bash
  cd services/mcp-financial-data
  docker build -t crizstian/mcp-financial-data:latest .
  docker push crizstian/mcp-financial-data:latest
  ```
- [ ] Deploy del service
  ```bash
  kubectl apply -f deploy/k8s/mcp-financial-data/deployment.yaml
  kubectl apply -f deploy/k8s/mcp-financial-data/service.yaml
  ```
- [ ] Verificar service running
  ```bash
  kubectl get pods -n harnessbank-demo -l app=mcp-financial-data
  kubectl exec -n harnessbank-demo deploy/mcp-financial-data -- curl -s localhost:5001/health
  # Esperado: {"status": "healthy"}
  ```

---

## Fase 6: Apigee API Management

**Objetivo**: Configurar el API proxy para la demo de API discovery y API management (Act 7).

- [ ] Verificar acceso a Apigee console
  - URL: https://apigee.google.com
  - Project: `sales-209522`
- [ ] Importar API proxy spec
  ```bash
  cat deploy/apigee/apiproxy-spec.yaml
  ```
- [ ] Crear API proxy en Apigee apuntando al ingress de DemoBank
- [ ] Configurar OAuth2 policy en el proxy
- [ ] Verificar proxy desplegado y ruteo correcto

---

## Fase 7: Ingress y Network

**Objetivo**: Exponer DemoBank al exterior con NGINX Ingress.

- [ ] Instalar NGINX Ingress Controller (si no existe)
  ```bash
  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
  helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx --create-namespace \
    --set controller.nodeSelector.scope=ai-agentic-demo \
    --set controller.tolerations[0].key=dedicated \
    --set controller.tolerations[0].value=ai_agentic_demo_space \
    --set controller.tolerations[0].effect=NoSchedule
  ```
- [ ] Aplicar Ingress resource
  ```bash
  kubectl apply -f deploy/k8s/ingress/ingress.yaml
  ```
- [ ] Obtener IP externa
  ```bash
  kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
  ```
- [ ] Configurar DNS (opcional) o usar IP directa
- [ ] Verificar acceso externo
  ```bash
  curl -s http://<EXTERNAL_IP>/health
  # Esperado: {"status": "ok"}
  ```

---

## Fase 8: OPA Policies en Harness

**Objetivo**: Cargar las OPA policies en Harness Governance para los gates del pipeline.

### Policies a crear

| Policy | Archivo | Pipeline Gate | Act |
|--------|---------|---------------|-----|
| No Critical Findings | `policies/no-critical-findings.rego` | Post-SAST/SCA scan | 3 |
| SLSA Attestation Required | `policies/slsa-attestation-required.rego` | Pre-deploy | 4 |
| Security Scan Required | `policies/security-scan-required.rego` | Pre-deploy | 4 |
| Block Unprotected AI Endpoints | `policies/block-unprotected-ai-endpoints.rego` | Post-AI-scan | 6 |

- [ ] Crear cada policy en Harness
  ```
  Prompt: "Crea 4 OPA policies en org sandbox, project CristianRamirez
  con el contenido de los archivos en policies/. Los nombres son:
  1. no-critical-findings (tipo: pipeline, accion: warn)
  2. slsa-attestation-required (tipo: pipeline, accion: error)
  3. security-scan-required (tipo: pipeline, accion: error)
  4. block-unprotected-ai-endpoints (tipo: pipeline, accion: warn)"
  ```
- [ ] Crear policy set agrupando las 4 policies
  ```
  Prompt: "Crea un policy set llamado secops-demo-gates en org sandbox,
  project CristianRamirez que agrupe las 4 policies creadas arriba.
  Entity type: pipeline, action: onstep"
  ```

---

## Fase 9: Semgrep / SAST Config

**Objetivo**: Verificar que la configuracion de Semgrep detecta las vulnerabilidades intencionadas.

- [ ] Validar reglas Semgrep localmente
  ```bash
  semgrep --config .semgrep.yml app/ --json 2>/dev/null | \
    python3 -c "import json,sys; r=json.load(sys.stdin); print(f'{len(r.get(\"results\",[]))} findings')"
  # Esperado: 7 findings (SAST-detectable vulns)
  ```
- [ ] Verificar que las 3 vulns AI-specific NO aparecen en Semgrep
  ```
  VULN-008 (prompt injection) — no detectable por SAST
  VULN-009 (PII leak via AI)  — no detectable por SAST
  VULN-010 (BOLA/IDOR)        — no detectable por SAST (requiere runtime)
  ```

---

## Fase 10: Demo Reset y Validacion Final

**Objetivo**: Ejecutar el script de reset, validar que todo funciona end-to-end.

### 10.1 Demo Reset

- [ ] Ejecutar reset script
  ```bash
  chmod +x scripts/demo-reset.sh
  ./scripts/demo-reset.sh
  ```

### 10.2 Validacion App

- [ ] App responde en `/health`
- [ ] Dashboard carga en `/`
- [ ] API accounts responde en `/api/accounts/`
- [ ] AI chatbox responde en `/api/ai/chat`
- [ ] MCP financial data responde (E-W) desde dentro del cluster

### 10.3 Validacion Attack Chain

- [ ] Ejecutar attack chain en modo dry-run
  ```bash
  chmod +x scripts/attack-chain.sh
  bash scripts/attack-chain.sh --target http://<EXTERNAL_IP>
  ```
- [ ] Verificar que los 5 pasos del ataque son exitosos contra la app sin proteccion

### 10.4 Validacion Traceable

- [ ] Traceable detecta las APIs en el API Catalog
- [ ] Traffic flow visible entre DemoBank ↔ MCP Financial Data
- [ ] Behavioral baseline establecido (requiere ~5 min de trafico normal)

---

## Prompt Cards para Agentes AI

Prompts listos para usar durante la demo con Claude Code, Cursor, o cualquier AI coding agent.

### Act 1 — Inner Loop (AI Coding Agent)

```
Analiza el codebase de DemoBank (app/) y agrega una nueva feature:
un endpoint POST /api/ai/chat que conecte con un servicio MCP interno
en localhost:5001 para consultar datos financieros del cliente.
El endpoint debe aceptar {message, session_id} y responder con
{response, context_used, model}.
```

### Act 2 — Software Delivery Agent (PR Validation)

```
Crea un PR del branch secops/ai-agentic-demo hacia main.
El PR debe incluir un resumen de todos los cambios y un test plan.
Usa el Software Delivery Agent para validar el PR:
analizar los cambios, identificar riesgos, y generar recomendaciones.
```

### Act 3 — Security Testing Agent (SAST + SCA)

```
Ejecuta un security scan del codebase usando Semgrep con la config
.semgrep.yml. Analiza los resultados, prioriza los findings por
severidad, y genera un plan de remediacion automatizado.
¿Cuantas vulnerabilidades detecta? ¿Cuales son las criticas?
```

### Act 4 — Deploy Gobernado (IACM + Pipeline)

```
Ejecuta el pipeline IACMterraforminfraworkflow en org sandbox,
project CristianRamirez con:
- workspace: ai_agentic_demo_nodepool
- backendType: gcs
- type: apply

Despues verifica el status del node pool y confirma que el taint
dedicated=ai_agentic_demo_space:NoSchedule esta activo.
```

### Act 5 — El Ataque (Shield Right)

```
Ejecuta el attack chain script (scripts/attack-chain.sh) contra
la app DemoBank desplegada en http://<TARGET_URL>.
Documenta cada paso del ataque y que vulnerabilidad explota:
1. Prompt injection
2. PII exfiltration via AI
3. BOLA/IDOR
4. SQL injection
5. Command injection
```

### Act 6 — Shield Right + Shift Left

```
Analiza los findings de Traceable despues del ataque.
El runtime detection agent deberia haber detectado:
- Prompt injection attempts
- Unusual API call patterns (BOLA)
- PII in API responses
Genera un SBOM (CycloneDX) y un reporte de remediacion
usando el Security Testing Agent.
```

### Act 7 — AI Security (3-Layer Model)

```
Demuestra el modelo de 3 capas de AI Security:
1. API Discovery: ¿que endpoints AI existen? (/api/ai/chat, /api/ai/status)
2. AI Security Posture: ¿el AIBOM (docs/samples/aibom-demobank.json)
   refleja todos los componentes AI?
3. Runtime Protection: ¿Traceable detecta y bloquea prompt injection
   en tiempo real?
```

---

## Quick Reference

### URLs

| Recurso | URL |
|---------|-----|
| Harness Project | https://app.harness.io/ng/account/EeRjnXTnS4GrLG5VNNJZUw/all/orgs/sandbox/projects/CristianRamirez |
| IACM Workspace | https://app.harness.io/ng/account/EeRjnXTnS4GrLG5VNNJZUw/module/iacm/orgs/sandbox/projects/CristianRamirez/workspaces/ai_agentic_demo_nodepool |
| IACM Pipeline | https://app.harness.io/ng/account/EeRjnXTnS4GrLG5VNNJZUw/module/iacm/orgs/sandbox/projects/CristianRamirez/pipelines/IACMterraforminfraworkflow |
| GitHub Repo | https://github.com/luisredda/ai-agentic-demo |
| Traceable | https://app.traceable.ai |

### GCP

| Parametro | Valor |
|-----------|-------|
| Project | `sales-209522` |
| Cluster | `se-sandbox` |
| Zone | `us-east1-b` |
| Node Pool | `ai-agentic-demo-nodepool` |
| Machine Type | `e2-standard-4` |
| Service Account | `sales-demo-admin@sales-209522.iam.gserviceaccount.com` |

### Taint / Toleration

```yaml
# Node taint (GKE)
key: dedicated
value: ai_agentic_demo_space
effect: NoSchedule

# Pod toleration (en todos los deploy/k8s/**/deployment.yaml)
tolerations:
  - key: dedicated
    operator: Equal
    value: ai_agentic_demo_space
    effect: NoSchedule

# Node selector
nodeSelector:
  scope: ai-agentic-demo
```

### Documentacion de la demo

| Documento | Path |
|-----------|------|
| Demo Script (7 acts) | `docs/ai-demo-script.md` |
| Demo Storyline | `docs/ai-demo-storyline.md` |
| Demo Inventory | `docs/demo-inventory.md` |
| Architecture Diagrams | `docs/architecture-diagrams.md` |
| Infrastructure Requirements | `docs/infrastructure-requirements.md` |
| Prompt Cards | `docs/prompt-cards.md` |
| Act Details | `docs/acts/act-{1-7}-*.md` |
| AIBOM Sample | `docs/samples/aibom-demobank.json` |
| SLSA Provenance | `docs/samples/slsa-provenance.json` |

### Cleanup (destruir infra al terminar)

```
Prompt: "Ejecuta el pipeline IACMterraforminfraworkflow con:
- workspace: ai_agentic_demo_nodepool
- backendType: gcs
- type: destroy"
```

```bash
kubectl delete ns harnessbank-demo
```
