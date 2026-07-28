---
description: Switch context to infrastructure and Kubernetes focus
allowed-tools: Read, Grep, Glob, Bash
---

Activate infrastructure context profile for this session.

## Instructions

1. Detect infrastructure tooling in the project:
   - Look for `terraform/` or `*.tf` files
   - Look for `k8s/`, `helm/`, `deploy/`, `charts/` directories
   - Check for `docker-compose*.yml` files
   - Check Kubernetes connectivity: `kubectl config current-context`

2. Summarize findings in 3-5 lines:
   - IaC tool (Terraform, Helm, Kustomize, raw manifests)
   - Kubernetes cluster access (yes/no, context name)
   - Cloud provider (GCP, AWS, Azure)
   - Any CI/CD integration for deploys

3. Set your focus for this session:
   - Use `@k8s-debugger` for pod/service investigation
   - Use Kubernetes MCP tools for cluster queries
   - For Terraform: validate plans before apply, check state drift
   - For Helm: validate values, check release status
   - Flag security concerns (exposed secrets, privileged containers, missing resource limits)

4. Tell the user: "Infrastructure context active. I'll focus on IaC, Kubernetes, and cloud resources. Use `@k8s-debugger` for cluster issues."
