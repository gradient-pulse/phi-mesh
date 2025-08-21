/* docs/map.js – renderer (data expected in window.PHI_DATA) */
(function () {
  // ---- DATA ----
  const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object')
    ? window.PHI_DATA
    : { nodes: [], links: [], tagDescriptions: {}, pulsesByTag: {} };

  // ---- DOM ----
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const sidebar = document.getElementById('sidebar-content');
  const searchInput = document.getElementById('search');

  function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  function safeArray(x){return Array.isArray(x)?x:[]}

  // ---- Config ----
  const vbW  = (svg.node().clientWidth  || 1200);
  const vbH  = (svg.node().clientHeight || 800);
  svg.attr('viewBox', `0 0 ${vbW} ${vbH}`);

  const minR = 6, maxR = 24;           // ellipse base radii
  const ellipseAspect = 1.6;           // rx = r*aspect, ry = r
  const linkOpacity = 0.28;
  const linkOpacityDim = 0.08;

  const satDot = 4.6;                  // satellite dot size
  const spiralStepR = 8;               // constant radial step (px) between pulses
  const spiralStepTheta = 0.48 * Math.PI;
  const spiralStartR = 52;

  // age -> class bucket
  function ageClass(d){
    var a = (d && d.ageDays);
    if (a == null) return 'age-old';
    if (a <= 14)  return 'age-very-new';
    if (a <= 45)  return 'age-new';
    if (a <= 120) return 'age-mid';
    if (a <= 270) return 'age-old';
    return 'age-very-old';
  }

  // ---- Build link objects & degree ----
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links.map(l => ({
    source: idToNode.get(l.source) || l.source,
    target: idToNode.get(l.target) || l.target
  })).filter(l => l.source && l.target);

  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id) || 0) + 1);
    degree.set(l.target.id, (degree.get(l.target.id) || 0) + 1);
  });

  // centrality helper (no ?? mixed with ||)
  function getCentrality(d){
    return (typeof d.centrality === 'number') ? d.centrality : (degree.get(d.id) || 1);
  }

  // radius scale
  const centralities = DATA.nodes.map(getCentrality);
  const cMinRaw = d3.min(centralities);
  const cMaxRaw = d3.max(centralities);
  const cMin = (cMinRaw == null ? 0 : cMinRaw);
  const cMax = (cMaxRaw == null ? 1 : cMaxRaw);
  const rScale = d3.scaleSqrt()
    .domain([ (cMin || 0.0001), (cMax || 1) ])
    .range([ minR, maxR ]);

  // ---- Layers & zoom ----
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');
  const satLayer  = root.append('g').attr('class','satellites');

  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform));
  svg.call(zoom);

  // background click clears selection
  svg.on('click', (ev) => {
    if (ev.target === svg.node()) {
      clearSatellites();
      clearFocus();
      sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
    }
  });

  // ---- Draw ----
  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('stroke','#b9c7dd')
    .attr('stroke-opacity', linkOpacity);

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');

      g.append('ellipse')
        .attr('rx', d => rScale(getCentrality(d)) * ellipseAspect)
        .attr('ry', d => rScale(getCentrality(d)));

      g.append('text')
        .attr('x', d => rScale(getCentrality(d)) * ellipseAspect + 4)
        .attr('y', 4)
        .text(d => d.id);

      g.on('mouseover', (ev,d) => showTagTooltip(ev, d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
       .on('click', (ev,d) => { ev.stopPropagation(); onTagClick(d.id); });

      return g;
    });

  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(75).strength(0.7))
    .force('charge', d3.forceManyBody().strength(-180))
    .force('center', d3.forceCenter(vbW/2, vbH/2))
    .force('collision', d3.forceCollide().radius(d => rScale(getCentrality(d)) * 1.2));

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x)
      .attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x)
      .attr('y2', d=>d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites aligned to host
    satLayer.selectAll('g.satellite')
      .attr('transform', d => `translate(${d.host.x + d._xoff},${d.host.y + d._yoff})`);
  });

  // ---- Tooltip ----
  function showTagTooltip(evt, tag) {
    var desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
    var n = idToNode.get(tag);
    var deg = (degree.get(tag) || 0);
    var cent = (n && typeof n.centrality === 'number') ? n.centrality.toFixed(2) : String(deg || 0);
    tooltip.html(
      '<div style="font-weight:700; margin-bottom:4px">'+esc(tag)+'</div>' +
      '<div class="muted" style="margin-bottom:6px">degree '+deg+' • centrality '+cent+'</div>' +
      '<div style="white-space:pre-wrap; opacity:.92">'+esc(desc)+'</div>' +
      '<div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to reveal pulse satellites</div>'
    ).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){ var pad=12; tooltip.style('left',(evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px'); }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ---- Focus & dimming ----
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  function clearFocus(){
    nodeSel.classed('dim', false);
    linkSel.classed('dim', false);
  }

  // ---- Satellites (spiral) ----
  function clearSatellites(){ satLayer.selectAll('*').remove(); }

  function placeSpiralOffsets(n){
    const out = [];
    for (var i=0;i<n;i++){
      var r = spiralStartR + i*spiralStepR;
      var t = i*spiralStepTheta;
      out.push({ _xoff: r*Math.cos(t), _yoff: r*Math.sin(t) });
    }
    return out;
  }

  function onTagClick(tagId){
    // dim to neighbors of tagId (+ itself)
    const neighbors = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id===tagId) neighbors.add(l.target.id);
      if (l.target.id===tagId) neighbors.add(l.source.id);
    });
    setFocus(neighbors);

    // clear + draw satellites
    clearSatellites();

    const host = idToNode.get(tagId);
    if (!host) return;

    const pulses = safeArray(DATA.pulsesByTag && DATA.pulsesByTag[tagId]);
    if (!pulses.length) return;

    const offs = placeSpiralOffsets(pulses.length);
    const g = satLayer.selectAll('g.satellite')
      .data(pulses.map((p,i)=>Object.assign({}, p, {host:host}, offs[i])), d => d.id || d.title || (d.date||'') );

    const enter = g.enter().append('g').attr('class','satellite');

    enter.append('circle')
      .attr('r', satDot)
      .attr('class', d => ageClass(d));

    enter.append('text')
      .attr('y', -9)
      .attr('text-anchor','middle')
      .attr('font-size', 9)
      .attr('fill', '#a3b3c7')
      .text(d => (d.date ? String(d.date).slice(2,10) : ''));

    enter.on('click', (ev,d) => { ev.stopPropagation(); showPulseDetails(d); });

    sim.alpha(0.5).restart();
  }

  // ---- Sidebar rendering ----
  function renderLinksBlock(label, items){
    if (!items || !items.length) return '';
    const norm = items.map(u => {
      if (typeof u === 'string') return {title:u, url:u};
      if (u && u.url) return u;
      return {title:(u && u.title) ? u.title : (u && u.url) ? u.url : '', url:(u && u.url) ? u.url : ''};
    });
    var html = '<div style="margin-top:12px"><strong>'+esc(label)+'</strong><ul style="padding-left:18px; margin:6px 0 0 0">';
    norm.forEach(it => {
      const title = it.title || it.url || '';
      const href  = it.url || it.title || '#';
      html += '<li><a class="ellipsis" href="'+esc(href)+'" target="_blank" rel="noopener">'+esc(title)+'</a></li>';
    });
    html += '</ul></div>';
    return html;
  }

  function showPulseDetails(p){
    const when = p.date ? ' <span class="muted">('+esc(p.date)+')</span>' : '';
    var html = '<h2>'+esc(p.title || p.id || 'Pulse')+ when +'</h2>';
    if (p.summary) html += '<div style="white-space:pre-wrap; margin:.3rem 0 1rem 0">'+esc(p.summary)+'</div>';
    html += renderLinksBlock('Papers', p.papers);
    html += renderLinksBlock('Podcasts', p.podcasts);
    sidebar.innerHTML = html;
  }

  // ---- Search ----
  function applyFilter(q){
    const s = String(q||'').trim().toLowerCase();
    if (!s){ clearFocus(); return; }
    const keep = new Set(DATA.nodes.filter(n => String(n.id).toLowerCase().includes(s)).map(n=>n.id));
    setFocus(keep);
  }
  if (searchInput) searchInput.addEventListener('input', e => applyFilter(e.target.value));

  // ---- Initial sidebar ----
  sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
})();
