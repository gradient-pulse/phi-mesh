import os
import yaml
import json

TAG_INDEX_PATH = "meta/tag_index.yml"
PULSE_DIR = "pulse/"
GRAPH_DATA_JS_PATH = "docs/graph_data.js"

def load_tag_index():
    with open(TAG_INDEX_PATH, "r") as f:
        return yaml.safe_load(f)

def collect_resources_for_tag(tag):
    pulses = []
    papers = set()
    podcasts = set()

    for filename in os.listdir(PULSE_DIR):
        if filename.endswith(".yml"):
            with open(os.path.join(PULSE_DIR, filename), "r") as f:
                try:
                    pulse_data = yaml.safe_load(f)
                    if not isinstance(pulse_data, dict):
                        continue
                    if tag in pulse_data.get("tags", []):
                        title = pulse_data.get("title", filename)
                        pulses.append({
                            "title": title,
                            "path": f"pulse/{filename}"
                        })

                        papers.update(pulse_data.get("papers", [])[:3])
                        podcasts.update(pulse_data.get("podcasts", [])[:3])
                except Exception as e:
                    print(f"⚠️ Error in {filename}: {e}")

    return {
        "pulses": pulses[:3],
        "papers": list(papers)[:3],
        "podcasts": list(podcasts)[:3]
    }

def build_graph_data(tag_index):
    nodes = []
    links = []

    for tag, metadata in tag_index.items():
        if isinstance(metadata, dict):
            links_list = metadata.get("links", [])
        else:
            links_list = metadata

        resource_data = collect_resources_for_tag(tag)

        nodes.append({
            "id": tag,
            "pulses": resource_data["pulses"],
            "papers": resource_data["papers"],
            "podcasts": resource_data["podcasts"]
        })

        for linked_tag in links_list:
            links.append({
                "source": tag,
                "target": linked_tag
            })

    return {"nodes": nodes, "links": links}

if __name__ == "__main__":
    print("🔁 Running generate_graph_data.py")
    tag_index = load_tag_index()
    graph_data = build_graph_data(tag_index)

    with open(GRAPH_DATA_JS_PATH, "w") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";")
