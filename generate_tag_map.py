import os
import yaml
import json
from collections import defaultdict

DATA_JS_PATH = "docs/data.js"
GRAPH_JS_PATH = "docs/graph.js"
TAG_INDEX_PATH = "meta/tag_index.yml"
PULSE_DIR = "pulse"


def load_tag_index():
    with open(TAG_INDEX_PATH, 'r') as f:
        return yaml.safe_load(f)


def collect_data():
    tag_to_pulses = defaultdict(list)
    tag_to_papers = defaultdict(list)
    tag_to_podcasts = defaultdict(list)

    for fname in os.listdir(PULSE_DIR):
        if not fname.endswith(".yml"):
            continue

        with open(os.path.join(PULSE_DIR, fname), 'r') as f:
            doc = yaml.safe_load(f)

        tags = doc.get("tags", [])
        title = doc.get("title", fname.replace(".yml", ""))
        link = f"https://gradient-pulse.github.io/phi-mesh/pulse/{fname.replace('.yml', '.html')}"

        for tag in tags:
            tag_to_pulses[tag].append({"title": title, "link": link})

        for paper in doc.get("papers", []):
            for tag in tags:
                if isinstance(paper, dict):
                    tag_to_papers[tag].append({"title": paper.get("title", "paper"), "link": paper.get("link", "#")})

        for podcast in doc.get("podcasts", []):
            for tag in tags:
                if isinstance(podcast, dict):
                    tag_to_podcasts[tag].append({"title": podcast.get("title", "podcast"), "link": podcast.get("link", "#")})

    return tag_to_pulses, tag_to_papers, tag_to_podcasts


def build_graph_data(tag_index):
    nodes = sorted([{"id": tag} for tag in tag_index])
    links = []
    if isinstance(tag_index, dict):
        for src, linked in tag_index.items():
            if isinstance(linked, list):
                for dst in linked:
                    links.append({"source": src, "target": dst})
    return {"nodes": nodes, "links": links}


def generate_sidebar_data(tag_to_pulses, tag_to_papers, tag_to_podcasts):
    sidebar = {}
    all_tags = set(tag_to_pulses) | set(tag_to_papers) | set(tag_to_podcasts)
    for tag in sorted(all_tags):
        sidebar[tag] = {
            "pulses": tag_to_pulses.get(tag, []),
            "papers": tag_to_papers.get(tag, []),
            "podcasts": tag_to_podcasts.get(tag, [])
        }
    return sidebar


def write_data_js(graph_data, sidebar_data):
    with open(DATA_JS_PATH, 'w') as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";\n\n")
        f.write("const sidebarData = ")
        json.dump(sidebar_data, f, indent=2)
        f.write(";")


def copy_graph_js():
    graph_js_code = '''
// Updated graph.js (Phase 4)
const svg = d3.select("svg");
const width = window.innerWidth - 280;
const height = window.innerHeight;
svg.attr("width", width).attr("height", height);

const simulation = d3.forceSimulation(graphData.nodes)
  .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(60))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
  .attr("stroke", "#999")
  .attr("stroke-opacity", 0.6)
.selectAll("line")
.data(graphData.links)
.join("line")
  .attr("stroke-width", 1);

const node = svg.append("g")
  .attr("stroke", "#fff")
  .attr("stroke-width", 1.5)
.selectAll("g")
.data(graphData.nodes)
.join("g")
  .call(drag(simulation));

node.append("circle")
    .attr("r", 6)
    .attr("fill", "#a8c4e6")
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
  return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
}

function showInfo(event, d) {
  const tag = d.id;
  const info = document.getElementById("info");
  const details = sidebarData[tag] || { pulses: [], papers: [], podcasts: [] };
  info.innerHTML = `<div class='section-title'>Tag: ${tag}</div>`;

  for (const section of ["pulses", "papers", "podcasts"]) {
    const items = details[section];
    if (items.length > 0) {
      info.innerHTML += `<div class='section-title'>${section.charAt(0).toUpperCase() + section.slice(1)}</div>`;
      info.innerHTML += `<ul class='link-list'>` +
        items.map(entry => `<li style='margin-left:12px'><a href="${entry.link}" target="_blank">${entry.title}</a></li>`).join("\n") +
        `</ul>`;
    }
  }
}
'''
    with open(GRAPH_JS_PATH, 'w') as f:
        f.write(graph_js_code)


def main():
    tag_index = load_tag_index()
    pulses, papers, podcasts = collect_data()
    graph_data = build_graph_data(tag_index)
    sidebar_data = generate_sidebar_data(pulses, papers, podcasts)
    write_data_js(graph_data, sidebar_data)
    copy_graph_js()


if __name__ == '__main__':
    main()
