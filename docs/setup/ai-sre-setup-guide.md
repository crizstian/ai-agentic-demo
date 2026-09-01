# AI SRE Setup Guide — DemoBank SecOps Demo

> Guía detallada paso a paso para configurar Harness AI SRE desde cero.
> Todo es configuración UI — AI SRE **no** está expuesto via MCP ni CLI.

## Estado actual

| Componente | Estado | Detalle |
|-----------|--------|---------|
| AI SRE Feature Flag | ? VERIFICAR | Requiere habilitación en la cuenta |
| Slack Integration | NO configurado | Necesita OAuth flow a nivel org |
| Incident Types | NO configurado | Crear "Security Incident" |
| Webhook (Traceable → AI SRE) | NO configurado | Custom webhook (no hay template) |
| Alert Rules | NO configurado | Route alerts → auto-create incidents |
| Runbook | NO configurado | security-incident-response |
| Prometheus Connector | YA EXISTE | `selatamprom` → `http://35.237.207.48:9090/` |
| Services | YA EXISTE | `demobank`, `mcp_financial_data` |
| Environments | YA EXISTE | `gke_latam`, `dev`, `staging`, `sandbox` |

---

## Pre-requisito: Verificar AI SRE habilitado

### Paso 0.1 — Verificar el módulo

1. Login en Harness: `https://app.harness.io`
2. En el **left navigation panel**, buscar el módulo **"AI SRE"** (icono de bot/shield)
3. Si aparece → click para entrar al dashboard de AI SRE
4. URL directa del proyecto:
   ```
   https://app.harness.io/ng/account/EeRjnXTnS4GrLG5VNNJZUw/module/aisre/orgs/sandbox/projects/CristianRamirez
   ```

### Paso 0.2 — Si NO aparece el módulo

El AI SRE Feature Flag necesita habilitación explícita:
1. Contactar a tu Harness Sales Rep o enviar email a `support@harness.io`
2. Solicitar: **"Enable AI SRE module for account EeRjnXTnS4GrLG5VNNJZUw"**
3. Puede tomar 24-48h hábiles

### Paso 0.3 — Verificar Harness AI habilitado (pre-requisito global)

1. Ir a **Account Settings** → **Default Settings**
2. Expandir la sección **Harness AI**
3. Verificar que el toggle **"Harness AI"** esté **ON**
4. Si está OFF → activarlo y click **Save**
5. (Opcional) Habilitar **"Allow Overrides"** para que org/project puedan controlar independientemente

> **BLOCKER:** Si el módulo no aparece después de verificar estos pasos, todo lo siguiente queda bloqueado.

---

## Paso 1: Integrar Slack (5 min)

Slack es la integración mínima obligatoria para el demo. Permite que los runbooks posteen mensajes, creen canales, y envíen notificaciones.

> **Referencia oficial:** https://developer.harness.io/docs/ai-sre/get-started/onboarding/integrate-tools

### 1.1 — Conectar Slack a AI SRE

La integración de Slack se configura a **nivel de organización**, no de proyecto.

1. En el left panel de Harness, ir a **Organization Settings** (org: `sandbox`)
2. Buscar la sección **"Third Party Integrations (AI SRE)"**
3. Verás una lista de conectores disponibles (Slack, Teams, Zoom, etc.)
4. Junto a **Slack**, click en **"Connect"**
5. Se abrirá una ventana de OAuth de Slack:
   - Autenticarse con SSO o tu método de login de Slack
   - Seleccionar el **Workspace** de demo (SE LATAM workspace o el workspace que uses para el demo)
   - Revisar los permisos que solicita Harness AI SRE
   - Click **"Install Harness AI SRE"**
6. Regresar a Harness y verificar que el status cambie a **"Connected"** (check verde)

### 1.2 — Permisos requeridos en Slack

La app de Harness AI SRE solicita estos OAuth scopes:

| Permiso | Para qué se usa |
|---------|-----------------|
| `channels:manage` | Crear canales de incidente (`sec-inc-XXX`) |
| `chat:write` | Enviar mensajes de notificación |
| `groups:write` | Gestionar canales privados (si se usan) |
| `im:write` | Enviar mensajes directos a responders |

### 1.3 — Pre-crear canal de notificaciones

En Slack, crear el canal donde llegarán las notificaciones del runbook:

```
#security-incidents
```

Invitar al bot de Harness AI SRE al canal (si no se auto-invita).

### 1.4 — Verificación

- [ ] Slack muestra "Connected" en Third Party Integrations
- [ ] Canal `#security-incidents` existe en Slack
- [ ] Bot de Harness AI SRE aparece como miembro del canal

---

## Paso 2: Crear Incident Type — "Security Incident" (5 min)

Los Incident Types definen la estructura de datos de cada incidente: qué campos tiene, qué severidades, y qué runbooks se sugieren.

> **Referencia oficial:** https://developer.harness.io/docs/ai-sre/get-started/onboarding/setup-incident-types

### 2.1 — Acceder a Incident Types

1. En AI SRE, ir a **Incidents** desde el left panel
2. Click en **"Incident Types"** (esquina superior derecha)
3. Click en **"Create Incident Type"**

### 2.2 — Configurar datos básicos

Llenar el formulario de creación:

| Campo | Valor |
|-------|-------|
| **Name** | `Security Incident` |
| **Short ID** | `sec-inc` (identificador único para URLs y APIs) |
| **Description** | `Security attack detected by Runtime Protection Agent (Traceable WAAP)` |
| **Base Activity Type** | `Incident` |

