(function initWhenReady(){
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init(){
    const DATA = (window.PHI_DATA && typeof window.PHI_DATA === "object")
      ? window.PHI_DATA : { nodes: [], links: [], pulsesByTag: {}, tagDescriptions: {} };

    // --- DOM lookups ---
    const svg = d3.select("#graph");
    if (!svg.node()) return; // safety

    const leftBox = document.getElementById("sidebar-content");
    const rightTitle = document.getElementById("right-title");
    const rightList = document.getElementById("right-list");
    const searchInput = document.getElementById("search");
    const tooltip = d3.select("#tooltip");

    // --- sizing (robust) ---
    const w = svg.node().clientWidth || 1200;
    const h = svg.node().clientHeight || 800;
    svg.attr("viewBox", `0 0 ${w} ${h}`);

    // --- helpers ---
    const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
    const safeArr = v => Array.isArray(v) ? v : [];

    // Build link objects with node refs
    const links = safeArr(DATA.links)
      .map(l => ({
        source: idToNode.get(l.source) || l.source,
        target: idToNode.get(l.target) || l.target
      }))
      .filter(l => l.source && l.target);

    // Degree map (fallback metric)
    const degree = new Map();
    links.forEach(l => {
      degree.set(l.source.id, (degree.get(l.source.id) || 0) + 1);
      degree.set(l.target.id, (degree.get(l.target.id) || 0) + 1);
    });

    // Node sizing — smaller overall
    const minR = 5, maxR = 18, ellipseAspect = 1.55;
    const centralities = DATA.nodes.map(n => (typeof n.centrality === 'number' ? n.centrality : (degree.get(n.id) || 0)));
    const cMin = d3.min(centralities) ?? 0, cMax = d3.max(centralities) ?? 1;
    const rScale = d3.scaleSqrt().domain([cMin || 0.0001, cMax || 1]).range([minR, maxR]);

    // Safari-safe node score (no ?? mixed with ||)
    function nodeScore(d){
      const c = d.centrality;
      return (typeof c === "number") ? c : ((degree.get(d.id) || 1));
    }

    // Truncate (default 40 chars)
    function trunc(txt, n=40){ txt = String(txt||""); return (txt.length>n)?(txt.slice(0,n)+"…"):txt; }

    // Age coloring (used if you later add dots beside pulses)
    function ageClass(days){
      if (days==null) return "age-mid";
      if (days<=14) return "age-very-new";
      if (days<=45) return "age-new";
      if (days<=120) return "age-mid";
      return "age-old";
    }

    // --- layers & zoom ---
    const root = svg.append("g");
    const linkLayer = root.append("g").attr("class","links");
    const nodeLayer = root.append("g").attr("class","nodes");

    const zoom = d3.zoom().scaleExtent([0.35, 4]).on("zoom", ev => root.attr("transform", ev.transform));
    svg.call(zoom);

    // --- forces (less dense) ---
    const sim = d3.forceSimulation(DATA.nodes)
      .force("link", d3.forceLink(links).id(d=>d.id).distance(80).strength(0.7))
      .force("charge", d3.forceManyBody().strength(-50))
      .force("center", d3.forceCenter(w/2, h/2))
      .force("collision", d3.forceCollide().radius(d => rScale(nodeScore(d))*1.15));

    const linkSel = linkLayer.selectAll("line")
      .data(links)
      .join("line")
      .attr("class","link");

    const nodeSel = nodeLayer.selectAll("g.node")
      .data(DATA.nodes, d=>d.id)
      .join(enter => {
        const g = enter.append("g").attr("class","node");

        g.append("ellipse")
          .attr("rx", d => rScale(nodeScore(d))*ellipseAspect)
          .attr("ry", d => rScale(nodeScore(d)));

        g.append("text")
          .attr("x", d => rScale(nodeScore(d))*ellipseAspect + 4)
          .attr("y", 4)
          .text(d => d.id);

        g.on("mouseover", (ev,d)=>showTagTooltip(ev,d.id))
         .on("mousemove", moveTooltip)
         .on("mouseout", hideTooltip)
         .on("click", (ev,d)=>{ ev.stopPropagation(); onTagClick(d.id); });

        return g;
      });

    sim.on("tick", () => {
      linkSel
        .attr("x1", d=>d.source.x)
        .attr("y1", d=>d.source.y)
        .attr("x2", d=>d.target.x)
        .attr("y2", d=>d.target.y);

      nodeSel.attr("transform", d=>`translate(${d.x},${d.y})`);
    });

    // Clear selections when clicking backdrop
    svg.on("click", ev => {
      if (ev.target === svg.node()){
        clearFocus();
        rightTitle.textContent = "Click a tag to list its pulses.";
        rightList.innerHTML = "";
        leftBox.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
      }
    });

    // --- tooltip ---
    function showTagTooltip(evt, tag){
      const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) || "—";
      const deg = degree.get(tag) || 0;
      const n = idToNode.get(tag);
      const cent = (typeof n?.centrality === "number") ? n.centrality.toFixed(2) : String(deg);
      tooltip.html(`
        <div style="font-weight:700; margin-bottom:4px">${escapeHtml(tag)}</div>
        <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
        <div style="white-space:pre-wrap; opacity:.92">${escapeHtml(desc)}</div>
        <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to list pulses</div>
      `).style("display","block");
      moveTooltip(evt);
    }
    function moveTooltip(evt){ const pad=12; tooltip.style("left",(evt.clientX+pad)+"px").style("top",(evt.clientY+pad)+"px"); }
    function hideTooltip(){ tooltip.style("display","none"); }
    function escapeHtml(s){return String(s||"").replace(/[&<>"']/g,c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;' }[c]))}

    // --- focus/dimming ---
    function setFocus(keepIds){
      const keep = new Set(keepIds);
      nodeSel.classed("dim", d => !keep.has(d.id))
             .classed("focus", d => keep.has(d.id));
      linkSel.classed("dim", d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    }
    function clearFocus(){
      nodeSel.classed("dim", false).classed("focus", false);
      linkSel.classed("dim", false);
    }

    // --- right sidebar: list pulses for tag ---
    function onTagClick(tagId){
      const tagPulsesRaw = safeArr(DATA.pulsesByTag?.[tagId]);

      // de-dup (by title+date or id)
      const seen = new Set();
      const dedup = [];
      for (const p of tagPulsesRaw){
        const key = (p.id || "") + "|" + (p.title || "") + "|" + (p.date || "");
        if (!seen.has(key)){ seen.add(key); dedup.push(p); }
      }

      // sort newest first
      const pulses = dedup.sort((a,b) => String(b.date||"").localeCompare(String(a.date||"")));

      // dim to neighbors + tag itself
      const keep = new Set([tagId]);
      links.forEach(l => {
        if (l.source.id===tagId) keep.add(l.target.id);
        if (l.target.id===tagId) keep.add(l.source.id);
      });
      setFocus(keep);

      // right title + list
      rightTitle.textContent = `Pulses for ${tagId}`;
      rightList.innerHTML = "";
      for (const p of pulses){
        const row = document.createElement("div");
        row.className = "pulse-item";
        const dot = document.createElement("div");
        dot.className = "pulse-dot";
        row.appendChild(dot);

        const a = document.createElement("a");
        const title = p.title || p.id || "Pulse";
        const date = p.date ? ` (${p.date})` : "";
        a.textContent = trunc(`${title}${date}`, 40);
        a.href = "javascript:void(0)";
        a.onclick = (ev)=>{ ev.preventDefault(); showPulseDetails(p); };
        row.appendChild(a);
        rightList.appendChild(row);
      }

      // if nothing to list
      if (!pulses.length){
        const empty = document.createElement("div");
        empty.className = "muted";
        empty.textContent = "No pulses recorded for this tag.";
        rightList.appendChild(empty);
      }
    }

    // --- left sidebar: pulse details ---
    function renderLinksBlock(label, items){
      items = safeArr(items);
      if (!items.length) return "";
      const norm = items.map(u => typeof u==='string'
        ? {title:u, url:u}
        : (u?.url ? u : {title:(u?.title||u?.url||""), url:(u?.url||"")})
      );

      let html = `<div style="margin-top:12px"><strong>${label}</strong><ul style="padding-left:18px; margin:6px 0 0 0">`;
      for (const it of norm){
        const title = trunc(it.title || it.url || "", 40);
        const href  = it.url || "#";
        html += `<li><a class="ellipsis" href="${escapeHtml(href)}" target="_blank" rel="noopener">${escapeHtml(title)}</a></li>`;
      }
      html += `</ul></div>`;
      return html;
    }

    function showPulseDetails(p){
      const when = p.date ? ` <span class="muted">(${escapeHtml(p.date)})</span>` : "";
      let html = `<h2 style="margin:0 0 8px 0;font-size:16px">${escapeHtml(p.title || p.id || "Pulse")}${when}</h2>`;
      if (p.summary) html += `<div style="white-space:pre-wrap; margin:.3rem 0 1rem 0">${escapeHtml(p.summary)}</div>`;
      html += renderLinksBlock("Papers", p.papers);
      html += renderLinksBlock("Podcasts", p.podcasts);
      leftBox.innerHTML = html;
    }

    // --- search (left filter dims nodes) ---
    function applyFilter(q){
      const s = String(q||"").trim().toLowerCase();
      if (!s){ clearFocus(); return; }
      const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
      setFocus(keep);
    }
    if (searchInput) searchInput.addEventListener("input", e => applyFilter(e.target.value));
  }
})();
