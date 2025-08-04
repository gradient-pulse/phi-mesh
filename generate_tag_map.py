import os
import yaml
import json
from collections import defaultdict

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PULSE_DIR = os.path.join(SCRIPT_DIR, "pulse")
TAG_INDEX_PATH = os.path.join(SCRIPT_DIR, "meta", "tag_index.yml")
HTML_OUTPUT = os.path.join(SCRIPT_DIR, "docs", "tag_map.html")
DATA_JS_OUTPUT = os.path.join(SCRIPT_DIR, "docs", "data.js")

# Utility to load YAML
def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Load pulses and collect tags, papers, podcasts
def collect_data():
    tag_to_pulses = defaultdict(set)
    tag_to_papers = defaultdict(set)
    tag_to_podcasts = defaultdict(set)

    for fname in os.listdir(PULSE_DIR):
        if not fname.endswith(".yml"):
            continue
        with open(os.path.join(PULSE_DIR, fname), 'r', encoding='utf-8') as f:
            doc = yaml.safe_load(f)

        tags = doc.get("tags", [])
        title = doc.get("title", fname.replace(".yml", ""))
        pulse_link = f"https://gradient-pulse.github.io/phi-mesh/pulse/{fname.replace('.yml', '.html')}"

        for tag in tags:
            tag_to_pulses[tag].add((title, pulse_link))

        for paper in doc.get("papers", []):
            for tag in tags:
                if isinstance(paper, dict):
                    tag_to_papers[tag].add(tuple(paper.items()))
                elif isinstance(paper, list):
                    for item in paper:
                        if isinstance(item, dict):
                            tag_to_papers[tag].add(tuple(item.items()))

        for podcast in doc.get("podcasts", []):
            for tag in tags:
                if isinstance(podcast, dict):
                    tag_to_podcasts[tag].add(tuple(podcast.items()))
                elif isinstance(podcast, list):
                    for item in podcast:
                        if isinstance(item, dict):
                            tag_to_podcasts[tag].add(tuple(item.items()))

    return tag_to_pulses, tag_to_papers, tag_to_podcasts

# Write data.js
def write_data_js(tag_to_pulses):
    nodes = [{"id": tag, "group": 1} for tag in tag_to_pulses]
    links = []
    tags = list(tag_to_pulses.keys())
    for i, source in enumerate(tags):
        for j in range(i + 1, len(tags)):
            target = tags[j]
            shared = len(set(p["path"] for p in tag_to_pulses[source]) &
                         set(p["path"] for p in tag_to_pulses[target]))
            if shared > 0:
                links.append({"source": source, "target": target, "value": shared})
    with open(DATA_JS_OUTPUT, "w", encoding="utf-8") as f:
        f.write(f"const graph = {json.dumps({'nodes': nodes, 'links': links}, indent=2)};")

# Copy base HTML template
def write_html():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>RGP Tag Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="data.js"></script>
    <script src="graph.js"></script>
    <style>
        body { margin: 0; font-family: sans-serif; }
        #sidebar {
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 250px;
            background: #f8f8f8;
            padding: 8px;
            overflow-y: auto;
            border-right: 1px solid #ccc;
        }
        #graph-container {
            position: absolute;
            left: 250px; top: 0; right: 0; bottom: 0;
        }
        ul { padding-left: 16px; }
        a { color: #00f; word-break: break-word; }
    </style>
</head>
<body>
    <div id="sidebar">
        <b>RGP Tag Map</b><br>
        <span>Coherence Tracking Across Fields—<br>click a tag</span><br><br>
        <div id="tag-details"></div>
    </div>
    <div id="graph-container"><svg width="100%" height="100%"></svg></div>
</body>
</html>
"""
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    pulses, papers, podcasts = collect_data()

    # Save full mapping for sidebar use
    sidebar_data = {
        "pulses": {k: v for k, v in pulses.items()},
        "papers": {k: sorted(list(v)) for k, v in papers.items()},
        "podcasts": {k: sorted(list(v)) for k, v in podcasts.items()},
    }
    with open(os.path.join(SCRIPT_DIR, "docs", "sidebar_data.json"), "w", encoding="utf-8") as f:
        json.dump(sidebar_data, f, indent=2)

    write_data_js(pulses)
    write_html()
