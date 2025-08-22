/* docs/map.js — render tag graph using window.PHI_DATA */
(function(){
  const DATA = window.PHI_DATA || { nodes:[], links:[] };

  // DOM
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const leftContent = document.getElementById('left-content');
  const leftHint = document.getElementById('left-hint');
  const pulseList = document.getElementById('pulse-list');
  const searchInput = document.getElementById('search');

  // initial left panel hint only (no extra paragraph lives in HTML)
  leftContent.innerHTML = ''; // keep empty until a pulse is opened

  // sizes
  const W = svg.node().clientWidth || 1200;
  const H = svg.node().clientHeight || 800;
  svg.attr('viewBox', `0 0 ${W} ${H}`);

  // layers
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');

  // maps
  const idToNode = new Map(DATA.nodes.map(n=>[n.id,n]));
  const links = DATA.links.map(l => ({
    source: idToNode.get(l.source) || l.source,
    target: idToNode.get(l.target) || l.target
  })).filter(l => l.source && l.target);

  // degree & sizing
  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
    degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
  });
  const centralities = DATA.nodes.map(n => (typeof n.centrality==='number' ? n.centrality : (degree.get(n.id)||0)));
  const cMin = d3.min(centralities) ?? 0, cMax = d3.max(centralities) ?? 1;
  const rScale = d3.scaleSqrt().domain([cMin||0.0001, cMax||1]).range([6, 22]);
  const ellipseAspect = 1.6;

  // simulation — slightly looser -> less dense
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(78).strength(0.65))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collide', d3.forceCollide().radius(d => rScale(d.centrality ?? degree.get(d.id) || 1)*1.25));

  // draw
  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');
      g.append('ellipse')
        .attr('rx', d => rScale(d.centrality ?? degree.get(d.id) || 1) * ellipseAspect)
        .attr('ry', d => rScale(d.centrality ?? degree.get(d.id) || 1));
      g.append('text')
        .attr('x', d => rScale(d.centrality ?? degree.get(d.id) || 1) * ellipseAspect + 4)
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

  // zoom
  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', ev => root.attr('transform', ev.transform));
  svg.call(zoom);

  // background click resets selection
  svg.on('click', () => {
    clearFocus();
    nodeSel.classed('selected', false);
    pulseList.textContent = 'Click a tag to list its pulses.';
    pulseList.className = 'muted one-line';
  });

  // tooltips
  function showTip(evt, tag){
    const desc = DATA.tagDescriptions?.[tag] || '—';
    const deg = degree.get(tag)||0;
    const cent = (typeof idToNode.get(tag)?.centrality==='number') ? idToNode.get(tag).centrality.toFixed(2) : deg;
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

  // focus/dim
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  function clearFocus(){ nodeSel.classed('dim', false); linkSel.classed('dim', false); }

  // right sidebar list
  function renderPulseList(tagId){
    const raw = Array.isArray(DATA.pulsesByTag?.[tagId]) ? DATA.pulsesByTag[tagId] : [];
    if (!raw.length){
      pulseList.textContent = `No pulses for ${tagId}.`;
      pulseList.className = 'muted one-line';
      return;
    }
    // dedupe by (id || title || date)
    const seen = new Set();
    const items = [];
    for (const p of raw){
      const key = p.id || p.title || p.date || JSON.stringify(p).slice(0,60);
      if (seen.has(key)) continue;
      seen.add(key);
      items.push(p);
    }
    // sort newest first by ISO date `YYYY-MM-DD`
    items.sort((a,b) => String(b.date||'').localeCompare(String(a.date||'')));

    const rows = items.map(p => {
      const title = p.title || p.id || 'Pulse';
      const date = p.date ? ` (${p.date})` : '';
      return `<div class="one-line" data-key="${esc(p.id||p.title||'')}" style="padding:6px 4px; cursor:pointer">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ff8a70;margin-right:8px;vertical-align:middle"></span>
                <span>${esc(title)}${esc(date)}</span>
              </div>`;
    }).join('');
    pulseList.className = '';
    pulseList.innerHTML = `<div style="font-weight:600; margin:2px 0 6px 0">Pulses for ${esc(tagId)}</div>${rows}`;

    // clicking a pulse shows details in the LEFT panel
    pulseList.querySelectorAll('[data-key]').forEach(el => {
      el.addEventListener('click', () => {
        const key = el.getAttribute('data-key');
        const pulse = items.find(p => (p.id||p.title||'')===key);
        if (pulse) showPulseLeft(pulse);
      });
    });
  }

  function showPulseLeft(p){
    // clear helper forever
    leftHint.textContent = '';
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<div style="font-weight:700; font-size:15px; margin-bottom:6px">${esc(p.title || p.id || 'Pulse')}${when}</div>`;
    if (p.summary) html += `<div style="white-space:pre-wrap; margin:6px 0 12px 0">${esc(p.summary)}</div>`;
    html += renderLinkBlock('Papers', p.papers);
    html += renderLinkBlock('Podcasts', p.podcasts);
    leftContent.innerHTML = html;
  }

  function renderLinkBlock(label, items){
    if (!Array.isArray(items) || !items.length) return '';
    const norm = items.map(u => typeof u==='string' ? {title:u, url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
    let s = `<div style="margin-top:10px"><strong>${label}</strong><ul style="padding-left:18px; margin:6px 0 0 0">`;
    for (const it of norm){
      s += `<li class="one-line"><a href="${esc(it.url||'#')}" target="_blank" rel="noopener">${esc(it.title||it.url||'link')}</a></li>`;
    }
    s += `</ul></div>`;
    return s;
  }

  // tag click handler
  function onTagClick(tagId){
    // highlight JUST the clicked node
    nodeSel.classed('selected', d => d.id === tagId);

    // dim to neighbors (and itself)
    const keep = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id===tagId) keep.add(l.target.id);
      if (l.target.id===tagId) keep.add(l.source.id);
    });
    setFocus(keep);

    // fill right sidebar
    renderPulseList(tagId);
  }

  // search filter -> dim everything except matches
  if (searchInput){
    searchInput.addEventListener('input', e => {
      const q = e.target.value.trim().toLowerCase();
      if (!q){ clearFocus(); return; }
      const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(q)).map(n=>n.id));
      setFocus(keep);
    });
  }
})();
