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

    # Compact JSON payload for the front-end
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
      margin-bottom: 1rem;
    }}

    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1.25rem;
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

    .detail-panel {{
      margin: 0.75rem 0 1.75rem 0;
      padding: 0.9rem 1.1rem;
      border-radius: 0.9rem;
      background: rgba(10, 15, 35, 0.94);
      border: 1px solid rgba(120, 160, 255, 0.35);
    }}

    .detail-title {{
      font-weight: 600;
      font-size: 0.95rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 0.45rem;
      color: #a9c4ff;
    }}

    .detail-body {{
      font-size: 0.95rem;
      color: #e5e7f1;
      line-height: 1.5;
      white-space: pre-line;
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
      flex-direction: column;
      align-items: flex-start;
      gap: 0.1rem;
      margin-bottom: 0.35rem;
    }}

    .phase-title {{
      font-size: 0.95rem;
      font-weight: 600;
    }}

    .phase-cycle {{
      font-size: 0.8rem;
      color: #9ca3af;
    }}

    .phase-label {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #6b7280;
    }}

    .phase-description {{
      font-size: 0.8rem;
      color: #9ca3af;
      margin-bottom: 0.5rem;
    }}

    .tag-list {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      /* whole page scrolls; no inner scrollbars */
    }}

    .tag-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 0.4rem 0.7rem;
      border-radius: 999px;
      border: 1px solid rgba(17, 24, 39, 0.9);
      background-color: #020617;
      cursor: pointer;
      font-size: 0.9rem;
      color: #e5e7eb;
      gap: 0.5rem;
      transition: border-color 0.12s ease-out, background-color 0.12s ease-out, transform 0.06s;
    }}

    .tag-pill:hover {{
      border-color: #38bdf8;
      background-color: #02071f;
      transform: translateY(-1px);
    }}

    .tag-name {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.85rem;
      color: #e5e7eb;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .tag-count {{
      font-size: 0.75rem;
      color: #9ca3af;
      white-space: nowrap;
    }}

    .no-results {{
      font-size: 0.85rem;
      color: #6b7280;
      margin-top: 1.5rem;
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

    <div class="detail-panel" id="tagDetail">
      <div class="detail-title">Tag details</div>
      <div class="detail-body">
Click a tag to see its description here.
      </div>
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
          label: "Difference, initiation, tension"
        }},
        gc: {{
          title: "GC — Resonance",
          cycle: "Cycle 2",
          label: "Alignment, rhythm, propagation"
        }},
        cf: {{
          title: "CF — Integration / Closure",
          cycle: "Cycle 3",
          label: "Stability, context, attractors"
        }},
        unknown: {{
          title: "Unclassified",
          cycle: "Open",
          label: "Yet to be determined"
        }}
      }};

      const phaseOrder = ["delta", "gc", "cf", "unknown"];

      const phaseGrid = document.getElementById("phaseGrid");
      const phaseFilter = document.getElementById("phaseFilter");
      const searchBox = document.getElementById("searchBox");
      const noResults = document.getElementById("noResults");

      const detailPanel = document.getElementById("tagDetail");
      const detailTitle = detailPanel.querySelector(".detail-title");
      const detailBody = detailPanel.querySelector(".detail-body");

      function render() {{
        const phaseValue = phaseFilter.value;
        const searchValue = searchBox.value.trim().toLowerCase();

        phaseGrid.innerHTML = "";
        let anyVisible = false;

        phaseOrder.forEach(phaseKey => {{
          const items = phases[phaseKey] || [];
          if (!items.length) return;

          // If a specific phase is selected, skip others
          if (phaseValue !== "all" && phaseValue !== phaseKey) return;

          // Filter items by search
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

          const meta = phaseMeta[phaseKey] || {{}};

          const title = document.createElement("div");
          title.className = "phase-title";
          title.textContent = meta.title || phaseKey;

          const cycle = document.createElement("div");
          cycle.className = "phase-cycle";
          cycle.textContent = meta.cycle || "";

          const label = document.createElement("div");
          label.className = "phase-label";
          label.textContent = meta.label || "";

          header.appendChild(title);
          if (cycle.textContent) header.appendChild(cycle);
          if (label.textContent) header.appendChild(label);

          const desc = document.createElement("div");
          desc.className = "phase-description";
          desc.textContent = "";

          const list = document.createElement("div");
          list.className = "tag-list";

          filtered.forEach(item => {{
            const pill = document.createElement("button");
            pill.type = "button";
            pill.className = "tag-pill";
            pill.dataset.tag = item.tag;
            pill.dataset.phase = phaseKey;

            const description = (item.description || "").trim() || "No description available.";
            const pulses = item.pulses || [];

            pill.dataset.description = description;
            pill.dataset.pulses = pulses.join(", ");
            pill.title = description;

            const tagName = document.createElement("span");
            tagName.className = "tag-name";
            tagName.textContent = item.tag;

            const tagCount = document.createElement("span");
            tagCount.className = "tag-count";
            tagCount.textContent = "pulses: " + (item.count || 0);

            pill.appendChild(tagName);
            pill.appendChild(tagCount);

            list.appendChild(pill);
          }});

          phaseCol.appendChild(header);
          phaseCol.appendChild(desc);
          phaseCol.appendChild(list);
          phaseGrid.appendChild(phaseCol);
        }});

        noResults.style.display = anyVisible ? "none" : "block";
      }}

      phaseFilter.addEventListener("change", render);
      searchBox.addEventListener("input", render);

      phaseGrid.addEventListener("click", (event) => {{
        const pill = event.target.closest(".tag-pill");
        if (!pill) return;

        const tagName = pill.dataset.tag || "(unknown tag)";
        const desc = pill.dataset.description || "No description available.";
        const pulses = (pill.dataset.pulses || "").trim();

        detailTitle.textContent = tagName;

        let text = desc;
        if (pulses) {{
          text += "\\n\\nExample pulses: " + pulses;
        }}

        detailBody.textContent = text;
      });

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
