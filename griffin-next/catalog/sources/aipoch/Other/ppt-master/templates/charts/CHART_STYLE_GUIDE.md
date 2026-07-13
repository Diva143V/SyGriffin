# Chart SVG Style Guide

> `templates/charts/` SVG 。 
> **** ，。

## 0. 

 **** 。：

> **[`references/shared-standards.md`](../../references/shared-standards.md)** — SVG 、PPT 、Canvas 、tspan 、、/、

 shared-standards 。（ marker 、clipPath 、）。

---

## 1. (Tailwind CSS Palette)

### 1.1 

| | | Tailwind Token | |
|------|------|----------------|------|
| **** | `#0F172A` | Slate 900 | |
| **** | `#0F172A` | Slate 900 | 、 |
| **** | `#64748B` | Slate 500 | 、 |
| **** | `#64748B` | Slate 500 | X/Y |
| ** / ** | `#475569` | Slate 600 | "（）"、 |
| **** | `#94A3B8` | Slate 400 | |
| ** / ** | `#CBD5E1` | Slate 300 | "" |

### 1.2 （）

| | | （） | |
|------|------|------------------|------|
| **Blue** | `#3B82F6` | `#2563EB` | 1 （） |
| **Emerald** | `#10B981` | `#059669` | 2 |
| **Amber** | `#F59E0B` | `#D97706` | 3 |
| **Violet** | `#8B5CF6` | `#7C3AED` | 4 |
| **Rose** | `#FB7185` | `#E11D48` | 5 / |
| **Pink** | `#EC4899` | `#BE185D` | （） |

> （）：`#60A5FA`、`#34D399`、`#FBBF24`、`#A78BFA`、`#FB7185`

### 1.3 

| | | |
|------|------|------|
| / | `#10B981` | Emerald 500 |
| / | `#F59E0B` | Amber 500 |
| / | `#EF4444` | Red 500 |
| | `#F43F5E` | Rose 500 |

### 1.4 UI 

| | | |
|------|------|------|
| **** | `#94A3B8` | Slate 400, stroke-width="2" |
| **** | `#E2E8F0` `#E0E0E0` | stroke-dasharray="4,4" |
| **** | `#CBD5E1` | |
| **** | `#F8FAFC` / `#F8F9FA` | Slate 50 |
| **** | `#E2E8F0` | Slate 200 |
| **** | `#F1F5F9` | Slate 100（） |
| **Tint **（） | `#EFF6FF` | Blue 50 |
| **Tint **（） | `#ECFDF5` | Emerald 50 |
| **Tint **（） | `#FFF1F2` | Rose 50 |
| **Tint **（） | `#FFFBEB` | Amber 50 |

---

## 2. 

### 2.1 

```
font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif"
```

- `'PingFang SC', 'Microsoft YaHei'`
- **** `@font-face`、、`<style>` 

### 2.2 

| | | font-weight | |
|------|------|-------------|------|
| H1 | `34px` | `bold` (700) | |
| H2 | `22px` | `600` | （""） |
| Body L | `18-20px` | `600` | 、 |
| Body M | `15-16px` | `600` | 、 |
| Body S | `14px` | | 、、 |
| Caption | `12-13px` | | 、 |

> **：12px**。 12px。

### 2.3 tspan 

 `<text>` **** `<tspan>` ：

```xml
<!-- -->
<text x="60" y="80" font-size="34" fill="#0F172A">
 <tspan></tspan>
</text>

<!-- -->
<text x="60" y="80" font-size="34" fill="#0F172A"></text>
```

### 2.4 （shared-standards SS4）

** = `<text>`**。/， `<tspan>` ，**** `<text>`：

```xml
<!-- ： text frame， run -->
<text x="100" y="200" font-size="24" fill="#333333">
 <tspan fill="#3B82F6" font-weight="bold">10</tspan>
</text>

<!-- ： text frame，PPT -->
<text x="100" y="200"></text>
<text x="160" y="200" fill="#3B82F6">10</text>
<text x="240" y="200"></text>
```

> tspan **** `x` / `y` / `dy`， text frame。`dx` 。

### 2.5 

：
- **** — 、、 → `<tspan fill="" font-weight="bold">`
- **** — /、/ → （/）
- **** — 、、（、、）

---

## 3. 

`<filter>` 、 PPT /（""）。 primitive —— `feFlood` ，**** `<filter>` `<feComponentTransfer>`：

