/* docs/graph.js
 *
 * Expects window.PHI_DATA with:
 *  - nodes: [{ id, centrality? }]
 *  - links: [{ source, target }]
 *  - tagDescriptions: { [tag]: string }
 *  - tagResources: { [tag]: { papers?: string[], podcasts?: string[] } }  (optional)
 *  - pulsesByTag: { [tag]: Pulse[] }                                    (preferred)
 *  - OR (fallbacks)
 *      pulses: Pulse[]
 *      tagToPulses: { [tag]: string[] }           (pulse ids)
 *
 * Pulse shape (flexible): { id?, title?, date?, ageDays?, summary?, papers?, podcasts?, tags? }
 *
 * DOM requirements in tag_map.html:
 *  - <svg id="graph"></svg>
 *  - <div id="tooltip"></div>
 *  - <div id="sidebar-content"></div>
 *  - <input id="search"> (optional)
 *  - <div id="status">   (optional)
 *
 * Uses D3 v7 (must be loaded before this file).
 */

(function () {
  // --- Guard -----------------------------------------------------------------
  if (typeof d3 === 'undefined') {
    console.error('[graph.js] D3 not found. Ensure <script src="https://d3js.org/d3.v7.min.js"> is loaded before graph.js');
    return;
  }

  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  // --- DOM handles -----------------------------------------------------------
  const svg       = d3.select('#graph');
  const tooltip   = d3.select('#tooltip');
  const sidebar   = document.getElementById('sidebar-content');
  const searchEl  = document.getElementById('search');
  const statusEl  = document.getElementById('status');

  // --- Helpers ---------------------------------------------------------------
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'})[c]
  );
  const safeArr = (x) => (Array.isArray(x) ? x : []);

  const tagDesc = (t) => (DATA.tagDescriptions && DATA.tagDescriptions[t]) || '';

  function pulsesFor(tag) {
    if (DATA.pulsesByTag && DATA.pulsesByTag[tag]) return safeArr(DATA.pulsesByTag[tag]);

    // fallback: compose from tagToPulses + pulses
    if (DATA.tagToPulses && DATA.pulses) {
      const ids = safeArr(DATA.tagToPulses[tag]);
      if (!ids.length) return [];
      const byId = new Map(safeArr(DATA.pulses).map(p => [p.id, p]));
      return ids.map(id => byId.get(id)).filter(Boolean);
    }

    // last resort: scan all pulses for tag membership
    if (DATA.pulses) {
      return safeArr(DATA.pulses).filter(p => safeArr(p.tags).includes(tag));
    }

    return [];
  }

  // satellites age color classes
  function ageClass(ageDays) {
    if (ageDays == null)   return 'age-old';
    if (ageDays <= 14)     return 'age-very-new';
    if (ageDays <= 45)     return 'age-new';
    if (ageDays <= 120)    return 'age-mid';
    if (ageDays <= 270)    return 'age-old';
    return 'age-very-old';
  }

  // --- SVG layers & zoom -----------------------------------------------------
  const width  = svg.node().clientWidth  || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr('viewBox', `0 0 ${width} ${height}`);

  const root          = svg.append('g');
  const linkLayer     = root.append('g').attr('class', 'links');
  const nodeLayer     = root.append('g').attr('class', 'nodes');
  const satelliteLayer= root.append('g').attr('class', 'satellites');

  svg.call(d3.zoom()
    .scaleExtent([0.25, 4])
    .on('zoom', (ev) => { root.attr('transform', ev.transform); })
  );

  // --- Data wiring -----------------------------------------------------------
  const idToNode = new Map(DATA.nodes.map(n => [n.id, n]));
  const links = safeArr(DATA.links)
    .map(l => ({
      source: idToNode.get(l.source) || l.source,
      target: idToNode.get(l.target) || l.target
    }))
    .filter(l => l.source && l.target);

  // neighbor map for fast highlight
  const neighbors = new Map(DATA.nodes.map(n => [n.id, new Set()]));
  links.forEach(l => {
    neighbors.get(l.source.id)?.add(l.target.id);
    neighbors.get(l.target.id)?.add(l.source.id);
  });

  // --- Force simulation ------------------------------------------------------
  const sim = d3.forceSimulation(DATA.nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(90).strength(0.25))
    .force('charge', d3.forceManyBody().strength(-420))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collide', d3.forceCollide().radius(d => 10 + Math.sqrt((d.centrality || 0) * 600)));

  // --- Draw links & nodes ----------------------------------------------------
  const linkSel = linkLayer
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('class', 'link');

  const nodeSel = nodeLayer
    .selectAll('g.node')
    .data(DATA.nodes, d => d.id)
    .join(enter => {
      const g = enter.append('g').attr('class', 'node');

      // label + dot (kept compact; ellipses can be reinstated if you prefer)
      g.append('circle').attr('r', 6);
      g.append('text')
        .attr('x', 9)
        .attr('y', 4)
        .text(d => d.id);

      // interactions
      g.on('mouseover', (ev, d) => showTagTip(ev, d.id))
       .on('mousemove', (ev)   => moveTip(ev))
       .on('mouseout',  hideTip)
       .on('click',     (_ev, d) => onTagClick(d.id));

      return g;
    });

  sim.on('tick', () => {
    linkSel
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);

    nodeSel.attr('transform', d => `translate(${d.x},${d.y})`);

    // Satellites are positioned relative to their host every tick
    satelliteLayer.selectAll('g.satellite')
      .attr('transform', d => {
        const r = d._radius || 110;
        const a = d._angle  || 0;
        const x = d.host.x + r * Math.cos(a);
        const y = d.host.y + r * Math.sin(a);
        return `translate(${x},${y})`;
      });
  });

  // --- Tooltip ---------------------------------------------------------------
  function moveTip(ev) {
    // Use pageX/pageY: viewport + scroll, consistent across browsers
    const pad = 10;
    tooltip
      .style('left', (ev.pageX + pad) + 'px')
      .style('top',  (ev.pageY + pad) + 'px');
  }

  function showTagTip(ev, tag) {
    const desc = tagDesc(tag);
    const deg  = (neighbors.get(tag)?.size) || 0;
    const cent = (idToNode.get(tag)?.centrality || 0);

    tooltip
      .html(
        `<div style="font-weight:700;margin-bottom:2px">${esc(tag)}</div>
         <div style="opacity:.9;margin-bottom:6px">degree ${deg} · centrality ${cent.toFixed(2)}</div>
         ${
           desc
             ? `<div style="max-width:280px;white-space:pre-wrap">${esc(desc)}</div>`
             : `<div style="opacity:.6">No description found.</div>`
         }
         <div style="margin-top:6px;opacity:.9"><em>Click to reveal pulse satellites</em></div>`
      )
      .style('display', 'block');

    moveTip(ev);
  }
  function hideTip() {
    tooltip.style('display', 'none');
  }

  // --- Sidebar ---------------------------------------------------------------
  function setSidebarHTML(html) {
    if (!sidebar) return;
    sidebar.innerHTML = html;
  }

  function showPulseDetails(pulse) {
    const when = pulse.date ? ` <span class="muted">(${esc(pulse.date)})</span>` : '';
    let html = `<div class="panel">
      <div class="panel-title">${esc(pulse.title || pulse.id || 'Pulse')}${when}</div>
      ${pulse.summary ? `<div style="white-space:pre-wrap;margin:.5rem 0 0.75rem 0">${esc(pulse.summary)}</div>` : ''}
    `;

    const papers = safeArr(pulse.papers);
    const pods   = safeArr(pulse.podcasts);

    if (papers.length) {
      html += `<div class="panel-subtitle">Papers</div><ul class="link-list">`;
      for (const u of papers) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul>`;
    }
    if (pods.length) {
      html += `<div class="panel-subtitle" style="margin-top:.5rem">Podcasts</div><ul class="link-list">`;
      for (const u of pods) html += `<li><a href="${u}" target="_blank" rel="noopener">${esc(u)}</a></li>`;
      html += `</ul>`;
    }

    html += `</div>`;
    setSidebarHTML(html);
  }

  function showTagPanel(tag) {
    // Minimal tag panel: we don’t dump tag resources here (you prefer to show pulse details only)
    const desc = tagDesc(tag);
    const hint = `<div class="hint">Click a pulse satellite to see its summary, papers & podcasts.</div>`;

    setSidebarHTML(
      `<div class="panel">
        <div class="panel-title">${esc(tag)}</div>
        ${desc ? `<div style="white-space:pre-wrap;margin:.3rem 0 .6rem 0">${esc(desc)}</div>` : ``}
        ${hint}
      </div>`
    );
  }

  // --- Highlight cluster + Satellites ---------------------------------------
  function highlightNeighbors(tag) {
    const keep = new Set([tag]);
    const neigh = neighbors.get(tag) || new Set();
    neigh.forEach(n => keep.add(n));

    nodeSel.classed('dim', d => !keep.has(d.id));
    linkSel.classed('on', d => keep.has(d.source.id) && keep.has(d.target.id));
  }

  function clearHighlight() {
    nodeSel.classed('dim', false);
    linkSel.classed('on', false);
  }

  function onTagClick(tag) {
    showTagPanel(tag);
    highlightNeighbors(tag);

    // Clear previous satellites
    satelliteLayer.selectAll('*').remove();

    const host = idToNode.get(tag);
    if (!host) return;

    const pulses = safeArr(pulsesFor(tag));
    if (!pulses.length) {
      setSidebarHTML(
        `<div class="panel"><div class="panel-title">${esc(tag)}</div>
         <div class="hint">No pulses tagged <strong>${esc(tag)}</strong> yet.</div></div>`
      );
      return;
    }

    // Layout: first ring up to 28, second ring next 36, then fall back to 3rd ring.
    const TWO_PI = Math.PI * 2;
    const ring1 = 28, ring2 = 36;
    const R1 = 110, R2 = 156, R3 = 200;

    const layout = pulses.map((p, i) => {
      let r, idx, tot;
      if (i < ring1) {
        r = R1; idx = i; tot = Math.min(ring1, pulses.length);
      } else if (i < ring1 + ring2) {
        r = R2; idx = i - ring1; tot = Math.min(ring2, pulses.length - ring1);
      } else {
        r = R3; idx = i - ring1 - ring2; tot = Math.max(1, pulses.length - ring1 - ring2);
      }
      return { ...p, host, _radius: r, _angle: (idx / tot) * TWO_PI };
    });

    const sats = satelliteLayer.selectAll('g.satellite')
      .data(layout, d => d.id || `${d.title || ''}:${d.date || ''}`)
      .join(enter => {
        const g = enter.append('g').attr('class', 'satellite');

        g.append('circle')
          .attr('r', 4.8)
          .attr('class', d => ageClass(d.ageDays));

        // small title on hover
        g.append('title')
          .text(d => `${d.title || d.id || 'pulse'}${d.date ? ` — ${d.date}` : ''}`);

        g.on('click', (_ev, d) => {
          // Stop propagation so you don’t retrigger node click through the svg
          d3.event?.stopPropagation?.();
          showPulseDetails(d);
        });

        return g;
      });

    // Nudge the sim so satellites appear smoothly
    sim.alpha(0.5).restart();
  }

  // Clicking blank background clears highlight + satellites
  svg.on('click', (ev) => {
    if (ev.target === svg.node()) {
      clearHighlight();
      satelliteLayer.selectAll('*').remove();
      setSidebarHTML(`<div class="hint">Pick a tag to reveal pulse satellites. Click a pulse to see its details.</div>`);
    }
  });

  // --- Search filter ---------------------------------------------------------
  function applyFilter(q) {
    const norm = (q || '').toString().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
    if (!norm) {
      nodeSel.attr('opacity', 1);
      linkSel.attr('opacity', 0.35);
      statusEl && (statusEl.textContent = `tags: ${DATA.nodes.length}`);
      return;
    }
    const keep = new Set(DATA.nodes.filter(n => n.id.toLowerCase().includes(norm)).map(n => n.id));
    nodeSel.attr('opacity', d => keep.has(d.id) ? 1 : 0.12);
    linkSel.attr('opacity', d => (keep.has(d.source.id) && keep.has(d.target.id)) ? 0.35 : 0.05);
    statusEl && (statusEl.textContent = `filtered: ${keep.size}/${DATA.nodes.length}`);
  }

  if (searchEl) {
    let t = null;
    searchEl.addEventListener('input', (e) => {
      if (t) clearTimeout(t);
      t = setTimeout(() => applyFilter(e.target.value), 80);
    });
  }

  // --- Initial sidebar text --------------------------------------------------
  setSidebarHTML(`<div class="hint">Hover a tag for its description • Click a tag to show pulse satellites • Click a pulse to see details</div>`);
  statusEl && (statusEl.textContent = `tags: ${DATA.nodes.length}`);
})();
