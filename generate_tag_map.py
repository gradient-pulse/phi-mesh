import yaml
import json
import os

# Path constants
PULSE_DIR = "pulse"
OUTPUT_HTML = "docs/tag_map.html"
OUTPUT_DATA = "docs/data.js"
TAG_INDEX_FILE = "meta/tag_index.yml"

# Load all .yml files from the pulse directory
def load_pulses():
    pulses = []
    for filename in os.listdir(PULSE_DIR):
        if filename.endswith(".yml"):
            with open(os.path.join(PULSE_DIR, filename), "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                    if data:
                        data["filename"] = os.path.join(PULSE_DIR, filename)
                        pulses.append(data)
                except yaml.YAMLError:
                    print(f"Error parsing {filename}")
    return pulses

# Build tag index from pulses
def build_tag_index(pulses):
    tag_index = {}
    for pulse in pulses:
        tags = pulse.get("tags", [])
        for tag in tags:
            if tag not in tag_index:
                tag_index[tag] = {"links": set(), "pulses": []}
            tag_index[tag]["pulses"].append(pulse["filename"])
            for linked_tag in tags:
                if linked_tag != tag:
                    tag_index[tag]["links"].add(linked_tag)
    # Convert sets to sorted lists
    for tag in tag_index:
        tag_index[tag]["links"] = sorted(tag_index[tag]["links"])
    return tag_index

# Build graph data for D3.js

def build_graph_data(tag_index):
    nodes = sorted([{"id": tag} for tag in tag_index.keys()], key=lambda x: x["id"].lower())
    links = []
    for src, entry in tag_index.items():
        for dst in entry["links"]:
            if src < dst:  # avoid duplicate edges
                links.append({"source": src, "target": dst})
    return {"nodes": nodes, "links": links}

# Write the JavaScript data file
def write_data_js(graph_data):
    with open(OUTPUT_DATA, "w", encoding="utf-8") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";")

# Main function to run the process
def main():
    pulses = load_pulses()
    tag_index = build_tag_index(pulses)
    graph_data = build_graph_data(tag_index)
    write_data_js(graph_data)

if __name__ == "__main__":
    main()
