<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let p = $derived(data?.planning || {});
  let facts = $derived(p.facts || []);
  let applicable = $derived(p.applicable_actions || []);

  // Show the dynamic facts (robot/parcel/keycard/locked) prominently; the
  // static connectivity facts are de-emphasised.
  const DYNAMIC = new Set(["at", "holding", "handempty", "locked", "unlocked"]);
  let dynamicFacts = $derived(facts.filter((f) => DYNAMIC.has(f.predicate)));
  let staticFacts = $derived(facts.filter((f) => !DYNAMIC.has(f.predicate)));
</script>

<div class="wrap">
  <div class="section">
    <span class="panel-title">Current state</span>
    <div class="chips">
      {#each dynamicFacts as f}
        <span class="chip dyn">{f.text}</span>
      {/each}
    </div>
  </div>

  <div class="section">
    <span class="panel-title">Applicable actions</span>
    <div class="actions">
      {#each applicable as a}
        <span class="chip" class:sel={p.selected_action === a.signature}>{a.signature}</span>
      {/each}
      {#if !applicable.length}<span class="muted">none</span>{/if}
    </div>
  </div>

  <details class="section">
    <summary class="panel-title">World facts ({staticFacts.length})</summary>
    <div class="chips">
      {#each staticFacts as f}
        <span class="chip muted-chip">{f.text}</span>
      {/each}
    </div>
  </details>
</div>

<style>
  .wrap {
    min-height: 300px;
    overflow: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .chips,
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .chip {
    font-family: var(--mono);
    font-size: 0.82rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 2px 9px;
    background: var(--surface);
  }
  .chip.dyn {
    background: var(--accent-soft);
    border-color: color-mix(in srgb, var(--accent) 25%, transparent);
    color: var(--accent-strong);
  }
  .chip.sel {
    background: var(--final-soft);
    border-color: var(--final);
  }
  .muted-chip {
    color: var(--muted);
  }
  .muted {
    color: var(--muted);
  }
  summary {
    cursor: pointer;
  }
</style>
