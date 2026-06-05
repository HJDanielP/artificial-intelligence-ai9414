<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data, cfg = {} } = $props();
  let block = $derived(data?.[cfg.dataKey || "csp"] || {});
  let variables = $derived(block.variables || []);

  const COLOURS = { red: "#dc2626", green: "#16a34a", blue: "#2563eb" };
  const swatch = (v) => (v && (COLOURS[v] || (String(v).startsWith("#") ? v : null))) || null;

  function varClass(v) {
    const c = ["var"];
    if (v.is_focus) c.push("focus");
    if (v.is_failed) c.push("failed");
    if (v.assigned_value != null) c.push("assigned");
    return c.join(" ");
  }
</script>

<div class="wrap">
  {#each variables as v (v.variable)}
    <div class={varClass(v)}>
      <div class="head">
        <span class="name">{v.label || v.variable}</span>
        {#if v.assigned_value != null}
          {#if swatch(v.colour || v.assigned_value)}
            <span class="dot" style:background={swatch(v.colour || v.assigned_value)}></span>
          {/if}
          <span class="assigned-val">{v.assigned_label || v.assigned_value}</span>
        {:else}
          <span class="muted">choosing…</span>
        {/if}
      </div>
      <div class="domain">
        {#each (v.domain_labels || v.domain || []) as opt, i}
          {@const raw = (v.domain || [])[i]}
          <span class="opt">
            {#if swatch(raw)}<span class="dot sm" style:background={swatch(raw)}></span>{/if}
            {opt}
          </span>
        {/each}
        {#if !(v.domain || []).length}
          <span class="wipeout">domain wiped out</span>
        {/if}
      </div>
    </div>
  {/each}
</div>

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-height: 300px;
    overflow: auto;
  }
  .var {
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 8px 10px;
    background: var(--surface);
  }
  .var.focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent);
  }
  .var.failed {
    border-color: var(--bad);
    background: var(--bad-soft);
  }
  .var.assigned {
    background: var(--surface-2);
  }
  .head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }
  .name {
    font-weight: 700;
  }
  .assigned-val {
    font-family: var(--mono);
    font-size: 0.85rem;
  }
  .muted {
    color: var(--muted);
    font-size: 0.8rem;
  }
  .domain {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  .opt {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.78rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 1px 8px;
    background: var(--surface);
  }
  .dot {
    width: 12px;
    height: 12px;
    border-radius: 999px;
    border: 1px solid rgba(0, 0, 0, 0.15);
  }
  .dot.sm {
    width: 9px;
    height: 9px;
  }
  .wipeout {
    color: var(--bad);
    font-size: 0.8rem;
    font-weight: 600;
  }
</style>
