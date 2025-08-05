import os
import yaml
import json
from collections import defaultdict

PULSE_DIR = "pulse"
TAG_INDEX_FILE = "meta/tag_index.yml"
GRAPH_JS_FILE = "docs/graph_data.js"

def extract_tag_data():
    tag_to_pulses = defaultdict(set)
    pulse_files = [f for f in os.listdir(PULSE_DIR) if f.endswith(".yml")]

    for filename in pulse_files:
        with open(os.path.join(PULSE_DIR, filename), "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                tags = data.get("tags", [])
                for tag in tags:
                    tag_to_pulses[tag].add(filename)
            except yaml.YAMLError:
                continue

    return tag_to_pulses

def build_tag_links(tag_to_pulses):
    tag_links = defaultdict(lambda: {"links": set(), "pulses": set()})

    for pulse_file in set(p for ps in tag_to_pulses.values() for p in ps):
        tags_in_pulse = [tag for tag, ps in tag_to_pulses.items() if pulse_file in ps]
        for tag in tags_in_pulse:
            tag_links[tag]["pulses"].add(pulse_file)
            for other_tag in tags_in_pulse:
                if other_tag != tag:
                    tag_links[tag]["links"].add(other_tag)

    tag_index = {
        tag: {
            "links": sorted(list(data["links"])),
            "pulses": sorted(list(data["pulses"]))
        }
        for tag, data in tag_links.items()
    }

    return tag_index

def write_tag_index(tag_index):
    os.makedirs(os.path.dirname(TAG_INDEX_FILE), exist_ok=True)
    with open(TAG_INDEX_FILE, "w", encoding="utf-8") as f:
        yaml.dump(tag_index, f, allow_unicode=True, sort_keys=True)

def build_graph_data(tag_index):
    nodes = sorted([{"id": tag} for tag in tag_index], key=lambda x: x["id"].lower())
    links = []
    for src, entry in tag_index.items():
        for dst in entry.get("links", []):
            links.append({"source": src, "target": dst})
    return {"nodes": nodes, "links": links}

def write_graph_data_js(graph_data):
    os.makedirs(os.path.dirname(GRAPH_JS_FILE), exist_ok=True)
    with open(GRAPH_JS_FILE, "w", encoding="utf-8") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";")

def main():
    tag_to_pulses = extract_tag_data()
    tag_index = build_tag_links(tag_to_pulses)
    write_tag_index(tag_index)
    graph_data = build_graph_data(tag_index)
    write_graph_data_js(graph_data)

if __name__ == "__main__":
    main()
