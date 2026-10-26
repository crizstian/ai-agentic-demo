# Cobertura Demo vs Matriz Arquitectura TI (98 req)

> Detalle requisito por requisito
> Tipo: **TEC** = capacidad técnica de plataforma | **NO-TEC** = certificación, SLA, infra SaaS, proceso, contractual

## 1. Arquitectura de Solucion (22 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 1.1 | SLAs de atencion a incidentes | NO-TEC | DOC | Soporte enterprise P0-P4 |
| 1.2 | Documentacion tecnica (diagramas, APIs) | TEC | DOC | apidocs.harness.io, developer.harness.io |
| 1.3 | Buenas practicas de arquitectura | NO-TEC | DOC | Microservicios cloud-native en GCP |
| 1.4 | Facturacion por componente | NO-TEC | DOC | Developer 360 + Flex Pricing |
| 1.5 | Soporte en implementacion | NO-TEC | DOC | Soporte enterprise dedicado |
| 1.6 | GDPR/CCPA | NO-TEC | DOC | FF GDPR compliant, Zero Data Retention |
| 1.7 | PCI Compliance | NO-TEC | DOC | Read-only root filesystem, delegates aislados |
| 1.8 | OWASP Top 10 | TEC | DEMO | OWASP CI/CD Risks en RSPM, SCA integrado (Act 2) |
| 1.9 | HA >= 99.9% | NO-TEC | DOC | 99.9% SLA multi-region |
| 1.10 | Escalado vertical automatico | NO-TEC | DOC | SaaS GCP auto-gestionado |
| 1.11 | Escalado horizontal automatico | TEC | DEMO | HPA en delegates GKE (visible en demo) |
| 1.12 | Escalado por carga planificada | TEC | DOC | HPA + Cluster Orchestrator |
| 1.13 | Contingencia multi-region | NO-TEC | DOC | Dual-region GCP |
| 1.14 | Monitoreo y alertas | TEC | DEMO | Delegate heartbeat, CV, AI SRE notifications (Act 6) |
| 1.15 | DR plan con RTO | NO-TEC | DOC | Multi-region, Cloud SQL HA |
| 1.16 | Cifrado de intercambios | NO-TEC | DOC | AES-256 + TLS 1.3 |
| 1.17 | Replicacion HA | NO-TEC | DOC | Cloud SQL replicas sincronas |
| 1.18 | Hardware requerido | NO-TEC | DOC | SaaS (delegate ~200MB como pod K8s) |
| 1.19 | Integracion SIEM | TEC | UI | Audit streaming a Splunk/S3 |
| 1.20 | Updates sin downtime | TEC | DEMO | Rolling + Canary + Blue-Green nativos (Act 4) |
| 1.21 | Region cercana a Peru | NO-TEC | DOC | us-west, delegate en cualquier region |
| 1.22 | Multi-tenant vs single-tenant | NO-TEC | DOC | Multi-tenant con aislamiento logico, SMP disponible |

**Seccion 1: TEC=7, NO-TEC=15**

