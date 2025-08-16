/* docs/graph.js (one-sidebar edition)
 * Expects window.PHI_DATA with:
 *  - nodes: [{id, centrality?}], links: [{source, target}]
 *  - tagDescriptions: { [tag]: "..." }
 *  - tagResources: { [tag]: { papers: [url], podcasts: [url] } }
 *  - pulsesByTag: { [tag]: [{ id,title?,date?,ageDays?,summary?,papers?,podcasts?,tags? }] }
 */

(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // ---------- DOM ----------
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const searchInput = document.getElementById('search');
  const detailsEl = document.getElementById('details');
  const statusEl = document.getElementById('status');

  // ---------- helpers ----------
  const esc = (s) => String(s || '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
  const safeArray = (x) => Array.isArray(x) ? x : [];

  function ageClass(ageDays) {
    if (ageDays == null) return 'age-old';
    if (ageDays <= 14) return 'age-very-new';
    if (ageDays <= 45) return 'age-new';
    if (ageDays <= 120) return 'age-mid';
    if (ageDays <= 270) return 'age-old';
    return 'age-very-old';
  }

  // ---------- sizing / zoom ----------
  const width = svg.node().clientWidth || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr('viewBox', [0, 0, width, height].join(' '));

  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class', 'links');
  const nodeLayer = root.append('g').attr('class', 'nodes');
  const satelliteLayer = root.append('g').attr('class', 'satellites');

  svg.call(
    d3.zoom().scaleExtent([0.3, 4]).on('zoom', (e)=> root.attr('transform', e.transform))
  );

  // ---------- data wrangle ----------
  const nodes = DATA.nodes.map(d => ({ id: d.id, centrality: +d.centrality || 0 }));
  const idToNode = new Map(nodes.map(n => [n.id, n]));
  const links = (DATA.links || [])
    .map(l => ({ source: idToNode.get(l.source) || l.source, target: idToNode.get(l.target) || l.target }))
    .filter(l => l.source && l.target);

  // ---------- force sim ----------
  const nodeRadius = 6;
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(0.6))
    .force('charge', d3.forceManyBody().strength(-260))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(nodeRadius * 2.4));

  const linkSel = linkLayer.selectAll('line').data(links).join('line').attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(nodes, d=>d.id)
    .join(enter=>{
      const g = enter.append('g').attr('class','node');
      g.append('circle').attr('r', nodeRadius);
      g.append('text').attr('x', nodeRadius + 3).attr('y', 3).text(d=>d.id);

      g.on('mouseover', (evt,d)=> showTagTooltip(evt, d.id))
       .on('mousemove', (evt)=> moveTooltip(evt))
       .on('mouseout', hideTooltip)
       .on('click', (_evt,d)=> onTagClick(d.id));
      return g;
    });

  sim.on('tick', ()=>{
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites anchored around their host
    satelliteLayer.selectAll('g.satellite')
      .attr('transform', d=>{
        const angle = d._angle || 0, r = d._radius || 90;
        const x = d.host.x + r * Math.cos(angle);
        const y = d.host.y + r * Math.sin(angle);
        return `translate(${x},${y})`;
      });
  });

  // ---------- tooltip ----------
  function showTagTooltip(evt, tagId){
    const desc = DATA.tagDescriptions?.[tagId] || '';
    tooltip.html(
      `<div style="font-weight:600;margin-bottom:4px">${esc(tagId)}</div>
       <div style="white-space:pre-wrap;opacity:.9">${esc(desc || '—')}</div>
       <div style="margin-top:6px;font-size:12px;color:#97a3b6">Click to reveal pulse satellites</div>`
    ).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad = 12;
    const x = (evt.pageX ?? evt.clientX) + pad;
    const y = (evt.pageY ?? evt.clientY) + pad;
    tooltip.style('left', x + 'px').style('top', y + 'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ---------- sidebar rendering ----------
  function showHint(){
    detailsEl.innerHTML =
      `<div class="muted" style="margin-top:12px">
         Pick a tag to show pulse satellites, then click a pulse to see details here.
       </div>`;
  }

  function showPulseDetails(p){
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<h3 style="margin:.2rem 0 .3rem 0">${esc(p.title || p.id || 'Pulse')}${when}</h3>`;
    if (p.summary) {
      html += `<div style="white-space:pre-wrap;margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;
    }
    const papers = safeArray(p.papers), pods = safeArray(p.podcasts);
    if (papers.length){
      html += `<div><strong>Papers</strong><ul style="margin:.4rem 0 .8rem 1rem">`;
      for (const u of papers) html += `<li><a target="_blank" rel="noopener" href="${u}">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div><strong>Podcasts</strong><ul style="margin:.4rem 0 .8rem 1rem">`;
      for (const u of pods) html += `<li><a target="_blank" rel="noopener" href="${u}">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (p.tags?.length){
      html += `<div style="margin-top:.3rem"><strong>Tags</strong><div style="margin-top:.3rem">`;
      for (const t of p.tags) html += `<span class="pill">${esc(t)}</span>`;
      html += `</div></div>`;
    }
    detailsEl.innerHTML = html;
  }

  // ---------- satellites ----------
  let currentTag = null;
  function onTagClick(tagId){
    currentTag = tagId;
    // clear previous satellites
    satelliteLayer.selectAll('*').remove();

    const host = idToNode.get(tagId);
    if (!host) { showHint(); return; }

    const list = safeArray(DATA.pulsesByTag?.[tagId]);
    if (!list.length){
      detailsEl.innerHTML =
        `<div style="margin-top:8px"><strong>${esc(tagId)}</strong></div>
         <div class="muted" style="margin-top:6px">No pulses recorded for this tag yet.</div>`;
      return;
    }

    const n = list.length, TWO_PI = Math.PI * 2;
    const satellites = satelliteLayer.selectAll('g.satellite')
      .data(list.map((p,i)=>({ ...p, host, _angle:(i/n)*TWO_PI, _radius: 90 })), d=>d.id || d.title || `${tagId}:${d.date || Math.random()}`);

    const enter = satellites.enter().append('g').attr('class','satellite');

    enter.append('circle')
      .attr('r', 4.5)
      .attr('class', d => ageClass(d.ageDays))
      .style('pointer-events','all');

    enter.append('title').text(d => `${d.title || d.id || 'pulse'}${d.date ? ` — ${d.date}` : ''}`);

    enter.on('click', (evt, d) => {
      evt.stopPropagation?.();
      showPulseDetails(d);
    });

    // nudge the sim so satellites settle around the tag
    sim.alpha(0.5).restart();

    // also show a tiny header in details so users know what they're looking at
    detailsEl.innerHTML =
      `<div style="margin-top:6px"><strong>${esc(tagId)}</strong></div>
       <div class="muted" style="margin-top:4px">Click a pulse satellite for details.</div>`;
  }

  // ---------- search ----------
  function applyFilter(query){
    const q = (query || '').trim().toLowerCase();
    if (!q){
      nodeSel.classed('dim', false);
      linkSel.classed('dim', false);
      statusEl && (statusEl.textContent = `tags: ${nodes.length}`);
      return;
    }
    const keep = new Set(nodes.filter(n => n.id.toLowerCase().includes(q)).map(n=>n.id));
    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    statusEl && (statusEl.textContent = `filtered: ${keep.size}/${nodes.length}`);
  }
  searchInput?.addEventListener('input', (e)=> applyFilter(e.target.value));

  // ---------- init ----------
  showHint();
  statusEl && (statusEl.textContent = `tags: ${nodes.length}`);
})();
