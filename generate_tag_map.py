import yaml
import os
import json
from pyvis.network import Network

# Load canonical tag mappings
def load_tag_index(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

# Load metadata and identify linkages
def collect_link_data(tag_index):
    tag_links = {}
    for tag, data in tag_index.items():
        if tag == "canonical_tags":
            continue
        tag_links[tag] = {
            "pulses": data.get("linked_pulses", []),
            "papers": data.get("linked_papers", []),
            "podcasts": data.get("linked_podcasts", []),
        }
    return tag_links

# Generate visual graph
def generate_tag_map():
    tag_index_path = "meta/tag_index.yml"
    output_path = "docs/tag_map.html"

    tag_index = load_tag_index(tag_index_path)
    tag_links = collect_link_data(tag_index)

    net = Network(height="900px", width="100%", bgcolor="#000000", font_color="white")

    # Add tag nodes
    for tag in tag_links:
        net.add_node(tag, label=tag, shape="ellipse", color="#00ffcc")

    # Link shared artifacts between tags (pulses, papers, podcasts)
    artifact_to_tags = {}
    for tag, links in tag_links.items():
        for kind in ["pulses", "papers", "podcasts"]:
            for item in links[kind]:
                artifact_to_tags.setdefault(item, set()).add(tag)

    for artifact, tags in artifact_to_tags.items():
        tags = list(tags)
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                net.add_edge(tags[i], tags[j], color="#888888")

    # Set clean visualization options (JSON-compliant)
    net.set_options('''
{
  "nodes": {
    "font": {
      "size": 18,
      "face": "Arial"
    },
    "borderWidth": 2
  },
  "edges": {
    "color": {
      "inherit": true
    },
    "smooth": {
      "enabled": true
    }
  },
  "physics": {
    "enabled": true,
    "stabilization": {
      "enabled": true
    }
  },
  "layout": {
    "improvedLayout": true
  }
}
''')

    # Save map
    net.show(output_path)

if __name__ == "__main__":
    generate_tag_map()
