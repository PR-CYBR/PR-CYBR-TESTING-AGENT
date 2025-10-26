############################################################
# Terraform Cloud Workspace Variable Assignments
# ----------------------------------------------------------
# These placeholder values document every variable consumed
# by automation workflows and Terraform modules for the
# PR-CYBR Testing Agent. Update the real values inside the
# Terraform Cloud workspace or associated secrets store.
############################################################

# --- Docker / Registry ---
DOCKERHUB_USERNAME           = "prcybr-service"
DOCKERHUB_TOKEN              = "dockerhub-token-placeholder"
PR_CYBR_DOCKER_USER          = "prcybr-service"
PR_CYBR_DOCKER_PASS          = "dockerhub-password-placeholder"

# --- Global Infrastructure URIs ---
GLOBAL_DOMAIN                = "example.prcybr.net"
GLOBAL_ELASTIC_URI           = "https://elastic.example.prcybr.net"
GLOBAL_GRAFANA_URI           = "https://grafana.example.prcybr.net"
GLOBAL_KIBANA_URI            = "https://kibana.example.prcybr.net"
GLOBAL_PROMETHEUS_URI        = "https://prometheus.example.prcybr.net"

# --- Networking / Security ---
GLOBAL_TAILSCALE_AUTHKEY     = "tskey-XXXXXXXXXXXXXXXXXXXX"
GLOBAL_TRAEFIK_ACME_EMAIL    = "devops@example.prcybr.net"
GLOBAL_TRAEFIK_ENTRYPOINTS   = "web,websecure"
GLOBAL_ZEROTIER_NETWORK_ID   = "abcdef1234567890"

# --- Agent Tokens ---
AGENT_ACTIONS                = "agent-actions-token-placeholder"
AGENT_COLLAB                 = "agent-collab-token-placeholder"
GITHUB_TOKEN                 = "github-token-placeholder"
TFC_TOKEN                    = "tfc-token-placeholder"

# --- Notion Integrations ---
NOTION_API_TOKEN             = "notion-api-token-placeholder"
NOTION_SYNC_PLAN             = "{\"sync\": \"plan\"}"
NOTION_TOKEN                 = "notion-token-placeholder"
NOTION_DISCUSSIONS_ARC_DB_ID = "00000000000000000000000000000000"
NOTION_ISSUES_BACKLOG_DB_ID  = "11111111111111111111111111111111"
NOTION_KNOWLEDGE_FILE_DB_ID  = "22222222222222222222222222222222"
NOTION_PAGE_ID               = "33333333333333333333333333333333"
NOTION_PR_BACKLOG_DB_ID      = "44444444444444444444444444444444"
NOTION_PROJECT_BOARD_BACKLOG_DB_ID = "55555555555555555555555555555555"
NOTION_TASK_BACKLOG_DB_ID    = "66666666666666666666666666666666"
