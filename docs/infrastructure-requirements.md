# Infraestructura Completa — DemoBank Demo

Complete infrastructure inventory for the full 7-Act DemoBank demo. Every component listed here is required for the complete experience. No minimal configurations, no fallbacks.

---

## 1. Kubernetes Cluster

**What:** GKE cluster hosting all demo workloads — DemoBank app, MCP Financial Data service, and Traceable runtime agent.

**Why needed:** Acts 4-7 require a live cluster for canary deploys, Continuous Verification, WAAP runtime detection, and AI Security discovery. Acts 1-3 use the cluster as the deployment target for the pipeline.

**Acts:** All (1-7). Acts 1-3 deploy to it. Acts 4-7 run live on it.

### Exact Config

| Parameter | Value |
|-----------|-------|
| Provider | GKE (Google Kubernetes Engine) |
| Nodes | 3x `e2-standard-4` (4 vCPU, 16 GB each) |
| Region | `us-central1` (or nearest to demo audience) |
| K8s version | 1.28+ (stable channel) |
| Namespace | `harnessbank-demo` |
| Addons | NGINX Ingress Controller, Workload Identity |
| Network policy | Calico (for E-W visibility) |

### Workloads (3 total)

| Workload | Kind | Port | Service Type | Resources |
|----------|------|------|-------------|-----------|
| `harnessbank-demo` (DemoBank) | Deployment | 3000 | LoadBalancer (80->3000) | 100m-500m CPU, 128Mi-256Mi mem |
| `mcp-financial-data` | Deployment | 5001 | ClusterIP (5001, internal only) | 50m-200m CPU, 64Mi-128Mi mem |
| `traceable-agent` | DaemonSet | N/A | N/A (host-network sniffer) | 100m-500m CPU, 128Mi-256Mi mem |

### Total cluster resource budget

| Resource | Requests (min) | Limits (max) |
|----------|---------------|-------------|
| CPU | 250m per node (750m total) | 1200m per node (3600m total) |
| Memory | 320Mi per node (960Mi total) | 640Mi per node (1920Mi total) |

### Setup Commands

```bash
# Create cluster
gcloud container clusters create demobank-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-4 \
  --enable-ip-alias \
  --release-channel stable

# Get credentials
gcloud container clusters get-credentials demobank-cluster \
  --zone us-central1-a

# Create namespace
kubectl apply -f deploy/k8s/base/namespace.yaml

# Apply ConfigMap
kubectl apply -f deploy/k8s/base/configmap.yaml

# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml

# Deploy all workloads (after images are pushed — see Section 2)
kubectl apply -f deploy/k8s/demobank/deployment.yaml
kubectl apply -f deploy/k8s/demobank/service.yaml
kubectl apply -f deploy/k8s/mcp-financial-data/deployment.yaml
kubectl apply -f deploy/k8s/mcp-financial-data/service.yaml
kubectl apply -f deploy/k8s/ingress/ingress.yaml
kubectl apply -f deploy/k8s/traceable/traceable-agent.yaml
```

### Manifest Files

| File | Resource | Notes |
|------|----------|-------|
| `deploy/k8s/base/namespace.yaml` | Namespace `harnessbank-demo` | Apply first |
| `deploy/k8s/base/configmap.yaml` | ConfigMap `harnessbank-demo-config` | PORT=3000, NODE_ENV=demo, APP_NAME="DemoBank AI SDLC" |
| `deploy/k8s/demobank/deployment.yaml` | Deployment `harnessbank-demo` | Helm-template with `{{ .Values.* }}`, image from `<+artifact.image>` |
| `deploy/k8s/demobank/service.yaml` | Service `harnessbank-demo` | LoadBalancer, port 80->3000 |
| `deploy/k8s/demobank/values.yaml` | Helm values | replicas=1, healthCheckPath=/health (set /healthz for Manifest Remediator demo) |
| `deploy/k8s/mcp-financial-data/deployment.yaml` | Deployment `mcp-financial-data` | Labels: `tier: internal`, `component: mcp-tool` |
| `deploy/k8s/mcp-financial-data/service.yaml` | Service `mcp-financial-data` | ClusterIP (not exposed externally) |
| `deploy/k8s/ingress/ingress.yaml` | Ingress `demobank-ingress` | Host `demobank.app`, paths: /api/accounts, /api/ai, /api/admin, / |
| `deploy/k8s/traceable/traceable-agent.yaml` | DaemonSet `traceable-agent` + Secret `traceable-config` | NET_RAW + NET_ADMIN capabilities |

---

## 2. Container Registry

**What:** Container registry holding the two Docker images built from this repo.

**Why needed:** Harness CD pulls images from the registry during deployment. The pipeline builds, tags, pushes, and then references `<+artifact.image>` in the K8s manifests.

**Acts:** 3 (build artifact + SBOM), 4 (deploy from registry), all subsequent acts run the deployed images.

### Exact Config

| Parameter | Value |
|-----------|-------|
| Provider | Google Artifact Registry (GAR) recommended. Docker Hub or ECR also supported |
| Repository | `demobank` (Docker format) |
| Region | Same as GKE cluster (`us-central1`) |
| Authentication | Workload Identity (GKE) or service account key |

### Images (2 total)

