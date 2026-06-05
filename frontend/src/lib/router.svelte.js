/** Minimal hash router: `#/graph-bfs` -> "graph-bfs". Zero dependencies. */

function parseHash() {
  const raw = window.location.hash.replace(/^#\/?/, "").trim();
  return raw || null;
}

export const route = $state({ demo: parseHash() });

window.addEventListener("hashchange", () => {
  route.demo = parseHash();
});

/** @param {string} demo */
export function navigate(demo) {
  window.location.hash = `/${demo}`;
}