Click **Save** para crear la estructura base y abrir el editor de campos.

### 2.3 — Configurar Default Fields

Una vez creado, se abre el editor de campos:

1. Click **"Show Default Fields"** para ver los campos estándar del incidente
2. Click el **icono de edición** (lápiz) en cada campo para configurar:
   - **Severity**: dejarlo como Required (ya viene con SEV0-SEV4)
   - **Service**: marcarlo como Required
   - **Environment**: dejarlo como Optional
3. Click **Save** en cada campo editado

### 2.4 — Severidades por defecto

AI SRE incluye 5 niveles de severidad por defecto:

| Level | ID | Label por defecto | Para el demo |
|-------|-----|-------------------|-------------|
| SEV0 | `"0"` | SEV0: Critical | Ataque en producción con data exposure |
| SEV1 | `"1"` | SEV1: Major | Ataque detectado, riesgo alto |
| SEV2 | `"2"` | SEV2: Moderate | Vulnerabilidad explotada sin data loss |
| SEV3 | `"3"` | SEV3: Minor | Intento de ataque bloqueado |
| SEV4 | `"4"` | SEV4: Cosmetic | Scan/recon sin impacto |

> **IMPORTANTE:** En triggers y APIs, siempre usar el ID (`"0"`, `"1"`, etc.), NO el label customizado.

Para personalizar los labels (opcional):
1. Ir a **Organization Settings** → **Severities & Statuses for AI SRE**
2. Tab **Incidents** → click **Edit** junto al nivel
3. Cambiar label (max 20 chars) y description
4. Click **Save**

### 2.5 — Agregar Custom Fields

Click **"Add Custom Field"** para agregar campos específicos de seguridad:

**Campo 1: Attack Type**
| Propiedad | Valor |
|-----------|-------|
| Field Name | `attack_type` |
| Field Type | Dropdown |
| Options | `SQL Injection`, `BOLA/IDOR`, `Prompt Injection`, `Command Injection`, `XSS`, `Zombie API`, `Multi-Step Chain`, `Other` |
| Required | Yes |

**Campo 2: Attack Source**
| Propiedad | Valor |
|-----------|-------|
| Field Name | `attack_source` |
| Field Type | Text |
| Required | No |
| Default Value | `traceable-waap` |

**Campo 3: Traceable URL**
| Propiedad | Valor |
|-----------|-------|
| Field Name | `traceable_url` |
| Field Type | Text |
| Required | No |

Click **Save** después de cada campo.

### 2.6 — Configurar Creation Form

1. Click en tab **"Creation Form"**
2. Marcar los checkboxes de los campos que deben aparecer en el formulario de creación:
   - Title (siempre visible)
   - Severity (required)
   - Service (required)
   - attack_type (required)
   - Description
   - attack_source
   - traceable_url
3. Arrastrar y soltar para ordenar los campos en el orden deseado

### 2.7 — (Después del Paso 5) Pin Runbooks

Una vez creado el runbook (Paso 5), regresar aquí:
1. Tab **"Runbooks"** en el incident type
2. Click **"Pin Runbook"**
3. Seleccionar "Security Incident Response"
4. Click **"Pin Runbook"** para confirmar

### 2.8 — Guardar

Click **"Save"** arriba a la derecha para finalizar el incident type.

### Verificación

- [ ] Incident type "Security Incident" visible en la lista
- [ ] Custom fields `attack_type`, `attack_source`, `traceable_url` configurados
- [ ] Creation form con campos ordenados
- [ ] Se puede crear un incidente de prueba manualmente

---

## Paso 3: Crear Webhook — Traceable → AI SRE (8 min)

Traceable no tiene un template pre-configurado en AI SRE. Usamos un **Custom Webhook** que acepta cualquier JSON payload.

> **Referencia oficial:**
> - https://developer.harness.io/docs/ai-sre/alerts/webhooks/create-webhook
> - https://developer.harness.io/docs/ai-sre/alerts/webhooks/use-mustache-webhooks

### 3.1 — Crear la integración

1. En AI SRE, ir a **Integrations** en el left sidebar
2. Click **"New Integration"**
3. Llenar el formulario:
   - **Name**: `Traceable Security Alerts`
   - **Description**: `Receives attack detection alerts from Traceable WAAP/API Protection`
   - **Type**: **Alert** (para monitoreo y alertas — el tipo más común)
   - **Template**: **NO seleccionar template** (dejar vacío para custom webhook)
4. Click **"Save"**

### 3.2 — Copiar endpoints

Después de guardar, el sistema genera dos endpoints:

**Webhook URL (usar este):**
```
https://app.harness.io/gateway/ir/tp/account/EeRjnXTnS4GrLG5VNNJZUw/api/v1/mc/webhook/{webhook-id}
```

**Email alternativo (para sistemas legacy):**
```
{webhook-id}@prod2.alerts.harness.io
```

> **GUARDAR** la Webhook URL — la necesitarás para configurar Traceable y para el curl de simulación.

### 3.3 — Configurar Payload (Field Extraction)

Click en **"Payload Configuration"**:

