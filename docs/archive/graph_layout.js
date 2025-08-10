(function(){
  const el = document.getElementById("graph");
  const width = el.clientWidth, height = el.clientHeight;

  const svg = d3.select(el).append("svg")
    .attr("width", width).attr("height", height);

  const gZoom = svg.append("g");
  const linkG = gZoom.append("g").attr("class","links");
  const nodeG = gZoom.append("g").attr("class","nodes");
  const labelG = gZoom.append("g").attr("class","labels");
  const haloG = gZoom.append("g").attr("class","halos");

  const nodes = GRAPH_DATA.nodes.map(d => Object.assign({}, d));
  const links = GRAPH_DATA.links.map(d => Object.assign({}, d));

  const degreeMax = d3.max(nodes, d => d.degree || 0) || 1;
  const r = d => 4 + Math.sqrt((d.degree||0) / degreeMax) * 18;

  const sim = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((d,i)=>i).distance(d=>60 + (220*(1-((nodes[d.source.index||0].degree||0)/degreeMax))) ).strength(0.4))
    .force("charge", d3.forceManyBody().strength(-260))
    .force("center", d3.forceCenter(width/2, height/2))
    .force("collide", d3.forceCollide().radius(d => r(d) + 10).iterations(2));

  const line = linkG.selectAll("line").data(links).enter().append("line")
    .attr("class","link").attr("stroke-width", 1.1);

  const node = nodeG.selectAll("g").data(nodes).enter().append("g")
    .attr("class", d => "node" + ((d.degree||0) >= 8 ? " node--hub" : ""))
    .call(d3.drag()
      .on("start", (event,d)=>{ if(!event.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on("drag", (event,d)=>{ d.fx=event.x; d.fy=event.y; })
      .on("end",  (event,d)=>{ if(!event.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));

  node.append("circle").attr("r", d=>r(d));

  const labels = labelG.selectAll("text").data(nodes).enter().append("text")
    .attr("class","label").text(d=>d.id)
    .attr("dy",".32em");

  // halos (for hover focus)
  const halos = haloG.selectAll("circle").data(nodes).enter().append("circle")
    .attr("class","halo").attr("data-for","hover").attr("r", d=>r(d)+6);

  // Zoom & pan
  svg.call(d3.zoom().scaleExtent([0.25, 3]).on("zoom", (event)=> gZoom.attr("transform", event.transform)));

  // Click → sidebar
  node.on("click", (_, d) => {
    const info = LINK_INDEX[d.id] || {links:[], pulses:[]};
    const ul = document.getElementById("link-list");
    ul.innerHTML = "";
    const add = (title, arr) => {
      if(!arr || !arr.length) return;
      const li = document.createElement("li");
      li.innerHTML = `<strong>${title}</strong>`;
      ul.appendChild(li);
      arr.forEach(x=>{
        const li2 = document.createElement("li");
        const a = document.createElement("a");
        a.textContent = x;
        a.href = "#";
        li2.appendChild(a);
        ul.appendChild(li2);
      });
    };
    add("Links", info.links);
    add("Pulses", info.pulses);
  });

  sim.on("tick", ()=>{
    line
      .attr("x1", d=>d.source.x).attr("y1", d=>d.source.y)
      .attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);

    node.attr("transform", d=>`translate(${d.x},${d.y})`);
    labels.attr("x", d=>d.x + r(d) + 6).attr("y", d=>d.y);
    halos.attr("cx", d=>d.x).attr("cy", d=>d.y);
  });

  // Auto-fit after settle
  function fit() {
    const margin = 30;
    const box = gZoom.node().getBBox();
    const scale = Math.min(
      (width - margin*2) / box.width,
      (height - margin*2) / box.height
    );
    const s = Math.max(0.25, Math.min(1.5, scale));
    const tx = (width - s*(box.x + box.width/2));
    const ty = (height - s*(box.y + box.height/2));
    svg.transition().duration(700).call(
      d3.zoom().transform,
      d3.zoomIdentity.translate(tx, ty).scale(s)
    );
  }
  // Give the sim a moment, then fit
  setTimeout(()=>{ sim.alpha(0.15).restart(); setTimeout(fit, 900); }, 200);
})();
