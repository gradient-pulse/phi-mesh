// graph_layout.js — D3 v7 force layout with zoom, pan, truncation, modal-ready

const width = window.innerWidth - 280; // Sidebar width
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
    const graph = new Function('return ' + text)(); // safer than eval

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

    function clicked(event, d) {
      const tag = d.id;
      const sidebar = document.getElementById("link-list");
      sidebar.innerHTML = ""; // clear previous entries

      const data = linkIndex[tag];
      if (!data) {
        const li = document.createElement("li");
        li.textContent = "No linked content found.";
        sidebar.appendChild(li);
        return;
      }

      // Show tag name first
      const title = document.createElement("li");
      title.innerHTML = `<strong style="font-size: 18px;">${tag}</strong>`;
      sidebar.appendChild(title);

      // Helper to add section
      function addSection(titleText, items, type) {
        if (items.length === 0) return;
        const header = document.createElement("li");
        header.innerHTML = `<strong>${titleText}</strong>`;
        header.style.marginTop = "12px";
        sidebar.appendChild(header);

        items.slice(0, 3).forEach(path => {
          const li = document.createElement("li");
          const a = document.createElement("a");
          a.href = path;
          a.target = "_blank";

          // Shorten long names
          let label = path.split("/").pop();
          if (label.length > 25) label = label.slice(0, 25) + "...";

          a.textContent = label;

          // Optional: show modal for pulses
          if (type === "pulse") {
            a.addEventListener("click", (e) => {
              e.preventDefault();
              showModal(path);
            });
          }

          li.appendChild(a);
          sidebar.appendChild(li);
        });
      }

      addSection("Papers", data.papers, "paper");
      addSection("Podcasts", data.podcasts, "podcast");
      addSection("Pulses", data.pulses, "pulse");
    }

    function showModal(path) {
      alert(`Pulse preview requested for:\n${path}`);
      // In future: fetch(path).then(...).display()
    }
  });
