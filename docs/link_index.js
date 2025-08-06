
const linkIndex = {
  "scene-drift": {
    pulses: ["pulse/2025-07-20_laminar_turbulent_rgp-laminar.yml"],
    papers: ["foundational_rgp-papers/the_world_already_knows.md"],
    podcasts: ["mesh_academy/curriculum/recursive_gradients.md"]
  },
  "recursive-checkpoint": {
    pulses: ["pulse/2025-07-25_experimenter_silence.yml"],
    papers: [],
    podcasts: ["mesh_academy/curriculum/recursive_gradients.md"]
  }
};
function displayLinks(tag) {
  const links = linkIndex[tag];
  if (!links) return;

  const sidebar = document.getElementById("sidebar-content");
  sidebar.innerHTML = "";

  if (links.pulses && links.pulses.length > 0) {
    sidebar.innerHTML += "<h4>Pulses</h4><ul>" +
      links.pulses.map(p => `<li><a href="/phi-mesh/${p}" target="_blank">${p}</a></li>`).join("") +
      "</ul>";
  }

  if (links.papers && links.papers.length > 0) {
    sidebar.innerHTML += "<h4>Papers</h4><ul>" +
      links.papers.map(p => `<li><a href="/phi-mesh/${p}" target="_blank">${p}</a></li>`).join("") +
      "</ul>";
  }

  if (links.podcasts && links.podcasts.length > 0) {
    sidebar.innerHTML += "<h4>Podcasts</h4><ul>" +
      links.podcasts.map(p => `<li><a href="/phi-mesh/${p}" target="_blank">${p}</a></li>`).join("") +
      "</ul>";
  }
}
