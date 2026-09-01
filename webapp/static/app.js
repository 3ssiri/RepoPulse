/* RepoPulse web frontend — vanilla JS, no build step.
 *
 * Human and agent share the same state: the WebMCP tools call the exact
 * same scanRepository()/compareRefs() functions as the on-page buttons,
 * and both paths update `state` and re-render the visible UI.
 */
"use strict";

const state = {
  repositoryUrl: "",
  ref: "",
  currentReport: null,
  currentComparison: null,
  status: "idle",
  error: null,
  webmcpAvailable: false,
};

let requestGeneration = 0;
let activeController = null;

function isStaleRequest(startedGeneration) {
  return startedGeneration !== requestGeneration;
}

function isStaleComparison(startedGeneration, startedUrl) {
  return isStaleRequest(startedGeneration) || startedUrl !== state.repositoryUrl;
}

function beginRequest() {
  requestGeneration += 1;
  if (activeController) {
    activeController.abort();
  }
  activeController = new AbortController();
  return { generation: requestGeneration, controller: activeController };
}

function bindExternalSignal(controller, external) {
  if (!external) return;
  if (external.aborted) {
    controller.abort();
    return;
  }
  external.addEventListener("abort", function onAbort() {
    controller.abort();
  }, { once: true });
}

const els = {};

function collectElements() {
  for (const id of [
    "webmcp-badge", "scan-form", "repository-url", "ref", "scan-button",
    "status", "error", "report-section", "report-repo", "report-score",
    "report-grade", "report-truncated", "checks-list", "recommendations-list",
    "attention-section", "attention-list", "compare-form", "baseline-ref",
    "target-ref", "compare-button", "comparison-result", "comparison-delta",
    "improved-list", "regressed-list", "unchanged-list",
  ]) {
    els[id] = document.getElementById(id);
  }
}

function setStatus(status, message) {
  state.status = status;
  els["status"].textContent = message || "";
  const busy = status === "scanning" || status === "comparing";
  els["scan-button"].disabled = busy;
  els["compare-button"].disabled = busy;
}

function setError(message) {
  state.error = message || null;
  if (message) {
    els["error"].textContent = message;
    els["error"].hidden = false;
  } else {
    els["error"].textContent = "";
    els["error"].hidden = true;
  }
}

async function parseApiResponse(response) {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body && body.detail;
    const message = detail && detail.message ? detail.message : "Request failed.";
    const error = new Error(message);
    error.code = detail && detail.code ? detail.code : "unknown_error";
    throw error;
  }
  return body;
}

function syncScanForm(repositoryUrl, ref) {
  if (els["repository-url"]) els["repository-url"].value = repositoryUrl;
  if (els["ref"]) els["ref"].value = ref || "";
}

/* Single scan path used by BOTH the Scan button and the WebMCP
 * scan_repository tool. Returns the structured HealthReport. */
async function scanRepository(repositoryUrl, ref, signal) {
  const started = beginRequest();
  bindExternalSignal(started.controller, signal);
  setError(null);
  setStatus("scanning", "Scanning " + repositoryUrl + " ...");
  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository_url: repositoryUrl, ref: ref || null }),
      signal: started.controller.signal,
    });
    const report = await parseApiResponse(response);
    if (isStaleRequest(started.generation)) {
      const error = new Error("Request superseded.");
      error.name = "AbortError";
      throw error;
    }
    state.repositoryUrl = repositoryUrl;
    state.ref = ref || "";
    state.currentReport = report;
    state.currentComparison = null;
    syncScanForm(repositoryUrl, ref);
    renderReport(report);
    renderComparison(null);
    setStatus("idle", "Scan complete: " + report.repository.full_name +
      " — " + report.total_score + "/" + report.max_score + " (" + report.grade + ")");
    return report;
  } catch (error) {
    if (started.generation !== requestGeneration) {
      throw error;
    }
    setStatus("idle", "");
    if (error && error.name === "AbortError") {
      setError("Scan was cancelled.");
    } else {
      setError(error.message || "Scan failed.");
    }
    throw error;
  }
}

/* Single compare path used by BOTH the Compare button and the WebMCP
 * compare_refs tool. Returns the structured ComparisonReport. */
