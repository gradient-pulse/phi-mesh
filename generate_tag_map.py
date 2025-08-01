import json
import yaml

with open("meta/tag_index.yml", "r") as f:
    tag_index = yaml.safe_load(f)

nodes = [{"id": k, "centrality": v.get("centrality", 0)} for k, v in tag_index.items()]
edges = []
for k, v in tag_index.items():
    for link in v.get("links", []):
        if link in tag_index:
            edges.append({"source": k, "target": link})

graph = {"nodes": nodes, "links": edges}

with open("docs/data.js", "w") as f:
    f.write("const graphData = ")
    json.dump(graph, f, indent=2)
    f.write(";")
