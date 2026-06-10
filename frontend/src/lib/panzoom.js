/**
 * Reusable pan/zoom *camera* Svelte action for the SVG visualizers.
 *
 * Attach to an `<svg>` (with a fixed viewBox acting as the camera window) whose
 * zoomable content lives inside a child marked `data-zoom-layer`. Wheel zooms
 * around the cursor and drag pans, both counting as manual interaction. The
 * component can also drive the camera programmatically:
 *
 *   - `focusOn(wx, wy, scale?)` — centre a content point (for follow-the-frontier)
 *   - `fitInto(w, h)`          — frame the whole content box (the "Fit" button)
 *   - `zoomIn/zoomOut/reset`   — manual controls
 *
 * `onUserInteract` fires on manual wheel/drag so the component can pause an
 * auto-follow mode. No external dependency.
 *
 * @param {SVGSVGElement} svg
 * @param {{
 *   min?: number, max?: number,
 *   onInit?: (api: any) => void,
 *   onUserInteract?: () => void,
 * }} [options]
 */
export function panzoom(svg, options = {}) {
  const min = options.min ?? 0.05;
  const max = options.max ?? 6;
  let k = 1;
  let tx = 0;
  let ty = 0;

  const clamp = (v) => Math.min(max, Math.max(min, v));
  const layer = () => svg.querySelector("[data-zoom-layer]");
  const box = () => svg.viewBox.baseVal;

  function apply(animate) {
    const l = layer();
    if (!l) return;
    l.style.transition = animate ? "transform 240ms ease-out" : "none";
    l.setAttribute("transform", `translate(${tx} ${ty}) scale(${k})`);
  }

  // Map client (screen) coords into the SVG user space the transform lives in.
  function toView(clientX, clientY) {
    const ctm = svg.getScreenCTM();
    if (!ctm) return { x: 0, y: 0 };
    const p = new DOMPoint(clientX, clientY).matrixTransform(ctm.inverse());
    return { x: p.x, y: p.y };
  }

  function zoomAt(next, clientX, clientY) {
    next = clamp(next);
    const p = toView(clientX, clientY);
    const wx = (p.x - tx) / k;
    const wy = (p.y - ty) / k;
    k = next;
    tx = p.x - k * wx;
    ty = p.y - k * wy;
    apply(false);
  }

  function centre() {
    const r = svg.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }

  function onWheel(event) {
    event.preventDefault();
    options.onUserInteract?.();
    zoomAt(k * Math.exp(-event.deltaY * 0.0015), event.clientX, event.clientY);
  }

  let dragging = false;
  let last = { x: 0, y: 0 };

  function onPointerDown(event) {
    if (event.button !== 0) return;
    options.onUserInteract?.();
    dragging = true;
    last = toView(event.clientX, event.clientY);
    svg.setPointerCapture?.(event.pointerId);
    svg.classList.add("is-grabbing");
  }

  function onPointerMove(event) {
    if (!dragging) return;
    const cur = toView(event.clientX, event.clientY);
    tx += cur.x - last.x;
    ty += cur.y - last.y;
    last = cur;
    apply(false);
  }

  function onPointerUp(event) {
    dragging = false;
    svg.releasePointerCapture?.(event.pointerId);
    svg.classList.remove("is-grabbing");
  }

  // --- Programmatic camera ---------------------------------------------------

  /** Centre content point (wx,wy); optionally set the zoom. */
  function focusOn(wx, wy, scale, animate = true) {
    const vb = box();
    if (scale != null) k = clamp(scale);
    tx = vb.width / 2 - k * wx;
    ty = vb.height / 2 - k * wy;
    apply(animate);
  }

  /** Frame the whole content box (0,0,w,h) with a little margin. */
  function fitInto(w, h, animate = true) {
    const vb = box();
    k = clamp(Math.min(vb.width / w, vb.height / h) * 0.92);
    tx = (vb.width - k * w) / 2;
    ty = (vb.height - k * h) / 2;
    apply(animate);
  }

  function reset() {
    k = 1;
    tx = 0;
    ty = 0;
    apply(true);
  }

  svg.addEventListener("wheel", onWheel, { passive: false });
  svg.addEventListener("pointerdown", onPointerDown);
  svg.addEventListener("pointermove", onPointerMove);
  svg.addEventListener("pointerup", onPointerUp);
  svg.addEventListener("pointerleave", onPointerUp);

  options.onInit?.({
    zoomIn: () => {
      options.onUserInteract?.();
      const c = centre();
      zoomAt(k * 1.3, c.x, c.y);
    },
    zoomOut: () => {
      options.onUserInteract?.();
      const c = centre();
      zoomAt(k / 1.3, c.x, c.y);
    },
    focusOn,
    fitInto,
    reset,
    getScale: () => k,
  });

  return {
    destroy() {
      svg.removeEventListener("wheel", onWheel);
      svg.removeEventListener("pointerdown", onPointerDown);
      svg.removeEventListener("pointermove", onPointerMove);
      svg.removeEventListener("pointerup", onPointerUp);
      svg.removeEventListener("pointerleave", onPointerUp);
    },
  };
}
