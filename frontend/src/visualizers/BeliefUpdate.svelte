<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let u = $derived(data?.uncertainty || {});
  let rows = $derived(u.belief_rows || []);
  const f = (x) => (x == null ? "—" : Number(x).toFixed(3));
</script>

<div class="wrap">
  <div class="ctx">
    <div><span class="k">Action</span> {u.current_action || "—"}</div>
    <div><span class="k">Observation</span> {u.current_observation || "—"}</div>
    <div><span class="k">Most likely</span> {u.most_likely_label || "—"}</div>
  </div>

  <div class="panel-title">Bayes filter update</div>
  <table>
    <thead>
      <tr><th>Room</th><th>prior</th><th>predict</th><th>likeli.</th><th>post.</th></tr>
    </thead>
    <tbody>
      {#each rows as r (r.location)}
        <tr class:top={r.location === u.most_likely_location}>
          <td>{r.label}</td>
          <td>{f(r.prior)}</td>
          <td>{f(r.predicted)}</td>
          <td>{f(r.likelihood)}</td>
          <td>{f(r.posterior)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .wrap {
    min-height: 300px;
    overflow: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .ctx {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.9rem;
  }
  .k {
    display: inline-block;
    min-width: 92px;
    color: var(--muted);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    font-variant-numeric: tabular-nums;
  }
  th,
  td {
    padding: 5px 6px;
    border-bottom: 1px solid var(--line);
    text-align: right;
  }
  th:first-child,
  td:first-child {
    text-align: left;
  }
  th {
    color: var(--muted);
    font-size: 0.68rem;
    text-transform: uppercase;
  }
  tr.top {
    background: var(--final-soft);
  }
</style>
