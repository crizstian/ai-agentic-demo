# Harness AI-Native SecOps — Brief de Demo

**Demo:** SDLC AI End-to-End en 7 Actos
**Aplicación:** DemoBank — App bancaria con AI Chat Assistant
**Modalidad:** 100% desde el IDE — cero cambio de contexto

---

## Narrativa

Un desarrollador construye una funcionalidad nueva usando un AI Code Agent. El código pasa por un pipeline gobernado con agentes AI independientes. Se despliega con supply chain verificada y canary. Un atacante — también con AI — explota la app en producción. Harness detecta, responde en 12 segundos, y protege en runtime. Todo sin salir del IDE.

---

## Los 7 Actos

### Acto 1 — AI Code Agent
El desarrollador construye un Asistente Bancario AI (backend + frontend) en menos de 2 minutos. Crea un PR que dispara el pipeline automáticamente.

### Acto 2 — Gobernanza Automática
El pipeline ejecuta 4 agentes AI autónomos: Build & Lint, Test Intelligence, Change Advisor (code review) y Quality Agent (generación de tests). El desarrollador consulta resultados desde el IDE.

### Acto 3 — Remediación de Seguridad
El pipeline detectó SQLi, CMDi, XSS, CORS y una dependencia SCA vulnerable. El desarrollador remedia guiado por hallazgos concretos del scanner. El agente Security Remediator también auto-corrige y hace push.

### Acto 4 — Supply Chain + Canary + Feature Flag
CI genera SBOM, SLSA y firma artefactos. CD verifica todo antes de desplegar. Canary con 1 pod, luego rollout completo.

### Acto 5 — El Ataque
Un atacante usa un AI Code Agent para explotar la app: reconocimiento → descubre zombie API → prompt injection (tráfico E-W) → BOLA/IDOR → exfiltración masiva. Traceable detecta toda la cadena en modo Monitor. Un WAF tradicional no ve nada.

### Acto 6 — AI SRE + Radio de Impacto
Traceable alerta a Harness AI SRE. En 12 segundos: incidente SEV1, Slack, war room, Jira. Desde el IDE se evalúa radio de impacto vía SBOM y se crea política OPA de prevención.

### Acto 7 — Kill Switch + Block + AI Security
**Traceable Block** → SQLi, XSS, CMDi retornan 403. **AI Security** → AIBOM, AI Discovery, MCP Risk Score.

---

## Productos Harness en el Demo

CI · CD · STO · SCS · AI Agents · AI SRE · OPA · WAAP

---

> Los agentes de código se detienen en el PR. Los Agentes de Harness llevan cada cambio a producción — y protegen lo que corre ahí.
