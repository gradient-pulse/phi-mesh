function renderSidebar(tag) {
  const sidebar = document.getElementById("link-list");
  sidebar.innerHTML = "";

  const data = linkIndex[tag];

  const title = document.createElement("li");
  title.innerHTML = `<strong style="font-size: 14px;">${tag}</strong>`;
  sidebar.appendChild(title);

  if (!data) {
    const none = document.createElement("li");
    none.textContent = "No linked content found.";
    sidebar.appendChild(none);
    return;
  }

  const addLinks = (label, items) => {
    if (!items || items.length === 0) return;
    const header = document.createElement("li");
    header.innerHTML = `<strong>${label}</strong>`;
    sidebar.appendChild(header);

    items.slice(0, 3).forEach(path => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = path;
      a.target = "_blank";
      a.title = path;
      a.textContent = truncate(path.split("/").pop(), 25);
      li.appendChild(a);
      sidebar.appendChild(li);
    });
  };

  addLinks("Papers", data.papers);
  addLinks("Podcasts", data.podcasts);
  addLinks("Pulses", data.pulses);
}

function truncate(text, maxLength) {
  return text.length > maxLength ? text.slice(0, maxLength) + "…" : text;
}
