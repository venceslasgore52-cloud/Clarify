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
/** @type {string} */
let EXT_PATH;

// ── Activation ───────────────────────────────────────────────────
function activate(context) {
  EXT_PATH      = context.extensionPath;
  outputChannel = vscode.window.createOutputChannel("Clarify");
  outputChannel.appendLine(`[Clarify] Activée — ${EXT_PATH}`);
  outputChannel.show(true);

  // Notification immédiate pour confirmer l'activation
  vscode.window.showInformationMessage("⬡ Clarify activée !");

  context.subscriptions.push(
    vscode.commands.registerCommand(DASHBOARD_CMD, () => openDashboard(context)),
    vscode.commands.registerCommand(ANALYSE_CMD,   () => analyseCurrentFile(context)),
    vscode.commands.registerCommand(CLEAR_CMD,     () => clearErrors(context)),
    vscode.commands.registerCommand(LANG_CMD,      () => pickLanguage(context))
  );

  // Bouton barre de statut
  const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBar.text    = "⬡ Clarify";
  statusBar.tooltip = "Ouvrir le dashboard Clarify";
  statusBar.command = DASHBOARD_CMD;
  statusBar.show();
  context.subscriptions.push(statusBar);

  outputChannel.appendLine("[Clarify] Commandes enregistrées. Cliquez sur ⬡ Clarify.");
}

// ── Dashboard ────────────────────────────────────────────────────
function openDashboard(context) {
  outputChannel.appendLine("[Clarify] openDashboard() appelée");

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

  dashboardPanel.webview.html = loadingHtml();
  dashboardPanel.onDidDispose(() => { dashboardPanel = undefined; }, null, context.subscriptions);
  dashboardPanel.webview.onDidReceiveMessage(
    (msg) => handleMessage(msg, context), null, context.subscriptions
  );

  refreshDashboard(context);
}

function refreshDashboard(context) {
  if (!dashboardPanel) return;
  outputChannel.appendLine("[Clarify] refreshDashboard() — lancement Python...");

  const script = [
    `import sys, traceback`,
    `sys.path.insert(0, r'${EXT_PATH}')`,
    `try:`,
    `    from src.reporter.dashboard import get_webview_html`,
    `    print(get_webview_html(), end='')`,
    `except Exception:`,
    `    print('CLARIFY_ERROR:' + traceback.format_exc(), end='')`,
  ].join("\n");

  runPythonScript(script)
    .then((out) => {
      if (!dashboardPanel) return;
      outputChannel.appendLine(`[Clarify] Python répondu — ${out.length} caractères`);
      if (out.startsWith("CLARIFY_ERROR:")) {
        const detail = out.replace("CLARIFY_ERROR:", "").trim();
        outputChannel.appendLine(`[Clarify] Erreur Python:\n${detail}`);
        dashboardPanel.webview.html = errorHtml(detail);
      } else if (out.trim()) {
        dashboardPanel.webview.html = out;
      } else {
        dashboardPanel.webview.html = errorHtml("Sortie Python vide.");
      }
    })
    .catch((err) => {
      outputChannel.appendLine(`[Clarify] execFile échoué: ${err.message}`);
      if (dashboardPanel) dashboardPanel.webview.html = errorHtml(err.message);
    });
}

