// https://github.com/catppuccin/palette/blob/main/palette.json
// jq -> with_entries(select(.key != "version")) | with_entries(.value = (.value.colors | with_entries(.value = .value.hex) ) )
catppuccin = {
  latte: {
    rosewater: "#dc8a78",
    flamingo: "#dd7878",
    pink: "#ea76cb",
    mauve: "#8839ef",
    red: "#d20f39",
    maroon: "#e64553",
    peach: "#fe640b",
    yellow: "#df8e1d",
    green: "#40a02b",
    teal: "#179299",
    sky: "#04a5e5",
    sapphire: "#209fb5",
    blue: "#1e66f5",
    lavender: "#7287fd",
    text: "#4c4f69",
    subtext1: "#5c5f77",
    subtext0: "#6c6f85",
    overlay2: "#7c7f93",
    overlay1: "#8c8fa1",
    overlay0: "#9ca0b0",
    surface2: "#acb0be",
    surface1: "#bcc0cc",
    surface0: "#ccd0da",
    base: "#eff1f5",
    mantle: "#e6e9ef",
    crust: "#dce0e8",
  },
  mocha: {
    rosewater: "#f5e0dc",
    flamingo: "#f2cdcd",
    pink: "#f5c2e7",
    mauve: "#cba6f7",
    red: "#f38ba8",
    maroon: "#eba0ac",
    peach: "#fab387",
    yellow: "#f9e2af",
    green: "#a6e3a1",
    teal: "#94e2d5",
    sky: "#89dceb",
    sapphire: "#74c7ec",
    blue: "#89b4fa",
    lavender: "#b4befe",
    text: "#cdd6f4",
    subtext1: "#bac2de",
    subtext0: "#a6adc8",
    overlay2: "#9399b2",
    overlay1: "#7f849c",
    overlay0: "#6c7086",
    surface2: "#585b70",
    surface1: "#45475a",
    surface0: "#313244",
    base: "#1e1e2e",
    mantle: "#181825",
    crust: "#11111b",
  },
};

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
