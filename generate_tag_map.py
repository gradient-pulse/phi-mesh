import yaml
import networkx as nx
from pyvis.network import Network
import os
from tag_index_utils import build_graph_from_tag_index
from link_index_utils import add_links_to_graph

TAG_INDEX_PATH = "meta/tag_index.yml"
LINK_INDEX_PATH = "meta/link_index.yml"
OUTPUT_PATH = "docs/tag_map.html"


def generate_tag_map():
    # Load tag index
    with open(TAG_INDEX_PATH, 'r') as f:
        tag_index = yaml.safe_load(f)

    # Load link index
    with open(LINK_INDEX_PATH, 'r') as f:
        link_index = yaml.safe_load(f)

    # Build graph
    G = build_graph_from_tag_index(tag_index)
    add_links_to_graph(G, link_index)

    # Create PyVis network
    net = Network(height="800px", width="100%", bgcolor="#000000", font_color="#00ffff")
    net.barnes_hut(gravity=-5000, spring_length=180, central_gravity=0.2)

    # Add nodes and edges
    for node in G.nodes():
        label = str(node)
        net.add_node(
            node,
            label=label,
            title=label,
            shape="text",
            color="#00ffff",
            font={"size": 16, "color": "#00ffff"},
        )

    for source, target in G.edges():
        net.add_edge(source, target, color="#888888")

    # Add header and sidebar to HTML
    html_path = OUTPUT_PATH
    net.save_graph(html_path)

    # Inject header and sidebar
    with open(html_path, 'r') as f:
        html = f.read()

    # Insert header before </head>
    header_html = """
    <style>
      #header {
        font-size: 28px;
        font-weight: bold;
        padding: 16px;
        color: #00ffff;
        font-family: sans-serif;
        text-align: center;
        background-color: #000000;
      }
      #side-panel {
        position: fixed;
        right: 0;
        top: 60px;
        width: 280px;
        height: 90%;
        background-color: #111111;
        color: #00ffff;
        overflow-y: auto;
        padding: 12px;
        font-family: sans-serif;
        display: none;
        border-left: 1px solid #333333;
      }
    </style>
    <div id='header'>Phi-Mesh Tag Map</div>
    <div id='side-panel'></div>
    <script>
      function showTagInfo(tag) {
        const panel = document.getElementById("side-panel");
        panel.style.display = 'block';
        panel.innerHTML = '<h3>' + tag + '</h3>' +
                          '<p>Links and details coming soon...</p>';
      }
      document.querySelectorAll(".node").forEach(el => {
        el.onclick = () => showTagInfo(el.innerText);
      });
    </script>
    """
    html = html.replace("</head>", f"{header_html}\n</head>")

    # Save final
    with open(html_path, 'w') as f:
        f.write(html)

if __name__ == '__main__':
    generate_tag_map()
