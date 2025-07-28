import os
import yaml
import pyvis
from pyvis.network import Network
from jinja2 import Environment, FileSystemLoader

# Manually register Jinja2 environment for pyvis
template_dir = os.path.join(os.path.dirname(pyvis.__file__), 'templates')
if not os.path.exists(template_dir):
    raise FileNotFoundError("Pyvis template folder not found. This prevents rendering the HTML file.")

env = Environment(loader=FileSystemLoader(template_dir))

# Load tag data
tag_file = "meta/tag_index.yml"
with open(tag_file, 'r') as f:
    tags = yaml.safe_load(f).get("tags", {})

# Initialize network
g = Network(height='900px', width='100%', bgcolor='#111111', font_color='white')
g.force_atlas_2based()

# Add nodes
for tag, info in tags.items():
    description = info.get("description", "")
    count = info.get("count", 0)
    size = 10 + 4 * count
    g.add_node(tag, label=tag, title=description, size=size, color='#86e0f3')

# Add edges based on related_concepts
for tag, info in tags.items():
    related = info.get("related_concepts", [])
    for rel in related:
        if rel in tags:
            g.add_edge(tag, rel, color='#ccc')

# Ensure output directory exists
os.makedirs("docs", exist_ok=True)

# Write the map to GitHub Pages-visible location
g.write_html("docs/tag_map.html")
