/* docs/graph.js
 * Expects window.PHI_DATA:
 *  - nodes: [{id, degree?, centrality?}]
 *  - links: [{source, target}]
 *  - tagDescriptions: { [tag]: "..." } or { tags: { [tag]: "..." } }
 *  - pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts?, tags? }] }
 *
 * DOM:
 *  - <svg id="graph">
 *  - optional: #tag-search (input)
 *  - optional: #details (div) — if present, pulse click will render here
 *
 * Requires D3 v7.
 */
(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // ------------- DOM -----------------
  const svg = d3.select("#graph");
  if (svg.empty()) return;

  const detailsEl = document.getElementById("details");
  const searchInput = document.getElementById("tag-search");

  // Tooltip
  let tipEl = document.getElementById("phi-tip");
  if (!tipEl) {
    tipEl = document.createElement("div");
    tipEl.id = "phi-tip";
    tipEl.style.position = "fixed";
    tipEl.style.zIndex = "20";
    tipEl.style.pointerEvents = "none";
    tipEl.style.display = "none";
    tipEl.style.background = "#10141d";
    tipEl.style.border = "1px solid #2a3344";
    tipEl.style.borderRadius = "10px";
    tipEl.style.padding = "8px 10px";
    tipEl.style.color = "#e6edf6";
    tipEl.style.fontSize = "13px";
    tipEl.style.boxShadow = "0 8px 32px rgba(0,0,0,.45)";
    document.body.appendChild(tipEl);
  }

  // ------------- Helpers -------------
  const esc = (s) =>
    String(s || "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  function getTagDescription(tag) {
    const td = DATA.tagDescriptions || {};
    if (typeof td[tag] === "string") return td[tag];
    if (td.tags && typeof td.tags[tag] === "string") return td.tags[tag];
    return "";
  }

  function ageClass(ageDays) {
    if (ageDays == null) return "age-old";
    if (ageDays <= 14) return "age-very-new";
    if (ageDays <= 45) return "age-new";
    if (ageDays <= 120) return "age-mid";
    if (ageDays <= 270) return "age-old";
    return "age-very-old";
  }

  function showTip(html, x, y) {
    tipEl.innerHTML = html;
    tipEl.style.left = `${x + 12}px`;
    tipEl.style.top = `${y + 12}px`;
    tipEl.style.display = "block";
  }
  function moveTip(x, y) {
    tipEl.style.left = `${x + 12}px`;
    tipEl.style.top = `${y + 12}px`;
  }
  function hideTip() {
    tipEl.style.display = "none";
  }

  function showPulseDetails(p) {
    if (!detailsEl) return;
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : "";
    let html = `<h2 style="margin:.1rem 0 .5rem 0">${esc(p.title || p.id || "Pulse")}${when}</h2>`;
    if (p.summary) {
      html += `<div style="white-space:pre-wrap;margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;
    }
    const papers = Array.isArray(p.papers) ? p.papers : [];
    const pods = Array.isArray(p.podcasts) ? p.podcasts : [];

    if (papers.length) {
      html += `<div><strong>Papers</strong><ul>`;
      for (const it of papers) {
        if (typeof it === "string") {
          html += `<li><a href="${it}" target="_blank" rel="noopener">${esc(it)}</a></li>`;
        } else if (it && (it.url || it.doi)) {
          const url = it.url || (it.doi ? `https://doi.org/${it.doi}` : "");
          const label = it.title ? it.title : url;
          if (url) html += `<li><a href="${url}" target="_blank" rel="noopener">${esc(label)}</a></li>`;
        }
      }
      html += `</ul></div>`;
    }
    if (pods.length) {
      html += `<div style="margin-top:8px"><strong>Podcasts</strong><ul>`;
      for (const it of pods) {
        const url = typeof it === "string" ? it : it?.url;
        if (url) html += `<li><a href="${url}" target="_blank" rel="noopener">${esc(url)}</a></li>`;
      }
      html += `</ul></div>`;
    }
    detailsEl.innerHTML = html;
  }

  // ------------- Layout / layers -------------
  const width = svg.node().clientWidth || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr("viewBox", `0 0 ${width} ${height}`);

  const root = svg.append("g");
  const linkLayer = root.append("g").attr("class", "links");
  const nodeLayer = root.append("g").attr("class", "nodes");
  const satLayer = root.append("g").attr("class", "satellites");

  svg.call(
    d3
      .zoom()
      .scaleExtent([0.25, 4])
      .on("zoom", (evt) => root.attr("transform", evt.transform))
  );

  // map nodes by id
  const idToNode = new Map(DATA.nodes.map((n) => [n.id, n]));
  const links = DATA.links
    .map((l) => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target,
    }))
    .filter((l) => l.source && l.target);

  // force sim
  const sim = d3
    .forceSimulation(DATA.nodes)
    .force("link", d3.forceLink(links).id((d) => d.id).distance(90).strength(0.25))
    .force("charge", d3.forceManyBody().strength(-420))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius((d) => 6 + Math.sqrt((d.centrality || 0) * 900) + 8));

  // edges (make sure they’re visible even if CSS is missing)
  const linkSel = linkLayer
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("class", "link")
    .attr("stroke", "rgba(200,215,235,0.35)")
    .attr("stroke-width", 1.2);

  // nodes as ellipses + label
  const nodes = DATA.nodes;
  const rx = (d) => 6 + Math.sqrt((d.centrality || 0) * 900);
  const ry = (d) => 4 + Math.sqrt((d.centrality || 0) * 450);

  const nodeSel = nodeLayer
    .selectAll("g.node")
    .data(nodes, (d) => d.id)
    .join((enter) => {
      const g = enter.append("g").attr("class", "node").style("cursor", "pointer");

      g.append("ellipse")
        .attr("rx", rx)
        .attr("ry", ry)
        .attr("fill", "#2cc4ff")
        .attr("stroke", "#022433")
        .attr("stroke-width", 1.2)
        .style("filter", "drop-shadow(0 0 1px rgba(0,0,0,.3))");

      g.append("text")
        .attr("y", (d) => ry(d) + 12)
        .attr("text-anchor", "middle")
        .attr("fill", "#fff")
        .attr("font-size", 11)
        .style("pointer-events", "none")
        .text((d) => d.id);

      // tooltip
      g.on("mouseover", (event, d) => {
        const desc = getTagDescription(d.id);
        const deg = d.degree ?? d.deg ?? 0;
        const cen = Number(d.centrality || d.cent || 0).toFixed(2);
        const body = desc ? `<div style="opacity:.9;margin-top:4px">${esc(desc)}</div>` : `<div style="opacity:.7;margin-top:4px">—</div>`;
        const html = `
          <div style="font-weight:700;margin-bottom:2px">${esc(d.id)}</div>
          <div style="opacity:.85">degree ${deg} · centrality ${cen}</div>
          ${body}
          <div style="margin-top:6px;opacity:.9"><em>Click to reveal pulse satellites</em></div>
        `;
        showTip(html, event.clientX, event.clientY);
      })
       .on("mousemove", (event) => moveTip(event.clientX, event.clientY))
       .on("mouseout", hideTip)
       .on("click", (_evt, d) => revealSatellites(d.id));

      return g;
    });

  sim.on("tick", () => {
    linkSel
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    nodeSel.attr("transform", (d) => `translate(${d.x},${d.y})`);

    // keep satellites coordinated with host
    satLayer.selectAll("g.sat").attr("transform", (d) => {
      const host = d.host;
      const a = d._angle || 0;
      const r = d._radius || 100;
      return `translate(${host.x + r * Math.cos(a)},${host.y + r * Math.sin(a)})`;
    });
  });

  // ------------- Satellites -------------
  const RING_R_MIN = 100; // ring radius
  function revealSatellites(tagId) {
    hideTip();
    // clear previous
    satLayer.selectAll("*").remove();

    const host = idToNode.get(tagId);
    if (!host) return;

    const pulses = Array.isArray(DATA.pulsesByTag?.[tagId]) ? DATA.pulsesByTag[tagId] : [];
    if (!pulses.length) return;

    // sort by age (newer first -> warmer inside)
    const sorted = [...pulses].sort((a, b) => (a.ageDays ?? 99999) - (b.ageDays ?? 99999));

    const n = sorted.length;
    const TWO_PI = Math.PI * 2;
    const radius = RING_R_MIN;

    const sat = satLayer
      .selectAll("g.sat")
      .data(
        sorted.map((p, i) => ({
          ...p,
          host,
          _angle: (i / n) * TWO_PI,
          _radius: radius,
        })),
        (d) => d.id || d.title || `${tagId}:${d.date || i}`
      )
      .join((enter) => {
        const g = enter.append("g").attr("class", "sat").style("cursor", "pointer");

        g.append("circle")
          .attr("r", 5)
          .attr("class", (d) => ageClass(d.ageDays))
          // visible even if CSS missing:
          .attr("fill", (d) => {
            const ac = ageClass(d.ageDays);
            return ({
              "age-very-new": "#ff6b6b",
              "age-new": "#ff9e66",
              "age-mid": "#ffc94d",
              "age-old": "#8ecbff",
              "age-very-old": "#6aa4ff",
            }[ac] || "#8ecbff");
          })
          .attr("stroke", "#10131a")
          .attr("stroke-width", 1.25);

        g.append("title").text((d) => `${d.title || d.id || "pulse"}${d.date ? ` — ${d.date}` : ""}`);

        // click: show pulse in sidebar (if present)
        g.on("click", (_e, d) => showPulseDetails(d));

        return g;
      });

    // small nudge to settle
    sim.alpha(0.35).restart();
  }

  // ------------- Search -------------
  if (searchInput) {
    const normalize = (s) =>
      (s || "").toString().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

    function runSearch() {
      const q = normalize(searchInput.value);
      if (!q) {
        nodeSel.classed("dim", false).attr("opacity", 1);
        linkSel.attr("opacity", 0.35);
        return;
      }
      const matched = new Set(nodes.filter((n) => normalize(n.id).includes(q)).map((n) => n.id));
      nodeSel.classed("dim", (d) => !matched.has(d.id)).attr("opacity", (d) => (matched.has(d.id) ? 1 : 0.15));
      linkSel.attr("opacity", (l) => (matched.has(l.source.id) && matched.has(l.target.id) ? 0.35 : 0.06));
    }

    let t = null;
    searchInput.addEventListener("input", () => {
      if (t) clearTimeout(t);
      t = setTimeout(runSearch, 80);
    });
  }
})();
