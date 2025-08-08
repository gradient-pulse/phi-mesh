# generate_link_index.py — builds link_index.js from pulse files

import os
import yaml
import json

PULSE_DIR = "pulse"
OUTPUT_PATH = "docs/link_index.js"

def extract_links_from_pulse(file_path):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    tags = data.get("tags", [])
    papers = data.get("papers", [])
    podcasts = data.get("podcasts", [])
    return tags, papers, podcasts

def build_link_index():
    index = {}

    for root, _, files in os.walk(PULSE_DIR):
        for file in files:
            if file.endswith(".yml"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=".")

                tags, papers, podcasts = extract_links_from_pulse(full_path)
                for tag in tags:
                    if tag not in index:
                        index[tag] = {"papers": [], "podcasts": [], "pulses": []}
                    index[tag]["pulses"].append(rel_path)
                    index[tag]["papers"].extend(papers)
                    index[tag]["podcasts"].extend(podcasts)

    # Deduplicate
    for tag_data in index.values():
        tag_data["papers"] = sorted(list(set(tag_data["papers"])))
        tag_data["podcasts"] = sorted(list(set(tag_data["podcasts"])))
        tag_data["pulses"] = sorted(list(set(tag_data["pulses"])))

    return index

def main():
    index = build_link_index()
    with open(OUTPUT_PATH, "w") as out:
        out.write("const linkIndex = ")
        json.dump(index, out, indent=2)
        out.write(";")

if __name__ == "__main__":
    main()
