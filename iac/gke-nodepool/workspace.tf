terraform {
  required_providers {
    harness = {
      source  = "harness/harness"
      version = "~> 0.31"
    }
  }
}

variable "org_id" {
  type    = string
  default = "sandbox"
}

variable "project_id" {
  type    = string
  default = "CristianRamirez"
}

resource "harness_platform_workspace" "ai_agentic_demo_nodepool" {
  name                    = "AI Agentic Demo Nodepool"
  identifier              = "ai_agentic_demo_nodepool"
  org_id                  = var.org_id
  project_id              = var.project_id
  provisioner_type        = "terraform"
  provisioner_version     = "1.5.7"
  repository              = "platform-gitops"
  repository_branch       = "main"
  repository_path         = "Harness-Demo/Sandbox/iac/gcp-gke-nodepool"
  cost_estimation_enabled = true
  provider_connector      = "account.GCP_Sales_Admin"
  repository_connector    = "CodeRepoCristianRamirez"

  terraform_variable {
    key        = "gcp_project_id"
    value      = "sales-209522"
    value_type = "string"
  }

  terraform_variable {
    key        = "gcp_region"
    value      = "us-east1-b"
    value_type = "string"
  }

  terraform_variable {
    key        = "gke_cluster_name"
    value      = "se-sandbox"
    value_type = "string"
  }

  terraform_variable {
    key        = "gke_version_prefix"
    value      = "1.31."
    value_type = "string"
  }

  terraform_variable {
    key        = "gke_nodepools"
    value      = jsonencode({
      "ai-agentic-demo-nodepool" = {
        machine_type    = "e2-standard-4"
        service_account = "sales-demo-admin@sales-209522.iam.gserviceaccount.com"
        nodepool_labels = {
          owner   = "cristian-ramirez"
          scope   = "ai-agentic-demo"
          purpose = "demobank-demo"
        }
        autoscaling = {
          min_node_count = 1
          max_node_count = 2
        }
        node_locations = ["us-east1-b"]
        tags           = ["terraform", "iacm"]
        node_taints = {
          "ai-agentic-demo" = {
            key    = "dedicated"
            value  = "ai_agentic_demo_space"
            effect = "NO_SCHEDULE"
          }
        }
      }
    })
    value_type = "string"
  }
}
