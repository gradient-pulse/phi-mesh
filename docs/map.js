/* docs/map.js — renderer (data comes from window.PHI_DATA in docs/data.js) */
(function () {
  // Guard until DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    const DATA = (window.PHI_DATA && typeof window.PHI_DATA === 'object')
      ? window.PHI_DATA
      : { nodes: [], links: [], pulsesByTag: {}, tagDescriptions: {} };

    // --- DOM targets ---
    const svg = d3.select('#graph');
    if (!svg.node()) return;

    const leftBox  = document.getElementById('sidebar-content'); // pulse details
    const rightBox = document.getElementById('pulse-list');      // list of pulses for a tag
    const search   = document.getElementById('search');

    // Wipe the left “hint” forever (per request)
    if (leftBox) leftBox.innerHTML = "";

    // Tooltip (singleton)
    const tt = d3.select('#tooltip').style('display','none');

    // --- Sizing & layers ---
    const w = svg.node().clientWidth  || 1200;
    const h = svg.node().clientHeight || 800;
    svg.attr('viewBox', `0 0 ${w} ${h}`);

    const root      = svg.append('g');
    const linkLayer = root.append('g').attr('class','links');
    const nodeLayer = root.append('g').attr('class','nodes');

    // zoom/pan
    svg.call(d3.zoom().scaleExtent([0.35, 4]).on('zoom', (ev)=>root.attr('transform', ev.transform)));

    // --- Prep data ---
    const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
    const links = (DATA.links || [])
      .map(l => ({ source: idToNode.get(l.source) || l.source, target: idToNode.get(l.target) || l.target }))
      .filter(l => l.source && l.target);

    // degree for fallback sizing
    const degree = new Map();
    links.forEach(l => {
      degree.set(l.source.id, (degree.get(l.source.id)||0)+1);
      degree.set(l.target.id, (degree.get(l.target.id)||0)+1);
    });

    // size scale (smaller/lighter than before)
    const mins = d3.min(DATA.nodes, d => (typeof d.centrality==='number') ? d.centrality : (degree.get(d.id)||0)) ?? 0;
    const maxs = d3.max(DATA.nodes, d => (typeof d.centrality==='number') ? d.centrality : (degree.get(d.id)||1)) ?? 1;
    const rScale = d3.scaleSqrt().domain([mins || 0.0001, maxs || 1]).range([5, 20]); // slightly smaller
    const ellipseAspect = 1.55;

    function nodeScore(d){
      const c = d.centrality;
      return (typeof c === 'number') ? c : ((degree.get(d.id)||1));
    }

    // --- Simulation (a bit looser) ---
    const sim = d3.forceSimulation(DATA.nodes)
      .force('link', d3.forceLink(links).id(d=>d.id).distance(85).strength(0.6))
      .force('charge', d3.forceManyBody().strength(-220))
      .force('center', d3.forceCenter(w/2, h/2))
      .force('collide', d3.forceCollide().radius(d => rScale(nodeScore(d))*1.15));

    // --- Draw ---
    const link = linkLayer.selectAll('line')
      .data(links)
      .join('line')
      .attr('class','link')
      .attr('stroke','#b9c7dd')
      .attr('stroke-opacity', 0.22);

    const node = nodeLayer.selectAll('g.node')
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

        g.on('mouseover', (ev,d)=>showTip(ev, d))
         .on('mousemove', moveTip)
         .on('mouseout', hideTip)
         .on('click', (ev,d)=>{ ev.stopPropagation(); onTagClick(d.id); });

        return g;
      });

    sim.on('tick', () => {
      link
        .attr('x1', d=>d.source.x)
        .attr('y1', d=>d.source.y)
        .attr('x2', d=>d.target.x)
        .attr('y2', d=>d.target.y);

      node.attr('transform', d=>`translate(${d.x},${d.y})`);
    });

    // background click clears everything
    svg.on('click', () => {
      activeTag = null;
      node.classed('dim', false).classed('active', false);
      link.classed('dim', false);
      if (rightBox) rightBox.innerHTML = `<div class="muted">Click a tag to list its pulses.</div>`;
      if (leftBox) leftBox.innerHTML = "";
    });

    // --- Tooltip ---
    function showTip(evt, d){
      const deg = degree.get(d.id) || 0;
      const cent = (typeof d.centrality==='number') ? d.centrality.toFixed(2) : deg;
      const desc = (DATA.tagDescriptions && DATA.tagDescriptions[d.id]) ? DATA.tagDescriptions[d.id] : '—';
      tt.html(`
        <div style="font-weight:700; margin-bottom:4px">${escapeHTML(d.id)}</div>
        <div class="muted" style="margin-bottom:6px">degree ${deg} • centrality ${cent}</div>
        <div style="white-space:pre-wrap; opacity:.92">${escapeHTML(desc)}</div>
        <div style="margin-top:6px; font-size:12px; color:#97a3b6">Click to list pulses</div>
      `).style('display','block');
      moveTip(evt);
    }
    function moveTip(evt){ const p=12; tt.style('left',(evt.clientX+p)+'px').style('top',(evt.clientY+p)+'px'); }
    function hideTip(){ tt.style('display','none'); }

    // --- Focus / dimming ---
    function setFocus(keepIds){
      const keep = new Set(keepIds);
      node.classed('dim', d => !keep.has(d.id));
      link.classed('dim', d => !(keep.has(d.source.id) && keep.has(d.target.id)));
    }
    function clearFocus(){ node.classed('dim', false); link.classed('dim', false); }

    // --- Tag click -> highlight + right list ---
    let activeTag = null;

    function onTagClick(tag){
      activeTag = tag;

      // highlight ONLY clicked tag
      node.classed('active', d => d.id === tag);

      // dim to clicked tag + its neighbors
      const keep = new Set([tag]);
      links.forEach(l => {
        if (l.source.id === tag) keep.add(l.target.id);
        if (l.target.id === tag) keep.add(l.source.id);
      });
      setFocus(keep);

      // fill right sidebar with deduped, newest-first single-line list
      if (!rightBox) return;

      const raw = Array.isArray(DATA.pulsesByTag?.[tag]) ? DATA.pulsesByTag[tag] : [];
      // dedupe by (id || title || date) “key”
      const seen = new Set();
      const unique = [];
      for (const p of raw) {
        const k = p.id || p.title || (p.date || Math.random().toString(36).slice(2));
        if (!seen.has(k)) { seen.add(k); unique.push(p); }
      }
      unique.sort((a,b) => (b.date||'').localeCompare(a.date||''));

      const header = `<div class="list-title">Pulses for <span class="tag">${escapeHTML(tag)}</span></div>`;
      const items  = unique.map(p => {
        const label = (p.title || p.id || '(untitled)') + (p.date ? ` (${p.date})` : '');
        return `<li><button class="pill" data-pid="${escapeHTML(p.id || '')}" data-title="${escapeHTML(p.title||'')}"
                data-date="${escapeHTML(p.date||'')}">${escapeHTML(label)}</button></li>`;
      }).join('');

      rightBox.innerHTML = `${header}<ul class="pulse-list">${items || '<li class="muted">No pulses.</li>'}</ul>`;

      // wire pulse click -> show details (left)
      rightBox.querySelectorAll('button.pill').forEach(btn => {
        btn.onclick = () => {
          const p = findPulse(btn.dataset.pid, btn.dataset.title, btn.dataset.date, unique);
          if (p) showPulse(p);
        };
      });
    }

    function findPulse(id, title, date, pool){
      // robust match across shapes
      return pool.find(p =>
        (id && p.id===id) ||
        (title && p.title===title) ||
        (date && p.date===date)
      ) || null;
    }

    // --- Show pulse details (left) ---
    function showPulse(p){
      if (!leftBox) return;
      const when = p.date ? ` <span class="muted">(${escapeHTML(p.date)})</span>` : '';
      let html = `<h2 style="margin:0 0 .6rem 0">${escapeHTML(p.title || p.id || 'Pulse')}${when}</h2>`;
      if (p.summary) html += `<div style="white-space:pre-wrap; margin:.2rem 0 0.6rem 0">${escapeHTML(p.summary)}</div>`;
      html += renderLinks('Papers', p.papers);
      html += renderLinks('Podcasts', p.podcasts);
      leftBox.innerHTML = html;
    }

    function renderLinks(label, items){
      if (!items || !items.length) return '';
      const norm = items.map(u => (typeof u==='string') ? {title:u, url:u} : (u?.url ? u : {title:u?.title||u?.url, url:u?.url||''}));
      const lis = norm.map(it => {
        const t = it.title || it.url || '';
        const u = it.url || it.title || '#';
        return `<li><a class="ellipsis" href="${escapeHTML(u)}" target="_blank" rel="noopener">${escapeHTML(t)}</a></li>`;
      }).join('');
      return `<div class="links"><div class="label">${label}</div><ul>${lis}</ul></div>`;
    }

    // --- Search (dimming) ---
    if (search) {
      search.addEventListener('input', e => {
        const q = (e.target.value || '').trim().toLowerCase();
        if (!q) { clearFocus(); return; }
        const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(q)).map(n=>n.id));
        setFocus(keep);
      });
    }

    // --- helpers ---
    function escapeHTML(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
  }
})();
