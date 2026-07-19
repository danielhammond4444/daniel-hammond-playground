#!/usr/bin/env python3
"""
Minimal, complete example of a BRAND-CUSTOMISABLE build step for a data report site.

Same reusable frame as the JET version, but branding is a parameter:
  - one BRAND dict drives every colour/font (injected into CSS :root) — no hardcoded hex
  - stdlib only (csv, json, datetime) — no network, no auth, runs offline
  - reads committed CSVs, writes ONE self-contained index.html
  - config-driven metrics via (field, label, kind, delta_mode, higher_is_better) tuples
  - reporting period from a flag column, not today's date
  - a required Methodology section that traces every number

Run:
    python3 example_build.py --data ./data --out ./index.html            # neutral default brand
    python3 example_build.py --data ./data --out ./index.html --brand jet # JET preset

CSV shape expected (Data_Support.csv):
    region,month,is_last_month,is_month_minus2,tickets,avg_resolution_hours,csat_pct,first_contact_resolution_pct
Per-domain part you WILL rewrite: METRICS, load_rows(), bespoke sections. Everything else is generic.
"""
import argparse, csv, json, os
from datetime import datetime, timezone

# --- BRAND: swap this whole dict to rebrand. See assets/brand-template.md. -----
BRANDS = {
    "neutral": {
        "name": "Report", "brand": "#2563EB", "ink": "#1F2933", "muted": "#6B7280",
        "line": "#E5E7EB", "bg": "#F9FAFB", "card": "#FFFFFF", "up": "#15803D", "down": "#B91C1C",
        "font": "'Inter', system-ui, sans-serif",
        "font_link": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap",
    },
    "jet": {
        "name": "JET", "brand": "#FF8000", "ink": "#242E30", "muted": "#6B7678",
        "line": "#ECE7E1", "bg": "#FBF8F4", "card": "#FFFFFF", "up": "#1F8A53", "down": "#C0392B",
        "font": "'Inter', system-ui, sans-serif",
        "font_link": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap",
    },
}

# --- CONFIG: the only per-metric knobs. Adding a metric = adding a tuple. -----
# (source_field, display_label, kind, delta_mode, higher_is_better)
#   kind ∈ {money,int,pct}   delta_mode ∈ {rel (relative %), pp (percentage points)}
METRICS = [
    ("tickets",                        "Tickets",              "int",   "rel", None),   # neutral polarity
    ("csat_pct",                       "CSAT",                 "pct",   "pp",  True),
    ("first_contact_resolution_pct",   "First-contact resln.", "pct",   "pp",  True),
    ("avg_resolution_hours",           "Avg resolution (h)",   "int",   "rel", False),  # lower is better
]

# --- generic helpers ----------------------------------------------------------
def to_bool(v): return str(v).strip().upper() == "TRUE"
def num(v):
    v = str(v).strip()
    if v == "": return None
    f = float(v); return int(f) if f.is_integer() else f

def fmt(kind, v):
    if v is None: return "—"
    if kind == "money": return f"£{v:,.0f}"
    if kind == "pct":   return f"{v:.1f}%"
    return f"{v:,.0f}"

def delta(cur, prev, mode):
    if cur is None or prev is None: return "—", 0
    if mode == "pp":
        d = cur - prev; return f"{d:+.1f}pp", (d > 0) - (d < 0)
    if prev == 0: return "—", 0
    d = (cur - prev) / prev * 100; return f"{d:+.1f}%", (d > 0) - (d < 0)

def badge_class(sign, higher_is_better):
    if sign == 0 or higher_is_better is None: return "flat"
    return "up" if ((sign > 0) == higher_is_better) else "down"   # good/bad, not up/down

# --- per-domain load (rewrite for your data) ----------------------------------
def load_rows(data_dir, fname):
    with open(os.path.join(data_dir, fname), newline="") as f:
        return list(csv.DictReader(f))

def reporting_rows(rows):
    cur  = [r for r in rows if to_bool(r["is_last_month"])]
    prev = [r for r in rows if to_bool(r["is_month_minus2"])]
    if not cur:
        raise SystemExit("VERIFY FAIL: no row flagged is_last_month — cannot pick reporting period.")
    return cur, prev

