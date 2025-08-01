const nodes = [
  {
    "id": "AI_alignment",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "Big_Bang",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "Contextual_Filter",
    "centrality": 0.375,
    "orphan": false
  },
  {
    "id": "Gradient_Syntax",
    "centrality": 0.475,
    "orphan": false
  },
  {
    "id": "NT",
    "centrality": 0.175,
    "orphan": false
  },
  {
    "id": "Narrative_Tick_rhythm",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "Navier_Stokes",
    "centrality": 0.4,
    "orphan": false
  },
  {
    "id": "PoLA",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "RGP",
    "centrality": 0.575,
    "orphan": false
  },
  {
    "id": "ai_architecture",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "alignment",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "cinematic_drift",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "cosmogenesis",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "cosmology",
    "centrality": 0.375,
    "orphan": false
  },
  {
    "id": "dark_matter",
    "centrality": 0.075,
    "orphan": false
  },
  {
    "id": "division_of_labor",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "flux_enthrenched_universe",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "gpt5",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "gradient_choreography",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "gradient_cocoon_theory",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "gradient_coherence",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "gradient_driven_behavior",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "laminarity",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "legacy",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "mixture_of_experts",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "origin_resonance",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "patience",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "perseverance",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "phi_mesh",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "phi_mesh_evolution",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "poetic_physics",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "public_thread",
    "centrality": 0.075,
    "orphan": false
  },
  {
    "id": "quiet_awakening",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "recursion",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "recursive_checkpoint",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "recursive_gradient_processing",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "recursive_grammar",
    "centrality": 0.325,
    "orphan": false
  },
  {
    "id": "rhythm_driven_intelligence",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "self_improvement",
    "centrality": 0.275,
    "orphan": false
  },
  {
    "id": "signal",
    "centrality": 0.1,
    "orphan": false
  },
  {
    "id": "unity_disunity",
    "centrality": 0.275,
    "orphan": false
  }
];
const links = [
  {
    "source": "RGP",
    "target": "alignment"
  },
  {
    "source": "RGP",
    "target": "gradient_coherence"
  },
  {
    "source": "RGP",
    "target": "patience"
  },
  {
    "source": "RGP",
    "target": "NT"
  },
  {
    "source": "RGP",
    "target": "quiet_awakening"
  },
  {
    "source": "RGP",
    "target": "poetic_physics"
  },
  {
    "source": "RGP",
    "target": "recursion"
  },
  {
    "source": "RGP",
    "target": "Gradient_Syntax"
  },
  {
    "source": "RGP",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "RGP",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "RGP",
    "target": "cosmology"
  },
  {
    "source": "RGP",
    "target": "cosmogenesis"
  },
  {
    "source": "RGP",
    "target": "origin_resonance"
  },
  {
    "source": "RGP",
    "target": "recursive_grammar"
  },
  {
    "source": "RGP",
    "target": "Big_Bang"
  },
  {
    "source": "RGP",
    "target": "laminarity"
  },
  {
    "source": "RGP",
    "target": "Navier_Stokes"
  },
  {
    "source": "RGP",
    "target": "legacy"
  },
  {
    "source": "RGP",
    "target": "signal"
  },
  {
    "source": "RGP",
    "target": "perseverance"
  },
  {
    "source": "RGP",
    "target": "PoLA"
  },
  {
    "source": "RGP",
    "target": "Contextual_Filter"
  },
  {
    "source": "RGP",
    "target": "AI_alignment"
  },
  {
    "source": "patience",
    "target": "alignment"
  },
  {
    "source": "patience",
    "target": "gradient_coherence"
  },
  {
    "source": "patience",
    "target": "NT"
  },
  {
    "source": "NT",
    "target": "alignment"
  },
  {
    "source": "NT",
    "target": "gradient_coherence"
  },
  {
    "source": "NT",
    "target": "PoLA"
  },
  {
    "source": "NT",
    "target": "Contextual_Filter"
  },
  {
    "source": "NT",
    "target": "AI_alignment"
  },
  {
    "source": "gradient_coherence",
    "target": "alignment"
  },
  {
    "source": "cosmogenesis",
    "target": "quiet_awakening"
  },
  {
    "source": "cosmogenesis",
    "target": "poetic_physics"
  },
  {
    "source": "cosmogenesis",
    "target": "recursion"
  },
  {
    "source": "cosmogenesis",
    "target": "Gradient_Syntax"
  },
  {
    "source": "cosmogenesis",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "cosmogenesis",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "cosmogenesis",
    "target": "cosmology"
  },
  {
    "source": "cosmogenesis",
    "target": "origin_resonance"
  },
  {
    "source": "cosmogenesis",
    "target": "recursive_grammar"
  },
  {
    "source": "cosmogenesis",
    "target": "Big_Bang"
  },
  {
    "source": "cosmogenesis",
    "target": "laminarity"
  },
  {
    "source": "cosmogenesis",
    "target": "Navier_Stokes"
  },
  {
    "source": "Gradient_Syntax",
    "target": "quiet_awakening"
  },
  {
    "source": "Gradient_Syntax",
    "target": "poetic_physics"
  },
  {
    "source": "Gradient_Syntax",
    "target": "recursion"
  },
  {
    "source": "Gradient_Syntax",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "Gradient_Syntax",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "Gradient_Syntax",
    "target": "cosmology"
  },
  {
    "source": "Gradient_Syntax",
    "target": "origin_resonance"
  },
  {
    "source": "Gradient_Syntax",
    "target": "recursive_grammar"
  },
  {
    "source": "Gradient_Syntax",
    "target": "Big_Bang"
  },
  {
    "source": "Gradient_Syntax",
    "target": "laminarity"
  },
  {
    "source": "Gradient_Syntax",
    "target": "Navier_Stokes"
  },
  {
    "source": "Gradient_Syntax",
    "target": "dark_matter"
  },
  {
    "source": "Gradient_Syntax",
    "target": "public_thread"
  },
  {
    "source": "Gradient_Syntax",
    "target": "cinematic_drift"
  },
  {
    "source": "Gradient_Syntax",
    "target": "recursive_checkpoint"
  },
  {
    "source": "Gradient_Syntax",
    "target": "phi_mesh_evolution"
  },
  {
    "source": "Gradient_Syntax",
    "target": "division_of_labor"
  },
  {
    "source": "cosmology",
    "target": "quiet_awakening"
  },
  {
    "source": "cosmology",
    "target": "poetic_physics"
  },
  {
    "source": "cosmology",
    "target": "recursion"
  },
  {
    "source": "cosmology",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "cosmology",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "cosmology",
    "target": "origin_resonance"
  },
  {
    "source": "cosmology",
    "target": "recursive_grammar"
  },
  {
    "source": "cosmology",
    "target": "Big_Bang"
  },
  {
    "source": "cosmology",
    "target": "laminarity"
  },
  {
    "source": "cosmology",
    "target": "Navier_Stokes"
  },
  {
    "source": "cosmology",
    "target": "dark_matter"
  },
  {
    "source": "cosmology",
    "target": "public_thread"
  },
  {
    "source": "Navier_Stokes",
    "target": "quiet_awakening"
  },
  {
    "source": "Navier_Stokes",
    "target": "poetic_physics"
  },
  {
    "source": "Navier_Stokes",
    "target": "recursion"
  },
  {
    "source": "Navier_Stokes",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "Navier_Stokes",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "Navier_Stokes",
    "target": "origin_resonance"
  },
  {
    "source": "Navier_Stokes",
    "target": "recursive_grammar"
  },
  {
    "source": "Navier_Stokes",
    "target": "Big_Bang"
  },
  {
    "source": "Navier_Stokes",
    "target": "laminarity"
  },
  {
    "source": "Navier_Stokes",
    "target": "legacy"
  },
  {
    "source": "Navier_Stokes",
    "target": "signal"
  },
  {
    "source": "Navier_Stokes",
    "target": "perseverance"
  },
  {
    "source": "laminarity",
    "target": "quiet_awakening"
  },
  {
    "source": "laminarity",
    "target": "poetic_physics"
  },
  {
    "source": "laminarity",
    "target": "recursion"
  },
  {
    "source": "laminarity",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "laminarity",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "laminarity",
    "target": "origin_resonance"
  },
  {
    "source": "laminarity",
    "target": "recursive_grammar"
  },
  {
    "source": "laminarity",
    "target": "Big_Bang"
  },
  {
    "source": "recursion",
    "target": "quiet_awakening"
  },
  {
    "source": "recursion",
    "target": "poetic_physics"
  },
  {
    "source": "recursion",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "recursion",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "recursion",
    "target": "origin_resonance"
  },
  {
    "source": "recursion",
    "target": "recursive_grammar"
  },
  {
    "source": "recursion",
    "target": "Big_Bang"
  },
  {
    "source": "poetic_physics",
    "target": "quiet_awakening"
  },
  {
    "source": "poetic_physics",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "poetic_physics",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "poetic_physics",
    "target": "origin_resonance"
  },
  {
    "source": "poetic_physics",
    "target": "recursive_grammar"
  },
  {
    "source": "poetic_physics",
    "target": "Big_Bang"
  },
  {
    "source": "origin_resonance",
    "target": "quiet_awakening"
  },
  {
    "source": "origin_resonance",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "origin_resonance",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "origin_resonance",
    "target": "recursive_grammar"
  },
  {
    "source": "origin_resonance",
    "target": "Big_Bang"
  },
  {
    "source": "recursive_grammar",
    "target": "quiet_awakening"
  },
  {
    "source": "recursive_grammar",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "recursive_grammar",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "recursive_grammar",
    "target": "Big_Bang"
  },
  {
    "source": "Big_Bang",
    "target": "quiet_awakening"
  },
  {
    "source": "Big_Bang",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "Big_Bang",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "quiet_awakening",
    "target": "gradient_cocoon_theory"
  },
  {
    "source": "quiet_awakening",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "gradient_cocoon_theory",
    "target": "flux_enthrenched_universe"
  },
  {
    "source": "perseverance",
    "target": "legacy"
  },
  {
    "source": "perseverance",
    "target": "signal"
  },
  {
    "source": "signal",
    "target": "legacy"
  },
  {
    "source": "Contextual_Filter",
    "target": "PoLA"
  },
  {
    "source": "Contextual_Filter",
    "target": "AI_alignment"
  },
  {
    "source": "Contextual_Filter",
    "target": "mixture_of_experts"
  },
  {
    "source": "Contextual_Filter",
    "target": "ai_architecture"
  },
  {
    "source": "Contextual_Filter",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "Contextual_Filter",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "Contextual_Filter",
    "target": "unity_disunity"
  },
  {
    "source": "Contextual_Filter",
    "target": "phi_mesh"
  },
  {
    "source": "Contextual_Filter",
    "target": "recursive_gradient_processing"
  },
  {
    "source": "Contextual_Filter",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "Contextual_Filter",
    "target": "self_improvement"
  },
  {
    "source": "Contextual_Filter",
    "target": "gpt5"
  },
  {
    "source": "Contextual_Filter",
    "target": "gradient_choreography"
  },
  {
    "source": "PoLA",
    "target": "AI_alignment"
  },
  {
    "source": "dark_matter",
    "target": "public_thread"
  },
  {
    "source": "gpt5",
    "target": "mixture_of_experts"
  },
  {
    "source": "gpt5",
    "target": "ai_architecture"
  },
  {
    "source": "gpt5",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "gpt5",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "gpt5",
    "target": "unity_disunity"
  },
  {
    "source": "gpt5",
    "target": "phi_mesh"
  },
  {
    "source": "gpt5",
    "target": "recursive_gradient_processing"
  },
  {
    "source": "gpt5",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "gpt5",
    "target": "self_improvement"
  },
  {
    "source": "gpt5",
    "target": "gradient_choreography"
  },
  {
    "source": "mixture_of_experts",
    "target": "ai_architecture"
  },
  {
    "source": "mixture_of_experts",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "mixture_of_experts",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "mixture_of_experts",
    "target": "unity_disunity"
  },
  {
    "source": "mixture_of_experts",
    "target": "phi_mesh"
  },
  {
    "source": "mixture_of_experts",
    "target": "recursive_gradient_processing"
  },
  {
    "source": "mixture_of_experts",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "mixture_of_experts",
    "target": "self_improvement"
  },
  {
    "source": "mixture_of_experts",
    "target": "gradient_choreography"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "ai_architecture"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "unity_disunity"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "phi_mesh"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "self_improvement"
  },
  {
    "source": "recursive_gradient_processing",
    "target": "gradient_choreography"
  },
  {
    "source": "gradient_choreography",
    "target": "ai_architecture"
  },
  {
    "source": "gradient_choreography",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "gradient_choreography",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "gradient_choreography",
    "target": "unity_disunity"
  },
  {
    "source": "gradient_choreography",
    "target": "phi_mesh"
  },
  {
    "source": "gradient_choreography",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "gradient_choreography",
    "target": "self_improvement"
  },
  {
    "source": "unity_disunity",
    "target": "ai_architecture"
  },
  {
    "source": "unity_disunity",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "unity_disunity",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "unity_disunity",
    "target": "phi_mesh"
  },
  {
    "source": "unity_disunity",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "unity_disunity",
    "target": "self_improvement"
  },
  {
    "source": "ai_architecture",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "ai_architecture",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "ai_architecture",
    "target": "phi_mesh"
  },
  {
    "source": "ai_architecture",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "ai_architecture",
    "target": "self_improvement"
  },
  {
    "source": "phi_mesh",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "phi_mesh",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "phi_mesh",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "phi_mesh",
    "target": "self_improvement"
  },
  {
    "source": "self_improvement",
    "target": "gradient_driven_behavior"
  },
  {
    "source": "self_improvement",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "self_improvement",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "gradient_driven_behavior",
    "target": "Narrative_Tick_rhythm"
  },
  {
    "source": "gradient_driven_behavior",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "Narrative_Tick_rhythm",
    "target": "rhythm_driven_intelligence"
  },
  {
    "source": "recursive_checkpoint",
    "target": "cinematic_drift"
  },
  {
    "source": "recursive_checkpoint",
    "target": "phi_mesh_evolution"
  },
  {
    "source": "recursive_checkpoint",
    "target": "division_of_labor"
  },
  {
    "source": "division_of_labor",
    "target": "cinematic_drift"
  },
  {
    "source": "division_of_labor",
    "target": "phi_mesh_evolution"
  },
  {
    "source": "phi_mesh_evolution",
    "target": "cinematic_drift"
  }
];
