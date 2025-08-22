/* docs/map.js — renderer for Phi-Mesh Tag Map (uses window.PHI_DATA) */
(function(){
  const DATA = (typeof window !== 'undefined' && window.PHI_DATA) ? window.PHI_DATA : {nodes:[],links:[]};

  // --- DOM guards (Safari-safe) ---
  const svgSel = d3.select('#graph');
  if (svgSel.empty()) return; // no graph container found
  const tooltip = d3.select('#tooltip');
  const details = document.getElementById('details');
  const searchInput = document.getElementById('search');
  const pulseHint = document.getElementById('pulse-hint');
  const pulsesTitle = document.getElementById('pulses-title');
  const pulseList = document.getElementById('pulse-list');

  // --- helpers ---
  function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
  function arr(x){return Array.isArray(x)?x:[]}
  function ageClass(days){
    if (days == null) return 'old';
    if (days <= 14) return 'recent';
    if (days <= 90) return 'mid';
    return 'old';
  }
  function nodeScore(d, degree){
    const c = d && d.centrality;
    return (typeof c === 'number') ? c : ((degree.get(d.id) || 1));
  }
  function parseDate(s){
    if (!s) return null;
    // prefer ISO (YYYY-MM-DD)
    const t = Date.parse(s);
    return isNaN(t) ? null : new Date(t);
  }

  // --- layout config ---
  const w = svgSel.node().clientWidth || 1200;
  const h = svgSel.node().clientHeight || 800;
  svgSel.attr('viewBox', `0 0 ${w} ${h}`);

  const minR = 5, maxR = 18;         // smaller caps so labels breathe
  const ellipseAspect = 1.5;         // horizontal stretch
  const linkDistance = 105;          // spread graph more
  const repulsion = -260;            // stronger (more space)
  const collidePad = 1.15;           // slight padding

  const root = svgSel.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');

  // zoom/pan
  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', ev => root.attr('transform', ev.transform));
  svgSel.call(zoom);

  // click background clears selections
  svgSel.on('click', ev => {
    if (ev.target === svgSel.node()){
      clearFocus();
      setSelectedTag(null);
      renderPulseList(null);
      renderPulseDetails(null);
    }
  });

  // --- prep data ---
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links
    .map(l => ({source: idToNode.get(l.source) || l.source, target: idToNode.get(l.target) || l.target}))
    .filter(l => l.source && l.target);

  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
    degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
  });

  const centralities = DATA.nodes.map(n => nodeScore(n, degree));
  const cMin = d3.min(centralities) ?? 1, cMax = d3.max(centralities) ?? 1;
  const rScale = d3.scaleSqrt().domain([cMin, cMax]).range([minR, maxR]);

  // --- simulation ---
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(linkDistance).strength(0.7))
    .force('charge', d3.forceManyBody().strength(repulsion))
    .force('center', d3.forceCenter(w/2, h/2))
    .force('collide', d3.forceCollide().radius(d => rScale(nodeScore(d,degree))*collidePad));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');

      g.append('ellipse')
        .attr('rx', d => rScale(nodeScore(d,degree))*ellipseAspect)
        .attr('ry', d => rScale(nodeScore(d,degree)));

      g.append('text')
        .attr('x', d => rScale(nodeScore(d,degree))*ellipseAspect + 4)
        .attr('y', 4)
        .text(d => d.id);

      g.on('mouseover', (ev,d) => showTagTip(ev, d.id))
       .on('mousemove', moveTip)
       .on('mouseout', hideTip)
       .on('click', (ev,d) => { ev.stopPropagation(); onTagClick(d.id); });

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x)
      .attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x)
      .attr('y2', d=>d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);
  });

  // --- tooltip ---
  function showTagTip(evt, tag){
    const desc = DATA.tagDescriptions && DATA.tagDescriptions[tag] ? DATA.tagDescriptions[tag] : '';
    const deg = degree.get(tag) || 0;
    const n = idToNode.get(tag);
    const cent = (typeof n?.centrality === 'number') ? n.centrality.toFixed(2) : String(deg);
    tooltip.html(
      `<div style="font-weight:700;margin-bottom:4px">${esc(tag)}</div>
       <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${esc(cent)}</div>
       <div style="white-space:pre-wrap;opacity:.92">${esc(desc)}</div>`
    ).style('display','block');
    moveTip(evt);
  }
  function moveTip(evt){ const pad=12; tooltip.style('left',(evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px'); }
  function hideTip(){ tooltip.style('display','none'); }

  // --- focus / dimming ---
  let selectedTag = null;
  function setSelectedTag(tagId){
    selectedTag = tagId;
    nodeSel.classed('selected', d => d.id === tagId);
  }
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  function clearFocus(){
    nodeSel.classed('dim', false);
    linkSel.classed('dim', false);
    setSelectedTag(null);
  }

  // --- tag click => list pulses on right, highlight graph ---
  function onTagClick(tagId){
    setSelectedTag(tagId);

    // dim to neighbors of tag
    const keep = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id === tagId) keep.add(l.target.id);
      if (l.target.id === tagId) keep.add(l.source.id);
    });
    setFocus(keep);

    renderPulseList(tagId);
    // keep map centered; side panel scrolls independently
  }

  // --- right panel: list of pulses for tag (sorted, deduped) ---
  function renderPulseList(tagId){
    pulseList.innerHTML = '';
    pulsesTitle.textContent = '';
    if (pulseHint) pulseHint.style.display = tagId ? 'none' : '';

    if (!tagId) return;

    const raw = arr(DATA.pulsesByTag && DATA.pulsesByTag[tagId]);
    // normalize to objects with {title,url?,date,ageDays,...}
    const norm = raw.map(p => (typeof p === 'string' ? {title:p} : p || {}));

    // de-duplicate by (title,date)
    const seen = new Set();
    const dedup = [];
    for (const p of norm){
      const key = `${p.title||p.id||''}||${p.date||''}`;
      if (!seen.has(key)){ seen.add(key); dedup.push(p); }
    }

    // sort by date desc (fallback: leave order)
    dedup.sort((a,b) => {
      const da = parseDate(a.date); const db = parseDate(b.date);
      if (da && db) return db - da;
      if (da) return -1;
      if (db) return 1;
      return 0;
    });

    pulsesTitle.textContent = `Pulses for ${tagId}`;

    for (const p of dedup){
      const li = document.createElement('li');
      const dot = document.createElement('span');
      dot.className = `dot ${ageClass(p.ageDays)}`;
      const title = document.createElement('span');
      const label = p.title || p.id || '(untitled)';
      const when = p.date ? ` (${p.date})` : '';
      title.className = 'title';
      title.textContent = `${label}${when}`;
      li.appendChild(dot);
      li.appendChild(title);
      li.addEventListener('click', () => renderPulseDetails(p));
      pulseList.appendChild(li);
    }
  }

  // --- left panel: pulse details ---
  function renderLinksBlock(label, items){
    if (!items || !items.length) return '';
    const norm = items.map(u => typeof u==='string' ? {title:u,url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
    let html = `<div class="block"><strong>${esc(label)}</strong>`;
    for (const it of norm){
      const t = it.title || it.url || '';
      const href = it.url || it.title || '#';
      html += `<a href="${esc(href)}" target="_blank" rel="noopener">${esc(t)}</a>`;
    }
    html += `</div>`;
    return html;
  }

  function renderPulseDetails(p){
    if (!p){ details.innerHTML=''; return; }
    const when = p.date ? ` <span class="date">(${esc(p.date)})</span>` : '';
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
    if (p.summary) html += `<div class="summary">${esc(p.summary)}</div>`;
    html += renderLinksBlock('Papers', p.papers);
    html += renderLinksBlock('Podcasts', p.podcasts);
    details.innerHTML = html;
  }

  // --- search filter ---
  function applyFilter(q){
    const s = (q||'').trim().toLowerCase();
    if (!s){ clearFocus(); return; }
    const keepIds = DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id);
    setFocus(keepIds);
  }
  if (searchInput) searchInput.addEventListener('input', e => applyFilter(e.target.value));

})();
