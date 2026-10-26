# Cobertura Demo vs Matriz Arquitectura Seguridad TI (27 req)

> Detalle requisito por requisito
> Tipo: **TEC** = capacidad técnica de plataforma | **NO-TEC** = certificación, SLA, infra SaaS, proceso, contractual

| # | Requisito | Tipo | Estado | Acto/Step |
|---|---|---|---|---|
| **Proteccion de Datos** | | | | |
| 1 | Cifrado AES-256 en reposo | NO-TEC | DOC | Harness Secret Manager AES-256-GCM, Google KMS |
| 2 | TLS 1.3/1.2 + RSA-2048 en transito | NO-TEC | DOC | TLS 1.3 default, mTLS para delegates |
| 3 | Verificacion de integridad (SHA-2/3) | TEC | DEMO | SLSA provenance + SBOM verification (Act 4) |
| 4 | Retencion y eliminacion segura | TEC | DOC | 6 meses ejecuciones, 2 anos audit trail |
| 5 | Respaldo cifrado con RTO/RPO | NO-TEC | DOC | Cloud SQL HA, DR multi-region, Git como backup |
| **Seguridad de Aplicaciones** | | | | |
| 6 | S-SDLC (SAST/DAST/SCA) | TEC | DEMO | SAST Semgrep + SCA + Secrets Detection (Act 2) |
| 7 | OWASP Top 10 | TEC | DEMO | OWASP CI/CD Risks en RSPM, Dependency-Check (Act 2) |
| 8 | Pentesting periodico | NO-TEC | DOC | trust.harness.io, certificaciones |
| 9 | Auditorias externas anuales | NO-TEC | DOC | SOC2 Type 2, ISO, trust.harness.io |
| **Supply Chain** | | | | |
| 10 | Gestion de terceros | TEC | DEMO | SBOM + SCA + dependency management (Act 4, Act 6) |
| 11 | Vulnerabilidades en OSS | TEC | DEMO | SCA con CVSS v3.1, requests==2.28.0 detectado (Act 2) |
| **IAM** | | | | |
| 12 | SSO con Microsoft Entra ID | TEC | UI | SAML config en Harness |
| 13 | RBAC granular (minimo privilegio) | TEC | UI | RBAC screens Account>Org>Project |
| 14 | Ciclo de vida de accesos (SCIM) | TEC | DOC | SCIM con Okta/Entra ID |
| 15 | OAuth 2.0 / OIDC / certificados | TEC | DOC | SAML, OAuth, LDAP, 2FA |
| **Perimetro** | | | | |
| 16 | WAF/WAAP + Anti-DDoS | TEC | DEMO | Traceable WAAP detect + block (Act 5, Act 7) |
| **Monitoreo y Deteccion** | | | | |
| 17 | Logs de seguridad detallados | TEC | DEMO | Audit Trail con actor, timestamp, accion (Act 2, 4) |
| 18 | SIEM forwarding (Syslog/API) | TEC | UI | Audit streaming config (Splunk, S3, GCS) |
| 19 | Retencion logs 30+ dias | TEC | DOC | 2 anos audit trail |
| **Compliance** | | | | |
| 20 | ISO 27001 | NO-TEC | DOC | trust.harness.io |
| 21 | ISO 27017 + 27018 | NO-TEC | DOC | trust.harness.io |
| 22 | SOC2 Type 2 | NO-TEC | DOC | trust.harness.io |
| 23 | ISO 22301 (continuidad) | NO-TEC | DOC | trust.harness.io |
| 24 | ISO 27701 / GDPR | NO-TEC | DOC | trust.harness.io |
| **Seguridad AI** | | | | |
| 25 | Proteccion modelos AI / datasets | TEC | DEMO | AIBOM + AI Discovery (Act 7) |
| 26 | No training con datos del cliente | NO-TEC | DOC | Zero Data Retention policy |
| 27 | AIMS (ISO 42001 / NIST AI RMF) | NO-TEC | DOC | Practicas documentadas, trust.harness.io |

## Resumen

| Estado | Total | TEC | NO-TEC |
|---|---|---|---|
| DEMO | 8 | 8 | 0 |
| UI | 3 | 3 | 0 |
| DOC | 16 | 4 | 12 |
| GAP | 0 | 0 | 0 |
| **Total** | **27** | **15 (56%)** | **12 (44%)** |

### Cobertura sobre capacidades tecnicas

| Metrica | Valor |
|---|---|
| Capacidades tecnicas | 15 |
| Demostradas (DEMO+UI) | 11 |
| **% cobertura tecnica** | **73%** |
| Faltantes TEC en DOC | 4 |

> Los 12 NO-TEC son certificaciones (ISO, SOC2), procesos del vendor (pentesting, auditorias), politicas (no training) e infra SaaS (cifrado, TLS, backups). Se responden con `trust.harness.io` y documentacion de arquitectura.

---

## Faltantes de Demostrar (4 capacidades tecnicas)

| # | Requisito | Estado | Promocion | Que mostrar | Esfuerzo |
|---|---|---|---|---|---|
| 4 | Retencion y eliminacion segura | DOC → UI | Pantalla | Entity Retention config + Audit Trail filtrado por fecha | 2 min |
| 14 | Ciclo de vida de accesos (SCIM) | DOC → UI | Pantalla | SCIM Providers en Access Control settings | 2 min |
| 15 | OAuth 2.0 / OIDC / certificados | DOC → UI | Pantalla | Authentication settings (SAML/OAuth/LDAP config) | 2 min |
| 19 | Retencion logs 30+ dias | DOC → UI | Pantalla | Audit Trail → filtrar 6+ meses atras, mostrar retencion 2 anos | 2 min |

**Con estas 4 promociones: 15/15 = 100% de capacidades tecnicas cubiertas.**