# --- build --------------------------------------------------------------------
def build(data_dir):
    support = load_rows(data_dir, "Data_Support.csv")
    cur, prev = reporting_rows(support)
    tiles = []
    for field, label, kind, mode, hib in METRICS:
        c = sum(num(r[field]) or 0 for r in cur)
        p = sum(num(r[field]) or 0 for r in prev) if prev else None
        if kind == "pct":  # ticket-weight the rate metrics
            cw = sum(num(r["tickets"]) or 0 for r in cur) or 1
            c = sum((num(r[field]) or 0) * (num(r["tickets"]) or 0) for r in cur) / cw
            if prev:
                pw = sum(num(r["tickets"]) or 0 for r in prev) or 1
                p = sum((num(r[field]) or 0) * (num(r["tickets"]) or 0) for r in prev) / pw
        dtext, sign = delta(c, p, mode)
        tiles.append({"label": label, "value": fmt(kind, c), "delta": dtext, "cls": badge_class(sign, hib)})
    return {
        "period": cur[0]["month"], "tiles": tiles,
        "definitions": [{"label": l, "field": f, "kind": k} for f, l, k, m, h in METRICS],
        "rowcounts": {"Data_Support.csv": len(support)},
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
    }

# --- single self-contained page; brand injected, nothing hardcoded ------------
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__NAME__ — Support Performance</title>
__FONT_LINK__
<style>
:root{__ROOT__}
*{box-sizing:border-box}body{margin:0;font-family:var(--font);background:var(--bg);color:var(--ink)}
.hero{background:var(--brand);color:#fff;padding:28px 24px}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;opacity:.9}
.wrap{max-width:960px;margin:0 auto;padding:24px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.val{font-size:28px;font-weight:800;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:600}
.up{background:color-mix(in srgb,var(--up) 15%,#fff);color:var(--up)}
.down{background:color-mix(in srgb,var(--down) 15%,#fff);color:var(--down)}
.flat{background:#eee;color:var(--muted)}
h2{text-transform:uppercase;letter-spacing:.06em;font-size:13px;color:var(--muted);margin-top:32px}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{border-bottom:1px solid var(--line);padding:8px;text-align:left;font-size:14px}
</style></head><body>
<div class="hero"><div class="eyebrow">__NAME__ · Support Performance</div><div style="font-size:22px;font-weight:800">Reporting period __PERIOD__</div></div>
<div class="wrap">
<div class="tiles" id="tiles"></div>
<h2>Methodology</h2>
<div class="card" id="method"></div>
</div>
<script>const D=__PAYLOAD__;
document.getElementById('tiles').innerHTML=D.tiles.map(t=>
 `<div class="card"><div class="eyebrow" style="color:var(--muted)">${t.label}</div>
  <div class="val">${t.value}</div><span class="badge ${t.cls}">${t.delta} MoM</span></div>`).join('');
document.getElementById('method').innerHTML=
 `<p>Reporting period = rows flagged <code>is_last_month</code>; deltas compare to rows flagged <code>is_month_minus2</code>.
  Rate metrics are ticket-weighted. Delta colour reflects good/bad, not up/down.</p>
  <p>Rows loaded: ${Object.entries(D.rowcounts).map(([k,v])=>k+': '+v).join(', ')}. Built ${D.built}.</p>
  <table><tr><th>Metric</th><th>Source field</th><th>Type</th></tr>
  ${D.definitions.map(d=>`<tr><td>${d.label}</td><td><code>${d.field}</code></td><td>${d.kind}</td></tr>`).join('')}</table>`;
</script></body></html>"""

def root_css(brand):
    keys = ["brand", "ink", "muted", "line", "bg", "card", "up", "down"]
    vars_ = "".join(f"--{k}:{brand[k]};" for k in keys)
    return vars_ + f"--font:{brand['font']};"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="./data")
    ap.add_argument("--out", default="./index.html")
    ap.add_argument("--brand", default="neutral", help="preset name, or path to a JSON brand file")
    a = ap.parse_args()

    if os.path.isfile(a.brand):
        with open(a.brand) as f: brand = json.load(f)
    elif a.brand in BRANDS:
        brand = BRANDS[a.brand]
    else:
        raise SystemExit(f"Unknown brand '{a.brand}'. Presets: {', '.join(BRANDS)}, or pass a JSON file path.")

    payload = build(a.data)
    link = f'<link href="{brand["font_link"]}" rel="stylesheet">' if brand.get("font_link") else ""
    html = (PAGE
            .replace("__NAME__", brand.get("name", "Report"))
            .replace("__FONT_LINK__", link)
            .replace("__ROOT__", root_css(brand))
            .replace("__PERIOD__", payload["period"])
            .replace("__PAYLOAD__", json.dumps(payload)))
    with open(a.out, "w") as f:
        f.write(html)
    print(f"Wrote {a.out} — brand '{brand.get('name')}', period {payload['period']}, {len(payload['tiles'])} tiles.")

if __name__ == "__main__":
    main()
