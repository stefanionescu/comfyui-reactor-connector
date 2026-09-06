export type Pointer = { x: number; y: number; active: boolean };

export function bindDrag(
  image: HTMLImageElement,
  signal: AbortSignal,
  send: (pointer: Pointer) => void,
): () => void {
  let pointer: Pointer = { x: 0.5, y: 0.5, active: false };
  let captured: number | undefined;
  image.tabIndex = 0;
  image.draggable = false;
  image.style.touchAction = "none";
  image.setAttribute(
    "aria-label",
    "Drag on the output to move the subject. Use arrow keys to position the pointer, Space to hold it, and Escape to release it.",
  );
  const release = () => {
    const wasActive = pointer.active;
    pointer = { ...pointer, active: false };
    const previousCapture = captured;
    captured = undefined;
    if (wasActive) send(pointer);
    if (previousCapture !== undefined && image.hasPointerCapture(previousCapture))
      image.releasePointerCapture(previousCapture);
  };
  const position = (event: PointerEvent, active: boolean) => {
    const rect = image.getBoundingClientRect();
    pointer = {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
      active,
    };
    send(pointer);
  };
  image.addEventListener(
    "pointerdown",
    (event) => {
      if (event.button !== 0 || captured !== undefined) return;
      captured = event.pointerId;
      image.setPointerCapture(captured);
      image.focus();
      position(event, true);
    },
    { signal },
  );
  image.addEventListener(
    "pointermove",
    (event) => {
      if (captured === event.pointerId) position(event, true);
    },
    { signal },
  );
  for (const name of ["pointerup", "pointercancel", "lostpointercapture"])
    image.addEventListener(name, release, { signal });
  image.addEventListener(
    "keydown",
    (event) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " ", "Escape"].includes(event.key))
        return;
      event.preventDefault();
      event.stopPropagation();
      if (event.key === "Escape") {
        release();
        image.blur();
        return;
      }
      pointer = {
        x: Math.max(
          0,
          Math.min(
            1,
            pointer.x + (event.key === "ArrowRight" ? 0.03 : event.key === "ArrowLeft" ? -0.03 : 0),
          ),
        ),
        y: Math.max(
          0,
          Math.min(
            1,
            pointer.y + (event.key === "ArrowDown" ? 0.03 : event.key === "ArrowUp" ? -0.03 : 0),
          ),
        ),
        active: event.key === " " || pointer.active,
      };
      send(pointer);
    },
    { signal },
  );
  image.addEventListener(
    "keyup",
    (event) => {
      if (event.key === " ") {
        event.preventDefault();
        event.stopPropagation();
        release();
      }
    },
    { signal },
  );
  image.addEventListener("blur", release, { signal });
  window.addEventListener("blur", release, { signal });
  document.addEventListener(
    "visibilitychange",
    () => {
      if (document.hidden) release();
    },
    { signal },
  );
  signal.addEventListener("abort", release, { once: true });
  return release;
}