| Image | Dockerfile | Base | Port | Tag convention |
|-------|-----------|------|------|---------------|
| `demobank` | `./Dockerfile` | `python:3.12-slim` | 3000 | `<registry>/demobank:<git-sha>` |
| `mcp-financial-data` | `./services/mcp-financial-data/Dockerfile` | `python:3.12-slim` | 5001 | `<registry>/mcp-financial-data:<git-sha>` |

### Setup Commands

```bash
# Create GAR repository
gcloud artifacts repositories create demobank \
  --repository-format=docker \
  --location=us-central1 \
  --description="DemoBank demo images"

# Authenticate Docker to GAR
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push DemoBank image
docker build -t us-central1-docker.pkg.dev/<PROJECT>/demobank/demobank:latest .
docker push us-central1-docker.pkg.dev/<PROJECT>/demobank/demobank:latest

# Build and push MCP Financial Data image
docker build -t us-central1-docker.pkg.dev/<PROJECT>/demobank/mcp-financial-data:latest \
  -f services/mcp-financial-data/Dockerfile services/mcp-financial-data/
docker push us-central1-docker.pkg.dev/<PROJECT>/demobank/mcp-financial-data:latest
```

### Harness Connector

| Field | Value |
|-------|-------|
| Type | Docker Registry / Google Artifact Registry |
| Provider | `us-central1-docker.pkg.dev/<PROJECT>/demobank` |
| Auth | GCP Service Account or Workload Identity |
| Delegate | Harness delegate in same GKE cluster |

---

## 3. API Gateway (Apigee)

