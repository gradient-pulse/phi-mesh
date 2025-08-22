/* docs/map.js — renderer for Phi-Mesh Tag Map
   - No spiral satellites (right list only)
   - Left sidebar starts EMPTY (no hint line)
   - Safari-safe (no ?? mixed with ||)
   - Defensive DOM lookups for right panel IDs
*/
(function () {
  const DATA = (window.PHI_DATA && typeof window.PHI_DATA === "object")
    ? window.PHI_DATA
    : { nodes: [], links: [], tagDescriptions: {}, pulsesByTag: {} };

  // ---------- DOM ----------
  const svg = d3.select("#graph");
  const tooltip = d3.select("#tooltip"); // single declaration

  const leftPanel = document.getElementById("sidebar-content")
                   || document.querySelector("#sidebar-content, #left, aside .content")
                   || document.body;

  // Right side: try several common IDs/classes you’ve used
  const rightTitleEl = document.getElementById("pulse-title")
                    || document.querySelector("#pulse-title, #rightTitle, #pulses h3, #pulses .title");
  const rightListEl  = document.getElementById("pulse-list")
                    || document.querySelector("#pulse-list, #rightList, #pulses .list, #pulses ul");

  const searchInput = document.getElementById("search")
                    || document.querySelector("#search, input[type='search']");

  // Clear the left sidebar on load (removes that superfluous hint forever)
  if (leftPanel) leftPanel.innerHTML = "";

  // ---------- Helpers ----------
  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
      ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[c])
    );
  }
  function safeArray(x){ return Array.isArray(x) ? x : (x ? [x] : []); }

  // Node score without mixing ?? and ||
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const linksRaw = safeArray(DATA.links)
    .map(l => ({ source: idToNode.get(l.source) || l.source,
                 target: idToNode.get(l.target) || l.target }))
    .filter(l => l.source && l.target);

  const degree = new Map();
  linksRaw.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id) || 0) + 1);
    degree.set(l.target.id, (degree.get(l.target.id) || 0) + 1);
  });

  function nodeScore(d) {
    const c = d && d.centrality;
    if (typeof c === "number") return c;
    const deg = degree.get(d && d.id) || 1;
    return deg;
  }

  // Age color class (for pulse bullets in the right list if you add them)
  function ageClass(p){
    const a = p && p.ageDays;
    if (a == null) return "age-old";
    if (a <= 14)  return "age-very-new";
    if (a <= 45)  return "age-new";
    if (a <= 120) return "age-mid";
    if (a <= 270) return "age-old";
    return "age-very-old";
  }

  // ---------- SVG + Zoom ----------
  const vbWidth  = (svg.node() && svg.node().clientWidth)  || 1200;
  const vbHeight = (svg.node() && svg.node().clientHeight) || 800;
  svg.attr("viewBox", `0 0 ${vbWidth} ${vbHeight}`);

  const root = svg.append("g");
  const linkLayer = root.append("g").attr("class","links");
  const nodeLayer = root.append("g").attr("class","nodes");

  const zoom = d3.zoom().scaleExtent([0.35, 4]).on("zoom", ev => {
    root.attr("transform", ev.transform);
  });
  svg.call(zoom);

  // Background click clears focus (but keeps left sidebar as-is)
  svg.on("click", ev => {
    if (ev.target === svg.node()) {
      clearFocus();
      if (rightTitleEl) rightTitleEl.textContent = "Pulses";
      if (rightListEl)  rightListEl.innerHTML  = `<div style="opacity:.7">Click a tag to list its pulses.</div>`;
    }
  });

  // ---------- Visual tuning ----------
  // Slightly smaller nodes + looser layout (less dense)
  const minR = 5.5, maxR = 19;
  const ellipseAspect = 1.55;

  const scores = DATA.nodes.map(nodeScore);
  const sMin = d3.min(scores) ?? 1;
  const sMax = d3.max(scores) ?? 1;
  const rScale = d3.scaleSqrt().domain([sMin, sMax]).range([minR, maxR]);

  const sim = d3.forceSimulation(DATA.nodes)
    .force("link",
      d3.forceLink(linksRaw).id(d=>d.id).distance(92).strength(0.7)
    )
    .force("charge", d3.forceManyBody().strength(-220))
    .force("center", d3.forceCenter(vbWidth/2, vbHeight/2))
    .force("collision", d3.forceCollide().radius(d => rScale(nodeScore(d))*1.15));

  // ---------- Draw ----------
  const linkSel = linkLayer.selectAll("line")
    .data(linksRaw)
    .join("line")
      .attr("class","link")
      .attr("stroke","#b9c7dd")
      .attr("stroke-opacity", .22);

  const nodeSel = nodeLayer.selectAll("g.node")
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append("g").attr("class","node");

      g.append("ellipse")
        .attr("rx", d => rScale(nodeScore(d)) * ellipseAspect)
        .attr("ry", d => rScale(nodeScore(d)));

      g.append("text")
        .attr("x", d => rScale(nodeScore(d)) * ellipseAspect + 4)
        .attr("y", 4)
        .attr("font-size", 12)
        .attr("fill", "#d3e0f2")
        .text(d => d.id);

      g.on("mouseover", (ev,d) => showTagTooltip(ev, d.id))
       .on("mousemove", moveTooltip)
       .on("mouseout", hideTooltip)
       .on("click", (ev,d) => { ev.stopPropagation(); onTagClick(d.id); });

      return g;
    });

  sim.on("tick", () => {
    linkSel
      .attr("x1", d=>d.source.x).attr("y1", d=>d.source.y)
      .attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);

    nodeSel.attr("transform", d=>`translate(${d.x},${d.y})`);
  });

  // ---------- Tooltip ----------
  function showTagTooltip(evt, tag) {
    const n = idToNode.get(tag);
    const deg = degree.get(tag) || 0;
    const cent = (typeof n?.centrality === "number") ? n.centrality.toFixed(2) : String(deg);
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) || "—";

    tooltip.html(`
      <div style="font-weight:700; margin-bottom:4px">${esc(tag)}</div>
      <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${esc(cent)}</div>
      <div style="white-space:pre-wrap; opacity:.92">${esc(desc)}</div>
      <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to list pulses</div>
    `).style("display","block");
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad = 12;
    tooltip.style("left", (evt.clientX+pad)+"px").style("top", (evt.clientY+pad)+"px");
  }
  function hideTooltip(){ tooltip.style("display","none"); }

  // ---------- Focus / Dimming ----------
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed("dim", d => !keep.has(d.id));
    linkSel.classed("dim", d => !(keep.has(d.source.id) && keep.has(d.target.id)));

    // Highlight ONLY the clicked tag: we add a class; caller removes it beforehand
    nodeSel.classed("focusedTag", d => keep.has(d.id) && keep.size === (1 + neighborCount(d.id)));
  }
  function neighborCount(id){
    let c=0;
    linksRaw.forEach(l => { if (l.source.id===id || l.target.id===id) c++; });
    return c;
  }
  function clearFocus(){
    nodeSel.classed("dim", false).classed("focusedTag", false);
    linkSel.classed("dim", false);
  }

  // ---------- Right list rendering ----------
  function sortByDateDesc(a,b){
    // date formatted like '2025-08-12' or '2025-08-12T..'
    const ad = (a && a.date) ? a.date : "";
    const bd = (b && b.date) ? b.date : "";
    return (ad > bd) ? -1 : (ad < bd) ? 1 : 0;
  }

  function renderRightList(tagId){
    if (!rightListEl) return;

    // unique by id/title+date
    const raw = safeArray(DATA.pulsesByTag && DATA.pulsesByTag[tagId]);
    const seen = new Set();
    const dedup = [];
    for (const p of raw){
      const key = p.id || `${p.title || ""}|${p.date || ""}`;
      if (!seen.has(key)){ seen.add(key); dedup.push(p); }
    }
    dedup.sort(sortByDateDesc);

    // Build compact, single-line items (truncated)
    let html = "";
    for (const p of dedup){
      const title = p.title || p.id || "Pulse";
      const when  = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : "";
      html += `
        <div class="pulse-item" style="display:flex;align-items:center;gap:8px; margin:.18rem 0; cursor:pointer;">
          <span class="dot" style="width:8px;height:8px;border-radius:50%;display:inline-block;background:#ff8a70;"></span>
          <span class="ellipsis" title="${esc(title)}${p.date?` ${p.date}`:""}"
                data-id="${esc(p.id || "")}"
                data-title="${esc(title)}"
                data-date="${esc(p.date || "")}"
                style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%">
            ${esc(title)}${when}
          </span>
        </div>
      `;
    }
    rightListEl.innerHTML = html || `<div style="opacity:.7">No pulses recorded for this tag.</div>`;
    if (rightTitleEl) rightTitleEl.textContent = `Pulses for ${tagId}`;

    // Click to show left details
    rightListEl.querySelectorAll(".pulse-item .ellipsis").forEach(el => {
      el.addEventListener("click", () => {
        const pid   = el.getAttribute("data-id");
        const pdate = el.getAttribute("data-date");
        const ptitle= el.getAttribute("data-title");
        const match = dedup.find(p => (p.id && pid && p.id===pid) ||
                                       (p.title===ptitle && (p.date||"")===pdate));
        if (match) showPulseDetails(match);
      });
    });

    // keep list scrolled to top
    if (rightListEl.parentElement && typeof rightListEl.parentElement.scrollTop === "number"){
      rightListEl.parentElement.scrollTop = 0;
    }
  }

  function renderLinksBlock(label, items){
    if (!items || !items.length) return "";
    const norm = items.map(u => typeof u === "string"
      ? {title:u, url:u}
      : (u && u.url) ? u : {title:(u && u.title) || (u && u.url) || "", url:(u && u.url) || ""}
    );
    let html = `<div style="margin-top:.75rem"><strong>${label}</strong><ul style="padding-left:18px;margin:.3rem 0 0">`;
    for (const it of norm){
      const title = it.title || it.url || "";
      const href  = it.url   || it.title || "#";
      html += `<li style="margin:.15rem 0">
        <a class="ellipsis" href="${esc(href)}" target="_blank" rel="noopener"
           style="display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%">
          ${esc(title)}
        </a>
      </li>`;
    }
    html += `</ul></div>`;
    return html;
  }

  function showPulseDetails(p){
    if (!leftPanel) return;
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : "";
    let html = `<h2 style="margin:0 0 .5rem 0">${esc(p.title || p.id || "Pulse")}${when}</h2>`;
    if (p.summary){
      html += `<div style="white-space:pre-wrap;opacity:.95;margin:.25rem 0 1rem 0">${esc(p.summary)}</div>`;
    }
    html += renderLinksBlock("Papers",   p.papers);
    html += renderLinksBlock("Podcasts", p.podcasts);
    leftPanel.innerHTML = html;
  }

  // ---------- Tag click ----------
  function onTagClick(tagId){
    // highlight only the clicked tag; dim all others except neighbors
    nodeSel.classed("focusedTag", d => d.id === tagId);

    const keep = new Set([tagId]);
    linksRaw.forEach(l => {
      if (l.source.id === tagId) keep.add(l.target.id);
      if (l.target.id === tagId) keep.add(l.source.id);
    });
    setFocus(keep);

    // build right list
    renderRightList(tagId);
  }

  // ---------- Search (filter dims) ----------
  function applyFilter(q){
    const s = (q || "").trim().toLowerCase();
    if (!s){ clearFocus(); return; }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n => n.id));
    setFocus(keep);
  }
  if (searchInput){
    searchInput.addEventListener("input", e => applyFilter(e.target.value));
  }

  // ---------- Minimal CSS hooks (optional) ----------
  // If your CSS doesn’t define .dim or .focusedTag, these inline tweaks keep UX nice.
  const styleEl = document.createElement("style");
  styleEl.textContent = `
    .node.dim text { opacity:.18 }
    .node.dim ellipse { opacity:.22 }
    .link.dim { stroke-opacity:.08 }
    .node.focusedTag ellipse { fill:#ffb19a !important }
  `;
  document.head.appendChild(styleEl);

  // Initial right panel text (keeps left empty)
  if (rightTitleEl) rightTitleEl.textContent = "Pulses";
  if (rightListEl)  rightListEl.innerHTML  = `<div style="opacity:.7">Click a tag to list its pulses.</div>`;
})();
