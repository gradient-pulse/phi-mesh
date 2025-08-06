import yaml
import json

# Path to source YAML and output JS
TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_JS_PATH = "docs/graph_data.js"

def load_tag_index(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_graph_data(tag_index):
    nodes = set()
    links = []

    for tag, metadata in tag_index.items():
        nodes.add(tag)
        for linked_tag in metadata.get("links", []):
            nodes.add(linked_tag)
            links.append({"source": tag, "target": linked_tag})

    return {
        "nodes": [{"id": tag} for tag in sorted(nodes)],
        "links": links
    }

def write_graph_data_js(graph_data, path):
    with open(path, "w") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";\n")

if __name__ == "__main__":
    tag_index = load_tag_index(TAG_INDEX_PATH)
    graph_data = build_graph_data(tag_index)
    write_graph_data_js(graph_data, OUTPUT_JS_PATH)
    print(f"✅ graph_data.js updated with {len(graph_data['nodes'])} nodes and {len(graph_data['links'])} links.")
