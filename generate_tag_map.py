import os
import json
import networkx as nx
import yaml

# Paths
TAG_INDEX_PATH = "meta/tag_index.yml"
LINK_INDEX_PATH = "meta/link_index.yml"  # Currently unused but reserved
OUTPUT_DIR = "docs"
DATA_JS = os.path.join(OUTPUT_DIR, "data.js")
HTML_FILE = os.path.join(OUTPUT_DIR, "tag_map.html")

# Load YAML tag index
def load_yaml_file(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Construct graph from tag index
def build_graph(tag_index):
    G = nx.Graph()
    for tag, data in tag_index.items():
        G.add_node(tag)
        for linked_tag in data.get("links", []):
            if G.has_edge(tag, linked_tag):
                G[tag][linked_tag]["weight"] += 1
            else:
                G.add_edge(tag, linked_tag, weight=1)
    return G

# Extract papers, podcasts, pulses for each tag
def gather_resources(tag_index):
    tag_resources = {}
    for tag, data in tag_index.items():
        tag_resources[tag] = {
            "papers": list(set(p["title"] for p in data.get("papers", []))),
            "podcasts": list(set(p["title"] for p in data.get("podcasts", []))),
            "pulses": list(set(p["title"] for p in data.get("pulses", []))),
        }
    return tag_resources

# Output data.js file for tag map
def export_data_js(G, tag_resources):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    nodes = [{"id": tag, "resources": tag_resources.get(tag, {})} for tag in G.nodes]
    links = [
        {"source": u, "target": v, "weight": G[u][v]["weight"]}
        for u, v in G.edges()
    ]
    data = {"nodes": nodes, "links": links}

    with open(DATA_JS, "w") as f:
        f.write("const graphData = ")
        json.dump(data, f, indent=2)

# Copy full D3-based tag map viewer
def copy_template_html():
    html_content = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RGP Tag Map</title>
  <style>
    body { font-family: sans-serif; margin: 0; display: flex; }
    #sidebar { width: 300px; padding: 1em; background: #f8f8f8; overflow-y: auto; border-right: 1px solid #ddd; }
    #graph { flex: 1; }
    .link { stroke: #aaa; stroke-width: 1.5px; }
    .node circle { fill: #b3cde0; stroke: #333; stroke-width: 1.5px; }
    .node text { pointer-events: none; font-size: 12px; }
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>RGP Tag Map</h2>
    <p>Click a node to view details</p>
    <div id="details"></div>
  </div>
  <svg id="graph" width="960" height="800"></svg>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="./data.js"></script>
  <script>
    const svg = d3.select("#graph")
    const width = +svg.attr("width")
    const height = +svg.attr("height")

    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))

    const link = svg.append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(graphData.links)
      .join("line")
      .attr("stroke-width", d => Math.sqrt(d.weight))

    const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(graphData.nodes)
      .join("circle")
      .attr("r", 10)
      .attr("fill", "#89bdd3")
      .call(drag(simulation))
      .on("click", showDetails)

    const label = svg.append("g")
      .selectAll("text")
      .data(graphData.nodes)
      .join("text")
      .attr("dy", 3)
      .attr("x", 12)
      .text(d => d.id)

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)
      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
      label
        .attr("x", d => d.x)
        .attr("y", d => d.y)
    })

    function drag(simulation) {
      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      }
      function dragged(event, d) {
        d.fx = event.x
        d.fy = event.y
      }
      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0)
        d.fx = null
        d.fy = null
      }
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    }

    function showDetails(event, d) {
      const div = document.getElementById("details")
      div.innerHTML = `<h3>${d.id}</h3>`
      for (const [type, items] of Object.entries(d.resources)) {
        if (items.length > 0) {
          div.innerHTML += `<strong>${type}:</strong><ul>` + items.map(x => `<li>${x}</li>`).join("") + '</ul>'
        }
      }
    }
  </script>
</body>
</html>'''

    with open(HTML_FILE, "w") as f:
        f.write(html_content)

# Main entry
if __name__ == "__main__":
    tag_index = load_yaml_file(TAG_INDEX_PATH)
    G = build_graph(tag_index)
    tag_resources = gather_resources(tag_index)
    export_data_js(G, tag_resources)
    copy_template_html()
