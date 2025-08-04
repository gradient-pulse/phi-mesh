import os
import yaml
import json
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_PATH = "docs/data.js"


def load_tag_index():
    with open(TAG_INDEX_PATH, 'r') as f:
        return yaml.safe_load(f)


def generate_graph(tag_index):
    nodes = []
    links = []
    tag_set = set(tag_index.keys())
    
    # Create a node for each tag
    for tag in sorted(tag_set):
        nodes.append({"id": tag, "centrality": 0.0})

    # Invert the tag index: for each pulse, list all associated tags
    pulse_to_tags = defaultdict(set)
    for tag, pulses in tag_index.items():
        for pulse in pulses:
            pulse_to_tags[pulse].add(tag)

    # Generate links between co-occurring tags
    seen_links = set()
    for tags in pulse_to_tags.values():
        tag_list = sorted(tags)
        for i in range(len(tag_list)):
            for j in range(i + 1, len(tag_list)):
                a, b = tag_list[i], tag_list[j]
                link_key = tuple(sorted((a, b)))
                if link_key not in seen_links:
                    links.append({"source": a, "target": b})
                    seen_links.add(link_key)

    return {"nodes": nodes, "links": links}


def write_data_js(graph):
    with open(OUTPUT_PATH, 'w') as f:
        f.write("const graphData = ")
        json.dump(graph, f, indent=2)
        f.write(";")


def main():
    tag_index = load_tag_index()
    graph = generate_graph(tag_index)
    write_data_js(graph)
    print("✅ Tag map and data.js generated successfully.")


if __name__ == "__main__":
    main()
