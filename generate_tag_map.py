# generate_tag_map.py

import os
import json
import networkx as nx
from meta.tag_index_utils import load_tag_index

# Load tag index
tag_index = load_tag_index()

# Create graph
G = nx.Graph()
for tag, metadata in tag_index.items():
    G.add_node(tag)
    for linked_tag in metadata.get("links", []):
        if G.has_node(linked_tag):
            G.add_edge(tag, linked_tag)

# Assign centrality
centrality = nx.degree_centrality(G)

nodes = []
links = []
for node in G.nodes():
    nodes.append({
        "id": node,
        "centrality": round(centrality.get(node, 0), 3)
    })
for source, target in G.edges():
    links.append({"source": source, "target": target})

# Ensure output directory exists
output_dir = os.path.join("docs")
os.makedirs(output_dir, exist_ok=True)

# Write data.js
with open(os.path.join(output_dir, "data.js"), "w") as f:
    json_data = json.dumps({"nodes": nodes, "links": links}, indent=2)
    f.write(f"const data = {json_data};")

# Write tag_map.html
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RGP Tag Map</title>
  <style>
    body { font-family: sans-serif; }
    #graph { width: 100vw; height: 90vh; }
  </style>
</head>
<body>
  <h2>RGP Tag Map</h2>
  <div id="graph">Graph will load here.</div>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="data.js"></script>
  <script>
    const width = window.innerWidth;
    const height = window.innerHeight * 0.9;
    const svg = d3.select("#graph").append("svg")
      .attr("width", width)
      .attr("height", height);

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(60))
      .force("charge", d3.forceManyBody().strength(-100))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.selectAll("line")
      .data(data.links)
      .enter().append("line")
      .style("stroke", "#aaa");

    const node = svg.selectAll("circle")
      .data(data.nodes)
      .enter().append("circle")
      .attr("r", 5)
      .style("fill", "#3399ff")
      .call(drag(simulation));

    const label = svg.selectAll("text")
      .data(data.nodes)
      .enter().append("text")
      .text(d => d.id)
      .attr("font-size", "10px")
      .attr("dx", 6)
      .attr("dy", 2);

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

      node.attr("cx", d => d.x)
          .attr("cy", d => d.y);

      label.attr("x", d => d.x)
           .attr("y", d => d.y);
    });

    function drag(simulation) {
      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }
      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }
  </script>
</body>
</html>'''

with open(os.path.join(output_dir, "tag_map.html"), "w") as f:
    f.write(html_content)
