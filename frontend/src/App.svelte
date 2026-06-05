<script>
  import { onMount } from "svelte";
  import { store, loadDemos, openDemo, loadExample, currentSnapshot } from "./lib/store.svelte.js";
  import { route, navigate } from "./lib/router.svelte.js";
  import { demoConfig } from "./demos/registry.js";
  import Sidebar from "./components/Sidebar.svelte";
  import TransportBar from "./components/TransportBar.svelte";
  import ExplanationPanel from "./components/ExplanationPanel.svelte";
  import MetricsGrid from "./components/MetricsGrid.svelte";
  import CodeEditor from "./components/CodeEditor.svelte";
  import { panelComponent } from "./visualizers/panels.js";

  let cfg = $derived(store.currentDemo ? demoConfig(store.currentDemo) : { supported: false });
  let snapshot = $derived(currentSnapshot());
  let LeftPanel = $derived(panelComponent(cfg.left));
  let RightPanel = $derived(panelComponent(cfg.right));

  // --- collapsible / resizable layout (persisted) ---
  const lsBool = (k, d) => {
    const v = localStorage.getItem(k);
    return v === null ? d : v === "1";
  };
  const lsNum = (k, d) => {
    const v = Number(localStorage.getItem(k));
    return Number.isFinite(v) && v > 0 ? v : d;
  };

  let sidebarOpen = $state(lsBool("ai9414.sidebar", true));
  let editorOpen = $state(lsBool("ai9414.editor", true));
  let editorWidth = $state(lsNum("ai9414.editorW", 460));
  let resizing = $state(false);

  $effect(() => localStorage.setItem("ai9414.sidebar", sidebarOpen ? "1" : "0"));
  $effect(() => localStorage.setItem("ai9414.editor", editorOpen ? "1" : "0"));
  $effect(() => localStorage.setItem("ai9414.editorW", String(editorWidth)));

  function startResize(event) {
    event.preventDefault();
    const startX = event.clientX;
    const startW = editorWidth;
    resizing = true;
    const move = (e) => {
      editorWidth = Math.max(320, Math.min(820, startW + (startX - e.clientX)));
    };
    const up = () => {
      resizing = false;
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
      document.body.style.userSelect = "";
    };
    document.body.style.userSelect = "none";
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  }

  onMount(async () => {
    await loadDemos();
    if (!route.demo) {
      const first = store.demos.find((d) => demoConfig(d.name).supported) || store.demos[0];
      if (first) navigate(first.name);
    }
  });

  $effect(() => {
    const demo = route.demo;
    if (demo && demo !== store.currentDemo) openDemo(demo);
  });
</script>