async function compareRefs(baselineRef, targetRef, signal) {
  const started = beginRequest();
  bindExternalSignal(started.controller, signal);
  const startedUrl = state.repositoryUrl;
  try {
    if (!startedUrl) {
      throw new Error("No repository is selected. Scan a repository first.");
    }
    setError(null);
    setStatus("comparing", "Comparing " + baselineRef + " with " + targetRef + " ...");
    const response = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repository_url: startedUrl,
        baseline_ref: baselineRef,
        target_ref: targetRef,
      }),
      signal: started.controller.signal,
    });
    const comparison = await parseApiResponse(response);
    if (isStaleComparison(started.generation, startedUrl)) {
      const error = new Error("Request superseded.");
      error.name = "AbortError";
      throw error;
    }
    state.currentComparison = comparison;
    renderComparison(comparison);
    setStatus("idle", "Comparison complete: delta " + comparison.score_delta +
      " (" + comparison.baseline_score + " → " + comparison.target_score + ")");
    return comparison;
  } catch (error) {
    if (started.generation !== requestGeneration) {
      throw error;
    }
    setStatus("idle", "");
    if (error && error.name === "AbortError") {
      setError("Comparison was cancelled.");
    } else {
      setError(error.message || "Comparison failed.");
    }
    throw error;
  }
}

/* All GitHub-derived data is untrusted: render with textContent and
 * createElement only, never innerHTML. */
function appendTextItem(list, text, className) {
  const li = document.createElement("li");
  if (className) li.className = className;
  li.textContent = text;
  list.appendChild(li);
}

function renderCheck(list, check) {
  const li = document.createElement("li");
  li.className = "check check-" + check.status;

  const head = document.createElement("div");
  head.className = "check-head";
  const badge = document.createElement("span");
  badge.className = "badge badge-" + check.status;
  badge.textContent = check.status.toUpperCase();
  const title = document.createElement("strong");
  title.textContent = check.title;
  const score = document.createElement("span");
  score.className = "muted";
  score.textContent = " " + check.score + "/" + check.max_score;
  head.appendChild(badge);
  head.appendChild(title);
  head.appendChild(score);
  li.appendChild(head);

  const message = document.createElement("p");
  message.textContent = check.message;
  li.appendChild(message);

  if (check.recommendations && check.recommendations.length > 0) {
    const recs = document.createElement("ul");
    for (const rec of check.recommendations) {
      appendTextItem(recs, rec);
    }
    li.appendChild(recs);
  }
  list.appendChild(li);
}

function attentionItems(report) {
  const failures = report.checks.filter((c) => c.status === "fail");
  const warnings = report.checks.filter((c) => c.status === "warn");
  return failures.concat(warnings);
}

function renderReport(report) {
  els["report-repo"].textContent = report.repository.full_name;
  els["report-score"].textContent =
    "Score " + report.total_score + "/" + report.max_score;
  const grade = els["report-grade"];
  grade.textContent = "Grade " + report.grade;
  grade.className = "badge badge-grade";
  els["report-truncated"].hidden = !report.scan_truncated;

  els["checks-list"].replaceChildren();
  for (const check of report.checks) {
    renderCheck(els["checks-list"], check);
  }

  els["recommendations-list"].replaceChildren();
  if (report.recommendations.length === 0) {
    appendTextItem(els["recommendations-list"], "No recommendations.");
  } else {
    for (const rec of report.recommendations) {
      appendTextItem(els["recommendations-list"], rec);
    }
  }
  els["report-section"].hidden = false;

  els["attention-list"].replaceChildren();
  const items = attentionItems(report);
  if (items.length === 0) {
    appendTextItem(els["attention-list"], "Nothing needs attention. All checks pass.");
  } else {
    for (const check of items) {
      renderCheck(els["attention-list"], check);
    }
  }
  els["attention-section"].hidden = false;
}

function renderComparison(comparison) {
  if (!comparison) {
    els["comparison-result"].hidden = true;
    return;
  }
  els["comparison-delta"].textContent =
    comparison.baseline_label + ": " + comparison.baseline_score + "/" + comparison.baseline_max_score +
    " → " + comparison.target_label + ": " + comparison.target_score + "/" + comparison.target_max_score +
    " (delta " + (comparison.score_delta >= 0 ? "+" : "") + comparison.score_delta + ")";
  const lists = {
    improved: els["improved-list"],
    regressed: els["regressed-list"],
    unchanged: els["unchanged-list"],
  };
  for (const key of Object.keys(lists)) {
    lists[key].replaceChildren();
    const values = comparison[key];
    if (values.length === 0) {
      appendTextItem(lists[key], "None.");
    } else {
      for (const value of values) {
        appendTextItem(lists[key], value);
      }
    }
  }
  els["comparison-result"].hidden = false;
}

function renderWebMCPStatus() {
  const badge = els["webmcp-badge"];
  if (state.webmcpAvailable) {
    badge.textContent = "WebMCP Available";
    badge.className = "badge badge-on";
  } else {
    badge.textContent = "WebMCP Unavailable";
    badge.className = "badge badge-off";
  }
}

function reportSummary(report) {
  return {
    repository: report.repository.full_name,
    score: report.total_score,
    max_score: report.max_score,
    grade: report.grade,
    scan_truncated: report.scan_truncated,
    checks: report.checks.map((c) => ({
      key: c.key, title: c.title, status: c.status,
      score: c.score, max_score: c.max_score, message: c.message,
    })),
    recommendations: report.recommendations,
  };
}

