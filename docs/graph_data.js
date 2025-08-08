window.graph = {
  nodes: [
    { id: 0, label: "RGP", centrality: 0.8 },
    { id: 1, label: "gradient_syntax", centrality: 0.6 },
    { id: 2, label: "Navier_Stokes", centrality: 0.4 }
  ],
  links: [
    { source: 0, target: 1 },
    { source: 1, target: 2 },
    { source: 2, target: 0 }
  ]
};
