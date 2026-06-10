/** Typed-ish client for the unified ai9414 API (`/api/{demo}/...`). */

/**
 * @param {string} url
 * @param {RequestInit} [options]
 */
async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error(`Request to ${url} failed (${response.status}).`);
  }
  if (!response.ok || payload.ok === false) {
    const error = payload?.error || payload?.detail?.error;
    const err = new Error(error?.message || "Request failed");
    // Attach structured details (e.g. solver stdout) for the caller to surface.
    err.details = error?.details || {};
    err.code = error?.code;
    throw err;
  }
  return payload;
}

/** @returns {Promise<{demos: Array<{name:string,title:string,description:string,group:string}>}>} */
export function getDemos() {
  return requestJson("/api/demos");
}

/** @param {string} demo */
export function getManifest(demo) {
  return requestJson(`/api/${demo}/manifest`);
}

/** @param {string} demo */
export function getState(demo) {
  return requestJson(`/api/${demo}/state`);
}

/** @param {string} demo */
export function getTrace(demo) {
  return requestJson(`/api/${demo}/trace`);
}

/** @param {string} demo */
export function getExamples(demo) {
  return requestJson(`/api/${demo}/examples`);
}

/** @param {string} demo */
export function getStub(demo) {
  return requestJson(`/api/${demo}/stub`);
}

/** Read the on-disk solver draft saved in the workspace. @param {string} demo */
export function getDraft(demo) {
  return requestJson(`/api/${demo}/draft`);
}

/**
 * Persist the solver draft to the on-disk workspace (solve_<demo>.py).
 * @param {string} demo
 * @param {string} code
 */
export function postDraft(demo, code) {
  return requestJson(`/api/${demo}/draft`, {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

/**
 * @param {string} demo
 * @param {string} action
 * @param {object} [payload]
 */
export function postAction(demo, action, payload = {}) {
  return requestJson(`/api/${demo}/action`, {
    method: "POST",
    body: JSON.stringify({ action, payload }),
  });
}

/**
 * Run student code in-process and get a replayable trace back.
 * @param {string} demo
 * @param {object} body  e.g. { code, graph } — keys depend on the demo
 */
export function postSolve(demo, body) {
  return requestJson(`/api/${demo}/solve`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
