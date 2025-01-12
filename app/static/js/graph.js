document.addEventListener("htmx:afterSwap", async (event) => {
  // Check if the `page-container` has been updated with the graph-container
  const container = document.getElementById("graph-container");
  if (container) {
    console.log("Graph container detected. Initializing Cytoscape...");

    let json = null;
    try {
      const response = await fetch("/graph");
      if (response.ok) {
        json = await response.json();
      }
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }

    // Use jj if valid; otherwise, fallback to window.graphData
    console.log(json);
    window.graphData =
      json && Object.keys(json).length ? json : window.graphData;

    if (!container) {
      console.error("Graph container not found!");
      return;
    }

    // Initialize Cytoscape
    const cy = cytoscape({
      container: container,
      elements: window.graphData,
      layout: { name: "grid" },
      style: [
        // Background color
        {
          selector: "core",
          style: {
            "background-color": "#302D41", // Catppuccin Mocha background
            "text-color": "#D9E0EE", // Text color
          },
        },
        // Node styling
        {
          selector: "node",
          style: {
            "background-color": "#6E5D7E", // Catppuccin Mocha node color
            "border-color": "#D9E0EE", // Light node border
            color: "#D9E0EE", // Text color on nodes
            "z-index": 5, // Ensure nodes are above edges
            label: "data(label)", // Show label from data
            shape: "ellipse", // Default shape: circle (ellipse)
          },
        },
        // Node shape based on type
        {
          selector: 'node[type="data"]',
          style: {
            shape: "ellipse", // Circle shape for "data" type
          },
        },
        {
          selector: 'node[type="analysis"]',
          style: {
            shape: "square", // Square shape for "analysis" type
          },
        },
        // Edge styling
        {
          selector: "edge",
          style: {
            "line-color": "#F2D5CF", // Light edge color
            width: 2, // Edge width
            "target-arrow-shape": "triangle", // Arrow at the target (destination)
            "target-arrow-color": "#F2D5CF", // Arrow color (same as edge line)
            "source-arrow-shape": "none", // No arrow at the source (optional)
            "z-index": 10, // Ensure edges are below nodes
            "arrow-scale": 2, // Scale the arrow to make it more visible
          },
        },
        // Make labels hidden by default (using 'label' style)
      ],
    });

    // Example interaction
    cy.on("tap", "node", function (evt) {
      const nodeId = evt.target.id();
      console.log("Node clicked:", nodeId);
    });
  }
});
