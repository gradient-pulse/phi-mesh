
import yaml
import json
import os

TAG_INDEX_PATH = "meta/tag_index.yml"
OUTPUT_PATH = "docs/data.js"

def load_tag_index():
    with open(TAG_INDEX_PATH, "r") as f:
        return yaml.safe_load(f)

def write_tag_map_data(tag_index):
    with open(OUTPUT_PATH, "w") as f:
        f.write("const tagData = ")
        json.dump(tag_index, f, indent=2)
        f.write(";")

if __name__ == "__main__":
    tag_index = load_tag_index()
    write_tag_map_data(tag_index)
