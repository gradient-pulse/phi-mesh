import os
import yaml
import json
import networkx as nx
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
GRAPH_HTML_PATH = "docs/tag_map.html"
GRAPH_DATA_PATH = "docs/data.js"

def load_tag_index(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_graph(tag_index):
    G = nx.Graph()

    # Add nodes
    for tag in tag_index:
        G.add_node(tag)

    # Link tags based on co-occurrence in pulses
    pulse_to_tags = defaultdict(set)
    for tag, pulses in tag_index.items():
        for pulse in pulses:
            pulse_to_tags[pulse].add(tag)

    for tags in pulse_to_tags.values():
        tags = list(tags)
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                G.add_edge(tags[i], tags[j])

    return G

def compute_centrality(G):
    centrality = nx.degree_centrality(G)
    return centrality

def write_graph_data(G, centrality, output_path):
    nodes = [{"id": tag, "centrality": round(centrality.get(tag, 0.0), 3)} for tag in G.nodes]
    links = [{"source": a, "target": b} for a, b in G.edges]
    data = {"nodes": nodes, "links": links}

    with open(output_path, "w") as f:
        f.write("const graphData = ")
        json.dump(data, f, indent=2)
        f.write(";")

def copy_static_html():
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RGP Tag Map</title>
  <script src="graph.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; height: 100%; font-family: sans-serif; }}
    #sidebar {{
      position: fixed;
      left: 0; top: 0; bottom: 0;
      width: 320px;
      background: #f9f9f9;
      overflow-y: auto;
      padding: 16px;
      border-right: 1px solid #ddd;
    }}
    #graph {{
      margin-left: 320px;
      height: 100%;
    }}
    h2 {{ margin-top: 0; }}
    .link-section {{ margin-top: 12px; }}
    .link-section h4 {{ margin: 6px 0 3px; }}
    .link-section ul {{ padding-left: 16px; margin: 0; }}
    .link-section li {{ font-size: 0.9em; margin: 0; }}
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>RGP Tag Map</h2>
    <p><em>Coherence Tracking Across Fields—click a tag</em></p>
    <div id="tag-info"></div>
  </div>
  <div id="graph"></div>
  <script src="data.js"></script>
</body>
</html>
"""
    with open(GRAPH_HTML_PATH, "w") as f:
        f.write(html)

def main():
    try:
        print("🔁 Loading tag index...")
        tag_index = load_tag_index(TAG_INDEX_PATH)

        print("🧱 Building graph...")
        G = build_graph(tag_index)

        print("📊 Calculating centrality...")
        centrality = compute_centrality(G)

        print("📤 Writing graph data...")
        write_graph_data(G, centrality, GRAPH_DATA_PATH)

        print("🖼️ Writing static HTML viewer...")
        copy_static_html()

        print("✅ Tag map and data.js generated successfully.")
    except Exception as e:
        print(f"❌ Error generating tag map: {e}")
        exit(1)

if __name__ == "__main__":
    main()
