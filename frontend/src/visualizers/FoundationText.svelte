<script>
  /** @type {{ data: any, cfg?: any }} */
  let { data } = $props();
  let fm = $derived(data?.foundation_models || null);
</script>

{#if fm}
  <div class="wrap">
    <div class="meta">
      <span class="pill accent">{fm.mode_label}</span>
      <span class="status">{fm.status}</span>
    </div>
    <div class="stream">
      {#each fm.overlay_segments || [] as seg}
        {#if seg.kind === "whitespace"}
          <span class="ws">{seg.text === " " ? "·" : seg.text}</span>
        {:else}
          <span class="tok">{seg.text}</span>
        {/if}
      {/each}
    </div>
    <p class="hint">Each chip is one token. Whitespace is shown as ·.</p>
  </div>
{/if}

<style>
  .wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-height: 300px;
  }
  .meta {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .status {
    color: var(--muted);
    font-size: 0.85rem;
  }
  .stream {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 2px;
    align-items: center;
    line-height: 2;
    font-family: var(--mono);
    font-size: 1rem;
  }
  .tok {
    background: var(--accent-soft);
    border: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
    color: var(--accent-strong);
    border-radius: 6px;
    padding: 2px 6px;
    font-weight: 700;
  }
  .ws {
    color: var(--line-strong);
    padding: 0 1px;
  }
  .hint {
    margin: 0;
    color: var(--muted);
    font-size: 0.8rem;
  }
</style>
