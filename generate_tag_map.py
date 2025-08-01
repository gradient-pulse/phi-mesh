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
    net = Network(height="100vh", width="100%", bgcolor="#000000", font_color="#ffffff")
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=120)

    # Add nodes and edges
    for node in G.nodes():
        label = str(node)
        net.add_node(
            node,
            label=label,
            title=label,
            shape="dot",
            color="#33ccff",  # Light blue
            size=12,
            font={"size": 14, "color": "#ffffff"},
        )

    for source, target in G.edges():
        net.add_edge(source, target, color="rgba(200,200,200,0.25)")

    # Save basic PyVis output
    html_path = OUTPUT_PATH
    net.save_graph(html_path)

    # Inject header and sidebar code
    with open(html_path, 'r') as f:
        html = f.read()

    injected = """
    <style>
      body { margin: 0; background-color: black; color: white; }
      #mynetwork { border: none !important; }
      #header {
        font-size: 24px;
        font-weight: bold;
        padding: 12px;
        color: #33ccff;
        font-family: sans-serif;
        text-align: center;
        background-color: black;
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
        panel.innerHTML = '<h3>' + tag + '</h3><p>Links and metadata coming soon...</p>';
      }

      // Wait for PyVis to render then hook events
      window.addEventListener('load', function () {
        const nodes = document.querySelectorAll('div.node');
        nodes.forEach(el => {
          el.addEventListener('click', () => showTagInfo(el.innerText));
        });
      });
    </script>
    """

    html = html.replace("</head>", injected + "\n</head>")

    # Save final HTML
    with open(html_path, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    generate_tag_map()
