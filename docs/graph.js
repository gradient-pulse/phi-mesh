// docs/graph.js
// Core D3 visualization logic for Phi-Mesh Tag Map

function renderTagMap(data) {
  const width = window.innerWidth - 300; // leave space for sidebar
  const height = window.innerHeight;

  const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-350))
    .force("center", d3.forceCenter(width / 2, height / 2));

  // draw links
  const link = svg.append("g")
    .attr("stroke", "#888")
    .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(data.links)
    .enter().append("line")
    .attr("stroke-width", 1.2);

  // draw nodes (tags)
  const node = svg.append("g")
    .selectAll("circle")
    .data(data.nodes)
    .enter().append("circle")
    .attr("r", 6)
    .attr("fill", "lightblue")
    .call(drag(simulation));

  // tag labels
  const label = svg.append("g")
    .selectAll("text")
    .data(data.nodes)
    .enter().append("text")
    .text(d => d.id)
    .attr("font-size", 10)
    .attr("dx", 10)
    .attr("dy", ".35em")
    .style("pointer-events", "none");

  // tooltips from tag_descriptions
  node.append("title")
    .text(d => d.description || "No description available");

  // click → show details in sidebar
  node.on("click", (event, d) => {
    showSidebarDetails(d);
  });

  simulation.on("tick", () => {
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
  });
}

// drag helpers
function drag(simulation) {
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
  return d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);
}

// sidebar handler (stub – we extend later with pulses, papers, podcasts)
function showSidebarDetails(d) {
  const sidebar = document.getElementById("sidebar-content");
  sidebar.innerHTML = `
    <h2>${d.id}</h2>
    <p>${d.description || "No description available"}</p>
    <h3>Pulses</h3>
    <ul>${(d.pulses || []).map(p => `<li>${p}</li>`).join("")}</ul>
  `;
}