## 2. Arquitectura de Integracion (18 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 2.1 | APIs REST JSON | TEC | DEMO | Harness REST API usada via MCP (todos los actos) |
| 2.2 | OAuth2/OIDC/SAML | TEC | DOC | OAuth 2.0, SAML 2.0, OIDC |
| 2.3 | Token expiration configurable | TEC | DOC | API keys 30/90/180 dias/custom |
| 2.4 | Sync/async + eventos | TEC | DEMO | REST sync + webhooks async (AI SRE, triggers) |
| 2.5 | Integracion masiva | TEC | DOC | APIs paginadas hasta 10,000 items |
| 2.6 | Batch SFTP por VPN | NO-TEC | DOC | Delegates + VPN |
| 2.7 | Integraciones directas/indirectas | TEC | DEMO | 150+ integraciones (Jira, Docker, K8s en demo) |
| 2.8 | Cache (Redis, etc.) | TEC | DOC | FF Relay Proxy, Cache Intelligence |
| 2.9 | Baja latencia (P50/P90/P99) | NO-TEC | DOC | Performance reports publicados |
| 2.10 | Tiempos de respuesta < 5s | NO-TEC | DOC | Performance reports |
| 2.11 | Max peticiones concurrentes | NO-TEC | DOC | 5000 req/10s por IP |
| 2.12 | Entornos de pruebas | TEC | DEMO | Pipelines con multiples environments (Act 4) |
| 2.13 | Conector a Core Bancario | TEC | GAP | Delegate + HTTP step + VPN (narrativa) |
| 2.14 | Reintentos y persistencia | TEC | DEMO | Failure strategies: Retry con backoff (Act 4 healthcheck) |
| 2.15 | Sync desde multiples origenes | TEC | DOC | SCIM, GitOps, connectors multi-repo |
| 2.16 | Ancho de banda minimo | NO-TEC | DOC | HTTPS estandar, gzip |
| 2.17 | Versionado de APIs | TEC | DOC | OpenAPI v3.0, SemVer SDKs |
| 2.18 | Rate limiting y throttling | TEC | DOC | 5000 req/10s, HTTP 429 |

**Seccion 2: TEC=13, NO-TEC=5**

## 3. Arquitectura de Aplicaciones (16 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 3.1 | Usuarios concurrentes | NO-TEC | DOC | SaaS cloud-native escalable |
| 3.2 | Resiliencia ante volumen | TEC | DOC | Resilience Testing (Chaos+Load+DR) |
| 3.3 | Dashboard de metricas | TEC | DEMO | DORA metrics dashboard (mostrable) |
| 3.4 | Health Check / monitoreo | TEC | DEMO | Delegate heartbeat, Portal Healthcheck step (Act 4) |
| 3.5 | Alertas multicanal | TEC | DEMO | AI SRE notifications Slack/email/webhook (Act 6) |
| 3.6 | Logs + integracion herramientas | TEC | DEMO | Audit trail + streaming (Splunk, S3) |
| 3.7 | Usuarios nominales + Entra ID | TEC | UI | SAML SSO + SCIM config |
| 3.8 | TLS 1.2+ | NO-TEC | DOC | TLS 1.3 default |
| 3.9 | Balanceo de carga | TEC | DOC | GCP Cloud LB, FF Relay Proxy |
| 3.10 | RBAC minimo privilegio | TEC | UI | RBAC config screens |
| 3.11 | Versionado y compatibilidad | TEC | DOC | SemVer, backward compatibility |
| 3.12 | Licencias OSS compatibles | NO-TEC | DOC | SDKs Apache 2.0/MIT |
| 3.13 | Gestion dependencias (SBOM) | TEC | DEMO | SBOM generation + SCA (Act 4, Act 6) |
| 3.14 | SDKs multi-lenguaje | TEC | DEMO | Feature Flags SDK JS + Python en demo |
| 3.15 | SDK SemVer + deprecation | TEC | DOC | 12 meses soporte post-release |
| 3.16 | SDK documentacion | TEC | DOC | developer.harness.io |

**Seccion 3: TEC=13, NO-TEC=3**

## 4. Arquitectura de Datos (10 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 4.1 | Gestion segura de secretos | TEC | DEMO | Harness Secret Manager, secrets.getValue() (Act 2, 4) |
| 4.2 | Politicas de backups | NO-TEC | DOC | Cloud SQL HA + DR + Velero |
| 4.3 | Cifrado reposo + transito | NO-TEC | DOC | AES-256 + TLS 1.3 |
| 4.4 | No PII en logs | TEC | DEMO | Secret masking automatico en logs (Act 2) |
| 4.5 | DR de base de datos | NO-TEC | DOC | Cloud SQL HA + point-in-time recovery |
| 4.6 | Exportacion a DWH/S3 | TEC | UI | Audit streaming config |
| 4.7 | Enmascaramiento PII | TEC | DEMO | FF GDPR, secret masking (visible en demo) |
| 4.8 | Almacenamiento datos historicos | TEC | DOC | 2 anos audit trail |
| 4.9 | Escalado de almacenamiento | NO-TEC | DOC | SaaS auto-escalado |
| 4.10 | Retencion/eliminacion + GDPR | TEC | DOC | Entity retention configurable |

