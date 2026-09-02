# Demo Reset Strategy — End-to-End SecOps AI Agentic Demo

## Overview

Reset procedure to present the 7-act demo from scratch. Resets **app code only** — all infrastructure, documentation, pipeline config, and Traceable components stay in place.

### Branch Architecture

```
main                            ← Upstream clean app (basic vulns, no AI)
  │
  └─ secops/ai-agentic-demo     ← Working branch (docs, infra, prompt cards, scripts)
       │                           App code oscillates through 3 states per demo run
       │
       └─ secops/ai-agentic-demo-main  ← Reference snapshot (intermediate state)
```

### App Code States

```
STATE 0 (pre-Act-1)              STATE 1 (post-Act-1)              STATE 2 (post-Act-3)
─────────────────                ─────────────────                ─────────────────
No AI assistant                  AI assistant + chat widget        AI assistant + chat widget
No chat widget                   VULN-001: SQLi ✗                 SQLi FIXED ✓
VULN-001: SQLi ✗                 VULN-002: CMDi ✗                 CMDi FIXED ✓
VULN-002: CMDi ✗                 VULN-006: XSS ✗                  XSS FIXED ✓
VULN-006: XSS ✗                  VULN-007: CORS ✗                 CORS FIXED ✓
VULN-007: CORS ✗                 VULN-008: Prompt Inj ✗           Prompt Inj FIXED ✓
No PII in DB                     VULN-009: PII exposure ✗         PII FIXED ✓
TEXT ids in schema                VULN-010: BOLA ✗                 BOLA FIXED ✓
3 accounts (DEMO-xxx)            PII in seed (email, phone)       PII removed
                                 INTEGER ids, 5 accounts          Aggregated queries only

Source: main                     Source: Act 1 commit              Source: Act 3 commit
```

---

## Reset Checklist

### Layer 1 — App Code (script automatizado)

```bash
./scripts/demo-reset.sh --db --commit
git push origin secops/ai-agentic-demo
```

Esto restaura los 10 archivos de app desde `main` y elimina `ai_assistant.py`. Verificación automática incluida en el script.

**Archivos que se restauran:**

| Archivo | Cambio |
|---------|--------|
| `app/app.py` | Remove AI blueprint, restore CORS wildcard, restore XSS |
| `app/db.py` | TEXT ids, no email/phone columns |
| `app/routes/accounts.py` | Restore SQLi (string concat), remove /details endpoint |
| `app/routes/admin.py` | Restore CMDi (shell=True) |
| `app/server.py` | Remove auto-seed logic |
| `app/static/app.js` | Remove chat widget JS |
| `app/static/styles.css` | Remove chat widget CSS |
| `app/templates/dashboard.html` | Remove chat widget HTML |
| `requirements.txt` | Remove requests library |
| `scripts/seed.py` | 3 accounts, TEXT ids, no PII |

**Archivos que se eliminan:**

| Archivo | Razón |
|---------|-------|
| `app/routes/ai_assistant.py` | No existe en STATE 0 |

**Archivos que NO se tocan:**

| Directorio | Contenido |
|------------|-----------|
| `docs/` | Prompt cards (Acts 1-7), architecture diagrams, setup guides |
| `deploy/` | K8s manifests, Traceable configs, Helm values |
| `.harness/` | Pipeline YAML, services, environments, OPA policies |
| `scripts/` | attack-chain.sh, traceable-demo-setup.sh, demo-reset.sh |
| `services/` | mcp-financial-data (Flask mock) |
| `policies/` | OPA rego files |
| `tests/` | 50 test files |

---

### Layer 2 — Pipeline / Docker Image

El pipeline se triggerea con push al branch. Después del reset:

```
Push STATE 0 → Pipeline runs → Build image :tag → Deploy to GKE
```

**Opción A — Dejar que el pipeline corra naturalmente:**
1. `demo-reset.sh --db --commit` + `git push`
2. Pipeline builds imagen con app en STATE 0
3. Deploy automático pone la app limpia en GKE
4. Demo empieza con la app limpia corriendo

