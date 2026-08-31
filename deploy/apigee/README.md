# Apigee API Gateway — Demo Configuration

## Purpose in the Demo

Apigee sits as the API Gateway in front of DemoBank's public APIs.
It provides: rate limiting, API key validation, request schema validation,
and traffic analytics.

In Act 5, we demonstrate that even WITH an API Manager, the attack chain
succeeds because:

1. **Zombie API** (`/api/ai/status`) — NOT registered in Apigee → no policies
2. **Prompt Injection** — valid JSON passes schema validation → Apigee can't inspect semantic content
3. **Este-Oeste traffic** — MCP service call NEVER passes through Apigee → invisible
4. **Session correlation** — Apigee sees 4 independent requests → no attack chain detection

## Architecture

```
Internet → [Apigee Gateway] → [K8s Ingress] → [DemoBank API]
                                                     │
                                                     ├── /api/accounts  (registered in Apigee)
                                                     ├── /api/ai/chat   (registered in Apigee)
                                                     ├── /api/ai/status (NOT in Apigee → zombie)
                                                     ├── /api/admin     (registered in Apigee)
                                                     │
                                                     └──── E-W traffic ──→ [MCP Financial Data]
                                                           (NEVER passes through Apigee)
```

## Apigee Configuration

### Option A: Apigee X (GCP-native)

If using GCP, deploy Apigee X with:

```bash
# Create API proxy
gcloud apigee apis create demobank-api \
  --display-name="DemoBank API" \
  --proxy-bundle=./proxy-bundle.zip

# Deploy to environment
gcloud apigee apis deploy demobank-api \
  --environment=demo \
  --revision=1
```

### Option B: Apigee hybrid / Mock Gateway

For non-GCP environments, use a lightweight mock that demonstrates
the same limitation — any API gateway (Kong, AWS API GW, Azure APIM)
has the same blind spots.

### Endpoints Registered in Apigee

| Endpoint | Policy | Auth | Rate Limit |
|----------|--------|------|------------|
| `GET /api/accounts/` | API Key required | Yes | 100/min |
| `GET /api/accounts/{id}` | API Key required | Yes | 100/min |
| `POST /api/ai/chat` | API Key required | Yes | 30/min |
| `GET /api/admin/ping` | API Key + IP whitelist | Yes | 10/min |
| `GET /api/fx/` | Open | No | 500/min |

### Endpoints NOT Registered (the blind spot)

| Endpoint | Why not registered | Demo impact |
|----------|-------------------|-------------|
| `GET /api/ai/status` | Debug endpoint — never documented | Zombie API → attacker's entry point |
| `GET /api/accounts/{id}/details` | Added later, forgot to register | BOLA/IDOR without auth policy |
| `POST mcp-financial-data:5001` | Internal E-W traffic | Never touches the gateway |

## Demo Talk Track

See Act 5 — CISO #4 objection: "Ya estoy protegido, tengo Apigee/Kong como API Gateway"