**Seccion 4: TEC=6, NO-TEC=4**

## 5. Otros Puntos / Capacidades (32 req)

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| 5.1 | CI/CD nativo | TEC | DEMO | Pipeline completo CI+CD (Acts 2-4) |
| 5.2 | Cross-repo multi-artefacto | TEC | DEMO | 2 Docker images, 2 services (Act 4) |
| 5.3 | Extensibilidad terceros | TEC | DEMO | 150+ integraciones usadas en demo |
| 5.4 | Infra cloud-native | TEC | DEMO | K8s GKE deployments (Act 4) |
| 5.5 | Despliegue modular | NO-TEC | DOC | Modular licensing |
| 5.6 | IaC provisioning | TEC | DOC | IaCM module |
| 5.7 | Shift-Left Security | TEC | DEMO | SAST+SCA+Secrets en PR pipeline (Act 2) |
| 5.8 | Supply Chain Security | TEC | DEMO | SBOM+SLSA+Signing+Verification (Act 4) |
| 5.9 | Runtime Security | TEC | DEMO | Traceable WAAP detect+block (Act 5, 7) |
| 5.10 | IGA integration | TEC | DOC | SCIM 2.0 |
| 5.11 | Automatizacion de cumplimiento | TEC | DEMO | OPA Policy as Code (Act 6) |
| 5.12 | Templates y estandares | TEC | UI | Template Library |
| 5.13 | Aplicacion de politicas | TEC | DEMO | OPA enforce + Jira Approval (Act 4, 6) |
| 5.14 | Visibilidad toolchain | TEC | UI | SEI module |
| 5.15 | Infraestructura gobernanza | TEC | DEMO | RBAC + OPA + Audit Trail (Acts 4, 6) |
| 5.16 | Deuda tecnica | TEC | UI | SCA + STO scanners |
| 5.17 | Portal interno desarrolladores | TEC | UI | IDP (Backstage-based) |
| 5.18 | UI ergonomica | TEC | DEMO | Pipeline Studio visual (visible en demo) |
| 5.19 | Reduccion fricciones | TEC | DEMO | Test Intelligence + Cache Intelligence + AIDA (Act 2) |
| 5.20 | Flujos agiles | TEC | DEMO | Pipeline Studio + Jira Approval + triggers (Acts 1-4) |
| 5.21 | Gestion artefactos | TEC | DEMO | Docker Hub push + verification (Act 4) |
| 5.22 | Encapsulacion dependencias | TEC | DEMO | Pipeline Chaining via webhook (Act 4) |
| 5.23 | Trazabilidad y procedencia | TEC | DEMO | SLSA + SBOM + Chain of Custody (Act 4, 6) |
| 5.24 | Integracion registros contenedores | TEC | DEMO | Docker Hub Build and Push (Act 4) |
| 5.25 | Metricas DORA | TEC | UI | DORA dashboard en CD module |
| 5.26 | Metricas DX | TEC | UI | SEI developer productivity |
| 5.27 | Telemetria y gestion errores | TEC | DEMO | Logs drill-down + AIDA + AI Remediation (Act 4) |
| 5.28 | Medicion del valor | TEC | UI | DORA + SEI + CCM |
| 5.29 | DataOps (DB changes) | TEC | DOC | Database DevOps module |
| 5.30 | Gobernanza | TEC | DEMO | OPA + Audit Trail + RBAC (Act 6) |
| 5.31 | Retroalimentacion CI | TEC | DEMO | Status checks en PR + Console View (Act 2) |
| 5.32 | DevSecOps | TEC | DEMO | STO 40+ scanners + SCS + OPA (Acts 2-7) |

**Seccion 5: TEC=31, NO-TEC=1**

---

## Resumen Arquitectura TI