**What:** Apigee X API gateway sitting in front of DemoBank to demonstrate the "API Manager blind spot" narrative (CISO Objection #4).

**Why needed:** Act 5 demonstrates that Apigee only protects registered endpoints. Unregistered endpoints (zombie APIs, new endpoints added post-launch) bypass the gateway entirely. This is the core argument for why WAAP is needed alongside a traditional API Manager.

**Acts:** 5 (attack chain exploits unregistered endpoints), 7 (AI Security discovery finds what Apigee missed).

### Registered Endpoints (4 -- protected by Apigee policies)

| Endpoint | Methods | Policies | Notes |
|----------|---------|----------|-------|
| `/api/accounts` | GET | `apikey-verify`, `rate-limit-100`, `response-cache-60s` | Account CRUD |
| `/api/accounts/{id}` | GET | `apikey-verify`, `rate-limit-100` | Single account |
| `/api/ai/chat` | POST | `apikey-verify`, `rate-limit-30`, `request-size-limit-10kb` | AI chat -- has auth but NO content inspection |
| `/api/admin/ping` | GET | `apikey-verify`, `ip-whitelist` (10.0.0.0/8, 172.16.0.0/12), `rate-limit-10` | Admin health |
| `/api/fx` | GET | `rate-limit-500` | Public rates, no auth |

### Unregistered Endpoints (2 -- BLIND SPOTS, the demo's point)

| Endpoint | Why unregistered | Attack impact |
|----------|-----------------|---------------|
| `/api/ai/status` | Zombie API -- debug endpoint the dev forgot to remove | Act 5 Step 1: attacker discovers model name + MCP URLs |
| `/api/accounts/{id}/details` | Added post-launch, never registered in gateway | Act 5 Step 3: BOLA/IDOR with no rate limiting |

### Apigee Policies Defined

| Policy | Type | Config |
|--------|------|--------|
| `apikey-verify` | VerifyAPIKey | Source: `request.header.x-api-key` |
| `rate-limit-100` | SpikeArrest | 100 requests/minute |
| `rate-limit-30` | SpikeArrest | 30 requests/minute |
| `rate-limit-10` | SpikeArrest | 10 requests/minute |
| `rate-limit-500` | SpikeArrest | 500 requests/minute |
| `ip-whitelist` | AccessControl | Allow: 10.0.0.0/8, 172.16.0.0/12 |
| `request-size-limit-10kb` | AssignMessage | maxPayloadSize: 10240 |

### Exact Config

| Parameter | Value |
|-----------|-------|
| Provider | Apigee X on GCP (preferred) |
| Alternative | Kong Gateway or AWS API Gateway with equivalent policies |
| Proxy name | `demobank-api` |
| Base path | `/api` |
| Target | `http://harnessbank-demo.harnessbank-demo.svc.cluster.local:80` |
| Spec file | `deploy/apigee/apiproxy-spec.yaml` |

### Setup Commands

```bash
# Option A: Apigee X (GCP)
gcloud apigee organizations provision --project=<PROJECT>
gcloud apigee apis create --body-file=deploy/apigee/apiproxy-spec.yaml
gcloud apigee apis deploy --api=demobank-api --environment=demo

# Option B: Kong Gateway (alternative)
helm repo add kong https://charts.konghq.com
helm install kong kong/kong --namespace kong --create-namespace
# Configure routes matching the apiproxy-spec.yaml endpoints and policies
```

### What Apigee does NOT cover (demo talking points)

| Capability | Apigee | WAAP (Traceable) |
|-----------|--------|------------------|
| Registered endpoints | Protects | Protects |
| Unregistered/zombie endpoints | Does not see | Auto-discovers |
| N-S traffic (ingress) | Inspects | Inspects |
| E-W traffic (service-to-service) | Does not see | Captures via TPA DaemonSet |
| Semantic content (prompt injection) | Does not parse | AI content inspection |
| Session correlation (7 days) | Request-level only | Session stitching |
| Rate limiting | Per-endpoint | Behavioral + per-actor |

---

## 4. WAAP (Traceable)

**What:** Traceable Platform Agent (TPA) deployed as a DaemonSet. Provides runtime API protection -- API Discovery, Behavioral Detection, Session Stitching, Threat Scoring, Blocking, Virtual Patching, and AI Security.

**Why needed:** The TPA monitors ALL traffic (N-S and E-W) without application code changes. It auto-discovers endpoints Apigee misses, detects the attack chain in Act 5, triggers the AI SRE runbook in Act 6, and catalogs AI assets in Act 7.

**Acts:** 5 (runtime detection of attack chain), 6 (alert triggers AI SRE), 7 (AI Discovery, MCP risk scoring, AI Security Dashboard).

### Exact Config

| Parameter | Value |
|-----------|-------|
| Image | `traceable/tpa:latest` |
| Kind | DaemonSet (runs on every node) |
| Namespace | `harnessbank-demo` |
| Manifest | `deploy/k8s/traceable/traceable-agent.yaml` |

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `TA_ENVIRONMENT` | `demo` | Environment label |
| `TA_SERVICE_NAME` | `demobank` | Service identifier |
| `TA_REPORTING_ENDPOINT` | From Secret `traceable-config` key `reporting-endpoint` | Traceable SaaS endpoint |
| `TA_API_TOKEN` | From Secret `traceable-config` key `api-token` | Auth token |
| `TA_CAPTURE_EAST_WEST` | `true` | Capture internal service-to-service traffic |
| `TA_AI_SECURITY_ENABLED` | `true` | Enable AI API discovery and AI content inspection |

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: traceable-config
  namespace: harnessbank-demo
type: Opaque
stringData:
  reporting-endpoint: "https://app.traceable.ai"   # Your Traceable tenant URL
  api-token: "<REPLACE_WITH_TRACEABLE_TOKEN>"       # From Traceable admin panel
```

### Security Context

```yaml
securityContext:
  capabilities:
    add: ["NET_RAW", "NET_ADMIN"]
```

Required for packet capture on the node network interfaces.

### Features Enabled (by Act)

| Feature | Act | Description |
|---------|-----|-------------|
| API Discovery | 5, 7 | Auto-discover all endpoints including zombies and undocumented |
| Behavioral Baseline Detection | 5 | Detect anomalies in both N-S and E-W traffic |
| Session Stitching | 5 | Correlate attacker requests across 7-day window |
| Threat Scoring | 5 | Escalating risk scores: 35 (recon) -> 65 (exploit) -> 85 (data exfil) |
| Blocking Policies | 5 | Auto-block threat actors exceeding threshold |
| Virtual Patching | 5, 6 | Protection policies without code changes |
| Data Protection (PII) | 5, 7 | Detect PII in API responses |
| AI Discovery | 7 | Catalog AI APIs + MCP tool connections |
| MCP Risk Score | 7 | Multi-factor risk scoring per AI asset |

### Setup Commands

```bash
# 1. Get Traceable token from admin panel
#    Go to: Traceable dashboard -> Settings -> Agent Tokens -> Generate

# 2. Create the secret with real values
kubectl create secret generic traceable-config \
  --namespace=harnessbank-demo \
  --from-literal=reporting-endpoint="https://<YOUR-TENANT>.app.traceable.ai" \
  --from-literal=api-token="<YOUR-TOKEN>"

# 3. Deploy the DaemonSet
kubectl apply -f deploy/k8s/traceable/traceable-agent.yaml

# 4. Verify agent is running on all nodes
kubectl get daemonset traceable-agent -n harnessbank-demo
kubectl logs -l app=traceable-agent -n harnessbank-demo --tail=20

# 5. Verify in Traceable dashboard
#    Agents -> Should show 3 agents (1 per node)
#    Services -> Should show "demobank" service auto-discovered
```

---

## 5. Load Balancer / Ingress

**What:** NGINX Ingress Controller routing external traffic to the DemoBank service via host-based rules.

**Why needed:** Provides the external entry point for the demo. Routes traffic to the correct service and gives Traceable N-S visibility. The ingress also demonstrates which paths Apigee registers vs. which paths bypass the gateway.

**Acts:** All acts use the ingress for external access. Act 5 specifically exploits paths not registered in Apigee.

### Exact Config

| Parameter | Value |
|-----------|-------|
| Controller | NGINX Ingress Controller v1.10.0+ |
| Host | `demobank.app` |
| TLS | Disabled for demo (`ssl-redirect: "false"`) |
| Manifest | `deploy/k8s/ingress/ingress.yaml` |

### Ingress Rules

| Path | PathType | Backend Service | Port |
|------|----------|----------------|------|
| `/api/accounts` | Prefix | `harnessbank-demo` | 80 |
| `/api/ai` | Prefix | `harnessbank-demo` | 80 |
| `/api/admin` | Prefix | `harnessbank-demo` | 80 |
| `/` | Prefix | `harnessbank-demo` | 80 |

### Service Topology

```
External traffic
    |
    v
[NGINX Ingress] -- host: demobank.app
    |
    |-- /api/accounts --> Service: harnessbank-demo (LB, 80->3000)
    |-- /api/ai       --> Service: harnessbank-demo (LB, 80->3000)
    |-- /api/admin    --> Service: harnessbank-demo (LB, 80->3000)
    |-- /             --> Service: harnessbank-demo (LB, 80->3000)
    |
    DemoBank app internally calls:
    |
    `--> Service: mcp-financial-data (ClusterIP, 5001) [E-W traffic]
```

### TLS Setup (for production-like demos)

```bash
# Optional: If TLS is needed, generate a self-signed cert or use cert-manager
kubectl create secret tls demobank-tls \
  --cert=tls.crt --key=tls.key \
  -n harnessbank-demo

# Then add to ingress spec:
# spec.tls:
#   - hosts: ["demobank.app"]
#     secretName: demobank-tls
```

---

## 6. DNS and Networking

**What:** DNS resolution for `demobank.app` and network configuration enabling both N-S and E-W traffic patterns.

**Why needed:** The demo uses `demobank.app` as the hostname. Attendees (or the presenter's machine) must resolve this to the ingress controller's external IP. Internal ClusterIP networking enables the E-W traffic pattern between DemoBank and MCP Financial Data.

**Acts:** All.

### DNS Record

| Record | Type | Value | TTL |
|--------|------|-------|-----|
| `demobank.app` | A | `<INGRESS_EXTERNAL_IP>` | 300 |

### Setup Commands

```bash
# Get the ingress controller external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Option A: Real DNS (if you own the domain)
# Add A record in your DNS provider pointing demobank.app to the external IP

# Option B: Local /etc/hosts (for local demos)
echo "<INGRESS_EXTERNAL_IP> demobank.app" | sudo tee -a /etc/hosts

# Option C: nip.io (no DNS setup needed)
# Use <EXTERNAL_IP>.nip.io instead of demobank.app
# Update ingress host accordingly
```

### Firewall Rules

| Rule | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| Allow HTTP ingress | TCP | 80 | 0.0.0.0/0 | Demo access |
| Allow HTTPS ingress | TCP | 443 | 0.0.0.0/0 | TLS demo access (if enabled) |
| Allow NodePort range | TCP | 30000-32767 | Internal | K8s node ports |

```bash
# GKE: Firewall rules are auto-created for LoadBalancer services.
# If using a custom VPC, ensure these rules exist:
gcloud compute firewall-rules create allow-demobank-http \
  --allow tcp:80,tcp:443 \
  --target-tags=gke-demobank-cluster \
  --source-ranges=0.0.0.0/0
```

### Internal Networking (E-W)

| Source | Destination | DNS | Port | Protocol |
|--------|------------|-----|------|----------|
| `harnessbank-demo` pod | `mcp-financial-data` service | `mcp-financial-data.harnessbank-demo.svc.cluster.local` | 5001 | HTTP |

The MCP Financial Data service is ClusterIP only -- never exposed externally. DemoBank calls it at `http://mcp-financial-data:5001/mcp/financial-data` from within the cluster. Traceable TPA captures this E-W traffic because `TA_CAPTURE_EAST_WEST=true`.

---

## 7. Observability

**What:** Prometheus metrics collection and Grafana dashboards for Continuous Verification during canary deployments.

**Why needed:** Act 4 uses Continuous Verification to compare canary vs. baseline metrics (latency p50/p99, error rate, throughput). Harness CV needs a metrics provider to query.

**Acts:** 4 (Continuous Verification), 6 (AI SRE health context).

### Prometheus Config

```bash
# Install Prometheus via Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### Scrape Config

```yaml
# ServiceMonitor for DemoBank
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: demobank-metrics
  namespace: monitoring
  labels:
    release: prometheus
spec:
  namespaceSelector:
    matchNames: [harnessbank-demo]
  selector:
    matchLabels:
      app: harnessbank-demo
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
```

### Metrics Required for Continuous Verification

| Metric | Type | Query (PromQL) | CV Purpose |
|--------|------|----------------|-----------|
| Request latency p99 | Histogram | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service="demobank"}[5m]))` | Latency regression detection |
| Request latency p50 | Histogram | `histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{service="demobank"}[5m]))` | Median latency baseline |
| Error rate | Counter | `rate(http_requests_total{service="demobank",status=~"5.."}[5m]) / rate(http_requests_total{service="demobank"}[5m])` | Error spike detection |
| Throughput | Counter | `rate(http_requests_total{service="demobank"}[5m])` | Traffic volume |

### Grafana Dashboard

```bash
# Grafana is included in kube-prometheus-stack
# Access via port-forward
kubectl port-forward svc/prometheus-grafana -n monitoring 3001:80

# Default credentials: admin / prom-operator
# Import DemoBank dashboard JSON or create:
#   Panel 1: Request Rate (throughput)
#   Panel 2: Latency p50/p99
#   Panel 3: Error Rate %
#   Panel 4: Pod CPU/Memory
```

### Harness CV Config

| Field | Value |
|-------|-------|
| Health Source | Prometheus |
| Prometheus URL | `http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090` |
| Metric Pack | Performance (latency, throughput), Errors (error rate) |
| Sensitivity | Medium |
| Duration | 5 minutes (demo speed) |
| Baseline | Last successful deployment |

---

## 8. Harness Platform

**What:** Harness SaaS platform with all required modules enabled and configured.

**Why needed:** Harness is the orchestration layer for the entire demo. Every Act from 1 to 7 uses Harness capabilities.

**Acts:** All (1-7).

### Required Modules

| Module | Acts | Capabilities Used |
|--------|------|------------------|
| **CI** (Continuous Integration) | 2 | Build, Test Intelligence, pipeline triggers |
| **CD** (Continuous Delivery) | 4 | Canary deployment, rollback, manifest management |
| **STO** (Security Testing Orchestration) | 3 | Semgrep, AI SAST (Qwiet), SCA scanners, triage agent, remediation agent |
| **SCS** (Supply Chain Security) | 3, 6 | SBOM generation (CycloneDX/SPDX), SLSA attestation, Cosign signing, Remediation Tracker |
| **SRM** (Service Reliability Management) | 4, 6 | Continuous Verification, AI SRE, runbooks, alert rules |
| **WAAP** (Web App & API Protection) | 5, 7 | Traceable integration, API Discovery, AI Security Dashboard |

### Pipeline: PR-Validation

The single pipeline that drives Acts 2-4:

```
Pipeline: PR-Validation
├── Trigger: GitHub PR on luisredda/ai-agentic-demo
│
├── Stage 1: CI Build
│   ├── Step: Checkout code
│   ├── Step: Run tests (pytest) with Test Intelligence
│   │   └── TI selects ~11 of 47 tests based on code changes
│   ├── Step: Build Docker image (demobank)
│   ├── Step: Build Docker image (mcp-financial-data)
│   └── Step: Push to container registry
│
├── Stage 2: Change Advisor (Expert Agent)
│   ├── Risk assessment of PR changes
│   └── Posts review comment on PR
│
├── Stage 3: Security Scan
│   ├── Step: Semgrep SAST (custom rules from .semgrep.yml)
│   ├── Step: AI SAST (Qwiet) with confidence scoring
│   ├── Step: SCA (dependency CVE scan — detects requests==2.25.1)
│   ├── Step: SBOM Generation (CycloneDX)
│   ├── Step: SLSA Attestation (Cosign signing)
│   ├── Step: Triage Agent (CVSS + EPSS + reachability)
│   ├── Step: Remediation Agent (fix generation + validation + push)
│   └── Gate: OPA policy "no-critical-findings"
│
├── Stage 4: Deploy
│   ├── Gate: SLSA Verification (pre-deploy)
│   ├── Gate: OPA Policies (4 policies)
│   ├── Gate: Change Management ticket (ServiceNow/Jira)
│   ├── Step: Canary deploy (10% -> 25% -> 100%)
│   └── Step: Continuous Verification (Prometheus metrics, 5 min)
```

### Connectors (11 total)

| Connector | Type | Purpose | Acts |
|-----------|------|---------|------|
| **GitHub** | Code Repository | PR triggers, code checkout, Change Advisor comments | 1, 2, 3 |
| **Container Registry** | Docker Registry / GAR | Push/pull images | 3, 4 |
| **Kubernetes** | K8s Cluster | Deploy target | 4 |
| **Prometheus** | Monitoring | Continuous Verification metrics source | 4 |
| **Traceable** | WAAP | Runtime protection integration, AI Security | 5, 7 |
| **Slack** | Notification | `#security-incidents` channel for AI SRE runbook | 6 |
| **Jira** | Ticketing | Project `SEC` for incidents + Remediation Tracker | 3, 6 |
| **PagerDuty** | Alerting | Service `security-oncall` for AI SRE runbook | 6 |
| **Zoom** | Collaboration | Incident bridge creation | 6 |
| **ServiceNow** | Change Management | Auto-generated change tickets | 4 |
| **Cosign** | Signing | SLSA attestation signing key | 3, 4 |

### Delegates

| Delegate | Where | Purpose |
|----------|-------|---------|
| K8s Delegate | In the GKE cluster (`harness-delegate` namespace) | Execute pipeline steps, deploy workloads, connect to cluster resources |

```bash
# Install Harness Delegate in the cluster
helm repo add harness-delegate https://app.harness.io/storage/harness-download/delegate-helm-chart/
helm install harness-delegate harness-delegate/harness-delegate-ng \
  --namespace harness-delegate --create-namespace \
  --set accountId=<HARNESS_ACCOUNT_ID> \
  --set delegateToken=<DELEGATE_TOKEN> \
  --set delegateName=demobank-delegate \
  --set managerEndpoint=https://app.harness.io
```

### Feature Flags

| Flag | Value | Purpose |
|------|-------|---------|
| `STO_AI_SAST` | Enabled | AI-enhanced SAST scanning |
| `SCS_AIBOM` | Enabled | AI Bill of Materials generation (v1.65.0+) |
| `SRM_AI_SRE` | Enabled | AI SRE runbooks and auto-remediation |
| `WAAP_AI_SECURITY` | Enabled | AI Security Dashboard and AI Discovery |
| `CI_TEST_INTELLIGENCE` | Enabled | ML-based test selection |

---

## 9. Integrations

Each integration with its provider, configuration, connector type, and which Acts depend on it.

### 9.1 GitHub

| Field | Value |
|-------|-------|
| Provider | GitHub.com |
| Repository | `luisredda/ai-agentic-demo` |
| Connector type | GitHub (Code Repository) |
| Auth | GitHub App or Personal Access Token (repo, workflow scopes) |
| Webhook | PR events (opened, synchronize, reopened) |
| Acts | 1 (code push), 2 (PR trigger, Change Advisor), 3 (Remediation Agent push) |

```bash
# Harness GitHub connector setup:
# 1. Create GitHub App or generate PAT with repo + workflow scopes
# 2. In Harness: Connectors -> + New -> GitHub
# 3. Set URL: https://github.com/luisredda/ai-agentic-demo
# 4. Add webhook trigger in pipeline: PR events -> PR-Validation pipeline
```

### 9.2 Slack

| Field | Value |
|-------|-------|
| Provider | Slack (workspace) |
| Channel | `#security-incidents` |
| Connector type | Slack (Notification) |
| Auth | Slack App with Bot Token (chat:write, channels:read) |
| Acts | 6 (AI SRE runbook Steps 1 and 6) |

```bash
# 1. Create Slack App: https://api.slack.com/apps
# 2. Add Bot Token scopes: chat:write, channels:read
# 3. Install to workspace, invite bot to #security-incidents
# 4. In Harness: Connectors -> + New -> Slack
# 5. Add Slack Bot Token
```

### 9.3 Jira

| Field | Value |
|-------|-------|
| Provider | Jira Cloud or Server |
| Project | `SEC` (Security) |
| Issue type | Incident |
| Connector type | Jira (Ticketing) |
| Auth | API token (user + token) |
| Acts | 3 (Remediation Tracker), 6 (AI SRE runbook Step 3) |

```bash
# 1. Create Jira project "SEC" with issue type "Incident"
# 2. Generate API token: https://id.atlassian.com/manage-profile/security/api-tokens
# 3. In Harness: Connectors -> + New -> Jira
# 4. Set Jira URL, username, API token
```

### 9.4 PagerDuty

| Field | Value |
|-------|-------|
| Provider | PagerDuty |
| Service | `security-oncall` |
| Connector type | PagerDuty (Alerting) |
| Auth | Integration Key (Events API v2) |
| Acts | 6 (AI SRE runbook Step 2) |

```bash
# 1. Create PagerDuty service "security-oncall"
# 2. Add integration: Events API v2 -> get Integration Key
# 3. In Harness: Connectors -> + New -> PagerDuty
# 4. Add Integration Key
```

### 9.5 Zoom

| Field | Value |
|-------|-------|
| Provider | Zoom |
| Purpose | Incident bridge meeting creation |
| Auth | Server-to-Server OAuth App |
| Acts | 6 (AI SRE runbook Step 5) |

```bash
# 1. Create Zoom Server-to-Server OAuth App: https://marketplace.zoom.us/
# 2. Add scopes: meeting:write:admin
# 3. In Harness: configure HTTP Request step with Zoom API
# 4. POST https://api.zoom.us/v2/users/me/meetings
```

### 9.6 ServiceNow

| Field | Value |
|-------|-------|
| Provider | ServiceNow |
| Purpose | Change Management auto-ticket generation |
| Connector type | ServiceNow (Change Management) |
| Auth | Service account (username + password) |
| Acts | 4 (pre-deploy change ticket CHG-2024-08271) |

```bash
# 1. ServiceNow instance with Change Management module
# 2. Create service account with change_manager role
# 3. In Harness: Connectors -> + New -> ServiceNow
# 4. Set instance URL, username, password
```

### 9.7 Prometheus

| Field | Value |
|-------|-------|
| Provider | Prometheus (in-cluster) |
| URL | `http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090` |
| Connector type | Prometheus (Monitoring) |
| Auth | None (in-cluster access) |
| Acts | 4 (Continuous Verification) |

### 9.8 Traceable (WAAP)

| Field | Value |
|-------|-------|
| Provider | Traceable.ai |
| Tenant URL | `https://<TENANT>.app.traceable.ai` |
| Connector type | Traceable (WAAP) |
| Auth | API Token from Traceable admin |
| Acts | 5 (runtime detection), 6 (alert source), 7 (AI Security Dashboard) |

---

## 10. Security Tools

**What:** Static and dynamic analysis tools integrated into the Harness pipeline for security testing.

**Why needed:** Act 3 demonstrates the Security Testing Agent: SAST finds code vulnerabilities, SCA finds dependency vulnerabilities, and SCS generates the SBOM and attestation. The 7 planted vulnerabilities must be detected by SAST. The `requests==2.25.1` CVE must be detected by SCA.

**Acts:** 3 (security scan), 4 (SLSA verification gate).

### Semgrep (SAST)

| Field | Value |
|-------|-------|
| Config file | `.semgrep.yml` (7 custom rules) |
| Pipeline step | STO -> Semgrep scanner |
| Expected findings | 7 vulnerabilities (4 detected by SAST, 3 runtime-only) |

Rules in `.semgrep.yml`:

| Rule ID | Severity | Vulnerability | File |
|---------|----------|--------------|------|
| `demo-bank-sql-injection` | ERROR | SQL Injection (VULN-001) | `accounts.py:14` |
| `demo-bank-command-injection` | ERROR | Command Injection (VULN-002) | `admin.py:18` |
| `demo-bank-reflected-xss` | WARNING | Reflected XSS (VULN-006) | `app.py:96` |
| `demo-bank-insecure-cors` | WARNING | Insecure CORS (VULN-007) | `app.py:31` |
| `demo-bank-prompt-injection` | ERROR | Prompt Injection (VULN-008) | `ai_assistant.py:64` |
| `demo-bank-pii-leak-ai-response` | WARNING | PII Leak (VULN-009) | `ai_assistant.py:77` |
| `demo-bank-bola-idor` | ERROR | BOLA/IDOR (VULN-010) | `accounts.py:36` |

### AI SAST (Qwiet)

| Field | Value |
|-------|-------|
| Provider | Qwiet (via Harness STO) |
| Features | Confidence scoring, data-flow analysis, reachability analysis |
| Pipeline step | STO -> AI SAST scanner |

### SCA (Software Composition Analysis)

| Field | Value |
|-------|-------|
| Pipeline step | STO -> SCA scanner |
| Expected finding | `requests==2.25.1` -> CVE-2023-32681 (HTTP redirect leak) |
| Fix | Upgrade to `requests>=2.31.0` |

### Cosign (SLSA Attestation)

| Field | Value |
|-------|-------|
| Tool | Cosign (Sigstore) |
| Purpose | Sign container images, generate SLSA provenance attestation |
| SLSA Level | 2 |
| Pipeline step | SCS -> Cosign Sign + Attest |

```bash
# Generate Cosign key pair (one-time setup)
cosign generate-key-pair

# In pipeline, Harness SCS handles:
# 1. cosign sign --key <key> <image>
# 2. cosign attest --key <key> --predicate sbom.json <image>
```

### OPA Policies (6 total)

| Policy | Act | Purpose | Enforcement |
|--------|-----|---------|------------|
| `no-critical-findings.rego` | 3 | Block pipeline if critical SAST findings exist | Pipeline gate after security scan |
| `security-scan-required.rego` | 4 | Require security scan completion before deploy | Pre-deploy gate |
| `slsa-attestation-required.rego` | 4 | Require SLSA attestation on artifact | Pre-deploy gate |
| `deploy-window-check.rego` | 4 | Block deploys outside approved window | Pre-deploy gate |
| `approval-requirements.rego` | 4 | Require 1+ reviewer approval | Pre-deploy gate |
| `block-unprotected-ai-endpoints.rego` | 6 | Block AI endpoints without auth or with prompt injection | Post-incident policy |

---

## 11. Developer Workstation

**What:** Local developer environment configured for Act 1 (Inner Loop) where Claude Code generates the AI assistant feature live.

**Why needed:** Act 1 is the "developer experience" showcase. The presenter writes code with Claude Code, uses Harness MCP tools for context, and pushes a PR that triggers the pipeline.

**Acts:** 1 (primary), 2-3 (monitoring pipeline from IDE).

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Claude Code | Latest | AI coding agent -- generates AI assistant feature |
| VS Code | 1.90+ | IDE with Harness extensions |
| Harness IDE Extension | Latest | Sidebar: pipeline status, security findings |
| Harness AI Chat Agent | Latest | Conversational interface in IDE |
| Python | 3.12+ | Local app development and testing |
| Docker | 24+ | Local image builds |
| kubectl | 1.28+ | Cluster interaction |
| gcloud CLI | Latest | GKE cluster management |
| git | 2.40+ | Version control |
| gh CLI | 2.40+ | GitHub operations |

### Harness MCP Configuration

```json
// .mcp.json (in project root)
{
  "mcpServers": {
    "harness": {
      "url": "https://app.harness.io/gratis/gateway/mcp/api/v1/accounts/<ACCOUNT_ID>/sse",
      "headers": {
        "x-api-key": "<HARNESS_API_KEY>"
      }
    }
  }
}
```

### Claude Code Setup

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify MCP connection
claude mcp list

# Key MCP tools available:
# - mcp__harness__harness_get: Get pipeline/service/deployment status
# - mcp__harness__harness_list: List resources
# - mcp__harness__harness_diagnose: Diagnose pipeline failures
# - mcp__harness__harness_execute: Trigger pipeline runs
```

### VS Code Extensions

| Extension | ID | Purpose |
|-----------|-----|---------|
| Harness | `harness.harness-vscode` | Pipeline status, security findings sidebar |
| Harness AI Chat | `harness.harness-ai-chat` | Conversational AI in IDE |
| Python | `ms-python.python` | Python language support |
| Semgrep | `returntocorp.semgrep` | Local SAST scanning |

### Terminal Environment

```bash
# Required environment variables
export HARNESS_ACCOUNT_ID="<account-id>"
export HARNESS_API_KEY="<api-key>"
export HARNESS_ORG_ID="default"
export HARNESS_PROJECT_ID="demobank"

# Verify cluster access
kubectl get pods -n harnessbank-demo

# Verify app is running
curl http://demobank.app/health
```

---

## Configuration Checklist

Ordered steps from zero to fully running demo. Estimated time per step.

### Phase A: Infrastructure (Steps 1-8)

| # | Step | Command / Action | Est. Time | Verification |
|---|------|-----------------|-----------|-------------|
| 1 | Create GKE cluster | `gcloud container clusters create demobank-cluster --zone us-central1-a --num-nodes 3 --machine-type e2-standard-4 --enable-ip-alias --release-channel stable` | 10 min | `kubectl get nodes` shows 3 Ready nodes |
| 2 | Get cluster credentials | `gcloud container clusters get-credentials demobank-cluster --zone us-central1-a` | 1 min | `kubectl cluster-info` returns API server URL |
| 3 | Create namespace | `kubectl apply -f deploy/k8s/base/namespace.yaml` | 1 min | `kubectl get ns harnessbank-demo` |
| 4 | Apply ConfigMap | `kubectl apply -f deploy/k8s/base/configmap.yaml` | 1 min | `kubectl get configmap -n harnessbank-demo` |
| 5 | Install NGINX Ingress | `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml` | 3 min | `kubectl get svc -n ingress-nginx` shows EXTERNAL-IP |
| 6 | Create GAR repository | `gcloud artifacts repositories create demobank --repository-format=docker --location=us-central1` | 2 min | `gcloud artifacts repositories list` |
| 7 | Build and push DemoBank image | `docker build -t <registry>/demobank:latest . && docker push <registry>/demobank:latest` | 5 min | `gcloud artifacts docker images list <registry>/demobank` |
| 8 | Build and push MCP image | `docker build -t <registry>/mcp-financial-data:latest -f services/mcp-financial-data/Dockerfile services/mcp-financial-data/ && docker push <registry>/mcp-financial-data:latest` | 3 min | `gcloud artifacts docker images list <registry>/mcp-financial-data` |

**Phase A total: ~26 min**

### Phase B: Harness Platform (Steps 9-15)

| # | Step | Command / Action | Est. Time | Verification |
|---|------|-----------------|-----------|-------------|
| 9 | Install Harness Delegate | `helm install harness-delegate harness-delegate/harness-delegate-ng --namespace harness-delegate --create-namespace --set accountId=<ID> --set delegateToken=<TOKEN> --set delegateName=demobank-delegate` | 5 min | Delegate shows "Connected" in Harness UI |
| 10 | Create GitHub connector | Harness UI: Connectors -> GitHub -> add PAT/App, set webhook | 10 min | Test connection succeeds |
| 11 | Create Container Registry connector | Harness UI: Connectors -> Docker Registry -> add GAR URL + auth | 5 min | Test connection succeeds |
| 12 | Create K8s cluster connector | Harness UI: Connectors -> Kubernetes -> use delegate in cluster | 5 min | Test connection succeeds |
| 13 | Create PR-Validation pipeline | Harness UI: Pipelines -> create with 4 stages (CI Build, Change Advisor, Security Scan, Deploy) | 60 min | Pipeline visible, trigger configured |
| 14 | Configure STO scanners | Harness UI: STO -> add Semgrep step (config `.semgrep.yml`), AI SAST, SCA steps | 30 min | Test scan on main branch finds expected vulnerabilities |
| 15 | Configure SCS | Harness UI: SCS -> SBOM generation (CycloneDX), Cosign key, SLSA attestation | 20 min | SBOM generated on test build |

**Phase B total: ~2.25 hours**

### Phase C: Integrations (Steps 16-20)

| # | Step | Command / Action | Est. Time | Verification |
|---|------|-----------------|-----------|-------------|
| 16 | Deploy workloads to K8s | `kubectl apply -f deploy/k8s/demobank/deployment.yaml -f deploy/k8s/demobank/service.yaml -f deploy/k8s/mcp-financial-data/deployment.yaml -f deploy/k8s/mcp-financial-data/service.yaml -f deploy/k8s/ingress/ingress.yaml` | 5 min | `curl http://demobank.app/health` returns 200 |
| 17 | Deploy Traceable agent | Create secret with real token, then `kubectl apply -f deploy/k8s/traceable/traceable-agent.yaml` | 15 min | DaemonSet shows 3/3 ready, service appears in Traceable dashboard |
| 18 | Install Prometheus stack | `helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace` | 10 min | `kubectl get pods -n monitoring` all running |
| 19 | Configure Harness CV | Harness UI: SRM -> Add Prometheus health source, configure metric queries, set sensitivity | 20 min | CV analysis runs on test deploy |
| 20 | Configure Slack + Jira + PagerDuty connectors | Harness UI: Connectors -> add each integration with tokens/keys | 30 min | Test notifications succeed |

**Phase C total: ~1.3 hours**

### Phase D: Verification (Steps 21-25)

| # | Step | Command / Action | Est. Time | Verification |
|---|------|-----------------|-----------|-------------|
| 21 | Configure DNS | Add A record for `demobank.app` pointing to ingress external IP, or update `/etc/hosts` | 5 min | `curl http://demobank.app/health` returns `{"status":"ok"}` |
| 22 | Configure AI SRE runbook | Harness UI: SRM -> Runbooks -> create "security-incident-response" with 6 steps (Slack, PagerDuty, Jira, HTTP, Zoom, Slack) | 30 min | Test runbook execution completes all steps |
| 23 | Configure Apigee (or mock gateway) | Deploy Apigee X proxy or Kong with equivalent policies from `deploy/apigee/apiproxy-spec.yaml` | 30 min | Registered endpoints require API key, unregistered endpoints accessible without |
| 24 | End-to-end smoke test | Run `scripts/smoke-test.sh`, test all API endpoints, verify MCP service responds, verify Traceable sees traffic | 15 min | All endpoints respond, Traceable shows discovered APIs |
| 25 | Dry-run demo flow | Create test PR, watch pipeline execute Acts 2-4 stages, run attack curls for Act 5 | 30 min | Pipeline completes, WAAP detects attack, AI SRE triggers |

**Phase D total: ~1.8 hours**

### Total Setup Time

| Phase | Steps | Estimated Time |
|-------|-------|---------------|
| A: Infrastructure | 1-8 | ~30 min |
| B: Harness Platform | 9-15 | ~2.25 hours |
| C: Integrations | 16-20 | ~1.3 hours |
| D: Verification | 21-25 | ~1.8 hours |
| **Total** | **25 steps** | **~5.5 hours** |

This assumes all accounts (Harness, Traceable, Slack, Jira, PagerDuty, Zoom, GCP) are already provisioned. Add 2-3 hours if account provisioning is needed.
