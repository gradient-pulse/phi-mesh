const graph = {
  nodes: [
    { id: "software-dev" },
    { id: "rgp-core" },
    { id: "gradient-syntax" },
    { id: "mesh-academy" },
    { id: "coherence" }
  ],
  links: [
    { source: "software-dev", target: "rgp-core" },
    { source: "rgp-core", target: "gradient-syntax" },
    { source: "gradient-syntax", target: "mesh-academy" },
    { source: "mesh-academy", target: "coherence" }
  ]
};
