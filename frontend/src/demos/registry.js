/**
 * Per-demo frontend configuration: which visualizers to mount, whether the
 * embedded editor is available, and the request key the solver expects.
 *
 * `supported` controls whether the new UI renders the demo at all (playback).
 * `hasEditor` is set only for demos whose backend `/solve` converter is wired.
 * Demos absent here render a "coming soon" placeholder.
 */

/**
 * @typedef {Object} DemoConfig
 * @property {boolean} supported
 * @property {"tree"} [left]
 * @property {"graph"} [right]
 * @property {"reachability"|"weighted"} [graphMode]
 * @property {boolean} [hasEditor]
 * @property {string} [problemKey]
 */

const graphReach = (hasEditor) => ({
  supported: true,
  left: "tree",
  right: "graph",
  graphMode: "reachability",
  showMetrics: true,
  hasEditor,
  problemKey: "graph",
});

const graphWeighted = (hasEditor) => ({
  supported: true,
  left: "tree",
  right: "graph",
  graphMode: "weighted",
  showMetrics: true,
  hasEditor,
  problemKey: "graph",
});

/** @type {Record<string, DemoConfig>} */
export const DEMO_CONFIG = {
  labyrinth: {
    supported: true,
    left: "tree",
    right: "labyrinth",
    leftTitle: "Search tree",
    rightTitle: "Maze",
    showMetrics: true,
    hasEditor: true,
    problemKey: "labyrinth",
  },
  delivery: {
    supported: true,
    left: "tree",
    right: "labyrinth",
    leftTitle: "Search tree",
    rightTitle: "Office floor",
    world: "delivery",
    showMetrics: true,
    hasEditor: true,
    problemKey: "labyrinth",
  },
  "graph-bfs": graphReach(true),
  "graph-dfs": graphReach(true),
  "graph-ucs": graphWeighted(true),
  "graph-astar": graphWeighted(true),
  "graph-gbfs": graphWeighted(true),
  // graph-bnb's reference trace delta-encodes tree nodes (see
  // build_search_trace_from_definition), so the ~2000-step trace is small enough
  // to play back. The editor stays off until build_search_trace_from_result lands.
  "graph-bnb": graphWeighted(false),
  "foundation-models": {
    supported: true,
    left: "foundation-tokens",
    right: "foundation-text",
    leftTitle: "Tokens & stats",
    rightTitle: "Tokenised text",
    showMetrics: false,
    hasEditor: false,
    problemKey: "text",
  },
  "logic-dpll": {
    supported: true,
    left: "logic-tree",
    right: "logic-clauses",
    leftTitle: "DPLL tree",
    rightTitle: "Clauses",
    showMetrics: false,
    hasEditor: true,
    problemKey: "logic_problem",
  },
  "csp-map": {
    supported: true,
    left: "csp-variables",
    right: "csp-assignments",
    leftTitle: "Variables & domains",
    rightTitle: "Assignment",
    dataKey: "csp",
    showMetrics: false,
    hasEditor: true,
    problemKey: "csp_problem",
  },
  "csp-delivery": {
    supported: true,
    left: "csp-variables",
    right: "csp-assignments",
    leftTitle: "Deliveries & domains",
    rightTitle: "Schedule",
    dataKey: "delivery_csp",
    showMetrics: false,
    hasEditor: true,
    problemKey: "delivery_problem",
  },
  uncertainty: {
    supported: true,
    left: "belief-bars",
    right: "belief-update",
    leftTitle: "Belief",
    rightTitle: "Bayes update",
    showMetrics: false,
    hasEditor: true,
    problemKey: "uncertainty_problem",
  },
  strips: {
    supported: true,
    left: "strips-plan",
    right: "strips-world",
    leftTitle: "Plan",
    rightTitle: "World state",
    showMetrics: false,
    hasEditor: true,
    problemKey: "strips_problem",
  },
};

/** @param {string} name @returns {DemoConfig} */
export function demoConfig(name) {
  return DEMO_CONFIG[name] || { supported: false };
}
