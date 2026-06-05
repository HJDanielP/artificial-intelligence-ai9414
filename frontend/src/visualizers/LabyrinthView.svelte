<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data, cfg = {} } = $props();

  const W = 1000;
  const H = 700;
  const key = (cell) => `${cell[0]},${cell[1]}`;

  let lab = $derived(data?.labyrinth || null);
  let search = $derived(data?.search || {});
  let delivery = $derived(cfg.world === "delivery");

  let geom = $derived.by(() => {
    if (!lab) return null;
    const cell = Math.min(880 / lab.cols, 620 / lab.rows);
    return {
      cell,
      ox: (W - lab.cols * cell) / 2,
      oy: (H - lab.rows * cell) / 2,
    };
  });

  let visited = $derived(new Set((search.visited_order || []).map(key)));
  let route = $derived(new Set((search.current_route || []).map(key)));
  let deadEnds = $derived(new Set((search.dead_end_cells || []).map(key)));
  let finalPath = $derived(new Set((search.final_path || []).map(key)));

  function cellClass(r, c, value) {
    const cls = ["maze-cell"];
    if (delivery) cls.push("delivery-cell");
    if (value === "#") {
      cls.push("wall");
      return cls.join(" ");
    }
    cls.push("open");
    const k = `${r},${c}`;
    if (visited.has(k)) cls.push("visited");
    if (deadEnds.has(k)) cls.push("dead-end");
    if (route.has(k)) cls.push("current");
    if (finalPath.has(k)) cls.push("final");
    if (lab.start[0] === r && lab.start[1] === c) cls.push("start");
    if (lab.exit[0] === r && lab.exit[1] === c) cls.push("exit");
    return cls.join(" ");
  }
</script>

{#if lab && geom}
  <svg viewBox="0 0 {W} {H}" class="canvas" role="img" aria-label="Maze">
    {#each lab.grid as rowStr, r}
      {#each rowStr.split("") as value, c}
        {@const x = geom.ox + c * geom.cell}
        {@const y = geom.oy + r * geom.cell}
        <rect class={cellClass(r, c, value)} {x} {y} width={geom.cell} height={geom.cell} rx={Math.max(1, geom.cell * 0.14)} />
        {#if delivery && value === "S"}
          {@const cx = x + geom.cell / 2}
          {@const cy = y + geom.cell / 2}
          {@const rad = geom.cell * 0.32}
          <polygon class="delivery-robot" points="{cx},{cy - rad} {cx - rad * 0.92},{cy + rad * 0.78} {cx + rad * 0.92},{cy + rad * 0.78}" />
        {:else if delivery && value === "E"}
          <circle class="delivery-goal" cx={x + geom.cell / 2} cy={y + geom.cell / 2} r={geom.cell * 0.32} />
        {:else if value === "S" || value === "E"}
          <text class="maze-cell-label" x={x + geom.cell / 2} y={y + geom.cell / 2 + Math.min(geom.cell * 0.18, 6)}>{value}</text>
        {/if}
      {/each}
    {/each}
  </svg>
{/if}

<style>
  .canvas {
    display: block;
    width: 100%;
    aspect-ratio: 10 / 7;
    max-height: 58vh;
  }
  .maze-cell {
    stroke: rgba(31, 40, 48, 0.08);
    stroke-width: 1;
  }
  .maze-cell.wall {
    fill: #2f3941;
  }
  .maze-cell.open {
    fill: var(--surface-2);
  }
  .maze-cell.visited {
    fill: var(--accent-soft);
  }
  .maze-cell.dead-end {
    fill: color-mix(in srgb, var(--bad) 22%, var(--surface));
  }
  .maze-cell.current {
    fill: color-mix(in srgb, var(--accent) 45%, var(--surface));
  }
  .maze-cell.final {
    fill: color-mix(in srgb, var(--final) 42%, var(--surface));
  }
  .maze-cell.start {
    stroke: var(--accent);
    stroke-width: 2.5;
  }
  .maze-cell.exit {
    stroke: var(--warn);
    stroke-width: 2.5;
  }
  /* Delivery "dark office" styling */
  .maze-cell.delivery-cell.wall {
    fill: #5b5e5b;
  }
  .maze-cell.delivery-cell.open {
    fill: #0b0b0b;
    stroke: rgba(255, 255, 255, 0.16);
  }
  .maze-cell.delivery-cell.visited {
    fill: color-mix(in srgb, var(--accent) 55%, #0b0b0b);
  }
  .maze-cell.delivery-cell.current {
    fill: color-mix(in srgb, var(--accent) 80%, #0b0b0b);
  }
  .maze-cell.delivery-cell.final {
    fill: color-mix(in srgb, var(--warn) 70%, #0b0b0b);
  }
  .maze-cell-label {
    fill: #fff;
    font-size: 14px;
    font-weight: 700;
    text-anchor: middle;
  }
  .delivery-robot {
    fill: #ff2a16;
    stroke: rgba(255, 208, 200, 0.95);
    stroke-width: 2;
  }
  .delivery-goal {
    fill: #ffd400;
  }
</style>
