import os
import json
import yaml
import networkx as nx

from meta.tag_index_utils import load_tag_index

TAG_INDEX_PATH = "meta/tag_index.yml"
HTML_TEMPLATE_PATH = "docs/tag_map_template.html"
DATA_JS_PATH = "docs/data.js"
OUTPUT_HTML_PATH = "docs/tag_map.html"

def build_graph(tag_index):
    G = nx.Graph()
    for tag, entry in tag_index.items():
        G.add_node(tag)
        for linked in entry.get("links", []):
            if linked in tag_index:
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
    if not os.path.exists(HTML_TEMPLATE_PATH):
        raise FileNotFoundError(f"Missing HTML template at: {HTML_TEMPLATE_PATH}")
    with open(HTML_TEMPLATE_PATH, "r") as template_file:
        html = template_file.read()
    with open(OUTPUT_HTML_PATH, "w") as out_file:
        out_file.write(html)

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
        print(f"❌ Error during tag map generation: {e}")
        raise

if __name__ == "__main__":
    main()
