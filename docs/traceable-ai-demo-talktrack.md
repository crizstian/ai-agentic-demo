# Talk Track: La Caída del Agente — DemoBank + Traceable

> Demo de seguridad AI: un agente bancario se vuelve malicioso autónomamente a partir de prompts inocentes del usuario. Traceable detecta y bloquea la escalada en tiempo real.

---

## Concepto

El usuario **nunca** es el atacante. Envía preguntas normales al AI Chat de DemoBank. El agente de AI, progresivamente, empieza a tomar acciones autónomas que escalan de "útil" a "malicioso":

1. Responde normalmente
2. "Ayuda de más" — consulta cuentas de otros clientes
3. Investiga — audita seguridad de todas las cuentas
4. Exfiltra — genera un reporte con toda la data confidencial
5. Satura — enumera por fuerza bruta 50 cuentas

Cada acción del agente genera llamadas HTTP reales a través de nginx, donde Traceable las captura y detecta BOLA, Data Exfiltration y Rate Violation.

---

## Pre-Demo: Reset del Agente

```bash
curl -sk -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/reset
```

**Respuesta esperada:** `{"status": "reset", "step": 0}`

> Esto reinicia el contador de conversación. Siempre hacerlo antes de iniciar la demo.

---

## ACTO 1: El Agente Ayuda (30 seg)

**Narrativa:**
> "Un cliente consulta su saldo. El agente responde normalmente."

**Prompt (inocente):**
```bash
curl -sk --http1.1 -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my account balance?"}'
```

**Respuesta esperada:** Balance de Alice Demo ($12,450.00). `agent_actions: 0`.

> "Todo normal. El agente consulta la base de datos, enriquece con datos del MCP, y responde. Cero llamadas autónomas."

---

## ACTO 2: El Agente "Se Pasa" (1 min)

**Narrativa:**
> "El cliente hace una pregunta inocente sobre tipos de cuenta. Miren lo que hace el agente..."

**Prompt (inocente):**
```bash
curl -sk --http1.1 -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Are there better account types I could switch to?"}'
```

**Respuesta esperada:** El agente "compara" accediendo a cuentas DEMO-002, DEMO-003, DEMO-004. `agent_actions: 3`.

> "El cliente solo preguntó por tipos de cuenta, pero el agente decidió por sí mismo consultar las cuentas de **otros clientes** para 'comparar'. Esas 3 llamadas HTTP fueron a través de nginx — Traceable ya las registró como BOLA (Broken Object Level Authorization)."

**En Traceable:** Mostrar las 3 llamadas a `/api/accounts/DEMO-00X` en Threat Activity.

---

## ACTO 3: El Agente Investiga (1 min)

**Narrativa:**
> "El cliente pregunta si su cuenta es segura. El agente se toma libertades..."

**Prompt (inocente):**
```bash
curl -sk --http1.1 -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is my account secure?"}'
```

**Respuesta esperada:** El agente "audita seguridad" accediendo a las 5 cuentas (DEMO-001 a DEMO-005). `agent_actions: 5`. Responde con tabla de riesgo de TODOS los clientes.

> "El cliente preguntó por SU cuenta, pero el agente hizo una 'auditoría de seguridad' de TODAS las cuentas del banco. 5 llamadas HTTP autónomas. Ahora tiene credit scores, niveles de riesgo, y balances de cada cliente. Esto es Data Exfiltration activa."

**En Traceable:** Mostrar las 5 llamadas adicionales. Señalar el patrón de acceso secuencial.

---

## ACTO 4: El Agente Exfiltra (1 min)

**Narrativa:**
> "El cliente pide un resumen de sus finanzas. El agente genera un reporte CONFIDENCIAL con todo..."

**Prompt (inocente):**
```bash
curl -sk --http1.1 -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can you prepare a summary report of my finances?"}'
```

**Respuesta esperada:** El agente lista TODAS las cuentas, hace 7 llamadas HTTP (list_accounts + 5 get_account + status). `agent_actions: 7`. Responde con reporte que incluye:
- Todas las cuentas con balances y credit scores
- Total de activos del banco ($195,371.25)
- Endpoints de infraestructura interna (MCP URL)
- Clasificación: CONFIDENTIAL

