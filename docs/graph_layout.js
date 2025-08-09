// graph_layout.js — panning, zoom, sidebar rendering, auto-zoom-to-fit, and robust link normalization

const graph = window.graph || { nodes: [], links: [] }; // Safe fallback

const sidebarWidth = 280;
const width = Math.max(640, window.innerWidth - sidebarWidth);
const height = Math.max(480, window.innerHeight);

// Build a label->id map so we can accept links by label or id
const idByLabel = new Map((graph.nodes || []).map(n => [n.label, n.id]));

// Normalize links to numeric ids if needed
const normalizedLinks = (graph.links || []).map(l => {
  const src = (typeof l.source === "number") ? l.source
            : (typeof l.source === "string") ? (idByLabel.get(l.source) ?? l.source)
            : l.source?.id ?? l.source;

  const tgt = (typeof l.target === "number") ? l.target
            : (typeof l.target === "string") ? (idByLabel.get(l.target) ?? l.target)
            : l.target?.id ?? l.target;

  return { source: src, target: tgt };
});

// Basic debug to confirm what we loaded
console.log(`Graph loaded: ${graph.nodes?.length || 0} nodes, ${normalizedLinks.length} links.`);

// Root SVG + zoom group
const zoom = d3.zoom()
  .scaleExtent([0.1, 6])
  .on("zoom", (event) => {
    svgGroup.attr("transform", event.transform);
  });

const svg = d3.select("#graph")
  .append("svg")
  .attr("width", width)
  .attr("height", height)
  .call(zoom);

const svgGroup = svg.append("g");

// Forces
const simulation = d3.forceSimulation()
  .force("link", d3.forceLink()
    .id(d => d.id)            // node ids are numeric
    .distance(40)
    .strength(0.35))
  .force("charge", d3.forceManyBody().strength(-80))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(18).strength(0.9))
  .force("x", d3.forceX(width / 2).strength(0.05))
  .force("y", d3.forceY(height / 2).strength(0.05));

// Links (darker so they’re clearly visible)
const link = svgGroup.append("g")
  .attr("stroke", "#666")
  .attr("stroke-opacity", 0.9)
  .selectAll("line")
  .data(normalizedLinks)
  .enter().append("line")
  .attr("stroke-width", 1.2);

// Nodes
const node = svgGroup.append("g")
  .selectAll("circle")
  .data(graph.nodes || [])
  .enter().append("circle")
  .attr("r", 10)
  .attr("fill", "#9ecae1")
  .attr("stroke", "#fff")
  .attr("stroke-width", 0.7)
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended))
  .on("click", (event, d) => renderSidebar(d.label));

// Labels
const labels = svgGroup.append("g")
  .selectAll("text")
  .data(graph.nodes || [])
  .enter().append("text")
  .text(d => d.label)
  .attr("text-anchor", "middle")
  .attr("dy", 20)
  .attr("font-size", "11px")
  .attr("fill", "#ddd")
  .attr("pointer-events", "none");

// Run simulation
simulation.nodes(graph.nodes).on("tick", ticked).on("end", zoomToFit);
simulation.force("link").links(normalizedLinks);

function ticked() {
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
    .attr("y", d => d.y);
}

// Drag handlers
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

// Auto-zoom to fit graph bounds
function zoomToFit() {
  if (!graph.nodes || graph.nodes.length === 0) return;

  const margin = 30;
  const minX = d3.min(graph.nodes, d => d.x);
  const maxX = d3.max(graph.nodes, d => d.x);
  const minY = d3.min(graph.nodes, d => d.y);
  const maxY = d3.max(graph.nodes, d => d.y);

  const boundsWidth = Math.max(1, maxX - minX);
  const boundsHeight = Math.max(1, maxY - minY);

  const scale = Math.min(
    (width - margin * 2) / boundsWidth,
    (height - margin * 2) / boundsHeight,
    3
  );

  const midX = (minX + maxX) / 2;
  const midY = (minY + maxY) / 2;

  const transform = d3.zoomIdentity
    .translate(width / 2, height / 2)
    .scale(scale)
    .translate(-midX, -midY);

  svg.transition().duration(600).call(zoom.transform, transform);
}
