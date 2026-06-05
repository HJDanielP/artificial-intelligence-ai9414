<script>
  import { edgeId, pathToEdgeIds } from "../lib/util.js";

  /** @type {{ data: any, cfg?: any }} */
  let { data, cfg = {} } = $props();
  let mode = $derived(cfg.graphMode || "reachability");

  const W = 1000;
  const H = 700;

  let graph = $derived(data?.graph || null);
  let search = $derived(data?.search || {});
  let nodeMap = $derived(new Map((graph?.nodes || []).map((n) => [n.id, n])));

  let currentPath = $derived(new Set(search.current_graph_path || []));
  let visited = $derived(new Set(search.visited_order || []));
  let deadEnds = $derived(new Set(search.dead_end_nodes || []));
  let bestPath = $derived(new Set(search.best_graph_path || []));
  let finalPath = $derived(new Set(search.final_graph_path || []));
  let activeNode = $derived((search.current_graph_path || []).slice(-1)[0]);

  let exploredEdges = $derived(
    new Set((search.explored_graph_edges || []).map(([u, v]) => edgeId(u, v))),
  );
  let currentEdges = $derived(pathToEdgeIds(search.current_graph_path || []));
  let bestEdges = $derived(pathToEdgeIds(search.best_graph_path || []));
  let finalEdges = $derived(pathToEdgeIds(search.final_graph_path || []));
  let consideredEdge = $derived(
    search.considered_edge ? edgeId(search.considered_edge[0], search.considered_edge[1]) : null,
  );

  function eid(edge) {
    return edge.id || edgeId(edge.u, edge.v);
  }

  function nodeClass(node) {
    const c = ["graph-node"];
    if (node.id === graph.start) c.push("start");
    if (node.id === graph.goal) c.push("goal");
    if (visited.has(node.id)) c.push("visited");
    if (deadEnds.has(node.id)) c.push("dead-end");
    if (currentPath.has(node.id)) c.push("current");
    if (bestPath.has(node.id)) c.push("best");
    if (finalPath.has(node.id)) c.push("final");
    if (activeNode === node.id) c.push("active");
    return c.join(" ");
  }
</script>

{#if graph}
  <svg viewBox="0 0 {W} {H}" class="canvas" role="img" aria-label="Problem graph">
    <g>
      {#each graph.edges as edge}
        {@const a = nodeMap.get(edge.u)}
        {@const b = nodeMap.get(edge.v)}
        {@const id = eid(edge)}
        <line class="graph-edge" x1={a.x * W} y1={a.y * H} x2={b.x * W} y2={b.y * H} />
        {#if exploredEdges.has(id)}
          <line class="graph-overlay explored" x1={a.x * W} y1={a.y * H} x2={b.x * W} y2={b.y * H} />
        {/if}
        {#if mode === "weighted" && bestEdges.has(id)}
          <line class="graph-overlay best" x1={a.x * W} y1={a.y * H} x2={b.x * W} y2={b.y * H} />
        {/if}
        {#if currentEdges.has(id)}
          <line class="graph-overlay current" x1={a.x * W} y1={a.y * H} x2={b.x * W} y2={b.y * H} />
        {/if}
        {#if consideredEdge === id}
          <line class="graph-overlay considered" x1={a.x * W} y1={a.y * H} x2={b.x * W} y2={b.y * H} />
        {/if}
        {#if finalEdges.has(id)}
          <line class="graph-overlay final" x1={a.x * W} y1={a.y * H} x2={b.x * W} y2={b.y * H} />
        {/if}
        {#if mode === "weighted"}
          <text class="graph-cost" x={((a.x + b.x) / 2) * W} y={((a.y + b.y) / 2) * H - 8}>
            {Number(edge.cost).toFixed(2)}
          </text>
        {/if}
      {/each}
    </g>
    <g>
      {#each graph.nodes as node (node.id)}
        <g class={nodeClass(node)} transform="translate({node.x * W}, {node.y * H})">
          <circle class="graph-node-circle" r="30" />
          <text class="graph-node-label">{node.id}</text>
        </g>
      {/each}
    </g>
  </svg>
{/if}

<style>
  .canvas {
    display: block;
    width: 100%;
    aspect-ratio: 10 / 7;
    max-height: 58vh;
  }
  .graph-edge {
    fill: none;
    stroke: var(--line-strong);
    stroke-width: 3;
  }
  .graph-overlay {
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .graph-overlay.explored {
    stroke: var(--muted);
    stroke-width: 5;
    opacity: 0.6;
  }
  .graph-overlay.current {
    stroke: var(--accent);
    stroke-width: 8;
  }
  .graph-overlay.best {
    stroke: var(--warn);
    stroke-width: 7;
  }
  .graph-overlay.considered {
    stroke: var(--accent);
    stroke-width: 6;
    stroke-dasharray: 10 8;
  }
  .graph-overlay.final {
    stroke: var(--final);
    stroke-width: 10;
  }
  .graph-cost {
    fill: var(--muted);
    font-size: 18px;
    text-anchor: middle;
  }
  .graph-node-circle {
    fill: var(--surface);
    stroke: var(--line-strong);
    stroke-width: 4;
  }
  .graph-node.start .graph-node-circle {
    fill: var(--accent-soft);
    stroke: var(--accent);
  }
  .graph-node.goal .graph-node-circle {
    fill: color-mix(in srgb, var(--warn) 16%, var(--surface));
    stroke: var(--warn);
  }
  .graph-node.visited .graph-node-circle {
    fill: var(--surface-2);
  }
  .graph-node.dead-end .graph-node-circle {
    fill: color-mix(in srgb, var(--bad) 18%, var(--surface));
    stroke: var(--bad);
  }
  .graph-node.current .graph-node-circle {
    fill: var(--accent-soft);
  }
  .graph-node.active .graph-node-circle {
    stroke: var(--accent);
    stroke-width: 6;
  }
  .graph-node.final .graph-node-circle {
    fill: color-mix(in srgb, var(--final) 16%, var(--surface));
    stroke: var(--final);
    stroke-width: 6;
  }
  .graph-node-label {
    fill: var(--ink);
    font-size: 26px;
    font-weight: 700;
    text-anchor: middle;
    dominant-baseline: middle;
  }
</style>
