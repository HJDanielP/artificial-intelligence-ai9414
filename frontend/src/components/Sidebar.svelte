<script>
  import { store } from "../lib/store.svelte.js";
  import { navigate } from "../lib/router.svelte.js";
  import { demoConfig } from "../demos/registry.js";

  /** @type {{ oncollapse?: () => void }} */
  let { oncollapse } = $props();

  let groups = $derived(groupDemos(store.demos));

  function groupDemos(demos) {
    /** @type {Record<string, any[]>} */
    const byGroup = {};
    for (const demo of demos) {
      (byGroup[demo.group] ||= []).push(demo);
    }
    return Object.entries(byGroup);
  }
</script>

<nav class="sidebar">
  <div class="brand-row">
    <button class="icon-btn" onclick={() => oncollapse?.()} title="Hide sidebar" aria-label="Hide sidebar">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2.5" />
        <line x1="9" y1="3" x2="9" y2="21" />
      </svg>
    </button>
    <div class="brand">ai9414</div>
  </div>
  {#each groups as [group, demos]}
    <div class="group">
      <div class="group-label">{group}</div>
      {#each demos as demo}
        <button
          class="item"
          class:active={store.currentDemo === demo.name}
          class:disabled={!demoConfig(demo.name).supported}
          onclick={() => navigate(demo.name)}
          title={demo.description}
        >
          {demo.title}
          {#if !demoConfig(demo.name).supported}<span class="soon">soon</span>{/if}
        </button>
      {/each}
    </div>
  {/each}
</nav>

<style>
  .sidebar {
    width: 230px;
    flex: 0 0 230px;
    height: 100%;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--line);
    padding: 14px 12px;
  }
  .brand-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 2px 2px 14px;
  }
  .brand {
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: 0.01em;
  }
  .group {
    margin-bottom: 14px;
  }
  .group-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    padding: 4px 8px;
  }
  .item {
    width: 100%;
    text-align: left;
    border: 0;
    background: transparent;
    border-radius: var(--radius-sm);
    padding: 7px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
  }
  .item:hover {
    background: var(--surface-2);
  }
  .item.active {
    background: var(--accent-soft);
    color: var(--accent-strong);
    font-weight: 600;
  }
  .item.disabled {
    color: var(--muted);
  }
  .soon {
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 1px 6px;
  }
</style>
