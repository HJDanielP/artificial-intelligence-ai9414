<script>
  import { store, currentStep, currentSnapshot } from "../lib/store.svelte.js";

  let step = $derived(currentStep());
  let snapshot = $derived(currentSnapshot());
  let status = $derived(snapshot?.search?.status || "ready");
</script>

<div class="panel explanation">
  <div class="head">
    <span class="event">{step.event_type || "initialise"}</span>
    <span class="pill info">{status}</span>
  </div>
  <h3>{step.label || "Initial state"}</h3>
  <p class="annotation">{step.annotation || snapshot?.example_subtitle || ""}</p>
  {#if step.teaching_note}
    <p class="note">{step.teaching_note}</p>
  {/if}
</div>

<style>
  .explanation {
    padding: 14px 16px;
  }
  .head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .event {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
  }
  h3 {
    margin: 0 0 6px;
    font-size: 1.1rem;
  }
  .annotation {
    margin: 0;
    line-height: 1.5;
  }
  .note {
    margin: 8px 0 0;
    color: var(--muted);
    line-height: 1.5;
  }
</style>
