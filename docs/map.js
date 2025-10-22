// Phi-Mesh Tag Map — full production build with gentle zoom refinement (2025-10-22)

(async () => {
  const data = window.PHI_DATA || window.GRAPH_DATA || window.DATA;
  if (!data || !data.nodes) {
    console.error("Phi-Mesh map: missing dataset");
    return;
  }

  const width = window.innerWidth;
  const height = window.innerHeight;

  // --- SVG setup and background --------------------------------------------
  const svg = d3
    .select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("id", "phi-map")
    .style("background", "radial-gradient(circle at 50% 50%, #0b0b0d 0%, #000 100%)");

  const defs = svg.append("defs");

  // Glow filter for active nodes
  const glow = defs
    .append("filter")
    .attr("id", "glow")
    .attr("x", "-50%")
    .attr("y", "-50%")
    .attr("width", "200%")
    .attr("height", "200%");
  glow
    .append("feGaussianBlur")
    .attr("stdDeviation", "3.5")
    .attr("result", "coloredBlur");
  const feMerge = glow.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");

  // Subtle gridlines background
  const gridPattern = defs
    .append("pattern")
    .attr("id", "grid")
    .attr("width", 50)
    .attr("height", 50)
    .attr("patternUnits", "userSpaceOnUse");
  gridPattern
    .append("path")
    .attr("d", "M 50 0 L 0 0 0 50")
    .attr("fill", "none")
    .attr("stroke", "#222")
    .attr("stroke-width", "0.5");
  svg.append("rect").attr("width", "100%").attr("height", "100%").attr("fill", "url(#grid)");

  const g = svg.append("g").attr("class", "main-layer");

  const zoom = d3
    .zoom()
    .scaleExtent([0.3, 5])
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
  svg.call(zoom);

  // --- Simulation setup -----------------------------------------------------
  const simulation = d3
    .forceSimulation(data.nodes)
    .force(
      "link",
      d3
        .forceLink(data.edges)
        .id((d) => d.id)
        .distance((d) => 60 + (d.weight || 1) * 10)
    )
    .force("charge", d3.forceManyBody().strength(-65))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(28));

  // --- Draw edges ----------------------------------------------------------
  const link = g
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(data.edges)
    .enter()
    .append("line")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.35)
    .attr("stroke-width", (d) => Math.sqrt(d.weight || 1));

  // --- Draw nodes ----------------------------------------------------------
  const node = g
    .append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("r", (d) => 6 + (d.centrality || 0) * 20)
    .attr("fill", (d) =>
      d.group
        ? d3.schemeCategory10[d.group % 10]
        : d.color || "rgba(0,180,255,0.75)"
    )
    .attr("stroke", "#111")
    .attr("stroke-width", 0.7)
    .style("filter", "url(#glow)")
    .on("mouseover", (event, d) => {
      tooltip
        .style("opacity", 1)
        .html(
          `<b>${d.id}</b><br/>degree ${d.degree}<br/>centrality ${(d.centrality || 0).toFixed(2)}`
        );
    })
    .on("mousemove", (event) => {
      tooltip
        .style("left", event.pageX + 8 + "px")
        .style("top", event.pageY + 8 + "px");
    })
    .on("mouseout", () => tooltip.style("opacity", 0))
    .on("click", (event, d) => {
      centerOnNode(d);
      showPulses(d);
    });

  // --- Draw labels ---------------------------------------------------------
  const label = g
    .append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(data.nodes)
    .enter()
    .append("text")
    .text((d) => d.id)
    .attr("font-size", "10px")
    .attr("fill", "#ccc")
    .attr("pointer-events", "none")
    .attr("text-anchor", "start");

  // --- Tooltip -------------------------------------------------------------
  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("background", "rgba(0,0,0,0.8)")
    .style("color", "#fff")
    .style("padding", "6px 8px")
    .style("border-radius", "4px")
    .style("font-size", "11px")
    .style("opacity", 0)
    .style("pointer-events", "none");

  // --- Pulse pane ----------------------------------------------------------
  const pulsePane = d3
    .select("body")
    .append("div")
    .attr("id", "pulse-pane")
    .style("position", "fixed")
    .style("right", "14px")
    .style("top", "14px")
    .style("width", "260px")
    .style("max-height", "70%")
    .style("overflow-y", "auto")
    .style("padding", "8px 10px")
    .style("background", "rgba(0,0,0,0.6)")
    .style("color", "#fff")
    .style("border-radius", "8px")
    .style("backdrop-filter", "blur(6px)")
    .style("display", "none");

  function showPulses(tag) {
    if (!tag.pulses || tag.pulses.length === 0) return;
    pulsePane.style("display", "block").html(
      `<h4>${tag.id}</h4><ul>${tag.pulses
        .map((p) => `<li>${p.title || p}</li>`)
        .join("")}</ul>`
    );
  }

  // Click outside to hide the pane
  svg.on("click", (event) => {
    if (event.target.tagName === "svg") pulsePane.style("display", "none");
  });

  // --- Simulation tick -----------------------------------------------------
  let tickCount = 0;
  simulation.on("tick", () => {
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

    if (++tickCount % 2 === 0) {
      label.attr("x", (d) => d.x + 8).attr("y", (d) => d.y + 3);
    }
  });

  // --- Search --------------------------------------------------------------
  const searchBox = d3.select("input[type='search']");
  if (searchBox.size()) {
    searchBox.on("input", (event) => {
      const query = event.target.value.trim().toLowerCase();
      const matches = data.nodes.filter((n) => n.id.toLowerCase().includes(query));

      node.attr("opacity", (d) => (!query ? 1 : matches.includes(d) ? 1 : 0.1));
      label.attr("opacity", (d) => (!query ? 1 : matches.includes(d) ? 1 : 0.1));
      link.attr("opacity", (d) =>
        !query
          ? 0.35
          : matches.includes(d.source) || matches.includes(d.target)
          ? 0.35
          : 0.05
      );

      if (matches.length > 0 && query.length > 1) {
        centerOnSelection(matches);
      }
    });

    // Keyboard shortcuts
    d3.select("body").on("keydown", (event) => {
      if (event.key === "Escape") {
        searchBox.node().value = "";
        node.attr("opacity", 1);
        label.attr("opacity", 1);
        link.attr("opacity", 0.35);
      }
      if (event.key === "Enter") {
        const q = searchBox.node().value.trim().toLowerCase();
        if (!q) return;
        const matches = data.nodes.filter((n) => n.id.toLowerCase().includes(q));
        if (matches.length > 0) centerOnSelection(matches);
      }
    });
  }

  // --- Gentle zoom functions -----------------------------------------------
  function centerOnSelection(selectedNodes) {
    const avgX = d3.mean(selectedNodes, (d) => d.x) || width / 2;
    const avgY = d3.mean(selectedNodes, (d) => d.y) || height / 2;
    const translate = [width / 2 - avgX * 0.8, height / 2 - avgY * 0.8];
    const scale = Math.min(1.4, 0.7 / Math.sqrt(selectedNodes.length));
    svg
      .transition()
      .duration(1200)
      .ease(d3.easeCubicOut)
      .call(zoom.transform, d3.zoomIdentity.translate(...translate).scale(scale));
  }

  function centerOnNode(d) {
    const translate = [width / 2 - d.x * 0.9, height / 2 - d.y * 0.9];
    svg
      .transition()
      .duration(1000)
      .ease(d3.easeCubicOut)
      .call(zoom.transform, d3.zoomIdentity.translate(...translate).scale(1.4));
  }

  // --- Resize --------------------------------------------------------------
  window.addEventListener("resize", () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    svg.attr("width", w).attr("height", h);
    simulation.force("center", d3.forceCenter(w / 2, h / 2));
  });

  console.log("Phi-Mesh Tag Map initialized — full edition with gentle zoom.");
})();
