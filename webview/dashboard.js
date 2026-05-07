/**
 * dashboard.js — logique du webview Clarify.
 *
 * Communication avec l'extension VS Code via l'API vscode.postMessage().
 * En mode standalone (hors VS Code), les données sont lues depuis
 * l'objet window.CLARIFY_DATA injecté par le backend Python.
 */

// Pont avec l'extension VS Code (undefined si ouvert hors VS Code)
const vscode = typeof acquireVsCodeApi !== "undefined"
  ? acquireVsCodeApi()
  : null;

// ── Utilitaires DOM ──────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = value ?? "—";
}

// ── Typage des badges ────────────────────────────────────────────
const ERROR_TYPES = {
  error:   ["NameError","IndexError","KeyError","AttributeError","TypeError",
            "ValueError","ZeroDivisionError","RuntimeError","RecursionError",
            "OverflowError","MemoryError","StopIteration"],
  warning: ["ImportError","ModuleNotFoundError","FileNotFoundError",
            "PermissionError","TimeoutError","OSError"],
  system:  ["SystemExit","KeyboardInterrupt","GeneratorExit",
            "NotImplementedError","SyntaxError","IndentationError"],
};

function getBadgeClass(type) {
  for (const [cls, list] of Object.entries(ERROR_TYPES)) {
    if (list.includes(type)) return cls;
  }
  return "";
}

// ── Rendu du tableau ─────────────────────────────────────────────
function renderTable(errors) {
  const tbody = $("errors-body");
  tbody.innerHTML = "";

  if (!errors || errors.length === 0) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="7">Aucune erreur enregistrée.</td></tr>`;
    return;
  }

  for (const err of errors) {
    const tr = document.createElement("tr");
    const badgeClass = getBadgeClass(err.type);
    const file = err.file ? err.file.split(/[\\/]/).pop() : "—";
    const time = err.time ? err.time.slice(11, 19) : "—";

    tr.innerHTML = `
      <td>${err.id}</td>
      <td><span class="type-badge ${badgeClass}">${err.type}</span></td>
      <td title="${err.message}">${err.message}</td>
      <td class="mono" title="${err.file}">${file}</td>
      <td>${err.line ?? "—"}</td>
      <td>${time}</td>
      <td><button class="btn-delete" data-id="${err.id}" title="Supprimer">✕</button></td>
    `;

    // Clic sur la ligne → ouvre le panneau de détail
    tr.addEventListener("click", (e) => {
      if (e.target.classList.contains("btn-delete")) return;
      openDetail(err);
    });

    // Clic sur le bouton supprimer
    tr.querySelector(".btn-delete").addEventListener("click", (e) => {
      e.stopPropagation();
      deleteError(err.id);
    });

    tbody.appendChild(tr);
  }
}

// ── Rendu du graphique en barres ─────────────────────────────────
function renderChart(byType) {
  const container = $("chart-types");
  container.innerHTML = "";

  if (!byType || byType.length === 0) {
    container.innerHTML = `<p style="color:var(--muted)">Aucune donnée.</p>`;
    return;
  }

  const max = byType[0].count;

  for (const item of byType) {
    const pct = max > 0 ? (item.count / max) * 100 : 0;
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <span class="bar-label">${item.type}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:${pct}%"></div>
      </div>
      <span class="bar-count">${item.count}</span>
    `;
    container.appendChild(row);
  }
}

// ── Rendu des stats ──────────────────────────────────────────────
function renderStats(stats, errors) {
  setText("stat-total",    stats.total ?? 0);
  $("total-badge").textContent = `${stats.total ?? 0} erreur${stats.total !== 1 ? "s" : ""}`;

  const topType = stats.by_type?.[0];
  setText("stat-top-type", topType ? `${topType.type} (${topType.count})` : "—");

  const topFile = stats.by_file?.[0];
  const shortFile = topFile
    ? topFile.file.split(/[\\/]/).pop() + ` (${topFile.count})`
    : "—";
  setText("stat-top-file", shortFile);

  const today = new Date().toISOString().slice(0, 10);
  const todayEntry = stats.recent?.find((r) => r.day === today);
  setText("stat-today", todayEntry ? todayEntry.count : 0);
}

// ── Panneau de détail ────────────────────────────────────────────
function openDetail(err) {
  setText("detail-type",        err.type);
  setText("detail-message",     err.message);
  setText("detail-file",        err.file || "—");
  setText("detail-line",        err.line ?? "—");
  setText("detail-description", err.description || "—");

  $("detail-solution").textContent = err.solution || "—";
  $("detail-conseil").textContent  = err.conseil  || "—";

  $("detail-panel").classList.remove("hidden");
  $("overlay").classList.remove("hidden");
}

function closeDetail() {
  $("detail-panel").classList.add("hidden");
  $("overlay").classList.add("hidden");
}

// ── Communication avec l'extension / backend ──────────────────────
function postMessage(type, payload = {}) {
  if (vscode) {
    vscode.postMessage({ type, ...payload });
  }
}

function deleteError(id) {
  postMessage("delete_error", { id });
  // Refresh local si données disponibles immédiatement
  refresh();
}

function refresh() {
  postMessage("refresh");
}

function clearAll() {
  if (!confirm("Supprimer toutes les erreurs ?")) return;
  postMessage("clear_all");
}

// ── Réception des messages de l'extension ────────────────────────
window.addEventListener("message", (event) => {
  const msg = event.data;

  if (msg.type === "update") {
    renderStats(msg.stats, msg.errors);
    renderChart(msg.stats.by_type);
    renderTable(msg.errors);
  }
});

// ── Données injectées en mode standalone (sans VS Code) ──────────
function loadStandaloneData() {
  if (typeof window.CLARIFY_DATA !== "undefined") {
    renderStats(window.CLARIFY_DATA.stats, window.CLARIFY_DATA.errors);
    renderChart(window.CLARIFY_DATA.stats.by_type);
    renderTable(window.CLARIFY_DATA.errors);
  }
}

// ── Initialisation ───────────────────────────────────────────────
$("btn-refresh").addEventListener("click", refresh);
$("btn-clear").addEventListener("click", clearAll);
$("detail-close").addEventListener("click", closeDetail);
$("overlay").addEventListener("click", closeDetail);

// Les données sont déjà dans window.CLARIFY_DATA (injectées par le backend).
// On ne demande pas de refresh au chargement pour éviter la boucle infinie.
loadStandaloneData();
