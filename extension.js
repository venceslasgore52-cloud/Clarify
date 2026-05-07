/**
 * extension.js — Point d'entrée de l'extension VS Code Clarify.
 *
 * Responsabilités :
 *  - Lancer le backend Python (core.activate) dans un terminal intégré
 *  - Ouvrir et rafraîchir le WebviewPanel du dashboard
 *  - Écouter les messages du webview (refresh, delete, clear)
 *  - Proposer les commandes via la palette de commandes
 */

"use strict";

const vscode = require("vscode");
const path   = require("node:path");
const { execFile } = require("node:child_process");

// ── Constantes ──────────────────────────────────────────────────────────────
const EXT_ID        = "clarify";
const DASHBOARD_CMD = "clarify.showDashboard";
const ANALYSE_CMD   = "clarify.analyseFile";
const CLEAR_CMD     = "clarify.clearErrors";
const LANG_CMD      = "clarify.setLanguage";

/** @type {vscode.WebviewPanel | undefined} */
let dashboardPanel;

/** @type {vscode.OutputChannel} */
let outputChannel;

// ── Activation ──────────────────────────────────────────────────────────────
/**
 * Appelée par VS Code au démarrage de l'extension (onLanguage:python).
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  outputChannel = vscode.window.createOutputChannel("Clarify");
  outputChannel.appendLine("[Clarify] Extension activée.");

  context.subscriptions.push(
    // Commande : ouvrir le dashboard
    vscode.commands.registerCommand(DASHBOARD_CMD, () => openDashboard(context)),

    // Commande : analyser le fichier Python actif
    vscode.commands.registerCommand(ANALYSE_CMD, () => analyseCurrentFile(context)),

    // Commande : effacer toutes les erreurs
    vscode.commands.registerCommand(CLEAR_CMD, () => {
      runPython(context, ["-c", "import sys,os; sys.path.insert(0,'.'); from src.database.queries import clear_all_errors; n=clear_all_errors(); print(f'{n} erreur(s) supprimée(s).')"])
        .then((out) => {
          vscode.window.showInformationMessage(`Clarify — ${out.trim()}`);
          refreshDashboard(context);
        });
    }),

    // Commande : changer la langue
    vscode.commands.registerCommand(LANG_CMD, async () => {
      const langs = [
        { label: "$(symbol-keyword) Auto (système)", value: "auto" },
        { label: "Français",   value: "fr" },
        { label: "English",    value: "en" },
        { label: "中文",        value: "zh" },
        { label: "العربية",    value: "ar" },
        { label: "Português",  value: "pt" },
        { label: "Español",    value: "es" },
      ];
      const pick = await vscode.window.showQuickPick(langs, {
        placeHolder: "Choisir la langue d'affichage de Clarify",
      });
      if (pick) {
        const config = vscode.workspace.getConfiguration(EXT_ID);
        await config.update("language", pick.value, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage(`Clarify — Langue définie : ${pick.label}`);
        refreshDashboard(context);
      }
    })
  );

  // Ouvre automatiquement le dashboard si autoActivate est activé
  const config = vscode.workspace.getConfiguration(EXT_ID);
  if (config.get("autoActivate")) {
    openDashboard(context);
  }
}

// ── Dashboard Webview ────────────────────────────────────────────────────────
/**
 * Ouvre ou révèle le panel WebView du dashboard.
 * @param {vscode.ExtensionContext} context
 */
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
      enableScripts:          true,
      localResourceRoots:     [vscode.Uri.file(path.join(context.extensionPath, "webview"))],
      retainContextWhenHidden: true,
    }
  );

  // Nettoyage quand le panel est fermé
  dashboardPanel.onDidDispose(() => {
    dashboardPanel = undefined;
  }, null, context.subscriptions);

  // Réception des messages du webview JS
  dashboardPanel.webview.onDidReceiveMessage(
    (message) => handleWebviewMessage(message, context),
    null,
    context.subscriptions
  );

  refreshDashboard(context);
}

/**
 * Charge les données Python et les envoie au webview.
 * @param {vscode.ExtensionContext} context
 */
