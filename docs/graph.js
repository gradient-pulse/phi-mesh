/* docs/graph.js
 * Requires:
 *  - window.PHI_DATA with:
 *      nodes: [{id, centrality?}], links: [{source, target}],
 *      tagDescriptions: { [tag]: "..." },
 *      tagResources: { [tag]: {papers:[], podcasts:[]} },
 *      pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts?, tags? }] }
 *  - DOM elements: #graph (svg), #sidebar-content (div), #tooltip (div), #search (input), #status (div)
 *  - D3 v7 loaded
 */
(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // -------- DOM --------------------------------------------------------------
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const sidebar = document.getElementById('sidebar-content');
  const searchInput = document.getElementById('search');
  const statusEl = document.getElementById('status');

  // defensive: if the svg is missing, bail gracefully
  if (!svg.node()) {
    console.warn('graph.js: #graph not found; aborting render.');
    return;
  }

  // helpers
  const safeArray = (x) => Array.isArray(x) ? x : [];
  const esc = (s) => String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));

  // -------- Sizing / viewBox -------------------------------------------------
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr('viewBox', [0,0,width,height].join(' '));

  // -------- Layers & zoom ----------------------------------------------------
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');
  const satelliteLayer = root.append('g').attr('class','satellites');

  const zoom = d3.zoom()
    .scaleExtent([0.3, 4])
    .on('zoom', (event) => root.attr('transform', event.transform));
  svg.call(zoom);

  // -------- Data prep --------------------------------------------------------
  // Map id -> node object so link endpoints can be dereferenced
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = (DATA.links || [])
    .map(l => ({ source: idToNode.get(l.source) || l.source, target: idToNode.get(l.target) || l.target }))
    .filter(l => l.source && l.target);

  // -------- Simulation -------------------------------------------------------
  const nodeRadius = 6;
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(85).strength(0.7))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(nodeRadius*2.2));

  // links
  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('opacity', 0.35);

  // nodes
  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d => d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');

      // circle receives pointer events
      g.append('circle').attr('r', nodeRadius).style('pointer-events','all');

      g.append('text')
        .attr('x', nodeRadius + 3)
        .attr('y', 3)
        .text(d => d.id);

      // interactions
      g.on('mouseover', (event, d) => showTagTooltip(event, d.id))
       .on('mousemove', (event) => moveTooltip(event))
       .on('mouseout', hideTooltip)
       .on('click', (_e, d) => onTagClick(d.id));

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);

    nodeSel.attr('transform', d => `translate(${d.x},${d.y})`);

    // Reposition satellites to follow the host
    satelliteLayer.selectAll('g.satellite')
      .attr('transform', d => {
        const a = d._angle || 0, r = d._radius || 90;
        const x = d.host.x + r*Math.cos(a);
        const y = d.host.y + r*Math.sin(a);
        return `translate(${x},${y})`;
      });
  });

  // -------- Tooltip ----------------------------------------------------------
  function showTagTooltip(evt, tagId) {
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tagId]) || '';
    const html = `
      <div style="font-weight:600;margin-bottom:4px">${esc(tagId)}</div>
      <div style="white-space:pre-wrap;opacity:.9">${esc(desc || '—')}</div>
      <div style="margin-top:6px;font-size:12px;color:#97a3b6">Click for pulse satellites + sidebar details</div>
    `;
    tooltip.html(html).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad = 12;
    tooltip.style('left', (evt.clientX + pad)+'px')
           .style('top',  (evt.clientY + pad)+'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // -------- Sidebar renders --------------------------------------------------
  function showTagDetails(tagId){
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tagId]) || '';
    const res  = (DATA.tagResources && DATA.tagResources[tagId]) || {};
    const papers = safeArray(res.papers);
    const pods   = safeArray(res.podcasts);

    let html = `<h2 style="margin:0 0 .4rem 0">${esc(tagId)}</h2>`;
    html += `<div style="white-space:pre-wrap;margin:.2rem 0 .8rem 0">${esc(desc || '—')}</div>`;
    if (papers.length){
      html += `<div><strong>Papers</strong><ul>`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div style="margin-top:.5rem"><strong>Podcasts</strong><ul>`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }

    // preview a few recent pulses
    const pulses = safeArray(DATA.pulsesByTag?.[tagId]);
    if (pulses.length){
      const sorted = [...pulses].sort((a,b)=>(a.ageDays??9999)-(b.ageDays??9999)).slice(0,6);
      html += `<div style="margin-top:.7rem"><strong>Recent pulses</strong><ul>`;
      for (const p of sorted){
        const when = p.date ? ` — ${esc(p.date)}` : '';
        html += `<li>${esc(p.title || p.id || 'pulse')}${when}</li>`;
      }
      html += `</ul></div>`;
    }

    sidebar.innerHTML = html;
  }

  function showPulseDetails(p){
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<h2 style="margin:0 0 .4rem 0">${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.2rem 0 .8rem 0">${esc(p.summary)}</div>`;

    const papers = safeArray(p.papers);
    const pods   = safeArray(p.podcasts);
    if (papers.length){
      html += `<div><strong>Papers</strong><ul>`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div style="margin-top:.5rem"><strong>Podcasts</strong><ul>`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (p.tags && p.tags.length){
      html += `<div style="margin-top:.6rem"><strong>Tags</strong><div style="margin-top:4px">`;
      for (const t of p.tags){
        html += `<span style="display:inline-block;background:#1a2233;border:1px solid #2c3950;border-radius:999px;padding:2px 8px;margin:2px;font-size:12px">${esc(t)}</span>`;
      }
      html += `</div></div>`;
    }
    sidebar.innerHTML = html;
  }

  // -------- Satellites (pulses around a tag) --------------------------------
  const satelliteR = 90;
  const satelliteSize = 4.5;
  function ageClass(days){
    if (days == null) return 'age-old';
    if (days <= 14)  return 'age-very-new';
    if (days <= 45)  return 'age-new';
    if (days <= 120) return 'age-mid';
    if (days <= 270) return 'age-old';
    return 'age-very-old';
  }

  function onTagClick(tagId){
    showTagDetails(tagId);

    satelliteLayer.selectAll('*').remove();
    const host = idToNode.get(tagId);
    if (!host) return;

    const pulses = safeArray(DATA.pulsesByTag?.[tagId]);
    if (!pulses.length) return;

    const n = pulses.length;
    const TWO_PI = Math.PI*2;
    const sats = satelliteLayer.selectAll('g.satellite')
      .data(pulses.map((p,i)=>({...p, host, _angle:(i/n)*TWO_PI, _radius:satelliteR})), d => d.id || d.title || `${tagId}:${d.date || i}`);

    const enter = sats.enter().append('g').attr('class','satellite');

    enter.append('circle')
      .attr('r', satelliteSize)
      .attr('class', d => ageClass(d.ageDays));

    // accessible title
    enter.append('title').text(d => `${d.title || d.id || 'pulse'}${d.date ? ` — ${d.date}` : ''}`);

    // small date chip
    enter.append('text')
      .attr('y', -8).attr('text-anchor','middle')
      .attr('font-size', 9).attr('fill','#a3b3c7')
      .text(d => d.date ? d.date.slice(2,10) : '');

    enter.on('click', (ev, d) => {
      ev.stopPropagation?.();
      showPulseDetails(d);
    });

    // kick the sim so the satellites render in the next ticks
    sim.alpha(0.5).restart();
  }

  // -------- Search -----------------------------------------------------------
  function applyFilter(query){
    const q = (query||'').trim().toLowerCase();
    if (!q){
      nodeSel.classed('dim', false).attr('opacity', 1);
      linkSel.attr('opacity', 0.35);
      statusEl && (statusEl.textContent = `tags: ${DATA.nodes.length}`);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n => (n.id||'').toLowerCase().includes(q)).map(n => n.id));
    nodeSel.attr('opacity', d => keep.has(d.id) ? 1 : 0.12)
           .classed('dim', d => !keep.has(d.id));
    linkSel.attr('opacity', d => (keep.has(d.source.id) && keep.has(d.target.id)) ? 0.35 : 0.06);
    statusEl && (statusEl.textContent = `filtered: ${keep.size}/${DATA.nodes.length}`);
  }
  if (searchInput){
    let t=null;
    searchInput.addEventListener('input', e => {
      if (t) clearTimeout(t);
      t = setTimeout(() => applyFilter(e.target.value), 80);
    });
  }

  // -------- Initial sidebar text --------------------------------------------
  sidebar.innerHTML = `<div class="muted">Pick a tag to see details. Hover tags for descriptions. Click tags to reveal pulse satellites (age-colored).</div>`;
  statusEl && (statusEl.textContent = `tags: ${DATA.nodes.length}`);
})();

// Back-compat entry point – presence is used to sanity check that the file loaded.
function renderTagMap(){ /* bootstraps on load */ }
