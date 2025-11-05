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
    json_data = json.dumps({"generated_at": meta.get("generated_at", ""), "phases": phases}, ensure_ascii=False)

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
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
      margin-bottom: 0.35rem;
    }}
    .phase-title {{
      font-size: 1rem;
      font-weight: 600;
    }}
    .phase-label {{
      font-size: 0.8rem;
      text-transform: none;
      letter-spacing: 0.02em;
      color: #9ca3af;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
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
      max-height: 460px;
      overflow-y: auto;
      padding-right: 0.25rem;
    }}
    .tag-card {{
      border-radius: 0.65rem;
      border: 1px solid #111827;
      padding: 0.4rem 0.55rem;
      background-color: #020617;
      transition: border-color 0.15s ease, background-color 0.15s ease,
                  transform 0.1s ease;
      cursor: default;
    }}
    .tag-card:hover {{
      border-color: #38bdf8;
      background-color: #020617;
      transform: translateY(-1px);
    }}
    .tag-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.1rem;
    }}
    .tag-name {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.85rem;
      color: #e5e7eb;
    }}
    .tag-count {{
      font-size: 0.75rem;
      color: #9ca3af;
    }}
    .tag-description {{
      font-size: 0.8rem;
      color: #d1d5db;
    }}
    .tag-pulses {{
      font-size: 0.72rem;
      color: #6b7280;
      margin-top: 0.15rem;
    }}
    .no-results {{
      font-size: 0.85rem;
      color: #6b7280;
      margin-top: 1.5rem;
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Φ-Mesh Tag Taxonomy</h1>
    <div class="subtitle">Tags grouped by RGPx phase: Δ (emergence), GC (resonance), CF (integration / closure).</div>

    <div class="controls">
      <label>Phase:
        <select id="phaseFilter">
          <option value="all">All phases</option>
          <option value="delta">Δ — Emergence (Cycle 1)</option>
          <option value="gc">GC — Resonance (Cycle 2)</option>
          <option value="cf">CF — Integration / Closure (Cycle 3)</option>
          <option value="unknown">Unclassified (Open)</option>
        </select>
      </label>
      <label>Search tag:
        <input type="text" id="searchBox" placeholder="Type to filter by tag name…" />
      </label>
    </div>

    <div id="phaseGrid" class="phase-grid"></div>
    <div id="noResults" class="no-results" style="display:none;">No tags match the current filter.</div>
  </div>

  <script id="taxonomy-data" type="application/json">{json_data}</script>
  <script>
    (function() {{
      const raw = document.getElementById("taxonomy-data").textContent;
      const payload = JSON.parse(raw);
      const phases = payload.phases || {{}};

      const phaseMeta = {{
        delta: {{ title: "Δ — Emergence", label: "difference, initiation, tension" }},
        gc: {{ title: "GC — Resonance", label: "alignment, rhythm, propagation" }},
        cf: {{ title: "CF — Integration / Closure", label: "stability, context, attractors" }},
        unknown: {{ title: "Unclassified", label: "yet to be determined" }}
      }};

      const phaseOrder = ["delta", "gc", "cf", "unknown"];
      const phaseGrid = document.getElementById("phaseGrid");
      const phaseFilter = document.getElementById("phaseFilter");
      const searchBox = document.getElementById("searchBox");
      const noResults = document.getElementById("noResults");

      function render() {{
        const phaseValue = phaseFilter.value;
        const searchValue = searchBox.value.trim().toLowerCase();
        phaseGrid.innerHTML = "";
        let anyVisible = false;

        phaseOrder.forEach(phaseKey => {{
          const items = phases[phaseKey] || [];
          if (!items.length) return;
          if (phaseValue !== "all" && phaseValue !== phaseKey) return;

          const filtered = items.filter(item => !searchValue || (item.tag || "").toLowerCase().includes(searchValue));
          if (!filtered.length) return;

          anyVisible = true;
          const phaseCol = document.createElement("div");
          phaseCol.className = "phase-column";
          const header = document.createElement("div");
          header.className = "phase-header";
          const title = document.createElement("div");
          title.className = "phase-title";
          title.textContent = phaseMeta[phaseKey].title;
          const label = document.createElement("div");
          label.className = "phase-label";
          label.textContent = phaseMeta[phaseKey].label;
          header.appendChild(title);
          header.appendChild(label);
          const list = document.createElement("div");
          list.className = "tag-list";

          filtered.forEach(item => {{
            const card = document.createElement("div");
            card.className = "tag-card";
            const tagHeader = document.createElement("div");
            tagHeader.className = "tag-header";
            const tagName = document.createElement("div");
            tagName.className = "tag-name";
            tagName.textContent = item.tag;
            const tagCount = document.createElement("div");
            tagCount.className = "tag-count";
            tagCount.textContent = "pulses: " + (item.count || 0);
            tagHeader.appendChild(tagName);
            tagHeader.appendChild(tagCount);
            const tagDesc = document.createElement("div");
            tagDesc.className = "tag-description";
            tagDesc.textContent = (item.description || "").trim() || "No description.";
            card.appendChild(tagHeader);
            card.appendChild(tagDesc);
            list.appendChild(card);
          }});
          phaseCol.appendChild(header);
          phaseCol.appendChild(list);
          phaseGrid.appendChild(phaseCol);
        }});
        noResults.style.display = anyVisible ? "none" : "block";
      }}

      searchBox.addEventListener("input", () => {{
        render();
        if (!searchBox.value.trim()) document.getElementById("phaseGrid").scrollIntoView({{ behavior: "smooth" }});
      }});
      phaseFilter.addEventListener("change", render);
      render();
    }})();
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ Written taxonomy HTML: {OUT_HTML}")


if __name__ == "__main__":
    build_html()
