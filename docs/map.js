/* docs/map.js — renderer (no data logic here) */
(function () {
  const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object') ? window.PHI_DATA : { nodes: [], links: [] };

  // DOM
  const svg      = d3.select('#graph');
  const tooltip  = d3.select('#tooltip');
  const left     = document.getElementById('sidebar-content');
  const rightUl  = document.getElementById('plist');
  const rightH   = document.getElementById('plist-title');
  const searchEl = document.getElementById('search');

  function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
  function safeArr(x){return Array.isArray(x)?x:[]}

  // Sizing
  svg.attr('viewBox', `0 0 ${svg.node().clientWidth || 1200} ${svg.node().clientHeight || 800}`);

  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;

  const minR = 5, maxR = 20;        // slightly smaller
  const ellipseAspect = 1.4;        // less oval
  const linkDist = 68;
  const charge = -150;

  // Age bucket → class
  function ageClass(d){
    const a = d?.ageDays;
    if (a == null) return 'age-old';
    if (a <= 14)  return 'age-very-new';
    if (a <= 45)  return 'age-new';
    if (a <= 120) return 'age-mid';
    if (a <= 270) return 'age-old';
    return 'age-very-old';
  }

  // Build maps
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links
    .map(l => ({ source: idToNode.get(l.source) || l.source, target: idToNode.get(l.target) || l.target }))
    .filter(l => l.source && l.target);

  // degree for fallback sizing
  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
    degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
  });

  const centralities = DATA.nodes.map(n => (typeof n.centrality === 'number' ? n.centrality : degree.get(n.id)||0));
  const cMin = d3.min(centralities) ?? 0, cMax = d3.max(centralities) ?? 1;
  const rScale = d3.scaleSqrt().domain([cMin || 0.0001, cMax || 1]).range([minR, maxR]);

  // Helper (Safari-safe; no ?? mixed with ||)
  function nodeScore(d){
    const c = d.centrality;
    return (typeof c === 'number') ? c : ((degree.get(d.id) || 1));
  }

  // Layers & zoom
  const root      = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');

  const zoom = d3.zoom().scaleExtent([0.45, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform));
  svg.call(zoom);

  // Clicking empty space clears selection
  svg.on('click', (ev)=>{ if (ev.target === svg.node()) { setFocus(null); showPulseList(null); left.innerHTML=''; } });

  // Simulation
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(linkDist).strength(0.8))
    .force('charge', d3.forceManyBody().strength(charge))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(d => rScale(nodeScore(d))*1.15));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  let activeTag = null;

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');

      g.append('ellipse')
        .attr('rx', d => rScale(nodeScore(d))*ellipseAspect)
        .attr('ry', d => rScale(nodeScore(d)));

      g.append('text')
        .attr('x', d => rScale(nodeScore(d))*ellipseAspect + 4)
        .attr('y', 4)
        .text(d => d.id);

      g.on('mouseover', (ev,d) => showTagTooltip(ev, d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
       .on('click', (ev,d) => { ev.stopPropagation(); onTagClick(d.id); });

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);
  });

  // Tooltip
  function showTagTooltip(evt, tag) {
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) || '—';
    const n = idToNode.get(tag);
    const deg = degree.get(tag) || 0;
    const cent = (typeof n?.centrality==='number') ? n.centrality.toFixed(2) : (deg||0);
    tooltip.html(`
      <div style="font-weight:700; margin-bottom:4px">${esc(tag)}</div>
      <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
      <div style="white-space:pre-wrap; opacity:.92">${esc(desc)}</div>
      <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to list pulses</div>
    `).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){ const pad=12; tooltip.style('left',(evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px'); }
  function hideTooltip(){ tooltip.style('display','none'); }

  // Focus / dim
  function setFocus(tagId){
    activeTag = tagId;
    if (!tagId){
      nodeSel.classed('dim', false).classed('active', false);
      linkSel.classed('dim', false);
      return;
    }
    const keep = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id===tagId) keep.add(l.target.id);
      if (l.target.id===tagId) keep.add(l.source.id);
    });
    nodeSel
      .classed('dim', d => !keep.has(d.id))
      .classed('active', d => d.id === tagId);
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }

  // Right list
  function showPulseList(tagId){
    rightUl.innerHTML = '';
    rightH.textContent = tagId ? `Pulses for ${tagId}` : 'Pulses';
    if (!tagId) return;
    const pulses = safeArr(DATA.pulsesByTag?.[tagId]);
    for (const p of pulses){
      const li = document.createElement('li');
      const dot = document.createElement('span');
      dot.className = `dot ${ageClass(p)}`;
      const title = document.createElement('span');
      title.className = 'ellipsis';
      title.textContent = p.title || p.id || 'Pulse';
      const date = document.createElement('span');
      date.className = 'pdate';
      date.textContent = p.date || '';

      li.appendChild(dot); li.appendChild(title); li.appendChild(date);
      li.addEventListener('click', (ev)=>{ ev.stopPropagation(); showPulseDetails(p); });
      rightUl.appendChild(li);
    }
  }

  // Left: pulse details (smaller text, one-line links)
  function linksBlock(label, items){
    if (!items?.length) return '';
    const norm = items.map(u => typeof u==='string' ? {title:u, url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
    let html = `<div style="margin-top:10px"><strong>${label}</strong><ul class="sidebar-links" style="padding-left:16px; margin:6px 0 0 0">`;
    for (const it of norm){
      const title = (it.title || it.url || '').slice(0, 40); // truncate display text
      const href  = it.url || it.title || '#';
      html += `<li><a class="ellipsis" href="${esc(href)}" target="_blank" rel="noopener">${esc(title)}</a></li>`;
    }
    html += `</ul></div>`;
    return html;
  }

  function showPulseDetails(p){
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<h2 style="font-size:16px; margin:.2rem 0 .4rem 0">${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap; margin:.2rem 0 .6rem 0; font-size:13px">${esc(p.summary)}</div>`;
    html += linksBlock('Papers', p.papers);
    html += linksBlock('Podcasts', p.podcasts);
    left.innerHTML = html;
  }

  // Tag click
  function onTagClick(tagId){
    setFocus(tagId);
    showPulseList(tagId);
  }

  // Search (filters nodes by substring; clears lists)
  function applyFilter(q){
    const s = (q||'').trim().toLowerCase();
    if (!s){ setFocus(null); showPulseList(null); return; }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
    nodeSel.classed('dim', d => !keep.has(d.id)).classed('active', false);
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    showPulseList(null);
    left.innerHTML = '';
  }
  searchEl?.addEventListener('input', e => applyFilter(e.target.value));

  // No default text in left sidebar (stays empty until a pulse is clicked)
})();
