import yaml

def load_tag_index(path="meta/tag_index.yml"):
    """
    Load and return the tag index from the given YAML file path.
    Raises FileNotFoundError or yaml.YAMLError if something goes wrong.
    """
    with open(path, "r") as f:
        tag_index = yaml.safe_load(f)

    if not isinstance(tag_index, dict):
        raise ValueError("Expected top-level structure in tag_index.yml to be a dictionary.")

    for tag, entry in tag_index.items():
        if "links" in entry and not isinstance(entry["links"], list):
            raise ValueError(f"Tag '{tag}' has a malformed 'links' field. Expected a list.")
        if "summary" in entry and not isinstance(entry["summary"], str):
            raise ValueError(f"Tag '{tag}' has a malformed 'summary' field. Expected a string.")

    return tag_index
