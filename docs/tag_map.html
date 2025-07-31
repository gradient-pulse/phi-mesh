# Updated generate_tag_map.py to include linked_papers and linked_podcasts

import os
import yaml
import networkx as nx
from pyvis.network import Network
from datetime import datetime
from pathlib import Path

TAG_INDEX_PATH = "meta/tag_index.yml"
LINK_INDEX_PATH = "meta/link_index.yml"
OUTPUT_HTML_PATH = "docs/tag_map.html"

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def add_node(net, name, count=0, is_orphan=False):
    label = f"{name}\n{count} links"
    title = f"{name} (linked: {count})"
    color = "#cccccc" if is_orphan else None
    shape = "ellipse"
    net.add_node(name, label=label, title=title, color=color, shape=shape)

def generate_tag_map():
    tag_data = load_yaml(TAG_INDEX_PATH)
    link_data = load_yaml(LINK_INDEX_PATH)

    G = nx.Graph()
    all_tags = {k for k in tag_data if k != 'canonical_tags'}

    # Create graph edges based on shared pulses
    for tag1 in all_tags:
        for tag2 in all_tags:
            if tag1 >= tag2:
                continue
            shared = set(tag_data[tag1].get("linked_pulses", [])) & set(tag_data[tag2].get("linked_pulses", []))
            if shared:
                G.add_edge(tag1, tag2, weight=len(shared))

    # Add nodes and detect orphans
    orphans = [tag for tag in all_tags if tag not in G.nodes]
    net = Network(height='950px', width='100%', bgcolor='#ffffff', font_color='black')

    for tag in G.nodes:
        count = G.degree(tag)
        add_node(net, tag, count)
    for orphan in orphans:
        add_node(net, orphan, is_orphan=True)

    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, value=d['weight'])

    # Attach linked papers and podcasts to central tags
    for key, value in link_data.items():
        if key.startswith("zenodo"):
            title = value.get("title", "Untitled")
            for tag in tag_data:
                if tag.lower() in title.lower():
                    G.add_node(title)
                    G.add_edge(tag, title)

    net.set_options('''
    var options = {
      nodes: {
        borderWidth: 1,
        size: 20,
        font: {
          size: 18
        },
        shapeProperties: {
          interpolation: false
        }
      },
      edges: {
        color: {inherit: true},
        width: 0.5,
        smooth: {
          type: "continuous"
        }
      },
      physics: {
        stabilization: true,
        barnesHut: {
          springLength: 200
        }
      }
    }
    ''')

    net.show(OUTPUT_HTML_PATH)
    print(f"✅ Tag map generated: {OUTPUT_HTML_PATH}")

if __name__ == "__main__":
    generate_tag_map()
