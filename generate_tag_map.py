import os
import sys
import json
import yaml
import networkx as nx

# Ensure meta is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "meta")))
from tag_index_utils import load_tag_index

TAG_INDEX_PATH = "meta/tag_index.yml"
HTML_TEMPLATE_PATH = "docs/tag_map_template.html"
DATA_JS_PATH = "docs/data.js"
OUTPUT_HTML_PATH = "docs/tag_map.html"

def build_graph(tag_index):
    G = nx.Graph()
    for tag, entry in tag_index.items():
        G.add_node(tag)
        for linked in entry.get("links", []):
            G.add_edge(tag, linked)
    return G

def compute_centrality(G):
    return nx.degree_centrality(G)

def generate_js_data(G, centrality):
    nodes = []
    links = []

    for i, node in enumerate(G.nodes()):
        nodes.append({
            "id": node,
            "group": 1,
            "centrality": centrality.get(node, 0),
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
    with open(HTML_TEMPLATE_PATH, "r") as template_file:
        template = template_file.read()

    with open(OUTPUT_HTML_PATH, "w") as out_file:
        out_file.write(template)

def main():
    tag_index = load_tag_index(TAG_INDEX_PATH)
    G = build_graph(tag_index)
    centrality = compute_centrality(G)
    data = generate_js_data(G, centrality)
    write_data_js(data)
    update_html_wrapper()
    print("✅ Tag map generation complete.")

if __name__ == "__main__":
    main()
