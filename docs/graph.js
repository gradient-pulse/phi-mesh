/* docs/graph.js — spiral satellites, dimming, ovals, less density, tidy sidebar links
   Expects window.PHI_DATA = { nodes, links, tagDescriptions?, tagResources?, pulsesByTag? }
*/
(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // DOM
  const svg = d3.select('#graph');
  const sidebar = document.getElementById('sidebar');
  const tooltip = d3.select('#tooltip');
  const searchInput = document.getElementById('tag-search');

  // sizing
  const width = svg.node().clientWidth || 1200;
  const height = svg.node().clientHeight || 800;

  // node ellipse size (oval, not round)
  const rx = 9, ry = 6;                 // tag node ellipse radii
  const labelDx = rx + 3, labelDy = 3;

  // link styling
  const LINK_OPA = 0.30;
  const LINK_OPA_DIM = 0.10;

  // simulation tunables to reduce density
  const LINK_DIST = 110;
  const CHARGE = -340;
  const COLLIDE_R = 12;                 // mild padding to reduce overlaps

  // age color (newer warmer)
  function ageColor(ageDays) {
    if (ageDays == null) return "#8fbfff";
    if (ageDays <= 14) return "#ff8161";
    if (ageDays <= 45) return "#ffb36e";
    if (ageDays <= 120) return "#ffd07e";
    if (ageDays <= 270) return "#a8c9ff";
    return "#8fbfff";
  }

  // Build graph layers
  svg.attr('viewBox', [0, 0, width, height].join(' '));
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class', 'links');
  const nodeLayer = root.append('g').attr('class', 'nodes');
  const satLayer  = root.append('g').attr('class', 'sats');

  const zoom = d3.zoom().scaleExtent([0.35, 5]).on('zoom', (ev) => root.attr('transform', ev.transform));
  svg.call(zoom);

  // map id -> node object
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = DATA.links
    .map(l => ({ source: idToNode.get(l.source) || l.source, target: idToNode.get(l.target) || l.target }))
    .filter(l => l.source && l.target);

  // simulation
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(LINK_DIST).strength(0.75))
    .force('charge', d3.forceManyBody().strength(CHARGE))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collide', d3.forceCollide().radius(COLLIDE_R));

  // render links
  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link')
    .attr('opacity', LINK_OPA);

  // render nodes (oval ellipses)
  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter => {
      const g = enter.append('g').attr('class','node');
      g.append('ellipse').attr('rx', rx).attr('ry', ry);
      g.append('text').attr('x', labelDx).attr('y', labelDy).text(d=>d.id);

      // interactions
      g.on('mouseover', (ev,d)=> showTagTooltip(ev, d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
       .on('click', (_ev,d)=> onTagClick(d.id));

      return g;
    });

  // tick
  sim.on('tick', () => {
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);

    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // position satellites (spiral is static off host pos)
    satLayer.selectAll('circle.sat-dot').attr('cx', d=>d._x).attr('cy', d=>d._y);
  });

  // ---------------- Tooltip ----------------
  const esc = (s)=> String(s||'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'})[c]);

  function showTagTooltip(evt, tag) {
    const desc = DATA.tagDescriptions?.[tag] || '';
    tooltip.html(
      `<div class="t-h">${esc(tag)}</div>`+
      `<div class="t-d">${esc(desc || '—')}</div>`+
      `<div class="t-hint">Click to reveal pulse satellites</div>`
    ).style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad=14;
    tooltip.style('left', (evt.clientX+pad)+'px').style('top', (evt.clientY+pad)+'px');
  }
  function hideTooltip(){ tooltip.style('display','none'); }

  // ---------------- Sidebar ----------------
  function sidebarPulse(p){
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : '';
    let html = `<div class="details"><h2>${esc(p.title||p.id||'Pulse')}${when}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.4rem 0 1rem 0">${esc(p.summary)}</div>`;

    const papers = Array.isArray(p.papers)? p.papers : [];
    const pods = Array.isArray(p.podcasts)? p.podcasts : [];

    if (papers.length){
      html += `<div class="muted" style="margin:.6rem 0 .2rem 0">Papers</div><div class="linklist">`;
      for(const it of papers){
        if (typeof it==='string'){
          html += `<a href="${it}" target="_blank" rel="noopener">${esc(it)}</a>`;
        }else if (it && (it.url||it.doi||it.link)){
          const url = it.url || it.doi || it.link;
          const label = it.title ? `${it.title}` : url;
          html += `<a href="${url}" target="_blank" rel="noopener">${esc(label)}</a>`;
        }
      }
      html += `</div>`;
    }
    if (pods.length){
      html += `<div class="muted" style="margin:.6rem 0 .2rem 0">Podcasts</div><div class="linklist">`;
      for(const u of pods){
        if (typeof u==='string') html += `<a href="${u}" target="_blank" rel="noopener">${esc(u)}</a>`;
        else if (u && u.url) html += `<a href="${u.url}" target="_blank" rel="noopener">${esc(u.url)}</a>`;
      }
      html += `</div>`;
    }

    html += `</div>`;
    sidebar.innerHTML = html;
  }

  // ---------------- Satellites (spiral) ----------------
  let focusedTag = null;

  function onTagClick(tagId){
    focusedTag = tagId;
    drawSatellites(tagId);
    applyFocusDimming(tagId);
  }

  function drawSatellites(tagId){
    // nuke old
    satLayer.selectAll('*').remove();

    const host = idToNode.get(tagId);
    if (!host) return;
    const pulses = (DATA.pulsesByTag?.[tagId] || []);
    if (!pulses.length) return;

    // Archimedean spiral around host — ensure close spacing
    const TWO_PI = Math.PI*2;
    const n = pulses.length;
    const a = 26;          // spiral start radius
    const b = 10;          // radial growth per turn (smaller => tighter spiral)
    const turnEvery = 8;   // dots per loop to keep visual spiral

    const sorted = [...pulses].sort((a,b)=> (a.ageDays??9e9) - (b.ageDays??9e9)); // newest first (warmer)

    const sat = satLayer.selectAll('circle.sat-dot')
      .data(sorted.map((p,i)=>{
        const theta = (i/turnEvery)*TWO_PI;
        const r = a + b*theta;
        const x = host.x + r*Math.cos(theta);
        const y = host.y + r*Math.sin(theta);
        return { ...p, _x:x, _y:y, _i:i };
      }), d=> d.id || d.title || `${tagId}:${d.date || d._i}`);

    sat.enter()
      .append('circle')
      .attr('class','sat-dot')
      .attr('r', 4.2)
      .attr('fill', d=> ageColor(d.ageDays))
      .attr('cx', d=>d._x)
      .attr('cy', d=>d._y)
      .on('click', (_ev,d)=> sidebarPulse(d));
  }

  // Dimming: keep host + its neighbors + satellites vivid; dim rest
  function applyFocusDimming(tagId){
    // collect neighbor ids
    const keep = new Set([tagId]);
    links.forEach(l=>{
      const a=l.source.id||l.source, b=l.target.id||l.target;
      if (a===tagId) keep.add(b);
      if (b===tagId) keep.add(a);
    });

    nodeSel.classed('dim', d=> !keep.has(d.id));
    linkSel
      .classed('dim', d=> !(keep.has(d.source.id) && keep.has(d.target.id)))
      .attr('opacity', d=> (keep.has(d.source.id) && keep.has(d.target.id)) ? LINK_OPA : LINK_OPA_DIM);

    // satellites inherit by being a separate layer (not dimmed)
  }

  // clicking empty background clears focus
  svg.on('click', (ev)=>{
    // ignore if a node/sat handled it
    if (ev.target.closest('.node, .sat-dot')) return;

    focusedTag = null;
    satLayer.selectAll('*').remove();
    nodeSel.classed('dim', false);
    linkSel.classed('dim', false).attr('opacity', LINK_OPA);
    // keep sidebar content; no reset text
  });

  // ---------------- Search ----------------
  function applyFilter(q){
    const s = (q||'').trim().toLowerCase();
    if (!s){
      nodeSel.classed('dim', false);
      linkSel.classed('dim', false).attr('opacity', LINK_OPA);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n=> n.id.toLowerCase().includes(s)).map(n=>n.id));
    nodeSel.classed('dim', d=> !keep.has(d.id));
    linkSel.classed('dim', d=> !(keep.has(d.source.id) && keep.has(d.target.id)))
           .attr('opacity', d=> (keep.has(d.source.id) && keep.has(d.target.id)) ? LINK_OPA : LINK_OPA_DIM);
  }
  if (searchInput) searchInput.addEventListener('input', (e)=> applyFilter(e.target.value));
})();
