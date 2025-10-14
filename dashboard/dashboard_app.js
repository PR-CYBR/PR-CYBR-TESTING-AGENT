/*
 * Dashboard UI logic for visualising agent workflows and activity.
 *
 * The script expects an element with the id ``dashboard-root`` to be present
 * on the page. It dynamically renders workflow cards, aggregated analytics,
 * and a continuously updating activity feed by calling the REST endpoints
 * exposed from ``dashboard_api.py``.
 */

const apiBaseUrl = "/api";
let workflowState = [];
let liveFeedSince = 0;
let liveFeedIntervalId = null;

const LEVEL_BADGE = {
  INFO: "badge-info",
  WARNING: "badge-warning",
  ERROR: "badge-error",
};

function createLayout(root) {
  root.innerHTML = `
    <section class="dashboard">
      <header class="dashboard__header">
        <h1>Agent Workflow Dashboard</h1>
        <p>Track orchestration, analytics, and live activity for automated agents.</p>
      </header>
      <div class="dashboard__analytics" id="analytics-cards"></div>
      <div class="dashboard__content">
        <div class="dashboard__workflows">
          <h2>Workflows</h2>
          <div id="workflow-list" class="workflow-list"></div>
        </div>
        <div class="dashboard__logs">
          <h2>Workflow Logs</h2>
          <div id="workflow-logs" class="logs-panel"></div>
          <h2>Live Activity</h2>
          <div id="live-feed" class="live-feed"></div>
        </div>
      </div>
    </section>
  `;
}

function renderAnalytics(metrics) {
  const container = document.getElementById("analytics-cards");
  if (!container) return;

  container.innerHTML = `
    <article class="card">
      <h3>Total Runs</h3>
      <p>${metrics.totalRuns}</p>
    </article>
    <article class="card">
      <h3>Running</h3>
      <p>${metrics.running}</p>
    </article>
    <article class="card">
      <h3>Paused</h3>
      <p>${metrics.paused}</p>
    </article>
    <article class="card">
      <h3>Failed</h3>
      <p>${metrics.failed}</p>
    </article>
    <article class="card card--muted">
      <h3>Last Updated</h3>
      <p>${new Date(metrics.lastUpdated).toLocaleString()}</p>
    </article>
  `;
}

function renderWorkflows(workflows) {
  workflowState = workflows;
  const list = document.getElementById("workflow-list");
  if (!list) return;

  list.innerHTML = "";
  workflows.forEach((workflow) => {
    const item = document.createElement("article");
    item.className = `workflow workflow--${workflow.status}`;
    item.innerHTML = `
      <div class="workflow__title">
        <h3>${workflow.name}</h3>
        <span class="workflow__status">${workflow.status.toUpperCase()}</span>
      </div>
      <p class="workflow__meta">Runs: <strong>${workflow.runs}</strong></p>
      <p class="workflow__meta">Last Run: <strong>${workflow.lastRun ? new Date(workflow.lastRun).toLocaleString() : "Never"}</strong></p>
      <p class="workflow__meta">Owner: <strong>${workflow.owner}</strong></p>
      <div class="workflow__tags">${workflow.tags.map((tag) => `<span class="tag">${tag}</span>`).join(" ")}</div>
      <div class="workflow__actions">
        ${renderActions(workflow)}
      </div>
    `;

    item.addEventListener("click", (event) => {
      if (event.target.closest("button")) {
        return;
      }
      loadWorkflowLogs(workflow.id);
    });

    list.appendChild(item);
  });
}

function renderActions(workflow) {
  const actions = [];
  if (workflow.status === "running") {
    actions.push({ label: "Pause", action: "pause" });
    actions.push({ label: "Stop", action: "stop" });
  } else if (workflow.status === "paused") {
    actions.push({ label: "Resume", action: "resume" });
    actions.push({ label: "Stop", action: "stop" });
  } else if (workflow.status === "idle" || workflow.status === "completed") {
    actions.push({ label: "Start", action: "start" });
  } else {
    actions.push({ label: "Start", action: "start" });
  }

  return actions
    .map(
      (item) => `
        <button class="btn" data-action="${item.action}" data-workflow="${workflow.id}">
          ${item.label}
        </button>
      `
    )
    .join("\n");
}

function renderWorkflowLogs(workflowId, logs) {
  const container = document.getElementById("workflow-logs");
  if (!container) return;

  const workflow = workflowState.find((wf) => wf.id === workflowId);
  const title = workflow ? workflow.name : workflowId;

  container.innerHTML = `
    <h3>${title}</h3>
    <ul class="log-list">
      ${logs
        .map(
          (log) => `
            <li>
              <span class="log-list__timestamp">${new Date(log.timestamp).toLocaleTimeString()}</span>
              <span class="log-list__badge ${LEVEL_BADGE[log.level] || "badge-info"}">${log.level}</span>
              <span class="log-list__message">${log.message}</span>
            </li>
          `
        )
        .join("")}
    </ul>
  `;
}

