import os
import json
import yaml
import networkx as nx
from meta.tag_index_utils import extract_tags_from_yaml

# Paths
PULSE_DIR = "phi-mesh/pulse"
TAG_INDEX_PATH = "meta/tag_index.yml"
HTML_PATH = "docs/tag_map.html"
JS_PATH = "docs/data.js"

# Load tag index
with open(TAG_INDEX_PATH, "r") as f:
    tag_index = yaml.safe_load(f)

def collect_tag_links(tag):
    links = {"papers": [], "podcasts": [], "pulses": []}
    for root, _, files in os.walk(PULSE_DIR):
        for file in files:
            if file.endswith(".yml"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    try:
                        data = yaml.safe_load(f)
                        if not data:
                            continue
                        pulse_tags = data.get("tags", [])
                        if tag in pulse_tags:
                            if "papers" in data:
                                links["papers"].extend(data["papers"])
                            if "podcasts" in data:
                                links["podcasts"].extend(data["podcasts"])
                            links["pulses"].append({"title": data.get("title", file), "path": path})
                    except yaml.YAMLError:
                        continue
    return links

def truncate(text, max_length=50):
    return text if len(text) <= max_length else text[:max_length - 3] + "..."

def build_graph(tag_index):
    G = nx.Graph()
    for tag, related in tag_index.items():
        G.add_node(tag, **collect_tag_links(tag))
        for r in related.get("related", []):
            G.add_edge(tag, r)
    return G

def render_data_js(G):
    nodes = []
    links = []
    for node in G.nodes:
        links_data = G.nodes[node]
        nodes.append({
            "id": node,
            "papers": links_data.get("papers", []),
            "podcasts": links_data.get("podcasts", []),
            "pulses": links_data.get("pulses", []),
        })
    for source, target in G.edges:
        links.append({"source": source, "target": target})
    with open(JS_PATH, "w") as f:
        f.write(f"const data = {json.dumps({"nodes": nodes, "links": links}, indent=2)};")

def copy_template_html():
    template_path = "meta/tag_map_template.html"
    if os.path.exists(template_path):
        with open(template_path, "r") as src:
            content = src.read()
        with open(HTML_PATH, "w") as dst:
            dst.write(content)

if __name__ == "__main__":
    G = build_graph(tag_index)
    render_data_js(G)
    copy_template_html()
