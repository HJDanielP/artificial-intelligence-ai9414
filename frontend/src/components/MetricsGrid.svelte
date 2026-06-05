<script>
  import { currentSnapshot } from "../lib/store.svelte.js";

  let search = $derived(currentSnapshot()?.search || {});

  let metrics = $derived([
    { label: "Explored nodes", value: search.explored_count ?? (search.visited_order || []).length },
    { label: "Current depth", value: search.current_depth ?? 0 },
    { label: "Frontier path", value: (search.current_graph_path || []).join(" → ") || "—" },
    { label: "Found", value: search.found ? "yes" : "no" },
  ]);
</script>

<div class="metrics">
  {#each metrics as m}
    <div class="card">
      <span class="label">{m.label}</span>
      <strong class="value">{m.value}</strong>
    </div>
  {/each}
</div>

<style>
  .metrics {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    min-width: 0;
  }
  .label {
    display: block;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 4px;
  }
  .value {
    font-size: 1rem;
    overflow-wrap: anywhere;
  }
  @media (max-width: 1100px) {
    .metrics {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }
</style>
