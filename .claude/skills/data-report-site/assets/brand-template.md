# Brand tokens — template & presets

Fill ONE token set and inject it into the page's CSS `:root`. Swapping brands = swapping this set; no other file should carry brand values. Colours are hex; font is a CSS font-family plus an optional webfont `<link>`.

## Token contract

| Token | Role |
|-------|------|
| `brand` | Primary/accent — hero band, active tab, primary chart series, key numbers |
| `ink` | Primary body text |
| `muted` | Secondary text, captions, micro-headers |
| `line` | Hairlines, borders, gridlines |
| `bg` | Page background |
| `card` | Card / panel surface |
| `up` | **Good** delta (often green) |
| `down` | **Bad** delta (often red) |
| `font` | CSS font-family stack |
| `font_link` | Webfont stylesheet URL (optional; omit if using system fonts) |
| `logo` | Path/URL to a logo for the hero (optional) |
| `series` | Ordered categorical palette for multi-series charts — validate with the `dataviz` skill for contrast + colourblind-safety |

**Rules**
- Delta colours encode **good/bad, not up/down**. Wire to metric polarity.
- Don't invent a brand. With no brand given, use **Neutral default** below and state that assumption on the page.
- After filling, check no distinctive values from a starting preset leaked (e.g. another client's accent).

## Fill-in (copy and complete)

```python
BRAND = {
    "name":  "____",
    "brand": "#______",
    "ink":   "#______",
    "muted": "#______",
    "line":  "#______",
    "bg":    "#______",
    "card":  "#FFFFFF",
    "up":    "#______",
    "down":  "#______",
    "font":  "'____', system-ui, sans-serif",
    "font_link": "https://fonts.googleapis.com/css2?family=____:wght@400;600;800&display=swap",
    "logo":  None,
    "series": ["#______", "#______", "#______"],  # validate with dataviz skill
}
```

## Presets

### Neutral default (brand-agnostic, safe when none specified)
```python
BRAND = {
    "name": "Report", "brand": "#2563EB", "ink": "#1F2933", "muted": "#6B7280",
    "line": "#E5E7EB", "bg": "#F9FAFB", "card": "#FFFFFF", "up": "#15803D", "down": "#B91C1C",
    "font": "'Inter', system-ui, sans-serif",
    "font_link": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap",
    "logo": None, "series": ["#2563EB", "#0D9488", "#CA8A04"],
}
```

### JET (Just Eat Takeaway)
```python
BRAND = {
    "name": "JET", "brand": "#FF8000", "ink": "#242E30", "muted": "#6B7678",
    "line": "#ECE7E1", "bg": "#FBF8F4", "card": "#FFFFFF", "up": "#1F8A53", "down": "#C0392B",
    "font": "'Inter', system-ui, sans-serif",
    "font_link": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap",
    "logo": None, "series": ["#FF8000", "#2B6CB0", "#1F8A53"],  # DE / GB / NL
}
```
(For JET work, the `jet-reporting-site` skill ships this preset ready to go.)

For chart colour choices, contrast, and colourblind-safe palettes, defer to the `dataviz` skill rather than hand-picking `series` here.
