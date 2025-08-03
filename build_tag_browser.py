
import yaml
from pathlib import Path
from generate_tag_map import generate_tag_graph

def build_tag_browser():
    # Generate the tag graph and save HTML + data.js
    print("Building tag map...")
    generate_tag_graph()
    print("Tag map generated.")

if __name__ == "__main__":
    build_tag_browser()