// ── Messages du webview ──────────────────────────────────────────
function handleMessage(msg, context) {
  const ep     = EXT_PATH.replace(/\\/g, "\\\\");
  const header = `import sys; sys.path.insert(0, r'${ep}')`;

  switch (msg.type) {
    case "ready":
    case "refresh":
      refreshDashboard(context);
      break;
    case "delete_error":
      runPythonScript(`import sys\nsys.path.insert(0, r'${EXT_PATH}')\nfrom src.database.queries import delete_error\ndelete_error(${Number(msg.id)})`)
        .then(() => refreshDashboard(context));
      break;
    case "clear_all":
      runPythonScript(`import sys\nsys.path.insert(0, r'${EXT_PATH}')\nfrom src.database.queries import clear_all_errors\nclear_all_errors()`)
        .then(() => refreshDashboard(context));
      break;
    case "open_file":
      if (msg.file && msg.line) {
        vscode.window.showTextDocument(vscode.Uri.file(msg.file)).then((editor) => {
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
  runPythonScript(
    `import sys\nsys.path.insert(0, r'${EXT_PATH}')\nfrom src.database.queries import clear_all_errors\nn=clear_all_errors()\nprint(n)`
  )
    .then((out) => {
      vscode.window.showInformationMessage(`Clarify — ${out.trim()} erreur(s) supprimée(s).`);
      refreshDashboard(context);
    })
    .catch((e) => outputChannel.appendLine(`[Clarify] clear: ${e.message}`));
}

async function pickLanguage(context) {
  const langs = [
    { label: "Auto",      value: "auto" },
    { label: "Français",  value: "fr"   },
    { label: "English",   value: "en"   },
    { label: "中文",       value: "zh"   },
    { label: "العربية",   value: "ar"   },
    { label: "Português", value: "pt"   },
    { label: "Español",   value: "es"   },
  ];
  const pick = await vscode.window.showQuickPick(langs, { placeHolder: "Langue Clarify" });
  if (!pick) return;
  await vscode.workspace.getConfiguration(EXT_ID).update("language", pick.value, vscode.ConfigurationTarget.Global);
  vscode.window.showInformationMessage(`Clarify — Langue : ${pick.label}`);
  refreshDashboard(context);
}

function analyseCurrentFile(context) {
  const editor = vscode.window.activeTextEditor;
  if (editor?.document.languageId !== "python") {
    vscode.window.showWarningMessage("Clarify — Ouvrez un fichier Python.");
    return;
  }
  const fp     = editor.document.uri.fsPath;
  const script = [
    `import sys`,
    `sys.path.insert(0, r'${EXT_PATH}')`,
    `from src.engine.core import activate`,
    `activate()`,
    `exec(open(r'${fp}').read())`,
  ].join("\n");

  vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: "Clarify — Analyse…" },
    () => runPythonScript(script)
      .then(() => { refreshDashboard(context); vscode.window.showInformationMessage("Clarify — Terminé."); })
      .catch((e) => { outputChannel.appendLine(`[Clarify] analyse: ${e.message}`); outputChannel.show(true); })
  );
}

// ── Python ───────────────────────────────────────────────────────
function detectPython() {
  const manual = vscode.workspace.getConfiguration(EXT_ID).get("pythonPath");
  if (manual) return manual;
  try {
    const pyExt = vscode.extensions.getExtension("ms-python.python");
    if (pyExt?.isActive) {
      const env = pyExt.exports?.environments?.getActiveEnvironmentPath?.();
      if (env?.path) return env.path;
    }
  } catch (_) { /* ignore */ }
  return process.platform === "win32" ? "python" : "python3";
}

function runPython(args) {
  return new Promise((resolve, reject) => {
    const python = detectPython();
    const lang   = vscode.workspace.getConfiguration(EXT_ID).get("language") || "auto";
    const env    = { ...process.env, CLARIFY_LANG: lang === "auto" ? "" : lang, PYTHONIOENCODING: "utf-8" };

    outputChannel.appendLine(`[Clarify] Exec: ${python}`);

    execFile(python, ["-X", "utf8", ...args], { cwd: EXT_PATH, env, timeout: 30000 }, (err, stdout, stderr) => {
      if (stderr) outputChannel.appendLine(`[Clarify][stderr] ${stderr.trim()}`);
      if (err)    reject(new Error(stderr || err.message));
      else        resolve(stdout);
    });
  });
}

/**
 * Écrit le script dans un fichier .py temporaire et l'exécute.
 * Évite tous les problèmes d'échappement sur Windows.
 */
function runPythonScript(script) {
  const os   = require("node:os");
  const fs   = require("node:fs");
  const tmp  = path.join(os.tmpdir(), `clarify_${Date.now()}.py`);
  fs.writeFileSync(tmp, script, "utf-8");
  return runPython([tmp]).finally(() => {
    try { fs.unlinkSync(tmp); } catch (_) {}
  });
}

// ── HTML ─────────────────────────────────────────────────────────
function loadingHtml() {
  return `<!DOCTYPE html><html><body style="background:#1e1e2e;color:#cdd6f4;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
    <div style="text-align:center">
      <div style="font-size:32px">⬡</div>
      <div style="color:#89b4fa;font-size:18px;font-weight:bold;margin-top:8px">Clarify</div>
      <div style="color:#6c7086;margin-top:8px">Chargement…</div>
    </div></body></html>`;
}

function errorHtml(msg) {
  const safe = String(msg).replace(/</g,"&lt;").replace(/>/g,"&gt;");
  return `<!DOCTYPE html><html><body style="background:#1e1e2e;color:#cdd6f4;font-family:sans-serif;padding:32px;margin:0">
    <div style="color:#89b4fa;font-size:18px;font-weight:bold;margin-bottom:16px">⬡ Clarify</div>
    <div style="background:#2a2a3d;border:1px solid #f38ba8;border-radius:8px;padding:16px">
      <div style="color:#f38ba8;font-weight:bold;margin-bottom:8px">Erreur</div>
      <pre style="color:#cdd6f4;font-size:12px;white-space:pre-wrap;margin:0">${safe}</pre>
    </div>
    <div style="color:#6c7086;margin-top:16px;font-size:12px">Voir Output &gt; Clarify pour les détails.</div>
  </body></html>`;
}

// ── Désactivation ────────────────────────────────────────────────
function deactivate() {
  outputChannel?.appendLine("[Clarify] Désactivée.");
  dashboardPanel?.dispose();
}

module.exports = { activate, deactivate };
