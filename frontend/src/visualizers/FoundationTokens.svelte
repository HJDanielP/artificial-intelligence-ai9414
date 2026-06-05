<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let fm = $derived(data?.foundation_models || null);
  let stats = $derived(fm?.stats || {});
  let comparison = $derived(fm?.comparison || []);
</script>

{#if fm}
  <div class="wrap">
    <div class="stats">
      <div class="card"><span class="k">Tokens</span><strong>{stats.token_count ?? "—"}</strong></div>
      <div class="card"><span class="k">Characters</span><strong>{stats.character_count ?? "—"}</strong></div>
      <div class="card"><span class="k">Avg length</span><strong>{stats.average_token_length ?? "—"}</strong></div>
      <div class="card"><span class="k">Context</span><strong>{stats.context_usage ?? "—"}</strong></div>
    </div>

    <div class="section">
      <div class="panel-title">Tokeniser comparison</div>
      <table>
        <thead><tr><th>Tokeniser</th><th>Tokens</th><th>Avg len</th></tr></thead>
        <tbody>
          {#each comparison as row}
            <tr class:active={row.active}>
              <td>{row.label}</td>
              <td>{row.token_count}</td>
              <td>{row.average_token_length}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="section">
      <div class="panel-title">Tokens ({(fm.tokens || []).length})</div>
      <div class="chips">
        {#each fm.tokens || [] as t}
          <span class="chip" title={"id " + t.token_id}>{t.text === " " ? "␣" : t.text}</span>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    gap: 14px;
    min-height: 300px;
    overflow: auto;
  }
  .stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .card {
    background: var(--surface-2);
    border-radius: var(--radius-sm);
    padding: 8px 10px;
  }
  .card .k {
    display: block;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
  }
  .card strong {
    font-size: 1.05rem;
  }
  .section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
  }
  th,
  td {
    text-align: left;
    padding: 6px 8px;
    border-bottom: 1px solid var(--line);
  }
  th {
    color: var(--muted);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  tr.active {
    background: var(--accent-soft);
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  .chip {
    font-family: var(--mono);
    font-size: 0.82rem;
    background: var(--surface-2);
    border: 1px solid var(--line);
    border-radius: 5px;
    padding: 1px 6px;
  }
</style>
