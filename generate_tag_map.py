import os
import json
import yaml
from meta.tag_index_utils import load_tag_index, get_resource_links

tag_index_path = "meta/tag_index.yml"
data_js_path = "docs/data.js"
tag_map_html_path = "docs/tag_map.html"


def generate_data_js(tag_index):
    nodes = []
    for tag in tag_index:
        resources = get_resource_links(tag)
        nodes.append({
            "id": tag,
            "resources": resources
        })
    return f"const data = {json.dumps({"nodes": nodes}, indent=2)};"


def generate_html():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RGP Tag Map</title>
  <style>
    body { font-family: sans-serif; }
    #sidebar { position: fixed; top: 0; left: 0; width: 250px; height: 100%; overflow-y: auto; background: #f4f4f4; padding: 1rem; border-right: 1px solid #ccc; }
    #graph { margin-left: 270px; padding: 1rem; }
    .node { cursor: pointer; margin: 0.5rem 0; }
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>RGP Tag Map</h2>
    <div id="info"></div>
  </div>
  <div id="graph">
    <svg width="1000" height="800"></svg>
  </div>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="data.js"></script>
  <script>
    const svg = d3.select("svg");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    const simulation = d3.forceSimulation(data.nodes)
      .force("charge", d3.forceManyBody().strength(-50))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(50))
      .on("tick", ticked);

    const node = svg.selectAll(".node")
      .data(data.nodes)
      .enter().append("text")
      .attr("class", "node")
      .attr("text-anchor", "middle")
      .text(d => d.id)
      .on("click", showInfo);

    function ticked() {
      node.attr("x", d => d.x).attr("y", d => d.y);
    }

    function showInfo(event, d) {
      const info = document.getElementById("info");
      info.innerHTML = `<h3>${d.id}</h3>` +
        ['papers', 'podcasts', 'pulses'].map(type => {
          const items = d.resources[type] || [];
          if (!items.length) return `<p><strong>${type}:</strong> None</p>`;
          return `<p><strong>${type}:</strong><br>` +
            items.map(link => `<a href="${link.url}" target="_blank">${link.title}</a>`).join("<br>") +
            `</p>`;
        }).join("");
    }
  </script>
</body>
</html>
'''


def main():
    tag_index = load_tag_index()
    data_js = generate_data_js(tag_index)
    html = generate_html()

    os.makedirs("docs", exist_ok=True)
    with open(data_js_path, "w") as f:
        f.write(data_js)
    with open(tag_map_html_path, "w") as f:
        f.write(html)
    print(f"Generated tag map: {tag_map_html_path}")


if __name__ == "__main__":
    main()
