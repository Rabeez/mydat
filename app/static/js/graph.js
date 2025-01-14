/**
 * Event listener for HTMX after a swap action. Initializes a Cytoscape graph
 * if a graph container is detected in the swapped content.
 *
 * @param {Event} event - The HTMX `htmx:afterSwap` event.
 */
document.addEventListener("htmx:afterSwap", async (event) => {
  // Check if the `page-container` has been updated with the graph-container
  const container = /** @type {HTMLElement | null} */ (
    document.getElementById("graph-container")
  );
  if (container) {
    console.log("Graph container detected. Initializing Cytoscape...");

    /** @type {Object<string, any> | null} */
    let json = null;

    try {
      const response = await fetch("/graph/");
      if (response.ok) {
        json = await response.json();
      }
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }

    // Use json if valid; otherwise, fallback to window.graphData
    window.graphData =
      json && Object.keys(json).length ? json : window.graphData;

    if (!container) {
      console.error("Graph container not found!");
      return;
    }

    /**
     * Initialize Cytoscape instance.
     * @type {import('cytoscape').Core}
     */
    const cy = cytoscape({
      container: container,
      elements: /** @type {Array} */ (window.graphData),
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
            label: "data(name)", // Show label from data
            shape: "ellipse", // Default shape: circle (ellipse)
          },
        },
        // Node shape based on type
        {
          selector: 'node[kind="data"]',
          style: {
            shape: "ellipse", // Circle shape for "data" type
          },
        },
        {
          selector: 'node[kind="analysis"]',
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

    /**
     * Add an event listener for tapping on nodes.
     * @param {import('cytoscape').EventObject} evt - Cytoscape event object.
     */
    cy.on("tap", "node", function (evt) {
      // TODO: determine node kind and issue HTTP request
      // if data -> 'view' request and show table head in modal
      // if analysis -> 'modify' request and trigger appropriate modal with 'current' values
      //    -> will require storage of analysis options on server
      const nodeId = evt.target.id();
      console.log("Node clicked:", nodeId);
    });
  }
});
