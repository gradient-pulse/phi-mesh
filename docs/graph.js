/* docs/graph.js (2025-08-20b)
   - Slightly brighter links, no node rim
   - Sidebar links truncated to one line
   - Satellites show; spiral layout auto for large sets
*/

(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [], tagDescriptions:{}, pulsesByTag:{} };

  // ---------- DOM ----------
  const svg = d3.select('#graph');
  const sidebar = document.getElementById('sidebar');
  const search = document.getElementById('tag-search');

  const W = svg.node().clientWidth || 1200;
  const H = svg.node().clientHeight || 800;

  svg.attr('viewBox', `0 0 ${W} ${H}`);
  const root = svg.append('g');
  const linkLayer = root.append('g').attr('class', 'links');
  const nodeLayer = root.append('g').attr('class', 'nodes');
  const satLayer  = root.append('g').attr('class', 'satellites');

  const zoom = d3.zoom().scaleExtent([0.35, 4]).on('zoom', (e)=>root.attr('transform', e.transform));
  svg.call(zoom);

  // ---------- helpers ----------
  const id2node = new Map(DATA.nodes.map(n=>[n.id, n]));
  const links = DATA.links.map(l => ({
    source: id2node.get(l.source) || l.source,
    target: id2node.get(l.target) || l.target
  })).filter(l=>l.source && l.target);

  const nodeRadius = 8;                    // a notch smaller (more labels fit)
  const satSize = 4.2;

  // pulse age bucket -> class (warmer = newer)
  function ageClass(age) {
    if (age == null) return 'p4';
    if (age <= 14) return 'p0';
    if (age <= 45) return 'p1';
    if (age <= 120) return 'p2';
    if (age <= 270) return 'p3';
    return 'p4';
  }

  function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}

  // Display a pulse in sidebar (summary + papers + podcasts)
  function showPulseDetails(p) {
    let html = `<h2>${esc(p.title || p.id || 'Pulse')}${p.date ? ` <span class="muted">(${esc(p.date)})</span>`:''}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;

    const papers = Array.isArray(p.papers) ? p.papers : [];
    const pods = Array.isArray(p.podcasts) ? p.podcasts : [];

    if (papers.length){
      html += `<div style="margin:.6rem 0 .25rem 0"><strong>Papers</strong></div>`;
      html += `<div>`;
      for (const it of papers){
        const u = typeof it === 'string' ? it : (it.url || '');
        const label = typeof it === 'string' ? shortLinkText(u) : (it.title || shortLinkText(u));
        html += `<a class="truncate" href="${esc(u)}" target="_blank" rel="noopener">${esc(label)}</a>`;
      }
      html += `</div>`;
    }
    if (pods.length){
      html += `<div style="margin:.8rem 0 .25rem 0"><strong>Podcasts</strong></div>`;
      html += `<div>`;
      for (const u of pods){
        const url = typeof u === 'string' ? u : (u.url || '');
        html += `<a class="truncate" href="${esc(url)}" target="_blank" rel="noopener">${esc(shortLinkText(url))}</a>`;
      }
      html += `</div>`;
    }

    sidebar.innerHTML = html;
  }

  function shortLinkText(url){
    try{
      const u = new URL(url);
      const parts = u.pathname.split('/').filter(Boolean);
      const tail = parts.length ? parts[parts.length-1] : '';
      return `${u.host}/…/${tail}`;
    }catch(_e){ return url; }
  }

  // ---------- simulation ----------
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(75).strength(0.7))
    .force('charge', d3.forceManyBody().strength(-180))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide().radius(nodeRadius*1.9));

  const linkSel = linkLayer.selectAll('line')
    .data(links)
    .join('line')
    .attr('class','link');

  const nodeSel = nodeLayer.selectAll('g.node')
    .data(DATA.nodes, d=>d.id)
    .join(enter=>{
      const g = enter.append('g').attr('class','node');
      g.append('circle').attr('r', nodeRadius);
      g.append('text')
        .attr('x', nodeRadius + 3)
        .attr('y', 3)
        .text(d=>d.id);

      g.on('mouseover', (e,d)=>showTagTooltip(e,d.id))
       .on('mousemove', moveTooltip)
       .on('mouseout', hideTooltip)
       .on('click', (_e,d)=>onTagClick(d.id));

      return g;
    });

  sim.on('tick', ()=>{
    linkSel
      .attr('x1', d=>d.source.x).attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    nodeSel.attr('transform', d=>`translate(${d.x},${d.y})`);

    // keep satellites glued to their host
    satLayer.selectAll('g.satellite').attr('transform', d=>{
      const r = d._r, a = d._a;
      return `translate(${d.host.x + r*Math.cos(a)}, ${d.host.y + r*Math.sin(a)})`;
    });
  });

  // ---------- tooltip ----------
  const tip = d3.select('body').append('div')
    .style('position','fixed').style('z-index',1000)
    .style('background','#0f1624').style('border','1px solid rgba(255,255,255,0.08)')
    .style('padding','10px 12px').style('border-radius','10px')
    .style('box-shadow','0 6px 24px rgba(0,0,0,.35)').style('display','none')
    .style('max-width','320px').style('color','#eaf1ff');

  function showTagTooltip(evt, tag){
    const d = (DATA.tagDescriptions && DATA.tagDescriptions[tag]) || '';
    const deg = (DATA.meta?.degree && DATA.meta.degree[tag]) ?? null;
    const cent = (DATA.meta?.centrality && DATA.meta.centrality[tag]) ?? null;
    const metrics = (deg!=null || cent!=null) ? `<div class="muted" style="margin-top:4px">degree ${deg ?? '—'} · centrality ${cent?.toFixed?.(2) ?? '—'}</div>` : '';
    tip.html(`<div style="font-weight:600;margin-bottom:4px">${esc(tag)}</div>
              <div class="muted" style="white-space:pre-wrap">${esc(d || '—')}</div>
              ${metrics}
              <div class="muted" style="margin-top:6px">Click to reveal pulse satellites</div>`)
       .style('display','block');
    moveTooltip(evt);
  }
  function moveTooltip(evt){
    const pad=12;
    tip.style('left', (evt.clientX + pad)+'px').style('top', (evt.clientY + pad)+'px');
  }
  function hideTooltip(){ tip.style('display','none'); }

  // ---------- satellites ----------
  let currentHost = null;

  function onTagClick(tagId){
    currentHost = tagId;
    satLayer.selectAll('*').remove();

    const host = id2node.get(tagId);
    if (!host) return;

    const pulses = (DATA.pulsesByTag?.[tagId] || []).slice();
    if (!pulses.length) return;

    // sort newest→oldest so spiral outward encodes time
    pulses.sort((a,b)=>(a.ageDays ?? 9e9) - (b.ageDays ?? 9e9));

    // layout: spiral for many, ring otherwise
    const many = pulses.length > 24;
    const R0 = 56, step = 13; // spiral
    const ringR = 86;

    const satData = pulses.map((p,i)=>{
      if (many){
        const a = i * 0.42;                     // radians between points
        return { ...p, host, _r: R0 + i*step/4, _a: a };
      }else{
        const a = (i/pulses.length)*Math.PI*2;
        return { ...p, host, _r: ringR, _a: a };
      }
    });

    const sats = satLayer.selectAll('g.satellite')
      .data(satData, d=>d.id || d.title || (d.date+':'+i))
      .join(enter=>{
        const g=enter.append('g').attr('class','satellite');
        g.append('circle')
          .attr('r', satSize)
          .attr('class', d=>ageClass(d.ageDays));
        // small hover title
        g.append('title')
          .text(d=>(d.title || d.id || 'pulse') + (d.date ? ` — ${d.date}`:''));
        g.on('click', (_e,d)=>showPulseDetails(d));
        return g;
      });

    // nudge sim so satellites settle immediately around host
    sim.alpha(0.6).restart();
  }

  // ---------- search ----------
  function applyFilter(q){
    const s = (q||'').trim().toLowerCase();
    if (!s){
      nodeSel.classed('dim', false);
      linkSel.classed('dim', false);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n=>n.id.toLowerCase().includes(s)).map(n=>n.id));
    nodeSel.classed('dim', d=>!keep.has(d.id));
    linkSel.classed('dim', d=>!(keep.has(d.source.id) && keep.has(d.target.id)));
  }
  search && search.addEventListener('input', e=>applyFilter(e.target.value));

  // initial sidebar hint
  sidebar.innerHTML = `<div class="muted">Pick a pulse to see its summary, papers & podcasts.</div>`;
})();
