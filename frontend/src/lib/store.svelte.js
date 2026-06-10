/** Central application state (Svelte 5 runes) and the actions that mutate it. */

import * as api from "./api.js";
import { clone, deepMerge } from "./util.js";
import { demoConfig } from "../demos/registry.js";

export const store = $state({
  /** @type {Array<{name:string,title:string,description:string,group:string}>} */
  demos: [],
  /** @type {string|null} */
  currentDemo: null,
  manifest: null,
  session: null,
  /** Bumped whenever the trace changes, so snapshot derivations re-run. */
  traceVersion: 0,
  stepIndex: 0,
  /** @type {string[]} */
  examples: [],
  /** @type {string|null} */
  exampleName: null,
  playbackSpeed: 1,
  /** "playback" (reference trace) | "live" (student trace) */
  mode: "playback",
  message: "",
  error: "",
  loading: false,
  playing: false,
  /** Solver console output (shown beneath the editor, not as a top banner). */
  solverOutput: { status: "idle", message: "", stdout: "", traceback: "" },
});

let playTimer = /** @type {ReturnType<typeof setInterval>|null} */ (null);

// The trace is held here as a plain (non-reactive) object. Svelte 5 deeply
// proxies anything assigned to `$state`, and structuredClone cannot clone
// those proxies — so we keep the raw trace out of the store and use
// `store.traceVersion` as the reactive signal instead.
let _rawTrace = /** @type {any} */ (null);

// Incremental snapshot cache. Building one full snapshot per step up front is
// O(n^2) in clones and freezes large traces (branch-and-bound has ~2000
// steps), so we fold patches lazily and remember the last computed position.
let _snap = { version: -1, idx: 0, state: {} };

export function maxStep() {
  // Touch traceVersion so `$derived(maxStep())` re-runs when the trace changes
  // (the layout stays mounted across demo switches and live runs).
  void store.traceVersion;
  return _rawTrace?.steps?.length || 0;
}

/** Snapshot after applying steps[0 .. idx-1] (idx 0 = initial state). */
function snapshotAt(idx) {
  const steps = _rawTrace?.steps || [];
  const target = Math.max(0, Math.min(idx, steps.length));
  if (_snap.version !== store.traceVersion || target < _snap.idx) {
    _snap = { version: store.traceVersion, idx: 0, state: clone(_rawTrace?.initial_state || {}) };
  }
  for (let i = _snap.idx; i < target; i += 1) {
    deepMerge(_snap.state, steps[i].state_patch || {});
  }
  _snap.idx = target;
  return clone(_snap.state);
}

export function currentSnapshot() {
  // Touch traceVersion so this re-runs when the trace changes.
  void store.traceVersion;
  return snapshotAt(store.stepIndex);
}

export function currentStep() {
  void store.traceVersion;
  const steps = _rawTrace?.steps || [];
  return store.stepIndex > 0 ? steps[store.stepIndex - 1] || {} : {};
}

export async function loadDemos() {
  const payload = await api.getDemos();
  store.demos = payload.demos;
}

/** @param {string} demo */
export async function openDemo(demo) {
  stopPlay();
  store.loading = true;
  store.error = "";
  store.message = "";
  store.mode = "playback";
  store.currentDemo = demo;
  store.solverOutput = { status: "idle", message: "", stdout: "" };
  // Clear the trace immediately so the new demo's panels don't flash the
  // previous demo's data while the new trace loads.
  _rawTrace = null;
  store.traceVersion += 1;
  store.stepIndex = 0;
  try {
    const cfg = demoConfig(demo);
    if (!cfg.supported) {
      store.manifest = null;
      _rawTrace = null;
      store.traceVersion += 1;
      return;
    }
    const [manifest, session, trace, examples] = await Promise.all([
      api.getManifest(demo),
      api.getState(demo),
      api.getTrace(demo),
      api.getExamples(demo),
    ]);
    store.manifest = manifest;
    store.session = session;
    store.examples = examples.examples || [];
    store.exampleName = session.example_name || null;
    store.playbackSpeed = Number(session.options?.playback_speed || 1);
    _setTrace(trace);
  } catch (err) {
    store.error = err instanceof Error ? err.message : String(err);
  } finally {
    store.loading = false;
  }
}

/** @param {object} trace */
function _setTrace(trace) {
  _rawTrace = trace;
  store.traceVersion += 1;
  store.stepIndex = 0;
}

/** @param {string} name */
export async function loadExample(name) {
  stopPlay();
  store.message = "";
  store.mode = "playback";
  try {
    await api.postAction(store.currentDemo, "load_example", { name });
    const [session, trace] = await Promise.all([
      api.getState(store.currentDemo),
      api.getTrace(store.currentDemo),
    ]);
    store.session = session;
    store.exampleName = name;
    _setTrace(trace);
  } catch (err) {
    store.error = err instanceof Error ? err.message : String(err);
  }
}

