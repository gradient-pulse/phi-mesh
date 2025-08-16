/* Phi-Mesh tag map behavior (v2)
   Expects window.PHI_DATA with:
   - nodes: [{id, centrality?}]
   - links: [{source, target}]
   - tagDescriptions: { [tag]: "..." }
   - tagResources: { [tag]: {papers:[url], podcasts:[url]} }
   - pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts? }] }
*/
(function () {
  const DATA = window.PHI_DATA || {nodes:[], links:[]};

  // -------- DOM
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const sidebar = document.getElementById('sidebar');
  const search = document.getElementById('search');

  // -------- helpers
  const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const A = x => Array.isArray(x) ? x : (x ? [x] : []);
  const satClass = (days) => {
    if (days == null) return 'age-old';
    if (days <= 14) return 'age-very-new';
    if (days <= 45) return 'age-new';
    if (days <= 120) return 'age-mid';
    if (days <= 270) return 'age-old';
    return 'age-very-old';
  };

  // -------- size & layers
  const W = svg.node().clientWidth || 1200;
  const H = svg.node().clientHeight || 800;
  svg.attr('viewBox', `0 0 ${W} ${H}`);

  const root = svg.append('g');
  const linkLayer = root.append('g');
  const nodeLayer = root.append('g');
  const satLayer  = root.append('g'); // satellites

  // zoom/pan
  svg.call(
    d3.zoom().scaleExtent([0.25, 4]).on('zoom', (ev)=> root.attr('transform', ev.transform))
  );

  // -------- graph data
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links.map(l => ({
    source: idToNode.get(l.source) || l.source,
    target: idToNode.get(l.target) || l.target
  })).filter(l => l.source && l.target);

  // neighbor map for dimming
  const neighbors = new Map(DATA.nodes.map(n => [n.id, new Set()]));
  links.forEach(l => { neighbors.get(l.source.id)?.add(l.target.id); neighbors.get(l.target.id)?.add(l.source.id); });

  // -------- draw
  const link = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('stroke-width', 1.1);

  const node = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d => d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');
      const rx = d => 6 + Math.sqrt((d.centrality||0) * 900);
      const ry = d => 4 + Math.sqrt((d.centrality||0) * 450);
      g.append('ellipse').attr('rx', rx).attr('ry', ry);
      g.append('text')
        .attr('y', d => (ry(d) + 12))
        .attr('text-anchor','middle')
        .text(d => d.id);

      // hover tooltip
      g.on('mousemove', (ev, d) => {
        const desc = (DATA.tagDescriptions && DATA.tagDescriptions[d.id]) || '';
        tooltip.select('.t1').text(d.id);
        tooltip.select('.t2').html(desc ? esc(desc) : '—');
        tooltip.style('display','block');

        // clamp inside viewport
        const pad = 12;
        const vw = window.innerWidth, vh = window.innerHeight;
        let x = ev.clientX + pad, y = ev.clientY + pad;
        const bb = tooltip.node().getBoundingClientRect();
        if (x + bb.width + 8 > vw) x = ev.clientX - bb.width - pad;
        if (y + bb.height + 8 > vh) y = ev.clientY - bb.height - pad;
        tooltip.style('left', x + 'px').style('top', y + 'px');
      }).on('mouseleave', () => tooltip.style('display','none'));

      // click = show satellites + sidebar tag details
      g.on('click', (_ev, d) => revealSatellites(d.id));
      return g;
    });

  // -------- sim (keep it light to avoid freeze)
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(90).strength(.25))
    .force('charge', d3.forceManyBody().strength(-420))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide().radius(d => 8 + Math.sqrt((d.centrality||0)*900)));

  sim.on('tick', () => {
    link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
        .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
    // keep satellites stuck to their host on every tick
    satLayer.selectAll('g.satellite').attr('transform', d => {
      const a = d._angle, r = d._radius, host = d.host;
      const x = host.x + r * Math.cos(a), y = host.y + r * Math.sin(a);
      return `translate(${x},${y})`;
    });
  });

  // -------- sidebar renders
  function renderTagDetails(tagId){
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tagId]) || '';
    const res  = (DATA.tagResources && DATA.tagResources[tagId]) || {};
    const papers = A(res.papers), pods = A(res.podcasts);

    let html = `<h2>${esc(tagId)}</h2>`;
    if (desc) html += `<div style="white-space:pre-wrap;margin:.25rem 0 1rem 0">${esc(desc)}</div>`;

    if (papers.length){ html += `<div><strong>Papers</strong><ul>` + papers.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('') + `</ul></div>`; }
    if (pods.length){   html += `<div style="margin-top:.5rem"><strong>Podcasts</strong><ul>` + pods.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('') + `</ul></div>`; }

    sidebar.innerHTML = html || `<div class="hint">No details yet.</div>`;
  }

  function renderPulseDetails(p){
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}${p.date ? ` <span class="chip">${esc(p.date)}</span>` : ''}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.25rem 0 1rem 0">${esc(p.summary)}</div>`;

    const papers = A(p.papers), pods = A(p.podcasts);
    if (papers.length){ html += `<div><strong>Papers</strong><ul>` + papers.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('') + `</ul></div>`; }
    if (pods.length){   html += `<div style="margin-top:.5rem"><strong>Podcasts</strong><ul>` + pods.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('') + `</ul></div>`; }

    sidebar.innerHTML = html;
  }

  // -------- satellites
  let currentHost = null;

  function revealSatellites(tagId){
    currentHost = idToNode.get(tagId);
    renderTagDetails(tagId);

    // dimming: keep cluster + host prominent
    const neigh = neighbors.get(tagId) || new Set();
    const keep = new Set([tagId, ...neigh]);
    node.classed('dim', d => !keep.has(d.id));
    link.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));

    // remove old
    satLayer.selectAll('*').remove();

    const pulses = (DATA.pulsesByTag && DATA.pulsesByTag[tagId]) || [];
    if (!pulses.length) return;

    // ring geometry (multi-ring if many)
    const perRing = 28; // cap per ring
    const baseR = 95, ringStep = 28;
    const TWO_PI = Math.PI * 2;

    const satData = pulses.map((p, i) => {
      const ring = Math.floor(i / perRing);
      const idx  = i % perRing;
      const nInRing = Math.min(perRing, pulses.length - ring*perRing);
      const angle = (idx / nInRing) * TWO_PI;
      return {
        ...p,
        host: currentHost,
        _angle: angle,
        _radius: baseR + ring * ringStep
      };
    });

    const s = satLayer.selectAll('g.satellite')
      .data(satData, d => d.id || d.title || (d.date ? `${tagId}:${d.date}` : `${tagId}:${Math.random()}`))
      .join(enter => {
        const g = enter.append('g').attr('class','satellite');
        g.append('circle')
          .attr('r', 4.6)
          .attr('class', d => satClass(d.ageDays));
        // small date label (optional)
        g.append('text')
          .attr('y', -8)
          .attr('text-anchor','middle')
          .attr('font-size', 9)
          .attr('fill', '#a8b7cc')
          .text(d => d.date ? d.date.slice(2,10) : '');

        // pulse click -> sidebar
        g.on('click', (_ev, d) => {
          renderPulseDetails(d);
          // prevent graph clickfall-through
          d3.event?.stopPropagation?.();
        });
        return g;
      });

    // nudge simulation slightly so host recenters; but keep layout intact
    sim.alphaTarget(0.12).restart();
    setTimeout(()=>sim.alphaTarget(0), 400);
  }

  // -------- search
  function applyFilter(q){
    const v = (q||'').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
    if (!v){
      node.classed('dim', false);
      link.classed('dim', false);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(v)).map(n=>n.id));
    node.classed('dim', d => !keep.has(d.id));
    link.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  let t=null;
  search.addEventListener('input', e => { if (t) clearTimeout(t); t = setTimeout(()=>applyFilter(e.target.value), 80); });

  // initial sidebar
  sidebar.innerHTML = `<div class="hint">Pick a tag to see details here.</div>`;
})();
