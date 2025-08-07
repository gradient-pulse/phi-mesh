
import yaml
import json

with open("meta/tag_index.yml", "r") as f:
    tag_index = yaml.safe_load(f)

def build_graph_data(tag_index):
    graph = {
        "nodes": [],
        "links": []
    }

    tag_names = set()
    for entry in tag_index:
        tag = entry.get("tag")
        tag_names.add(tag)
        graph["nodes"].append({
            "id": tag,
            "centrality": entry.get("centrality", 0)
        })

    for entry in tag_index:
        source = entry.get("tag")
        for linked_tag in entry.get("links", []):
            if linked_tag in tag_names:
                graph["links"].append({
                    "source": source,
                    "target": linked_tag
                })

    return graph

graph_data = build_graph_data(tag_index)

with open("docs/graph_data.js", "w") as f:
    f.write("const graphData = ")
    json.dump(graph_data, f, indent=2)
    f.write(";\n")
