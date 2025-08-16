/* docs/graph.js
   Expects window.PHI_DATA with:
   - nodes: [{id, centrality?}], links: [{source, target}]
   - tagDescriptions: { [tag]: string }
   - tagResources: { [tag]: {papers:[], podcasts:[]} }
   - pulsesByTag: { [tag]: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts?, tags? }] }
   DOM: #graph (svg), #tooltip, #sidebar-content, #search
   D3 v7 must be loaded.
*/
(function(){
  const DATA = window.PHI_DATA || {nodes:[], links:[]};

  // ---------- DOM ----------
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const sidebar = document.getElementById('sidebar-content');
  const searchInput = document.getElementById('search');

  function esc(s){return String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
  const SA = x => Array.isArray(x)?x:[];
  const W = svg.node().clientWidth||1200, H = svg.node().clientHeight||800;

  // ---------- zoom / layers ----------
  svg.attr('viewBox',`0 0 ${W} ${H}`);
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class','links');
  const nodeLayer = root.append('g').attr('class','nodes');
  const satLayer  = root.append('g').attr('class','satellites');

  svg.call(d3.zoom().scaleExtent([0.3,4]).on('zoom',e=>root.attr('transform',e.transform)));

  // ---------- nodes/links ----------
  const id2 = new Map((DATA.nodes||[]).map(n=>[n.id,n]));
  const links = SA(DATA.links).map(l=>({source:id2.get(l.source)||l.source,target:id2.get(l.target)||l.target}))
                              .filter(l=>l.source && l.target);

  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(88).strength(0.6))
    .force('charge', d3.forceManyBody().strength(-220))
    .force('center', d3.forceCenter(W/2,H/2))
    .force('collide', d3.forceCollide().radius(14));

  const linkSel = linkLayer.selectAll('line').data(links).join('line').attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter=>{
      const g = enter.append('g').attr('class','node');
      g.append('circle').attr('r',6);
      g.append('text').attr('x',9).attr('y',3).text(d=>d.id);
      g.on('mouseover', (evt,d)=>showTagTooltip(evt,d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
       .on('click', (_evt,d)=>onTagClick(d.id));
      return g;
    });

  sim.on('tick', ()=>{
    linkSel.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
           .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    nodeSel.attr('transform',d=>`translate(${d.x},${d.y})`);
    // keep satellites around host
    satLayer.selectAll('g.satellite').attr('transform',d=>{
      const a = d._angle||0, r = d._r||90;
      const x = d.host.x + r*Math.cos(a), y = d.host.y + r*Math.sin(a);
      return `translate(${x},${y})`;
    });
  });

  // ---------- tooltip (use pageX/pageY so it doesn't drift) ----------
  function tagDescription(id){
    return (DATA.tagDescriptions && DATA.tagDescriptions[id]) || '';
  }
  function showTagTooltip(evt, tagId){
    const html =
      `<div style="font-weight:700;margin-bottom:2px">${esc(tagId)}</div>`+
      `<div style="opacity:.95;white-space:pre-wrap">${esc(tagDescription(tagId)||'—')}</div>`+
      `<div style="margin-top:6px;opacity:.8;font-size:12px">Click for pulse satellites</div>`;
    tooltip.html(html).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad=12;
    tooltip.style('left', (evt.pageX+pad)+'px')
           .style('top',  (evt.pageY+pad)+'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ---------- sidebar renders ----------
  function showTagDetails(tagId){
    const desc = tagDescription(tagId);
    const res = (DATA.tagResources && DATA.tagResources[tagId]) || {};
    let html = `<h3 style="margin:.2rem 0">${esc(tagId)}</h3>`;
    html += `<div style="white-space:pre-wrap;margin:.25rem 0 0.6rem 0">${esc(desc||'—')}</div>`;
    const papers = SA(res.papers), pods = SA(res.podcasts);
    if(papers.length){
      html += `<div><strong>Papers</strong><ul style="margin:.3rem 0 .6rem 1.1rem">`+
              papers.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('')+
              `</ul></div>`;
    }
    if(pods.length){
      html += `<div><strong>Podcasts</strong><ul style="margin:.3rem 0 .6rem 1.1rem">`+
              pods.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('')+
              `</ul></div>`;
    }
    const pulses = SA(DATA.pulsesByTag?.[tagId]);
    if(pulses.length){
      const recent = [...pulses].sort((a,b)=>(a.ageDays??9e9)-(b.ageDays??9e9)).slice(0,6);
      html += `<div><strong>Recent pulses</strong><ul style="margin:.3rem 0 .6rem 1.1rem">`+
              recent.map(p=>`<li>${esc(p.title||p.id||'pulse')}${p.date?` — ${esc(p.date)}`:''}</li>`).join('')+
              `</ul></div>`;
    }
    sidebar.innerHTML = html;
  }

  function showPulseDetails(p){
    let html = `<h3 style="margin:.2rem 0">${esc(p.title||p.id||'Pulse')}</h3>`;
    if(p.date) html += `<div class="muted" style="margin:.1rem 0 .5rem 0">${esc(p.date)}</div>`;
    if(p.summary) html += `<div style="white-space:pre-wrap;margin:.25rem 0 .6rem 0">${esc(p.summary)}</div>`;
    const papers=SA(p.papers), pods=SA(p.podcasts);
    if(papers.length){
      html+=`<div><strong>Papers</strong><ul style="margin:.3rem 0 .6rem 1.1rem">`+
            papers.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('')+
            `</ul></div>`;
    }
    if(pods.length){
      html+=`<div><strong>Podcasts</strong><ul style="margin:.3rem 0 .6rem 1.1rem">`+
            pods.map(u=>`<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`).join('')+
            `</ul></div>`;
    }
    if(p.tags && p.tags.length){
      html += `<div style="margin-top:.4rem"><strong>Tags</strong><div style="margin-top:.2rem">`+
              p.tags.map(t=>`<span style="display:inline-block;background:#1a2233;border:1px solid #2c3950;border-radius:999px;padding:2px 8px;margin:2px;font-size:12px">${esc(t)}</span>`).join('')+
              `</div></div>`;
    }
    sidebar.innerHTML = html;
  }

  // ---------- satellites (pulses) ----------
  function ageClass(ageDays){
    if(ageDays==null) return 'age-old';
    if(ageDays<=14) return 'age-very-new';
    if(ageDays<=45) return 'age-new';
    if(ageDays<=120) return 'age-mid';
    if(ageDays<=270) return 'age-old';
    return 'age-very-old';
  }

  function onTagClick(tagId){
    hideTooltip();
    showTagDetails(tagId);

    satLayer.selectAll('*').remove();
    const host = id2.get(tagId);
    const pulses = SA(DATA.pulsesByTag?.[tagId]);
    if(!host || !pulses.length) return;

    const n = pulses.length, TWO_PI = Math.PI*2;
    const s = satLayer.selectAll('g.satellite')
      .data(pulses.map((p,i)=>({...p, host, _angle:(i/n)*TWO_PI, _r:90})), d=>d.id||d.title||`${tagId}:${d.date||i}`);

    const enter = s.enter().append('g').attr('class','satellite');
    enter.append('circle').attr('r',4.5).attr('class', d=>ageClass(d.ageDays));
    enter.append('title').text(d=>`${d.title||d.id||'pulse'}${d.date?` — ${d.date}`:''}`);
    enter.on('click', (_e,d)=>{ showPulseDetails(d); });

    sim.alpha(0.5).restart();
  }

  // ---------- search ----------
  function applyFilter(q){
    q = (q||'').toLowerCase().trim();
    if(!q){ nodeSel.classed('dim',false); linkSel.classed('dim',false); return; }
    const keep = new Set(DATA.nodes.filter(n=>n.id.toLowerCase().includes(q)).map(n=>n.id));
    nodeSel.classed('dim', d=>!keep.has(d.id));
    linkSel.classed('dim', d=>!(keep.has(d.source.id)&&keep.has(d.target.id)));
  }
  if(searchInput) searchInput.addEventListener('input',e=>applyFilter(e.target.value));

  // ---------- initial hint ----------
  sidebar.innerHTML = `<div class="muted">Pick a tag to see details. Hover tags for descriptions. Click a tag to reveal pulse satellites (age-colored), then click a pulse for details.</div>`;
})();
