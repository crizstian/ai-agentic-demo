import os
import re

ROOT = os.path.dirname(os.path.dirname(__file__))


def _read(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
        return f.read()


def test_readiness_probe_uses_configurable_health_path():
    manifest = _read("deploy/k8s/demobank/deployment.yaml")
    values = _read("deploy/k8s/demobank/values.yaml")
    assert re.search(
        r"readinessProbe:\s+httpGet:\s+path: \{\{ \.Values\.healthCheckPath \}\}",
        manifest,
    )
    assert 'healthCheckPath: "/health"' in values


def test_deployment_rolls_pods_on_every_harness_execution():
    manifest = _read("deploy/k8s/demobank/deployment.yaml")
    values = _read("deploy/k8s/demobank/values.yaml")

    assert "rolloutId: <+pipeline.executionId>" in values
    assert 'harness.io/rollout-id: "{{ .Values.rolloutId }}"' in manifest
    assert "imagePullPolicy: Always" in manifest
