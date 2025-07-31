
import os
import json
from meta.tag_index_utils import get_all_tags_and_links

def generate_tag_map_html(output_file="docs/tag_map.html"):
    tags_data = get_all_tags_and_links()

    # Separate tag nodes and edges
    tag_nodes = [{"id": tag, "label": tag, "shape": "dot", "font": {"size": 16}} for tag in tags_data]
    tag_edges = []
    for source, links in tags_data.items():
        for link in links.get("tag_links", []):
            tag_edges.append({"from": source, "to": link, "arrows": "to", "color": "#ccc"})
        for paper in links.get("papers", []):
            tag_nodes.append({"id": f"📄 {paper}", "label": f"📄 {paper}", "shape": "box", "color": "#c0ffc0", "font": {"size": 14}})
            tag_edges.append({"from": source, "to": f"📄 {paper}", "arrows": "to", "color": "#9ccc9c"})
        for podcast in links.get("podcasts", []):
            tag_nodes.append({"id": f"🎧 {podcast}", "label": f"🎧 {podcast}", "shape": "ellipse", "color": "#cce0ff", "font": {"size": 14}})
            tag_edges.append({"from": source, "to": f"🎧 {podcast}", "arrows": "to", "color": "#99bbee"})

    html_content = f"""
<!doctype html>
<html>
<head>
  <title>Phi-Mesh Tag Map</title>
  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.css" rel="stylesheet" type="text/css" />
  <style type="text/css">
    #network {{
      width: 100%;
      height: 92vh;
      background-color: #111;
      border: 1px solid lightgray;
    }}
  </style>
</head>
<body>
  <h2 style="text-align:center;color:white;">Phi-Mesh Interactive Tag Map</h2>
  <div id="network"></div>
  <script type="text/javascript">
    var nodes = new vis.DataSet({json.dumps(tag_nodes)});
    var edges = new vis.DataSet({json.dumps(tag_edges)});
    var container = document.getElementById('network');
    var data = {{ nodes: nodes, edges: edges }};
    var options = {{
      nodes: {{
        color: '#ffffff',
        font: {{ color: '#ffffff' }},
        borderWidth: 2
      }},
      edges: {{
        color: {{ color: '#888' }}
      }},
      physics: {{
        stabilization: true
      }},
      layout: {{
        improvedLayout: true
      }}
    }};
    var network = new vis.Network(container, data, options);
  </script>
</body>
</html>
    """

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_tag_map_html()
