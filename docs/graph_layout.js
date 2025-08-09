/* RGP Tag Map – force layout + interactions
   expects:
     - window.graph = { nodes:[{id,label,centrality?...}], links:[{source,target,weight?}] }
     - sidebar_display.js exposing: window.updateSidebar(tagLabel)
*/

(function () {
  const container = document.getElementById("graph");
  if (!container) {
    console.warn("graph_layout: #graph container not found");
    return;
  }

  // ---- SVG & sizing ----
  const svg = d3.select("#graph").append("svg")
    .attr("width", container.clientWidth)
    .attr("height", container.clientHeight);

  const gRoot = svg.append("g");              // zoom root
  const gLinks = gRoot.append("g").attr("class", "links");
  const gNodes = gRoot.append("g").attr("class", "nodes");
  const gLabels = gRoot.append("g").attr("class", "labels");

  // basic styles (inline so no CSS dependency)
  const NODE_R = 7;

  // ---- data ----
  const graph = window.graph || { nodes: [], links: [] };
  if (!graph.nodes) graph.nodes = [];
  if (!graph.links) graph.links = [];

  // warn if no links (helps debug)
  if (!graph.links.length) {
    console.warn("No links present in graph.links — check generation step or tag 'links' lists.");
  }

  // ---- forces ----
  const width = +svg.attr("width");
  const height = +svg.attr("height");

  const linkDistance = d => 90 + (d.weight ? Math.min(60, d.weight * 10) : 0);

  const simulation = d3.forceSimulation(graph.nodes)
    .force("link", d3.forceLink(graph.links)
      .id(d => d.id)
      .distance(linkDistance)
      .strength(0.6))
    .force("charge", d3.forceManyBody().strength(-220))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(() => NODE_R + 10).iterations(2));

  // ---- draw links ----
  const link = gLinks.selectAll("line")
    .data(graph.links)
    .join("line")
    .attr("stroke", "#aaa")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", d => 1 + Math.min(2, (d.weight || 0) * 0.5));

  // ---- draw nodes ----
  const node = gNodes.selectAll("circle")
    .data(graph.nodes, d => d.id)
    .join("circle")
      .attr("r", NODE_R)
      .attr("fill", "#87c1e9")
      .attr("stroke", "white")
      .attr("stroke-width", 1.2)
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .on("click", (_, d) => {
        highlight(d);
        if (window.updateSidebar) window.updateSidebar(d.label);
      })
      .on("mouseover", function (_, d) {
        d3.select(this).attr("fill", "#5aa9da");
      })
      .on("mouseout", function (_, d) {
        if (!d.__hl) d3.select(this).attr("fill", "#87c1e9");
      });

  // ---- labels ----
  const label = gLabels.selectAll("text")
    .data(graph.nodes, d => d.id)
    .join("text")
      .attr("font-size", 11)
      .attr("fill", "#666")
      .attr("pointer-events", "none")
      .text(d => d.label);

  // ---- zoom/pan ----
  const zoom = d3.zoom()
    .scaleExtent([0.2, 4])
    .on("zoom", (event) => gRoot.attr("transform", event.transform));

  svg.call(zoom);

  // ---- tick ----
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    label
      .attr("x", d => d.x + NODE_R + 4)
      .attr("y", d => d.y + 4);
  });

  // ---- resize ----
  window.addEventListener("resize", () => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    svg.attr("width", w).attr("height", h);
    simulation.force("center", d3.forceCenter(w / 2, h / 2)).alpha(0.08).restart();
    setTimeout(fitOnce, 300);
  });

  // ---- helpers ----
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.2).restart();
    d.fx = d.x; d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x; d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null; d.fy = null;
  }

  function highlight(center) {
    // reset
    graph.nodes.forEach(n => { n.__hl = false; });
    node.attr("fill", "#87c1e9").attr("opacity", 0.9);
    label.attr("opacity", 0.9);
    link.attr("stroke", "#aaa").attr("stroke-opacity", 0.45);

    // neighbors
    const nbr = new Set([center.id]);
    graph.links.forEach(l => {
      if (l.source.id === center.id) nbr.add(l.target.id);
      if (l.target.id === center.id) nbr.add(l.source.id);
    });

    node.filter(d => !nbr.has(d.id)).attr("opacity", 0.2);
    label.filter(d => !nbr.has(d.id)).attr("opacity", 0.15);
    link.filter(d => (d.source.id !== center.id && d.target.id !== center.id))
        .attr("stroke-opacity", 0.12);

    node.filter(d => nbr.has(d.id)).each(function (d) { d.__hl = true; })
        .attr("fill", d => d.id === center.id ? "#2f79b7" : "#5aa9da");
  }

  // initial fit to view
  function fitOnce() {
    if (!graph.nodes.length) return;
    const xs = graph.nodes.map(n => n.x || 0);
    const ys = graph.nodes.map(n => n.y || 0);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const w = Math.max(1, maxX - minX), h = Math.max(1, maxY - minY);

    const pad = 40;
    const vw = container.clientWidth - pad * 2;
    const vh = container.clientHeight - pad * 2;
    const scale = Math.max(0.2, Math.min(4, 0.95 * Math.min(vw / w, vh / h)));

    const tx = (container.clientWidth  - scale * (minX + maxX)) / 2;
    const ty = (container.clientHeight - scale * (minY + maxY)) / 2;

    svg.transition().duration(600)
       .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
  }

  // give the sim a moment to settle, then fit
  setTimeout(fitOnce, 800);
})();
