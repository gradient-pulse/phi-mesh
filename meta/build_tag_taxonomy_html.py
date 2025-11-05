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
    meta = data.get("meta", {}) or {}
    phases_raw = data.get("phases", {}) or {}

    # Normalize phases so every entry is a dict with tag/description/count/pulses
    phases: dict[str, list[dict]] = {}
    for key, items in phases_raw.items():
        norm_items = []
        for x in items or []:
            if isinstance(x, dict):
                # Ensure required keys exist
                norm_items.append(
                    {
                        "tag": x.get("tag", ""),
                        "description": x.get("description", "") or "",
                        "count": int(x.get("count", 0) or 0),
                        "pulses": x.get("pulses", []) or [],
                    }
                )
            else:
                # Bare string → minimal record
                norm_items.append(
                    {
                        "tag": str(x),
                        "description": "",
                        "count": 0,
                        "pulses": [],
                    }
                )
        # Sort by tag name
        phases[key] = sorted(norm_items, key=lambda rec: rec.get("tag", ""))

    # Compact payload for the front-end
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
      margin-bottom: 0.35rem;
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

    .selection-panel {{
      border-radius: 0.85rem;
      border: 1px solid #111827;
      background: radial-gradient(circle at top left, #020617 0, #020617 55%);
      padding: 0.85rem 1rem;
      margin-bottom: 1.25rem;
    }}

    .selection-title {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #6b7280;
      margin-bottom: 0.25rem;
    }}

    .selection-tag {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.95rem;
      margin-bottom: 0.25rem;
      color: #e5e7eb;
    }}

    .selection-meta {{
      font-size: 0.75rem;
      color: #9ca3af;
      margin-bottom: 0.35rem;
    }}

    .selection-description {{
      font-size: 0.85rem;
      color: #d1d5db;
      margin-bottom: 0.25rem;
    }}

    .selection-pulses {{
      font-size: 0.75rem;
      color: #6b7280;
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

    .phase-heading {{
      margin-bottom: 0.6rem;
    }}

    .phase-title {{
      font-size: 0.95rem;
      font-weight: 600;
      margin-bottom: 0.1rem;
    }}

    .phase-cycle {{
      font-size: 0.8rem;
      color: #9ca3af;
      margin-bottom: 0.05rem;
    }}

    .phase-label {{
      font-size: 0.8rem;
      color: #6b7280;
    }}

    .tag-list {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      margin-top: 0.6rem;
      max-height: 460px;
      overflow-y: auto;
      padding-right: 0.25rem;
    }}

    .tag-row {{
      border-radius: 9999px;
      border: 1px solid #111827;
      padding: 0.3rem 0.6rem;
      background-color: #020617;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.82rem;
      cursor: pointer;
      transition: border-color 0.12s ease, background-color 0.12s ease, transform 0.08s ease;
    }}

    .tag-row:hover {{
      border-color: #38bdf8;
      background-color: #020617;
      transform: translateY(-1px);
    }}

    .tag-name {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      color: #e5e7eb;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 75%;
    }}

    .tag-count {{
      font-size: 0.75rem;
      color: #9ca3af;
      margin-left: 0.35rem;
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

    <div id="selectionPanel" class="selection-panel" style="display:none;">
      <div class="selection-title">Selected tag</div>
      <div class="selection-tag" id="selectionTag"></div>
      <div class="selection-meta" id="selectionMeta"></div>
      <div class="selection-description" id="selectionDescription"></div>
      <div class="selection-pulses" id="selectionPulses"></div>
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
      const payload = JSON.parse(raw || "{{}}");
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

      const selectionPanel = document.getElementById("selectionPanel");
      const selectionTag = document.getElementById("selectionTag");
      const selectionMeta = document.getElementById("selectionMeta");
      const selectionDescription = document.getElementById("selectionDescription");
      const selectionPulses = document.getElementById("selectionPulses");

      let currentSelection = null;

      function clearSelection() {{
        currentSelection = null;
        selectionPanel.style.display = "none";
        selectionTag.textContent = "";
        selectionMeta.textContent = "";
        selectionDescription.textContent = "";
        selectionPulses.textContent = "";
      }}

      function selectTag(tagRecord, phaseKey) {{
        if (!tagRecord) {{
          clearSelection();
          return;
        }}
        currentSelection = {{ ...tagRecord, phase: phaseKey }};
        selectionPanel.style.display = "block";
        selectionTag.textContent = tagRecord.tag || "";

        const phaseInfo = phaseMeta[phaseKey] || {{}};
        const count = tagRecord.count || 0;
        selectionMeta.textContent =
          (phaseInfo.title || phaseKey) +
          " • " +
          (phaseInfo.cycle || "") +
          (count ? " • pulses: " + count : "");

        const desc = (tagRecord.description || "").trim();
        selectionDescription.textContent = desc || "No description available.";

        const pulses = tagRecord.pulses || [];
        if (pulses.length) {{
          let text = "e.g. " + pulses.slice(0, 3).join(", ");
          if (pulses.length > 3) text += ", …";
          selectionPulses.textContent = text;
        }} else {{
          selectionPulses.textContent = "";
        }}
      }}

      function render() {{
        const phaseValue = phaseFilter.value;
        const searchValue = (searchBox.value || "").trim().toLowerCase();

        phaseGrid.innerHTML = "";
        let anyVisible = false;

        phaseOrder.forEach(phaseKey => {{
          const items = phases[phaseKey] || [];
          if (!items.length) return;

          if (phaseValue !== "all" && phaseValue !== phaseKey) return;

          // Filter by search
          const filtered = items.filter(item => {{
            const tag = (item.tag || "").toLowerCase();
            return !searchValue || tag.includes(searchValue);
          }});

          if (!filtered.length) return;

          anyVisible = true;

          const phaseCol = document.createElement("div");
          phaseCol.className = "phase-column";
          phaseCol.dataset.phase = phaseKey;

          const heading = document.createElement("div");
          heading.className = "phase-heading";

          const phaseInfo = phaseMeta[phaseKey] || {{}};

          const title = document.createElement("div");
          title.className = "phase-title";
          title.textContent = phaseInfo.title || phaseKey;

          const cycle = document.createElement("div");
          cycle.className = "phase-cycle";
          cycle.textContent = phaseInfo.cycle || "";

          const label = document.createElement("div");
          label.className = "phase-label";
          label.textContent = phaseInfo.label || "";

          heading.appendChild(title);
          heading.appendChild(cycle);
          heading.appendChild(label);

          const list = document.createElement("div");
          list.className = "tag-list";

          filtered.forEach(item => {{
            const row = document.createElement("div");
            row.className = "tag-row";
            row.dataset.tag = item.tag;
            row.dataset.phase = phaseKey;

            const nameEl = document.createElement("div");
            nameEl.className = "tag-name";
            nameEl.textContent = item.tag;

            const countEl = document.createElement("div");
            countEl.className = "tag-count";
            countEl.textContent = "pulses: " + (item.count || 0);

            row.appendChild(nameEl);
            row.appendChild(countEl);

            row.addEventListener("click", () => selectTag(item, phaseKey));

            list.appendChild(row);
          }});

          phaseCol.appendChild(heading);
          phaseCol.appendChild(list);
          phaseGrid.appendChild(phaseCol);
        }});

        noResults.style.display = anyVisible ? "none" : "block";

        // If search is cleared, also clear the selection panel
        if (!searchValue) {{
          clearSelection();
        }} else if (currentSelection) {{
          // If we have a selection, but it's no longer visible under filters, clear it
          const visiblePhase = phaseFilter.value === "all" ||
                               phaseFilter.value === currentSelection.phase;
          const tagMatchesSearch = (currentSelection.tag || "")
            .toLowerCase()
            .includes(searchValue);
          if (!visiblePhase || !tagMatchesSearch) {{
            clearSelection();
          }}
        }}
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
