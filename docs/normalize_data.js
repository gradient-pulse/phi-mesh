/* docs/normalize_data.js — canonicalize tags in window.PHI_DATA
   - Merges alias spellings into a single canonical id
   - Fixes nodes, links, pulsesByTag, tagDescriptions
   - Adds sensible fallback descriptions when missing
   - Logs any NEW / unknown variants you might want to add to aliases
*/

(function(){
  const W = (typeof window !== 'undefined') ? window : {};
  if (!W.PHI_DATA || !W.PHI_DATA.nodes) {
    console.warn('[normalize_data] PHI_DATA missing; load data.js first.');
    return;
  }

  // --- Aliases map (variant -> canonical) ------------------------------
  // Covers the variants you surfaced + a few common ones we already saw.
  // You can extend freely; the heuristic normalizer also catches most str/dash/underscore diffs.
  const ALIAS = (() => {
    const map = new Map();

    // helper to register many variants
    const add = (canonical, variants) => {
      variants.forEach(v => map.set(v.toLowerCase(), canonical));
      // also teach the normalized form of canonical itself
      map.set(canonical.toLowerCase(), canonical);
    };

    // Core & map
    add('phi_mesh', [
      'phi-mesh', 'phimesh', 'phi mesh', 'PhiMesh', 'Phi-mesh'
    ]);
    add('rgp_tag_map', ['tagmap','TagMap','rgp-tag-map']);
    add('tag_map', ['TagMap','tagmap']);

    // Program vocabulary
    add('recursive_gradient_processing', [
      'recursive gradient processing','rgp (recursive gradient processing)','rgp_core_loop'
    ]);
    add('rgp', ['RGP','rgp']);

    // Physics / cosmology
    add('navier_stokes', [
      'navierstokes','navier-stokes','NavierStokes','Navier Stokes','navier_stokes','ns_solution'
    ]);
    add('ns_solution', ['NS_solution']);

    add('big_bang', ['big-bang','Big Bang','Big_Bang']);
    add('big_quiet', ['big-quiet','bigquiet','BigQuiet','Big_Quiet']);

    // RGP terms
    add('nt_narrative_tick', [
      'NT','Narrative Tick','Narrative_Tick','Narrative-Tick','NT_Narrative_Tick','nt_(narrative_tick)','nt (narrative_tick)'
    ]);
    add('nt_rhythm', ['NT-rhythm']);
    add('ud', ['unity-disunity','Unity-Disunity','UD']);

    add('contextual_filter', [
      'Contextual_Filter','ContextualFilter','contextual-filter','contectual_filter','contextualfilter'
    ]);
    add('gradient_syntax', ['Gradient_Syntax','gradient-syntax','GradientSyntax']);

    add('gradient_choreography', ['gradient-choreography']);

    add('gradient_memory', ['gradient-memory','gradientmemory']);

    add('gradient_cocoon', ['gradient-cocoon','gradient_cocoon_theory']);

    add('gradient_driven_behavior', ['gradient-driven_behavior','gradient-driven-behavior']);
    add('gradient_driven_intelligence', ['gradient-driven-intelligence']);

    add('mixture_of_experts', ['mixture-of-experts','moe','MoE']);

    add('triadic_emergence', ['triadic-emergence','deep_triad']);

    add('recursive_checkpoint', ['recursive-checkpoint']);
    add('recursive_cognition', ['recursive-cognition']);
    add('recursive_grammar', ['recursive-grammar']);
    add('recursive_awakening', ['recursive-awakening','recursive_awakening']);

    add('quiet_awakening', ['Quiet_Awakening']);

    add('phi_harmonics', ['Φ-harmonics', '\u03A6-harmonics', 'harmonics']);

    add('hrm', ['HRM']);

    add('r_phi', ['RΦ','r']); // map lone "r" to r_phi

    // Models / infra
    add('gpt5', ['GPT5']);
    add('grok3', ['GROK3']);
    add('gemini', ['Gemini']);

    // Tools
    add('phi_monitor', ['Phi-monitor','Phi_monitor','PhiMonitor']);
    add('proto_pulse', ['proto-pulse','protopulse']);

    // Society / language (a few likely ones)
    add('non_linear_society', ['non-linear_society','Non-linear_society']);

    // Pulses / meta
    add('experimenter_pulse', [
      'ExperimenterPulse','Experimenter','AgentPulse','agent_result','AutoPulse',
      'auto_pulse','lab_note','finding','experimenterpulse'
    ]);

    return map;
  })();

  // --- Heuristic canonicalization -------------------------------------
  // Normalize strings: lowercase, strip () and punctuation, collapse dashes/underscores/spaces to '_'
  function normalizeKey(s){
    if (s == null) return '';
    let t = String(s).trim().toLowerCase();
    t = t.replace(/[()]/g, '');
    t = t.replace(/[^a-z0-9_\-\s]/g, '');       // remove exotic punctuation but keep - _ and space
    t = t.replace(/[\s\-]+/g, '_');            // collapse spaces/dashes to underscore
    t = t.replace(/^_+|_+$/g, '');
    return t;
  }

  function canonicalize(raw){
    const n = normalizeKey(raw);
    // Direct alias look-up first
    if (ALIAS.has(n)) return ALIAS.get(n);
    // If not found, keep normalized form (this alone fixes many dash/space/underscore issues)
    return n;
  }

  // --- Patch PHI_DATA in-place ----------------------------------------
  const DATA = W.PHI_DATA;

  // 1) Canonicalize tagDescriptions keys (and ensure fallbacks)
  const descIn  = DATA.tagDescriptions || {};
  const descOut = {};
  Object.keys(descIn).forEach(k => {
    descOut[canonicalize(k)] = descIn[k];
  });
  DATA.tagDescriptions = descOut;

  // 2) Canonicalize pulsesByTag keys and make sure tags are canonical inside any arrays
  const pbtIn  = DATA.pulsesByTag || {};
  const pbtOut = {};
  Object.keys(pbtIn).forEach(k => {
    const c = canonicalize(k);
    const arr = Array.isArray(pbtIn[k]) ? pbtIn[k] : [];
    pbtOut[c] = arr; // contents are pulse objects; their internal tags aren’t required here
  });
  DATA.pulsesByTag = pbtOut;

  // 3) Canonicalize nodes and MERGE duplicates
  const merged = new Map(); // id -> node
  for (const n of (DATA.nodes || [])){
    const c = canonicalize(n.id);
    const existing = merged.get(c);
    if (existing){
      // keep the highest centrality if present
      const a = (existing.centrality != null) ? +existing.centrality : -Infinity;
      const b = (n.centrality != null) ? +n.centrality : -Infinity;
      existing.centrality = (isFinite(a) || isFinite(b)) ? Math.max(a, b) : undefined;
    } else {
      merged.set(c, { id:c, centrality:n.centrality });
    }
  }
  DATA.nodes = Array.from(merged.values());

  // 4) Canonicalize links and drop self-loops / broken refs
  const idSet = new Set(DATA.nodes.map(n => n.id));
  DATA.links = (DATA.links || []).map(l => {
    const s = canonicalize(l.source && (l.source.id || l.source));
    const t = canonicalize(l.target && (l.target.id || l.target));
    return { source:s, target:t };
  }).filter(l => l.source && l.target && idSet.has(l.source) && idSet.has(l.target) && l.source !== l.target);

  // 5) Provide default/fallback descriptions for any node still missing one
  const titleCase = id => id.replace(/_/g,' ').replace(/\b[a-z]/g, m => m.toUpperCase());
  for (const n of DATA.nodes){
    const key = n.id;
    if (!DATA.tagDescriptions[key]){
      // Prefer a short informative fallback instead of "—"
      DATA.tagDescriptions[key] = titleCase(key);
    }
  }

  // 6) Build an audit of variants that were seen and re-mapped (to help keep aliases.yaml fresh)
  const seen = new Set();
  const audit = [];
  function auditId(id){
    const norm = normalizeKey(id);
    if (!seen.has(norm)){
      seen.add(norm);
      const canon = canonicalize(norm);
      if (norm !== canon && !ALIAS.has(norm)){
        audit.push({ variant:id, normalized:norm, canonical:canon });
      }
    }
  }
  (W.PHI_DATA_RAW_IDS || []).forEach(auditId); // optional hook if you feed raw ids here
  // also audit from the actual data
  (DATA.nodes||[]).forEach(n => auditId(n.id));
  Object.keys(DATA.tagDescriptions||{}).forEach(auditId);
  Object.keys(DATA.pulsesByTag||{}).forEach(auditId);

  if (audit.length){
    console.groupCollapsed('[normalize_data] Aliases to consider adding');
    audit.forEach(x => console.log(`- "${x.variant}" -> canonical "${x.canonical}" (normalized: "${x.normalized}")`));
    console.groupEnd();
  } else {
    console.log('[normalize_data] All tag ids canonicalized.');
  }
})();
