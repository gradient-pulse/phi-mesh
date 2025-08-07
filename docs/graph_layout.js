// graph_layout.js — with Google Maps-style panning, zoom, and improved sidebar layout

const width = window.innerWidth - 280;
const height = window.innerHeight;

const zoom = d3.zoom()
  .scaleExtent([0.1, 5])
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
  .force("link", d3.forceLink().id(d => d.id).distance(80))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2));

fetch("graph_data.js")
  .then(response => response.text())
  .then(text => {
    const graph = eval(text); // Contains nodes and links

    const link = svgGroup.append("g")
      .selectAll("line")
      .data(graph.links)
      .enter().append("line")
      .attr("stroke", "#ccc")
      .attr("stroke-width", 1);

    const node = svgGroup.append("g")
      .selectAll("circle")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("r", 10)
      .attr("fill", "#9ecae1")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .on("click", clicked);

    const labels = svgGroup.append("g")
      .selectAll("text")
      .data(graph.nodes)
      .enter().append("text")
      .text(d => d.id)
      .attr("text-anchor", "middle")
      .attr("dy", 20)
      .attr("font-size", "11px")
      .attr("pointer-events", "none");

    simulation
      .nodes(graph.nodes)
      .on("tick", ticked);

    simulation.force("link")
      .links(graph.links);

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

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    function truncate(text, length = 25) {
      return text.length > length ? text.slice(0, length) + "..." : text;
    }

    function clicked(event, d) {
      const tag = d.id;
      const sidebar = document.getElementById("link-list");
      sidebar.innerHTML = "";

      const headerTag = document.createElement("div");
      headerTag.style.fontWeight = "bold";
      headerTag.style.fontSize = "18px";
      headerTag.style.marginBottom = "10px";
      headerTag.textContent = tag;
      sidebar.appendChild(headerTag);

      const data = linkIndex[tag];
      if (!data) {
        const noData = document.createElement("div");
        noData.textContent = "No linked content found.";
        sidebar.appendChild(noData);
        return;
      }

      function section(title, items) {
        if (items.length === 0) return;

        const header = document.createElement("div");
        header.style.fontWeight = "bold";
        header.style.fontSize = "15px";
        header.textContent = title;
        sidebar.appendChild(header);

        items.slice(0, 3).forEach(path => {
          const div = document.createElement("div");
          const a = document.createElement("a");
          a.href = path;
          a.target = "_blank";
          a.textContent = truncate(path.split("/").pop());
          a.title = path.split("/").pop();
          a.style.fontSize = "13px";
          div.appendChild(a);
          sidebar.appendChild(div);
        });
      }

      section("Papers", data.papers);
      section("Podcasts", data.podcasts);
      section("Pulses", data.pulses);
    }
  });
