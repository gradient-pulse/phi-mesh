// graph_layout.js — with panning, zoom, sidebar tweaks, and safe graph loading

const width = window.innerWidth - 280; // subtract sidebar
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
    const graph = new Function(text.replace(/^const graph\s*=\s*/, '').trim() + '; return graph;')();

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
      sidebar.innerHTML = "";

      const data = linkIndex[tag];
      if (!data) {
        const noData = document.createElement("li");
        noData.textContent = "No linked content found.";
        sidebar.appendChild(noData);
        return;
      }

      const headerTag = document.createElement("li");
      headerTag.innerHTML = `<strong>${tag}</strong>`;
      sidebar.appendChild(headerTag);

      const addLinks = (type, title) => {
        if (data[type]?.length > 0) {
          const header = document.createElement("li");
          header.innerHTML = `<strong>${title}</strong>`;
          sidebar.appendChild(header);
          data[type].slice(0, 3).forEach(path => {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = path;
            a.target = "_blank";
            const display = path.split("/").pop().slice(0, 25);
            a.textContent = display.length === 25 ? display + "..." : display;
            li.appendChild(a);
            sidebar.appendChild(li);
          });
        }
      };

      addLinks("papers", "Papers");
      addLinks("podcasts", "Podcasts");
      addLinks("pulses", "Pulses");
    }
  });
