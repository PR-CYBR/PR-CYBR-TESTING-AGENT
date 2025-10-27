#############################################
# PR-CYBR Testing Agent Variable Schema     #
#                                           #
# These declarations define the Terraform   #
# Cloud variables required by the testing   #
# agent workspace. Sensitive values are     #
# provided through Terraform Cloud and must #
# never be hard-coded in this repository.   #
#############################################

variable "AGENT_ACTIONS" {
  description = "Token used by the testing agent to authenticate GitHub Actions and CI pipelines"
  type        = string
  sensitive   = true
}

variable "NOTION_DISCUSSIONS_ARC_DB_ID" {
  description = "Notion database identifier for architecture discussions"
  type        = string
}

variable "NOTION_ISSUES_BACKLOG_DB_ID" {
  description = "Notion database identifier for the issues backlog"
  type        = string
}

variable "NOTION_KNOWLEDGE_FILE_DB_ID" {
  description = "Notion database identifier for knowledge file records"
  type        = string
}

variable "NOTION_PAGE_ID" {
  description = "Root Notion page identifier used for testing agent operations"
  type        = string
}

variable "NOTION_PR_BACKLOG_DB_ID" {
  description = "Notion database identifier for pull request backlog tracking"
  type        = string
}

variable "NOTION_PROJECT_BOARD_BACKLOG_DB_ID" {
  description = "Notion database identifier for project board backlog coordination"
  type        = string
}

variable "NOTION_TASK_BACKLOG_DB_ID" {
  description = "Notion database identifier for the task backlog"
  type        = string
}

variable "NOTION_TOKEN" {
  description = "API token granting the testing agent access to Notion"
  type        = string
  sensitive   = true
}

variable "TFC_TOKEN" {
  description = "Terraform Cloud API token used for workspace automation"
  type        = string
  sensitive   = true
}
