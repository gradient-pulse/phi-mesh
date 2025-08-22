/* docs/map.js — Tag Map renderer (DOM-ready + Safari-safe) */
(function () {
  function init() {
    const svg = d3.select('#graph');
    if (svg.empty()) return;

    const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object')
      ? window.PHI_DATA
      : { nodes: [], links: [], tagDescriptions:{}, pulsesByTag:{} };

    const tooltip   = d3.select('#tooltip');
    const leftPane  = document.getElementById('sidebar-content');
    const rightUl   = document.getElementById('plist');
    const rightHead = document.getElementById('plist-title');
    const searchEl  = document.getElementById('search');

    function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
    function safeArr(x){return Array.isArray(x)?x:[]}

    // ViewBox from actual element size (works with CSS sizing)
    const vbW = svg.node().clientWidth  || 1200;
    const vbH = svg.node().clientHeight || 800;
    svg.attr('viewBox', `0 0 ${vbW} ${vbH}`);

    // ----- Config tweaks (less dense, smaller nodes) -----
    const width = vbW, height = vbH;
    const minR = 5, maxR = 18;
    const ellipseAspect = 1.5;

    // Layers & zoom
    const root = svg.append('g');
    const linkLayer = root.append('g').attr('class','links');
    const nodeLayer = root.append('g').attr('class','nodes');

    const zoom = d3.zoom().scaleExtent([0.35, 5]).on('zoom', ev => root.attr('transform', ev.transform));
    svg.call(zoom);

    // Background click clears everything
    svg.on('click', ev => {
      if (ev.target === svg.node()) {
        clearFocus();
        clearPulseDetails();
        clearPulseList();
        nodeSel.classed('active', false);
      }
    });

    // Prep data
    const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
    const links = DATA.links.map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    })).filter(l => l.source && l.target);

    // degree map for fallback sizing
    const degree = new Map();
    links.forEach(l => {
      degree.set(l.source.id, (degree.get(l.source.id)||0) + 1);
      degree.set(l.target.id, (degree.get(l.target.id)||0) + 1);
    });

    function nodeScore(d){
      const c = d.centrality;
      return (typeof c === 'number') ? c : ((degree.get(d.id) || 1));
    }

    const cMin = d3.min(DATA.nodes, n => nodeScore(n)) ?? 1;
    const cMax = d3.max(DATA.nodes, n => nodeScore(n)) ?? 1;
    const rScale = d3.scaleSqrt().domain([cMin || 0.0001, cMax || 1]).range([minR, maxR]);

    // Simulation (lighter, less dense)
    const sim = d3.forceSimulation(DATA.nodes)
      .force('link', d3.forceLink(links).id(d=>d.id).distance(90).strength(0.7))
      .force('charge', d3.forceManyBody().strength(-160))
      .force('center', d3.forceCenter(width/2, height/2))
      .force('collision', d3.forceCollide().radius(d => rScale(nodeScore(d))*1.15));

    const linkSel = linkLayer.selectAll('line')
      .data(links)
      .join('line')
      .attr('class','link');

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
         .on('click', (ev,d) => { ev.stopPropagation(); onTagClick(d.id, g); });

        return g;
      });

    sim.on('tick', () => {
      linkSel
        .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
        .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);

      nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);
    });

    // Tooltip (no satellites mention)
    function showTagTooltip(evt, tag){
      const desc = DATA.tagDescriptions?.[tag] || '—';
      const deg = degree.get(tag) || 0;
      const cent = (typeof idToNode.get(tag)?.centrality==='number')
        ? idToNode.get(tag).centrality.toFixed(2)
        : deg;
      tooltip.html(
        `<div style="font-weight:700;margin-bottom:4px">${esc(tag)}</div>`+
        `<div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>`+
        `<div style="white-space:pre-wrap;opacity:.92">${esc(desc)}</div>`+
        `<div style="margin-top:6px;font-size:12px;color:#97a3b6">Click to list pulses</div>`
      ).style('display','block');
      moveTooltip(evt);
    }
    function moveTooltip(evt){
      const pad=12; tooltip.style('left',(evt.clientX+pad)+'px').style('top',(evt.clientY+pad)+'px');
    }
    function hideTooltip(){ tooltip.style('display','none'); }

    // Focus helpers
    function setFocus(keepIds){
      const keep = new Set(keepIds);
      nodeSel.classed('dim', d => !keep.has(d.id));
      linkSel.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    }
    function clearFocus(){
      nodeSel.classed('dim', false);
      linkSel.classed('dim', false);
      nodeSel.classed('active', false);
    }

    // Right panel pulse list
    function clearPulseList(){
      rightHead.textContent = 'Pulses';
      rightUl.innerHTML = `<div class="muted">Click a tag to list its pulses.</div>`;
    }
    function renderPulseList(tagId){
      const pulses = safeArr(DATA.pulsesByTag?.[tagId]);
      rightHead.textContent = `Pulses for ${tagId}`;
      if (!pulses.length){
        rightUl.innerHTML = `<div class="muted">No pulses recorded for this tag.</div>`;
        return;
      }
      const dots = {
        verynew:'#ff7a66', new:'#ff9966', mid:'#ffb066', old:'#86cbff', veryold:'#74a9ff'
      };
      function colorForAge(days){
        if (days == null) return dots.old;
        if (days <= 14)  return dots.verynew;
        if (days <= 45)  return dots.new;
        if (days <= 120) return dots.mid;
        if (days <= 270) return dots.old;
        return dots.veryold;
      }
      rightUl.innerHTML = '';
      for (const p of pulses){
        const li = document.createElement('div');
        li.className = 'pitem';
        const dot = document.createElement('div');
        dot.className = 'pdot';
        dot.style.background = colorForAge(p.ageDays);
        const title = document.createElement('div');
        const dt = p.date ? ` (${p.date})` : '';
        title.className='ptitle ellipsis';
        title.textContent = (p.title || p.id || 'Pulse') + dt;
        li.appendChild(dot); li.appendChild(title);
        li.onclick = (ev)=>{ ev.stopPropagation(); showPulseDetails(p); };
        rightUl.appendChild(li);
      }
    }

    // Left panel pulse details (compact)
    function clearPulseDetails(){
      leftPane.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
    }
    function linksBlock(label, items){
      if (!items?.length) return '';
      const norm = items.map(u => typeof u==='string' ? {title:u, url:u} :
        (u?.url ? u : {title:(u?.title||u?.url), url:(u?.url||'')}));
      let html = `<div class="block-title">${label}</div><ul class="linklist">`;
      for (const it of norm){
        const t = it.title || it.url || '';
        const u = it.url || it.title || '#';
        html += `<li><a class="ellipsis" href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a></li>`;
      }
      html += `</ul>`;
      return html;
    }
    function showPulseDetails(p){
      const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
      let html = `<h2>${esc(p.title || p.id || 'Pulse')}${when}</h2>`;
      if (p.summary) html += `<div class="summary" style="white-space:pre-wrap">${esc(p.summary)}</div>`;
      html += linksBlock('Papers', p.papers);
      html += linksBlock('Podcasts', p.podcasts);
      leftPane.innerHTML = html;
    }

    // Tag click handler (highlight + list)
    function onTagClick(tagId, nodeG){
      // highlight active tag
      nodeSel.classed('active', d => d.id === tagId);
      // focus to neighbors (+ self)
      const keep = new Set([tagId]);
      links.forEach(l => {
        if (l.source.id===tagId) keep.add(l.target.id);
        if (l.target.id===tagId) keep.add(l.source.id);
      });
      setFocus(keep);
      // replace right list
      renderPulseList(tagId);
    }

    // Search filter
    function applyFilter(q){
      const s = (q||'').trim().toLowerCase();
      if (!s){ clearFocus(); return; }
      const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(s)).map(n=>n.id));
      setFocus(keep);
    }
    if (searchEl) searchEl.addEventListener('input', e => applyFilter(e.target.value));

    // Initial states
    clearPulseDetails();
    clearPulseList();
  }

  // DOM ready guard (works with/without defer)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