function refreshDashboard(context) {
  if (!dashboardPanel) return;

  // Récupère le HTML complet généré par reporter.dashboard
  runPython(context, [
    "-c",
    [
      "import sys, os",
      "sys.path.insert(0, os.getcwd())",
      "from src.reporter.dashboard import get_webview_html",
      "print(get_webview_html(), end='')",
    ].join("; "),
  ]).then((html) => {
    if (dashboardPanel && html) {
      dashboardPanel.webview.html = html;
    }
  }).catch((err) => {
    outputChannel.appendLine(`[Clarify] Erreur dashboard : ${err}`);
  });
}

// ── Messages du webview ──────────────────────────────────────────────────────
/**
 * Traite les messages postMessage() envoyés depuis dashboard.js.
 */
function handleWebviewMessage(message, context) {
  switch (message.type) {

    case "ready":
    case "refresh":
      refreshDashboard(context);
      break;

    case "delete_error":
      runPython(context, [
        "-c",
        `import sys,os; sys.path.insert(0,os.getcwd()); from src.database.queries import delete_error; delete_error(${message.id})`,
      ]).then(() => refreshDashboard(context));
      break;

    case "clear_all":
      runPython(context, [
        "-c",
        "import sys,os; sys.path.insert(0,os.getcwd()); from src.database.queries import clear_all_errors; clear_all_errors()",
      ]).then(() => refreshDashboard(context));
      break;

    case "open_file":
      if (message.file && message.line) {
        const uri = vscode.Uri.file(message.file);
        vscode.window.showTextDocument(uri).then((editor) => {
          const pos = new vscode.Position(Math.max(0, message.line - 1), 0);
          editor.selection = new vscode.Selection(pos, pos);
          editor.revealRange(new vscode.Range(pos, pos));
        });
      }
      break;
  }
}

// ── Analyse fichier ──────────────────────────────────────────────────────────
/**
 * Lance une analyse Clarify sur le fichier Python actif.
 */
function analyseCurrentFile(context) {
  const editor = vscode.window.activeTextEditor;
  if (editor?.document.languageId !== "python") {
    vscode.window.showWarningMessage("Clarify — Ouvrez un fichier Python pour l'analyser.");
    return;
  }

  const filePath = editor.document.uri.fsPath;
  vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: "Clarify — Analyse en cours…" },
    () => runPython(context, [filePath])
      .then(() => {
        refreshDashboard(context);
        vscode.window.showInformationMessage("Clarify — Analyse terminée.");
      })
      .catch((err) => {
        outputChannel.appendLine(`[Clarify] Erreur analyse : ${err}`);
      })
  );
}

// ── Utilitaire Python ────────────────────────────────────────────────────────
/**
 * Exécute Python avec les arguments donnés dans le dossier du workspace.
 * Utilise le pythonPath configuré ou détecte automatiquement.
 *
 * @param {vscode.ExtensionContext} context
 * @param {string[]} args
 * @returns {Promise<string>} stdout
 */
function runPython(context, args) {
  return new Promise((resolve, reject) => {
    const config     = vscode.workspace.getConfiguration(EXT_ID);
    const pythonPath = config.get("pythonPath") || detectPython();
    const lang       = config.get("language") || "auto";
    const cwd        = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || context.extensionPath;

    const env = { ...process.env, CLARIFY_LANG: lang === "auto" ? "" : lang };

    execFile(pythonPath, ["-X", "utf8", ...args], { cwd, env }, (err, stdout, stderr) => {
      if (stderr) outputChannel.appendLine(`[Clarify][stderr] ${stderr}`);
      if (err)    reject(err);
      else        resolve(stdout);
    });
  });
}

/**
 * Détecte l'interpréteur Python disponible sur le système.
 */
function detectPython() {
  return process.platform === "win32" ? "python" : "python3";
}

// ── Désactivation ────────────────────────────────────────────────────────────
function deactivate() {
  outputChannel?.appendLine("[Clarify] Extension désactivée.");
  dashboardPanel?.dispose();
}

module.exports = { activate, deactivate };
