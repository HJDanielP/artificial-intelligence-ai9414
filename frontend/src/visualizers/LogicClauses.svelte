<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let logic = $derived(data?.logic || null);
  let clauses = $derived(logic?.clauses || []);
  // `assignment` is a list of {variable, value, reason, text} items.
  let assignment = $derived(Array.isArray(logic?.assignment) ? logic.assignment : []);
</script>

{#if logic}
  <div class="wrap">
    <div class="assignments">
      <span class="panel-title">Assignment</span>
      {#if assignment.length}
        <div class="chips">
          {#each assignment as item}
            <span class="assign">{item.text || `${item.variable} = ${item.value ? "T" : "F"}`}</span>
          {/each}
        </div>
      {:else}
        <span class="muted">No assignments yet</span>
      {/if}
    </div>

    <div class="clauses">
      <span class="panel-title">Clauses</span>
      {#each clauses as cl}
        <div class="clause {cl.status}">
          <div class="clause-head">
            <span class="ctext">{cl.text}</span>
            <span class="cstate">{cl.status}</span>
          </div>
          <div class="lits">
            {#each cl.literals as lit}
              <span class="lit {lit.state}">{lit.text}</span>
            {/each}
          </div>
        </div>
      {/each}
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
  .assignments {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .assign {
    font-family: var(--mono);
    font-weight: 700;
    background: var(--accent-soft);
    color: var(--accent-strong);
    border-radius: 6px;
    padding: 2px 8px;
  }
  .muted {
    color: var(--muted);
  }
  .clauses {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .clause {
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 8px 10px;
    background: var(--surface);
  }
  .clause.satisfied {
    border-color: color-mix(in srgb, var(--good) 40%, var(--line));
    background: var(--good-soft);
  }
  .clause.unit {
    border-color: color-mix(in srgb, var(--warn) 40%, var(--line));
    background: var(--warn-soft);
  }
  .clause.contradicted {
    border-color: color-mix(in srgb, var(--bad) 40%, var(--line));
    background: var(--bad-soft);
  }
  .clause-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  .ctext {
    font-family: var(--mono);
    font-weight: 700;
  }
  .cstate {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
  }
  .lits {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .lit {
    font-family: var(--mono);
    font-size: 0.82rem;
    border-radius: 999px;
    padding: 1px 9px;
    border: 1px solid var(--line);
    background: var(--surface);
  }
  .lit.true {
    background: var(--good-soft);
    border-color: color-mix(in srgb, var(--good) 35%, transparent);
  }
  .lit.false {
    background: var(--bad-soft);
    border-color: color-mix(in srgb, var(--bad) 35%, transparent);
  }
  .lit.unassigned {
    color: var(--muted);
  }
</style>
