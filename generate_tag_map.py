import yaml
import networkx as nx
from pyvis.network import Network

# Load tag_index.yml
with open("meta/tag_index.yml", "r") as f:
    tag_data = yaml.safe_load(f)

# Create a graph
G = nx.Graph()
for tag, data in tag_data.get('tags', {}).items():
    G.add_node(tag, title=data.get('description', 'No description'))
    for related in data.get('related_concepts', []):
        if related != tag:
            G.add_edge(tag, related)

# Create Pyvis interactive network
net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
net.from_nx(G)
net.repulsion(node_distance=150, central_gravity=0.33)

# Save HTML to visuals/tag_map.html
net.show("visuals/tag_map.html")
