import os
import yaml
import json
from collections import defaultdict

TAG_INDEX_PATH = "meta/tag_index.yml"
PULSE_DIR = "pulse/"
OUTPUT_HTML = "docs/tag_map.html"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RGP Tag Map</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; overflow: hidden; }
    h2 { font-size: 16px; margin: 0; padding: 0 0 4px; }
    #sidebar {
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 280px;
      background: #f9f9f9;
      border-right: 1px solid #ccc;
      padding: 10px;
      overflow-y: auto;
    }
    #graph {
      position: absolute;
      left: 280px;
      top: 0;
      right: 0;
      bottom: 0;
    }
    .link { stroke: #999; stroke-opacity: 0.6; }
    .node circle { fill: #add8e6; r: 6px; }
    .node text { font-size: 12px; fill: #000; pointer-events: none; }
    .section-title { font-weight: bold; margin-top: 10px; }
    .link-list { font-size: 13px; margin-left: 5px; }
  </style>
</head>
<body>
  <div id="sidebar">
    <h2>RGP Tag Map</h2>
    <div>Coherence Tracking Across Fields—click a tag</div>
    <div id="info"></div>
  </div>
  <svg id="graph"></svg>

  <script>
    const graph = __GRAPH_DATA__;
    const tagDetails = __TAG_DETAILS__;

    const svg = d3.select("svg");
    const width = window.innerWidth - 280;
    const height = window.innerHeight;
    svg.attr("width", width).attr("height", height);

    const simulation = d3.forceSimulation(graph.nodes)
        .force("link", d3.forceLink(graph.links).id(d => d.id).distance(60))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(graph.links)
      .join("line")
        .attr("stroke-width", 1);

    const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("g")
    .data(graph.nodes)
    .join("g")
      .call(drag(simulation));

    node.append("circle")
        .attr("r", 5)
        .attr("fill", "lightblue")
        .on("click", showInfo);

    node.append("text")
        .text(d => d.id)
        .attr("x", 8)
        .attr("y", "0.31em");

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

      node.attr("transform", d => `translate(${d.x},${d.y})`);
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

    function showInfo(event, d) {
      const details = tagDetails[d.id] || { pulses: [], papers: [], podcasts: [] };
      const info = document.getElementById("info");
      info.innerHTML = `<div class='section-title'>Tag: ${d.id}</div>`;

      for (const section of ["pulses", "papers", "podcasts"]) {
        if (details[section].length > 0) {
          info.innerHTML += `<div class='section-title'>${section.charAt(0).toUpperCase() + section.slice(1)}</div>`;
          info.innerHTML += `<ul class='link-list'>` +
            details[section].map(entry => `<li><a href="${entry.link}" target="_blank">${entry.title}</a></li>`).join("\n") +
            `</ul>`;
        }
      }
    }
  </script>
</body>
</html>
"""

def load_tag_index():
    with open(TAG_INDEX_PATH, 'r') as f:
        return yaml.safe_load(f)

def scan_pulses():
    tag_links = defaultdict(lambda: {"pulses": [], "papers": [], "podcasts": []})
    for fname in os.listdir(PULSE_DIR):
        if not fname.endswith(".yml"):
            continue
        with open(os.path.join(PULSE_DIR, fname), 'r') as f:
            doc = yaml.safe_load(f) or {}
        link_base = fname.replace(".yml", ".html")
        link = f"https://gradient-pulse.github.io/phi-mesh/pulse/{link_base}"
        title = doc.get("title", fname.replace(".yml", ""))

        for tag in doc.get("tags", []):
            tag_links[tag]["pulses"].append({"title": title, "link": link})

        for paper in doc.get("papers", []):
            for tag in doc.get("tags", []):
                if isinstance(paper, dict):
                    tag_links[tag]["papers"].append({
                        "title": paper.get("title", "paper"),
                        "link": paper.get("link", "#")
                    })
                elif isinstance(paper, str):
                    tag_links[tag]["papers"].append({
                        "title": "paper",
                        "link": paper
                    })

        for podcast in doc.get("podcasts", []):
            for tag in doc.get("tags", []):
                if isinstance(podcast, dict):
                    tag_links[tag]["podcasts"].append({
                        "title": podcast.get("title", "podcast"),
                        "link": podcast.get("link", "#")
                    })
                elif isinstance(podcast, str):
                    tag_links[tag]["podcasts"].append({
                        "title": "podcast",
                        "link": podcast
                    })
    return tag_links

def build_graph_data(tag_index):
    nodes = [{"id": tag} for tag in tag_index.keys()]
    links = []
    for src, entry in tag_index.items():
        if isinstance(entry, dict) and "links" in entry:
            for dst in entry["links"]:
                links.append({"source": src, "target": dst})
    return {"nodes": nodes, "links": links}

def write_html(graph_data, tag_details):
    with open(OUTPUT_HTML, 'w') as f:
        html = HTML_TEMPLATE.replace("__GRAPH_DATA__", json.dumps(graph_data))
        html = html.replace("__TAG_DETAILS__", json.dumps(tag_details))
        f.write(html)

def main():
    tag_index = load_tag_index()
    tag_details = scan_pulses()
    graph_data = build_graph_data(tag_index)
    write_html(graph_data, tag_details)

if __name__ == '__main__':
    main()
