import os
import yaml
import json

PULSE_DIR = "pulse"
TAG_INDEX_PATH = "meta/tag_index.yml"
GRAPH_DATA_PATH = "docs/data.js"


def load_yaml_file(filepath):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def load_all_pulses():
    pulses = []
    for root, _, files in os.walk(PULSE_DIR):
        for file in files:
            if file.endswith(".yml"):
                path = os.path.join(root, file)
                data = load_yaml_file(path)
                data["_filename"] = path  # store path for later reference
                pulses.append(data)
    return pulses


def build_graph_data(tag_index):
    nodes = []
    links = []
    tag_to_pulses = {}

    # Build pulse lookup
    pulses = load_all_pulses()
    for pulse in pulses:
        for tag in pulse.get("tags", []):
            if tag not in tag_to_pulses:
                tag_to_pulses[tag] = []
            tag_to_pulses[tag].append(pulse)

    for tag, metadata in tag_index.items():
        node = {
            "id": tag,
            "pulses": [],
            "papers": [],
            "podcasts": []
        }

        # Attach pulses
        for pulse in tag_to_pulses.get(tag, [])[:3]:
            title = pulse.get("title", pulse.get("_filename"))
            path = pulse.get("_filename", "")
            node["pulses"].append({"title": title, "path": path})

        # Attach up to 3 papers & podcasts
        papers = []
        podcasts = []
        for pulse in tag_to_pulses.get(tag, []):
            papers.extend(pulse.get("papers", []))
            podcasts.extend(pulse.get("podcasts", []))

        node["papers"] = papers[:3]
        node["podcasts"] = podcasts[:3]

        nodes.append(node)

        for linked_tag in metadata.get("links", []):
            links.append({"source": tag, "target": linked_tag})

    return {"nodes": nodes, "links": links}


def save_graph_data(graph_data):
    with open(GRAPH_DATA_PATH, "w") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";")


if __name__ == "__main__":
    tag_index = load_yaml_file(TAG_INDEX_PATH)
    graph_data = build_graph_data(tag_index)
    save_graph_data(graph_data)
    print("✅ Graph data generated and saved to docs/data.js")
