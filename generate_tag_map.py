import yaml
import networkx as nx
import os
import json

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_DATA_JS = "docs/data.js"

with open(TAG_INDEX_PATH, "r") as f:
    tag_index = yaml.safe_load(f)

tags = list(tag_index.keys())
G = nx.Graph()

# Add nodes
for tag in tags:
    G.add_node(tag)

# Add edges based on tag relationships
for tag, info in tag_index.items():
    related_tags = info.get("related", [])
    for related in related_tags:
        if related in tags:
            G.add_edge(tag, related)

# Compute metrics
centrality = nx.degree_centrality(G)
orphans = [n for n in G.nodes if G.degree[n] == 0]

# Serialize nodes and edges
nodes_data = [
    {
        "id": node,
        "centrality": round(centrality[node], 3),
        "orphan": node in orphans,
    }
    for node in G.nodes()
]
edges_data = [{"source": u, "target": v} for u, v in G.edges()]

# Write data.js (used by tag_map.html)
data_js = f"const nodes = {json.dumps(nodes_data, indent=2)};\n"
data_js += f"const links = {json.dumps(edges_data, indent=2)};\n"

with open(OUTPUT_DATA_JS, "w") as f:
    f.write(data_js)

print("✅ data.js generated successfully.")