```xml
<filter id="chartShadow" x="-15%" y="-15%" width="130%" height="130%">
 <feGaussianBlur in="SourceAlpha" stdDeviation="2-4"/>
 <feOffset dx="0" dy="1-3" result="offsetBlur"/>
 <feFlood flood-color="#0F172A" flood-opacity="0.08-0.15" result="shadowColor"/>
 <feComposite in="shadowColor" in2="offsetBlur" operator="in" result="shadow"/>
 <feMerge>
 <feMergeNode in="shadow"/>
 <feMergeNode in="SourceGraphic"/>
 </feMerge>
</filter>
```

### 

| | stdDeviation | dy | flood-opacity |
|------|-------------|-----|---------------|
| （、） | 4-6 | 2-4 | 0.12-0.15 |
| （、） | 2-3 | 1-2 | 0.10-0.15 |
| （） | 4-6 | 2-4 | 0.06-0.08 |

### 

- `flood-color="#000000"` → `#0F172A`
- `<feComponentTransfer>` + `<feFuncA slope=...>` → `<feFlood flood-color flood-opacity>` 
- `flood-opacity > 0.20` → ， 0.15-0.20

> ** sub-element， `<filter>` 。** `<filter>` PPT Master 、/（ [`shared-standards.md`](../../references/shared-standards.md) §1 filter、§6 filter shadow drop-shadow ）， [`svg_to_pptx/drawingml_styles.py`](../../scripts/svg_to_pptx/drawingml_styles.py) `feGaussianBlur` + `feOffset` + `feFlood` + `feComposite` + `feMerge`（ `feDropShadow` ） DrawingML `<a:outerShdw>`。
>
> `feComponentTransfer/feFuncA(slope)` ：**、**。 `feFuncA slope` alpha， `'000000'`——SVG （ SourceAlpha ）， PPTX `#000000`， `feFlood flood-color="#0F172A"` 。
>
> ：** filter ， primitive ""；"" primitive 。**

### （shared-standards SS6）

> **，。** ""。 "" 。

****：/、 CTA、（tooltip、callout）

****：/、、/、、/、（）

****： 2-3 。 4 ，。

****： `feOffset` `dx`/`dy` （ `dx=0, dy=`，）。

****：

| | | dy | stdDeviation | flood-opacity |
|------|------|----|--------------|---------------|
| （） | 、、、 | — | — | — |
| | /、 callout | 2-4 | 4-8 | 0.06-0.10 |
| | CTA、/、 | 6-10 | 10-16 | 0.12-0.20 |

****： + + + = 。""，。

---

## 4. 

### 4.1 （/）

```xml
<linearGradient id="barGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
 <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
 <stop offset="100%" style="stop-color:#2563EB;stop-opacity:1" />
</linearGradient>
```

- ：（ ）
- ID ：`barGrad1`、`leftGrad`、`actualBarBlue`

### 4.2 （）

```xml
<radialGradient id="bubbleGrad1" cx="30%" cy="30%">
 <stop offset="0%" style="stop-color:#60A5FA;stop-opacity:0.9" />
 <stop offset="100%" style="stop-color:#2563EB;stop-opacity:0.7" />
</radialGradient>
```

- (`cx="30%" cy="30%"`)
- opacity 0.7，

---

## 5. 

### 5.1 （shared-standards SS4 Grouping）

 `<g id="...">` ， PPT /：

```xml
<g id="chartArea"> <!-- -->
 <g id="bar-1">...</g> <!-- -->
 <g id="bar-2">...</g>
</g>
<g id="legend"> <!-- -->
 <g id="legend-high">...</g>
</g>
<g id="detailList"> <!-- -->
 <g id="list-items">
 <g id="item-1">...</g>
 </g>
</g>
```

****（ shared-standards）：

| | |
|---------|---------|
| / | rect + （）+ + + |
| | + + + |
| | / + + + |
| - | + |
| | + + |
| | （、、） |

****： `id`（ `card-1`、`step-discover`、`header`、`footer`）。

> `<g opacity="...">` （ SS2）。 `<g>` 。

### 5.2 viewBox

 `0 0 1280 720`（PPT 16:9），。

### 5.3 

：
```xml
<rect width="1280" height="720" fill="#FFFFFF"/>
```

### 5.4 

，：
```xml
<text x="60" y="695" font-family="..." font-size="14" fill="#94A3B8">
 <tspan>: XXX</tspan>
</text>
```

---

## 6. SVG （shared-standards SS1-2）

### 6.1 

