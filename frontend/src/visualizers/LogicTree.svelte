<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  const W = 1000;
  const H = 700;

  let nodes = $derived(data?.tree?.nodes || []);
  let nodeMap = $derived(new Map(nodes.map((n) => [n.tree_id, n])));
  let activePath = $derived(new Set(data?.search?.active_tree_path || []));

  function nodeClass(n) {
    const c = ["node", n.status];
    if (data?.search?.active_tree_node === n.tree_id) c.push("active");
    return c.join(" ");
  }
</script>

<svg viewBox="0 0 {W} {H}" class="canvas" role="img" aria-label="DPLL tree">
  <g>
    {#each nodes as n (n.tree_id)}
      {#if n.parent && nodeMap.has(n.parent)}
        {@const p = nodeMap.get(n.parent)}
        <line
          class="link"
          class:active={activePath.has(n.tree_id) && activePath.has(n.parent)}
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
        <rect class="card" x="-86" y="-32" width="172" height="64" rx="12" />
        <text class="heading" y="-6">{n.graph_node}</text>
        <text class="sub" y="13">{n.assignment_text || ""}</text>
        <text class="reason" y="27">{n.reason || ""}</text>
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
  .link {
    fill: none;
    stroke: var(--line-strong);
    stroke-width: 3;
  }
  .link.active {
    stroke: var(--accent);
    stroke-width: 4;
  }
  .card {
    fill: var(--surface);
    stroke: var(--line-strong);
    stroke-width: 2.5;
  }
  .node.active .card {
    fill: var(--accent-soft);
    stroke: var(--accent);
  }
  .node.forced .card {
    fill: var(--warn-soft);
    stroke: var(--warn);
  }
  .node.contradiction .card {
    fill: var(--bad-soft);
    stroke: var(--bad);
  }
  .node.solution .card {
    fill: var(--final-soft);
    stroke: var(--final);
    stroke-width: 4;
  }
  .heading {
    fill: var(--ink);
    font-size: 19px;
    font-weight: 700;
    text-anchor: middle;
  }
  .sub {
    fill: var(--muted);
    font-size: 12px;
    text-anchor: middle;
  }
  .reason {
    fill: var(--muted);
    font-size: 10px;
    text-anchor: middle;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
</style>
