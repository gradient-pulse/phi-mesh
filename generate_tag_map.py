# generate_tag_map.py

import yaml
import json
import networkx as nx
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_DATA_JS = "docs/data.js"

# Load tag index
with open(TAG_INDEX_PATH, "r") as f:
    tag_index = yaml.safe_load(f)

# Build reverse index: pulse → list of tags
pulse_to_tags = defaultdict(set)
for tag, info in tag_index.items():
    if tag == "canonical_tags":
        continue
    for pulse in info.get("linked_pulses", []):
        pulse_to_tags[pulse].add(tag)

# Initialize graph
G = nx.Graph()

# Add all tags as nodes
for tag in tag_index:
    if tag != "canonical_tags":
        G.add_node(tag)

# For each pulse, create links between co-occurring tags
for tags in pulse_to_tags.values():
    tag_list = list(tags)
    for i in range(len(tag_list)):
        for j in range(i + 1, len(tag_list)):
            G.add_edge(tag_list[i], tag_list[j])

# Calculate centrality
centrality = nx.degree_centrality(G)
orphans = [n for n in G.nodes if G.degree[n] == 0]

# Build output data structures
nodes = [
    {
        "id": node,
        "centrality": round(centrality[node], 3),
        "orphan": node in orphans
    }
    for node in sorted(G.nodes)
]

links = [
    {"source": u, "target": v}
    for u, v in G.edges
]

# Write to data.js
with open(OUTPUT_DATA_JS, "w") as f:
    f.write("const nodes = ")
    json.dump(nodes, f, indent=2)
    f.write(";\nconst links = ")
    json.dump(links, f, indent=2)
    f.write(";\n")
