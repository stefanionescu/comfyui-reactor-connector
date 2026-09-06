export function cameraAxes(keys: ReadonlySet<string>, world2: boolean): Record<string, string> {
  const direction = (negative: string, positive: string, first: string, second: string) =>
    keys.has(negative) === keys.has(positive) ? "idle" : keys.has(negative) ? first : second;
  const forward = direction("w", "s", "forward", "back");
  const lateral = direction("a", "d", "strafe_left", "strafe_right");
  return {
    ...(world2
      ? { move_longitudinal: forward, move_lateral: lateral }
      : { movement: forward !== "idle" ? forward : lateral }),
    look_horizontal: direction("ArrowLeft", "ArrowRight", "left", "right"),
    look_vertical: direction("ArrowUp", "ArrowDown", "up", "down"),
  };
}

export const cameraKeys = ["w", "s", "a", "d", "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];

export function bindCameraInput(
  surface: HTMLElement,
  controls: HTMLElement,
  signal: AbortSignal,
  update: (keys: ReadonlySet<string>, release?: boolean) => void,
): () => void {
  const keyboard = new Set<string>();
  const pointers = new Map<number, string>();
  const pointerStarted = new Map<number, number>();
  let lastHold: { key: string; milliseconds: number } | undefined;
  const nudges = new Map<string, ReturnType<typeof setTimeout>>();
  const publish = (release = false) =>
    update(new Set([...keyboard, ...pointers.values(), ...nudges.keys()]), release);
  const nudge = (key: string, milliseconds: number) => {
    const previous = nudges.get(key);
    if (previous !== undefined) clearTimeout(previous);
    nudges.set(
      key,
      setTimeout(() => {
        nudges.delete(key);
        publish();
      }, milliseconds),
    );
  };
  const release = () => {
    keyboard.clear();
    pointers.clear();
    pointerStarted.clear();
    lastHold = undefined;
    for (const timer of nudges.values()) clearTimeout(timer);
    nudges.clear();
    publish(true);
  };
  surface.addEventListener(
    "keydown",
    (event) => {
      const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
      if (cameraKeys.includes(key)) {
        event.preventDefault();
        event.stopPropagation();
        keyboard.add(key);
        publish();
      } else if (key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        release();
        surface.blur();
      }
    },
    { signal },
  );
  surface.addEventListener(
    "keyup",
    (event) => {
      const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
      if (cameraKeys.includes(key)) {
        event.preventDefault();
        event.stopPropagation();
        keyboard.delete(key);
        publish();
      }
    },
    { signal },
  );
  surface.addEventListener("blur", release, { signal });
  controls.addEventListener(
    "pointerdown",
    (event) => {
      const target = event.target;
      if (!(target instanceof HTMLButtonElement) || !target.dataset.key || event.button !== 0)
        return;
      event.preventDefault();
      target.setPointerCapture(event.pointerId);
      lastHold = undefined;
      pointers.set(event.pointerId, target.dataset.key);
      pointerStarted.set(event.pointerId, performance.now());
      publish();
    },
    { signal },
  );
  for (const kind of ["pointerup", "pointercancel", "lostpointercapture"] as const) {
    controls.addEventListener(
      kind,
      (event) => {
        const key = pointers.get(event.pointerId);
        const started = pointerStarted.get(event.pointerId);
        if (kind === "pointerup" && key && started !== undefined) {
          lastHold = { key, milliseconds: performance.now() - started };
          if (lastHold.milliseconds < 250) nudge(key, 250 - lastHold.milliseconds);
        }
        pointers.delete(event.pointerId);
        pointerStarted.delete(event.pointerId);
        publish();
      },
      { signal },
    );
  }
  controls.addEventListener(
    "keydown",
    (event) => {
      const target = event.target;
      if (
        target instanceof HTMLButtonElement &&
        target.dataset.key &&
        [" ", "Enter"].includes(event.key)
      ) {
        event.preventDefault();
        event.stopPropagation();
        keyboard.add(target.dataset.key);
        publish();
      }
    },
    { signal },
  );
  controls.addEventListener(
    "keyup",
    (event) => {
      const target = event.target;
      if (
        target instanceof HTMLButtonElement &&
        target.dataset.key &&
        [" ", "Enter"].includes(event.key)
      ) {
        event.preventDefault();
        event.stopPropagation();
        keyboard.delete(target.dataset.key);
        publish();
      }
    },
    { signal },
  );
  controls.addEventListener("focusout", release, { signal });
  controls.addEventListener(
    "click",
    (event) => {
      const target = event.target;
      if (!(target instanceof HTMLButtonElement) || !target.dataset.key) return;
      if (event.detail !== 0 && lastHold?.key === target.dataset.key) return;
      const key = target.dataset.key;
      nudge(key, 250);
      publish();
    },
    { signal },
  );
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
