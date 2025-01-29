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
    if (!container) {
      console.error("Graph container not found!");
      return;
    }

    init_graph(json, container);
  }
});

function init_graph(graphData, container) {
  /**
   * Initialize Cytoscape instance.
   * @type {import('cytoscape').Core}
   */
  const cy = cytoscape({
    container: container,
    elements: /** @type {Array} */ (graphData),
    layout: { name: "grid" },
    // TODO: setup Catppuccin palettes and use them instead of raw hex codes
    // use `window.theme` variable
    style: [
      // Background color
      {
        selector: "core",
        style: {
          "background-color": "#302D41", // Catppuccin Mocha background
        },
      },
      // Node styling
      {
        selector: "node",
        style: {
          "background-color": "#6E5D7E", // Catppuccin Mocha node color
          "border-color": "#D9E0EE", // Light node border
          color: "#D9E0EE", // Text color on nodes
          label: "data(name)", // Show label from data
          shape: "ellipse", // Default shape: circle (ellipse)
        },
      },
      // Node shape based on type
      {
        selector: 'node[kind="table"]',
        style: {
          shape: "square",
        },
      },
      {
        selector: 'node[kind="analysis"]',
        style: {
          shape: "ellipse",
        },
      },
      {
        selector: 'node[kind="chart"]',
        style: {
          shape: "diamond",
        },
      },
      // Edge styling
      {
        selector: "edge",
        style: {
          "line-color": "#F2D5CF", // Light edge color
          width: 2, // Edge width
          "mid-target-arrow-shape": "triangle", // Arrow at the target (destination)
          "mid-target-arrow-color": "#F2D5CF", // Arrow color (same as edge line)
          "target-arrow-shape": "triangle", // Arrow at the target (destination)
          "target-arrow-color": "#F2D5CF", // Arrow color (same as edge line)
          "source-arrow-shape": "none", // No arrow at the source (optional)
          "target-distance-from-node": 10,
        },
      },
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
    console.log(evt.target.data());
  });

  cy.on("cxttap", "node", function (evt) {
    const nodeId = evt.target.id();
    console.log("Node right clicked:", nodeId);
    console.log(evt.target.data());

    htmx
      .ajax("POST", "/graph/delete", {
        // TODO: implement OOB swap here to update sidebar charts list
        // will also need to modify delete endpoint
        // ALSO update `files` so the filter dropdown works
        swap: "none",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        values: { node_id: nodeId },
      })
      .then(() => {
        console.log("success");
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
}

init_graph(window.graphData, document.getElementById("graph-container"));
