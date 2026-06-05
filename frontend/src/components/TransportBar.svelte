<script>
  import {
    store,
    maxStep,
    next,
    prev,
    reset,
    gotoStep,
    togglePlay,
    setSpeed,
  } from "../lib/store.svelte.js";

  let max = $derived(maxStep());
</script>

<div class="panel transport">
  <div class="buttons">
    <button onclick={prev} disabled={store.stepIndex === 0} title="Previous step">◄</button>
    <button class="primary" onclick={togglePlay} disabled={max === 0}>
      {store.playing ? "Pause" : "Play"}
    </button>
    <button onclick={next} disabled={store.stepIndex >= max} title="Next step">►</button>
    <button onclick={reset} disabled={store.stepIndex === 0}>Reset</button>
  </div>

  <input
    class="scrubber"
    type="range"
    min="0"
    max={max}
    value={store.stepIndex}
    oninput={(e) => gotoStep(Number(e.currentTarget.value))}
  />
  <div class="readout">{store.stepIndex} / {max}</div>

  <label class="speed">
    speed
    <select value={store.playbackSpeed} onchange={(e) => setSpeed(Number(e.currentTarget.value))}>
      <option value={0.75}>0.75×</option>
      <option value={1}>1.0×</option>
      <option value={1.5}>1.5×</option>
      <option value={2}>2.0×</option>
      <option value={5}>5.0×</option>
    </select>
  </label>
</div>

<style>
  .transport {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 14px;
  }
  .buttons {
    display: flex;
    gap: 6px;
    flex: 0 0 auto;
  }
  .scrubber {
    flex: 1 1 auto;
  }
  .readout {
    flex: 0 0 auto;
    font-variant-numeric: tabular-nums;
    color: var(--muted);
    min-width: 60px;
    text-align: right;
  }
  .speed {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--muted);
    font-size: 0.85rem;
  }
</style>
