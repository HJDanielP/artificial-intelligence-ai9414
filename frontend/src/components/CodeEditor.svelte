<script>
  import { onMount, onDestroy } from "svelte";
  import {
    store,
    loadStub,
    loadInitialCode,
    saveLocalDraft,
    clearLocalDraft,
    saveDraftToDisk,
    runSolver,
    backToPlayback,
    resetSolverOutput,
  } from "../lib/store.svelte.js";

  /** @type {{ oncollapse?: () => void }} */
  let { oncollapse } = $props();

  let host = $state(/** @type {HTMLDivElement|null} */ (null));
  let view = null;
  let ready = $state(false);
  let busy = $state(false);
  let saved = $state(false);
  let lastDemo = store.currentDemo;
  let fileInput = $state(/** @type {HTMLInputElement|null} */ (null));
  let saveTimer = /** @type {ReturnType<typeof setTimeout>|null} */ (null);
  let savedTimer = /** @type {ReturnType<typeof setTimeout>|null} */ (null);

  let output = $derived(store.solverOutput);

  // Resizable console height (persisted).
  const lsNum = (k, d) => {
    const v = Number(localStorage.getItem(k));
    return Number.isFinite(v) && v > 0 ? v : d;
  };
  let consoleHeight = $state(lsNum("ai9414.consoleH", 150));
  $effect(() => localStorage.setItem("ai9414.consoleH", String(consoleHeight)));

  function startConsoleResize(event) {
    event.preventDefault();
    const startY = event.clientY;
    const startH = consoleHeight;
    const dockH = host?.closest(".editor")?.getBoundingClientRect().height || 600;
    const move = (e) => {
      consoleHeight = Math.max(70, Math.min(dockH - 140, startH + (startY - e.clientY)));
    };
    const up = () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
      document.body.style.userSelect = "";
    };
    document.body.style.userSelect = "none";
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  }

  function setDoc(code) {
    if (view) view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: code } });
  }

  // Load saved draft (localStorage > on-disk workspace) or fall back to the stub.
  async function loadCode() {
    let code = "";
    try {
      code = await loadInitialCode();
    } catch (err) {
      code = `# Could not load starter code: ${err}`;
    }
    setDoc(code);
  }

  // Debounced autosave to localStorage so switching demos / refreshing never
  // loses the student's work.
  function scheduleAutosave() {
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      if (view) saveLocalDraft(view.state.doc.toString());
    }, 400);
  }

  onMount(async () => {
    const [{ EditorView, basicSetup }, { python }, { keymap }, { indentWithTab }] = await Promise.all([
      import("codemirror"),
      import("@codemirror/lang-python"),
      import("@codemirror/view"),
      import("@codemirror/commands"),
    ]);
    view = new EditorView({
      parent: host,
      doc: "",
      extensions: [
        basicSetup,
        python(),
        keymap.of([indentWithTab]),
        EditorView.updateListener.of((u) => {
          if (u.docChanged) scheduleAutosave();
        }),
      ],
    });
    await loadCode();
    ready = true;
  });

  $effect(() => {
    const demo = store.currentDemo;
    if (ready && view && demo !== lastDemo) {
      lastDemo = demo;
      if (saveTimer) clearTimeout(saveTimer); // don't save old code under new demo's key
      resetSolverOutput();
      loadCode();
    }
  });

  onDestroy(() => {
    if (saveTimer) clearTimeout(saveTimer);
    if (savedTimer) clearTimeout(savedTimer);
    view?.destroy();
  });

  async function onRun() {
    if (!view) return;
    busy = true;
    try {
      await runSolver(view.state.doc.toString());
    } finally {
      busy = false;
    }
  }

  // Reset = discard my edits and restore the pristine starter code.
  async function onReload() {
    if (saveTimer) clearTimeout(saveTimer);
    clearLocalDraft();
    resetSolverOutput();
    setDoc(await loadStub());
  }

  function flashSaved() {
    saved = true;
    if (savedTimer) clearTimeout(savedTimer);
    savedTimer = setTimeout(() => (saved = false), 1500);
  }

  async function onSave() {
    if (!view) return;
    try {
      await saveDraftToDisk(view.state.doc.toString());
      flashSaved();
    } catch {
      /* surfaced elsewhere; keep the toolbar quiet */
    }
  }

  function onExport() {
    if (!view) return;
    const blob = new Blob([view.state.doc.toString()], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `solve_${store.currentDemo}.py`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function onImportFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setDoc(text);
    saveLocalDraft(text);
    event.target.value = ""; // allow re-importing the same file
  }
</script>

<div class="editor">
  <div class="bar">
    <div class="title-row">
      <button class="icon-btn" onclick={() => oncollapse?.()} title="Hide editor" aria-label="Hide editor">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2.5" />
          <line x1="15" y1="3" x2="15" y2="21" />
        </svg>
      </button>
      <span class="title">Your solver</span>
    </div>
    <div class="actions">
      {#if store.mode === "live"}
        <button class="sm" onclick={backToPlayback} title="Show the reference example again">Example</button>
      {/if}
      <input
        type="file"
        accept=".py,text/x-python,text/plain"
        bind:this={fileInput}
        onchange={onImportFile}
        hidden
      />
      <button class="sm" onclick={() => fileInput?.click()} disabled={!ready} title="Load a .py file into the editor">Import</button>
      <button class="sm" onclick={onExport} disabled={!ready} title="Download your code as solve_{store.currentDemo}.py">Export</button>
      <button class="sm" onclick={onSave} disabled={!ready} title="Save to the workspace file on disk">
        {saved ? "Saved ✓" : "Save"}
      </button>
      <button class="sm" onclick={onReload} disabled={!ready} title="Discard your edits and restore the starter code">Reset</button>
      <button class="sm primary" onclick={onRun} disabled={!ready || busy}>
        {busy ? "Running…" : "Run ▶"}
      </button>
    </div>
  </div>

  <div class="host" bind:this={host}></div>
  {#if !ready}<div class="loading">Loading editor…</div>{/if}

  <div
    class="console-resize"
    role="separator"
    aria-orientation="horizontal"
    tabindex="-1"
    onmousedown={startConsoleResize}
    title="Drag to resize"
  ></div>
  <div
    class="console"
    class:error={output.status === "error"}
    class:ok={output.status === "ok"}
    class:running={output.status === "running"}
    style:height="{consoleHeight}px"
  >
    <div class="console-head">
      <span class="dot"></span>
      <span class="console-label">Python output</span>
      <span class="console-status">{output.status === "idle" ? "ready" : output.status}</span>
    </div>
    <div class="console-body">
      {#if output.stdout}<pre class="out">{output.stdout}</pre>{/if}
      {#if output.traceback}
        <pre class="err">{output.traceback}</pre>
      {:else if output.status === "error"}
        <pre class="err">{output.message}</pre>
      {:else if output.message}
        <div class="status-line">{output.message}</div>
      {/if}
      {#if output.status === "idle" && !output.stdout}
        <div class="hint">Click <strong>Run ▶</strong>. Your code runs in the local Python environment; <code>print()</code> output and tracebacks appear here, just like <code>python solve.py</code>.</div>
      {/if}
    </div>
  </div>
</div>

<style>
  .editor {
    display: flex;
    flex-direction: column;
    background: var(--surface);
    height: 100%;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
  }
  .bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    border-bottom: 1px solid var(--line);
    flex: 0 0 auto;
    flex-wrap: nowrap;
  }
  .title-row {
    display: flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
  }
  .title {
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .actions {
    display: flex;
    gap: 6px;
    flex: 0 0 auto;
  }
  .actions :global(button.sm) {
    height: 28px;
    padding: 0 9px;
    font-size: 0.82rem;
    white-space: nowrap;
  }
  .host {
    flex: 1 1 auto;
    min-height: 0;
    overflow: auto;
    font-size: 13px;
  }
  .host :global(.cm-editor) {
    height: 100%;
  }
  .host :global(.cm-scroller) {
    font-family: var(--mono);
  }
  .loading {
    padding: 12px;
    color: var(--muted);
  }

  /* Resizable terminal-style console wired to the local Python run. */
  .console-resize {
    position: relative;
    height: 9px;
    flex: 0 0 auto;
    cursor: row-resize;
    background: var(--surface);
    border-top: 1px solid var(--line);
  }
  /* Subtle centred grip rather than a full-width bar. */
  .console-resize::after {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 30px;
    height: 3px;
    border-radius: 999px;
    background: var(--line-strong);
    transition: background 120ms ease;
  }
  .console-resize:hover::after {
    background: var(--accent);
  }
  .console {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    background: #0b1020;
    color: #e2e8f0;
    min-height: 70px;
  }
  .console-head {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
    flex: 0 0 auto;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #64748b;
  }
  .console.ok .dot {
    background: #22c55e;
  }
  .console.error .dot {
    background: #ef4444;
  }
  .console.running .dot {
    background: #eab308;
  }
  .console-label {
    flex: 1 1 auto;
  }
  .console-status {
    color: #cbd5e1;
  }
  .console-body {
    flex: 1 1 auto;
    overflow: auto;
    padding: 8px 10px 10px;
    font-family: var(--mono);
    font-size: 0.8rem;
    line-height: 1.5;
  }
  .console-body pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }
  .out {
    color: #cbd5e1;
  }
  .err {
    color: #fca5a5;
    margin-top: 6px;
  }
  .status-line {
    margin-top: 6px;
    color: #86efac;
  }
  .hint {
    color: #94a3b8;
    font-family: var(--font);
    line-height: 1.55;
  }
  .hint :global(code) {
    background: rgba(255, 255, 255, 0.1);
    padding: 0 4px;
    border-radius: 4px;
  }
</style>
