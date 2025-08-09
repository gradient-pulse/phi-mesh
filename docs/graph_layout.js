// graph_layout.js — safe load, with panning/zoom, collision, and sidebar rendering

(function initWhenReady() {
  function ready() {
    return window.graph && Array.isArray(window.graph.nodes) && Array.isArray(window.graph.links);
  }
  if (!ready()) {
    // Try again after the current task, then after DOMContentLoaded
    document.addEventListener("DOMContentLoaded", () => {
      if (!ready()) setTimeout(init, 0); else init();
    });
    // Also a short fallback in case scripts race
    setTimeout(() => { if (ready()) init(); }, 30);
  } else {
    init();
  }
})();

function init() {
  const graph = window.graph || { nodes: [], links: [] };

  const width = window.innerWidth - 280; // Subtract sidebar width
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

  const simulation = d3.forceSimulation(graph.nodes)
    .force("link", d3.forceLink(graph.links)
      .id(d => d.id)
      .distance(60)
      .strength(0.6))
    .force("charge", d3.forceManyBody().strength(-180))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(18));

  // Draw links
  const link = svgGroup.append("g")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("stroke-width", 1.2);

  // Draw nodes
  const node = svgGroup.append("g")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
    .attr("r", 8)
    .attr("fill", "#9ecae1")
    .call(d3.drag()
      .on("start", (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      })
      .on("drag", (event, d) => {
        d.fx = event.x; d.fy = event.y;
      })
      .on("end", (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
      }))
    .on("click", (event, d) => renderSidebar(d.label));

  // Draw labels
  const labels = svgGroup.append("g")
    .selectAll("text")
    .data(graph.nodes)
    .enter().append("text")
    .text(d => d.label)
    .attr("text-anchor", "middle")
    .attr("dy", 18)
    .attr("font-size", "11px")
    .attr("fill", "#666")
    .attr("pointer-events", "none");

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    labels
      .attr("x", d => d.x)
      .attr("y", d => d.y + 1);
  });

  // Simple resize handler
  window.addEventListener("resize", () => {
    const w = window.innerWidth - 280;
    const h = window.innerHeight;
    svg.attr("width", w).attr("height", h);
    simulation.force("center", d3.forceCenter(w / 2, h / 2)).alpha(0.1).restart();
  });

  // Optional visibility check
  if (!graph.links || graph.links.length === 0) {
    console.warn("No links present in graph.links – check generate_graph_data output or tag 'links' lists.");
  }
}
