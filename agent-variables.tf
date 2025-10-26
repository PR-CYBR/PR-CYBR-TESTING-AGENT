#############################################
# PR-CYBR Agent Variables (Generic Baseline)
# This file declares variables expected by
# Terraform Cloud across all PR-CYBR Agents.
# Real values are securely managed in TFC.
#############################################

# --- Docker / Registry ---
variable "DOCKERHUB_TOKEN" {
  type        = string
  sensitive   = true
  description = "Docker Hub access token"
}

variable "DOCKERHUB_USERNAME" {
  type        = string
  description = "Docker Hub username"
}

# --- Global Infrastructure URIs ---
variable "GLOBAL_DOMAIN" {
  type        = string
  description = "Root DNS domain for PR-CYBR services"
}

variable "GLOBAL_ELASTIC_URI" {
  type        = string
  description = "Elasticsearch endpoint"
}

variable "GLOBAL_GRAFANA_URI" {
  type        = string
  description = "Grafana endpoint"
}

variable "GLOBAL_KIBANA_URI" {
  type        = string
  description = "Kibana endpoint"
}

variable "GLOBAL_PROMETHEUS_URI" {
  type        = string
  description = "Prometheus endpoint"
}

# --- Networking / Security ---
variable "GLOBAL_TAILSCALE_AUTHKEY" {
  type        = string
  sensitive   = true
  description = "Auth key for Tailscale VPN/DNS"
}

variable "GLOBAL_TRAEFIK_ACME_EMAIL" {
  type        = string
  description = "Email used by Traefik for Let's Encrypt"
}

variable "GLOBAL_TRAEFIK_ENTRYPOINTS" {
  type        = string
  description = "Default entrypoints for Traefik"
}

variable "GLOBAL_ZEROTIER_NETWORK_ID" {
  type        = string
  sensitive   = true
  description = "ZeroTier overlay network ID"
}

# --- Agent Tokens ---
variable "AGENT_ACTIONS" {
  type        = string
  sensitive   = true
  description = "Token for CI/CD pipelines (builds, tests, deploys)"
}

variable "AGENT_COLLAB" {
  type        = string
  sensitive   = true
  description = "Token for governance, discussions, issues, project boards"
}

# --- GitHub / Terraform Cloud Authentication ---
variable "GITHUB_TOKEN" {
  type        = string
  sensitive   = true
  description = "GitHub token used by automation workflows"
}

variable "TFC_TOKEN" {
  type        = string
  sensitive   = true
  description = "Terraform Cloud API token for workspace operations"
}

# --- Docker Publishing ---
variable "PR_CYBR_DOCKER_USER" {
  type        = string
  description = "Service account username for Docker Hub publishing"
}

variable "PR_CYBR_DOCKER_PASS" {
  type        = string
  sensitive   = true
  description = "Service account password for Docker Hub publishing"
}

# --- Notion Integrations ---
variable "NOTION_API_TOKEN" {
  type        = string
  sensitive   = true
  description = "API token for Notion automation access"
}

variable "NOTION_SYNC_PLAN" {
  type        = string
  description = "JSON sync plan controlling Notion synchronization"
}

variable "NOTION_TOKEN" {
  type        = string
  sensitive   = true
  description = "Legacy Notion integration token referenced by workflows"
}

variable "NOTION_DISCUSSIONS_ARC_DB_ID" {
  type        = string
  description = "Database ID for the discussions archive board"
}

variable "NOTION_ISSUES_BACKLOG_DB_ID" {
  type        = string
  description = "Database ID for the issues backlog board"
}

variable "NOTION_KNOWLEDGE_FILE_DB_ID" {
  type        = string
  description = "Database ID for the knowledge file catalog"
}

variable "NOTION_PAGE_ID" {
  type        = string
  description = "Landing page identifier for workspace context"
}

variable "NOTION_PR_BACKLOG_DB_ID" {
  type        = string
  description = "Database ID for the pull request backlog board"
}

variable "NOTION_PROJECT_BOARD_BACKLOG_DB_ID" {
  type        = string
  description = "Database ID for the project board backlog"
}

variable "NOTION_TASK_BACKLOG_DB_ID" {
  type        = string
  description = "Database ID for the task backlog board"
}