| Seccion | Total | TEC | NO-TEC | Demo | UI | Doc | Gap |
|---|---|---|---|---|---|---|---|
| 1. Solucion | 22 | 7 | 15 | 4 (18%) | 1 | 17 | 0 |
| 2. Integracion | 18 | 13 | 5 | 5 (28%) | 0 | 12 | 1 |
| 3. Aplicaciones | 16 | 13 | 3 | 6 (38%) | 2 | 8 | 0 |
| 4. Datos | 10 | 6 | 4 | 3 (30%) | 1 | 6 | 0 |
| 5. Capacidades | 32 | 31 | 1 | 21 (66%) | 7 | 4 | 0 |
| **Total** | **98** | **70 (71%)** | **28 (29%)** | **39 (40%)** | **11 (11%)** | **47 (48%)** | **1 (1%)** |

### Cobertura sobre capacidades tecnicas

| Metrica | Valor |
|---|---|
| Capacidades tecnicas | 70 |
| Demostradas (DEMO+UI) | 50 |
| **% cobertura tecnica** | **71%** |
| Faltantes TEC en DOC | 19 |
| Faltantes TEC en GAP | 1 |

> Los 28 NO-TEC son SLAs (1.1, 1.9), compliance (1.6, 1.7), infra SaaS (cifrado, HA, DR, hardware, region), specs de performance (latencia, ancho de banda, concurrencia), modelo comercial (facturacion, soporte) y conectividad (SFTP/VPN). Se responden con documentacion tecnica y contractual.

---

## Faltantes de Demostrar (20 capacidades tecnicas)

### Promocion facil: DOC → UI (mostrar pantalla, ~2 min c/u)

| # | Requisito | Que mostrar |
|---|---|---|
| 1.2 | Documentacion tecnica | Abrir apidocs.harness.io → API reference live |
| 2.2 | OAuth2/OIDC/SAML | Authentication settings en Harness (SAML/OAuth config) |
| 2.3 | Token expiration configurable | API Key creation → dropdown de expiracion |
| 2.5 | Integracion masiva | API Explorer → paginacion pageSize, pageIndex |
| 2.15 | Sync desde multiples origenes | SCIM Providers + GitOps connectors en UI |
| 2.17 | Versionado de APIs | Link a OpenAPI spec v3.0 en apidocs |
| 3.9 | Balanceo de carga | FF Relay Proxy config screen |
| 3.16 | SDK documentacion | developer.harness.io/docs/feature-flags/ff-sdks |
| 4.8 | Almacenamiento datos historicos | Audit Trail → filtrar por fecha, mostrar retencion 2 anos |
| 4.10 | Retencion/eliminacion + GDPR | Entity Retention config screen |
| 5.6 | IaC provisioning | IaCM module overview screen |
| 5.10 | IGA integration | SCIM setup screen en Access Control |
| 5.29 | DataOps (DB changes) | DB DevOps module overview screen |

### Promocion media: DOC → DEMO (micro-adicion al flow)

| # | Requisito | Que agregar al demo |
|---|---|---|
| 1.12 | Escalado por carga planificada | `kubectl get hpa -n harnessbank-demo-end2end` durante Act 4 |
| 2.8 | Cache (Redis, etc.) | Mostrar Cache Intelligence hit ratio en pipeline logs |
| 2.18 | Rate limiting y throttling | Ya existe en Act 7 (Traceable Rate Limiting) — reclasificar a DEMO |
| 3.11 | Versionado y compatibilidad | `npm info @harnessio/ff-javascript-client-sdk versions` |
| 3.15 | SDK SemVer + deprecation | Mostrar changelog del SDK con versiones en GitHub releases |
| 3.2 | Resiliencia ante volumen | Mencionar Resilience Testing module con screenshot |

### GAP a cerrar

| # | Requisito | Solucion |
|---|---|---|
| **2.13** | Conector a Core Bancario | Mostrar HTTP Step en pipeline con Delegate → VPN connectivity. Narrativa: "El delegate corre dentro de su VPC, conecta via VPN al core bancario sin exponer APIs." |

**Con todas las promociones + cierre de GAP: 70/70 = 100% de capacidades tecnicas cubiertas.**