**Opción B — Solo reset de código, sin redeploy:**
1. `demo-reset.sh --commit` + `git push`
2. No triggear pipeline aún
3. La app en GKE sigue con la imagen anterior (STATE 2)
4. El primer deploy ocurre en Act 4 (con el código de Act 3)

**Recomendado: Opción A** — Así el SE puede mostrar la app limpia corriendo antes de empezar Act 1.

---

### Layer 3 — Traceable Protection Policies

Las policies se configuran en la UI de Traceable, no en el código. Resetear manualmente:

**URL:** `https://app.us9.traceable.ai` → Protection Policies

| Categoría | Reset a | Acción |
|-----------|---------|--------|
| Custom Signatures | Monitor | Dropdown → Monitor (si estaba en Block) |
| Malicious Sources | Monitor | Dropdown → Monitor |
| Rate Limiting | Monitor | Dropdown → Monitor (o eliminar reglas custom) |
| DLP | Monitor | Dropdown → Monitor |
| Enumeration | Monitor | Dropdown → Monitor |
| API Protection | Monitor | Ya está en Monitor (no tiene Block) |
| AI Firewall | Monitor | Ya está en Monitor (no tiene Block) |

**Threat Activity:** No necesita reset — las detecciones históricas se pueden ignorar o filtrar por fecha durante el demo.

---

### Layer 4 — Traceable Infrastructure (NO resetear)

Estos componentes persisten entre demos y NO necesitan reset:

| Componente | Namespace | Estado | Acción |
|------------|-----------|--------|--------|
| TPA (traceable-agent) | harnessbank-demo-end2end | Running | Mantener |
| eBPF Tracer (DaemonSet) | harnessbank-demo-end2end | Running | Mantener |
| AST Runner | harnessbank-demo-end2end | Running | Mantener |
| TME sidecar | nginx (en ingress pod) | Running (2/2) | Mantener |
| token-secret | nginx + harnessbank-demo-end2end | Present | Mantener |
| tme-template-override | harnessbank-demo-end2end | Present | Mantener |
| MutatingWebhook | cluster-wide | Active | Mantener |

El TME sidecar se mantiene inyectado. En el demo, Act 7 PASO 0 solo verifica que está corriendo — no lo reinstala.

---

### Layer 5 — Kubernetes DemoBank (se resetea con pipeline)

El deploy del pipeline reemplaza la imagen. Si se necesita reset manual:

```bash
# Verificar estado actual
kubectl get deploy -n harnessbank-demo-end2end -o wide

# La DB se re-crea al inicio de la app (init_db + seed en server.py)
# No hay volumen persistente — cada pod nuevo tiene DB fresca
```

---

### Layer 6 — Harness AI SRE Webhook

El webhook de AI SRE está configurado en el pipeline stage `AISRE_Deploy_Notification`. No necesita reset — se dispara en cada deploy.

**Verificar que la URL sigue activa:**
```
Webhook URL: configurado en el pipeline YAML (ver .harness/pipelines/ai-sdlc-demobank.yaml)
```

---

## Secuencia Completa de Reset