<div class="shell">
  {#if sidebarOpen}
    <Sidebar oncollapse={() => (sidebarOpen = false)} />
  {:else}
    <button class="rail left" onclick={() => (sidebarOpen = true)} title="Show demos" aria-label="Show demos">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2.5" />
        <line x1="9" y1="3" x2="9" y2="21" />
      </svg>
    </button>
  {/if}

  <main class="center" class:dim={store.loading}>
    {#if !store.currentDemo}
      <div class="placeholder">Select a demo from the sidebar.</div>
    {:else if !cfg.supported}
      <div class="placeholder">
        <h2>{store.demos.find((d) => d.name === store.currentDemo)?.title || store.currentDemo}</h2>
        <p>This demo's new interface is coming soon.</p>
      </div>
    {:else}
      <header class="header">
        <div class="title-row">
          <div>
            <h1>{store.manifest?.app_title || store.currentDemo}</h1>
            <p class="subtitle">{snapshot?.example_subtitle || ""}</p>
          </div>
        </div>
        <div class="header-controls">
          <span class="pill" class:good={store.mode === "live"}>{store.mode}</span>
          {#if store.examples.length}
            <label class="example">
              example
              <select value={store.exampleName} onchange={(e) => loadExample(e.currentTarget.value)}>
                {#each store.examples as ex}
                  <option value={ex}>{ex}</option>
                {/each}
              </select>
            </label>
          {/if}
          {#if cfg.hasEditor && !editorOpen}
            <button class="icon-btn" onclick={() => (editorOpen = true)} title="Show editor" aria-label="Show editor">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2.5" />
                <line x1="15" y1="3" x2="15" y2="21" />
              </svg>
            </button>
          {/if}
        </div>
      </header>

      {#if store.error}
        <div class="banner error">{store.error}</div>
      {:else if store.message}
        <div class="banner">{store.message}</div>
      {/if}

      <div class="panels">
        <section class="panel">
          <div class="panel-title">{cfg.leftTitle || "Search tree"}</div>
          {#if LeftPanel}
            <LeftPanel data={snapshot} {cfg} />
          {/if}
        </section>
        <section class="panel">
          <div class="panel-title">{cfg.rightTitle || "Problem"}</div>
          {#if RightPanel}
            <RightPanel data={snapshot} {cfg} />
          {/if}
        </section>
      </div>

      <TransportBar />
      {#if cfg.showMetrics}
        <MetricsGrid />
      {/if}
      <ExplanationPanel />
    {/if}
  </main>

  {#if cfg.hasEditor}
    <aside class="editor-dock" class:collapsed={!editorOpen} style:width={editorOpen ? `${editorWidth}px` : "0"}>
      {#if editorOpen}
        <div
          class="resize-handle"
          class:resizing
          role="separator"
          aria-orientation="vertical"
          tabindex="-1"
          title="Drag to resize"
          onmousedown={startResize}
        ></div>
      {/if}
      <CodeEditor oncollapse={() => (editorOpen = false)} />
    </aside>
  {/if}
</div>

<style>
  .shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }
  .center {
    flex: 1 1 auto;
    min-width: 0;
    overflow-y: auto;
    padding: 16px 20px 28px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    transition: opacity 120ms ease;
  }
  .center.dim {
    opacity: 0.55;
  }
  .rail {
    flex: 0 0 auto;
    width: 44px;
    height: 100vh;
    border: 0;
    border-right: 1px solid var(--line);
    background: var(--surface);
    border-radius: 0;
    color: var(--muted);
    align-items: flex-start;
    padding: 16px 0 0;
  }
  .rail:hover {
    background: var(--surface-2);
  }
  .placeholder {
    margin: auto;
    text-align: center;
    color: var(--muted);
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }
  .title-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  h1 {
    margin: 0 0 4px;
    font-size: 1.5rem;
  }
  .subtitle {
    margin: 0;
    color: var(--muted);
  }
  .header-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .example {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--muted);
    font-size: 0.85rem;
  }
  .banner {
    padding: 10px 14px;
    border-radius: var(--radius-sm);
    background: var(--accent-soft);
    border: 1px solid var(--line-strong);
  }
  .banner.error {
    background: color-mix(in srgb, var(--bad) 10%, var(--surface));
    border-color: var(--bad);
    color: var(--bad);
  }
  .panels {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
  .panel {
    padding: 12px;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  .panel-title {
    margin-bottom: 10px;
  }
  .editor-dock {
    position: relative;
    flex: 0 0 auto;
    height: 100vh;
    background: var(--bg);
    border-left: 1px solid var(--line);
    padding: 14px 14px 14px 16px;
    overflow: hidden;
  }
  .editor-dock.collapsed {
    padding: 0;
    border-left: 0;
  }
  .editor-dock.collapsed :global(.editor) {
    display: none;
  }
  /* Width drag handle: a thin line on the dock's left edge that turns blue on
     hover and while dragging. */
  .resize-handle {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 9px;
    cursor: col-resize;
    z-index: 2;
  }
  .resize-handle::after {
    content: "";
    position: absolute;
    left: 3px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: transparent;
    transition: background 120ms ease;
  }
  .resize-handle:hover::after,
  .resize-handle.resizing::after {
    background: var(--accent);
  }
  @media (max-width: 1100px) {
    .panels {
      grid-template-columns: 1fr;
    }
  }
</style>