/** @param {number} index */
export function gotoStep(index) {
  store.stepIndex = Math.max(0, Math.min(index, maxStep()));
}

export function next() {
  gotoStep(store.stepIndex + 1);
}

export function prev() {
  gotoStep(store.stepIndex - 1);
}

export function reset() {
  stopPlay();
  store.stepIndex = 0;
}

function _intervalMs() {
  return Math.max(120, 900 / (store.playbackSpeed || 1));
}

export function play() {
  stopPlay();
  if (store.stepIndex >= maxStep()) store.stepIndex = 0;
  store.playing = true;
  playTimer = setInterval(() => {
    if (store.stepIndex >= maxStep()) {
      stopPlay();
      return;
    }
    store.stepIndex += 1;
  }, _intervalMs());
}

export function stopPlay() {
  if (playTimer) clearInterval(playTimer);
  playTimer = null;
  store.playing = false;
}

export function togglePlay() {
  store.playing ? stopPlay() : play();
}

/** @param {number} speed */
export function setSpeed(speed) {
  store.playbackSpeed = speed;
  if (store.playing) play();
}

/** Fetch the starter code for the embedded editor. */
export async function loadStub() {
  const payload = await api.getStub(store.currentDemo);
  return payload.code || "";
}

// --- Solver draft persistence -----------------------------------------------
// Three layers: localStorage autosaves every keystroke (instant refresh/switch
// safety), the on-disk workspace holds a real solve_<demo>.py (submittable,
// loadable via `--solver`), and the stub is the fallback for a fresh demo.

/** @param {string} demo */
function draftKey(demo) {
  return `ai9414.draft.${demo}`;
}

/** Read the per-demo localStorage draft, or null if none. */
function readLocalDraft(demo) {
  try {
    return localStorage.getItem(draftKey(demo));
  } catch {
    return null;
  }
}

/** Autosave the current editor contents for the active demo. @param {string} code */
export function saveLocalDraft(code) {
  if (!store.currentDemo) return;
  try {
    localStorage.setItem(draftKey(store.currentDemo), code);
  } catch {
    /* localStorage may be unavailable (private mode); autosave is best-effort. */
  }
}

/** Drop the saved draft so Reset restores the pristine stub. */
export function clearLocalDraft() {
  if (!store.currentDemo) return;
  try {
    localStorage.removeItem(draftKey(store.currentDemo));
  } catch {
    /* best-effort */
  }
}

/**
 * Resolve the code to show when the editor (re)loads a demo.
 * Precedence: in-browser autosave > on-disk workspace draft > starter stub.
 */
export async function loadInitialCode() {
  const demo = store.currentDemo;
  const local = readLocalDraft(demo);
  if (local != null) return local;
  try {
    const payload = await api.getDraft(demo);
    if (payload.code) return payload.code;
  } catch {
    /* no workspace draft yet — fall through to the stub. */
  }
  return loadStub();
}

/** Write the current editor contents to the on-disk workspace. @param {string} code */
export async function saveDraftToDisk(code) {
  if (!store.currentDemo) return;
  await api.postDraft(store.currentDemo, code);
}

/**
 * Run student code in-process and replay the returned trace.
 * @param {string} code
 */
export async function runSolver(code) {
  stopPlay();
  store.message = "";
  store.error = "";
  store.solverOutput = { status: "running", message: "Running your solver…", stdout: "", traceback: "" };
  const cfg = demoConfig(store.currentDemo);
  const problemKey = cfg.problemKey || "problem";
  const problem = store.session?.data?.[problemKey] ?? store.session?.data?.graph;
  const body = { code, [problemKey]: problem };
  if (store.session?.data?.options) body.options = store.session.data.options;
  try {
    const payload = await api.postSolve(store.currentDemo, body);
    _setTrace(payload.trace);
    store.mode = "live";
    // A run that reaches the solver is worth persisting to the real file too.
    saveDraftToDisk(code).catch(() => {});
    const steps = payload.trace?.summary?.step_count ?? 0;
    store.solverOutput = {
      status: "ok",
      message: `→ ${steps} step${steps === 1 ? "" : "s"}, replaying below`,
      stdout: payload.stdout || "",
      traceback: "",
    };
  } catch (err) {
    store.solverOutput = {
      status: "error",
      message: err?.message || String(err),
      stdout: err?.details?.stdout || "",
      traceback: err?.details?.traceback || "",
    };
  }
}

export function resetSolverOutput() {
  store.solverOutput = { status: "idle", message: "", stdout: "", traceback: "" };
}

/** Switch back to the reference (playback) trace. */
export async function backToPlayback() {
  stopPlay();
  store.mode = "playback";
  store.error = "";
  store.message = "";
  const trace = await api.getTrace(store.currentDemo);
  _setTrace(trace);
}
