<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let p = $derived(data?.planning || {});
  let plan = $derived(p.plan || []);
  let goals = $derived(p.goal_facts || []);
</script>

<div class="wrap">
  <div class="goal" class:done={p.goal_satisfied}>
    <span class="panel-title">Goal {p.goal_satisfied ? "✓ satisfied" : ""}</span>
    <div class="chips">
      {#each goals as g}
        <span class="chip">{g.text || g}</span>
      {/each}
    </div>
  </div>

  <div class="panel-title">Plan</div>
  {#if plan.length}
    <ol class="plan">
      {#each plan as step, i}
        <li class:current={i === p.plan_index} class:done={i < (p.plan_index ?? 0)}>
          <span class="sig">{step.signature || step.text || step.name}</span>
        </li>
      {/each}
    </ol>
  {:else}
    <p class="muted">No plan yet — step through to build it.</p>
  {/if}
</div>

<style>
  .wrap {
    min-height: 300px;
    overflow: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .goal {
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 10px;
    background: var(--surface);
  }
  .goal.done {
    border-color: var(--good);
    background: var(--good-soft);
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
  }
  .chip {
    font-family: var(--mono);
    font-size: 0.8rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 1px 8px;
  }
  .plan {
    margin: 0;
    padding-left: 22px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .plan li {
    padding: 4px 6px;
    border-radius: 6px;
  }
  .plan li.current {
    background: var(--accent-soft);
  }
  .plan li.done {
    color: var(--muted);
  }
  .sig {
    font-family: var(--mono);
    font-size: 0.86rem;
  }
  .muted {
    color: var(--muted);
  }
</style>
