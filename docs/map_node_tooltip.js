// docs/map_node_tooltip.js
// Lightweight, reusable tooltips for the Phi-Mesh map.
// Usage in tag_map.html:
//   <script src="map_node_tooltip.js"></script>
//   attachTagTooltips(node, d => htmlString)
//
// The callback gets the bound datum d and should return an HTML string (or "").

(function (global) {
  function initTooltip() {
    // Single shared tooltip div
    let tip = document.getElementById("phi-tip");
    if (!tip) {
      tip = document.createElement("div");
      tip.id = "phi-tip";
      tip.style.position = "fixed";
      tip.style.padding = "8px 10px";
      tip.style.borderRadius = "8px";
      tip.style.background = "rgba(20,24,34,0.96)";
      tip.style.color = "#e6f0ff";
      tip.style.fontSize = "12px";
      tip.style.maxWidth = "360px";
      tip.style.lineHeight = "1.35";
      tip.style.border = "1px solid rgba(255,255,255,0.08)";
      tip.style.boxShadow = "0 8px 24px rgba(0,0,0,0.35)";
      tip.style.pointerEvents = "none";
      tip.style.zIndex = "9999";
      tip.style.display = "none";
      document.body.appendChild(tip);
    }
    return tip;
  }

  function attachTagTooltips(nodeSelection, getHTML) {
    const tip = initTooltip();

    function show(event, d) {
      const html = (typeof getHTML === "function") ? (getHTML(d) || "") : "";
      if (!html) {
        tip.style.display = "none";
        return;
      }
      tip.innerHTML = html;
      const x = event.clientX + 12;
      const y = event.clientY + 12;
      tip.style.left = x + "px";
      tip.style.top  = y + "px";
      tip.style.display = "block";
    }

    function hide() {
      tip.style.display = "none";
    }

    nodeSelection
      .on("mousemove.tagtip", show)
      .on("mouseleave.tagtip", hide)
      .on("click.tagtip", hide); // clicking a node focuses; hide the tip to reduce clutter
  }

  // export
  global.attachTagTooltips = attachTagTooltips;
})(window);
