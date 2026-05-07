"use strict";

const vscode    = require("vscode");
const path      = require("node:path");
const { execFile } = require("node:child_process");

const EXT_ID        = "clarify";
const DASHBOARD_CMD = "clarify.showDashboard";
const ANALYSE_CMD   = "clarify.analyseFile";
const CLEAR_CMD     = "clarify.clearErrors";
const LANG_CMD      = "clarify.setLanguage";

/** @type {vscode.WebviewPanel | undefined} */
let dashboardPanel;
/** @type {vscode.OutputChannel} */
let outputChannel;
/** @type {string} chemin absolu du dossier de l'extension */
let EXT_PATH;

// ── Activation ───────────────────────────────────────────────────
function activate(context) {
  EXT_PATH      = context.extensionPath;
  outputChannel = vscode.window.createOutputChannel("Clarify");
  outputChannel.appendLine(`[Clarify] Activée — ${EXT_PATH}`);

  context.subscriptions.push(
    vscode.commands.registerCommand(DASHBOARD_CMD, () => openDashboard(context)),
    vscode.commands.registerCommand(ANALYSE_CMD,   () => analyseCurrentFile(context)),
    vscode.commands.registerCommand(CLEAR_CMD,     () => clearErrors(context)),
    vscode.commands.registerCommand(LANG_CMD,      () => pickLanguage(context))
  );

  // Bouton dans la barre de statut pour ouvrir le dashboard rapidement
  const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBar.text    = "⬡ Clarify";
  statusBar.tooltip = "Ouvrir le dashboard Clarify";
  statusBar.command = DASHBOARD_CMD;
  statusBar.show();
  context.subscriptions.push(statusBar);

  // activate() se termine immédiatement — Python ne se lance qu'à la demande
  outputChannel.appendLine("[Clarify] Prête — clique sur ⬡ Clarify ou Ctrl+Shift+P");
}

// ── Dashboard ────────────────────────────────────────────────────
function openDashboard(context) {
  if (dashboardPanel) {
    dashboardPanel.reveal(vscode.ViewColumn.Two);
    refreshDashboard(context);
    return;
  }

  dashboardPanel = vscode.window.createWebviewPanel(
    "clarifyDashboard",
    "Clarify — Dashboard",
    vscode.ViewColumn.Two,
    {
      enableScripts:           true,
      localResourceRoots:      [vscode.Uri.file(path.join(EXT_PATH, "webview"))],
      retainContextWhenHidden: true,
    }
  );

  // Affiche un écran de chargement immédiatement
  dashboardPanel.webview.html = loadingHtml();

  dashboardPanel.onDidDispose(() => { dashboardPanel = undefined; }, null, context.subscriptions);
  dashboardPanel.webview.onDidReceiveMessage(
    (msg) => handleMessage(msg, context), null, context.subscriptions
  );

  refreshDashboard(context);
}

function refreshDashboard(context) {
  if (!dashboardPanel) return;

  // EXT_PATH est passé directement au script Python — aucune ambiguïté de CWD
  const script = [
    `import sys`,
    `sys.path.insert(0, r'${EXT_PATH.replace(/\\/g, "\\\\")}')`,
    `from src.reporter.dashboard import get_webview_html`,
    `print(get_webview_html(), end='')`,
  ].join("; ");

  runPython(["-c", script])
    .then((html) => {
      if (dashboardPanel && html.trim()) {
        dashboardPanel.webview.html = html;
      } else if (dashboardPanel) {
        dashboardPanel.webview.html = errorHtml("Dashboard vide — aucune erreur enregistrée.");
      }
    })
    .catch((err) => {
      outputChannel.appendLine(`[Clarify] Dashboard error: ${err.message}`);
      if (dashboardPanel) {
        dashboardPanel.webview.html = errorHtml(err.message);
      }
    });
}

// ── Messages du webview ──────────────────────────────────────────
function handleMessage(msg, context) {
  const extPathEsc = EXT_PATH.replace(/\\/g, "\\\\");
  const header     = `import sys; sys.path.insert(0, r'${extPathEsc}')`;

  switch (msg.type) {
    case "ready":
    case "refresh":
      refreshDashboard(context);
      break;

    case "delete_error":
      runPython(["-c", `${header}; from src.database.queries import delete_error; delete_error(${Number(msg.id)})`])
        .then(() => refreshDashboard(context))
        .catch((e) => outputChannel.appendLine(`[Clarify] delete error: ${e.message}`));
      break;

    case "clear_all":
      runPython(["-c", `${header}; from src.database.queries import clear_all_errors; clear_all_errors()`])
        .then(() => refreshDashboard(context))
        .catch((e) => outputChannel.appendLine(`[Clarify] clear error: ${e.message}`));
      break;

    case "open_file":
      if (msg.file && msg.line) {
        const uri = vscode.Uri.file(msg.file);
        vscode.window.showTextDocument(uri).then((editor) => {
          const pos = new vscode.Position(Math.max(0, msg.line - 1), 0);
          editor.selection = new vscode.Selection(pos, pos);
          editor.revealRange(new vscode.Range(pos, pos));
        });
      }
      break;
  }
}

