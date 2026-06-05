<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data, cfg = {} } = $props();
  let block = $derived(data?.[cfg.dataKey || "csp"] || {});
  let variables = $derived(block.variables || []);
  let assignedCount = $derived(variables.filter((v) => v.assigned_value != null).length);

  const COLOURS = { red: "#dc2626", green: "#16a34a", blue: "#2563eb" };
  const swatch = (v) => (v && (COLOURS[v] || (String(v).startsWith("#") ? v : null))) || null;
</script>

<div class="wrap">
  <div class="summary">{assignedCount} / {variables.length} assigned</div>
  <div class="grid">
    {#each variables as v (v.variable)}
      {@const col = swatch(v.colour || v.assigned_value)}
      <div class="cell" class:assigned={v.assigned_value != null} class:focus={v.is_focus} class:failed={v.is_failed}>
        <div class="swatch" style:background={v.assigned_value != null && col ? col : "transparent"}></div>
        <div class="label">{v.label || v.variable}</div>
        <div class="value">{v.assigned_label || v.assigned_value || "—"}</div>
      </div>
    {/each}
  </div>
</div>

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-height: 300px;
    overflow: auto;
  }
  .summary {
    color: var(--muted);
    font-size: 0.85rem;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
  }
  .cell {
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 10px;
    text-align: center;
    background: var(--surface);
  }
  .cell.focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent);
  }
  .cell.failed {
    border-color: var(--bad);
    background: var(--bad-soft);
  }
  .swatch {
    width: 100%;
    height: 28px;
    border-radius: 6px;
    border: 1px solid var(--line);
    margin-bottom: 8px;
  }
  .label {
    font-weight: 700;
    font-size: 0.85rem;
  }
  .value {
    color: var(--muted);
    font-size: 0.78rem;
    font-family: var(--mono);
    margin-top: 2px;
  }
</style>