```
PRE-DEMO RESET (30 min antes del demo)
═══════════════════════════════════════

1. CÓDIGO — Reset app a STATE 0
   ┌─────────────────────────────────────────────┐
   │ ./scripts/demo-reset.sh --db --commit       │
   │ git push origin secops/ai-agentic-demo      │
   └─────────────────────────────────────────────┘

2. PIPELINE — Opcional: deploy STATE 0 a GKE
   ┌─────────────────────────────────────────────┐
   │ Triggear pipeline manualmente en Harness UI │
   │ O esperar auto-trigger del push             │
   └─────────────────────────────────────────────┘

3. TRACEABLE — Reset policies a Monitor
   ┌─────────────────────────────────────────────┐
   │ app.us9.traceable.ai → Protection Policies  │
   │ Custom Signatures → Monitor                 │
   │ Malicious Sources → Monitor                 │
   │ Rate Limiting → Monitor                     │
   └─────────────────────────────────────────────┘

4. VERIFICACIÓN
   ┌─────────────────────────────────────────────┐
   │ ✓ App code en STATE 0 (git diff main = 0)   │
   │ ✓ No ai_assistant.py                        │
   │ ✓ No chat widget visible                    │
   │ ✓ SQLi/CMDi/XSS/CORS presentes             │
   │ ✓ Traceable policies en Monitor             │
   │ ✓ TME sidecar corriendo (2/2 nginx pod)     │
   │ ✓ Claude Code + Harness MCP respondiendo    │
   │ ✓ Prompt cards accesibles en docs/prompts/  │
   └─────────────────────────────────────────────┘
```

---

## Demo Flow Post-Reset

```
STATE 0 ──────────────────────────────────────────────────────────────────
  │
  │ Act 1: SE pide a Claude Code agregar AI chat feature
  │   Claude genera: ai_assistant.py + chat widget + PII seed
  │   Introduce: VULN-008 (prompt inj), VULN-009 (PII), VULN-010 (BOLA)
  │   → git commit + push
  │
STATE 1 ──────────────────────────────────────────────────────────────────
  │
  │ Act 2: Pipeline auto-trigger
  │   Build → Test Intelligence → SLSA → SBOM
  │   AI SRE notificado del deploy
  │
  │ Act 3: Pipeline security scanning
  │   Semgrep SAST → encuentra VULN-001,002,006,007,008,009,010
  │   SE pide a Claude Code remediar → commit + push
  │
STATE 2 ──────────────────────────────────────────────────────────────────
  │
  │ Act 4: Pipeline deploy
  │   Canary → CV → Primary → AI SRE notificado
  │
  │ Act 5: Attack chain (scripts/attack-chain.sh o manual)
  │   SQLi, BOLA, Prompt Injection → Traceable DETECTA en Monitor
  │   eBPF captura E-W traffic
  │
  │ Act 6: AI SRE responde
  │   Webhook → Remediation Tracker → SBOM blast radius → OPA policy
  │
  │ Act 7: Block mode + AI Security
  │   Custom Signatures → Block (SQLi/XSS blocked 403)
  │   Malicious Sources → Block (attacker IP blocked 403)
  │   BOLA → Monitor (by design)
  │   AIBOM + AI Discovery + MCP Risk Score
  │
DEMO COMPLETE ────────────────────────────────────────────────────────────
```

---

## Troubleshooting

**El pipeline no se triggerea con el push:**
- Verificar que el trigger está configurado para el branch `secops/ai-agentic-demo`
- Trigger manual: Harness UI → Pipelines → AI SDLC DemoBank → Run

**La app en GKE no refleja STATE 0:**
- La imagen Docker se construye en el pipeline — necesita un pipeline run
- Verificar imagen: `kubectl get deploy harnessbank-demo-end2end -n harnessbank-demo-end2end -o jsonpath='{.spec.template.spec.containers[0].image}'`

**TME no bloquea después de Act 7:**
- Polling cycle: 30 segundos después de cambiar policy en UI
- Verificar: `kubectl logs -n nginx deploy/ingress-nginx-controller -c tme --tail=20`
- Testear desde dentro del cluster: `kubectl run curl-test --rm -i --restart=Never --image=curlimages/curl -- curl -s -w "\n%{http_code}" "http://ingress-nginx-controller.nginx.svc/api/accounts?id=1'%20OR%201=1--" -H "Host: demobank-e2e.selatam.harness-demo.site"`

**demo-reset.sh falla al restaurar archivos:**
- Verificar que `main` branch existe localmente: `git branch -a | grep main`
- Si no: `git fetch origin main:main`

**Zscaler bloquea requests externos:**
- Testear siempre desde dentro del cluster con `kubectl run`
- O usar VPN que bypasee Zscaler para el demo