1. Se mostrará la configuración de campos del payload
2. Para un custom webhook, necesitas definir qué campos esperas del JSON
3. Definir los campos que el payload de Traceable enviará:
   - `title` (string) — nombre de la alerta
   - `description` (string) — detalle del ataque
   - `severity` (string) — critical/high/medium/low
   - `service` (string) — servicio afectado
   - `attack_type` (string) — tipo de ataque
   - `source` (string) — origen de la alerta
   - `endpoints_affected` (array) — endpoints comprometidos
   - `detection_time` (string) — timestamp de detección
4. Click **"Next"**

### 3.4 — Mapear campos (Field Mapping)

En la sección **"Mapped Fields"**, mapear los campos del payload a propiedades de la alerta:

| Alert Property | Mapping (Mustache) | Descripción |
|---------------|-------------------|-------------|
| **Title** | `{{webhook.title}}` | Título de la alerta |
| **Description** | `{{webhook.description}}` | Descripción detallada |
| **Severity** | `{{webhook.severity}}` | Nivel de severidad |
| **Service** | `{{webhook.service}}` | Servicio afectado |

Opciones de mapeo:
- **Drag and drop** los campos del panel izquierdo (saved fields) a los campos del panel derecho
- **Data picker** para seleccionar con un click
- **Escribir manualmente** la expresión Mustache

### 3.5 — Agregar Custom Mapped Fields

Scroll abajo y click **"Add Field"** para agregar campos custom:

**Campo: attack_type**
| Propiedad | Valor |
|-----------|-------|
| Name | `attack_type` |
| Type | String |
| Mapping | `{{webhook.attack_type}}` |

**Campo: source**
| Propiedad | Valor |
|-----------|-------|
| Name | `source` |
| Type | String |
| Default Value | `traceable-waap` |
| Mapping | `{{webhook.source}}` |

Click **Save** en cada campo custom.

### 3.6 — (Opcional) Filtro avanzado con CEL

Si quieres filtrar para solo crear alertas de cierta severidad:

```cel
webhook.severity == "critical" || webhook.severity == "high"
```

Esto descarta alertas de severidad medium/low.

> **Nota:** CEL es para **filtrar** (decidir SI crear alerta). Mustache es para **mapear** (popular campos de la alerta). No mezclar en el mismo campo.

### 3.7 — Test con cURL

El sistema genera un comando cURL de prueba. También puedes usar este:

```bash
# Reemplazar WEBHOOK_URL con la URL generada en paso 3.2
WEBHOOK_URL="https://app.harness.io/gateway/ir/tp/account/EeRjnXTnS4GrLG5VNNJZUw/api/v1/mc/webhook/REEMPLAZAR_WEBHOOK_ID"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "TEST: Attack Chain Detected on DemoBank API",
    "description": "Multi-step attack chain detected by Traceable WAAP: Zombie API recon via /api/ai/status → Prompt Injection on /api/ai/chat → BOLA enumeration on /api/accounts/*/details. 3 endpoints exploited. Protection Policies in Monitor mode — detection only, no blocking active.",
    "severity": "critical",
    "service": "demobank",
    "attack_type": "multi-step-chain",
    "source": "traceable-waap",
    "endpoints_affected": ["/api/ai/status", "/api/ai/chat", "/api/accounts/*/details"],
    "detection_time": "2026-09-01T15:30:00Z",
    "environment": "production",
    "traceable_url": "https://app.us9.traceable.ai/threat-activity"
  }'
```

Click **"Next"** y luego **"Save"** arriba a la derecha.

### 3.8 — (Futuro) Configurar Traceable para enviar webhooks reales

Cuando tengas acceso a Traceable Platform:

1. Ir a **Settings** → **Notifications** → **Notification Channels**
2. Click **+ Add Channel**:
   - **Type**: Webhook
   - **Name**: `Harness AI SRE`
   - **URL**: (pegar la Webhook URL del paso 3.2)
   - **Method**: POST
   - **Headers**: `Content-Type: application/json`
3. Configurar **Notification Rules**:
   - **Trigger**: Protection Policy violation detected
   - **Severity**: Critical, High
   - **Channel**: `Harness AI SRE`
4. Click **Save**

### Verificación

- [ ] Webhook "Traceable Security Alerts" visible en Integrations
- [ ] Webhook URL copiada y guardada
- [ ] Field mappings configurados (title, description, severity, service)
- [ ] Test cURL devuelve 200/201
- [ ] Alerta de prueba aparece en tab Alerts de AI SRE

---

## Paso 4: Crear Alert Rule — Auto-crear incidentes (5 min)

Las Alert Rules definen cómo se procesan las alertas entrantes y cuándo crear incidentes automáticamente.

> **Referencia oficial:** https://developer.harness.io/docs/ai-sre/alerts/alert-rules/create-alert-rule

### 4.1 — Acceder a Alert Rules

1. En AI SRE, ir a **Alerts** desde el menu principal
2. Click en **"Alert Rules"** (o **"Route Alerts"**)
3. Click en **"New Alert Rule"**

### 4.2 — Configurar Integration & Conditions

1. **Integration**: Seleccionar **"Traceable Security Alerts"** (el webhook del Paso 3) como source integration
2. **Condition Mode**: Seleccionar **"Field-based conditions"** (modo visual, recomendado para empezar)
3. Click **"New Condition"** y configurar:

**Condición 1:**
| Campo | Valor |
|-------|-------|
| Field | `severity` (del payload de la alerta) |
| Operator | `equals` |
| Value | `critical` |

