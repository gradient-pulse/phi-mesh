import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import os
from meta.tag_index import tag_index
from meta.link_index import link_index

# Initialize graph
G = nx.Graph()

# Add tag nodes
for tag in tag_index:
    G.add_node(tag, type="tag")

# Add edges from tag_index
for tag, data in tag_index.items():
    for related_tag in data.get("related", []):
        if related_tag in G:
            G.add_edge(tag, related_tag)

# Add edges from link_index (e.g., podcast, paper connections)
for item_id, item_data in link_index.items():
    tags = item_data.get("tags", [])
    for i, tag1 in enumerate(tags):
        for tag2 in tags[i + 1:]:
            if G.has_node(tag1) and G.has_node(tag2):
                G.add_edge(tag1, tag2)

# Create Pyvis network
net = Network(height='1000px', width='100%', bgcolor='#000000', font_color='white')

# Node size based on centrality
centrality = nx.degree_centrality(G)

for node in G.nodes():
    net.add_node(
        node,
        label=node,
        title=node,
        color='deepskyblue',
        size=15 + 25 * centrality.get(node, 0)
    )

for source, target in G.edges():
    net.add_edge(source, target, color='rgba(255,255,255,0.2)')

# Enable physics and clustering for elegance
net.barnes_hut(gravity=-20000, central_gravity=0.3, spring_length=200, spring_strength=0.001, damping=0.9)

# Add header HTML for styling and link injection
header_html = '''
<style>
  h1 {
    font-family: sans-serif;
    font-size: 24px;
    color: deepskyblue;
    text-align: center;
    margin-top: 10px;
  }
</style>
<h1>Phi-Mesh Tag Map</h1>
'''

# Generate and customize HTML
output_path = os.path.join("docs", "tag_map.html")
net.show(output_path)

# Inject header into the HTML
with open(output_path, "r") as f:
    html = f.read()

html = html.replace("</head>", f"{header_html}</head>")

with open(output_path, "w") as f:
    f.write(html)
