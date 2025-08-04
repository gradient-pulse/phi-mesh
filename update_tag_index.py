import os
import yaml
from collections import defaultdict
from tag_index_utils import save_tag_index

PULSE_DIR = "phi-mesh/pulse"
TAG_INDEX_PATH = "phi-mesh/meta/tag_index.yml"

def load_yaml_file(filepath):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def main():
    tag_index = defaultdict(lambda: {
        "pulses": [],
        "papers": [],
        "podcasts": []
    })

    for filename in os.listdir(PULSE_DIR):
        if filename.endswith(".yml"):
            filepath = os.path.join(PULSE_DIR, filename)
            data = load_yaml_file(filepath)

            tags = data.get("tags", [])
            papers = data.get("papers", [])
            podcasts = data.get("podcasts", [])

            for tag in tags:
                entry = tag_index[tag]
                if filename not in entry["pulses"]:
                    entry["pulses"].append(filename)
                for paper in papers:
                    if paper not in entry["papers"]:
                        entry["papers"].append(paper)
                for podcast in podcasts:
                    if podcast not in entry["podcasts"]:
                        entry["podcasts"].append(podcast)

    save_tag_index(dict(tag_index), TAG_INDEX_PATH)

if __name__ == "__main__":
    main()