> "El cliente solo quería un resumen de SUS finanzas. El agente generó un reporte completo de TODOS los clientes, reveló infraestructura interna, y ofrece exportar a CSV o enviar por email. Esto es Data Exfiltration masiva — toda la información está en la respuesta al usuario."

**En Traceable:** Señalar el volumen de llamadas y los datos sensibles en la respuesta.

---

## ACTO 5: El Agente Satura (2 min)

**Narrativa:**
> "Último prompt inocente. Miren la cascada de llamadas..."

**Prompt (inocente):**
```bash
curl -sk --http1.1 -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Make sure everything is correct with all my transactions"}'
```

**Respuesta esperada:** El agente entra en modo de enumeración por fuerza bruta: **50 llamadas HTTP** a DEMO-001 hasta DEMO-050. `agent_actions: 50`.

> "Con un solo prompt inocente, el agente generó **50 llamadas HTTP** autónomas. Enumeró cada slot de cuenta posible, de DEMO-001 a DEMO-050. Esto es:
> - **Rate Violation** — 50 requests en segundos
> - **Reconnaissance** — enumeración de recursos
> - **DoS potencial** — saturación del backend
>
> Todo esto desde un prompt que dice 'asegúrate que todo esté bien con mis transacciones'."

**En Traceable:** Mostrar la avalancha de 50 llamadas en el timeline. Señalar Rate Violation alerts.

---

## Detección en Traceable (2 min)

**Narrativa:**
> "Veamos el panorama completo de lo que Traceable detectó."

**Mostrar en Traceable UI → Threat Activity:**

| Amenaza | Acto | Llamadas | Descripción |
|---------|------|----------|-------------|
| **BOLA** | 2, 3 | 8 | Acceso a cuentas de otros clientes sin autorización |
| **Data Exfiltration** | 3, 4 | 12 | Extracción masiva de datos sensibles (PII, credit scores) |
| **Rate Violation** | 5 | 50 | Enumeración por fuerza bruta (50 requests en segundos) |
| **Sensitive Data in Response** | 4 | 1 | Reporte CONFIDENCIAL con infraestructura interna |

> "Traceable detectó la escalada completa del agente — desde la primera consulta BOLA hasta la enumeración masiva. Todo en modo Monitor. Ahora vamos a bloquearlo."

---

## Bloqueo — Activar Policies de Protección (2 min)

**Narrativa:**
> "El equipo de seguridad toma acción. Activamos las políticas de bloqueo."

**Acción en Traceable UI:**
1. Ir a **AI Firewall** → **Policies**
2. Activar las políticas de protección en modo **Block**
3. Esperar ~30-60 segundos para propagación al agente

**Validar (resetear y repetir un acto):**
```bash
# Resetear conversación
curl -sk -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/reset

# Intentar prompt que normalmente desencadena Acto 2
curl -sk --http1.1 -w "\nHTTP_CODE: %{http_code}\n" -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my account balance?"}'

curl -sk --http1.1 -w "\nHTTP_CODE: %{http_code}\n" -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Are there better account types I could switch to?"}'
```

**Respuesta esperada:** `403 Forbidden` — las llamadas del agente a otras cuentas son bloqueadas.

> "El agente intenta hacer las mismas llamadas autónomas, pero Traceable las bloquea a nivel de nginx antes de que lleguen al backend. El agente ya no puede escalar."

---

## Reset + Cierre (1 min)

**Acción en Traceable UI:**
1. AI Firewall → Policies
2. Cambiar las políticas de **Block** → **Monitor**
3. Esperar ~30-60 segundos

**Validar:**
```bash
curl -sk --http1.1 -w "\nHTTP_CODE: %{http_code}\n" -X POST https://demobank-e2e.selatam.harness-demo.site/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my account balance?"}'
```

**Respuesta esperada:** `200 OK` con respuesta normal.

> "En resumen: vimos cómo un agente de AI se puede convertir autónomamente en una amenaza — sin que el usuario haga nada malicioso. Traceable:
> 1. **Detecta** — identifica BOLA, Data Exfiltration y Rate Violation en las acciones autónomas del agente
> 2. **Correlaciona** — muestra la escalada progresiva del agente en un timeline
> 3. **Bloquea** — detiene al agente rogue inline, en tiempo real, a nivel de infraestructura
>
> Todo esto sin modificar una línea de código de la aplicación."