function renderLiveFeed(events) {
  const container = document.getElementById("live-feed");
  if (!container) return;

  events.forEach((event) => {
    const row = document.createElement("div");
    row.className = "live-feed__row";
    row.innerHTML = `
      <span class="live-feed__timestamp">${new Date(event.timestamp).toLocaleTimeString()}</span>
      <span class="live-feed__workflow">${event.workflowId}</span>
      <span class="live-feed__badge ${LEVEL_BADGE[event.level] || "badge-info"}">${event.level}</span>
      <span class="live-feed__message">${event.message}</span>
    `;
    container.prepend(row);
  });

  while (container.children.length > 50) {
    container.removeChild(container.lastChild);
  }
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Request failed: ${response.status} ${detail}`);
  }

  return response.json();
}

async function loadWorkflows() {
  const payload = await fetchJSON(`${apiBaseUrl}/workflows`);
  renderWorkflows(payload.workflows);
  if (payload.workflows.length > 0) {
    loadWorkflowLogs(payload.workflows[0].id);
  }
}

async function loadAnalytics() {
  const payload = await fetchJSON(`${apiBaseUrl}/analytics/summary`);
  renderAnalytics(payload.analytics);
}

async function loadWorkflowLogs(workflowId) {
  const payload = await fetchJSON(`${apiBaseUrl}/workflows/${workflowId}/logs`);
  renderWorkflowLogs(workflowId, payload.logs);
}

async function sendWorkflowAction(workflowId, action) {
  await fetchJSON(`${apiBaseUrl}/workflows/${workflowId}/actions`, {
    method: "POST",
    body: JSON.stringify({ action }),
  });
  await Promise.all([loadWorkflows(), loadAnalytics()]);
}

async function fetchLiveStatus() {
  const payload = await fetchJSON(`${apiBaseUrl}/status/live?since=${liveFeedSince}`);
  liveFeedSince = payload.nextSince || liveFeedSince;
  if (payload.events && payload.events.length) {
    renderLiveFeed(payload.events);
  }
}

function attachWorkflowActionHandler() {
  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-workflow]");
    if (!button) return;
    const { workflow: workflowId, action } = button.dataset;
    sendWorkflowAction(workflowId, action).catch((error) => {
      console.error("Failed to apply workflow action", error);
      alert(`Unable to ${action} workflow: ${error.message}`);
    });
  });
}

function injectStyles() {
  if (document.getElementById("dashboard-style")) {
    return;
  }

  const style = document.createElement("style");
  style.id = "dashboard-style";
  style.innerHTML = `
    :root {
      --bg: #0b111b;
      --panel: #121a27;
      --text: #e3ecff;
      --muted: #8594b0;
      --accent: #5c7cfa;
      --warning: #f4a261;
      --error: #ef6f6c;
    }
    body {
      font-family: "Inter", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
    }
    .dashboard {
      padding: 2rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }
    .dashboard__header h1 {
      margin: 0 0 0.5rem;
      font-size: 2rem;
    }
    .dashboard__header p {
      margin: 0;
      color: var(--muted);
    }
    .dashboard__analytics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
    }
    .card {
      background: var(--panel);
      padding: 1rem;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    .card--muted h3 {
      color: var(--muted);
    }
    .dashboard__content {
      display: grid;
      grid-template-columns: 2fr 1.5fr;
      gap: 2rem;
    }
    .workflow-list {
      display: grid;
      gap: 1rem;
    }
    .workflow {
      background: var(--panel);
      border-radius: 12px;
      padding: 1rem;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .workflow:hover {
      transform: translateY(-2px);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
    }
    .workflow__title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }
    .workflow__status {
      font-size: 0.75rem;
      letter-spacing: 1px;
      color: var(--muted);
    }
    .workflow__meta {
      margin: 0.25rem 0;
      color: var(--muted);
    }
    .workflow__tags {
      margin: 0.5rem 0;
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }
    .tag {
      background: rgba(92, 124, 250, 0.15);
      color: var(--accent);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      font-size: 0.75rem;
    }
    .workflow__actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 0.75rem;
    }
    .btn {
      background: var(--accent);
      border: none;
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 600;
      transition: background 0.2s ease;
    }
    .btn:hover {
      background: #4c6ef5;
    }
    .logs-panel,
    .live-feed {
      background: var(--panel);
      border-radius: 12px;
      padding: 1rem;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
      min-height: 200px;
    }
    .log-list {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    .log-list__timestamp {
      color: var(--muted);
      margin-right: 0.5rem;
      font-size: 0.75rem;
    }
    .log-list__badge,
    .live-feed__badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 0.1rem 0.6rem;
      font-size: 0.75rem;
      margin-right: 0.5rem;
    }
    .badge-info {
      background: rgba(92, 124, 250, 0.2);
      color: var(--accent);
    }
    .badge-warning {
      background: rgba(244, 162, 97, 0.2);
      color: var(--warning);
    }
    .badge-error {
      background: rgba(239, 111, 108, 0.2);
      color: var(--error);
    }
    .live-feed {
      margin-top: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      max-height: 400px;
      overflow-y: auto;
    }
    .live-feed__row {
      display: grid;
      grid-template-columns: 1fr 1.5fr 1fr 3fr;
      gap: 0.5rem;
      font-size: 0.85rem;
      align-items: center;
    }
    @media (max-width: 900px) {
      .dashboard__content {
        grid-template-columns: 1fr;
      }
    }
  `;
  document.head.appendChild(style);
}

function startLiveFeed() {
  if (liveFeedIntervalId) return;
  liveFeedIntervalId = window.setInterval(() => {
    fetchLiveStatus().catch((error) => console.error("Live feed error", error));
  }, 4000);
}

async function initialiseDashboard() {
  const root = document.getElementById("dashboard-root");
  if (!root) {
    console.warn("dashboard-root element not found; skipping dashboard initialisation");
    return;
  }

  injectStyles();
  createLayout(root);
  attachWorkflowActionHandler();

  try {
    await Promise.all([loadWorkflows(), loadAnalytics(), fetchLiveStatus()]);
    startLiveFeed();
  } catch (error) {
    console.error("Failed to initialise dashboard", error);
    root.innerHTML = `<p class="error">Failed to load dashboard data: ${error.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", initialiseDashboard);
