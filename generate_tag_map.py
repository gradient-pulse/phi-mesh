
import yaml
import networkx as nx
import os
import re
from pathlib import Path

TAG_INDEX_FILE = "meta/tag_index.yml"
PULSE_DIR = "phi-mesh/pulse"
OUTPUT_HTML = "docs/generated/generated/tag_map.html"
DATA_JS = "docs/generated/generated/data.js"

def extract_links_from_pulses():
    tag_to_resources = {}
    for pulse_path in Path(PULSE_DIR).rglob("*.yml"):
        with open(pulse_path, "r") as f:
            try:
                data = yaml.safe_load(f)
                pulses = data.get("pulses", []) + data.get("acknowledgments", [])
                for pulse in pulses:
                    tags = pulse.get("tags", [])
                    link = pulse.get("file", "")
                    paper_links = pulse.get("papers", [])
                    podcast_links = pulse.get("podcasts", [])
                    for tag in tags:
                        if tag not in tag_to_resources:
                            tag_to_resources[tag] = {"pulses": [], "papers": [], "podcasts": []}
                        tag_to_resources[tag]["pulses"].append(link)
                        tag_to_resources[tag]["papers"].extend(paper_links)
                        tag_to_resources[tag]["podcasts"].extend(podcast_links)
            except Exception as e:
                print(f"Failed to parse {pulse_path}: {e}")
    return tag_to_resources

def parse_tag_index():
    with open(TAG_INDEX_FILE, "r") as f:
        return yaml.safe_load(f)

def build_graph(tag_index):
    G = nx.Graph()
    for tag, data in tag_index.items():
        G.add_node(tag)
        for related_tag in data.get("links", []):
            G.add_edge(tag, related_tag)
    return G

def export_data_js(G, tag_resources):
    nodes = [{"id": tag, "resources": tag_resources.get(tag, {})} for tag in G.nodes]
    links = [{"source": u, "target": v} for u, v in G.edges]
    js_data = f"const graphData = {{nodes: {nodes}, links: {links}}};"
    with open(DATA_JS, "w") as f:
        f.write(js_data)

def generate_html():
    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RGP Tag Map</title>
  <style>
    body {{ margin: 0; background: #111; color: white; font-family: sans-serif; overflow: hidden; }}
    .sidebar {{
      position: absolute;
      left: 0; top: 0; bottom: 0; width: 320px;
      background: rgba(30,30,30,0.8);
      overflow-y: auto; padding: 1em;
      border-right: 1px solid #333;
    }}
    svg {{ position: absolute; top: 0; left: 320px; right: 0; bottom: 0; }}
    a {{ color: white; text-decoration: underline; word-break: break-word; }}
    h2 {{ margin-top: 0; }}
  </style>
</head>
<body>
<div class="sidebar">
  <h2>RGP Tag Map</h2>
  <p><em>Coherence Tracking Across Fields—click a tag</em></p>
  <div id="details">Hover over a node to see connections</div>
</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="data.js"></script>
<script>
const width = window.innerWidth - 320, height = window.innerHeight;

const svg = d3.select("body").append("svg")
  .attr("width", width).attr("height", height);

const simulation = d3.forceSimulation(graphData.nodes)
  .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-250))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .on("tick", ticked);

const link = svg.append("g")
  .selectAll("line")
  .data(graphData.links)
  .enter().append("line")
  .attr("stroke", "#aaa");

const node = svg.append("g")
  .selectAll("circle")
  .data(graphData.nodes)
  .enter().append("circle")
  .attr("r", 8)
  .attr("fill", "#89CFF0")
  .on("click", showDetails)
  .call(drag(simulation));

const label = svg.append("g")
  .selectAll("text")
  .data(graphData.nodes)
  .enter().append("text")
  .text(d => d.id)
  .style("fill", "white")
  .style("font-size", "10px")
  .attr("text-anchor", "middle")
  .attr("dy", "1.2em");

function ticked() {
  link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
  node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  label
      .attr("x", d => d.x)
      .attr("y", d => d.y);
}

function drag(simulation) {
  return d3.drag()
      .on("start", event => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      })
      .on("drag", event => {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      })
      .on("end", event => {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      });
}

function showDetails(event, d) {
  const details = document.getElementById("details");
  const res = d.resources || {};
  details.innerHTML = `
    <strong>${d.id}</strong><br/>
    ${["pulses", "papers", "podcasts"].map(kind => {
      const list = (res[kind] || []).map(url => `<a href="${url}" target="_blank">${truncate(url)}</a>`).join("<br/>");
      return list ? `<h3>${kind.charAt(0).toUpperCase() + kind.slice(1)}</h3>` + list : "";
    }).join("")}
  `;
}

function truncate(str) {
  return str.length > 40 ? str.slice(0, 37) + "..." : str;
}
</script>
</body>
</html>
'''
    with open(OUTPUT_HTML, "w") as f:
        f.write(html_template)

def generate_tag_graph():
    tag_index = parse_tag_index()
    tag_resources = extract_links_from_pulses()
    G = build_graph(tag_index)
    nodes = [{"id": tag, "resources": tag_resources.get(tag, {})} for tag in G.nodes]
    links = [{"source": u, "target": v} for u, v in G.edges]
    metadata = {
        "node_count": len(nodes),
        "link_count": len(links)
    }
    return {
        "nodes": nodes,
        "links": links,
        "metadata": metadata
    }

def main():
    tag_index = parse_tag_index()
    tag_resources = extract_links_from_pulses()
    G = build_graph(tag_index)
    export_data_js(G, tag_resources)
    generate_html()

if __name__ == "__main__":
    main()
