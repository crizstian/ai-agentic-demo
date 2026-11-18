# Constraints

Restricciones que los agentes DEBEN respetar. Violaciones causan fallos
en pipeline, estado corrupto, o comportamiento inesperado.

---

## Hard Constraints (violar = fallo garantizado)

1. **No modificar CSS existente** — solo agregar reglas nuevas al final de styles.css
2. **No crear archivos fuera de las rutas registradas** — Harness solo deploya
   archivos ya registrados en el service manifest
3. **No hardcodear PLUGIN_MAX_TURNS** — declarar como input formal
4. **No usar `type: Secret`** en service variables — usar `type: String` + JEXL
5. **No intentar delete_branch** via GitHub MCP — la tool no existe
6. **No poner quotes en `<+input>.default()`** — causa runtime errors
7. **No enviar secretos a prompts, logs, Git, Jira ni memory**
8. **No usar `git checkout` para resetear** — solo `scripts/demo-reset.sh`
9. **No correr pipeline HC y GitHub simultaneamente** — comparten K8s deployment
10. **No push sin sync MCP** cuando pipeline es INLINE

## Soft Constraints (violar = resultado suboptimo)

1. **Split SDK lazy init** — module-level init causa timeout en CI
2. **Sync MCP antes de push** — evita trigger con YAML desactualizado
3. **Un remote a la vez** — solo push al que el usuario pidio
4. **Agent turns budget** — security_analyzer max 35, qa_ui_analyzer max 25
5. **Canary count: 2** — no usar porcentaje, pods son efimeros
6. **AI Evals expected_output como string plano** — no dict

## Anti-Patterns Conocidos

- Agent gastando turns en `pip install X==9999.0.0` para descubrir versiones
- Agent intentando borrar branches despues de merge
- Agent haciendo harness_get secuenciales en vez de batch
- Agent creando secret.yaml (no se deployea, no esta en manifest)
- MCP servers que no reconectan mid-session (requiere restart)
