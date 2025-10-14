# System Diagrams

The following diagrams illustrate the workflow interconnections and human-in-the-loop (HITL) touchpoints that keep the PR-CYBR Testing Agent aligned with the broader platform.

## Workflow Interconnections
```mermaid
flowchart LR
    subgraph Dev[Development Inputs]
        Code[Code Commits]
        Config[Config Changes]
    end

    Code -->|Triggers| CI[CI/CD Agent]
    Config -->|Updates| CI

    CI -->|Pipeline Verdicts| Testing[Testing Agent]
    Sec[Security Agent] -->|Vuln Reports| Testing
    Perf[Performance Agent] -->|Load Metrics| Testing

    Testing -->|Test Results| Dashboard[Agent Dashboard]
    Testing -->|Events| Bus[Event Bus]
    Bus -->|Notifications| Hooks[Automation Hooks]
    Hooks -->|Alerts| Slack[Slack Channel]
    Hooks -->|Emails| Email[Status Distribution]

    Dashboard -->|Insights| Stakeholders[Stakeholders]
```

## HITL Touchpoints
```mermaid
sequenceDiagram
    participant CI as CI/CD Agent
    participant Test as Testing Agent
    participant Dash as Agent Dashboard
    participant HITL as HITL Operator
    participant Sec as Security Agent

    CI->>Test: Dispatch regression suite
    Test->>Dash: Publish anomaly alert
    Dash->>HITL: Notify via dashboard + Slack
    HITL->>Dash: Apply override and annotate issue
    Dash->>Sec: Escalate critical vulnerability context
    Sec->>Test: Provide remediation guidance
    Test->>CI: Re-run gated checks
```

> These diagrams use Mermaid syntax and can be rendered directly in GitHub or compatible documentation viewers.
