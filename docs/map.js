/* docs/map.js — renderer. Expects window.PHI_DATA from docs/data.js */
(function(){
  const DATA = (typeof window !== 'undefined' && window.PHI_DATA) ? window.PHI_DATA
              : { nodes:[], links:[], tagDescriptions:{}, pulsesByTag:{} };

  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const sidebar = document.getElementById('sidebar-content');
  const searchInput = document.getElementById('search');

  function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
  const W = svg.node().clientWidth  || 1200;
  const H = svg.node().clientHeight || 800;

  const minR = 6, maxR = 24, ellipseAspect = 1.6;
  const linkOpacity = .28;

  const rScale = (() => {
    const deg = new Map();
    DATA.links.forEach(l => {
      deg.set(l.source,(deg.get(l.source)||0)+1);
      deg.set(l.target,(deg.get(l.target)||0)+1);
    });
    const c = DATA.nodes.map(n => typeof n.centrality==='number' ? n.centrality : (deg.get(n.id)||0));
    const cMin = d3.min(c) ?? 0, cMax = d3.max(c) ?? 1;
    return d3.scaleSqrt().domain([cMin||1e-4, cMax||1]).range([minR,maxR]);
  })();

  svg.attr('viewBox',`0 0 ${W} ${H}`);
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');
  const satLayer  = root.append('g').attr('class','satellites');

  svg.call(d3.zoom().scaleExtent([0.35,4]).on('zoom',ev=>root.attr('transform',ev.transform)));
  svg.on('click', ev=>{
    if(ev.target===svg.node()){ clearSatellites(); clearFocus(); sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;}
  });

  const idToNode = new Map(DATA.nodes.map(n=>[n.id,n]));
  const links = DATA.links.map(l=>({
    source: idToNode.get(l.source)||l.source,
    target: idToNode.get(l.target)||l.target
  })).filter(l=>l.source && l.target);

  const degMap = new Map();
  links.forEach(l=>{
    degMap.set(l.source.id,(degMap.get(l.source.id)||0)+1);
    degMap.set(l.target.id,(degMap.get(l.target.id)||0)+1);
  });

  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(75).strength(.7))
    .force('charge', d3.forceManyBody().strength(-180))
    .force('center', d3.forceCenter(W/2,H/2))
    .force('collision', d3.forceCollide().radius(d=>rScale(d.centrality ?? degMap.get(d.id)||1)*1.2));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('stroke-opacity',linkOpacity);

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter=>{
      const g=enter.append('g').attr('class','node');
      g.append('ellipse')
        .attr('rx',d=>rScale(d.centrality ?? degMap.get(d.id)||1)*ellipseAspect)
        .attr('ry',d=>rScale(d.centrality ?? degMap.get(d.id)||1));
      g.append('text')
        .attr('x',d=>rScale(d.centrality ?? degMap.get(d.id)||1)*ellipseAspect+4)
        .attr('y',4)
        .text(d=>d.id);
      g.on('mouseover',(ev,d)=>showTagTip(ev,d.id))
       .on('mousemove',moveTip)
       .on('mouseout',hideTip)
       .on('click',(ev,d)=>{ev.stopPropagation(); onTagClick(d.id);});
      return g;
    });

  sim.on('tick',()=>{
    linkSel.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
           .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    nodeSel.attr('transform',d=>`translate(${d.x},${d.y})`);
    satLayer.selectAll('g.satellite')
      .attr('transform',d=>`translate(${d.host.x + d._xoff},${d.host.y + d._yoff})`);
  });

  function showTagTip(evt,tag){
    const n=idToNode.get(tag);
    const deg=degMap.get(tag)||0;
    const cent=typeof n?.centrality==='number'?n.centrality.toFixed(2):deg;
    const desc=(DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
    tooltip.html(
      `<div style="font-weight:700;margin-bottom:4px">${esc(tag)}</div>
       <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
       <div style="white-space:pre-wrap;opacity:.92">${esc(desc)}</div>
       <div style="margin-top:6px;font-size:12px;color:#97a3b6">Click to reveal pulse satellites</div>`
    ).style('display','block'); moveTip(evt);
  }
  function moveTip(evt){ const pad=12; tooltip.style('left',(evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px'); }
  function hideTip(){ tooltip.style('display','none'); }

  function setFocus(keepIds){
    const keep=new Set(keepIds);
    nodeSel.classed('dim',d=>!keep.has(d.id));
    linkSel.classed('dim',d=>!(keep.has(d.source.id)&&keep.has(d.target.id)));
  }
  function clearFocus(){ nodeSel.classed('dim',false); linkSel.classed('dim',false); }

  function clearSatellites(){ satLayer.selectAll('*').remove(); }

  function spiralOffsets(n){
    const out=[]; const stepR=8, stepT=0.48*Math.PI, startR=52;
    for(let i=0;i<n;i++){ const r=startR+i*stepR, t=i*stepT; out.push({_xoff:r*Math.cos(t), _yoff:r*Math.sin(t)}); }
    return out;
  }

  function ageClass(d){
    const a=d?.ageDays;
    if(a==null) return 'age-old';
    if(a<=14) return 'age-very-new';
    if(a<=45) return 'age-new';
    if(a<=120) return 'age-mid';
    if(a<=270) return 'age-old';
    return 'age-very-old';
  }

  function onTagClick(tagId){
    const neighbors=new Set([tagId]);
    links.forEach(l=>{ if(l.source.id===tagId) neighbors.add(l.target.id); if(l.target.id===tagId) neighbors.add(l.source.id);});
    setFocus(neighbors);
    clearSatellites();

    const host=idToNode.get(tagId);
    const pulses = Array.isArray(DATA.pulsesByTag?.[tagId]) ? DATA.pulsesByTag[tagId] : [];
    if(!host || !pulses.length) return;
    const offs=spiralOffsets(pulses.length);

    const enter=satLayer.selectAll('g.satellite')
      .data(pulses.map((p,i)=>({...p,host,...offs[i]})), d=>d.id||d.title||(d.date||''))
      .enter().append('g').attr('class','satellite');

    enter.append('circle').attr('r',4.6).attr('class',d=>ageClass(d));
    enter.append('text').attr('y',-9).attr('text-anchor','middle').attr('font-size',9).attr('fill','#a3b3c7')
         .text(d=>d.date ? d.date.slice(2,10) : '');

    enter.on('click',(ev,d)=>{ev.stopPropagation(); showPulse(d);});
    // give the sim a nudge for quicker layout settle
    d3.timeout(()=>{ /* cosmetic */ }, 0);
  }

  function linksBlock(label, items){
    if(!items||!items.length) return '';
    const norm = items.map(u => typeof u==='string' ? {title:u,url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
    let html = `<div style="margin-top:12px"><strong>${label}</strong><ul style="padding-left:18px;margin:6px 0 0 0">`;
    norm.forEach(it => { const title=it.title||it.url; const href=it.url||it.title||'#';
      html += `<li><a class="ellipsis" href="${esc(href)}" target="_blank" rel="noopener">${esc(title)}</a></li>`;});
    return html + `</ul></div>`;
  }

  function showPulse(p){
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
    if(p.summary) html += `<div style="white-space:pre-wrap;margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;
    html += linksBlock('Papers', p.papers);
    html += linksBlock('Podcasts', p.podcasts);
    sidebar.innerHTML = html;
  }

  function applyFilter(q){
    const s=(q||'').trim().toLowerCase();
    if(!s){ clearFocus(); return; }
    const keep=new Set(DATA.nodes.filter(n=>n.id.toLowerCase().includes(s)).map(n=>n.id));
    setFocus(keep);
  }
  if(searchInput) searchInput.addEventListener('input',e=>applyFilter(e.target.value));

  sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
})();