| | |
|---------|---------| 
| HTML （`&nbsp;` `&mdash;` `&copy;` `&ndash;` `&reg;` `&hellip;` `&bull;` …） | Unicode （`—` `–` `©` `®` `→` NBSP …） |
| / `& < > " '` | XML `&amp;` `&lt;` `&gt;` `&quot;` `&apos;` |
| `<style>` / `class` | （`id` `<defs>` ） |
| `<foreignObject>` | `<text>` + `<tspan>` |
| `mask` | / gradient overlay |
| `<symbol>` + `<use>` | |
| `textPath` | `<text>` |
| `@font-face` | |
| `<animate*>` / `<set>` | （PPT ） |
| `<script>` / event | |
| `<iframe>` | |

### 6.2 PPT 

| | |
|---------|----------|
| `fill="rgba(255,255,255,0.1)"` | `fill="#FFFFFF" fill-opacity="0.1"` |
| `<g opacity="0.2">...</g>` | `fill-opacity` / `stroke-opacity` |
| `<image opacity="0.3"/>` | image `<rect fill="" opacity="0.7"/>` |

### 6.3 

| | | |
|------|------|----------|
| `marker-start` / `marker-end` | `<marker>` `<defs>` ，`orient="auto"`，// | DrawingML `<a:headEnd>` / `<a:tailEnd>` |
| `clipPath` on `<image>` | `<clipPath>` `<defs>` ，，** image** | DrawingML `<a:prstGeom>` / `<a:custGeom>` |
| `stroke-dasharray` | `4,4` / `2,2` / `8,4` / `8,4,2,4` | PPTX `<a:prstDash>` |
| `text-decoration` | `underline` / `line-through` | PPTX |
| `transform="rotate(...)"` | | PPTX `<a:xfrm rot="...">` |

> [`shared-standards.md`](../../references/shared-standards.md) SS1.1（marker ） SS1.2（clipPath ）。

### 6.4 

| SVG | PPTX | |
|--------|-----------|---------|
| `4,4` | Dash | 、 |
| `2,2` | Dot (sysDot) | 、 |
| `8,4` | Long dash | 、 |
| `8,4,2,4` | Long dash-dot | 、 |

---

## 7. 

，：

| (Material/Flat) | → | (Tailwind) | |
|----------------------|---|-----------------|------|
| `#2C3E50` | → | `#0F172A` | |
| `#7F8C8D` | → | `#64748B` | |
| `#5D6D7E` | → | `#475569` | |
| `#95A5A6` | → | `#94A3B8` | |
| `#BDC3C7` | → | `#CBD5E1` | |
| `#2196F3` / `#1976D2` | → | `#3B82F6` / `#2563EB` | |
| `#4CAF50` / `#388E3C` | → | `#10B981` / `#059669` | |
| `#FF9800` / `#F57C00` | → | `#F59E0B` / `#D97706` | |
| `#E91E63` | → | `#F43F5E` | |
| `#000000` (shadow) | → | `#0F172A` | |

---

## 8. (Placeholder Content Strategy)

 SVG AI “”， **、**，。，“”：

### 8.0 (English-Only Rule)
****：（、、、、、）****。
- ****： LLM ，。

