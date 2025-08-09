// docs/graph_layout.js
// D3 v7 force layout with zoom, collision, and a race-safe init that waits for window.graph.

(function () {
  const SIDEBAR_W = 280;

  function warnNoLinks(graph) {
    if (!graph || !Array.isArray(graph.links) || graph.links.length === 0) {
      console.warn("⚠️ No links present in graph.links — check generation step or tag 'links' lists.");
    }
  }

  function init(graph) {
    warnNoLinks(graph);

    const width = window.innerWidth - SIDEBAR_W;
    const height = window.innerHeight;

    const container = d3.select("#graph");
    container.selectAll("*").remove(); // clean slate

    const svg = container.append("svg")
      .attr("width", width)
      .attr("height", height);

    const gRoot = svg.append("g");

    const zoom = d3.zoom()
      .scaleExtent([0.2, 3])
      .on("zoom", (event) => gRoot.attr("transform", event.transform));

    svg.call(zoom).on("dblclick.zoom", null);

    const links = gRoot.append("g")
      .attr("stroke", "#aaa")
      .attr("stroke-width", 1)
      .selectAll("line")
      .data(graph.links || [])
      .join("line");

    const node = gRoot.append("g")
      .selectAll("circle")
      .data(graph.nodes || [], d => d.id)
      .join("circle")
      .attr("r", 7)
      .attr("fill", "lightsteelblue")
      .attr("stroke", "#666")
      .attr("stroke-width", 1)
      .call(drag(simulation()));

    const labels = gRoot.append("g")
      .selectAll("text")
      .data(graph.nodes || [], d => d.id)
      .join("text")
      .text(d => d.id)
      .attr("font-size", 11)
      .attr("dominant-baseline", "middle")
      .attr("fill", "#333");

    // Sidebar hookup (expects window.LINK_INDEX and #link-list)
    node.on("click", (_, d) => updateSidebar(d.id));

    // Force setup (done after selections so we can reference them)
    const sim = d3.forceSimulation(graph.nodes || [])
      .force("link", d3.forceLink(graph.links || [])
        .id(d => d.id)
        .distance(65)
        .strength(0.25))
      .force("charge", d3.forceManyBody().strength(-140))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(18))
      .alpha(1)
      .alphaTarget(0.02)
      .restart();

    function simulation() { return sim; }

    sim.on("tick", () => {
      links
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      labels
        .attr("x", d => d.x + 10)
        .attr("y", d => d.y + 1);
    });

    // Resize handler keeps center and size in sync
    window.addEventListener("resize", () => {
      const w = window.innerWidth - SIDEBAR_W;
      const h = window.innerHeight;
      svg.attr("width", w).attr("height", h);
      sim.force("center", d3.forceCenter(w / 2, h / 2)).alpha(0.1).restart();
    });

    // Drag behavior
    function drag(sim) {
      function dragstarted(event, d) {
        if (!event.active) sim.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      }
      function dragged(event, d) {
        d.fx = event.x; d.fy = event.y;
      }
      function dragended(event, d) {
        if (!event.active) sim.alphaTarget(0);
        d.fx = null; d.fy = null;
      }
      return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
    }

    // Sidebar updater (minimal – relies on window.LINK_INDEX built by link_index.js)
    function updateSidebar(tag) {
      const ul = document.getElementById("link-list");
      if (!ul) return;
      ul.innerHTML = "";

      const bucket = (window.LINK_INDEX && window.LINK_INDEX[tag]) || {};
      const sections = [
        ["papers", "Papers"],
        ["podcasts", "Podcasts"],
        ["pulses", "Pulses"],
      ];

      const title = document.createElement("li");
      title.innerHTML = `<strong>${tag}</strong>`;
      ul.appendChild(title);

      for (const [key, label] of sections) {
        const list = Array.isArray(bucket[key]) ? bucket[key] : [];
        if (!list.length) continue;
        const header = document.createElement("li");
        header.innerHTML = `<strong>${label}</strong>`;
        ul.appendChild(header);
        for (const href of list) {
          const li = document.createElement("li");
          li.innerHTML = `<a href="${href}" target="_blank" rel="noopener noreferrer">${href.replace(/^https?:\/\//,'')}</a>`;
          ul.appendChild(li);
        }
      }
    }
  }

  // Race-safe boot: wait until window.graph exists (loader injects it)
  function waitForGraph(attempt = 0) {
    if (window.graph && Array.isArray(window.graph.nodes)) {
      init(window.graph);
      return;
    }
    if (attempt > 40) {
      console.error("graph_layout: timed out waiting for window.graph");
      return;
    }
    setTimeout(() => waitForGraph(attempt + 1), 50);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", waitForGraph, { once: true });
  } else {
    waitForGraph();
  }
})();