// ── Commandes ────────────────────────────────────────────────────
function clearErrors(context) {
  const extPathEsc = EXT_PATH.replace(/\\/g, "\\\\");
  runPython(["-c",
    `import sys; sys.path.insert(0, r'${extPathEsc}'); from src.database.queries import clear_all_errors; n=clear_all_errors(); print(n)`
  ])
    .then((out) => {
      vscode.window.showInformationMessage(`Clarify — ${out.trim()} erreur(s) supprimée(s).`);
      refreshDashboard(context);
    })
    .catch((e) => outputChannel.appendLine(`[Clarify] clear error: ${e.message}`));
}

async function pickLanguage(context) {
  const langs = [
    { label: "Auto (système)", value: "auto" },
    { label: "Français",       value: "fr"   },
    { label: "English",        value: "en"   },
    { label: "中文",            value: "zh"   },
    { label: "العربية",        value: "ar"   },
    { label: "Português",      value: "pt"   },
    { label: "Español",        value: "es"   },
  ];
  const pick = await vscode.window.showQuickPick(langs, {
    placeHolder: "Choisir la langue Clarify",
  });
  if (!pick) return;
  const config = vscode.workspace.getConfiguration(EXT_ID);
  await config.update("language", pick.value, vscode.ConfigurationTarget.Global);
  vscode.window.showInformationMessage(`Clarify — Langue : ${pick.label}`);
  refreshDashboard(context);
}

function analyseCurrentFile(context) {
  const editor = vscode.window.activeTextEditor;
  if (editor?.document.languageId !== "python") {
    vscode.window.showWarningMessage("Clarify — Ouvrez un fichier Python.");
    return;
  }
  const filePath    = editor.document.uri.fsPath;
  const extPathEsc  = EXT_PATH.replace(/\\/g, "\\\\");
  const script = [
    `import sys`,
    `sys.path.insert(0, r'${extPathEsc}')`,
    `from src.engine.core import activate`,
    `activate()`,
    `exec(open(r'${filePath.replace(/\\/g, "\\\\")}').read())`,
  ].join("; ");

  vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: "Clarify — Analyse…" },
    () => runPython(["-c", script])
      .then(() => { refreshDashboard(context); vscode.window.showInformationMessage("Clarify — Terminé."); })
      .catch((e) => outputChannel.appendLine(`[Clarify] analyse error: ${e.message}`))
  );
}

// ── Utilitaire Python ────────────────────────────────────────────
/**
 * Exécute Python depuis EXT_PATH (toujours le dossier de l'extension).
 * @param {string[]} args
 * @returns {Promise<string>}
 */
function runPython(args) {
  return new Promise((resolve, reject) => {
    const config     = vscode.workspace.getConfiguration(EXT_ID);
    const python     = config.get("pythonPath") || (process.platform === "win32" ? "python" : "python3");
    const lang       = config.get("language") || "auto";
    const env        = { ...process.env, CLARIFY_LANG: lang === "auto" ? "" : lang };

    outputChannel.appendLine(`[Clarify] python ${args[0] === "-c" ? "-c <script>" : args.join(" ")}`);

    execFile(python, ["-X", "utf8", ...args], { cwd: EXT_PATH, env }, (err, stdout, stderr) => {
      if (stderr) outputChannel.appendLine(`[Clarify][stderr] ${stderr.trim()}`);
      if (err)    reject(err);
      else        resolve(stdout);
    });
  });
}

// ── HTML helpers ─────────────────────────────────────────────────
function loadingHtml() {
  return `<!DOCTYPE html><html><body style="background:#1e1e2e;color:#cdd6f4;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
    <div style="text-align:center">
      <div style="font-size:32px;margin-bottom:12px">⬡</div>
      <div style="color:#89b4fa;font-size:18px;font-weight:bold">Clarify</div>
      <div style="color:#6c7086;margin-top:8px">Chargement du dashboard…</div>
    </div>
  </body></html>`;
}

function errorHtml(message) {
  const safe = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return `<!DOCTYPE html><html><body style="background:#1e1e2e;color:#cdd6f4;font-family:sans-serif;padding:32px;margin:0">
    <div style="color:#89b4fa;font-size:18px;font-weight:bold;margin-bottom:16px">⬡ Clarify</div>
    <div style="background:#2a2a3d;border:1px solid #f38ba8;border-radius:8px;padding:16px">
      <div style="color:#f38ba8;font-weight:bold;margin-bottom:8px">Erreur de chargement</div>
      <pre style="color:#cdd6f4;font-size:12px;white-space:pre-wrap;margin:0">${safe}</pre>
    </div>
    <div style="color:#6c7086;margin-top:16px;font-size:12px">
      Vérifiez l'onglet <strong>Clarify</strong> dans le panneau Output pour les détails.
    </div>
  </body></html>`;
}

// ── Désactivation ────────────────────────────────────────────────
function deactivate() {
  outputChannel?.appendLine("[Clarify] Désactivée.");
  dashboardPanel?.dispose();
}

module.exports = { activate, deactivate };
