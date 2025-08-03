import os
import yaml
import json

TAG_INDEX_PATH = "meta/tag_index.yml"
PULSES_DIR = "phi-mesh/pulse"
DOCS_DIR = "docs"
DATA_JS_PATH = os.path.join(DOCS_DIR, "data.js")
HTML_PATH = os.path.join(DOCS_DIR, "tag_map.html")

def load_tag_index():
    with open(TAG_INDEX_PATH, "r") as f:
        return yaml.safe_load(f)

def collect_resources():
    resources = {}
    for root, _, files in os.walk(PULSES_DIR):
        for file in files:
            if file.endswith(".yml"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    try:
                        pulse_data = yaml.safe_load(f)
                        tags = pulse_data.get("tags", [])
                        for tag in tags:
                            tag = str(tag)
                            if tag not in resources:
                                resources[tag] = {"papers": [], "podcasts": [], "pulses": []}
                            if "papers" in pulse_data:
                                resources[tag]["papers"].extend(pulse_data["papers"])
                            if "podcasts" in pulse_data:
                                resources[tag]["podcasts"].extend(pulse_data["podcasts"])
                            resources[tag]["pulses"].append(file.replace(".yml", ""))
                    except yaml.YAMLError as e:
                        print(f"Error reading {path}: {e}")
    return resources

def write_data_js(tag_data):
    nodes = [{"id": tag, "resources": tag_data[tag]} for tag in sorted(tag_data)]
    js_content = "const data = " + json.dumps({"nodes": nodes}, indent=2) + ";"
    with open(DATA_JS_PATH, "w") as f:
        f.write(js_content)

def write_html():
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>RGP Tag Map</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="data.js"></script>
</head>
<body>
  <h1>RGP Tag Map</h1>
  <div id="graph">Graph will load here.</div>
  <script>
    console.log(data);  // Placeholder: real D3 code would go here.
  </script>
</body>
</html>
"""
    with open(HTML_PATH, "w") as f:
        f.write(html_content)

def main():
    tag_data = load_tag_index()
    resource_data = collect_resources()
    for tag in tag_data:
        if tag not in resource_data:
            resource_data[tag] = {"papers": [], "podcasts": [], "pulses": []}
    write_data_js(resource_data)
    write_html()
    print(f"✓ Tag map generated at: {HTML_PATH}")

if __name__ == "__main__":
    main()
