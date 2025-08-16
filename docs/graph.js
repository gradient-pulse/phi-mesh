/* docs/graph.js
   Renders the force graph + age-colored pulse satellites on tag click.
   Expects window.PHI_DATA with:
     - nodes: [{id, centrality?}]
     - links: [{source, target}]
     - tagDescriptions: { [tag]: string }
     - pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts? }] }
     - meta: { builtAt? }
*/

(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // ------- DOM -------
  const svg      = d3.select('#graph');
  const tooltip  = d3.select('#tooltip');
  const sidebar  = document.getElementById('sidebar');
  const searchEl = document.getElementById('search');

  // ------- helpers -------
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));
  const A = x => Array.isArray(x) ? x : (x ? [x] : []);
  const tagDesc = (t) => (DATA.tagDescriptions && DATA.tagDescriptions[t]) || '';
  const pulsesFor = (t) => (DATA.pulsesByTag && DATA.pulsesByTag[t]) || [];

  // Age → color class
  function ageClass(days) {
    if (days == null) return 'pulse-old';
    if (days <= 14)   return 'pulse-very-new';
    if (days <= 45)   return 'pulse-new';
    if (days <= 120)  return 'pulse-mid';
    if (days <= 270)  return 'pulse-old';
    return 'pulse-very-old';
  }

  // ------- sizing / geometry -------
  const W = 1280, H = 860;
  svg.attr('viewBox', `0 0 ${W} ${H}`);

  // Node size by “importance”
  const deg = {};
  (DATA.links||[]).forEach(({source,target})=>{
    deg[source] = (deg[source]||0)+1;
    deg[target] = (deg[target]||0)+1;
  });
  const rx = d => 6 + Math.sqrt((d.centrality||0) * 900);
  const ry = d => 4 + Math.sqrt((d.centrality||0) * 450);

  // ------- zoom / layers -------
  const root = svg.append('g');
  const linkLayer      = root.append('g').attr('class','links');
  const nodeLayer      = root.append('g').attr('class','nodes');
  const satelliteLayer = root.append('g').attr('class','satellites');

  svg.call(
    d3.zoom()
      .scaleExtent([0.25, 4])
      .on('zoom', (ev)=> root.attr('transform', ev.transform))
  );

  // ------- data plumbing for simulation -------
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = (DATA.links||[])
    .map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    }))
    .filter(l => l.source && l.target);

  // Spread a touch more (less density) vs earlier
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(0.35))
    .force('charge', d3.forceManyBody().strength(-420))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide().radius(d => Math.max(rx(d),ry(d))+4));

  // ------- draw links / nodes -------
  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d => d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');
      g.append('ellipse').attr('rx', rx).attr('ry', ry);
      g.append('text')
        .attr('y', d => ry(d) + 12)
        .attr('text-anchor','middle')
        .text(d => d.id);
      g.on('mouseover', (ev,d)=> showTagTip(ev, d.id))
       .on('mousemove', (ev)=> moveTip(ev))
       .on('mouseout', hideTip)
       .on('click', (_ev,d)=> onTagClick(d.id));
      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites following their host
    satelliteLayer.selectAll('g.satellite')
      .attr('transform', d => {
        const a = d._angle, r = d._radius, {x,y} = d.host;
        return `translate(${x + r*Math.cos(a)}, ${y + r*Math.sin(a)})`;
      });
  });

  // ------- tooltip -------
  function showTagTip(ev, tag) {
    const desc = tagDesc(tag);
    tooltip
      .html(`<div style="font-weight:700;margin-bottom:2px">${esc(tag)}</div>
             ${desc ? `<div style="opacity:.9">${esc(desc)}</div>` :
                      `<div style="opacity:.7">Click to reveal pulse satellites.</div>`}`)
      .style('display','block');
    moveTip(ev);
  }
  function moveTip(ev) {
    const pad = 12;
    tooltip
      .style('left', (window.scrollX + ev.pageX + pad) + 'px')
      .style('top',  (window.scrollY + ev.pageY + pad) + 'px');
  }
  function hideTip() {
    tooltip.style('display','none');
  }

  // ------- sidebar -------
  function showTagDetails(tag) {
    const desc = tagDesc(tag);
    const p = pulsesFor(tag);
    let html = `<h2>${esc(tag)}</h2>`;
    if (desc) html += `<div style="white-space:pre-wrap;margin:.25rem 0 1rem 0">${esc(desc)}</div>`;
    html += `<div class="chip">degree ${deg[tag]||0}</div>`;
    const centrality = idToNode.get(tag)?.centrality ?? 0;
    html += `<div class="chip">centrality ${Number(centrality).toFixed(2)}</div>`;

    // Only list pulses after you click a satellite (per your preference),
    // so here we keep it minimal.
    sidebar.innerHTML = html;
  }

  function showPulseDetails(pulse) {
    let html = `<h2>${esc(pulse.title || pulse.id || 'Pulse')}`;
    if (pulse.date) html += ` <span class="muted">(${esc(pulse.date)})</span>`;
    html += `</h2>`;
    if (pulse.summary) {
      html += `<div style="white-space:pre-wrap;margin:.25rem 0 1rem 0">${esc(pulse.summary)}</div>`;
    }
    const papers = A(pulse.papers);
    const pods   = A(pulse.podcasts);
    if (papers.length) {
      html += `<div><strong>Papers</strong><ul>`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (pods.length) {
      html += `<div style="margin-top:8px"><strong>Podcasts</strong><ul>`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    sidebar.innerHTML = html;
  }

  // ------- satellites (keeps main graph visible) -------
  const RING_R = 110;
  const DOT_R  = 4.6;

  function onTagClick(tag) {
    showTagDetails(tag);
    satelliteLayer.selectAll('*').remove();

    const host = idToNode.get(tag);
    if (!host) return;

    // Sort newest (smallest ageDays) first
    const pulses = [...pulsesFor(tag)].sort((a,b)=> (a.ageDays??9e9) - (b.ageDays??9e9));
    if (!pulses.length) return;

    // If many pulses, use 2 rings
    const firstRingCount  = Math.min(28, pulses.length);
    const secondRingCount = Math.max(0, pulses.length - firstRingCount);

    const TWO_PI = Math.PI * 2;
    const lay = [];
    for (let i=0;i<firstRingCount;i++){
      lay.push({ idx:i, total:firstRingCount, r:RING_R });
    }
    for (let j=0;j<secondRingCount;j++){
      lay.push({ idx:j, total:secondRingCount, r:RING_R+46 });
    }

    const sat = satelliteLayer.selectAll('g.satellite')
      .data(pulses.map((p, i) => {
        const ring = lay[i] || {idx:i,total:pulses.length,r:RING_R};
        return {
          ...p,
          host,
          _radius: ring.r,
          _angle: (ring.idx / ring.total) * TWO_PI
        };
      }), d => d.id || `${tag}:${d.date || Math.random()}`);

    const g = sat.enter().append('g').attr('class','satellite');
    g.append('circle')
      .attr('r', DOT_R)
      .attr('class', d => ageClass(d.ageDays));
    g.append('title').text(d => `${d.title || d.id || 'pulse'}${d.date ? ` — ${d.date}` : ''}`);
    g.on('click', (_ev,d)=> showPulseDetails(d));

    // kick the sim a bit so the ring settles
    sim.alpha(0.5).restart();
  }

  // ------- search filter -------
  const norm = s => (s||'').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();

  function applyFilter(q){
    const query = norm(q);
    if(!query){
      nodeSel.classed('dim', false);
      linkSel.classed('on', false);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n => norm(n.id).includes(query)).map(n => n.id));
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('on', d => keep.has(d.source.id) && keep.has(d.target.id));
  }
  searchEl.addEventListener('input', e => applyFilter(e.target.value));

  // initial sidebar message
  sidebar.innerHTML = `<div class="muted">Pick a tag to see details here.</div>`;
})();
