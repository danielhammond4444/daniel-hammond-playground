---
name: data-report-site
description: Use when building a shareable website, dashboard, or report from a dataset — CSV, spreadsheet, or Google Sheet — for any brand or white-label context, such as a recurring metrics report, leadership dashboard, or client-branded static data site. Triggers include "build a data website", "turn this sheet into a report", "dashboard from CSV/Excel", "branded/white-label report", "custom brand template", "publish data to GitHub Pages".
---

# Data Report Site (brand-customisable)

## Overview

Build a data-driven website as a **fetch → CSV → single static HTML** pipeline: pull the source into committed CSVs, then generate one self-contained `index.html` from those CSVs with a stdlib-only build. The CSV layer is the durable, offline-reproducible interface between "where the data lives" (auth, VPN, changing sources) and "what gets published" (a static page anyone can host).

Branding is a **parameter**, not a hardcoded default: colours, fonts, and logo come from a brand-tokens file you fill in during intake, so the same pipeline produces a JET report, a client-branded deck, or a neutral internal dashboard.

**Core principle:** A capable agent will produce a good-looking page unprompted. What it skips — and what this skill enforces — is the judgment that makes the result *correct, traceable, refreshable, and on-brand*: intake (including brand) before building, provenance in the page, and output-sanity verification (not just "the code runs").

**For JET-specific work**, the `jet-reporting-site` skill is this pipeline pre-loaded with the JET brand preset — use it instead when the deliverable is JET-branded and you don't need to customise.

## When to use

- Turning a spreadsheet / Google Sheet / CSV export into a published report or dashboard, for any brand
- Recurring metrics reports (monthly/weekly) that need a repeatable refresh
- Client-branded or white-label static data sites hosted on GitHub Pages / S3 / Netlify

**Not for:** interactive apps with a backend/database, real-time data, or user-specific views. This produces a static, point-in-time (or on-refresh) artifact.

## Step 0 — Intake gate (REQUIRED before building)

Do not start building until these are answered. Ask the user; if you must proceed on assumptions, state each assumption explicitly in your response AND in the page's methodology section. The single biggest failure mode is guessing these.

1. **Source & access** — where does the data actually come from, and how is it accessed? (public CSV, private Google Sheet needing auth/VPN, DB export). This determines whether you need a `fetch` step and what it can reach.
2. **Markets / dimensions** — which segments, regions, or breakdowns are in scope.
3. **Metrics** — the exact list, each with: display label, unit/kind (money / integer / percentage), and **delta polarity** (is "up" good, bad, or neutral? e.g. resolution-time down is good).
4. **Time window & reporting period** — how is "the reporting period" chosen (a flag column? latest complete month?), and does every metric share it or do some lag intentionally.
5. **Deliverable surface** — single page vs tabs; which sections; hosting target.
6. **Brand** — which brand? Fill the brand-tokens file ([assets/brand-template.md](assets/brand-template.md)): primary/accent, text, background, card, good/bad delta colours, font (+ webfont link), optional logo. If no brand is given, use the neutral default preset and say so — do **not** silently borrow another org's brand (e.g. JET orange).
7. **Cadence & refresh owner** — one-off or recurring; who refreshes and how; is publishing manual or automated.

## Architecture contract

```
source (sheet/db/api) ──[fetch step]──▶ data/Data_<domain>.csv  ──[build step]──▶ index.html
        auth/VPN/creds live here          durable committed interface        pure stdlib, offline, no auth
```

- **Split fetch from build.** Fetch handles auth/network and writes CSVs. Build reads only CSVs and writes HTML — no network, no credentials, reproducible offline and in CI. Never fold fetching into the build.
- **CSV is the durable interface.** Commit the CSVs. They are the snapshot the build (and any CI fallback) works from. This is why the site rebuilds without touching the live source.
- **One self-contained `index.html`.** Inline the data as a JSON payload and inline CSS; a single CDN `<script>` (e.g. Chart.js) is fine. Prefer one shareable file over emitting separate `data.js` / helper files.
- **Config-driven metrics.** Define metrics as tuples — `(source_field, display_label, kind, delta_mode)` where `kind ∈ {money,int,pct}` and `delta_mode ∈ {rel, pp}` (relative % vs percentage-point). Adding a metric = adding a tuple, not new rendering code.
- **Brand-driven styling.** Read brand tokens from one config object (a dict or JSON) and inject them into the page's CSS `:root` — never scatter hardcoded hex/font values through the template. Swapping brands = swapping the token set. See [assets/example_build.py](assets/example_build.py) for a complete runnable example that parameterises brand this way.
- **Reporting period from a flag, not "today".** Derive the reporting period from an explicit flag column in the data (e.g. `is_last_month`) and compare to a prior-period flag. Never infer it from the current date — partial current periods must be excluded deliberately.

