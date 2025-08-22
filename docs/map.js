/* docs/map.js — render tag graph using window.PHI_DATA */
document.addEventListener('DOMContentLoaded', () => {
  const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object')
    ? window.PHI_DATA : { nodes:[], links:[] };

  // --- DOM ---
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const leftContent = document.getElementById('left-content');
  const leftHint = document.getElementById('left-hint');
  const pulseList = document.getElementById('pulse-list');
  const searchInput = document.getElementById('search');

  // left panel starts empty (hint stays in header)
  if (leftContent) leftContent.innerHTML = '';

  // --- sizes & viewBox ---
  const W = (svg.node() && svg.node().clientWidth)  || 1200;
  const H = (svg.node() && svg.node().clientHeight) || 800;
  svg.attr('viewBox', `0 0 ${W} ${H}`);

  // --- layers ---
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');

  // --- prep data ---
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links.map(l => ({
    source: idToNode.get(l.source) || l.source,
    target: idToNode.get(l.target) || l.target
  })).filter(l => l.source && l.target);

  // degree for fallback sizing
  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
    degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
  });

  function nodeScore(d){
    const c = d && d.centrality;
    return (typeof c === 'number') ? c : (degree.get(d.id) || 1);
  }

  const centralities = DATA.nodes.map(nodeScore);
  const mmMin = d3.min(centralities);
  const mmMax = d3.max(centralities);
  const cMin = (mmMin == null ? 0 : mmMin);
  const cMax = (mmMax == null ? 1 : mmMax);

  const rScale = d3.scaleSqrt()
    .domain([ (cMin === 0 ? 0.0001 : cMin), (cMax === 0 ? 1 : cMax) ])
    .range([5, 20]); // slightly smaller nodes

  const ellipseAspect = 1.6;

  // --- simulation (looser => less dense) ---
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(0.50))
    .force('charge', d3.forceManyBody().strength(-290))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collide', d3.forceCollide().radius(d => rScale(nodeScore(d))*1.35));

  // --- draw ---
  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

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

      g.on('mouseover', (ev,d)=>showTip(ev,d.id))
       .on('mousemove', moveTip)
       .on('mouseout', hideTip)
       .on('click', (ev,d)=>{ ev.stopPropagation(); onTagClick(d.id); });

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);
  });

  // --- zoom/pan ---
  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', ev => root.attr('transform', ev.transform));
  svg.call(zoom);

  // --- background click clears focus & right list hint ---
  svg.on('click', () => {
    clearFocus();
    nodeSel.classed('selected', false);
    if (pulseList){
      pulseList.textContent = 'Click a tag to list its pulses.';
      pulseList.className = 'muted one-line';
    }
  });

  // --- tooltip helpers ---
  function showTip(evt, tag){
    const n = idToNode.get(tag);
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
    const deg = degree.get(tag) || 0;
    const cent = (n && typeof n.centrality === 'number') ? n.centrality.toFixed(2) : String(deg);
    tooltip.html(
      `<div style="font-weight:700; margin-bottom:4px">${esc(tag)}</div>
       <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
       <div style="white-space:pre-wrap; opacity:.92">${esc(desc)}</div>
       <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to list pulses</div>`
    ).style('display','block');
    moveTip(evt);
  }
  function moveTip(evt){ const p=12; tooltip.style('left',(evt.clientX+p)+'px').style('top',(evt.clientY+p)+'px'); }
  function hideTip(){ tooltip.style('display','none'); }
  function esc(s){ return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c])) }

  // --- focus/dim ---
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  function clearFocus(){ nodeSel.classed('dim', false); linkSel.classed('dim', false); }

  // --- right sidebar list ---
  function renderPulseList(tagId){
    const raw = (DATA.pulsesByTag && Array.isArray(DATA.pulsesByTag[tagId])) ? DATA.pulsesByTag[tagId] : [];
    if (!pulseList) return;

    if (!raw.length){
      pulseList.textContent = `No pulses for ${tagId}.`;
      pulseList.className = 'muted one-line';
      return;
    }

    // de-dupe by (id || title || date)
    const seen = new Set();
    const items = [];
    for (const p of raw){
      const key = p.id || p.title || p.date || JSON.stringify(p).slice(0,60);
      if (seen.has(key)) continue;
      seen.add(key);
      items.push(p);
    }

    // newest first
    items.sort((a,b) => String(b.date||'').localeCompare(String(a.date||'')));

    const rows = items.map(p => {
      const title = p.title || p.id || 'Pulse';
      const date = p.date ? ` (${p.date})` : '';
      return `<div class="one-line" data-key="${esc(p.id||p.title||'')}" style="padding:6px 4px; cursor:pointer">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--pulse);margin-right:8px;vertical-align:middle"></span>
                <span>${esc(title)}${esc(date)}</span>
              </div>`;
    }).join('');

    pulseList.className = ''; // allow multiple rows, but each is one-line
    pulseList.innerHTML = `<div style="font-weight:600; margin:2px 0 6px 0">Pulses for ${esc(tagId)}</div>${rows}`;

    // clicking a pulse shows details in LEFT panel
    pulseList.querySelectorAll('[data-key]').forEach(el => {
      el.addEventListener('click', () => {
        const key = el.getAttribute('data-key') || '';
        const pulse = items.find(p => (p.id||p.title||'') === key);
        if (pulse) showPulseLeft(pulse);
      });
    });
  }

  function renderLinkBlock(label, items){
    if (!Array.isArray(items) || !items.length) return '';
    const norm = items.map(u => typeof u==='string' ? {title:u, url:u}
      : (u && u.url ? u : {title:(u && (u.title||u.url)) || '', url:(u && u.url) || ''}));
    let s = `<div style="margin-top:10px"><strong>${label}</strong><ul style="padding-left:18px; margin:6px 0 0 0">`;
    for (const it of norm){
      const t = it.title || it.url || 'link';
      const h = it.url || '#';
      s += `<li class="one-line"><a href="${esc(h)}" target="_blank" rel="noopener">${esc(t)}</a></li>`;
    }
    s += `</ul></div>`;
    return s;
  }

  function showPulseLeft(p){
    if (leftHint) leftHint.textContent = '';
    if (!leftContent) return;

    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<div style="font-weight:700; font-size:15px; margin-bottom:6px">${esc(p.title || p.id || 'Pulse')}${when}</div>`;
    if (p.summary) html += `<div style="white-space:pre-wrap; margin:6px 0 12px 0">${esc(p.summary)}</div>`;
    html += renderLinkBlock('Papers', p.papers);
    html += renderLinkBlock('Podcasts', p.podcasts);
    leftContent.innerHTML = html;
  }

  // --- tag click ---
  function onTagClick(tagId){
    nodeSel.classed('selected', d => d.id === tagId); // just the clicked node

    // keep only neighbors + self
    const keep = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id === tagId) keep.add(l.target.id);
      if (l.target.id === tagId) keep.add(l.source.id);
    });
    setFocus(keep);

    renderPulseList(tagId);
  }

  // --- search filter ---
  if (searchInput){
    searchInput.addEventListener('input', e => {
      const q = (e.target && e.target.value ? e.target.value : '').trim().toLowerCase();
      if (!q){ clearFocus(); return; }
      const keep = new Set(DATA.nodes.filter(n => (n.id||'').toLowerCase().includes(q)).map(n=>n.id));
      setFocus(keep);
    });
  }
});
