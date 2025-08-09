// docs/graph_layout.js
(function () {
  // ----- Utilities -----
  function uniqBy(arr, keyFn) {
    const seen = new Set();
    const out = [];
    for (const x of arr) {
      const k = keyFn(x);
      if (!seen.has(k)) {
        seen.add(k);
        out.push(x);
      }
    }
    return out;
  }

  // Build edges from tagIndex if we have no links in window.graph.
  function buildLinksFromTagIndex(tagIndex) {
    if (!tagIndex) return [];
    const edges = [];
    const seen = new Set();
    for (const [tag, payload] of Object.entries(tagIndex)) {
      const nbrs = (payload && payload.links) || [];
      for (const nb of nbrs) {
        const a = String(tag);
        const b = String(nb);
        if (a === b) continue;
        const key = a < b ? `${a}::${b}` : `${b}::${a}`;
        if (!seen.has(key)) {
          seen.add(key);
          edges.push({ source: a, target: b, weight: 1 });
        }
      }
    }
    return edges;
  }

  // ----- Gather data from globals written by data.js / graph_data.js -----
  // window.graph: { nodes:[{id,...}], links:[{source,target,...}] }
  // tagIndex: from data.js (try a few common names)
  const tagIndex =
    window.tagIndex ||
    window.TAG_INDEX ||
    (window.DATA && window.DATA.tagIndex) ||
    null;

  const baseGraph = (window.graph && JSON.parse(JSON.stringify(window.graph))) || {
    nodes: [],
    links: [],
  };

  // If links are missing, fall back to building from tagIndex.
  if (!baseGraph.links || baseGraph.links.length === 0) {
    console.warn("No links present in graph.links — rebuilding from tagIndex.");
    baseGraph.links = buildLinksFromTagIndex(tagIndex);
  }

  // Ensure every node that appears in an edge exists in nodes[]
  const ids = new Set(baseGraph.nodes.map((n) => String(n.id)));
  for (const e of baseGraph.links) {
    const s = String(e.source);
    const t = String(e.target);
    if (!ids.has(s)) {
      baseGraph.nodes.push({ id: s });
      ids.add(s);
    }
    if (!ids.has(t)) {
      baseGraph.nodes.push({ id: t });
      ids.add(t);
    }
  }

  // De-duplicate nodes by id (defensive)
  baseGraph.nodes = uniqBy(baseGraph.nodes, (n) => String(n.id));

  // ----- D3 rendering -----
  const container = document.getElementById("graph");
  const w = container.clientWidth;
  const h = container.clientHeight;

  const svg = d3
    .select("#graph")
    .append("svg")
    .attr("width", w)
    .attr("height", h);

  const gRoot = svg.append("g");

  // Zoom / pan
  const zoom = d3
    .zoom()
    .scaleExtent([0.25, 4])
    .on("zoom", (event) => {
      gRoot.attr("transform", event.transform);
    });
  svg.call(zoom);

  // Link + node + label layers
  const link = gRoot
    .append("g")
    .attr("stroke", "#aaa")
    .attr("stroke-opacity", 0.7)
    .selectAll("line")
    .data(baseGraph.links)
    .join("line")
    .attr("stroke-width", (d) => Math.max(1, (d.weight || 1) * 0.6));

  const node = gRoot
    .append("g")
    .selectAll("circle")
    .data(baseGraph.nodes, (d) => d.id)
    .join("circle")
    .attr("r", 6)
    .attr("fill", "#8ec0df")
    .attr("stroke", "#5b9ec7")
    .attr("stroke-width", 1)
    .call(
      d3
        .drag()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    )
    .on("click", (_, d) => {
      // sidebar_display.js expects window.showTag(tagId)
      if (typeof window.showTag === "function") {
        window.showTag(String(d.id));
      }
    });

  const label = gRoot
    .append("g")
    .selectAll("text")
    .data(baseGraph.nodes, (d) => d.id)
    .join("text")
    .text((d) => d.id)
    .attr("font-size", 11)
    .attr("fill", "#555")
    .attr("pointer-events", "none");

  // Forces — spaced a bit wider than before
  const simulation = d3
    .forceSimulation(baseGraph.nodes)
    .force(
      "link",
      d3
        .forceLink(baseGraph.links)
        .id((d) => d.id)
        .distance((d) => 85 + (d.weight ? 6 * (1 / d.weight) : 0))
        .strength(0.4)
    )
    .force("charge", d3.forceManyBody().strength(-220))
    .force("collision", d3.forceCollide().radius(18))
    .force("center", d3.forceCenter(w / 2, h / 2));

  simulation.on("tick", () => {
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

    // offset labels slightly to reduce overlap with nodes
    label.attr("x", (d) => d.x + 8).attr("y", (d) => d.y + 3);
  });

  // Resize handler
  window.addEventListener("resize", () => {
    const nw = container.clientWidth;
    const nh = container.clientHeight;
    svg.attr("width", nw).attr("height", nh);
    simulation.force("center", d3.forceCenter(nw / 2, nh / 2)).alpha(0.15).restart();
  });
})();
