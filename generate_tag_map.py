import yaml
import os
import json
from pyvis.network import Network
from jinja2 import Template

def load_tag_index(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

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

def generate_tag_map():
    tag_index_path = "meta/tag_index.yml"
    output_path = "docs/tag_map.html"
    template_path = "pyvis_template.html"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    tag_index = load_tag_index(tag_index_path)
    tag_links = collect_link_data(tag_index)

    # Initialize PyVis Network
    net = Network(height="900px", width="100%", bgcolor="#000000", font_color="white", directed=False)

    # Add tag nodes
    for tag in tag_links:
        net.add_node(tag, label=tag, shape="ellipse", color="#00ffcc")

    # Link tags that share any artifact
    artifact_to_tags = {}
    for tag, links in tag_links.items():
        for kind in ["pulses", "papers", "podcasts"]:
            for item in links[kind]:
                artifact_to_tags.setdefault(item, set()).add(tag)

    for artifact, tags in artifact_to_tags.items():
        tag_list = list(tags)
        for i in range(len(tag_list)):
            for j in range(i + 1, len(tag_list)):
                net.add_edge(tag_list[i], tag_list[j], color="#888888")

    # Valid JSON string for net.set_options()
    options_json = json.dumps({
        "nodes": {
            "font": {
                "size": 18,
                "face": "Arial"
            },
            "borderWidth": 2
        },
        "edges": {
            "color": {
                "inherit": True
            },
            "smooth": {
                "enabled": True
            }
        },
        "physics": {
            "enabled": True,
            "stabilization": {
                "enabled": True
            }
        },
        "layout": {
            "improvedLayout": True
        }
    })

    net.set_options(options_json)

    # Load dark theme template (via Jinja2) for GitHub Actions compatibility
    with open(template_path, "r") as f:
        custom_template = Template(f.read())
    net.show(output_path, notebook=False, template=custom_template)

if __name__ == "__main__":
    generate_tag_map()