### 8.1 
- **/**：（、 `tspan`）。 AI ，。
- ****：（ `$1,234.5M`、`98.5%`） `10`，。

### 8.2 
- 、，（）。
- ****： `Category A`、`Q1 Revenue`、`Strategic Objective`、`Phase 01`。
- ****：（“2023”）。

### 8.3 
- （，），。

---

## 9. charts_index.json

 SVG ，**** [`charts_index.json`](./charts_index.json) ， Strategist 。

### 9.1 

```json
"<key>": {
 "summary": "Pick for < + >. Skip if < → >."
}
```

- **`key`** = SVG `.svg`，（ `bullet_chart`）
- **`summary`** ****，。 `meta.summaryGrammar`：， `Skip if ... (use <other_key>)` 
- **`meta.total`** +1

> **** `label` / `categories` / `quickLookup` / `keywords` —— 。Strategist summary ，。****：summary ， source /（""、""、""），Strategist 。， summary Pick 。

### 9.2 

❌ ""：`"summary": "Bidirectional comparison chart for two datasets"`
✅ ""：`"summary": "Pick for two mirrored datasets sharing a common axis (age pyramid, A/B). Skip for >2 sides (use grouped_bar_chart)."`

❌ summary （>400 ）—— ， 150-300 。

> **Why not stricter**：/（ `quadrant_text_bullets` SWOT + Ansoff，`top_down_tree` org + OKR），summary （"principles, key takeaways, action items" ） Strategist ""， 100-180 -。

---

## 10. 

，：

### 
-  `xmllint --noout` 
-  viewBox `0 0 1280 720`
-  `<rect width="1280" height="720" fill="#FFFFFF"/>`

### 
-  （`grep` ，）
-  `flood-color` `#0F172A`，opacity 0.20
-  `#94A3B8`

### 
-  `font-size < 12` 
-  `<text>` `<tspan>`
-  `<tspan>`，**** `<text>`
-  `<tspan>` `x` / `y` / `dy`
-  34px、 18px、 14px

### 
-  `<g id="...">`
-  `<style>`、`class`、`<foreignObject>`、`mask`、`rgba`
-  `<g>` `opacity` 
-  Unicode（`—` `©` `→` NBSP ）， HTML （`&nbsp;` `&mdash;` `&copy;` ）； `& < >` `&amp; &lt; &gt;`

### 
-  `feFlood` （ `feComponentTransfer`）
-  `dx`/`dy` 
-  3 

### （）
-  `charts_index.json` `charts.<key>` `summary` 
-  `summary` （`Pick for ... Skip if ... (use <other>)`），
-  `summary` 150-300 （>400 ）；/， 350 
-  `meta.total` +1

### （calculator-supported ）
-  （bar / horizontal_bar / grouped_bar / stacked_bar / line / area / stacked_area / scatter / waterfall / pareto / butterfly） `<!-- chart-plot-area: x_min,y_min,x_max,y_max -->` 
-  Pie / donut / radar `<!-- chart-plot-area: <type> | center: cx,cy | radius: r -->` 
-  `<g id="chartArea">` 、、
-  SVG 

### 
```bash
# 
f="your_chart.svg"
xmllint --noout "skills/ppt-master/templates/charts/$f" && echo "XML OK" || echo "XML FAIL"
echo "Old colors:" && grep -c '#2C3E50\|#7F8C8D\|#95A5A6\|#5D6D7E\|#000000' "skills/ppt-master/templates/charts/$f"
echo "Small fonts:" && grep -c 'font-size="[0-9]"' "skills/ppt-master/templates/charts/$f"
```

---

## 11. (Card Container Patterns)

 PPT Master （KPI 、、）。、 PPTX ""，，。

### 11.1 (Half-Rounded Section Tab)

****：""，（S/W/O/T、Political/Economic、/）。，。

****—— tab ""：

| | | | |
|------|------|---------|---------|
| ****  | ， | "" | 、quadrant 、 |
| ****  | ， | /"" | 、、 |

> ：****， path 。" + /" hack（ PPTX ，）。

**：（）**

```xml
<!-- ： W、 H、 R， (x, y) -->
<path d="M {x+R} {y} h {W-2R} a {R} {R} 0 0 1 {R} {R} v {H-R} h -{W} v -{H-R} a {R} {R} 0 0 1 {R} -{R} Z"
 fill="#2563EB"/>

<!-- ：240×50, r=25, (245, 140) -->
<path d="M 245 140 h 190 a 25 25 0 0 1 25 25 v 25 h -240 v -25 a 25 25 0 0 1 25 -25 Z" fill="#2563EB"/>
```

**：（）**

```xml
<!-- ： W、 H、 R， (x, y) -->
<path d="M {x} {y} h {W} v {H-R} a {R} {R} 0 0 1 -{R} {R} h -{W-2R} a {R} {R} 0 0 1 -{R} -{R} Z"
 fill="#2563EB"/>

<!-- ：240×50, r=25, (245, 140) -->
<path d="M 245 140 h 240 v 25 a 25 25 0 0 1 -25 25 h -190 a 25 25 0 0 1 -25 -25 Z" fill="#2563EB"/>
```

****（PEST/SWOT/comparison_columns ）：

```xml
<!-- ❌ ： + -->
<rect width="260" height="120" rx="12" fill="#EFF6FF"/>
<rect y="100" width="260" height="20" fill="#EFF6FF"/>
```

 SVG→PPTX 、，PPT 、""。

### 11.2 (Nested Card Border)

****：""， stroke。stroke PPTX ，。

****： rect + rect， 8–20px ""。

```xml
<!-- "" -->
<rect x="60" y="140" width="560" height="255" rx="20" fill="#F1F5F9"/>
<!-- （ 20px，） -->
<rect x="80" y="210" width="520" height="165" rx="12" fill="#FFFFFF"/>
```

****：
- §11.1 ，""
- **** ： OR stroke OR ，（ §3 ）

### 11.3 (Card Grid as Page Skeleton)

****： 4 （pillar / aspect / quadrant）， 2×2 。

****（1280×720 ）：

| | × | | (x, y) |
|------|-------------|------|-------------|
| 2×2 | 560 × 255 | 40 | (60, 140) (660, 140) (60, 420) (660, 420) |
| 2×3  | 370 × 260 | 25 | (50, 130) 290 |
| 1×3  | 400 × 540 | 30 | (60, 130) 430 |
| 1×4  | 280 × 250 | 20 | (60, 150) 300 |

****："4 " → 2×2；"3 " → 1×3；"6 " → 2×3；"4 " → 1×4。`page_rhythm` `breathing` **** （ executor-base.md §2.1）。

### 11.5 (Diagonal Dashed Connector)

****："/"——、、、。/""，""，。

****： `<line>` + `stroke-dasharray="6 5"` + `marker-end`。 marker（， Slate 600 `#475569` "、"）。

```xml
<defs>
 <marker id="migrationArrow" markerWidth="12" markerHeight="12"
 refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
 <path d="M 0,0 L 10,6 L 0,12 Z" fill="#475569"/>
 </marker>
</defs>

<!-- Q4  Q2  -->
<line x1="850" y1="605" x2="385" y2="200"
 stroke="#475569" stroke-width="2"
 stroke-dasharray="6 5" stroke-linecap="round"
 marker-end="url(#migrationArrow)"/>

<!-- ：， -->
<rect x="525" y="385" width="190" height="28" rx="14"
 fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1"/>
<text x="620" y="403" text-anchor="middle" font-size="12"
 font-weight="700" fill="#475569" letter-spacing="1">PRIORITY MIGRATION</text>
```

> ****：（），""。/（ `process_flow`）。

### 11.6 (Ground Anchor Ellipse) — filter 

****："/icon///"""，** `<filter>` **。

****：
1. PPTX /，， `<a:outerShdw>`（）
2. §3 「」—— 2-3 ，""
3. filter ** PPT **（、、）

****：********（`ry << rx`），， Slate 900：

```xml
<!-- /，cy 10-15px -->
<ellipse cx="80" cy="172" rx="70" ry="5" fill="#0F172A" opacity="0.10"/>
<!-- （，） -->
<circle cx="80" cy="80" r="80" fill="#E2E8F0"/>
```

****：

| | rx | ry | opacity |
|-------------|---------|---------|---------|
| 30-50 px | r × 0.85 | 3-4 | 0.10-0.15 |
| 50-100 px | r × 0.85 | 5-6 | 0.10-0.12 |
| 100+ px | r × 0.85 | 7-9 | 0.08-0.10 |

： `#0F172A`（），（ `#1E3A8A`）""。

****：（`ry/rx > 0.25` ）。`<filter>` ——。

### 11.7 (Bidirectional Interaction Arrows)

****："/"、"/"、"/"、"/"。。

****： `<line>` + `marker-end`，，****：

```xml
<defs>
 <marker id="reqArrow" markerWidth="10" markerHeight="10" refX="9" refY="5"
 orient="auto" markerUnits="strokeWidth">
 <path d="M0,0 L10,5 L0,10 Z" fill="#3B82F6"/>
 </marker>
 <marker id="respArrow" markerWidth="10" markerHeight="10" refX="9" refY="5"
 orient="auto" markerUnits="strokeWidth">
 <path d="M0,0 L10,5 L0,10 Z" fill="#10B981"/>
 </marker>
</defs>

<!-- ：， -->
<line x1="380" y1="250" x2="926" y2="250" stroke="#3B82F6" stroke-width="2.5"
 marker-end="url(#reqArrow)"/>
<rect x="500" y="216" width="280" height="26" rx="11" fill="#FFFFFF"
 stroke="#3B82F6" stroke-width="1"/>
<text x="640" y="234" text-anchor="middle" font-size="14" font-weight="700"
 fill="#3B82F6">① Login Request · POST /auth/login</text>

<!-- ：， -->
<line x1="926" y1="290" x2="384" y2="290" stroke="#10B981" stroke-width="2.5"
 marker-end="url(#reqArrow)"/>
<!-- ...... -->
```

****：（initiator） `#3B82F6`、（responder） `#10B981`。（ A↔B ）， Slate 600 `#475569` 。

****：""——****；。

### 11.8 

| | |
|------|---------|
| §11.1 （） | `quadrant_text_bullets.svg`, `labeled_card.svg`, `vertical_pillars.svg`, `comparison_columns.svg` |
| §11.2 | `labeled_card.svg` |
| §11.3 2×2 | `kpi_cards.svg`, `quadrant_text_bullets.svg`, `labeled_card.svg` |
| §11.3 2×3 | `icon_grid.svg` |
| §11.3 1×3/1×4 | `comparison_columns.svg`, `vertical_pillars.svg` |
| §11.5 | `matrix_2x2.svg` |
| §11.6 | `team_roster.svg` |
| §11.7 | `client_server_flow.svg` |