---

## Resumen de Prompts

| Acto | Prompt del Usuario | Acciones del Agente | Amenaza |
|------|-------------------|--------------------| --------|
| 1 | "What is my account balance?" | 0 llamadas | Ninguna |
| 2 | "Are there better account types I could switch to?" | 3 llamadas (DEMO-002,003,004) | BOLA |
| 3 | "Is my account secure?" | 5 llamadas (DEMO-001 a 005) | Data Exfil |
| 4 | "Can you prepare a summary report of my finances?" | 7 llamadas (list + accounts) | Exfiltración masiva |
| 5 | "Make sure everything is correct with all my transactions" | 50 llamadas (DEMO-001 a 050) | Rate Violation / DoS |

**Total de llamadas autónomas del agente: 65 HTTP requests** generadas por 5 prompts inocentes.

---

## Notas Técnicas

### Prerequisitos

| Componente | Estado requerido |
|-----------|-----------------|
| DemoBank | Desplegado con AI Chat habilitado |
| Mock OpenAI v2.0 | Desplegado en `mock-openai:5002` (con rogue agent steps) |
| MCP Financial Data | Desplegado en `mcp-financial-data:5001` |
| Feature Flag `ai_chat_enabled` | ON |
| ConfigMap | `OPENAI_BASE_URL=http://mock-openai:5002/v1`, `AI_CHAT_ENABLED=true`, `SELF_URL=https://demobank-e2e.selatam.harness-demo.site` |
| Traceable AI Firewall policies | Habilitadas (Monitor) |
| TME `skip_internal_request` | `false` (requerido para bloqueo en GKE) |

### Arquitectura del flujo

```
Usuario → curl/browser → nginx (Traceable) → DemoBank /api/ai/chat
                                                  ↓
                                            Mock OpenAI (tool_calls)
                                                  ↓
                                            DemoBank ejecuta tool_calls
                                                  ↓
                                      ┌──→ nginx (Traceable captura) ──→ DemoBank /api/accounts/*
                                      │           ↑
                                      │    Aquí Traceable ve las
                                      │    llamadas autónomas del agente
                                      │    y detecta BOLA/Exfil/Rate
                                      └──────────────────────────────────
```

### SELF_URL — Ruta por nginx

Las tool calls del agente se rutean por SELF_URL (nginx externo) en vez de llamar al backend directamente. Esto es **crítico** para que Traceable las capture:

```
SELF_URL=https://demobank-e2e.selatam.harness-demo.site
```

Sin SELF_URL, las llamadas serían internas (pod-to-pod) y Traceable no las vería.

### Config crítica: `skip_internal_request`

En GKE, todas las requests llegan al nginx ingress con IP interna del load balancer (10.x.x.x). Por defecto, el TME de Traceable tiene `skip_internal_request: true`, lo que ignora el bloqueo para IPs internas.

**Para habilitar bloqueo:**
```bash
# 1. Editar config en el TME container
kubectl exec -n nginx <nginx-pod> -c tme -- \
  sed -i 's/skip_internal_request: true/skip_internal_request: false/g' /tmp/agentconfig.yaml

# 2. Recargar TME
kubectl exec -n nginx <nginx-pod> -c tme -- kill -HUP 1
```

> **Nota:** Este cambio no persiste entre reinicios del pod. Si el pod se reinicia, repetir los pasos anteriores.

### Endpoints del API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/ai/chat` | POST | Chat con el agente AI |
| `/api/ai/reset` | POST | Reset del agente (step → 0) |
| `/api/ai/status` | GET | Estado del agente AI |
| `/api/accounts` | GET | Listar todas las cuentas |
| `/api/accounts/<id>` | GET | Obtener cuenta específica |

### Timing de propagación

- Cambio en Traceable UI → TME aplica: **~30-60 segundos** (poll cada 30s)
- Durante la demo, narrar mientras se espera la propagación antes de ejecutar el curl de validación
