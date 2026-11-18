# Approved Patterns

Patrones validados que los agentes deben seguir. Cada patron fue
probado y confirmado como funcional.

---

## Feature Flag Check (Backend)

```python
def _check_feature_flag():
    try:
        factory = _get_split_factory()
        client = factory.client()
        treatment = client.get_treatment("demobank-server", "ai_chat_backend")
        if treatment != "control":
            return treatment == "on"
    except Exception:
        pass
    return _check_feature_flag_rest()  # fallback REST API
```

Razon: SDK devuelve "control" cuando no puede conectar. Fallback a REST API
directa que si funciona via `requests`.

## Split SDK Lazy Init

```python
_split_factory = None

def _get_split_factory():
    global _split_factory
    if _split_factory is None:
        factory = get_factory(
            os.environ.get("SPLIT_SDK_KEY", "v4kvjbb2cuupu0ihed20iceumvv1m9po07bn"),
            config={"connectionTimeout": 5, "readTimeout": 5},
        )
        try:
            factory.block_until_ready(5)
        except TimeoutException:
            pass
        _split_factory = factory
    return _split_factory
```

Razon: module-level init bloquea imports en CI donde egress a split.io esta bloqueado.

## MCP Financial Data Integration

```python
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp-financial-data:5001")

def _get_mcp_context(message, account_ids):
    try:
        payload = {"query": message, "context": {"accounts": [{"id": aid} for aid in account_ids]}}
        resp = requests.post(f"{MCP_SERVER_URL}/api/enrich", json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None
```

Razon: MCP service puede no estar disponible (pod caido, red). Fallback graceful a None.

## Worker Agent Prompt Structure

```yaml
env:
  PLUGIN_MAX_TURNS: ${{inputs.maxTurns}}
  PLUGIN_TASK: |
    You are [role]. [context].

    ## Context
    - Repo: <+inputs.repoSlug>
    - Source branch: <+inputs.sourceBranch>

    ## Platform Detection
    Detect from Repo URL:
    - "github.com" → GitHub MCP tools
    - "git.harness.io" → Harness Code MCP tools

    ## Process
    1. [step]
    2. [step]

    ## Anti-Patterns — DO NOT:
    - [what not to do]
```

Razon: agents necesitan platform detection (GitHub vs HC), inputs dinamicos,
y anti-patterns explicitos para evitar waste de turns.

## Pipeline YAML Sync

```bash
# 1. Edit YAML locally
# 2. Sync to Harness via MCP (BEFORE push)
mcp__harness__harness_update(pipeline_yaml)
# 3. Commit + push to Git
git commit && git push
```

Razon: pipeline es INLINE. Push triggerea pipeline con el YAML que Harness tiene,
no el que esta en Git. Sync primero asegura que Harness use la version nueva.

## Demo Reset

```bash
./scripts/demo-reset.sh --db --commit --push
```

Razon: el script maneja 16 invariantes, limpia pycache, resetea DB, syncs
3 branches, y triggerea deploy. Manual checkout pierde invariantes.
