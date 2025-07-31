
import yaml
from collections import defaultdict
import os

TAG_INDEX_PATH = 'meta/tag_index.yml'

def load_tag_index(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def canonicalize_tags(tag_index):
    canonical_map = defaultdict(set)
    for canonical, group in tag_index.get('canonical_tags', {}).items():
        for alias in group:
            canonical_map[canonical].add(alias)
    return canonical_map

def main():
    if not os.path.exists(TAG_INDEX_PATH):
        print(f"{TAG_INDEX_PATH} not found.")
        return
    tag_index = load_tag_index(TAG_INDEX_PATH)
    canonical_map = canonicalize_tags(tag_index)
    for k, v in canonical_map.items():
        print(f"{k}: {sorted(v)}")

if __name__ == "__main__":
    main()
