/* docs/graph.js — single-sidebar build with compatibility shim
   Expects window.PHI_DATA (from docs/data.js).

   Uses these keys if present:
   - nodes: [{ id, centrality? }], links: [{ source, target }]
   - tagDescriptions: { [tag]: "..." }
   - tagResources: { [tag]: { papers: string[], podcasts: string[] } }
   - pulses: { [pulseId]: { id, title?, date?, ageDays?, summary?, papers?, podcasts?, tags? } }
   - tagToPulses: { [tag]: string[] }          // pulse IDs per tag

   If pulsesByTag is missing, we build it from pulses + tagToPulses.
*/

(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // ---- Compatibility shim: build pulsesByTag if absent ----------------------
  if (!DATA.pulsesByTag && DATA.tagToPulses && DATA.pulses) {
    const byTag = {};
    for (const [tag, idList] of Object.entries(DATA.tagToPulses)) {
      byTag[tag] = (idList || [])
        .map(id => DATA.pulses[id])
        .filter(Boolean);
    }
    DATA.pulsesByTag = byTag;
  }

  // ---- DOM ------------------------------------------------------------------
  const svg = d3.select('#graph');
  const tooltip = d3.select('#tooltip');
  const detailsEl = document.getElementById('details');
  const searchEl = document.getElementById('search');

  function safeArr(x){ return Array.isArray(x) ? x : []; }
  function esc(s){ return String(s||'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  // ---- Config ---------------------------------------------------------------
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;
  const nodeR = 6;
  const satRingR = 92;
  const satDotR  = 4.6;

  // Age → class bucket
  function ageClass(ageDays){
    if (ageDays == null) return 'age-old';
    if (ageDays <= 14)  return 'age-very-new';
    if (ageDays <= 45)  return 'age-new';
    if (ageDays <= 120) return 'age-mid';
    if (ageDays <= 270) return 'age-old';
    return 'age-very-old';
  }

  // ---- SVG Layers & Zoom ----------------------------------------------------
  svg.attr('viewBox', `0 0 ${width} ${height}`);
  const root = svg.append('g');
  const gLinks = root.append('g').attr('class','links');
  const gNodes = root.append('g').attr('class','nodes');
  const gSats  = root.append('g').attr('class','satellites');

  svg.call(d3.zoom().scaleExtent([0.3, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform)));

  // ---- Build link objects with node refs -----------------------------------
  const idToNode = new Map(DATA.nodes.map(n=>[n.id, n]));
  const links = (DATA.links || []).map(l => ({
    source: idToNode.get(l.source) || l.source,
    target: idToNode.get(l.target) || l.target
  })).filter(l=>l.source && l.target);

  // ---- Force simulation -----------------------------------------------------
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(86).strength(0.65))
    .force('charge', d3.forceManyBody().strength(-190))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(nodeR*2.2));

  const linkSel = gLinks.selectAll('line').data(links).join('line').attr('class','link');

  const nodeSel = gNodes.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter=>{
      const g = enter.append('g').attr('class','node');
      g.append('circle').attr('r', nodeR);
      g.append('text').attr('x', nodeR + 3).attr('y', 3).text(d=>d.id);

      // interactions
      g.on('mouseover', (ev,d)=>showTagTooltip(ev, d.id))
       .on('mousemove',  (ev)=>moveTooltip(ev))
       .on('mouseout',   hideTooltip)
       .on('click',      (_ev,d)=>onTagClick(d.id));

      return g;
    });

  sim.on('tick', ()=>{
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites ringed around host
    gSats.selectAll('g.satellite')
      .attr('transform', d=>{
        const a = d._angle || 0, r = d._radius || satRingR;
        const x = d.host.x + r*Math.cos(a);
        const y = d.host.y + r*Math.sin(a);
        return `translate(${x},${y})`;
      });
  });

  // ---- Tooltip (tag description) -------------------------------------------
  function showTagTooltip(ev, tagId){
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tagId]) || '';
    const html = `
      <div style="font-weight:600;margin-bottom:4px">${esc(tagId)}</div>
      <div style="white-space:pre-wrap;opacity:.92">${esc(desc || '—')}</div>
      <div style="margin-top:6px;font-size:12px;color:#9fb0c3">Click for pulse satellites</div>
    `;
    tooltip.html(html).style('display','block');
    moveTooltip(ev);
  }
  function moveTooltip(ev){
    const pad = 14;
    tooltip.style('left', (ev.pageX + pad) + 'px')
           .style('top',  (ev.pageY + pad) + 'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ---- Sidebar renderers ----------------------------------------------------
  function renderTagDetails(tagId){
    const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tagId]) || '';
    const res  = (DATA.tagResources && DATA.tagResources[tagId]) || {};
    const papers = safeArr(res.papers), pods = safeArr(res.podcasts);

    let html = `<h2>${esc(tagId)}</h2>`;
    html += `<div style="white-space:pre-wrap;margin:.25rem 0 0.6rem 0">${esc(desc || '—')}</div>`;

    if (papers.length){
      html += `<div><strong>Papers</strong><ul style="margin:.25rem 0 .65rem 1.1rem">`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div><strong>Podcasts</strong><ul style="margin:.25rem 0 .2rem 1.1rem">`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    html += `<div class="muted" style="margin-top:.4rem">Click a pulse satellite to see its summary & links.</div>`;
    detailsEl.innerHTML = html;
  }

  function renderPulseDetails(p){
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}</h2>`;
    if (p.date) html += `<div class="muted" style="margin:-4px 0 6px 0">${esc(p.date)}</div>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.25rem 0 .6rem 0">${esc(p.summary)}</div>`;

    const papers = safeArr(p.papers), pods = safeArr(p.podcasts);
    if (papers.length){
      html += `<div><strong>Papers</strong><ul style="margin:.25rem 0 .65rem 1.1rem">`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div><strong>Podcasts</strong><ul style="margin:.25rem 0 .2rem 1.1rem">`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul></div>`;
    }
    if (p.tags && p.tags.length){
      html += `<div style="margin-top:.4rem"><strong>Tags</strong><div style="margin-top:4px">`;
      for (const t of p.tags){
        html += `<span style="display:inline-block;background:#152236;border:1px solid #2b3a52;border-radius:999px;padding:2px 8px;margin:2px;font-size:12px">${esc(t)}</span>`;
      }
      html += `</div></div>`;
    }
    detailsEl.innerHTML = html;
  }

  // ---- Pulses as satellites -------------------------------------------------
  let focusedTag = null;

  function onTagClick(tagId){
    focusedTag = tagId;
    nodeSel.classed('focus', d=>d.id===tagId).classed('dim', d=>d.id!==tagId);
    linkSel.classed('dim', d => !(d.source.id===tagId || d.target.id===tagId));

    // sidebar
    renderTagDetails(tagId);

    // clear existing satellites
    gSats.selectAll('*').remove();

    const host = idToNode.get(tagId);
    const pulses = safeArr(DATA.pulsesByTag?.[tagId]);
    if (!host || pulses.length===0) return;

    const n = pulses.length, TWO_PI = Math.PI*2;
    const sats = gSats.selectAll('g.satellite')
      .data(pulses.map((p,i)=>({
        ...p, host, _angle:(i/n)*TWO_PI, _radius:satRingR
      })), d=>d.id || d.title || `${tagId}:${d.date||''}:${Math.random()}`);

    const enter = sats.enter().append('g').attr('class','satellite');

    enter.append('circle')
      .attr('r', satDotR)
      .attr('class', d=>ageClass(d.ageDays));

    // pulse click → show details
    enter.on('click', (_ev,d)=>renderPulseDetails(d));

    // small inline date label (optional)
    enter.append('text')
      .attr('y', -8).attr('text-anchor','middle')
      .attr('font-size', 9).attr('fill', '#a3b3c7')
      .text(d => d.date ? d.date.slice(2,10) : '');

    sim.alpha(0.5).restart();
  }

  // clicking empty space clears focus
  svg.on('click', (ev)=>{
    if (ev.target.tagName === 'svg'){
      focusedTag = null;
      nodeSel.classed('focus', false).classed('dim', false);
      linkSel.classed('dim', false);
      gSats.selectAll('*').remove();
      detailsEl.innerHTML = `<div class="muted">Pick a tag to see details. Hover a tag for descriptions. Click a tag to reveal pulse satellites (age-colored), then click a pulse to view its summary & links here.</div>`;
      sim.alpha(0.15).restart();
    }
  });

  // ---- Search filter --------------------------------------------------------
  function runFilter(qRaw){
    const q = (qRaw||'').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
    if (!q){
      nodeSel.classed('dim', false).attr('opacity', 1);
      linkSel.attr('opacity', 0.35);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(q)).map(n=>n.id));
    nodeSel.attr('opacity', d => keep.has(d.id) ? 1 : 0.12);
    linkSel.attr('opacity', d => (keep.has(d.source.id) && keep.has(d.target.id)) ? 0.35 : 0.05);
  }
  let t=null;
  searchEl.addEventListener('input', e => { if(t)clearTimeout(t); t=setTimeout(()=>runFilter(e.target.value), 80); });

  // ---- Initial hint ---------------------------------------------------------
  detailsEl.innerHTML = `<div class="muted">Pick a tag to see details. Hover a tag for descriptions. Click a tag to reveal pulse satellites (age-colored), then click a pulse to view its summary & links here.</div>`;
})();
