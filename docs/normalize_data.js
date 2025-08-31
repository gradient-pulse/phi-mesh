// normalize_data.js
(function () {
  if (!window.PHI_DATA) return;

  const aliases = (window.PHI_ALIASES || {}).aliases || {};
  const tagDescriptions = (window.PHI_TAG_DESCRIPTIONS || {}).tags || {};

  // Build reverse lookup: variant → canonical
  const lookup = {};
  for (const [canon, vars] of Object.entries(aliases)) {
    lookup[canon] = canon; // include itself
    if (Array.isArray(vars)) {
      for (const v of vars) lookup[v] = canon;
    }
  }

  const seen = new Set();
  const normalize = tag => lookup[tag] || tag;

  // Track logs
  const merges = [];
  const drops = [];

  // --- Normalize nodes ---
  if (window.PHI_DATA.nodes) {
    window.PHI_DATA.nodes.forEach(n => {
      const oldId = n.id;
      const canon = normalize(oldId);

      if (canon !== oldId) {
        merges.push(`${oldId} → ${canon}`);
        n.id = canon;
      }

      if (seen.has(n.id)) {
        drops.push(oldId);
      } else {
        seen.add(n.id);
      }
    });
  }

  // --- Normalize links ---
  if (window.PHI_DATA.links) {
    window.PHI_DATA.links.forEach(l => {
      l.source = normalize(l.source);
      l.target = normalize(l.target);
    });
  }

  // --- Normalize pulsesByTag ---
  if (window.PHI_DATA.pulsesByTag) {
    const newPulses = {};
    for (const [tag, arr] of Object.entries(window.PHI_DATA.pulsesByTag)) {
      const canon = normalize(tag);
      if (!newPulses[canon]) newPulses[canon] = [];
      newPulses[canon].push(...arr);
      if (canon !== tag) merges.push(`pulsesByTag: ${tag} → ${canon}`);
    }
    window.PHI_DATA.pulsesByTag = newPulses;
  }

  // --- Attach descriptions if missing ---
  if (window.PHI_DATA.nodes) {
    window.PHI_DATA.nodes.forEach(n => {
      if (!n.description && tagDescriptions[n.id]) {
        n.description = tagDescriptions[n.id];
      }
    });
  }

  // --- Console audit ---
  if (merges.length) {
    console.groupCollapsed("%c[normalize_data] Aliases merged", "color: #6cf;");
    merges.forEach(m => console.log(m));
    console.groupEnd();
  }
  if (drops.length) {
    console.groupCollapsed("%c[normalize_data] Duplicate nodes dropped", "color: #f66;");
    drops.forEach(d => console.log(d));
    console.groupEnd();
  }
})();
