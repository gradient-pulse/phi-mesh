/* Phi-Mesh interactive tag + pulse map
 * expects window.PHI_DATA with:
 *  nodes: [{id, centrality?}], links: [{source, target}],
 *  tagDescriptions: {tag: string},
 *  pulsesByTag: {tag: [{ id, title?, date?, ageDays?, summary?, papers?, podcasts?, tags? }]}
 */
(function(){
  const D = window.PHI_DATA || {nodes:[],links:[]};
  const svg = d3.select('#graph');
  const sidebar = document.getElementById('sidebar');
  const tooltip = document.getElementById('tooltip');
  const search = document.getElementById('search');

  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  // --- helpers ---------------------------------------------------------------
  const byId = new Map((D.nodes||[]).map(n=>[n.id,n]));
  const neighbors = new Map((D.nodes||[]).map(n=>[n.id,new Set]));
  (D.links||[]).forEach(l=>{
    neighbors.get(l.source)?.add(l.target);
    neighbors.get(l.target)?.add(l.source);
  });

  const esc = s => String(s||"").replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const safeArr = x => Array.isArray(x) ? x : [];
  const trunc = (s,n=80)=> (s && s.length>n) ? s.slice(0,n-1) + '…' : (s||'');

  // satellite color (new→warm, old→cool)
  function pulseColor(ageDays){
    if (ageDays == null) return '#6aa4ff';
    if (ageDays <= 14)  return '#ff7a66';
    if (ageDays <= 45)  return '#ffb266';
    if (ageDays <= 120) return '#ffd166';
    if (ageDays <= 270) return '#9ec7ff';
    return '#6aa4ff';
  }

  function placeTooltip(evt, html){
    tooltip.innerHTML = html;
    tooltip.style.display = 'block';
    const pad = 14;
    const x = (evt.clientX ?? 0) + pad;
    const y = (evt.clientY ?? 0) + pad;
    tooltip.style.left = x + 'px';
    tooltip.style.top  = y + 'px';
  }
  function hideTooltip(){ tooltip.style.display='none'; }

  function showPulseDetails(p){
    let html = '';
    const when = p.date ? ` <span class="chip">${esc(p.date)}</span>` : '';
    html += `<h2>${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.25rem 0 1rem 0">${esc(p.summary)}</div>`;
    const papers = safeArr(p.papers);
    const pods   = safeArr(p.podcasts);
    if (papers.length){
      html += `<div style="margin:.25rem 0 .25rem 0"><strong>Papers</strong></div><ul class="list">`;
      for (const u of papers){
        html += `<li><a class="ellipsis" href="${u}" target="_blank" rel="noopener">${esc(trunc(u, 88))}</a></li>`;
      }
      html += `</ul>`;
    }
    if (pods.length){
      html += `<div style="margin:.5rem 0 .25rem 0"><strong>Podcasts</strong></div><ul class="list">`;
      for (const u of pods){
        html += `<li><a class="ellipsis" href="${u}" target="_blank" rel="noopener">${esc(trunc(u, 88))}</a></li>`;
      }
      html += `</ul>`;
    }
    sidebar.innerHTML = html || `<div class="empty">No details for this pulse.</div>`;
  }

  // --- layers & zoom ---------------------------------------------------------
  const root = svg.append('g');
  const linkLayer = root.append('g');
  const nodeLayer = root.append('g');
  const satLayer  = root.append('g'); // satellites

  svg.call(
    d3.zoom().scaleExtent([0.35, 4]).on('zoom', (e)=> root.attr('transform', e.transform))
  );

  // --- simulation ------------------------------------------------------------
  // map link endpoints to node objects
  const id2 = new Map((D.nodes||[]).map(n=>[n.id,n]));
  const links = (D.links||[]).map(l=>({
    source: id2.get(l.source) || l.source,
    target: id2.get(l.target) || l.target
  })).filter(l=>l.source && l.target);

  // precompute “degree” for ellipse sizes
  const degree = {};
  links.forEach(({source,target})=>{
    const s = (source.id??source), t = (target.id??target);
    degree[s] = (degree[s]||0)+1;
    degree[t] = (degree[t]||0)+1;
  });

  const nodes = D.nodes || [];
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(95).strength(.25))
    .force('charge', d3.forceManyBody().strength(-420))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(d=>8 + Math.sqrt((degree[d.id]||0)) * 1.6));

  const link = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  const node = nodeLayer.selectAll('g.node')
    .data(nodes, d=>d.id)
    .join(enter=>{
      const g = enter.append('g').attr('class','node').style('cursor','pointer');
      // ellipse size driven by degree/centrality
      const rx = d => 6 + Math.sqrt((degree[d.id]||0)) * 1.2 + Math.sqrt((d.centrality||0))*12;
      const ry = d => 4 + Math.sqrt((degree[d.id]||0)) * 0.9 + Math.sqrt((d.centrality||0))*8;
      g.append('ellipse').attr('rx', rx).attr('ry', ry);
      g.append('text').attr('y', d=>ry(d)+12).attr('text-anchor','middle').text(d=>d.id);

      g.on('mouseover', (evt, d)=>{
        const desc = (D.tagDescriptions && D.tagDescriptions[d.id]) || '';
        const metrics = `degree ${degree[d.id]||0} · centrality ${(d.centrality||0).toFixed(2)}`;
        const html = `
          <div class="t1">${esc(d.id)}</div>
          <div class="t2">${metrics}</div>
          ${desc ? `<div>${esc(desc)}</div>` : ``}
          <div class="t2" style="margin-top:6px">Click to reveal pulse satellites</div>
        `;
        placeTooltip(evt, html);
      }).on('mousemove', (evt)=> placeTooltip(evt, tooltip.innerHTML))
        .on('mouseout', hideTooltip)
        .on('click', (_evt, d)=> onTagClick(d.id));

      return g;
    });

  sim.on('tick', ()=>{
    link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
        .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    node.attr('transform', d=>`translate(${d.x},${d.y})`);
    // keep satellites locked to their host each tick
    satLayer.selectAll('g.satellite')
      .attr('transform', d=>{
        const a = d._angle || 0, R = d._radius || 90;
        const x = d.host.x + R*Math.cos(a);
        const y = d.host.y + R*Math.sin(a);
        return `translate(${x},${y})`;
      });
  });

  // --- focus & satellites ----------------------------------------------------
  let focused = null;

  function onTagClick(tagId){
    focused = tagId;

    // focus highlight on neighbors, keep the structure visible
    const keep = new Set([tagId, ...(neighbors.get(tagId)||[])]);
    node.classed('dim', d=>!keep.has(d.id)).classed('focus', d=>d.id===tagId);
    link.classed('dim', d=> !(keep.has(d.source.id) && keep.has(d.target.id)));

    // draw satellites
    drawSatellites(tagId);

    // small nudge so satellites settle into place
    sim.alpha(0.15).restart();
  }

  function drawSatellites(tagId){
    satLayer.selectAll('*').remove();
    const host = byId.get(tagId);
    if(!host) return;
    const pulses = safeArr(D.pulsesByTag?.[tagId]);
    if(!pulses.length) return;

    // Angle layout (ring; if many pulses, they’ll cluster pleasantly)
    const n = pulses.length, TWO = Math.PI*2, R = 90;
    const data = pulses.map((p,i)=> Object.assign({}, p, {
      host, _angle:(i/n)*TWO, _radius:R
    }));

    const g = satLayer.selectAll('g.satellite')
      .data(data, d=>d.id || `${tagId}:${d.date||Math.random()}`)
      .join(enter=>{
        const s = enter.append('g').attr('class','satellite').style('cursor','pointer');
        s.append('circle').attr('r', 5).attr('fill', d=>pulseColor(d.ageDays));
        // tiny date label (optional)
        s.append('text').attr('y', -8).attr('text-anchor','middle')
          .text(d => d.date ? d.date.slice(2,10) : '');
        s.append('title').text(d => `${d.title || d.id || 'pulse'}${d.date ? ` — ${d.date}`:''}`);
        s.on('click', (_e, d)=> showPulseDetails(d));
        return s;
      });
  }

  // --- searching -------------------------------------------------------------
  function applyFilter(q){
    const norm = (q||'').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
    if(!norm){
      node.classed('dim', false); link.classed('dim', false); return;
    }
    const keep = new Set(nodes
      .filter(n => n.id.toLowerCase().includes(norm))
      .map(n => n.id)
    );
    node.classed('dim', d=>!keep.has(d.id));
    link.classed('dim', d=> !(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  let t=null;
  search.addEventListener('input', ()=>{ clearTimeout(t); t=setTimeout(()=>applyFilter(search.value),80); });

  // initial sidebar state
  sidebar.innerHTML = `<div class="empty">Pick a pulse to see its summary, papers &amp; podcasts.</div>`;
})();