## Brand tokens

The brand is defined once, in a token set the build injects into the page. Fill [assets/brand-template.md](assets/brand-template.md), which carries the token contract plus ready presets (neutral default, JET). Rules:

- **Every brand-affecting value comes from a token.** `--brand`, `--ink`, `--muted`, `--line`, `--bg`, `--card`, `--up` (good delta), `--down` (bad delta), font family + webfont link, and optional logo.
- **Delta colour = good/bad, not up/down.** For a metric where lower is better (resolution time, cost), a decrease shows the `--up` colour. Wire this to the metric's polarity, not the sign of the change.
- **Validate the categorical/series palette** (for multi-series charts) with the `dataviz` skill — contrast and colourblind-safety, not just brand match. Don't hardcode series colours here.
- **No brand leakage.** If a preset was used as a starting point, confirm none of its distinctive values (e.g. a previous client's accent) remain unless intended.

## Methodology section (REQUIRED in the output)

Every published number must be traceable. Include a methodology/definitions section on the page containing:
- Source link/name and which tabs/files were consumed, with **row counts** actually loaded
- The reporting-period rule ("reporting period = the row flagged X; deltas compare to Y")
- A **definitions table** mapping each displayed label to its source field and meaning
- The **formulas** used (e.g. relative delta vs percentage-point delta)
- Any intentional gaps ("segment Z tracked from May 2026 onward")

If a metric can't be traced this way, it doesn't go on the page.

## Verification gates (output sanity, not just "code runs")

Passing a syntax check or a DOM shim proves the code executes — it does **not** prove the report is correct. Before calling it done, confirm:

1. **Freshness** — is the reporting period the latest *complete* period? Did it actually advance from the previous build?
2. **Population** — are tiles/tables populated, or are values silently blank / "—"? A source-column rename degrades metrics to blank without erroring. Empty tiles = failed build, even if exit code is 0.
3. **Brand applied** — do the rendered colours/font match the intended brand tokens, with no leftover placeholder or borrowed-brand values?
4. **Intentional gaps** — is any missing/lagging data deliberate (per intake) rather than a bug?
5. **Sanity** — do headline numbers match a hand calculation on a couple of rows?
6. **Renders** — actually view the page (preview server / browser), not just parse it.

**REQUIRED SUB-SKILL:** use `superpowers:verification-before-completion` — evidence before claiming done.

## Guardrails (side effects are opt-in)

- **Do not push, deploy, schedule, or send** anything without explicit approval. Build and verify locally, then stop and report — publishing is the user's call.
- **Read-only on the source.** Export/download only; never write back to the sheet/DB.
- **Don't "fix" deliberate knobs** (a pinned start month, a metric intentionally lacking MoM). Confirm before changing config that looks like a mistake.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Building before intake — guessing metrics/audience/polarity/brand | Answer Step 0 first; state any assumption in the page |
| Defaulting to a familiar brand (e.g. JET orange) with no instruction | Use the neutral preset and say so; brand is an intake question |
| Hardcoding hex/font through the template | All brand values come from one token set injected into `:root` |
| Brand leakage from a preset starting point | Verify no distinctive prior-brand values remain |
| No methodology section — numbers untraceable | Required section: source, row counts, definitions, formulas |
| "It runs" treated as "it's correct" | Run the output-sanity gates; empty tiles = failure |
| Fetching inside the build step | Split fetch (auth) from build (offline, stdlib) |
| Emitting multiple files (index.html + data.js) | Inline the payload into one self-contained HTML |
| Reporting period from `today` | Derive from an explicit flag column |
| Pushing/deploying without asking | Side effects are opt-in; build, verify, stop |
