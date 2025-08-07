
import yaml
import json
import os

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_PATH = "docs/graph_data.js"

def load_tag_index():
    with open(TAG_INDEX_PATH, "r") as f:
        return yaml.safe_load(f)

def build_graph_data(tag_index):
    nodes = []
    links = []

    # Create nodes
    for tag, data in tag_index.items():
        node = {
            "id": tag,
            "centrality": data.get("centrality", 0),
            "num_links": len(data.get("links", []))
        }
        nodes.append(node)

    # Create links
    for source_tag, metadata in tag_index.items():
        if isinstance(metadata, dict):
            for linked_tag in metadata.get("links", []):
                links.append({
                    "source": source_tag,
                    "target": linked_tag
                })

    return {"nodes": nodes, "links": links}

def write_graph_data_js(graph_data):
    with open(OUTPUT_PATH, "w") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";")

if __name__ == "__main__":
    tag_index = load_tag_index()
    graph_data = build_graph_data(tag_index)
    write_graph_data_js(graph_data)