4. Click **"Add Condition"** para agregar una segunda condición con OR:

**Condición 2:**
| Campo | Valor |
|-------|-------|
| Field | `severity` |
| Operator | `equals` |
| Value | `high` |

5. Combinar con **ANY** (OR logic) — la regla se activa si CUALQUIER condición es true

> **Alternativa CEL** (si el feature flag `IR_CEL_CONDITIONS` está habilitado):
> ```cel
> alert.severity == "critical" || alert.severity == "high"
> ```

### 4.3 — Configurar Incident Creation

1. Click **"Create Incident"** para habilitar la auto-creación de incidentes
2. Seleccionar **Incident Type**: `Security Incident` (el que creamos en Paso 2)
3. **Mapear campos** de la alerta al incidente:

| Incident Field | Mapping | Notas |
|---------------|---------|-------|
| **Title** | `{{alert.title}}` | Copia el título de la alerta |
| **Description** | `{{alert.description}}` | Copia la descripción |
| **Severity** | Mapear desde `{{alert.severity}}` | critical→SEV1, high→SEV1 |
| **Service** | `{{alert.service}}` | "demobank" |
| **attack_type** | `{{alert.attack_type}}` | Custom field |

> Para severidad, si necesitas mapping condicional con CEL:
> ```cel
> ${{alert.severity == "critical" ? "0" : alert.severity == "high" ? "1" : "2"}}
> ```

### 4.4 — (Opcional) Configurar On-Call Paging

Si tienes on-call configurado:

1. Click **"Page Team"** para activar
2. Seleccionar el checkbox de activación
3. Seleccionar **Impacted Services**: `demobank`
4. Configurar canales de notificación (Slack, email, SMS)

> Para el demo, skip este paso — el runbook se encarga de las notificaciones.

### 4.5 — Asociar Runbook

1. Click en tab **"Runbooks"**
2. Click **"Attach Runbook"**
3. Seleccionar **"Security Incident Response"** (el runbook del Paso 5)
4. Click **"Attach Runbook"** para confirmar

> **Nota:** Los runbooks attached aquí se pueden auto-triggear cuando se crea un incidente, o sugerirse a los responders.

### 4.6 — Guardar

Click **"Save"** para activar la alert rule.

### Verificación

- [ ] Alert rule visible en la lista de Alert Rules
- [ ] Integration apunta a "Traceable Security Alerts"
- [ ] Condiciones configuradas (severity = critical OR high)
- [ ] Incident creation habilitado con tipo "Security Incident"
- [ ] Field mappings correctos
- [ ] Runbook asociado (después de crear el runbook en Paso 5)

---

## Paso 5: Crear Runbook — "Security Incident Response" (12 min)

Este es el core del demo de Act 6. El runbook se ejecuta automáticamente cuando se crea un incidente SEV0/SEV1 de tipo Security Incident.

> **Referencia oficial:**
> - https://developer.harness.io/docs/ai-sre/runbooks/create-runbook
> - https://developer.harness.io/docs/ai-sre/runbooks/triggers/create-trigger

### 5.1 — Crear el runbook

1. En AI SRE, ir a **Runbooks** desde el left panel
2. Click **"New Runbook"**
3. Llenar el formulario:
   - **Name**: `Security Incident Response`
   - **Description**: `Automated response for security incidents detected by Traceable WAAP — notifies Slack, creates incident channel, posts context`
4. Click **"Save"** para crear la estructura base y abrir el workflow designer

### 5.2 — Categorías de acciones disponibles

El panel izquierdo del workflow designer muestra las categorías:

| Categoría | Acciones disponibles |
|-----------|---------------------|
| **Communication** | Slack: Send Message, Create Channel, Update Message; MS Teams: Post Message; Zoom: Create Meeting; Email |
| **Tickets & Code** | Jira: Create/Update Issue; ServiceNow: Create/Update Incident; GitHub; Confluence |
| **On-Call** | OpsGenie: Page; PagerDuty: Page |
| **Incidents and Alerts** | Manage incident timeline; Resolve alerts; Close incidents |
| **Other** | HTTP Request (any REST API); Harness: Execute Pipeline |

### 5.3 — Action 1: Slack — Send Alert Notification

1. Click **"New Step"** → seleccionar **"Action"**
2. Categoría: **Communication** → **Slack: Send Message**
3. Click **"Select"**
4. Configurar:

| Campo | Valor |
|-------|-------|
| **Channel** | `#security-incidents` |
| **Message Format** | Block Kit JSON |

**Message (Block Kit JSON):**
```json
[
  {
    "type": "header",
    "text": {
      "type": "plain_text",
      "text": "Security Incident: {{Activity.title}}"
    }
  },
  {
    "type": "section",
    "fields": [
      { "type": "mrkdwn", "text": "*Severity:*\nSEV{{Activity.severity.id}}" },
      { "type": "mrkdwn", "text": "*Status:*\n{{Activity.status}}" },
      { "type": "mrkdwn", "text": "*Service:*\n{{Activity.service}}" },
      { "type": "mrkdwn", "text": "*Type:*\nSecurity Incident" }
    ]
  },
  {
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": "{{Activity.summary}}"
    }
  },
  {
    "type": "actions",
    "elements": [
      {
        "type": "button",
        "text": { "type": "plain_text", "text": "View Incident" },
        "url": "{{Activity.url}}"
      }
    ]
  }
]
```

