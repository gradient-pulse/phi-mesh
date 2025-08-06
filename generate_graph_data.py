import yaml
import json

with open("meta/tag_index.yml", "r") as f:
    tag_index = yaml.safe_load(f)

def build_graph_data(tag_index):
    nodes = []
    links = []

    for tag, metadata in tag_index.items():
        nodes.append({"id": tag})

        if not isinstance(metadata, dict):
            print(f"⚠️ Skipping tag '{tag}': metadata is not a dict")
            continue

        for linked_tag in metadata.get("links", []):
            links.append({
                "source": tag,
                "target": linked_tag
            })

    return {"nodes": nodes, "links": links}

graph_data = build_graph_data(tag_index)

with open("docs/graph_data.js", "w") as f:
    f.write("const graphData = ")
    json.dump(graph_data, f, indent=2)
    f.write(";")
