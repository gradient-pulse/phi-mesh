/* Tag Map renderer – expects window.PHI_DATA created by data.js
   Safari-safe (no mixing ?? and ||), single tooltip, dimming + single-node highlight,
   right sidebar list with one-line truncation, and smaller/looser graph layout. */

(function(){
  // Wait for DOM so #graph exists (prevents clientWidth null)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init(){
    const DATA = window.PHI_DATA || { nodes:[], links:[], tagDescriptions:{}, pulsesByTag:{} };

    // DOM
    const svg      = d3.select('#graph');
    const leftBox  = document.getElementById('left');
    const rightBox = document.getElementById('right');
    const search   = document.getElementById('search');
    const tooltip  = d3.select('#tooltip');              // <— single tooltip (fix for “const twice”)
    const rootNode = svg.node();
    const width    = rootNode.clientWidth  || 1200;
    const height   = rootNode.clientHeight || 800;

    // helpers
    const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
    function safeArray(x){ return Array.isArray(x) ? x : []; }
    function esc(s){ return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

    // links -> node references
    const links = DATA.links.map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    })).filter(l => l.source && l.target);

    // degree (fallback for sizing)
    const degree = new Map();
    links.forEach(l => {
      degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
      degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
    });

    // radius scale (slightly smaller); Safari-safe scoring (no ?? mixed with ||)
    const centralities = DATA.nodes.map(n => (typeof n.centrality === 'number' ? n.centrality : (degree.get(n.id)||0)));
    const cMin = d3.min(centralities) ?? 0, cMax = d3.max(centralities) ?? 1;
    const rMin = 5, rMax = 20;
    const rScale = d3.scaleSqrt().domain([cMin||0.0001, cMax||1]).range([rMin, rMax]);
    const ellipseAspect = 1.55;
    function nodeScore(d){
      const c = d.centrality;
      return (typeof c === 'number') ? c : ((degree.get(d.id)||1));
    }

    // layers & zoom
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    const root = svg.append('g');
    const linkLayer = root.append('g').attr('class','links');
    const nodeLayer = root.append('g').attr('class','nodes');

    const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform));
    svg.call(zoom);

    // background click: clear highlight & lists (left stays as-is until a pulse is clicked)
    svg.on('click', (ev)=>{
      if (ev.target === svg.node()) {
        clearFocus();
        rightBox.innerHTML = `<div class="hint">Click a tag to list its pulses.</div>`;
      }
    });

    // layout – make graph **less dense**
    const sim = d3.forceSimulation(DATA.nodes)
      .force('link', d3.forceLink(links).id(d=>d.id).distance(92).strength(0.6))
      .force('charge', d3.forceManyBody().strength(-260))
      .force('center', d3.forceCenter(width/2, height/2))
      .force('collide', d3.forceCollide().radius(d => rScale(nodeScore(d))*1.15).iterations(1));

    const linkSel = linkLayer.selectAll('line')
      .data(links)
      .join('line')
      .attr('class','link');

    const nodeSel = nodeLayer.selectAll('g.node')
      .data(DATA.nodes, d=>d.id)
      .join(enter => {
        const g = enter.append('g').attr('class','node');

        g.append('ellipse')
          .attr('rx', d => rScale(nodeScore(d))*ellipseAspect)
          .attr('ry', d => rScale(nodeScore(d)));

        g.append('text')
          .attr('x', d => rScale(nodeScore(d))*ellipseAspect + 4)
          .attr('y', 4)
          .text(d => d.id);

        g.on('mouseover', (ev,d) => showTagTooltip(ev, d.id))
         .on('mousemove', moveTooltip)
         .on('mouseout', hideTooltip)
         .on('click', (ev,d) => { ev.stopPropagation(); onTagClick(d.id); });

        return g;
      });

    sim.on('tick', () => {
      linkSel
        .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
        .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);

      nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);
    });

    // tooltip
    function showTagTooltip(evt, tag){
      const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
      const deg  = degree.get(tag)||0;
      const n    = idToNode.get(tag);
      const cent = (typeof n?.centrality==='number') ? n.centrality.toFixed(2) : (deg||0);
      tooltip.html(
        `<div style="font-weight:700;margin-bottom:4px">${esc(tag)}</div>
         <div style="color:#97a3b6;margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
         <div style="white-space:pre-wrap;opacity:.92">${esc(desc)}</div>
         <div style="margin-top:6px;font-size:12px;color:#97a3b6">Click to list pulses</div>`
      ).style('display','block');
      moveTooltip(evt);
    }
    function moveTooltip(evt){
      const pad=12; tooltip.style('left',(evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px');
    }
    function hideTooltip(){ tooltip.style('display','none'); }

    // focus/highlight – only the clicked tag colored; neighbors dimmed
    function setFocus(tagId){
      const keep = new Set([tagId]);
      links.forEach(l => { if (l.source.id===tagId) keep.add(l.target.id); if (l.target.id===tagId) keep.add(l.source.id); });
      nodeSel
        .classed('dim', d => !keep.has(d.id))
        .classed('highlight', d => d.id===tagId);
      linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    }
    function clearFocus(){
      nodeSel.classed('dim', false).classed('highlight', false);
      linkSel.classed('dim', false);
    }

    // right sidebar list (one-line items)
    function renderRightList(tagId){
      const pulsesRaw = safeArray(DATA.pulsesByTag?.[tagId]);
      if (!pulsesRaw.length){
        rightBox.innerHTML = `<div class="hint">No pulses for <strong>${esc(tagId)}</strong>.</div>`;
        return;
      }

      // sort by date desc, dedupe by id|title|date
      const key = p => (p.id||'') + '|' + (p.title||'') + '|' + (p.date||'');
      const seen = new Set();
      const pulses = pulsesRaw
        .slice()
        .sort((a,b)=> String(b.date||'').localeCompare(String(a.date||'')))
        .filter(p => (seen.has(key(p)) ? false : (seen.add(key(p)), true)));

      let html = `<div class="hint" style="margin-bottom:6px">Pulses for <strong>${esc(tagId)}</strong></div>`;
      html += `<ul class="pulse-list">`;
      for (const p of pulses){
        const title = p.title || p.id || '(Pulse)';
        const when  = p.date ? ` (${p.date})` : '';
        html += `<li data-key="${esc(key(p))}"><span class="pulse-dot"></span><span class="ellipsis" title="${esc(title+when)}">${esc(title+when)}</span></li>`;
      }
      html += `</ul>`;
      rightBox.innerHTML = html;

      // click -> render pulse details in left panel
      rightBox.querySelectorAll('li').forEach(li=>{
        li.addEventListener('click', ()=>{
          const k = li.getAttribute('data-key');
          const p = pulses.find(x => key(x)===k);
          if (p) renderPulseLeft(p);
        });
      });
    }

    // left pulse details (smaller text, links truncated by CSS width)
    function renderPulseLeft(p){
      const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
      let html = `<h2>${esc(p.title||p.id||'Pulse')}${when}</h2>`;
      if (p.summary) html += `<div class="block" style="white-space:pre-wrap">${esc(p.summary)}</div>`;
      html += renderLinks('Papers', p.papers);
      html += renderLinks('Podcasts', p.podcasts);
      leftBox.innerHTML = html;
    }
    function renderLinks(label, items){
      if (!items || !items.length) return '';
      const norm = items.map(u => typeof u==='string' ? {title:u, url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
      let html = `<div class="block"><strong>${label}</strong><div>`;
      for (const it of norm){
        const title = it.title || it.url;
        const href  = it.url || it.title || '#';
        html += `<div class="ellipsis"><a href="${esc(href)}" target="_blank" rel="noopener">${esc(title)}</a></div>`;
      }
      html += `</div></div>`;
      return html;
    }

    // tag click
    function onTagClick(tagId){
      setFocus(tagId);
      renderRightList(tagId);
    }

    // search: dim everything except matching tags
    function applyFilter(q){
      const s = (q||'').trim().toLowerCase();
      if (!s){ clearFocus(); return; }
      const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
      nodeSel.classed('dim', d => !keep.has(d.id)).classed('highlight', false);
      linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    }
    if (search) search.addEventListener('input', e => applyFilter(e.target.value));

    // start state: **no** help text under the search box (by request)
    leftBox.innerHTML = '';
    rightBox.innerHTML = `<div class="hint">Click a tag to list its pulses.</div>`;
  }
})();
