/* docs/map.js – renderer (data lives in docs/data.js)
   - Empty sidebar until a pulse is clicked
   - Clear sidebar when clicking a tag
   - Dimming + force tweaks for a cleaner layout
   - Sidebar "Pulses for <tag>" list with colored dots
*/
(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // ----- DOM -----
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const sidebar = document.getElementById('sidebar-content');
  const searchInput = document.getElementById('search');

  // Sidebar helpers
  function setSidebarHTML(html) { sidebar.innerHTML = html || ''; }
  function clearSidebar() { setSidebarHTML(''); }

  // Esc helpers
  const esc = (s)=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const safeArray = (x)=>Array.isArray(x)?x:[];

  // ----- Config -----
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;

  const minR = 6, maxR = 24;
  const ellipseAspect = 1.6;

  // Layout: open up a bit, but not chaotic
  const LINK_DIST = 92;
  const LINK_STR  = 0.7;
  const CHARGE    = -230;
  const COLLIDE_K = 1.25;

  // Dimming
  const linkOpacity = 0.26;
  const linkOpacityDim = 0.05;

  // Satellite spiral (constant radial step)
  const satDot = 4.6;
  const spiralStepR = 8;
  const spiralStepTheta = 0.48 * Math.PI;
  const spiralStartR = 52;

  // Age -> CSS class for color
  function ageClass(d){
    const a = d?.ageDays;
    if (a == null) return 'age-old';
    if (a <= 14)  return 'age-very-new';
    if (a <= 45)  return 'age-new';
    if (a <= 120) return 'age-mid';
    if (a <= 270) return 'age-old';
    return 'age-very-old';
  }

  // ----- SVG layers + zoom -----
  svg.attr('viewBox', `0 0 ${width} ${height}`);
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');
  const satLayer  = root.append('g').attr('class','satellites');

  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform));
  svg.call(zoom);

  // Background click clears satellites + focus, and empties sidebar
  svg.on('click', (ev) => {
    if (ev.target === svg.node()) {
      clearSatellites();
      clearFocus();
      clearSidebar();
    }
  });

  // ----- Prep DATA -----
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links
    .map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    }))
    .filter(l => l.source && l.target);

  // Compute degree for size fallback
  const degree = new Map();
  links.forEach(l => {
    degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
    degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
  });

  const centr = DATA.nodes.map(n => (typeof n.centrality === 'number' ? n.centrality : degree.get(n.id)||0));
  const cMin = d3.min(centr) ?? 0, cMax = d3.max(centr) ?? 1;
  const rScale = d3.scaleSqrt().domain([cMin||0.0001, cMax||1]).range([minR, maxR]);

  // ----- Simulation -----
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(LINK_DIST).strength(LINK_STR))
    .force('charge', d3.forceManyBody().strength(CHARGE))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(d => rScale(d.centrality ?? degree.get(d.id) || 1)*COLLIDE_K));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('stroke-opacity', linkOpacity);

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

      g.on('mouseover', (ev,d) => showTagTooltip(ev, d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
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

    // keep satellites aligned to the host node
    satLayer.selectAll('g.satellite')
      .attr('transform', d => `translate(${d.host.x + d._xoff},${d.host.y + d._yoff})`);
  });

  // ----- Tooltip -----
  function showTagTooltip(evt, tag) {
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
    const n = idToNode.get(tag);
    const deg = degree.get(tag) || 0;
    const cent = (typeof n?.centrality==='number') ? n.centrality.toFixed(2) : (deg||0);
    tooltip.html(
      `<div style="font-weight:700; margin-bottom:4px">${esc(tag)}</div>
       <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
       <div style="white-space:pre-wrap; opacity:.92">${esc(desc)}</div>
       <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to reveal pulse satellites</div>`
    ).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad=12;
    tooltip.style('left', (evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ----- Focus & dimming -----
  function setFocus(keepIds){
    const keep = new Set(keepIds);
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  function clearFocus(){
    nodeSel.classed('dim', false);
    linkSel.classed('dim', false);
  }

  // ----- Satellites (spiral) -----
  let currentTag = null;

  function clearSatellites(){
    currentTag = null;
    satLayer.selectAll('*').remove();
  }

  function spiralOffsets(n){
    const out = [];
    for (let i=0;i<n;i++){
      const r = spiralStartR + i*spiralStepR;
      const t = i*spiralStepTheta;
      out.push({ _xoff: r*Math.cos(t), _yoff: r*Math.sin(t) });
    }
    return out;
  }

  // Sidebar pulse list (click to open)
  function renderPulseList(tagId, pulses){
    if (!pulses.length) { setSidebarHTML(''); return; }
    const items = pulses.map(p => {
      const label = p.date ? p.date.slice(2,10) : (p.title || p.id || 'Pulse');
      const title = p.title || p.id || '';
      const aClass = `pill ${ageClass(p)}`;
      return `<li data-id="${esc(p.id||p.title||'')}" title="${esc(title)}">
                <span class="${aClass}"></span>
                <span class="ellipsis">${esc(label)} — ${esc(title)}</span>
              </li>`;
    }).join('');
    setSidebarHTML(
      `<div class="listWrap">
         <div class="listHead">Pulses for <strong>${esc(tagId)}</strong></div>
         <ul class="pulseList">${items}</ul>
       </div>`
    );
    // attach click handlers
    sidebar.querySelectorAll('.pulseList li').forEach(li=>{
      li.addEventListener('click', ()=>{
        const id = li.getAttribute('data-id');
        const p = pulses.find(x => (x.id||x.title||'') === id);
        if (p) showPulseDetails(p);
      });
    });
  }

  function onTagClick(tagId){
    currentTag = tagId;

    // Clear satellites and sidebar (you asked the last pulse not to linger)
    clearSatellites();
    clearSidebar();

    // dim to neighbors of tagId (+ itself)
    const neighbors = new Set([tagId]);
    links.forEach(l => {
      if (l.source.id===tagId) neighbors.add(l.target.id);
      if (l.target.id===tagId) neighbors.add(l.source.id);
    });
    setFocus(neighbors);

    const host = idToNode.get(tagId);
    if (!host) return;

    const pulses = safeArray(DATA.pulsesByTag?.[tagId]);
    if (!pulses.length) return;

    // Draw satellites
    const offs = spiralOffsets(pulses.length);
    const g = satLayer.selectAll('g.satellite')
      .data(pulses.map((p,i)=>({...p, host, ...offs[i]})), d => d.id || d.title || (d.date||'') );

    const enter = g.enter().append('g').attr('class','satellite');

    enter.append('circle')
      .attr('r', satDot)
      .attr('class', d => ageClass(d));

    enter.append('text')
      .attr('y', -9)
      .attr('text-anchor','middle')
      .attr('font-size', 9)
      .attr('fill', '#a3b3c7')
      .text(d => d.date ? d.date.slice(2,10) : '');

    enter.on('click', (ev,d) => { ev.stopPropagation(); showPulseDetails(d); });

    // Also list the pulses in the sidebar (one-liners)
    renderPulseList(tagId, pulses);

    sim.alpha(0.45).restart();
  }

  // ----- Pulse details -----
  function renderLinksBlock(label, items){
    if (!items?.length) return '';
    const norm = items.map(u => typeof u==='string' ? {title:u, url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
    let html = `<div style="margin-top:12px"><strong>${label}</strong><ul style="padding-left:18px; margin:6px 0 0 0">`;
    for (const it of norm){
      const title = it.title || it.url;
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
    html += renderLinksBlock('Papers', p.papers);
    html += renderLinksBlock('Podcasts', p.podcasts);
    setSidebarHTML(html);
  }

  // ----- Search -----
  function applyFilter(q){
    const s = (q||'').trim().toLowerCase();
    if (!s){ clearFocus(); return; }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
    setFocus(keep);
  }
  if (searchInput) searchInput.addEventListener('input', e => applyFilter(e.target.value));

  // Start with an empty sidebar (your preference)
  clearSidebar();
})();
