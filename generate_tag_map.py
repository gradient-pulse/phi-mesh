import os
import json
import yaml
import networkx as nx

from meta.tag_index_utils import load_tag_index  # Corrected import

TAG_INDEX_PATH = "meta/tag_index.yml"
HTML_TEMPLATE_PATH = "docs/tag_map_template.html"
DATA_JS_PATH = "docs/data.js"
OUTPUT_HTML_PATH = "docs/tag_map.html"

DEFAULT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RGP Tag Map</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #fff; }
    h1 { font-size: 24px; }
  </style>
</head>
<body>
  <h1>RGP Tag Map</h1>
  <p>Graph will load here.</p>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="data.js"></script>
  <script>
    // Your D3 visualization will mount here
  </script>
</body>
</html>
"""

def build_graph(tag_index):
    G = nx.Graph()
    for tag, entry in tag_index.items():
        G.add_node(tag)
        for linked in entry.get("links", []):
            if linked in tag_index:  # Avoid linking to undefined nodes
                G.add_edge(tag, linked)
    return G

def compute_centrality(G):
    return nx.degree_centrality(G)

def generate_js_data(G, centrality):
    nodes = []
    links = []

    for node in G.nodes():
        nodes.append({
            "id": node,
            "group": 1,
            "centrality": centrality.get(node, 0)
        })

    for source, target in G.edges():
        links.append({"source": source, "target": target})

    return {"nodes": nodes, "links": links}

def write_data_js(data):
    with open(DATA_JS_PATH, "w") as f:
        f.write("const graphData = ")
        json.dump(data, f, indent=2)
        f.write(";")

def update_html_wrapper():
    if os.path.exists(HTML_TEMPLATE_PATH):
        with open(HTML_TEMPLATE_PATH, "r") as template_file:
            template = template_file.read()
    else:
        print("⚠️ No tag_map_template.html found. Using fallback HTML.")
        template = DEFAULT_HTML_TEMPLATE

    with open(OUTPUT_HTML_PATH, "w") as out_file:
        out_file.write(template)

def main():
    try:
        tag_index = load_tag_index(TAG_INDEX_PATH)
        G = build_graph(tag_index)
        centrality = compute_centrality(G)
        data = generate_js_data(G, centrality)
        write_data_js(data)
        update_html_wrapper()
        print("✅ Tag map generation complete.")
    except Exception as e:
        print(f"❌ Error generating tag map: {e}")
        raise

if __name__ == "__main__":
    main()
