############################################################
# PR-CYBR Agent Terraform Bootstrap
#
# This module does not provision infrastructure directly.
# Instead, it normalizes the variables that Terraform Cloud
# injects for each agent so downstream modules can consume
# a consistent structure.
############################################################

terraform {
  required_version = ">= 1.6.0"
}

locals {
  agent_profile = {
    id             = var.AGENT_ID
    notion_page_id = var.NOTION_PAGE_ID
    global_domain  = var.GLOBAL_DOMAIN
  }

  registry_credentials = {
    pr_cybr = {
      username = var.PR_CYBR_DOCKER_USER
      password = var.PR_CYBR_DOCKER_PASS
    }
    dockerhub = {
      username = var.DOCKERHUB_USERNAME
      token    = var.DOCKERHUB_TOKEN
    }
  }

  notion_integrations = {
    token                     = var.NOTION_TOKEN
    discussions_database_id   = var.NOTION_DISCUSSIONS_ARC_DB_ID
    issues_database_id        = var.NOTION_ISSUES_BACKLOG_DB_ID
    knowledge_database_id     = var.NOTION_KNOWLEDGE_FILE_DB_ID
    project_board_database_id = var.NOTION_PROJECT_BOARD_BACKLOG_DB_ID
    pr_database_id            = var.NOTION_PR_BACKLOG_DB_ID
    task_database_id          = var.NOTION_TASK_BACKLOG_DB_ID
    agent_page_id             = var.NOTION_PAGE_ID
  }

  automation_tokens = {
    agent_actions = var.AGENT_ACTIONS
    tfc_token     = var.TFC_TOKEN
  }
}

output "agent_profile" {
  description = "Core identifiers required by downstream modules"
  value       = local.agent_profile
}

output "registry_credentials" {
  description = "Credential bundle for container registries"
  value       = local.registry_credentials
  sensitive   = true
}

output "notion_integrations" {
  description = "Notion integration tokens and database identifiers"
  value       = local.notion_integrations
  sensitive   = true
}

output "automation_tokens" {
  description = "Tokens used for GitHub Actions and Terraform Cloud access"
  value       = local.automation_tokens
  sensitive   = true
}
