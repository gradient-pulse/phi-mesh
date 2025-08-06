import yaml
import json

with open("meta/tag_index.yml") as f:
    tag_index = yaml.safe_load(f)

def build_graph_data(index):
    nodes = []
    links = []
    seen = set()

    for tag, metadata in index.items():
        nodes.append({"id": tag})
        if isinstance(metadata, dict):
            for linked_tag in metadata.get("links", []):
                key = tuple(sorted([tag, linked_tag]))
                if key not in seen:
                    links.append({"source": tag, "target": linked_tag})
                    seen.add(key)
        else:
            print(f"⚠️ Skipping tag '{tag}' due to unexpected format: {metadata}")

    return {"nodes": nodes, "links": links}

graph_data = build_graph_data(tag_index)

with open("docs/archive/graph_data.js", "w") as f:
    f.write("const graphData = ")
    json.dump(graph_data, f, indent=2)
    f.write(";\n")
