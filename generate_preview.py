"""Génère webview/preview.html — dashboard standalone avec les données réelles de la DB."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from src.database.queries import get_all_errors, get_stats

stats  = get_stats()
errors = [e.to_dict() for e in get_all_errors()]
data   = json.dumps({"stats": stats, "errors": errors}, ensure_ascii=False, indent=2)

base = os.path.join(os.path.dirname(__file__), "webview")

with open(os.path.join(base, "dashboard.html"), encoding="utf-8") as f:
    html = f.read()
with open(os.path.join(base, "dashboard.css"), encoding="utf-8") as f:
    css = f.read()
with open(os.path.join(base, "dashboard.js"), encoding="utf-8") as f:
    js = f.read()

html = html.replace(
    '<link rel="stylesheet" href="dashboard.css" />',
    f"<style>{css}</style>"
)
html = html.replace(
    '<script src="dashboard.js"></script>',
    f"<script>window.CLARIFY_DATA={data};</script>\n<script>{js}</script>"
)

out = os.path.join(base, "preview.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Preview generee : {out}")
print(f"{len(errors)} erreurs — {stats['total']} total")
