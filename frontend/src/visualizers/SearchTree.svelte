<script>
  import { formatNumber } from "../lib/util.js";

  /** @type {{ data: any, cfg?: any }} */
  let { data, cfg = {} } = $props();
  let showCost = $derived(cfg.graphMode === "weighted");

  const W = 1000;
  const H = 700;

  let nodes = $derived((data?.tree?.nodes || []).filter((n) => n.status !== "pruned"));
  let nodeMap = $derived(new Map(nodes.map((n) => [n.tree_id, n])));
  let activePath = $derived(new Set(data?.search?.active_tree_path || []));
  let bestPath = $derived(new Set(data?.search?.best_tree_path || []));
  let finalPath = $derived(
    new Set([...(data?.search?.final_tree_path || []), ...(data?.search?.active_tree_path || [])]),
  );

  function linkClass(n) {
    const c = ["tree-link"];
    if (activePath.has(n.tree_id) && activePath.has(n.parent)) c.push("active");
    if (bestPath.has(n.tree_id) && bestPath.has(n.parent)) c.push("best");
    if (finalPath.has(n.tree_id) && finalPath.has(n.parent)) c.push("final");
    return c.join(" ");
  }

  function nodeClass(n) {
    const c = ["tree-node", n.status];
    if (data?.search?.active_tree_node === n.tree_id) c.push("active");
    if (activePath.has(n.tree_id)) c.push("branch");
    if (bestPath.has(n.tree_id)) c.push("best");
    if (finalPath.has(n.tree_id)) c.push("final");
    return c.join(" ");
  }
</script>

<svg viewBox="0 0 {W} {H}" class="canvas" role="img" aria-label="Search tree">
  <g>
    {#each nodes as n (n.tree_id)}
      {#if n.parent && nodeMap.has(n.parent)}
        {@const p = nodeMap.get(n.parent)}
        <line
          class={linkClass(n)}
          x1={p.x * W}
          y1={p.y * H}
          x2={n.x * W}
          y2={n.y * H}
        />
      {/if}
    {/each}
  </g>
  <g>
    {#each nodes as n (n.tree_id)}
      <g class={nodeClass(n)} transform="translate({n.x * W}, {n.y * H})">
        <circle class="tree-node-circle" r="34" />
        <text class="tree-node-label" y={showCost ? -6 : 4}>{n.graph_node}</text>
        {#if showCost}
          <text class="tree-node-cost" y="24">{formatNumber(n.path_cost)}</text>
        {/if}
      </g>
    {/each}
  </g>
</svg>

<style>
  .canvas {
    display: block;
    width: 100%;
    aspect-ratio: 10 / 7;
    max-height: 58vh;
  }
  .tree-link {
    fill: none;
    stroke: var(--line-strong);
    stroke-width: 3;
  }
  .tree-link.active {
    stroke: var(--accent);
    stroke-width: 5;
  }
  .tree-link.best {
    stroke: var(--warn);
    stroke-width: 5;
  }
  .tree-link.final {
    stroke: var(--final);
    stroke-width: 6;
  }
  .tree-node-circle {
    fill: var(--surface);
    stroke: var(--line-strong);
    stroke-width: 3;
  }
  .tree-node.active .tree-node-circle {
    fill: var(--accent-soft);
    stroke: var(--accent);
    stroke-width: 5;
  }
  .tree-node.branch .tree-node-circle {
    fill: var(--accent-soft);
  }
  .tree-node.expanded .tree-node-circle {
    fill: var(--surface-2);
  }
  .tree-node.final .tree-node-circle {
    fill: color-mix(in srgb, var(--final) 14%, var(--surface));
    stroke: var(--final);
    stroke-width: 5;
  }
  .tree-node-label {
    font-size: 26px;
    font-weight: 700;
    fill: var(--ink);
    text-anchor: middle;
  }
  .tree-node-cost {
    font-size: 18px;
    fill: var(--muted);
    text-anchor: middle;
  }
</style>
