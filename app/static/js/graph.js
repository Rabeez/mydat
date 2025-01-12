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
    });

    // Example interaction
    cy.on("tap", "node", function (evt) {
      const nodeId = evt.target.id();
      console.log("Node clicked:", nodeId);
    });
  }
});
