/* docs/graph.js
   One-sidebar version. Tag description tooltips. Pulse satellites on tag click.
   Requires: window.PHI_DATA from docs/data.js and d3 v7.
*/
(() => {
  const DATA = window.PHI_DATA || {nodes:[],links:[]};

  // -------- DOM ----------
  const svg = d3.select('#graph');
  const root = svg.append('g');
  const linkLayer = root.append('g');
  const nodeLayer = root.append('g');
  const satLayer  = root.append('g');
  const tooltip = d3.select('#tooltip');
  const details = document.getElementById('details');
  const search  = document.getElementById('search');

  // -------- config ----------
  const W = svg.node().viewBox.baseVal.width  || 1200;
  const H = svg.node().viewBox.baseVal.height || 800;
  const nodeRxBase = 8, nodeRyBase = 5;
  const linkOpacity = 0.35;

  // Age → class
  function ageClass(days){
    if(days == null) return 'age-old';
    if(days <= 14)  return 'age-very-new';
    if(days <= 45)  return 'age-new';
    if(days <= 120) return 'age-mid';
    if(days <= 270) return 'age-old';
    return 'age-very-old';
  }

  // -------- data prep ----------
  const nodes = (DATA.nodes||[]).map(d => ({id: d.id || d.name, centrality: +d.centrality||0}));
  const idToNode = new Map(nodes.map(n => [n.id, n]));
  const links = (DATA.links||[])
    .map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    }))
    .filter(l => l.source && l.target);

  // neighbors for dimming
  const neigh = new Map(nodes.map(n=>[n.id,new Set]));
  links.forEach(l => {neigh.get(l.source.id)?.add(l.target.id); neigh.get(l.target.id)?.add(l.source.id);});

  // pulsesByTag: guaranteed map (generator now supplies this)
  const pulsesByTag = DATA.pulsesByTag || {};

  // -------- sim ----------
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(95).strength(.25))
    .force('charge', d3.forceManyBody().strength(-440))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide().radius(d => 12 + Math.sqrt((d.centrality||0)*500)));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('stroke-opacity', linkOpacity);

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');
      g.append('ellipse')
        .attr('rx', d => nodeRxBase + Math.sqrt((d.centrality||0)*700))
        .attr('ry', d => nodeRyBase + Math.sqrt((d.centrality||0)*350));
      g.append('text')
        .attr('y', d => (nodeRyBase + Math.sqrt((d.centrality||0)*350)) + 12)
        .attr('text-anchor','middle')
        .text(d=>d.id);

      g.on('mouseover', (ev,d)=>showTagTooltip(ev,d.id))
       .on('mousemove',  (ev)=>moveTooltip(ev))
       .on('mouseout',   hideTooltip)
       .on('click', (_ev,d)=>onTagClick(d.id));

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites bound to their host
    satLayer.selectAll('g.satellite')
      .attr('transform', d => {
        const x = d.host.x + d.r * Math.cos(d.a);
        const y = d.host.y + d.r * Math.sin(d.a);
        return `translate(${x},${y})`;
      });
  });

  svg.call(d3.zoom().scaleExtent([0.3, 4]).on('zoom', (e)=>root.attr('transform', e.transform)));

  // -------- tooltip ----------
  const ESC = s => String(s||'').replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  function showTagTooltip(ev, tag){
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) || '';
    const metrics = nodes.find(n=>n.id===tag) || {};
    const body = `
      <div style="font-weight:700;margin-bottom:3px">${ESC(tag)}</div>
      ${desc ? `<div style="white-space:pre-wrap;margin-bottom:6px">${ESC(desc)}</div>`:''}
      <div style="opacity:.9;font-size:12px">degree ${ (neigh.get(tag)||[]).size } · centrality ${ Number(metrics.centrality||0).toFixed(2) }</div>
      <div style="opacity:.9;margin-top:6px;font-size:12px"><em>Click to reveal pulse satellites</em></div>
    `;
    tooltip.html(body).style('display','block'); moveTooltip(ev);
  }
  function moveTooltip(ev){ const p=12; tooltip.style('left',(ev.pageX+p)+'px').style('top',(ev.pageY+p)+'px'); }
  function hideTooltip(){ tooltip.style('display','none'); }

  // -------- sidebar render ----------
  function showPulseDetails(p){
    let html = `<div style="font-weight:700">${ESC(p.title || p.id || 'Pulse')}</div>`;
    if (p.date) html += `<div class="chip">${ESC(p.date)}</div>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.5rem 0 0">${ESC(p.summary)}</div>`;

    const papers = Array.isArray(p.papers)?p.papers:[];
    const pods   = Array.isArray(p.podcasts)?p.podcasts:[];
    if (papers.length){
      html += `<div style="margin-top:10px"><strong>Papers</strong><ul style="margin:.25rem 0 0 1.1rem">`;
      papers.forEach(u=> html += `<li><a href="${u}" target="_blank" rel="noopener">${ESC(u)}</a></li>`);
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div style="margin-top:10px"><strong>Podcasts</strong><ul style="margin:.25rem 0 0 1.1rem">`;
      pods.forEach(u=> html += `<li><a href="${u}" target="_blank" rel="noopener">${ESC(u)}</a></li>`);
      html += `</ul></div>`;
    }

    details.innerHTML = html;
  }

  // -------- satellites ----------
  function onTagClick(tag){
    // focus styling + slight link bias
    nodeSel.classed('focus', d=>d.id===tag)
           .classed('dim',   d=>d.id!==tag && !neigh.get(tag)?.has(d.id));
    linkSel.classed('dim', d=> !(d.source.id===tag || d.target.id===tag ||
                                 neigh.get(tag)?.has(d.source.id) && neigh.get(tag)?.has(d.target.id)));

    // remove old satellites
    satLayer.selectAll('*').remove();

    const host = idToNode.get(tag);
    if (!host) return;

    const pulses = Array.isArray(pulsesByTag[tag]) ? pulsesByTag[tag] : [];
    if (!pulses.length){
      details.innerHTML = `<div style="color:#9aa6b2">No pulses tagged <strong>${ESC(tag)}</strong> yet.</div>`;
      return;
    }

    // multiple rings (newest inside). up to 24 per ring.
    const sorted = [...pulses].sort((a,b)=>(a.ageDays??9e9)-(b.ageDays??9e9));
    const perRing = 24, base = 105, step = 32;
    const satData = sorted.map((p,i) => {
      const ring = Math.floor(i/perRing);
      const pos  = i % perRing;
      const a = (pos / perRing) * Math.PI*2;       // radians
      const r = base + ring*step;
      return { ...p, a, r, host };
    });

    const sat = satLayer.selectAll('g.satellite')
      .data(satData, d=>d.id || `${tag}:${d.date||Math.random()}`)
      .join(enter=>{
        const g = enter.append('g').attr('class','satellite');
        g.append('circle')
          .attr('r', 5)
          .attr('class', d=>ageClass(d.ageDays));
        g.append('title').text(d => `${d.title || d.id || 'pulse'}${d.date?` — ${d.date}`:''}`);

        g.on('click', (_e,d)=>showPulseDetails(d));
        return g;
      });

    // gently re-stabilize
    sim.alpha(0.35).restart();

    // default sidebar message for the selected tag
    details.innerHTML = `<div style="color:#9aa6b2">
      Satellites for <strong>${ESC(tag)}</strong> shown on the map.
      Click a <strong>pulse dot</strong> to see its summary, papers & podcasts here.
    </div>`;
  }

  // -------- search filter ----------
  function norm(s){ return (s||'').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim(); }
  function applyFilter(q){
    const text = norm(q);
    if(!text){
      nodeSel.classed('dim',false); linkSel.classed('dim',false);
      return;
    }
    const keep = new Set(nodes.filter(n=>norm(n.id).includes(text)).map(n=>n.id));
    nodeSel.classed('dim', d=>!keep.has(d.id));
    linkSel.classed('dim', d=> !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  let t=null;
  if (search){
    search.addEventListener('input', e => { clearTimeout(t); t=setTimeout(()=>applyFilter(e.target.value), 80); });
  }

  // initial details
  details.innerHTML = `<div style="color:#9aa6b2">Click a pulse to see its summary, papers & podcasts.</div>`;
})();
