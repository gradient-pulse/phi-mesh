from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
META_DIR = ROOT / "meta"
DOCS_DIR = ROOT / "docs"

TAXONOMY_YAML = META_DIR / "tag_taxonomy.yml"
OUT_HTML = DOCS_DIR / "tag_taxonomy.html"


def load_yaml(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_html():
    data = load_yaml(TAXONOMY_YAML)
    meta = data.get("meta", {})
    phases = data.get("phases", {})

    # Defensive sort per phase (builder already did this, but keep it stable)
    for key, items in list(phases.items()):
        phases[key] = sorted(items, key=lambda x: x.get("tag", ""))

    front_payload = {
        "generated_at": meta.get("generated_at", ""),
        "phases": phases,
    }

    json_data = json.dumps(front_payload, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Φ-Mesh Tag Taxonomy</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      color: #f5f5f5;
      background-color: #020617;
    }}

    body {{
      margin: 0;
      padding: 0;
      background: radial-gradient(circle at top, #0f172a 0, #020617 55%);
      color: #e5e7eb;
    }}

    .page {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 1.5rem 1.25rem 3rem;
    }}

    h1 {{
      font-size: 1.9rem;
      margin-bottom: 0.25rem;
    }}

    .subtitle {{
      font-size: 0.95rem;
      color: #9ca3af;
      margin-bottom: 1.5rem;
    }}

    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
      align-items: center;
    }}

    .controls label {{
      font-size: 0.85rem;
      color: #9ca3af;
    }}

    .controls input[type="text"],
    .controls select {{
      background-color: #020617;
      border: 1px solid #1f2933;
      border-radius: 9999px;
      padding: 0.45rem 0.85rem;
      color: #e5e7eb;
      font-size: 0.9rem;
      outline: none;
    }}

    .controls input[type="text"]:focus,
    .controls select:focus {{
      border-color: #38bdf8;
    }}

    .phase-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1rem;
    }}

    .phase-column {{
      border-radius: 0.75rem;
      border: 1px solid #111827;
      padding: 0.85rem;
      background: linear-gradient(to bottom, #020617, #020617f2);
    }}

    .phase-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.6rem;
    }}

    .phase-title {{
      font-size: 0.95rem;
      font-weight: 600;
    }}

    .phase-subtitles {{
      text-align: right;
      font-size: 0.78rem;
      line-height: 1.25;
    }}

    .phase-cycle {{
      color: #9ca3af;
    }}

    .phase-label {{
      color: #9ca3af;
      white-space: nowrap;
    }}

    .tag-list {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}

    .tag-card {{
      border-radius: 9999px;
      border: 1px solid #111827;
      padding: 0.3rem 0.65rem;
      background-color: #020617;
      transition: border-color 0.15s ease, background-color 0.15s ease,
                  transform 0.1s ease;
      cursor: default;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .tag-card:hover {{
      border-color: #38bdf8;
      background-color: #020617;
      transform: translateY(-1px);
    }}

    .tag-name {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.85rem;
      color: #e5e7eb;
    }}

    .tag-count {{
      font-size: 0.75rem;
      color: #9ca3af;
      margin-left: 0.75rem;
      white-space: nowrap;
    }}

    .no-results {{
      font-size: 0.85rem;
      color: #6b7280;
      margin-top: 1.5rem;
    }}

    /* Custom tooltip layer */

    .tooltip-layer {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 40;
      display: none;
    }}

    .tooltip-card {{
      position: absolute;
      max-width: 360px;
      padding: 0.6rem 0.75rem;
      border-radius: 0.6rem;
      background: #020617;
      border: 1px solid #38bdf8;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
      font-size: 0.82rem;
      color: #e5e7eb;
      line-height: 1.4;
      white-space: normal;
    }}

    @media (max-width: 640px) {{
      .phase-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Φ-Mesh Tag Taxonomy</h1>
    <div class="subtitle">
      Tags grouped by RGPx phase: Δ (emergence), GC (resonance), CF (integration / closure).
    </div>

    <div class="controls">
      <label>
        Phase:
        <select id="phaseFilter">
          <option value="all">All phases</option>
          <option value="delta">Δ — Emergence</option>
          <option value="gc">GC — Resonance</option>
          <option value="cf">CF — Integration / Closure</option>
          <option value="unknown">Unclassified</option>
        </select>
      </label>
      <label>
        Search tag:
        <input type="text" id="searchBox" placeholder="Type to filter by tag name…" />
      </label>
    </div>

    <div id="phaseGrid" class="phase-grid"></div>

    <div id="noResults" class="no-results" style="display:none;">
      No tags match the current filter.
    </div>
  </div>

  <script id="taxonomy-data" type="application/json">
{json_data}
  </script>

  <script>
    (function() {{
      const raw = document.getElementById("taxonomy-data").textContent;
      const payload = JSON.parse(raw);
      const phases = payload.phases || {{}};

      const phaseMeta = {{
        delta: {{
          title: "Δ — Emergence",
          cycle: "Cycle 1",
          label: "difference, initiation, tension"
        }},
        gc: {{
          title: "GC — Resonance",
          cycle: "Cycle 2",
          label: "alignment, rhythm, propagation"
        }},
        cf: {{
          title: "CF — Integration / Closure",
          cycle: "Cycle 3",
          label: "stability, context, attractors"
        }},
        unknown: {{
          title: "Unclassified",
          cycle: "Open",
          label: "yet to be determined"
        }}
      }};

      const phaseOrder = ["delta", "gc", "cf", "unknown"];

      const phaseGrid = document.getElementById("phaseGrid");
      const phaseFilter = document.getElementById("phaseFilter");
      const searchBox = document.getElementById("searchBox");
      const noResults = document.getElementById("noResults");

      // --- custom tooltip setup ---

      const tooltipLayer = document.createElement("div");
      tooltipLayer.className = "tooltip-layer";
      const tooltipCard = document.createElement("div");
      tooltipCard.className = "tooltip-card";
      tooltipLayer.appendChild(tooltipCard);
      document.body.appendChild(tooltipLayer);

      function showTooltip(text, x, y) {{
        if (!text) return;
        tooltipCard.textContent = text;
        const offsetX = 14;
        const offsetY = 14;
        let left = x + offsetX;
        let top = y + offsetY;

        const rect = tooltipCard.getBoundingClientRect();
        const vw = window.innerWidth;
        const vh = window.innerHeight;

        if (left + rect.width + 16 > vw) {{
          left = vw - rect.width - 16;
        }}
        if (top + rect.height + 16 > vh) {{
          top = vh - rect.height - 16;
        }}

        tooltipCard.style.left = left + "px";
        tooltipCard.style.top = top + "px";

        tooltipLayer.style.display = "block";
      }}

      function moveTooltip(x, y) {{
        if (tooltipLayer.style.display !== "block") return;
        showTooltip(tooltipCard.textContent, x, y);
      }}

      function hideTooltip() {{
        tooltipLayer.style.display = "none";
      }}

      // --- render function ---

      function render() {{
        const phaseValue = phaseFilter.value;
        const searchValue = searchBox.value.trim().toLowerCase();

        phaseGrid.innerHTML = "";
        let anyVisible = false;

        phaseOrder.forEach(phaseKey => {{
          const items = phases[phaseKey] || [];
          if (!items.length) return;

          if (phaseValue !== "all" && phaseValue !== phaseKey) return;

          const filtered = items.filter(item => {{
            if (!searchValue) return true;
            const tag = (item.tag || "").toLowerCase();
            return tag.includes(searchValue);
          }});

          if (!filtered.length) return;

          anyVisible = true;

          const phaseCol = document.createElement("div");
          phaseCol.className = "phase-column";
          phaseCol.dataset.phase = phaseKey;

          const header = document.createElement("div");
          header.className = "phase-header";

          const title = document.createElement("div");
          title.className = "phase-title";
          title.textContent = (phaseMeta[phaseKey] && phaseMeta[phaseKey].title) || phaseKey;

          const subtitles = document.createElement("div");
          subtitles.className = "phase-subtitles";

          const cycle = document.createElement("div");
          cycle.className = "phase-cycle";
          cycle.textContent = (phaseMeta[phaseKey] && phaseMeta[phaseKey].cycle) || "";

          const label = document.createElement("div");
          label.className = "phase-label";
          label.textContent = (phaseMeta[phaseKey] && phaseMeta[phaseKey].label) || "";

          subtitles.appendChild(cycle);
          subtitles.appendChild(label);

          header.appendChild(title);
          header.appendChild(subtitles);

          const list = document.createElement("div");
          list.className = "tag-list";

          filtered.forEach(item => {{
            const card = document.createElement("div");
            card.className = "tag-card";
            card.dataset.tag = item.tag;
            card.dataset.phase = phaseKey;

            const descText = (item.description || "").trim() || "No description available.";

            const tagName = document.createElement("div");
            tagName.className = "tag-name";
            tagName.textContent = item.tag;

            const tagCount = document.createElement("div");
            tagCount.className = "tag-count";
            tagCount.textContent = "pulses: " + (item.count || 0);

            card.appendChild(tagName);
            card.appendChild(tagCount);

            // Instant, styled tooltip
            card.addEventListener("mouseenter", (ev) => {{
              showTooltip(descText, ev.clientX, ev.clientY);
            }});
            card.addEventListener("mousemove", (ev) => {{
              moveTooltip(ev.clientX, ev.clientY);
            }});
            card.addEventListener("mouseleave", hideTooltip);

            list.appendChild(card);
          }});

          phaseCol.appendChild(header);
          phaseCol.appendChild(list);
          phaseGrid.appendChild(phaseCol);
        }});

        noResults.style.display = anyVisible ? "none" : "block";
      }}

      phaseFilter.addEventListener("change", render);
      searchBox.addEventListener("input", render);

      render();
    }})();
  </script>
</body>
</html>
"""

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Written: {OUT_HTML}")


if __name__ == "__main__":
    build_html()
