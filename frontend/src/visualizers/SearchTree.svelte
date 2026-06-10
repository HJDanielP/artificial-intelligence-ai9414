<script>
  import { formatNumber } from "../lib/util.js";
  import { panzoom } from "../lib/panzoom.js";

  /** @type {{ data: any, cfg?: any }} */
  let { data, cfg = {} } = $props();
  let showCost = $derived(cfg.graphMode === "weighted");

  let nodes = $derived((data?.tree?.nodes || []).filter((n) => n.status !== "pruned"));
  let nodeMap = $derived(new Map(nodes.map((n) => [n.tree_id, n])));

  // The SVG viewBox is a fixed camera window; node content is laid out in a
  // larger coordinate space (constant spacing — leaves ~110 wide, levels ~130
  // tall) that the camera pans/zooms over. Deep narrow DFS trees would shrink
  // to an unreadable sliver if we fit the whole thing into the window, so by
  // default the camera stays at a readable zoom and *follows the frontier*
  // (the active node) as playback advances. "Fit" shows the whole tree.
  const VBW = 1000;
  const VBH = 700;
  const FOLLOW_K = 0.62;

  let parents = $derived(new Set(nodes.map((n) => n.parent).filter((p) => p != null)));
  let leafCount = $derived(Math.max(1, nodes.filter((n) => !parents.has(n.tree_id)).length));
  let maxDepth = $derived(nodes.reduce((d, n) => Math.max(d, n.depth || 0), 0));
  let W = $derived(Math.max(VBW, leafCount * 110));
  let H = $derived(Math.max(VBH, (maxDepth + 1) * 130));

  // Whole tree too big to show legibly at once → follow mode; otherwise fit it.
  let bigTree = $derived(Math.min(VBW / W, VBH / H) < FOLLOW_K);
  // The node to keep centred: the active one, else the deepest (end states).
  let focusNode = $derived(
    (data?.search?.active_tree_node && nodeMap.get(data.search.active_tree_node)) ||
      nodes.reduce((best, n) => (!best || (n.depth || 0) > (best.depth || 0) ? n : best), null),
  );

  let controls = $state(/** @type {any} */ (null));
  let follow = $state(true);

  // Drive the camera each step while follow mode is on.
  $effect(() => {
    const api = controls;
    const node = focusNode;
    const big = bigTree;
    const w = W;
    const h = H;
    if (!api || !follow) return;
    if (big && node) api.focusOn(node.x * w, node.y * h, FOLLOW_K);
    else api.fitInto(w, h);
  });

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

<div class="viz">
  <svg
    viewBox="0 0 {VBW} {VBH}"
    class="canvas"
    role="img"
    aria-label="Search tree"
    use:panzoom={{ onInit: (api) => (controls = api), onUserInteract: () => (follow = false) }}
  >
    <g data-zoom-layer>
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
    </g>
  </svg>
  <div class="zoom-controls">
    <button class="icon-btn" onclick={() => controls?.zoomIn()} title="Zoom in" aria-label="Zoom in">+</button>
    <button class="icon-btn" onclick={() => controls?.zoomOut()} title="Zoom out" aria-label="Zoom out">−</button>
    <button
      class="icon-btn wide"
      onclick={() => {
        follow = false;
        controls?.fitInto(W, H);
      }}
      title="Show the whole tree"
    >Fit</button>
    <button
      class="icon-btn wide"
      class:active={follow}
      onclick={() => (follow = true)}
      title="Follow the current node during playback"
    >Follow</button>
  </div>
</div>

<style>
  .viz {
    position: relative;
  }
  .canvas {
    display: block;
    width: 100%;
    aspect-ratio: 10 / 7;
    max-height: 58vh;
    cursor: grab;
    touch-action: none;
  }
  .canvas.is-grabbing {
    cursor: grabbing;
  }
  .zoom-controls {
    position: absolute;
    top: 8px;
    right: 8px;
    display: flex;
    gap: 4px;
  }
  .zoom-controls .icon-btn {
    width: 28px;
    height: 28px;
    font-size: 16px;
    line-height: 1;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 6px;
    color: var(--ink);
    box-shadow: var(--shadow);
  }
  .zoom-controls .icon-btn.wide {
    width: auto;
    padding: 0 8px;
    font-size: 12px;
  }
  .zoom-controls .icon-btn.active {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
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
