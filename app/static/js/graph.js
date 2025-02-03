// https://github.com/catppuccin/palette/blob/main/palette.json
// jq -> with_entries(select(.key != "version")) | with_entries(.value = (.value.colors | with_entries(.value = .value.hex) ) )

/**
 * @typedef {Record<"rosewater" | "flamingo" | "pink" | "mauve" | "red" | "maroon" |
 * "peach" | "yellow" | "green" | "teal" | "sky" | "sapphire" | "blue" | "lavender" |
 * "text" | "subtext1" | "subtext0" | "overlay2" | "overlay1" | "overlay0" |
 * "surface2" | "surface1" | "surface0" | "base" | "mantle" | "crust", string>} CatppuccinPalette
 */

/**
 * @typedef {{ latte: CatppuccinPalette, mocha: CatppuccinPalette }} CatppuccinThemes
 */

/** @type {CatppuccinThemes} */
const catppuccin = {
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
      const response = await fetch("/graph");
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
  const theme = /** @type {keyof CatppuccinThemes} */ (window.theme);

  /**
   * Initialize Cytoscape instance.
   * @type {import('cytoscape').Core}
   */
  const cy = cytoscape({
    container: container,
    elements: /** @type {Array} */ (graphData),
    layout: { name: "dagre" },
    style: [
      // Background color
      {
        selector: "core",
        style: {
          "background-color": catppuccin[theme].base,
        },
      },
      // Node styling
      {
        selector: "node",
        style: {
          "background-color": catppuccin[theme].mauve,
          "border-color": catppuccin[theme].surface0,
          color: catppuccin[theme].text,
          label: "data(name)",
          shape: "ellipse",
        },
      },
      // Node shape based on type
      {
        selector: 'node[kind="table"]',
        style: {
          shape: "square",
          "background-color": catppuccin[theme].mauve,
        },
      },
      {
        selector: 'node[kind="analysis"]',
        style: {
          shape: "ellipse",
          "background-color": catppuccin[theme].peach,
        },
      },
      {
        selector: 'node[kind="chart"]',
        style: {
          shape: "triangle",
          "background-color": catppuccin[theme].teal,
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
          "line-color": catppuccin[theme].surface2,
          width: 2, // Edge width
          "mid-target-arrow-shape": "triangle",
          "mid-target-arrow-color": catppuccin[theme].surface2,
          "target-arrow-shape": "triangle",
          "target-arrow-color": catppuccin[theme].surface2,
          "source-arrow-shape": "none",
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
    const data = evt.target.data();
    console.log("HTMX request triggered:", {
      node_id: nodeId,
      node_kind: data.kind,
      node_subkind: data.subkind,
    });
    evt.stopPropagation();
    evt.preventDefault();

    let swap = "";
    let target_elem = "";
    if (data.kind === "analysis") {
      swap = "innerHTML";
      target_elem = `#modal_${data.subkind}`;
    } else if (data.kind === "table") {
      swap = "innerHTML";
      target_elem = `#modal_${data.kind}`;
    } else {
      swap = "none";
      target_elem = undefined;
    }
    console.log(target_elem);
    htmx
      .ajax("GET", "/graph/view", {
        swap: swap,
        target: target_elem,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        values: {
          node_id: nodeId,
          node_kind: data.kind,
          node_subkind: data.subkind,
        },
      })
      .then(() => {
        if (target_elem) {
          document.getElementById(target_elem.slice(1)).showModal();
          console.log("success fetch modal", target_elem.slice(1));
        } else {
          document.getElementById(`sb_btn_${nodeId}`).click();
          console.log("success chart redirect", nodeId);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

  cy.on("cxttap", "node", function (evt) {
    const nodeId = evt.target.id();
    console.log("Node right clicked:", nodeId);
    console.log(evt.target.data());

    htmx
      .ajax("POST", "/graph/delete", {
        // TODO: implement OOB swap here to update `files` list in new_chart and new_filter modals????
        // will also need to modify delete endpoint
        swap: "outerHTML",
        target: "#sidebar-charts-list",
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
