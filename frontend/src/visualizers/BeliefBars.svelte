<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let u = $derived(data?.uncertainty || {});
  let rows = $derived(u.belief_rows || []);
  const pct = (x) => `${Math.round((Number(x) || 0) * 100)}%`;
</script>

<div class="wrap">
  <div class="bars">
    {#each rows as r (r.location)}
      <div class="row" class:top={r.location === u.most_likely_location}>
        <div class="rowhead">
          <span class="label">{r.label}</span>
          <span class="val">{pct(r.posterior)}</span>
        </div>
        <div class="track"><span style:width={pct(r.posterior)}></span></div>
      </div>
    {/each}
  </div>
</div>

<style>
  .wrap {
    min-height: 300px;
    overflow: auto;
  }
  .bars {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .row.top .label {
    color: var(--accent-strong);
    font-weight: 700;
  }
  .rowhead {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    margin-bottom: 4px;
  }
  .val {
    font-variant-numeric: tabular-nums;
    color: var(--muted);
  }
  .track {
    height: 12px;
    border-radius: 999px;
    background: var(--surface-2);
    overflow: hidden;
  }
  .track span {
    display: block;
    height: 100%;
    background: var(--accent);
    border-radius: inherit;
  }
  .row.top .track span {
    background: var(--final);
  }
</style>
