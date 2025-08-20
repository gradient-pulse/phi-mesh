/* docs/graph.js — RGP Looking Glass
   Expects window.PHI_DATA with:
   - nodes: [{id, centrality?, degree?}], links: [{source, target}]
   - tagDescriptions: { [tag]: "..." }  (or {tags:{...}})
   - pulsesByTag: { [tag]: [{ id?, title?, date?, summary?, ageDays?, papers?, podcasts? }] }
   DOM:
   - <svg id="graph">, <input id="search">, sidebar container #details (or #tag-meta/#sidebar-content)
   Uses D3 v7.
*/
(function () {
  const DATA = window.PHI_DATA || {nodes:[], links:[]};
  const tagDescMap = (DATA.tagDescriptions && (DATA.tagDescriptions.tags || DATA.tagDescriptions)) || {};
  const pulsesByTag = DATA.pulsesByTag || DATA.tagToPulses || {};
  const svg = d3.select('#graph');
  const searchEl = document.getElementById('search') || document.getElementById('tag-search');
  const detailsEl =
    document.getElementById('details') ||
    document.getElementById('tag-meta') ||
    document.getElementById('sidebar-content');

  // Ensure a tooltip element exists
  let tooltip = d3.select('#tooltip');
  if (tooltip.empty()) {
    tooltip = d3.select('body').append('div').attr('id','tooltip');
  }
  tooltip
    .style('position','absolute')
    .style('pointer-events','none')
    .style('z-index','9999')
    .style('background','#0f141c')
    .style('border','1px solid #2a3444')
    .style('border-radius','8px')
    .style('padding','8px 10px')
    .style('color','#e6edf6')
    .style('font-size','13px')
    .style('box-shadow','0 8px 28px rgba(0,0,0,.45)')
    .style('display','none')
    .style('max-width','320px');

  // Helpers
  const esc = s => String(s||'').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const trunc = (s, n=72) => (s && s.length>n ? s.slice(0,n-1)+'…' : s||'');
  const byId = new Map((DATA.nodes||[]).map(n => [n.id, n]));
  const neighbors = new Map((DATA.nodes||[]).map(n => [n.id, new Set()]));
  (DATA.links||[]).forEach(l=>{
    const s = typeof l.source === 'string' ? l.source : l.source?.id;
    const t = typeof l.target === 'string' ? l.target : l.target?.id;
    if(!s || !t) return;
    neighbors.get(s)?.add(t);
    neighbors.get(t)?.add(s);
  });

  // Age → class bucket (for satellites)
  function ageClass(ageDays) {
    if (ageDays == null) return 'age-old';
    if (ageDays <= 14)  return 'age-very-new';
    if (ageDays <= 45)  return 'age-new';
    if (ageDays <= 120) return 'age-mid';
    if (ageDays <= 270) return 'age-old';
    return 'age-very-old';
  }

  // Size
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  // Layers
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');
  const satLayer  = root.append('g').attr('class','satellites');

  // Zoom/pan
  const zoom = d3.zoom().scaleExtent([0.3, 4]).on('zoom', (ev)=> root.attr('transform', ev.transform));
  svg.call(zoom);

  // Simulation
  const nodes = DATA.nodes.map(d => ({...d}));
  const links = (DATA.links||[]).map(l => ({
    source: typeof l.source === 'string' ? l.source : l.source?.id,
    target: typeof l.target === 'string' ? l.target : l.target?.id
  })).filter(l=>l.source && l.target);

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(0.25))
    .force('charge', d3.forceManyBody().strength(-380))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(d => 10 + Math.sqrt((d.centrality||0)*900)));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('stroke','#3a4153')
    .attr('stroke-opacity',0.35)
    .attr('stroke-width',1.1);

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node').style('cursor','pointer');
      // Ellipse size feels better than circles for labels
      const rx = d => 10 + Math.sqrt((d.centrality||0)*900);
      const ry = d => 6  + Math.sqrt((d.centrality||0)*450);
      g.append('ellipse')
        .attr('rx', rx)
        .attr('ry', ry)
        .attr('fill','#6fc1ff')
        .attr('stroke','#05263a')
        .attr('stroke-width',1.2);
      g.append('text')
        .attr('y', d => ry(d)+12)
        .attr('text-anchor','middle')
        .attr('font-size',11)
        .attr('fill','#e8eef8')
        .text(d => d.id);

      // Hover → tooltip with description
      g.on('mouseover', (event,d)=> {
          const desc = tagDescMap[d.id] || '';
          const html = `
            <div style="font-weight:700;margin-bottom:4px">${esc(d.id)}</div>
            ${desc ? `<div style="opacity:.95">${esc(desc)}</div>` : `<div style="opacity:.7">—</div>`}
            <div style="margin-top:6px;opacity:.8;font-size:12px"><em>Click to reveal pulse satellites</em></div>
          `;
          tooltip.html(html).style('display','block');
          moveTooltip(event);
      })
      .on('mousemove', moveTooltip)
      .on('mouseout', () => tooltip.style('display','none'))
      .on('click', (_,d) => focusTag(d.id));

      return g;
    });

  sim.on('tick', ()=>{
    linkSel
      .attr('x1', d=> byId.get(d.source)?.x ?? d.source.x)
      .attr('y1', d=> byId.get(d.source)?.y ?? d.source.y)
      .attr('x2', d=> byId.get(d.target)?.x ?? d.target.x)
      .attr('y2', d=> byId.get(d.target)?.y ?? d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // Reposition satellites around their host
    satLayer.selectAll('g.sat')
      .attr('transform', d => {
        const host = byId.get(d.hostId);
        if(!host) return null;
        const x = host.x + d._radius * Math.cos(d._angle);
        const y = host.y + d._radius * Math.sin(d._angle);
        return `translate(${x},${y})`;
      });
  });

  // Tooltip positioning that ignores SVG transforms
  function moveTooltip(ev) {
    // Use page coordinates so zoom/pan don’t throw us off
    const x = (ev.pageX || 0) + 12;
    const y = (ev.pageY || 0) + 12;
    tooltip.style('left', x+'px').style('top', y+'px');
  }

  // Focus logic (dim non-neighbors), plus satellites
  let focusedTag = null;
  function focusTag(tagId){
    focusedTag = tagId;

    const keep = new Set([tagId, ...(neighbors.get(tagId) || [])]);
    nodeSel.classed('dim', d=>!keep.has(d.id));
    linkSel.attr('stroke-opacity', d => (keep.has(d.source) && keep.has(d.target)) ? 0.35 : 0.08);

    // Satellites
    renderSatellites(tagId);

    // Sidebar: prompt to click a pulse (do NOT dump all resources)
    showHint(`Click a pulse to see its summary, papers & podcasts.`);
    sim.alpha(0.25).restart();
  }

  function clearFocus(){
    focusedTag = null;
    nodeSel.classed('dim', false);
    linkSel.attr('stroke-opacity', 0.35);
    satLayer.selectAll('*').remove();
    showHint(`Pick a tag to see details here.`);
    sim.alpha(0.12).restart();
  }

  svg.on('click', (ev)=>{
    // Clicked on empty space?
    if (ev.target === svg.node()) {
      clearFocus();
      tooltip.style('display','none');
    }
  });

  // Satellites: arrange pulses in concentric rings and color by age
  function renderSatellites(tagId){
    satLayer.selectAll('*').remove();

    const host = byId.get(tagId);
    if(!host) return;

    const pulses = (pulsesByTag[tagId] || []).slice();
    if(!pulses.length) return;

    // Concentric rings: up to 24 per ring
    const perRing = 24;
    const baseR = 85;
    const stepR = 28;

    const satData = [];
    for (let i=0;i<pulses.length;i++){
      const ring = Math.floor(i / perRing);
      const idxInRing = i % perRing;
      const inThisRing = Math.min(perRing, pulses.length - ring*perRing);
      const angle = (idxInRing / inThisRing) * Math.PI * 2;
      satData.push({
        pulse: pulses[i],
        hostId: tagId,
        _angle: angle,
        _radius: baseR + ring*stepR
      });
    }

    const sat = satLayer.selectAll('g.sat')
      .data(satData, d => (d.pulse.id || d.pulse.title || `${d.pulse.date||''}:${d._angle}`))
      .join(enter => {
        const g = enter.append('g').attr('class','sat');
        g.append('circle')
          .attr('r', 5)
          .attr('class', d => ageClass(d.pulse.ageDays))
          .attr('stroke','#0b1119')
          .attr('stroke-width',1.4)
          .style('filter','drop-shadow(0 0 1px rgba(0,0,0,.35))');
        // small invisible hit area for easier clicking
        g.append('circle').attr('r', 10).attr('fill','transparent');

        g.on('click', (ev,d) => {
          ev.stopPropagation();
          // visual select
          satLayer.selectAll('g.sat circle:first-child').attr('r', 5);
          d3.select(g.node()).select('circle').attr('r', 7);
          // sidebar details
          showPulse(d.pulse);
        });
        return g;
      });
  }

  // Sidebar rendering
  function showHint(text){
    if(!detailsEl) return;
    detailsEl.innerHTML = `<div class="muted" style="color:#9fb0c3;font-size:13px">${esc(text||'')}</div>`;
    // prevent horizontal scrollbar
    detailsEl.style.overflowX = 'hidden';
    detailsEl.style.wordBreak = 'break-word';
    detailsEl.style.overflowWrap = 'anywhere';
  }

  function showPulse(p){
    if(!detailsEl || !p) return;
    const papers = (p.papers||[]).map(item => {
      if (typeof item === 'string') return {title:'', url:item};
      return {title:item.title||'', url:item.url||item.doi||''};
    }).filter(x=>x.url);
    const pods = (p.podcasts||[]).map(u => (typeof u==='string'? u : (u.url||''))).filter(Boolean);

    let html = '';
    html += `<h2 style="margin:0 0 6px 0;font-size:16px">${esc(p.title || p.id || 'Pulse')}</h2>`;
    if (p.date) html += `<div class="muted" style="color:#9fb0c3;margin-bottom:8px">${esc(p.date)}</div>`;
    if (p.summary) {
      html += `<div style="white-space:pre-wrap;margin:8px 0 12px 0">${esc(p.summary)}</div>`;
    }
    if (papers.length){
      html += `<div style="margin-top:8px"><strong>Papers</strong><ul style="margin:.35rem 0 .75rem 1.1rem">`;
      for (const {title,url} of papers){
        const label = title ? trunc(title, 88) : trunc(url.replace(/^https?:\/\//,''), 88);
        html += `<li style="margin:.15rem 0"><a style="color:#7dc1ff;text-decoration:none" href="${url}" target="_blank" rel="noopener">${esc(label)}</a></li>`;
      }
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div style="margin-top:4px"><strong>Podcasts</strong><ul style="margin:.35rem 0 .75rem 1.1rem">`;
      for (const u of pods){
        const label = trunc(String(u).replace(/^https?:\/\//,''), 88);
        html += `<li style="margin:.15rem 0"><a style="color:#7dc1ff;text-decoration:none" href="${u}" target="_blank" rel="noopener">${esc(label)}</a></li>`;
      }
      html += `</ul></div>`;
    }

    detailsEl.innerHTML = html;
    // keep sidebar tidy
    detailsEl.style.overflowX = 'hidden';
    detailsEl.style.wordBreak = 'break-word';
    detailsEl.style.overflowWrap = 'anywhere';
  }

  // Search (substring, case/diacritic-insensitive)
  if (searchEl){
    const normalize = s => (s||'').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
    let t=null;
    const run = () => {
      const q = normalize(searchEl.value);
      if(!q){
        nodeSel.classed('dim', false);
        linkSel.attr('stroke-opacity', 0.35);
        return;
      }
      const keep = new Set(nodes.filter(n => normalize(n.id).includes(q)).map(n=>n.id));
      nodeSel.classed('dim', d=>!keep.has(d.id));
      linkSel.attr('stroke-opacity', d => (keep.has(d.source) && keep.has(d.target)) ? 0.35 : 0.05);
    };
    searchEl.addEventListener('input', ()=>{ if(t) clearTimeout(t); t=setTimeout(run, 80); });
  }

  // Initial hint
  showHint('Pick a tag to see details here.');
})();
