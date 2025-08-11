// docs/map_node_tooltip.js
// Standalone, opt-in tooltips for tag nodes.
// Usage (later):
//   <script src="map_node_tooltip.js"></script>
//   attachTagTooltips(nodeSel, d => d.summary);

(function (global) {
  function initTooltip() {
    const tip = d3.select("body").append("div")
      .attr("class", "tagmap-tooltip")
      .style("position", "fixed")
      .style("padding", "8px 10px")
      .style("border-radius", "8px")
      .style("background", "rgba(20,24,34,0.96)")
      .style("color", "#e6f0ff")
      .style("font-size", "12px")
      .style("max-width", "360px")
      .style("line-height", "1.35")
      .style("box-shadow", "0 8px 24px rgba(0,0,0,0.35)")
      .style("pointer-events", "none")
      .style("z-index", "9999")
      .style("display", "none");
    return tip;
  }

  function attachTagTooltips(nodeSelection, getHTML) {
    const tip = initTooltip();

    nodeSelection
      .on("mousemove.tagtip", (event, d) => {
        const html = (typeof getHTML === "function") ? getHTML(d) : "";
        if (!html) return tip.style("display", "none");
        tip.html(html)
          .style("left", (event.clientX + 12) + "px")
          .style("top",  (event.clientY - 28) + "px")
          .style("display", "block");
      })
      .on("mouseleave.tagtip", () => tip.style("display", "none"));
  }

  // export
  global.attachTagTooltips = attachTagTooltips;
})(window);
