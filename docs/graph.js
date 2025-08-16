/* Phi-Mesh interactive tag map
 * Expects window.PHI_DATA from docs/data.js:
 *  - nodes: [{id, centrality?}], links: [{source, target}]
 *  - tagDescriptions: { [tag]: "..." }
 *  - tagResources: { [tag]: {papers:[], podcasts:[]} }  (optional, not shown until pulse clicked)
 *  - pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts? }] }
 */

(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // ----- DOM -----
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const detailsEl = document.getElementById('details');
  const searchEl = document.getElementById('search');

  // ----- Sizing -----
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  // ----- Layers -----
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class', 'links');
  const nodeLayer = root.append('g').attr('class', 'nodes');
  const satLayer  = root.append('g').attr('class', 'satellites');

  // ----- Zoom / Pan -----
  svg.call(
    d3.zoom()
      .scaleExtent([0.3, 4])
      .on('zoom', (e) => root.attr('transform', e.transform))
  );

  // ----- Graph data -----
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links
    .map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    }))
    .filter(l => l.source && l.target);

  // ----- Helpers -----
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const rx = d => 6 + Math.sqrt(clamp(d.centrality ?? 0, 0, 1) * 900);
  const ry = d => 4 + Math.sqrt(clamp(d.centrality ?? 0, 0, 1) * 450);

  function ageClass(age) {
    if (age == null) return 'age-old';
    if (age <= 14)  return 'age-very-new';
    if (age <= 45)  return 'age-new';
    if (age <= 120) return 'age-mid';
    if (age <= 270) return 'age-old';
    return 'age-very-old';
  }
  function esc(s) {
    return String(s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // ----- Simulation (tuned for less density & clearer links) -----
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(95).strength(0.25))
    .force('charge', d3.forceManyBody().strength(-360))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collide', d3.forceCollide().radius(d => Math.max(rx(d), ry(d)) + 8));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');
      g.append('ellipse')
        .attr('rx', rx)
        .attr('ry', ry);
      g.append('text')
        .attr('y', d => ry(d)+12)
        .attr('text-anchor','middle')
        .text(d => d.id);

      // interactions
      g.on('mouseover', (event, d) => {
          const desc = (DATA.tagDescriptions && DATA.tagDescriptions[d.id]) || '';
          tooltip.select('.t1').text(d.id);
          tooltip.select('.t2').text(desc || '—');
          tooltip.style('display','block');
          moveTooltip(event);
        })
        .on('mousemove', moveTooltip)
        .on('mouseout', () => tooltip.style('display','none'))
        .on('click', (_e, d) => onTagClick(d.id));

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites glued around host on every tick
    satLayer.selectAll('g.satellite')
      .attr('transform', d => {
        const ang = d._angle, r = d._radius;
        const x = d.host.x + r * Math.cos(ang);
        const y = d.host.y + r * Math.sin(ang);
        return `translate(${x},${y})`;
      });
  });

  function moveTooltip(e){
    const pad=12;
    tooltip.style('left', (e.clientX+pad)+'px').style('top',(e.clientY+pad)+'px');
  }

  // ----- Sidebar rendering -----
  function showPulseDetails(p){
    let html = `<h3 style="margin:0 0 6px 0">${esc(p.title || p.id || 'Pulse')}</h3>`;
    if (p.date) html += `<div class="muted" style="margin:-2px 0 8px 0">${esc(p.date)}</div>`;
    if (p.summary) html += `<div style="white-space:pre-wrap">${esc(p.summary)}</div>`;

    const papers = Array.isArray(p.papers) ? p.papers : [];
    const pods   = Array.isArray(p.podcasts) ? p.podcasts : [];

    if (papers.length){
      html += `<h3 style="margin:12px 0 6px 0">Papers</h3><ul>`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul>`;
    }
    if (pods.length){
      html += `<h3 style="margin:12px 0 6px 0">Podcasts</h3><ul>`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul>`;
    }
    detailsEl.innerHTML = html;
  }
  function clearDetails(){
    detailsEl.innerHTML = `<div class="empty">Click a pulse to see its summary, papers & podcasts.</div>`;
  }
  clearDetails();

  // ----- Satellites -----
  function onTagClick(tagId){
    clearDetails();                 // per spec: nothing until a pulse is clicked
    satLayer.selectAll('*').remove();

    const host = idToNode.get(tagId);
    if (!host) return;

    const pulses = (DATA.pulsesByTag && DATA.pulsesByTag[tagId]) || [];
    if (!pulses.length) return;

    // sort newest first
    const sorted = [...pulses].sort((a,b) => (a.ageDays??99999) - (b.ageDays??99999));

    // layout: if many, spiral; else 1–2 rings (new inner)
    const n = sorted.length;
    const innerMax = Math.min(36, n);
    const outerMax = Math.min(72, Math.max(0, n - innerMax));
    const innerR = 90, outerR = 130;
    const satSize = 5;

    let layoutPts = [];
    if (n > 72){
      // spiral from center outward (new→old)
      const a0 = Math.PI/6;
      const k = 7; // growth
      for (let i=0;i<n;i++){
        const a = a0 + i*0.38;
        const r = innerR + k*i*0.65;
        layoutPts.push({angle:a, radius:r});
      }
    } else {
      // two rings
      for (let i=0;i<innerMax;i++){
        layoutPts.push({angle:(i/innerMax)*Math.PI*2, radius:innerR});
      }
      for (let j=0;j<outerMax;j++){
        layoutPts.push({angle:(j/Math.max(1,outerMax))*Math.PI*2 + 0.12, radius:outerR});
      }
    }

    const sat = satLayer.selectAll('g.satellite')
      .data(sorted.map((p,i)=>({ ...p, host, _angle:layoutPts[i].angle, _radius:layoutPts[i].radius })), d=>d.id || d.title || `${tagId}:${d.date || i}`)
      .join(enter=>{
        const g = enter.append('g').attr('class','satellite');
        g.append('circle')
          .attr('r', satSize)
          .attr('class', d => ageClass(d.ageDays));
        g.append('title').text(d => `${d.title || d.id || 'pulse'}${d.date?` — ${d.date}`:''}`);
        g.on('click', (_e, d) => showPulseDetails(d));
        return g;
      });

    // nudge simulation so satellites settle in position
    sim.alpha(0.5).restart();
  }

  // ----- Search filter -----
  function applyFilter(qraw){
    const q = (qraw||'').trim().toLowerCase();
    if (!q){
      nodeSel.classed('dim', false);
      linkSel.classed('dim', false);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(q)).map(n => n.id));
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  searchEl.addEventListener('input', e => applyFilter(e.target.value));
})();
