import os
import json
import networkx as nx
import yaml

# File paths
TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_DIR = "docs"
DATA_JS = os.path.join(OUTPUT_DIR, "data.js")
HTML_FILE = os.path.join(OUTPUT_DIR, "tag_map.html")

# Load YAML
def load_yaml_file(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Build Graph
def build_graph(tag_index):
    G = nx.Graph()
    for tag, data in tag_index.items():
        G.add_node(tag)
        for linked_tag in data.get("links", []):
            if G.has_edge(tag, linked_tag):
                G[tag][linked_tag]["weight"] += 1
            else:
                G.add_edge(tag, linked_tag, weight=1)
    return G

# Extract Resource Titles
def gather_resources(tag_index):
    tag_resources = {}
    for tag, data in tag_index.items():
        tag_resources[tag] = {
            "papers": sorted(set(p["title"] for p in data.get("papers", []))),
            "podcasts": sorted(set(p["title"] for p in data.get("podcasts", []))),
            "pulses": sorted(set(p["title"] for p in data.get("pulses", []))),
        }
    return tag_resources

# Export data.js
def export_data_js(G, tag_resources):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    nodes = [{"id": tag, "resources": tag_resources.get(tag, {})} for tag in G.nodes]
    links = [{"source": u, "target": v, "weight": G[u][v]["weight"]} for u, v in G.edges]
    data = {"nodes": nodes, "links": links}
    with open(DATA_JS, "w") as f:
        f.write("const graphData = ")
        json.dump(data, f, indent=2)

# Export tag_map.html (minimal template for now)
def copy_template_html():
    template = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RGP Tag Map</title>
</head>
<body>
  <h1>RGP Tag Map</h1>
  <script src="data.js"></script>
  <script>
    document.write("<pre>" + JSON.stringify(graphData, null, 2) + "</pre>");
  </script>
</body>
</html>
'''
    with open(HTML_FILE, "w") as f:
        f.write(template)

# Main logic
def main():
    tag_index = load_yaml_file(TAG_INDEX_PATH)
    G = build_graph(tag_index)
    tag_resources = gather_resources(tag_index)
    export_data_js(G, tag_resources)
    copy_template_html()

if __name__ == "__main__":
    main()
