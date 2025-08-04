import yaml
import json
from collections import defaultdict
import networkx as nx

TAG_INDEX_PATH = "meta/tag_index.yml"
DATA_JS_PATH = "docs/data.js"
TAG_MAP_HTML_PATH = "docs/tag_map.html"

def load_tag_index(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def generate_graph_data(tag_index):
    G = nx.Graph()

    # Reverse index: pulse → list of tags
    pulse_to_tags = defaultdict(list)
    for tag, pulses in tag_index.items():
        for pulse in pulses:
            pulse_to_tags[pulse].append(tag)

    # Add tags as nodes
    for tag in tag_index:
        G.add_node(tag)

    # Link all tags that co-occur in the same pulse
    for tags in pulse_to_tags.values():
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i+1:]:
                G.add_edge(tag1, tag2)

    # Compute centrality scores
    centrality = nx.degree_centrality(G)

    nodes = [{"id": tag, "centrality": round(centrality.get(tag, 0), 3)} for tag in G.nodes()]
    links = [{"source": src, "target": tgt} for src, tgt in G.edges()]

    return {"nodes": nodes, "links": links}

def write_data_js(graph_data, path):
    with open(path, "w") as f:
        f.write("const graphData = ")
        json.dump(graph_data, f, indent=2)
        f.write(";")

def inject_into_template(graph_data, output_path):
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RGP Tag Map</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body {{
      font-family: sans-serif;
      margin: 0;
    }}
    .node {{
      stroke: #000;
      stroke-width: 0.5px;
    }}
    .link {{
      stroke: #999;
      stroke-opacity: 0.6;
    }}
    .sidebar {{
      position: absolute;
      top: 0;
      left: 0;
      width: 250px;
      height: 100%;
      overflow-y: auto;
      background: #f0f0f0;
      padding: 10px;
      border-right: 1px solid #ccc;
    }}
    .content {{
      margin-left: 260px;
      padding: 10px;
    }}
    .tag-label {{
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="sidebar">
    <h2>RGP Tag Map</h2>
    <p>Coherence Tracking Across Fields—click a tag</p>
    <ul id="tagList"></ul>
  </div>
  <div class="content">
    <svg width="960" height="800"></svg>
  </div>
  <script>
{{
  const graphData = {json.dumps(graph_data, indent=2)};
}}

  const svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

  const simulation = d3.forceSimulation(graphData.nodes)
    .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(80))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const link = svg.append("g")
    .selectAll("line")
    .data(graphData.links)
    .join("line")
    .attr("class", "link");

  const node = svg.append("g")
    .selectAll("circle")
    .data(graphData.nodes)
    .join("circle")
    .attr("class", "node")
    .attr("r", 8)
    .attr("fill", "#aec7e8")
    .call(drag(simulation));

  const label = svg.append("g")
    .selectAll("text")
    .data(graphData.nodes)
    .join("text")
    .attr("class", "tag-label")
    .attr("text-anchor", "middle")
    .attr("dy", "1.5em")
    .text(d => d.id);

  simulation.on("tick", () => {{
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
  }});

  function drag(simulation) {{
    function dragstarted(event, d) {{
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }}

    function dragged(event, d) {{
      d.fx = event.x;
      d.fy = event.y;
    }}

    function dragended(event, d) {{
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }}

    return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }}
  </script>
</body>
</html>
"""
    with open(output_path, "w") as f:
        f.write(html_template)

def main():
    try:
        tag_index = load_tag_index(TAG_INDEX_PATH)
        graph_data = generate_graph_data(tag_index)
        write_data_js(graph_data, DATA_JS_PATH)
        inject_into_template(graph_data, TAG_MAP_HTML_PATH)
        print("✅ Tag map and data.js generated successfully.")
    except Exception as e:
        print(f"❌ Error generating tag map: {e}")

if __name__ == "__main__":
    main()
