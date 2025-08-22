/* Tag Map renderer (expects window.PHI_DATA from docs/data.js) */
(function () {
  function init() {
    const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object')
      ? window.PHI_DATA
      : { nodes: [], links: [], tagDescriptions: {}, pulsesByTag: {} };

    // ----- DOM -----
    const svgSel = d3.select('#graph');
    const svgNode = svgSel.node();
    if (!svgNode) return;

    const tooltip = d3.select('#tooltip');
    const sidebar = document.getElementById('sidebar-content');
    const searchInput = document.getElementById('search');
    const tray = document.getElementById('pulse-tray');

    function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
    function safeArray(x){return Array.isArray(x)?x:[]}
    function clip(s, n){ s=String(s||''); return s.length>n ? s.slice(0,n-1)+'…' : s; }

    // ----- Config -----
    const width  = svgNode.clientWidth  || 1200;
    const height = svgNode.clientHeight || 800;

    const minR = 6, maxR = 24;
    const ellipseAspect = 1.6;
    const linkOpacity = 0.18;

    const satDot = 4.6;
    const spiralStepR = 8;
    const spiralStepTheta = 0.48 * Math.PI;
    const spiralStartR = 52;
    const SATELLITE_MAX = 16; // draw spiral only up to this many pulses

    // age helpers
    function ageClass(d){
      const a = d?.ageDays;
      if (a == null) return 'age-old';
      if (a <= 14)  return 'age-very-new';
      if (a <= 45)  return 'age-new';
      if (a <= 120) return 'age-mid';
      if (a <= 270) return 'age-old';
      return 'age-very-old';
    }
    function ageIdx(d){
      const a = d?.ageDays;
      if (a == null) return 3;
      if (a <= 14)  return 0;
      if (a <= 45)  return 1;
      if (a <= 120) return 2;
      if (a <= 270) return 3;
      return 4;
    }

    // ----- Layers & zoom -----
    svgSel.attr('viewBox', `0 0 ${width} ${height}`);
    const root = svgSel.append('g');

    // full-size transparent rect to reliably capture background clicks
    root.append('rect').attr('class','bgcatch').attr('x',0).attr('y',0).attr('width',width).attr('height',height);

    const linkLayer = root.append('g').attr('class','links');
    const nodeLayer = root.append('g').attr('class','nodes');
    const satLayer  = root.append('g').attr('class','satellites');

    const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform));
    svgSel.call(zoom);

    // Clear selection on background click
    root.on('click', (ev) => {
      if (ev.target && ev.target.classList && ev.target.classList.contains('bgcatch')) {
        clearSatellites();
        clearFocus();
        sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers &amp; podcasts.</div>`;
        renderTray(null, []);
      }
    });

    // ----- Prep graph data -----
    const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
    const links = DATA.links
      .map(l => ({
        source: idToNode.get(l.source) || l.source,
        target: idToNode.get(l.target) || l.target
      }))
      .filter(l => l.source && l.target);

    // degree fallback for sizing
    const degree = new Map();
    links.forEach(l => {
      degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
      degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
    });

    const centralities = DATA.nodes.map(n =>
      (typeof n.centrality === 'number' ? n.centrality : degree.get(n.id)||0)
    );
    const cMin = d3.min(centralities) ?? 0, cMax = d3.max(centralities) ?? 1;
    const rScale = d3.scaleSqrt().domain([cMin || 0.0001, cMax || 1]).range([minR, maxR]);

    // Safari-safe node score
    function nodeScore(d){
      const c = d.centrality;
      return (typeof c === 'number') ? c : (degree.get(d.id) || 1);
    }

    // ----- Simulation (LESS DENSE) -----
    const sim = d3.forceSimulation(DATA.nodes)
      .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(0.7))
      .force('charge', d3.forceManyBody().strength(-230))
      .force('center', d3.forceCenter(width/2, height/2))
      .force('collision', d3.forceCollide().radius(d => rScale(nodeScore(d))*1.1));

    const linkSel = linkLayer.selectAll('line')
      .data(links)
      .join('line')
      .attr('class','link')
      .attr('stroke-opacity', linkOpacity);

    const nodeSel = nodeLayer.selectAll('g.node')
      .data(DATA.nodes, d=>d.id)
      .join(enter => {
        const g = enter.append('g').attr('class','node');

        g.append('ellipse')
          .attr('rx', d => rScale(nodeScore(d)) * ellipseAspect)
          .attr('ry', d => rScale(nodeScore(d)));

        g.append('text')
          .attr('x', d => rScale(nodeScore(d)) * ellipseAspect + 4)
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
        .attr('x1', d=>d.source.x)
        .attr('y1', d=>d.source.y)
        .attr('x2', d=>d.target.x)
        .attr('y2', d=>d.target.y);

      nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

      // keep satellites aligned to host
      satLayer.selectAll('g.satellite')
        .attr('transform', d => `translate(${d.host.x + d._xoff},${d.host.y + d._yoff})`);
    });

    // ----- Tooltip -----
    function showTagTooltip(evt, tag) {
      const desc = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) ? DATA.tagDescriptions[tag] : '—';
      const n = idToNode.get(tag);
      const deg = degree.get(tag) || 0;
      const cent = (typeof n?.centrality==='number') ? n.centrality.toFixed(2) : (deg||0);
      tooltip.html(`
        <div style="font-weight:700; margin-bottom:4px">${esc(tag)}</div>
        <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
        <div style="white-space:pre-wrap; opacity:.92">${esc(desc)}</div>
        <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to reveal pulse satellites</div>
      `).style('display','block');
      moveTooltip(evt);
    }
    function moveTooltip(evt){
      const pad=12; tooltip.style('left', (evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px');
    }
    function hideTooltip(){ tooltip.style('display','none'); }

    // ----- Focus & dimming -----
    function setFocus(keepIds){
      const keep = new Set(keepIds);
      nodeSel.classed('dim', d => !keep.has(d.id));
      linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    }
    function clearFocus(){
      nodeSel.classed('dim', false);
      linkSel.classed('dim', false);
    }

    // ----- Satellites (spiral/list) -----
    let currentTag = null;

    function clearSatellites(){
      currentTag = null;
      satLayer.selectAll('*').remove();
    }

    function placeSpiralOffsets(n){
      const out = [];
      for (let i=0;i<n;i++){
        const r = spiralStartR + i*spiralStepR;
        const t = i*spiralStepTheta;
        out.push({ _xoff: r*Math.cos(t), _yoff: r*Math.sin(t) });
      }
      return out;
    }

    function onTagClick(tagId){
      currentTag = tagId;

      // focus to neighbors of tagId (+ itself)
      const neighbors = new Set([tagId]);
      links.forEach(l => {
        if (l.source.id===tagId) neighbors.add(l.target.id);
        if (l.target.id===tagId) neighbors.add(l.source.id);
      });
      setFocus(neighbors);

      // satellites + tray
      satLayer.selectAll('*').remove();
      const host = idToNode.get(tagId);
      const pulses = safeArray(DATA.pulsesByTag?.[tagId]);

      // Always show the list on the right
      renderTray(tagId, pulses);

      // Only draw spiral if not too many pulses
      if (host && pulses.length && pulses.length <= SATELLITE_MAX){
        const offs = placeSpiralOffsets(pulses.length);
        const g = satLayer.selectAll('g.satellite')
          .data(pulses.map((p,i)=>({...p, host, ...offs[i]})), d => d.id || d.title || (d.date||'') );

        const enter = g.enter().append('g').attr('class','satellite');

        enter.append('circle')
          .attr('r', satDot)
          .attr('class', d => ageClass(d));

        enter.append('text')
          .attr('y', -9)
          .attr('text-anchor','middle')
          .attr('font-size', 9)
          .attr('fill', '#a3b3c7')
          .text(d => d.date ? d.date.slice(2,10) : '');

        enter.on('click', (ev,d) => { ev.stopPropagation(); showPulseDetails(d); });
      }

      // clear old pulse body when selecting a tag
      sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers &amp; podcasts.</div>`;

      sim.alpha(0.5).restart();
    }

    // ----- Right tray -----
    function renderTray(tagId, pulses){
      tray.innerHTML = '';
      const title = document.createElement('div');
      title.className='trayTitle';
      title.textContent = tagId ? `Pulses for ${tagId}` : 'Pulses';
      tray.appendChild(title);

      if (!pulses || !pulses.length){
        const em = document.createElement('div');
        em.className='trayEmpty';
        em.textContent = tagId ? 'No pulses found for this tag.' : 'Click a tag to list its pulses.';
        tray.appendChild(em);
        return;
      }

      const sorted = [...pulses].sort((a,b)=>String(b.date||'').localeCompare(String(a.date||'')));

      for (const p of sorted){
        const row = document.createElement('div');
        row.className='pulseRow';
        row.title = p.title || p.id || '';
        const dot = document.createElement('div');
        dot.className = 'dot pAge' + ageIdx(p);
        const label = document.createElement('div');
        const dt = p.date ? ` ${p.date}` : '';
        label.textContent = clip((p.title || p.id || 'Pulse') + dt, 40);
        row.appendChild(dot);
        row.appendChild(label);
        row.addEventListener('click', (ev)=>{ ev.stopPropagation(); showPulseDetails(p); });
        tray.appendChild(row);
      }
    }

    // ----- Left sidebar pulse details -----
    function renderLinksBlock(label, items){
      if (!items?.length) return '';
      const norm = items.map(u => typeof u==='string' ? {title:u, url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
      let html = `<div style="margin-top:8px"><strong>${label}</strong><ul style="padding-left:18px; margin:6px 0 0 0">`;
      for (const it of norm){
        const title = it.title || it.url;
        const href  = it.url || it.title || '#';
        html += `<li><a class="ellipsis" href="${esc(href)}" target="_blank" rel="noopener">${esc(clip(title, 40))}</a></li>`;
      }
      html += `</ul></div>`;
      return html;
    }

    function showPulseDetails(p){
      const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
      let html = `<h2>${esc(clip(p.title || p.id || 'Pulse', 60))}${when}</h2>`;
      if (p.summary) html += `<div class="body" style="white-space:pre-wrap; margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;
      html += renderLinksBlock('Papers', p.papers);
      html += renderLinksBlock('Podcasts', p.podcasts);
      sidebar.innerHTML = html;
    }

    // ----- Search -----
    function applyFilter(q){
      const s = (q||'').trim().toLowerCase();
      if (!s){ clearFocus(); return; }
      const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
      setFocus(keep);
    }
    if (searchInput) searchInput.addEventListener('input', e => applyFilter(e.target.value));
  }

  if (document.getElementById('graph')) {
    init();
  } else {
    window.addEventListener('DOMContentLoaded', init, { once:true });
  }
})();
