import yaml
import json

# Load tag index
with open("meta/tag_index.yml", "r") as f:
    raw_data = yaml.safe_load(f)

# Normalize tag entries
normalized_tags = []
for entry in raw_data:
    if isinstance(entry, str):
        normalized_tags.append({
            "tag": entry,
            "centrality": 0.0,
            "links": []
        })
    elif isinstance(entry, dict):
        normalized_tags.append(entry)

def build_graph_data(tag_entries):
    nodes = []
    links = []
    tag_lookup = {entry["tag"]: idx for idx, entry in enumerate(tag_entries)}

    for idx, entry in enumerate(tag_entries):
        tag = entry["tag"]
        centrality = entry.get("centrality", 0)
        nodes.append({
            "id": idx,
            "label": tag,
            "centrality": centrality
        })

        for linked_tag in entry.get("links", []):
            if linked_tag in tag_lookup:
                links.append({
                    "source": idx,
                    "target": tag_lookup[linked_tag]
                })

    return {"nodes": nodes, "links": links}

graph_data = build_graph_data(normalized_tags)

# Output file
with open("docs/graph_data.js", "w") as f:
    f.write("const graph = ")
    json.dump(graph_data, f, indent=2)
    f.write(";")    
