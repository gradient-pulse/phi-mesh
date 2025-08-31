/* docs/normalize_data.js — robust, self-contained alias normalization
   1) Collapses alias spellings → ONE canonical id
   2) Merges duplicate nodes; rewrites links & pulsesByTag keys
   3) Ensures every node has a tooltip (fallback if missing)
   4) Logs an audit of merged/dropped items
*/
(function(){
  const W = (typeof window !== 'undefined') ? window : {};
  const D = W.PHI_DATA;
  if (!D || !Array.isArray(D.nodes) || !Array.isArray(D.links)) {
    console.warn('[normalize_data] PHI_DATA missing or incomplete; load data.js first.');
    return;
  }

  // ----- Alias table (from your meta/aliases.yml, condensed) -----
  const ALIASES = {
    // Core
    phi_mesh: ['phi-mesh','phimesh','phi mesh','PhiMesh','Phi-mesh'],
    rgp_tag_map: ['TagMap','tagmap','rgp-tag-map'],
    tag_map: ['TagMap','tagmap'],

    // Program
    recursive_gradient_processing: ['recursive gradient processing','RGP (Recursive Gradient Processing)','rgp_core_loop'],
    rgp: ['RGP','rgp'],

    // Physics / cosmology
    navier_stokes: ['Navier_Stokes','navier-stokes','NavierStokes','Navier Stokes','navierstokes','ns_solution'],
    ns_solution: ['NS_solution'],
    big_bang: ['Big Bang','Big_Bang','big-bang'],
    big_quiet: ['Big_Quiet','Big-Quiet','BigQuiet','big-quiet','bigquiet'],

    // RGP vocab
    nt_narrative_tick: ['NT','Narrative Tick','Narrative_Tick','Narrative-Tick','NT_Narrative_Tick','NT_(Narrative_Tick)','nt_(narrative_tick)'],
    nt_rhythm: ['NT-rhythm'],
    ud: ['UD','Unity-Disunity','unity-disunity'],

    contextual_filter: ['Contextual_Filter','ContextualFilter','contextual-filter','contectual_filter','contextualfilter'],
    gradient_syntax: ['Gradient_Syntax','gradient-syntax','GradientSyntax'],
    gradient_choreography: ['gradient-choreography'],
    gradient_memory: ['gradient-memory','gradientmemory'],
    gradient_cocoon: ['gradient-cocoon','gradient_cocoon_theory'],
    gradient_driven_behavior: ['gradient-driven_behavior','gradient-driven-behavior'],
    gradient_driven_intelligence: ['gradient-driven-intelligence'],
    rhythm_of_least_divergence: ['rhythm-of-least-divergence'],
    rhythm_of_nature: ['rhythm-of-nature'],
    mixture_of_experts: ['mixture-of-experts','MoE','moe'],
    coherence_amplifier: ['coherence-amplifier'],
    subjective_logging: ['subjective-logging'],
    triadic_emergence: ['triadic-emergence','deep_triad'],
    recursive_checkpoint: ['recursive-checkpoint'],
    recursive_cognition: ['recursive-cognition'],
    recursive_grammar: ['recursive-grammar'],
    recursive_awakening: ['recursive-awakening','recursive_awakening'],
    quiet_awakening: ['Quiet_Awakening'],
    phi_harmonics: ['Φ-harmonics','\u03A6-harmonics','harmonics'],
    hrm: ['HRM'],
    r_phi: ['RΦ','r'],

    // Models / infra
    gpt5: ['GPT5'], grok3: ['GROK3'], gemini: ['Gemini'],

    // Tools / platform
    phi_monitor: ['Phi-monitor','Phi_monitor','PhiMonitor'],
    proto_pulse: ['proto-pulse','protopulse'],

    // Society / language (examples)
    non_linear_society: ['non-linear_society','Non-linear_society'],

    // Pulses / meta
    experimenter_pulse: ['ExperimenterPulse','Experimenter','experimenter_pulse','AgentPulse','agent_result','AutoPulse','auto_pulse','lab_note','finding','experimenterpulse'],
  };

  // Build reverse lookup: variant -> canonical
  const REV = new Map();
  const norm = s => String(s||'').trim().toLowerCase().replace(/[()]/g,'').replace(/[^a-z0-9_\-\s]/g,'').replace(/[\s\-]+/g,'_').replace(/^_+|_+$/g,'');
  for (const [canon, vars] of Object.entries(ALIASES)) {
    REV.set(norm(canon), canon);
    for (const v of vars) REV.set(norm(v), canon);
  }
  const canonicalize = (raw) => {
    const n = norm(raw);
    return REV.get(n) || n; // map known aliases; else keep normalized
  };

  // Pull descriptions if present in data.js (generator usually embeds them)
  const DESC_IN  = D.tagDescriptions || {};
  const descOut = {};
  for (const k of Object.keys(DESC_IN)) {
    descOut[canonicalize(k)] = DESC_IN[k];
  }
  D.tagDescriptions = descOut;

  // Merge nodes by canonical id (keep max centrality)
  const byId = new Map();
  const merges = [];
  const drops  = [];
  for (const n of (D.nodes || [])) {
    const c = canonicalize(n.id);
    if (c !== n.id) merges.push(`${n.id} → ${c}`);
    const prev = byId.get(c);
    if (!prev) {
      byId.set(c, { id:c, centrality: (n.centrality != null ? +n.centrality : undefined) });
    } else {
      const a = (prev.centrality != null) ? +prev.centrality : -Infinity;
      const b = (n.centrality != null) ? +n.centrality : -Infinity;
      prev.centrality = (isFinite(a) || isFinite(b)) ? Math.max(a,b) : undefined;
      drops.push(n.id);
    }
  }
  D.nodes = Array.from(byId.values());

  // Rewrite links to canonical ids & drop invalid/self
  const idSet = new Set(D.nodes.map(n=>n.id));
  D.links = (D.links || []).map(l => {
    const s = canonicalize(l.source && (l.source.id || l.source));
    const t = canonicalize(l.target && (l.target.id || l.target));
    return { source:s, target:t };
  }).filter(l => l.source && l.target && idSet.has(l.source) && idSet.has(l.target) && l.source !== l.target);

  // Normalize pulsesByTag keys
  if (D.pulsesByTag && typeof D.pulsesByTag === 'object') {
    const out = {};
    for (const [k, arr] of Object.entries(D.pulsesByTag)) {
      const c = canonicalize(k);
      if (!out[c]) out[c] = [];
      if (Array.isArray(arr)) out[c].push(...arr);
      if (c !== k) merges.push(`pulsesByTag: ${k} → ${c}`);
    }
    D.pulsesByTag = out;
  }

  // Ensure every node has a description (fallback)
  const titleCase = id => id.replace(/_/g,' ').replace(/\b[a-z]/g, m => m.toUpperCase());
  for (const n of D.nodes) {
    if (!D.tagDescriptions[n.id]) D.tagDescriptions[n.id] = titleCase(n.id);
  }

  // Console audit
  if (merges.length) {
    console.groupCollapsed('%c[normalize_data] Aliases merged','color:#7ad;');
    merges.forEach(m => console.log(m));
    console.groupEnd();
  }
  if (drops.length) {
    console.groupCollapsed('%c[normalize_data] Duplicate nodes merged','color:#fa8;');
    drops.forEach(d => console.log('dropped:', d));
    console.groupEnd();
  }
  console.log('[normalize_data] canonical nodes:', D.nodes.length, 'links:', D.links.length);
})();