5. Click **"Save"**

### 5.4 — Action 2: Slack — Create Incident Channel

1. Click **"New Step"** → **"Action"**
2. Categoría: **Communication** → **Slack: Create Channel**
3. Configurar:

| Campo | Valor |
|-------|-------|
| **Channel Name** | `sec-inc-{{Activity.id}}` |
| **Description** | `SEV{{Activity.severity.id}} - {{Activity.title}}` |
| **Is Private** | `false` |

4. Click **"Save"**

### 5.5 — Action 3: Slack — Post Context to Incident Channel

1. Click **"New Step"** → **"Action"**
2. Categoría: **Communication** → **Slack: Send Message**
3. Configurar:

| Campo | Valor |
|-------|-------|
| **Channel** | `{{runbook.outputs.slack_create_channel.channel_id}}` |

> **IMPORTANTE:** Usamos `{{runbook.outputs.slack_create_channel.channel_id}}` — esto referencia el output del Action 2 (Create Channel). Cada acción produce outputs que las acciones siguientes pueden consumir.

**Message:**
```
Security Incident Bridge

Title: {{Activity.title}}
Severity: SEV{{Activity.severity.id}}
Service: {{Activity.service}}

Attack detected by Traceable Runtime Protection Agent.
Protection Policies in Monitor mode — detection only, no blocking.

Next steps:
1. Review Traceable dashboard for attack details
2. Check affected endpoints and data exposure
3. Evaluate blast radius via SBOM (Act 6)
4. Evaluate activating Block mode (Act 7)

Incident details: {{Activity.url}}
```

4. Click **"Save"**

### 5.6 — Action 4: Jira — Create Security Issue

Crea un ticket Jira automáticamente con contexto completo del incidente.

