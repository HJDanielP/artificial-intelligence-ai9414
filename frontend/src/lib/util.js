/** Small shared helpers (snapshot building, formatting, edge ids). */

/** @param {any} value */
export function clone(value) {
  return value === undefined ? value : structuredClone(value);
}

/**
 * True when `value` is a non-empty array whose every item is an object carrying
 * a `tree_id`. Such arrays (the search tree's `tree.nodes`) are delta-encoded by
 * the backend and must be merged by key rather than replaced wholesale.
 * @param {any} value
 */
function isKeyedNodeArray(value) {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    value.every((item) => item && typeof item === "object" && "tree_id" in item)
  );
}

/**
 * Merge a delta of keyed nodes into a base array: existing `tree_id`s are
 * replaced in place, new ones are appended. Search trees only grow, so nodes are
 * never removed.
 * @param {Array<{tree_id: string}>} base
 * @param {Array<{tree_id: string}>} patch
 */
function mergeKeyedById(base, patch) {
  const indexOf = new Map(base.map((item, i) => [item.tree_id, i]));
  const result = base.slice();
  for (const item of patch) {
    const at = indexOf.get(item.tree_id);
    if (at === undefined) {
      indexOf.set(item.tree_id, result.length);
      result.push(clone(item));
    } else {
      result[at] = clone(item);
    }
  }
  return result;
}

/**
 * Deep-merge `patch` into `base` in place (objects merge, keyed node arrays
 * merge by tree_id, everything else replaces). Mirrors the backend
 * `_deep_merge` used to apply step patches.
 * @param {Record<string, any>} base
 * @param {Record<string, any>} patch
 */
export function deepMerge(base, patch) {
  for (const [key, value] of Object.entries(patch || {})) {
    if (
      value &&
      typeof value === "object" &&
      !Array.isArray(value) &&
      base[key] &&
      typeof base[key] === "object" &&
      !Array.isArray(base[key])
    ) {
      deepMerge(base[key], value);
    } else if (isKeyedNodeArray(value) && isKeyedNodeArray(base[key])) {
      base[key] = mergeKeyedById(base[key], value);
    } else {
      base[key] = clone(value);
    }
  }
  return base;
}

/**
 * Expand a TraceBundle into one full state snapshot per step (index 0 is the
 * initial state). Mirrors the former `buildSnapshots` in app.js.
 * @param {{initial_state?: object, steps?: Array<{state_patch?: object}>}} trace
 */
export function buildSnapshots(trace) {
  const initial = clone(trace?.initial_state || {});
  const snapshots = [initial];
  let current = clone(initial);
  for (const step of trace?.steps || []) {
    current = deepMerge(clone(current), step.state_patch || {});
    snapshots.push(clone(current));
  }
  return snapshots;
}

/** @param {number|null|undefined} value @param {number} digits */
export function formatNumber(value, digits = 3) {
  return value === null || value === undefined ? "none" : Number(value).toFixed(digits);
}

/** @param {string} u @param {string} v */
export function edgeId(u, v) {
  return [u, v].sort().join("--");
}

/** @param {string[]} path */
export function pathToEdgeIds(path) {
  const ids = new Set();
  for (let i = 0; i < (path?.length || 0) - 1; i += 1) {
    ids.add(edgeId(path[i], path[i + 1]));
  }
  return ids;
}
