document.addEventListener("DOMContentLoaded", function () {
  const sidebarWidth = 280;
  const margin = 50;
  const width = window.innerWidth - sidebarWidth - margin;
  const height = window.innerHeight - margin;

  const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const simulation = d3.forceSimulation(graphData.nodes)
    .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-250))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX(width / 2).strength(0.1))
    .force("y", d3.forceY(height / 2).strength(0.1));

  const link = svg.append("g")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 1.5)
    .selectAll("line")
    .data(graphData.links)
    .join("line");

  const node = svg.append("g")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(graphData.nodes)
    .join("circle")
    .attr("r", 8)
    .attr("fill", "steelblue")
    .call(drag(simulation));

  const label = svg.append("g")
    .selectAll("text")
    .data(graphData.nodes)
    .join("text")
    .text(d => d.id)
    .attr("font-size", 12)
    .attr("dx", 12)
    .attr("dy", "0.35em");

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
});