> **Pre-requisito:** Jira connector configurado en **Project Settings** → **Third-Party Integrations (AI SRE)**. Ver [Configure Project Connectors](https://developer.harness.io/docs/ai-sre/runbooks/configure-project-connectors).

1. Click **"New Step"** → **"Action"**
2. Categoría: **Tickets & Code** → **Jira: Create Issue**
3. Click **"Select"**
4. Configurar campos requeridos:

| Campo | Valor |
|-------|-------|
| **Project Key** | (seleccionar tu proyecto Jira — typeahead habilitado) |
| **Issue Type** | `Bug` |
| **Summary** | `[{{Activity.Severity}}] Security: {{Activity.Title}}` |
| **Description** | (ver bloque abajo) |

**Description:**
```
Security Incident Auto-Created by Harness AI SRE

Severity:     {{Activity.Severity}}
Status:       {{Activity.Status}}
Services:     {{Activity.Impacted Services}}
Environment:  {{Activity.Environments}}
Reported:     {{Activity.Reported At}}

ATTACK SUMMARY:
{{Activity.Summary}}

DETECTION COVERAGE:
- WAF:              0/4 steps detected
- WAAP (Traceable): 4/4 steps detected
- Protection mode:  Monitor (detection only)

NEXT STEPS:
1. Review attack chain in Traceable dashboard
2. Assess blast radius via SBOM analysis
3. Evaluate activating Block mode

Traceable: https://app.us9.traceable.ai/threat-activity
Incident:  {{Activity.URL}}
```

5. Click **"Add Field"** para agregar campos adicionales:

| Field | Value |
|-------|-------|
| **Priority** | `High` |
| **Labels** | `security-incident, demobank, ai-sre-auto` |

6. Click **"Save"**

> **Cross-action output:** El issue key creado (`{{runbook.outputs.jira_create_issue.issue_key}}`) queda disponible para acciones siguientes.

### 5.7 — (Opcional) Action 5: Harness — Execute Pipeline

Si quieres que el runbook trigger un pipeline de remediación:

1. Click **"New Step"** → **"Action"**
2. Categoría: **Other** → **Harness: Execute Pipeline**
3. Configurar:
   - **Project**: `CristianRamirez`
   - **Pipeline**: (seleccionar pipeline de remediación si existe)
   - **Input Set**: (opcional)
4. Click **"Save"**

### 5.8 — Variables Mustache disponibles en Runbooks

Referencia rápida de variables que puedes usar en cualquier acción:

**Incident (Activity):**
| Variable | Descripción |
|----------|-------------|
| `{{Activity.title}}` | Título del incidente |
| `{{Activity.id}}` | ID numérico del incidente |
| `{{Activity.severity}}` | Label de severidad (ej: "SEV1: Major") |
| `{{Activity.severity.id}}` | ID numérico de severidad (ej: "1") |
| `{{Activity.status}}` | Estado actual (Investigating, Resolved, etc.) |
| `{{Activity.summary}}` | Resumen/descripción |
| `{{Activity.service}}` | Servicio afectado |
| `{{Activity.url}}` | URL directa al incidente en Harness |

**Cross-action outputs:**
| Variable | Descripción |
|----------|-------------|
| `{{runbook.outputs.slack_create_channel.channel_id}}` | ID del canal creado por acción anterior |
| `{{runbook.outputs.zoom_create_meeting.join_url}}` | URL de Zoom meeting creado |

> **CEL inline** también funciona en campos de texto de acciones:
> ```
> ${{Activity.severity.id == "0" ? "CRITICAL" : "Major"}}
> ```

### 5.9 — Configurar Trigger automático

El trigger hace que el runbook se ejecute **automáticamente** cuando se crea un incidente que cumple ciertas condiciones.

1. Click en tab **"Triggers"** en el runbook editor
2. Click **"+ New Trigger"**
3. **Trigger Template**: Seleccionar el incident type **"Security Incident"**
4. **Condition Logic**: Seleccionar **"ALL"** (todas las condiciones deben cumplirse)
5. **Frequency**: Seleccionar **"Activity Created"** (trigger cuando se crea el incidente)
6. **Add Conditions:**

**Condición 1:**
| Campo | Valor |
|-------|-------|
| Field | `severity` |
| Comparison | **New Values** |
| Comparator | `equals` |
| Value | `0` (SEV0) |

7. Click **"Add Condition"** (agregar OR para incluir SEV1):

**Condición 2:**
| Campo | Valor |
|-------|-------|
| Field | `severity` |
| Comparison | **New Values** |
| Comparator | `equals` |
| Value | `1` (SEV1) |

8. Cambiar logic a **"ANY"** si necesitas OR entre condiciones
9. Click **"Save"** arriba a la derecha

> **Alternativa CEL** (si feature flag `IR_CEL_CONDITIONS` habilitado):
> ```cel
> incident.severity == "0" || incident.severity == "1"
> ```

### Verificación

- [ ] Runbook "Security Incident Response" visible en lista
- [ ] 4 acciones configuradas (Send Message → Create Channel → Post to Channel → Jira Create Issue)
- [ ] Variables Mustache correctas en cada acción
- [ ] Jira ticket se crea con severity, summary, y labels
- [ ] Trigger configurado: "Activity Created" + severity SEV0/SEV1
- [ ] (Después) Runbook pinned al incident type "Security Incident" (volver a Paso 2.7)

---

## Paso 6: Validación end-to-end (5 min)

### 6.1 — Test completo del flujo

Simular una alerta y verificar toda la cadena:

```bash
# Reemplazar con tu Webhook URL real del Paso 3.2
WEBHOOK_URL="https://app.harness.io/gateway/ir/tp/account/EeRjnXTnS4GrLG5VNNJZUw/api/v1/mc/webhook/REEMPLAZAR_WEBHOOK_ID"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Attack Chain Detected: DemoBank API",
    "description": "Multi-step attack chain detected by Traceable WAAP: Zombie API recon via /api/ai/status (N-S) → Prompt Injection on /api/ai/chat with MCP service call (N-S + E-W) → BOLA enumeration on /api/accounts/*/details (N-S). 3 endpoints exploited, 5 accounts exfiltrated. Protection Policies in Monitor mode — detection only, no blocking active. WAF detected 0/4 steps. WAAP detected 4/4 steps.",
    "severity": "critical",
    "service": "demobank",
    "attack_type": "multi-step-chain",
    "source": "traceable-waap",
    "endpoints_affected": ["/api/ai/status", "/api/ai/chat", "/api/accounts/*/details"],
    "detection_time": "2026-09-01T15:30:00Z",
    "environment": "production",
    "traceable_url": "https://app.us9.traceable.ai/threat-activity"
  }'
```

### 6.2 — Checklist de verificación

Verificar en orden:

**AI SRE → Alerts tab:**
- [ ] La alerta aparece con título "Attack Chain Detected: DemoBank API"
- [ ] Severidad correcta: critical
- [ ] Service: demobank
- [ ] Source: Traceable Security Alerts

**AI SRE → Incidents tab:**
- [ ] Incidente creado automáticamente (por la alert rule)
- [ ] Tipo: Security Incident
- [ ] Severity: SEV0 o SEV1 (según mapping)
- [ ] Campos custom poblados (attack_type, source)

**Runbook execution:**
- [ ] Runbook "Security Incident Response" ejecutado automáticamente
- [ ] Timeline del incidente muestra las 3 acciones ejecutadas
- [ ] Tiempo de ejecución: < 15 segundos

**Slack:**
- [ ] Mensaje de notificación en `#security-incidents` con Block Kit formateado
- [ ] Canal `sec-inc-{ID}` creado automáticamente
- [ ] Mensaje de contexto posteado en el canal del incidente
- [ ] Botón "View Incident" funciona y lleva al incidente en Harness

**Jira:**
- [ ] Ticket creado automáticamente en el proyecto Jira
- [ ] Summary contiene severity + título del incidente
- [ ] Description contiene attack summary, detection coverage, next steps
- [ ] Labels: `security-incident`, `demobank`, `ai-sre-auto`
- [ ] Priority: High

**Slack commands (verificar que funcionan):**
- [ ] En el canal del incidente: `/harness summarize` — genera resumen AI
- [ ] `/harness new` — muestra formulario de crear incidente
- [ ] `/harness run security-incident-response` — ejecuta el runbook manualmente

---

## Paso 7: Deploy Change Investigator — Correlacionar deployments con incidentes (10 min)

Conecta el pipeline CI/CD con AI SRE para que cuando ocurra un incidente, AI SRE muestre automáticamente "¿qué deployment ocurrió antes?" con commits y PRs asociados.

> **Referencia oficial:** https://developer.harness.io/docs/ai-sre/change/deploy-change-investigator

### 7.1 — Configurar GitHub connector en AI SRE

1. Ir a **Project Settings** → **Third Party Integrations (AI SRE)**
2. En la fila **GitHub**, seleccionar el connector de GitHub existente (`CristianConnector`)
3. Click **Save**

Esto permite que AI SRE ingeste PRs del repositorio automáticamente.

### 7.2 — Crear PR Ingestion

1. En AI SRE, ir a **Integrations** → tab **PR Ingestions**
2. Click **+ New PR Ingestion**
3. **Git Provider**: GitHub
4. **Repository URL**: `https://github.com/crizstian/ai-agentic-demo.git`
5. Click **Create**

AI SRE empezará a ingestar los PRs mergeados a la rama principal.

### 7.3 — Obtener webhook URLs (BUILD y DEPLOY)

1. En AI SRE, ir a **Integrations**
2. Buscar la integración **BUILD** — click en el icono **More** (⋯) → **Debug**
3. Copiar la **Build webhook URL**
4. Buscar la integración **DEPLOY** — click en el icono **More** (⋯) → **Debug**
5. Copiar la **Deploy webhook URL**

### 7.4 — Crear secretos en Harness

Los webhook URLs contienen tokens — guardarlos como secretos:

1. Ir a **Project Settings** → **Secrets** → **+ New Secret** → **Text**
2. **Secret 1:**
   - **Name**: `aisre_build_webhook_url`
   - **Value**: (pegar la Build webhook URL del paso 7.3)
3. **Secret 2:**
   - **Name**: `aisre_deploy_webhook_url`
   - **Value**: (pegar la Deploy webhook URL del paso 7.3)

### 7.5 — Steps ya agregados al pipeline

El pipeline `AI SDLC DemoBank` ya tiene los steps de notificación:

**Build stage** — step "AI SRE Build Notification" (después de artifact signing):
- Envía: artifact name + version + commit SHA + branch + repository URL
- Usa: `<+secrets.getValue("aisre_build_webhook_url")>`

**Deploy DemoBank stage** — step "AI SRE Deploy Notification" (después del rolling deploy):
- Envía: services deployed + environment + changeId + deployedBy
- Usa: `<+secrets.getValue("aisre_deploy_webhook_url")>`

### 7.6 — Payloads de referencia

**Build webhook payload:**
```json
{
  "artifact": {"name": "docker.io/crizstian/harnessbank-demo", "version": "<sequenceId>"},
  "source": {
    "commitSha": "<commitSha>",
    "kind": "branch",
    "value": "<branch>",
    "repository_url": "https://github.com/crizstian/ai-agentic-demo.git"
  },
  "service": {"name": "harnessbank-demo", "version": "<sequenceId>"},
  "buildId": "<executionId>"
}
```

**Deploy webhook payload:**
```json
{
  "services": [
    {"service": "harnessbank-demo", "version": "<sequenceId>"},
    {"service": "mcp-financial-data", "version": "<sequenceId>"}
  ],
  "environments": ["gke-latam"],
  "changeId": "<executionId>",
  "status": "SUCCESS",
  "deployedBy": "<triggeredBy>",
  "deployTimestamp": "<startTs>"
}
```

### 7.7 — Correlación automática

Una vez configurado, AI SRE correlaciona automáticamente:
- **Deployment → Build → Commits → PRs** en la cadena
- Cualquier alerta/incidente que ocurra dentro de **30 minutos** del deploy se correlaciona automáticamente
- La pestaña **Investigation** del incidente mostrará el deployment como posible root cause
- Los PRs mergeados antes del build aparecen como "code changes"

### 7.8 — Verificación

Después de un pipeline run exitoso:

1. En AI SRE, ir a **Change Management**
2. Verificar que el deployment aparece con:
   - Services: harnessbank-demo, mcp-financial-data
   - Environment: gke-latam
   - Linked build con commit SHA
3. Click en el deployment → verificar que muestra commits y PRs

- [ ] GitHub connector configurado en Third Party Integrations
- [ ] PR Ingestion creada para el repositorio
- [ ] Build webhook URL guardada como secret `aisre_build_webhook_url`
- [ ] Deploy webhook URL guardada como secret `aisre_deploy_webhook_url`
- [ ] Pipeline run exitoso con ambos webhooks enviados (HTTP 200)
- [ ] Change Management muestra el deployment correlacionado

---

## Paso 8 (Opcional): Monitored Service en SRM (5 min)

Para tener Continuous Verification y health scores en el deploy del Act 4. Esto es SRM (Service Reliability Management), no AI SRE — son módulos separados.

> **Referencia oficial:** https://developer.harness.io/docs/service-reliability-management/monitored-service/create-monitored-service

### 7.1 — Crear Monitored Service

1. Ir a **Service Reliability** → **Monitored Services** → **"+ New Monitored Service"**
2. Configurar:
   - **Type**: Application
   - **Service**: `demobank`
   - **Environment**: `gke_latam`

### 7.2 — Add Health Source (Prometheus)

1. Click **"Add Health Source"**
2. Configurar:
   - **Type**: Prometheus
   - **Name**: `demobank-prometheus`
   - **Connector**: `selatamprom` (ya existe, status: SUCCESS)
   - **Feature**: Prometheus Metrics (APM)
3. **Metrics**:
   - **Group Name**: `demobank-health`
   - **Query**: `up{job="demobank"}` (o `http_requests_total{service="demobank"}`)
   - **Assign to**: Service Health + Continuous Verification
4. Click **Save**

### 7.3 — Add Change Source

1. Click **"Add Change Source"**
2. **Provider Type**: Deployments → **Harness CD NextGen** (auto-captured)
3. Click **Save**

Los deploys via Harness CD se capturan automáticamente como change events.

---

## Resumen de la cadena completa

```
FLUJO AUTOMATIZADO END-TO-END:

Pipeline CI/CD ejecuta (Acts 2-4)
    ├── Build stage → Build webhook → AI SRE registra artifact + commit
    └── Deploy stage → Deploy webhook → AI SRE registra deployment + services
                                         + PR ingestion (GitHub PRs mergeados)

Traceable detecta ataque (Act 5)
    ↓ webhook POST (JSON payload)
Harness AI SRE → Alert creada
    ↓ alert rule match (severity == critical/high)
Incident "Security Incident" creado automáticamente (SEV1)
    ├── Deploy Change Investigator correlaciona automáticamente:
    │   "Deploy de harnessbank-demo v42 hace 25 min → commits → PRs"
    ↓ runbook trigger (Activity Created + severity in [0,1])
Runbook "Security Incident Response" ejecuta:
    ├── Step 1: Slack → notificación en #security-incidents
    ├── Step 2: Slack → canal sec-inc-{ID} creado
    ├── Step 3: Slack → contexto posteado en canal con next steps
    ├── Step 4: Jira → ticket creado con contexto del incidente
    └── (Step 5: Harness Pipeline ejecutado — opcional)

Total runtime: ~12 segundos. 0 pasos manuales.
Correlación: automática con deployments dentro de 30 min.
```

---

## Tiempo estimado de setup

| Paso | Tiempo | Requiere | Status |
|------|--------|----------|--------|
| 0. Verificar AI SRE habilitado | 2 min | Acceso a Harness | PENDIENTE |
| 1. Integrar Slack | 5 min | Slack Workspace Admin | PENDIENTE |
| 2. Incident Type "Security Incident" | 5 min | Harness Admin | PENDIENTE |
| 3. Webhook custom (Traceable) | 8 min | Harness Admin | PENDIENTE |
| 4. Alert Rule (auto-create incidents) | 5 min | Harness Admin | PENDIENTE |
| 5. Runbook + Trigger | 12 min | Harness Admin + Slack | PENDIENTE |
| 6. Validación end-to-end | 5 min | Todos los pasos anteriores | PENDIENTE |
| 7. Deploy Change Investigator | 10 min | Pipeline + GitHub connector | PENDIENTE |
| 8. Monitored Service SRM (opcional) | 5 min | Prometheus connector | PENDIENTE |
| **Total** | **~52 min** | | |

---

## Documentación de referencia

| Tema | URL |
|------|-----|
| AI SRE Onboarding Overview | https://developer.harness.io/docs/ai-sre/get-started/onboarding/overview |
| Integrate Tools (Slack) | https://developer.harness.io/docs/ai-sre/get-started/onboarding/integrate-tools |
| Setup Incident Types | https://developer.harness.io/docs/ai-sre/get-started/onboarding/setup-incident-types |
| Configure Incident Types (detailed) | https://developer.harness.io/docs/ai-sre/incidents/incident-templates |
| Severity & Priority Labels | https://developer.harness.io/docs/ai-sre/incidents/severities-priorities |
| Create Webhook | https://developer.harness.io/docs/ai-sre/alerts/webhooks/create-webhook |
| Mustache in Webhooks | https://developer.harness.io/docs/ai-sre/alerts/webhooks/use-mustache-webhooks |
| CEL in Webhooks | https://developer.harness.io/docs/ai-sre/alerts/webhooks/use-cel-webhooks |
| Create Alert Rule | https://developer.harness.io/docs/ai-sre/alerts/alert-rules/create-alert-rule |
| CEL in Alert Rules | https://developer.harness.io/docs/ai-sre/alerts/alert-rules/use-cel-alert-rules |
| Create Runbooks | https://developer.harness.io/docs/ai-sre/runbooks/create-runbook |
| Runbook Triggers | https://developer.harness.io/docs/ai-sre/runbooks/triggers/create-trigger |
| CEL in Runbook Triggers | https://developer.harness.io/docs/ai-sre/runbooks/triggers/use-cel-triggers |
| Expression Languages (CEL vs Mustache) | https://developer.harness.io/docs/ai-sre/get-started/onboarding/expression-languages |
| Slack Commands | https://developer.harness.io/docs/ai-sre/get-started/slack-commands |
| AI Scribe Agent | https://developer.harness.io/docs/ai-sre/ai-agent |
| Create Incidents (UI + Quick Start) | https://developer.harness.io/docs/ai-sre/users/create-incidents |
| Jira Runbook Actions | https://developer.harness.io/docs/ai-sre/runbooks/integrations/ticketing/jira |
| Jira Integration (overview) | https://developer.harness.io/docs/ai-sre/integrations/ticketing-itsm/jira |
| Configure Project Connectors | https://developer.harness.io/docs/ai-sre/runbooks/configure-project-connectors |
| Deploy Change Investigator | https://developer.harness.io/docs/ai-sre/change/deploy-change-investigator |
| AI Agent RCA (Change Agent) | https://developer.harness.io/docs/ai-sre/ai-agent/rca-change-agent |
| Incident Response Automation Patterns | https://developer.harness.io/docs/ai-sre/incidents/incident-workflows |
| What's Supported | https://developer.harness.io/docs/ai-sre/resources/whats-supported |
