# Notion Integration via Terraform Cloud

This project syncs with Notion databases using credentials that are managed entirely through Terraform Cloud (TFC) workspace variables. No secrets or database identifiers should be committed to the repository.

## Required Environment Variables

Create the following **environment** variables in the PR-CYBR Terraform Cloud workspace used for this project:

| Variable Name | Sensitive? | Purpose |
| --- | --- | --- |
| `NOTION_TOKEN` | Yes | Notion internal integration token used for API access. |
| `NOTION_AGENT_DATABASE_ID` | Yes | Database that stores agent configuration and status. |
| `NOTION_LOG_DATABASE_ID` | Yes | Database that receives runtime or audit logs. |

> **Tip:** Mark each variable as *Sensitive* so Terraform Cloud redacts it in logs. Database IDs are treated as sensitive to avoid leaking workspace structure in public pipelines.

## How to Configure in Terraform Cloud

1. Sign in to [Terraform Cloud](https://app.terraform.io/).
2. Open the workspace that orchestrates this repository.
3. Navigate to **Variables** → **Environment Variables**.
4. Add the variables listed above, ensuring the *Sensitive* toggle is enabled for each value.
5. Save the variables. They will automatically be made available to GitHub Actions via the Terraform Cloud → GitHub secrets sync process.

Once set, the CI workflow references these values through the standard `secrets.*` context so they can be injected into scripts that communicate with Notion.
