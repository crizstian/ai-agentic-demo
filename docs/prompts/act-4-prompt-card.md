# ACTO 4 — Prompt Card para el SE

## Contexto

Las vulnerabilidades están corregidas. El pipeline re-validó. El PR está limpio.
El SE aprueba el PR, mergea, y usa el IDE para monitorear todo — build, supply chain
governance, y canary deployment.

**Estructura del pipeline en merge:**

```
CI Stage (Build and Supply Chain):
├── [parallel] Build DemoBank Image              → Docker push
├── [parallel] Build MCP Financial Data          → Docker push
├── [parallel] SBOM DemoBank                     → SscaOrchestration (CycloneDX + keyless)
├── [parallel] SBOM MCP Financial Data           → SscaOrchestration (CycloneDX + keyless)
├── [parallel] SLSA DemoBank                     → provenance (keyless attestation)
├── [parallel] SLSA MCP Financial                → provenance (keyless attestation)
├── [parallel] Artifact Signing DemoBank         → SscaArtifactSigning (keyless)
└── [parallel] Artifact Signing MCP Financial    → SscaArtifactSigning (keyless)

CD Stage — Deploy DemoBank:
├── Supply Chain (stepGroupInfra: K8s)
│   ├── [parallel] SscaEnforcement               → SBOM policy enforcement + attestation verify
│   ├── [parallel] SlsaVerification              → SLSA provenance verification
│   └── [parallel] SscaArtifactVerification      → Artifact signature verification
├── Canary Deploy (2 pods)
├── Canary Delete
└── Rolling Deploy

CD Stage — Deploy MCP Financial Data:
├── Supply Chain (stepGroupInfra: K8s)
│   ├── [parallel] SscaEnforcement               → SBOM policy enforcement
│   ├── [parallel] SlsaVerification              → SLSA provenance verification
│   └── [parallel] SscaArtifactVerification      → Artifact signature verification
└── Rolling Deploy
```

**CI genera → CD verifica:**
- CI: SBOM + SLSA provenance + artifact signing
- CD: SBOM enforcement + SLSA verification + artifact signature verification

## Pre-requisitos

1. PR #5 con remediaciones aplicadas y pipeline verde
2. Claude Code con Harness MCP conectado
3. Harness IDE Extension mostrando pipeline status
4. `kubectl` configurado para el cluster GKE

---

## PASO 1 — Aprobar y Mergear el PR (t=0:00)

> **Talk Track:** "Las correcciones pasaron la re-validación. Todo verde. Ahora viene el único paso manual del ciclo — la aprobación humana."

### Prompt:

```
Merge PR #5 on the ai-agentic-demo repo. The security remediations
passed validation. Add a merge comment: "Approved: security findings
remediated and re-validated by pipeline."
```

### Resultado esperado:

PR mergeado a `secops/ai-agentic-demo-main`. Pipeline se auto-triggers.

> **Talk Track:** *"Este es el único punto donde un humano interviene. AI propone, humanos disponen."*

---

## PASO 2 — Monitorear Build, SBOM, SLSA y Artifact Signing (CI) (t=0:30)

> **Talk Track:** "El merge disparó el pipeline. Primero el CI stage: build, SBOM, SLSA provenance, y firma de artefactos. Todo lo que genera la cadena de confianza."

### Prompt:

```
The PR was merged and the pipeline should be running. Use the Harness
MCP tools to monitor the Build and Supply Chain steps in the CI stage
of AI_SDLC_DemoBank.

Show me:
1. Docker image build status for both images
2. SBOM generation status (SscaOrchestration)
3. SLSA provenance generation (provenance step)
4. Artifact signing status (SscaArtifactSigning)
```

### Resultado esperado:

```
Build and Supply Chain (CI):
├── Build DemoBank Image          → crizstian/harnessbank-demo:<sequenceId>  ✅
├── Build MCP Financial Data      → crizstian/mcp-financial-data:<sequenceId>  ✅
├── SBOM DemoBank                 → CycloneDX JSON + keyless attestation  ✅
├── SBOM MCP Financial Data       → CycloneDX JSON + keyless attestation  ✅
├── SLSA DemoBank                 → Provenance generated + keyless signed  ✅
├── SLSA MCP Financial            → Provenance generated + keyless signed  ✅
├── Artifact Signing DemoBank     → Keyless signature applied  ✅
└── Artifact Signing MCP          → Keyless signature applied  ✅
```

> **Talk Track:** "Tres capas de supply chain security generadas en CI. Primero, SBOM — inventario completo de cada librería en el container. Segundo, SLSA provenance — certificado de que este artefacto fue construido por este pipeline, con este código. Tercero, artifact signing — firma criptográfica del artefacto. Todo keyless con Harness OIDC."

---

## PASO 3 — Supply Chain Verification en CD (t=1:30)

> **Talk Track:** "CI generó todo. Ahora el CD stage verifica todo — antes de desplegar un solo pod."

### Prompt:

```
The CI stage completed. Show me the Deploy DemoBank CD stage.
I want to see the Supply Chain verification steps that run
BEFORE the canary deployment:
1. SBOM Enforcement (SscaEnforcement)
2. SLSA Verification (SlsaVerification)
3. Artifact Verification (SscaArtifactVerification)
Are they running in parallel? Did they pass?
```

### Resultado esperado:

```
Deploy DemoBank — Supply Chain (parallel, stepGroupInfra: K8s):
├── SscaEnforcement        → SBOM policy check + attestation verify  ✅
├── SlsaVerification       → SLSA provenance verified (keyless)  ✅
└── SscaArtifactVerification → Artifact signature verified (keyless)  ✅
→ All passed, proceeding to Canary Deployment
```

> **Talk Track:**
>
> *"Tres verificaciones en paralelo, usando infraestructura K8s dedicada. Cada una valida una capa diferente:"*
>
> *"SBOM Enforcement — ¿el inventario de componentes cumple con las policies? ¿Hay dependencias prohibidas?"*
>
> *"SLSA Verification — ¿el certificado de provenance fue firmado correctamente? ¿Este artefacto realmente salió de nuestro pipeline?"*
>
> *"Artifact Verification — ¿la firma del container es válida? ¿No fue alterado después del build?"*
>
> *"Si cualquiera de estas falla, el deploy no avanza. CI genera, CD verifica. Separación completa."*

---

## PASO 4 — Consultar OPA Policies (t=2:00)

> **Talk Track:** "Además de la verificación de artefactos, governance policies evalúan compliance a nivel de pipeline."

### Prompt:

```
Show me the governance policy evaluations from the current execution.
Also read the policy files in the policies/ directory — I want to
show the audience these are rules as code in the repo.
```

### Resultado esperado:

Claude Code muestra evaluaciones + lee `.rego` files:

```
policies/
├── block-unprotected-ai-endpoints.rego  → Bloquea si hay /ai/ endpoints sin auth
├── no-critical-findings.rego            → Bloquea si SAST tiene CRITICAL (CVSS ≥ 9.0)
├── slsa-attestation-required.rego       → Requiere SLSA L2 + cosign verification
└── security-scan-required.rego          → Requiere security scan stage completado
```

> **Talk Track:** *"Policies como código, en el repo, versionadas. La policy slsa-attestation-required verifica que el artefacto tiene SLSA Level 2 y firma cosign. Si no, el deploy se bloquea. No importa quién hace el merge."*

---

## PASO 5 — Canary Deployment (t=2:30)

> **Talk Track:** "Artefacto verificado en 3 capas, policies evaluadas. Ahora el canary."

### Prompt:

```
Show me the Canary Deployment progress. How many canary pods?
What happens after canary? What's the rollback plan?
```

### Resultado esperado:

```
Canary Deployment:
├── K8s Canary Deploy (2 pods)  ✅
├── Canary Delete               ✅
└── Rolling Deploy              ✅
Rollback: Canary Delete + Rolling Rollback (automático)
```

> **Talk Track:** *"2 pods canary con la nueva versión. Si fallan, se eliminan — cero downtime. Si pasan, rolling deployment completo."*

---

## PASO 6 — Verificar Deployment Live (t=3:30)

> **Talk Track:** "Deploy completado. Confirmemos desde el IDE."

### Prompt:

```
Verify the deployment is healthy:
1. Check pods in harnessbank-demo-end2end namespace
2. Confirm the image tag is the sequenceId, not latest
3. Hit http://demobank-e2e.selatam.harness-demo.site/health
4. Check /api/ai/status
```

### Resultado esperado:

```
Pods: running with image crizstian/harnessbank-demo:<sequenceId>
Health: {"status": "ok"}
AI Status: {"status": "active", "model": "demobank-assistant-v1"}
```

> **Talk Track:** "DemoBank live — imagen verificada por SBOM, SLSA, y firma de artefacto."

---

## PASO 7 — Cierre del Acto (t=4:00)

> **Talk Track:**
>
> *"Recapitulemos — todo desde el IDE:"*
>
> *"1. Mergeamos el PR — el único paso manual"*
> *"2. CI generó: SBOM, SLSA provenance, y artifact signing para cada imagen"*
> *"3. CD verificó: SBOM enforcement, SLSA verification, y artifact signature — las 3 en paralelo, ANTES de desplegar"*
> *"4. OPA policies validaron compliance — incluyendo SLSA L2 obligatorio"*
> *"5. Canary deployment con rollback automático"*
>
> **[pausa]**
>
> *"CI genera la cadena de confianza. CD la verifica. Si CI no firma, CD no despliega. Si CD no verifica, no hay rollout. Separación completa de responsabilidades."*

---

## Contingencia

Si la Supply Chain verification falla:

```
The Supply Chain verification failed in Deploy DemoBank.
Which step failed — SscaEnforcement, SlsaVerification, or
SscaArtifactVerification? What's the specific error?
```

Si el canary falla:

```
The canary deployment failed. Show me the failure reason and
whether the rollback executed.
```

---

## Checklist Pre-Demo

- [ ] PR #5 listo para merge
- [ ] Build and Deploy trigger habilitado
- [ ] GKE cluster accesible
- [ ] DemoBank URL respondiendo
- [ ] Claude Code con Harness MCP respondiendo
- [ ] SSCA policy set configurado en Harness
- [ ] Harness IDE Extension mostrando pipeline

---

## Transición al Acto 5

> **Talk Track:**
>
> *"El código está en producción. Construido, firmado, verificado, y desplegado."*
>
> **[pausa dramática]**
>
> *"Pero producción es donde empieza el verdadero riesgo. El AI banking assistant está expuesto al mundo. Y no todos los que lo usan tienen buenas intenciones."*
>
> *"¿Qué pasa cuando alguien intenta prompt injection? ¿Cuando enumera accounts? ¿Cuando descubre un zombie API?"*
>
> *"Para eso tenemos Traceable. Vamos al Acto 5."*
