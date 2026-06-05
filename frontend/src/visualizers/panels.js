/** Map of panel "kind" -> visualizer component. Each takes `{ data, cfg }`. */

import SearchTree from "./SearchTree.svelte";
import GraphView from "./GraphView.svelte";
import LabyrinthView from "./LabyrinthView.svelte";
import FoundationText from "./FoundationText.svelte";
import FoundationTokens from "./FoundationTokens.svelte";
import LogicTree from "./LogicTree.svelte";
import LogicClauses from "./LogicClauses.svelte";
import CspVariables from "./CspVariables.svelte";
import CspAssignments from "./CspAssignments.svelte";
import BeliefBars from "./BeliefBars.svelte";
import BeliefUpdate from "./BeliefUpdate.svelte";
import StripsPlan from "./StripsPlan.svelte";
import StripsWorld from "./StripsWorld.svelte";

export const PANELS = {
  tree: SearchTree,
  graph: GraphView,
  labyrinth: LabyrinthView,
  "foundation-text": FoundationText,
  "foundation-tokens": FoundationTokens,
  "logic-tree": LogicTree,
  "logic-clauses": LogicClauses,
  "csp-variables": CspVariables,
  "csp-assignments": CspAssignments,
  "belief-bars": BeliefBars,
  "belief-update": BeliefUpdate,
  "strips-plan": StripsPlan,
  "strips-world": StripsWorld,
};

/** @param {string|undefined} kind */
export function panelComponent(kind) {
  return kind ? PANELS[kind] : null;
}
