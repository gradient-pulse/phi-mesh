// graph_layout.js — single-init, panning/zoom, sidebar rendering, debug logs

// ---- prevent double init ----
if (window.__RGP_GRAPH_INIT__) {
  console.warn("[RGP] graph_layout.js already initialized. Skipping.");
} else {
  window.__RGP_GRAPH_INIT__ = true;

  const graph = (window.graph && Array.isArray(window.graph.nodes) && Array.isArray(window.graph.links))
    ? window.graph
    : { nodes: [], links: [] };

  console.log(`[RGP] Graph loaded: ${graph.nodes.length} nodes, ${graph.links.length} links`);

  const width = window.innerWidth - 280; // sidebar is ~280px
  const height = window.innerHeight;

  const zoom = d3.zoom()
    .scaleExtent([0.2, 4])
    .on("zoom", (event) => {
      svgGroup.attr("transform", event.transform);
    });

  const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .call(zoom);

  const svgGroup = svg.append("g");

  const simulation = d3.forceSimulation()
    .force("link", d3.forceLink()
      // ids in our graph are numeric (0..N-1)
      .id(d => d.id)
      .distance(80)
      .strength(0.7)
    )
    .force("charge", d3.forceManyBody().strength(-280))
    .force("center", d3.forceCenter(width / 2, height / 2));

  // Draw links first (behind nodes)
  const link = svgGroup.append("g")
    .attr("stroke", "#bbb")
    .attr("stroke-opacity", 0.8)
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("stroke-width", 1);

  // Draw nodes
  const node = svgGroup.append("g")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
    .attr("r", 9)
    .attr("fill", "#9ecae1")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended))
    .on("click", (event, d) => renderSidebar(d.label));

  // Labels
  const labels = svgGroup.append("g")
    .selectAll("text")
    .data(graph.nodes)
    .enter().append("text")
    .text(d => d.label)
    .attr("text-anchor", "middle")
    .attr("dy", 18)
    .attr("font-size", "11px")
    .attr("pointer-events", "none")
    .attr("fill", "#666");

  simulation.nodes(graph.nodes).on("tick", ticked);
  simulation.force("link").links(graph.links);

  function ticked() {
    link
      .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    labels
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  }

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x; d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x; d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null; d.fy = null;
  }
}