function registerWebMCPTools() {
  // Feature detection: WebMCP is progressive enhancement only.
  if (!("modelContext" in document) || !document.modelContext ||
      typeof document.modelContext.registerTool !== "function") {
    state.webmcpAvailable = false;
    renderWebMCPStatus();
    return;
  }

  const registration = new AbortController();
  const readOnly = { readOnlyHint: true, untrustedContentHint: true };

  const tools = [
    {
      name: "scan_repository",
      title: "Scan repository",
      description: "Scan a public GitHub repository with RepoPulse, update the visible dashboard, and return its health report. Use this before asking for check details or attention items.",
      inputSchema: {
        type: "object",
        properties: {
          repository_url: { type: "string", description: "Public github.com repository URL." },
          ref: { type: "string", description: "Optional branch, tag, or commit ref." },
        },
        required: ["repository_url"],
      },
      annotations: readOnly,
      execute: async (input, options) => {
        const report = await scanRepository(
          input.repository_url, input.ref || null, options && options.signal);
        return reportSummary(report);
      },
    },
    {
      name: "get_attention_items",
      title: "Get attention items",
      description: "Return the failing and warning checks from the current RepoPulse report, ordered FAIL first then WARN. Reads the current page state only; run scan_repository first.",
      inputSchema: { type: "object", properties: {} },
      annotations: readOnly,
      execute: async () => {
        const report = state.currentReport;
        if (!report) {
          return { error: "No repository report is loaded. Run scan_repository first." };
        }
        return {
          repository: report.repository.full_name,
          score: report.total_score,
          max_score: report.max_score,
          grade: report.grade,
          attention_items: attentionItems(report).map((c) => ({
            key: c.key, title: c.title, status: c.status,
            message: c.message, recommendations: c.recommendations,
          })),
        };
      },
    },
    {
      name: "get_check_details",
      title: "Get check details",
      description: "Return full details for one RepoPulse check from the current report, including its recommendations. Reads the current page state only; run scan_repository first.",
      inputSchema: {
        type: "object",
        properties: {
          check_key: { type: "string", description: "RepoPulse check key from the current report." },
        },
        required: ["check_key"],
      },
      annotations: readOnly,
      execute: async (input) => {
        const report = state.currentReport;
        if (!report) {
          return { error: "No repository report is loaded. Run scan_repository first." };
        }
        const check = report.checks.find((c) => c.key === input.check_key);
        if (!check) {
          return {
            error: "Unknown check key: " + input.check_key,
            available_keys: report.checks.map((c) => c.key),
          };
        }
        return {
          repository: report.repository.full_name,
          score: report.total_score,
          grade: report.grade,
          check: check,
        };
      },
    },
    {
      name: "compare_refs",
      title: "Compare refs",
      description: "Compare repository health between two refs of the currently scanned repository, update the visible dashboard, and return the comparison report. Run scan_repository first to select the repository.",
      inputSchema: {
        type: "object",
        properties: {
          baseline_ref: { type: "string", description: "Baseline branch, tag, or commit ref." },
          target_ref: { type: "string", description: "Target branch, tag, or commit ref." },
        },
        required: ["baseline_ref", "target_ref"],
      },
      annotations: readOnly,
      execute: async (input, options) => {
        if (!state.repositoryUrl) {
          return { error: "No repository is selected. Run scan_repository first." };
        }
        const comparison = await compareRefs(
          input.baseline_ref, input.target_ref, options && options.signal);
        return {
          repository: comparison.target_repository,
          baseline_label: comparison.baseline_label,
          target_label: comparison.target_label,
          baseline_score: comparison.baseline_score,
          target_score: comparison.target_score,
          score_delta: comparison.score_delta,
          improved: comparison.improved,
          regressed: comparison.regressed,
          unchanged: comparison.unchanged,
          checks: comparison.checks,
        };
      },
    },
  ];

  Promise.all(
    tools.map((tool) =>
      document.modelContext.registerTool(tool, { signal: registration.signal }))
  ).then(() => {
    state.webmcpAvailable = true;
    renderWebMCPStatus();
  }).catch(() => {
    registration.abort();
    state.webmcpAvailable = false;
    renderWebMCPStatus();
  });
}

function main() {
  collectElements();
  renderWebMCPStatus();

  els["scan-form"].addEventListener("submit", (event) => {
    event.preventDefault();
    scanRepository(els["repository-url"].value.trim(), els["ref"].value.trim())
      .catch(() => {});
  });

  els["compare-form"].addEventListener("submit", (event) => {
    event.preventDefault();
    compareRefs(els["baseline-ref"].value.trim(), els["target-ref"].value.trim())
      .catch(() => {});
  });

  registerWebMCPTools();
}

document.addEventListener("DOMContentLoaded", main);