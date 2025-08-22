/* docs/map.js
 * Renders the Tag Map using window.PHI_DATA (produced by generate_graph_data.py)
 * Expected DATA shape:
 *  - nodes: [{ id, centrality? }]
 *  - links: [{ source, target }]
 *  - tagDescriptions: { [tag]: "..." }
 *  - pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts? }] }
 */

(function () {
  const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object') ? window.PHI_DATA : { nodes: [], links: [] };

  // ---------- DOM ----------
  const svg      = d3.select('#graph');
  const tooltip  = d3.select('#tooltip');
  const sidebar  = document.getElementById('sidebar-content');
  const searchEl = document.getElementById('search');

  function esc(s){ return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c])); }
  function arr(x){ return Array.isArray(x) ? x : []; }

  // ---------- Config ----------
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;

  const ellipseAspect = 1.55; // >1 makes horizontal pills
  const minR = 6, maxR = 24;

  const linkOpacity     = 0.22;
  const linkOpacityDim  = 0.06;

  // Satellites
  const satDot           = 4.5;
  const spiralStartR     = 52;     // pixels from tag center
  const spiralStepR      = 12;     // fixed radial increment (keeps the spiral compact)
  const spiralStepTheta  = 0.48 * Math.PI; // angular step

  // Pulse age -> class
  function ageClass(d){
    const a = d && d.ageDays;
    if (a == null) return 'age-old';
    if (a <= 14)  return 'age-very-new';
    if (a <= 45)  return 'age-new';
    if (a <= 120) return 'age-mid';
    if (a <= 270) return 'age-old';
    return 'age-very-old';
  }

  // ---------- SVG layers & zoom ----------
  svg.attr('viewBox', `0 0 ${width} ${height}`);
  const root      = svg.append('g');
  const linkLayer = root.append('g').attr('class', 'links');
  const nodeLayer = root.append('g').attr('class', 'nodes');
  const satLayer  = root.append('g').attr('class', 'satellites');

  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', (ev) => root.attr('transform', ev.transform));
  svg.call(zoom);

  // Click on background clears selection
  svg.on('click', (ev) => {
    if (ev.target === svg.node()) {
      clearSatellites();
      clearFocus();
      showIdleSidebar();
    }
  });

  // ---------- Prep data ----------
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links.map(l => ({
    source: idToNode.get(l.source) || l.source,
    target: idToNode.get(l.target) || l.target
  })).filter(l => l.source && l.target);

  // Degree map (fallback for sizing)
  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id) || 0) + 1);
    degree.set(l.target.id, (degree.get(l.target.id) || 0) + 1);
  });

  const centralities = DATA.nodes.map(n => (typeof n.centrality === 'number' ? n.centrality : (degree.get(n.id) || 0)));
  const cMin = d3.min(centralities) ?? 0;
  const cMax = d3.max(centralities) ?? 1;
  const rScale = d3.scaleSqrt().domain([cMin || 0.0001, cMax || 1]).range([minR, maxR]);

  // SAFARI-SAFE node score (no mixing ?? with ||)
  function nodeScore(d){
    const c = d.centrality;
    if (typeof c === 'number') return c;
    const g = degree.get(d.id);
    return (g || 1);
  }

  // ---------- Simulation ----------
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(82).strength(0.7))
    .force('charge', d3.forceManyBody().strength(-190))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(d => rScale(nodeScore(d)) * 1.18));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class', 'link')
    .attr('stroke', '#b9c7dd')
    .attr('stroke-opacity', linkOpacity)
    .attr('stroke-width', 1);

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d => d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');

      g.append('ellipse')
        .attr('rx', d => rScale(nodeScore(d)) * ellipseAspect)
        .attr('ry', d => rScale(nodeScore(d)));

      g.append('text')
        .attr('x', d => rScale(nodeScore(d)) * ellipseAspect + 4)
        .attr('y', 4)
        .text(d => d.id);

      g.on('mouseover', (ev, d) => showTagTooltip(ev, d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
       .on('click', (ev, d) => { ev.stopPropagation(); onTagClick(d.id); });

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    nodeSel.attr('transform', d => `translate(${d.x},${d.y})`);

    // keep satellites glued to their host
    satLayer.selectAll('g.satellite')
      .attr('transform', d => `translate(${d.host.x + d._xoff},${d.host.y + d._yoff})`);
  });

  // ---------- Tooltip ----------
  function showTagTooltip(evt, tag) {
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
    const n = idToNode.get(tag);
    const deg = degree.get(tag) || 0;
    const cent = (typeof n?.centrality === 'number') ? n.centrality.toFixed(2) : String(deg);
    tooltip.html(
      `<div style="font-weight:700; margin-bottom:4px">${esc(tag)}</div>
       <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${esc(cent)}</div>
       <div style="white-space:pre-wrap; opacity:.92">${esc(desc)}</div>
       <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to reveal pulse satellites</div>`
    ).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad = 12;
    tooltip.style('left', (evt.clientX + pad) + 'px').style('top', (evt.clientY + pad) + 'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ---------- Focus / dim ----------
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)))
            .attr('stroke-opacity', d => (keep.has(d.source.id) && keep.has(d.target.id)) ? linkOpacity : linkOpacityDim);
  }
  function clearFocus(){
    nodeSel.classed('dim', false);
    linkSel.classed('dim', false).attr('stroke-opacity', linkOpacity);
  }

  // ---------- Satellites (spiral) ----------
  let currentTag = null;

  function clearSatellites(){
    currentTag = null;
    satLayer.selectAll('*').remove();
  }

  function spiralOffsets(n){
    const out = [];
    for (let i = 0; i < n; i++){
      const r = spiralStartR + i * spiralStepR;          // <- FIXED spacing
      const t = i * spiralStepTheta;
      out.push({ _xoff: r * Math.cos(t), _yoff: r * Math.sin(t) });
    }
    return out;
  }

  function onTagClick(tagId){
    currentTag = tagId;

    // Dim to neighbors (+self)
    const keep = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id === tagId) keep.add(l.target.id);
      if (l.target.id === tagId) keep.add(l.source.id);
    });
    setFocus(keep);

    // satellites
    satLayer.selectAll('*').remove();
    const host = idToNode.get(tagId);
    if (!host) { showIdleSidebar(); return; }

    const pulses = arr(DATA.pulsesByTag && DATA.pulsesByTag[tagId]);
    if (!pulses.length){
      // No pulses; show a small message but keep the focus
      sidebar.innerHTML = `<h2>${esc(tagId)}</h2><div class="muted">No pulses found for this tag.</div>`;
      return;
    }

    const offs = spiralOffsets(pulses.length);
    const g = satLayer.selectAll('g.satellite')
      .data(pulses.map((p, i) => ({ ...p, host, ...offs[i] })), d => d.id || d.title || (d.date || ''));

    const enter = g.enter().append('g').attr('class','satellite');

    enter.append('circle')
      .attr('r', satDot)
      .attr('class', d => ageClass(d));

    // Tiny date label above each pulse
    enter.append('text')
      .attr('y', -9)
      .attr('text-anchor','middle')
      .attr('font-size', 9)
      .attr('fill', '#a3b3c7')
      .text(d => d.date ? d.date.slice(2,10) : '');

    enter.on('click', (ev, d) => { ev.stopPropagation(); showPulseDetails(d); });

    // Sidebar: pulse list for the tag (click to open details)
    renderPulseList(tagId, pulses);

    sim.alpha(0.5).restart();
  }

  // ---------- Sidebar rendering ----------
  function showIdleSidebar(){
    sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
  }

  function renderLinksBlock(label, items){
    if (!items || !items.length) return '';
    const norm = items.map(u => typeof u === 'string'
      ? { title: u, url: u }
      : (u && u.url ? u : { title: (u && (u.title || u.url)) || '', url: (u && u.url) || '' })
    );
    let html = `<div style="margin-top:12px"><strong>${label}</strong><ul style="padding-left:18px; margin:6px 0 0 0">`;
    for (const it of norm){
      const title = it.title || it.url || '';
      const href  = it.url || it.title || '#';
      html += `<li><a class="ellipsis" href="${esc(href)}" target="_blank" rel="noopener">${esc(title)}</a></li>`;
    }
    html += `</ul></div>`;
    return html;
  }

  function showPulseDetails(p){
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap; margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;
    html += renderLinksBlock('Papers',   p.papers);
    html += renderLinksBlock('Podcasts', p.podcasts);
    sidebar.innerHTML = html;
  }

  function renderPulseList(tagId, pulses){
    // Sidebar block with a clickable list of pulses for the selected tag
    let html = `<h2>Pulses for <span class="muted">${esc(tagId)}</span> <span class="muted">(${pulses.length})</span></h2>`;
    html += `<ul style="list-style:none; padding-left:0; margin:.5rem 0 0 0">`;
    for (const p of pulses){
      const label = `${p.date ? p.date : ''} — ${p.title || p.id || 'Pulse'}`.trim();
      const safeId = esc((p.id || p.title || p.date || Math.random().toString(36).slice(2)));
      html += `<li style="margin:.25rem 0">
        <a href="#" data-pulse-key="${safeId}" class="ellipsis">${esc(label)}</a>
      </li>`;
    }
    html += `</ul>`;
    sidebar.innerHTML = html;

    // Wire clicks to open details
    const links = sidebar.querySelectorAll('a[data-pulse-key]');
    links.forEach((a, i) => {
      a.addEventListener('click', (ev) => {
        ev.preventDefault();
        showPulseDetails(pulses[i]);
      });
    });
  }

  // ---------- Search (tag filter) ----------
  function applyFilter(q){
    const s = (q || '').trim().toLowerCase();
    if (!s){ clearFocus(); return; }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n => n.id));
    setFocus(keep);
  }
  if (searchEl) searchEl.addEventListener('input', (e) => applyFilter(e.target.value));

  // ---------- Initial sidebar ----------
  showIdleSidebar();
})();
