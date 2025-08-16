/* docs/graph.js — tag tooltips + pulse satellites + click-for-details
   Expects window.PHI_DATA with:
     nodes, links,
     tagDescriptions: { [tag]: "..." },
     pulsesByTag: { [tag]: [ {id,title?,summary?,date?,ageDays?,papers?,podcasts?} ] }
*/

(function(){
  const DATA = window.PHI_DATA || {nodes:[],links:[]};
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const details = document.getElementById('details');
  const search = document.getElementById('search');

  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;

  const idToNode = new Map((DATA.nodes||[]).map(n => [n.id, n]));

  // ---- helpers --------------------------------------------------------------
  const safeArr = x => Array.isArray(x) ? x : [];
  const esc = s => String(s||'').replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m]));
  const firstSentence = (txt, max=240) => {
    if(!txt) return '';
    const cut = txt.split(/(?<=\.)\s+/)[0];
    return (cut.length<=max)? cut : (cut.slice(0,max-1)+'…');
  };
  const trimUrl = (u, max=60) => {
    try{
      const s = u.replace(/^https?:\/\//,'').replace(/\/$/,'');
      return s.length>max ? (s.slice(0,max-1)+'…') : s;
    }catch{ return u; }
  };
  function ageClass(days){
    if(days==null) return 'age-old';
    if(days<=14)  return 'age-very-new';
    if(days<=45)  return 'age-new';
    if(days<=120) return 'age-mid';
    if(days<=270) return 'age-old';
    return 'age-very-old';
  }

  // ---- zoom/layers ----------------------------------------------------------
  svg.attr('viewBox', `0 0 ${width} ${height}`);
  const root = svg.append('g');
  const linkLayer = root.append('g');
  const nodeLayer = root.append('g');
  const satLayer  = root.append('g');

  svg.call(d3.zoom().scaleExtent([0.35, 4]).on('zoom', e => root.attr('transform', e.transform)));

  // ---- data wiring ----------------------------------------------------------
  const rawLinks = safeArr(DATA.links).map(l => ({
    source: idToNode.get(l.source)||l.source, target: idToNode.get(l.target)||l.target
  })).filter(l => l.source && l.target);

  const nodes = safeArr(DATA.nodes);
  const links = rawLinks;

  const linkSel = linkLayer.selectAll('line').data(links).join('line').attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(nodes, d=>d.id)
    .join(enter=>{
      const g = enter.append('g').attr('class','node');
      const rx = d => 6 + Math.sqrt((d.centrality||0)*900);
      const ry = d => 4 + Math.sqrt((d.centrality||0)*450);
      g.append('ellipse').attr('rx', rx).attr('ry', ry);
      g.append('text').attr('y', d=>ry(d)+12).attr('text-anchor','middle').text(d=>d.id);
      g.on('mouseover', (e,d)=>showTagTip(e,d.id))
       .on('mousemove', moveTip)
       .on('mouseout', hideTip)
       .on('click', (_e,d)=>focusTag(d.id));
      return g;
    });

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(.25))
    .force('charge', d3.forceManyBody().strength(-420))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(d=>10+Math.sqrt((d.centrality||0)*900)));

  sim.on('tick', ()=>{
    linkSel.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
           .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites tied to host
    satLayer.selectAll('g.satellite')
      .attr('transform', d=>{
        const a = d._angle||0, r = d._radius||100;
        const x = d.host.x + r*Math.cos(a), y = d.host.y + r*Math.sin(a);
        return `translate(${x},${y})`;
      });
  });

  // ---- tooltips -------------------------------------------------------------
  function showTagTip(evt, tagId){
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tagId]) || '';
    tooltip.html(`
      <div style="font-weight:700;margin-bottom:2px">${esc(tagId)}</div>
      <div class="muted" style="max-width:280px">${esc(firstSentence(desc)||'—')}</div>
      <div class="muted" style="margin-top:6px"><em>Click to reveal pulse satellites</em></div>
    `).style('display','block');
    moveTip(evt);
  }
  function moveTip(evt){
    const pad=12;
    tooltip.style('left', (evt.clientX+pad)+'px').style('top', (evt.clientY+pad)+'px');
  }
  function hideTip(){ tooltip.style('display','none'); }

  // ---- focus + satellites ---------------------------------------------------
  let focused = null;

  function focusTag(tagId){
    focused = tagId;
    hideTip();
    // dim others except neighborhood
    const neigh = new Set([tagId]);
    links.forEach(l=>{
      if(l.source.id===tagId) neigh.add(l.target.id);
      if(l.target.id===tagId) neigh.add(l.source.id);
    });
    nodeSel.classed('dim', d=>!neigh.has(d.id))
            .classed('focus', d=>d.id===tagId);
    linkSel.classed('dim', d=>!(neigh.has(d.source.id) && neigh.has(d.target.id)));

    // show satellites only; clear sidebar prompt
    details.innerHTML = `<div class="muted">Click a pulse to see its summary, papers & podcasts.</div>`;
    drawSatellites(tagId, 100);

    // give neighbors a little slack
    sim.force('link').distance(l => (l.source.id===tagId || l.target.id===tagId)? 120 : 90);
    sim.alpha(0.25).restart();
  }

  function drawSatellites(tagId, radius){
    satLayer.selectAll('*').remove();

    const host = idToNode.get(tagId);
    if(!host) return;

    const pulses = safeArr(DATA.pulsesByTag && DATA.pulsesByTag[tagId]);
    if(!pulses.length) return;

    // ring (newest near top by default)
    const n = pulses.length, TWO = Math.PI*2;
    const sats = pulses.map((p,i)=>({
      ...p, host, _angle: (-Math.PI/2) + (i/n)*TWO, _radius: radius
    }));

    const g = satLayer.selectAll('g.satellite')
      .data(sats, d=>d.id||`${tagId}:${d.date||d.title||Math.random()}`)
      .join(enter=>{
        const s = enter.append('g').attr('class','satellite');
        s.append('circle')
          .attr('r', 5)
          .attr('class', d=>ageClass(d.ageDays));
        s.append('title').text(d=>`${d.title||d.id||'pulse'}${d.date?` — ${d.date}`:''}`);
        s.on('click', (_e,d)=>showPulse(d));
        return s;
      });
  }

  // ---- render a single pulse in sidebar ------------------------------------
  function showPulse(p){
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}${p.date?` <span class="muted">(${esc(p.date)})</span>`:''}</h2>`;
    if(p.summary){
      html += `<div style="white-space:pre-wrap;margin:.35rem 0 1rem 0">${esc(p.summary)}</div>`;
    }
    const papers = safeArr(p.papers);
    const pods   = safeArr(p.podcasts);

    if(papers.length){
      html += `<div><span class="chip">Papers</span></div>`;
      papers.forEach(u => html += `<a href="${u}" target="_blank" rel="noopener">${esc(trimUrl(u))}</a>`);
    }
    if(pods.length){
      html += `<div style="margin-top:10px"><span class="chip">Podcasts</span></div>`;
      pods.forEach(u => html += `<a href="${u}" target="_blank" rel="noopener">${esc(trimUrl(u))}</a>`);
    }
    details.innerHTML = html;
  }

  // ---- search ---------------------------------------------------------------
  function runFilter(q){
    const s = (q||'').toLowerCase().trim();
    if(!s){
      nodeSel.classed('dim', false); linkSel.classed('dim', false);
      return;
    }
    const keep = new Set(nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
    nodeSel.classed('dim', d=>!keep.has(d.id));
    linkSel.classed('dim', d=>!(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  search && search.addEventListener('input', e=>runFilter(e.target.value));

  // ---- initial hint ---------------------------------------------------------
  details.innerHTML = `<div class="muted">Pick a tag to see details here.</div>`;
})();
