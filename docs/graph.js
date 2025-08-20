/* docs/graph.js
 * Uses window.PHI_DATA:
 *  nodes [{id, degree?, centrality?}], links [{source,target}],
 *  tagDescriptions { [tag]: "..." } or { tags:{[tag]:"..."} },
 *  pulsesByTag { tag: [ {id,title?,date?,ageDays?,summary?,papers?,podcasts?,tags?} ] }
 */
(function () {
  const DATA = window.PHI_DATA || { nodes: [], links: [] };

  const svg = d3.select("#graph");
  if (svg.empty()) return;

  const detailsEl = document.getElementById("details");
  const searchInput = document.getElementById("tag-search");

  // ---------- tooltip ----------
  let tip = document.getElementById("phi-tip");
  if (!tip) {
    tip = document.createElement("div");
    tip.id = "phi-tip";
    Object.assign(tip.style, {
      position: "fixed", zIndex: 20, pointerEvents: "none", display: "none",
      background: "#10141d", border: "1px solid #2a3344", borderRadius: "10px",
      padding: "8px 10px", color: "#e6edf6", fontSize: "13px",
      boxShadow: "0 8px 32px rgba(0,0,0,.45)",
    });
    document.body.appendChild(tip);
  }
  const esc = (s)=>String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const showTip=(html,x,y)=>{tip.innerHTML=html; tip.style.left=(x+12)+"px"; tip.style.top=(y+12)+"px"; tip.style.display="block";};
  const moveTip=(x,y)=>{tip.style.left=(x+12)+"px"; tip.style.top=(y+12)+"px";};
  const hideTip=()=>{tip.style.display="none";};

  function getTagDescription(tag){
    const td = DATA.tagDescriptions || {};
    if (typeof td[tag] === "string") return td[tag];
    if (td.tags && typeof td.tags[tag] === "string") return td.tags[tag];
    return "";
  }
  function ageClass(days){
    if (days == null) return "age-old";
    if (days <= 14) return "age-very-new";
    if (days <= 45) return "age-new";
    if (days <= 120) return "age-mid";
    if (days <= 270) return "age-old";
    return "age-very-old";
  }

  function showPulseDetails(p){
    if (!detailsEl) return;
    const when = p.date ? ` <span class="muted">(${esc(p.date)})</span>` : "";
    let html = `<h2>${esc(p.title || p.id || "Pulse")}${when}</h2>`;
    if (p.summary) html += `<div style="white-space:pre-wrap;margin:.3rem 0 1rem 0">${esc(p.summary)}</div>`;

    const papers = Array.isArray(p.papers)?p.papers:[];
    const pods = Array.isArray(p.podcasts)?p.podcasts:[];
    if (papers.length){
      html += `<div><strong>Papers</strong><ul>`;
      for (const it of papers){
        if (typeof it === "string"){
          html += `<li><a href="${it}" target="_blank" rel="noopener">${esc(it)}</a></li>`;
        }else if (it && (it.url || it.doi)){
          const url = it.url || (it.doi ? `https://doi.org/${it.doi}` : "");
          const label = it.title || url;
          if (url) html += `<li><a href="${url}" target="_blank" rel="noopener">${esc(label)}</a></li>`;
        }
      }
      html += `</ul></div>`;
    }
    if (pods.length){
      html += `<div style="margin-top:8px"><strong>Podcasts</strong><ul>`;
      for (const it of pods){
        const url = typeof it === "string" ? it : it?.url;
        if (url) html += `<li><a href="${url}" target="_blank" rel="noopener">${esc(url)}</a></li>`;
      }
      html += `</ul></div>`;
    }
    detailsEl.innerHTML = html;
  }

  // ---------- layout ----------
  const width = svg.node().clientWidth || 1200;
  const height = svg.node().clientHeight || 800;
  svg.attr("viewBox", `0 0 ${width} ${height}`);

  const root = svg.append("g");
  const linkLayer = root.append("g").attr("class","links");
  const nodeLayer = root.append("g").attr("class","nodes");
  const satLayer  = root.append("g").attr("class","satellites");

  svg.call(d3.zoom().scaleExtent([0.25,4]).on("zoom", (e)=>root.attr("transform", e.transform)));

  const idToNode = new Map(DATA.nodes.map(n=>[n.id,n]));
  const links = DATA.links.map(l=>({source:idToNode.get(l.source)||l.source, target:idToNode.get(l.target)||l.target})).filter(l=>l.source&&l.target);

  const sim = d3.forceSimulation(DATA.nodes)
    .force("link", d3.forceLink(links).id(d=>d.id).distance(90).strength(.25))
    .force("charge", d3.forceManyBody().strength(-440))
    .force("center", d3.forceCenter(width/2, height/2))
    .force("collision", d3.forceCollide().radius(d=>5 + Math.sqrt((d.centrality||0)*700) + 6));

  // clearer links
  const linkSel = linkLayer.selectAll("line").data(links).join("line")
    .attr("class","link")
    .attr("stroke","rgba(200,215,235,0.68)")
    .attr("stroke-width",1.5);

  // smaller node ellipses
  const rx = (d)=> 5 + Math.sqrt((d.centrality||0)*700);
  const ry = (d)=> 3.5 + Math.sqrt((d.centrality||0)*350);

  const nodeSel = nodeLayer.selectAll("g.node").data(DATA.nodes, d=>d.id).join(enter=>{
    const g = enter.append("g").attr("class","node").style("cursor","pointer");

    g.append("ellipse")
      .attr("rx", rx).attr("ry", ry)
      .attr("fill","#2cc4ff").attr("stroke","#022433").attr("stroke-width",1.2)
      .style("filter","drop-shadow(0 0 1px rgba(0,0,0,.3))");

    g.append("text")
      .attr("y", d=>ry(d)+12)
      .attr("text-anchor","middle")
      .attr("fill","#fff").attr("font-size",11)
      .style("pointer-events","none")
      .text(d=>d.id);

    g.on("mouseover",(ev,d)=>{
      const desc = getTagDescription(d.id);
      const deg = d.degree ?? d.deg ?? 0;
      const cen = Number(d.centrality||0).toFixed(2);
      const body = desc ? `<div style="opacity:.9;margin-top:4px">${esc(desc)}</div>` : `<div style="opacity:.7;margin-top:4px">—</div>`;
      showTip(`
        <div style="font-weight:700;margin-bottom:2px">${esc(d.id)}</div>
        <div style="opacity:.85">degree ${deg} · centrality ${cen}</div>
        ${body}
        <div style="margin-top:6px;opacity:.9"><em>Click to reveal pulse satellites</em></div>
      `, ev.clientX, ev.clientY);
    }).on("mousemove",(ev)=>moveTip(ev.clientX, ev.clientY))
      .on("mouseout", hideTip)
      .on("click", (_e,d)=>revealSatellites(d.id));

    return g;
  });

  sim.on("tick", ()=>{
    linkSel
      .attr("x1", d=>d.source.x).attr("y1", d=>d.source.y)
      .attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);
    nodeSel.attr("transform", d=>`translate(${d.x},${d.y})`);
    satLayer.selectAll("g.sat").attr("transform", d=>{
      const a = d._angle||0, r=d._radius||100, h=d.host;
      return `translate(${h.x + r*Math.cos(a)},${h.y + r*Math.sin(a)})`;
    });
  });

  // ---------- satellites ----------
  function revealSatellites(tagId){
    hideTip();
    satLayer.selectAll("*").remove();

    const host = idToNode.get(tagId);
    if (!host) return;
    const pulses = Array.isArray(DATA.pulsesByTag?.[tagId]) ? DATA.pulsesByTag[tagId] : [];
    if (!pulses.length) return;

    const sorted = [...pulses].sort((a,b)=>(a.ageDays??99999)-(b.ageDays??99999));
    const n = sorted.length, TWO_PI = Math.PI*2, R = 100;

    satLayer.selectAll("g.sat").data(sorted.map((p,i)=>({
      ...p, host, _angle:(i/n)*TWO_PI, _radius:R
    })), d=>d.id||d.title||`${tagId}:${d.date||""}`)
    .join(enter=>{
      const g = enter.append("g").attr("class","sat").style("cursor","pointer");

      g.append("circle")
        .attr("r",5).attr("class", d=>ageClass(d.ageDays))
        .attr("fill", d=>{
          const m = {"age-very-new":"#ff6b6b","age-new":"#ff9e66","age-mid":"#ffc94d","age-old":"#8ecbff","age-very-old":"#6aa4ff"};
          return m[ageClass(d.ageDays)] || "#8ecbff";
        }).attr("stroke","#10131a").attr("stroke-width",1.25);

      g.append("title").text(d=>`${d.title||d.id||"pulse"}${d.date?` — ${d.date}`:""}`);

      g.on("click", (_e,d)=> showPulseDetails(d));
      return g;
    });

    sim.alpha(0.35).restart();
  }

  // ---------- search ----------
  if (searchInput){
    const norm = s => (s||"").toString().normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();
    const run = ()=>{
      const q = norm(searchInput.value);
      if (!q){
        nodeSel.classed("dim",false).attr("opacity",1);
        linkSel.attr("opacity",0.68);
        return;
      }
      const keep = new Set(DATA.nodes.filter(n=>norm(n.id).includes(q)).map(n=>n.id));
      nodeSel.attr("opacity", d=>keep.has(d.id)?1:.15);
      linkSel.attr("opacity", l=> (keep.has(l.source.id)&&keep.has(l.target.id)) ? 0.68 : 0.08);
    };
    let t=null; searchInput.addEventListener("input", ()=>{clearTimeout(t); t=setTimeout(run,80);});
  }
})();
