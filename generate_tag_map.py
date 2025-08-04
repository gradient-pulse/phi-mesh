// Updated graph.js (for tag_map.html) – Phase 4 fixes included

const width = window.innerWidth;
const height = window.innerHeight;

const svg = d3
  .select("#graph")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

const container = svg.append("g");

const zoom = d3.zoom().on("zoom", (event) => container.attr("transform", event.transform));
svg.call(zoom);

fetch("tag_index.yml")
  .then((response) => response.text())
  .then((rawYaml) => {
    const tagData = jsyaml.load(rawYaml);
    const nodes = Object.keys(tagData).map((tag) => ({ id: tag }));
    const links = [];

    // Generate links between all co-occurring tags
    Object.values(tagData).forEach((paths) => {
      for (let i = 0; i < paths.length; i++) {
        for (let j = i + 1; j < paths.length; j++) {
          const a = Object.keys(tagData).find((tag) => tagData[tag].includes(paths[i]));
          const b = Object.keys(tagData).find((tag) => tagData[tag].includes(paths[j]));
          if (a && b && a !== b) {
            links.push({ source: a, target: b });
          }
        }
      }
    });

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d) => d.id).distance(140))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = container
      .append("g")
      .attr("stroke", "#ccc")
      .attr("stroke-opacity", 0.7)
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 1);

    const node = container
      .append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 6)
      .attr("fill", "#99c3eb") // paler blue
      .call(drag(simulation))
      .on("click", (event, d) => showTagDetails(d.id));

    const label = container
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => d.id)
      .attr("font-size", 11)
      .attr("fill", "black")
      .attr("text-anchor", "middle")
      .attr("dy", "1.3em"); // below dot

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
      label.attr("x", (d) => d.x).attr("y", (d) => d.y);
    });

    function drag(simulation) {
      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }

      return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
    }
  });

function showTagDetails(tag) {
  document.querySelector("#sidebar").innerHTML = `<h3>Tag: ${tag}</h3>`;

  fetch("pulse_index.json")
    .then((response) => response.json())
    .then((pulseIndex) => {
      const related = pulseIndex[tag] || {};
      const sections = ["Pulses", "Papers", "Podcasts"];
      sections.forEach((section) => {
        if (related[section.toLowerCase()]?.length) {
          const entries = related[section.toLowerCase()].map((entry) => `<li style='margin-left: 10px;'><a href='${entry.url}' target='_blank'>${entry.title}</a></li>`).join("\n");
          document.querySelector("#sidebar").innerHTML += `<h4>${section}</h4><ul>${entries}</ul>`;
        }
      });
    });
}
