import { browserLimits } from '#web/browser.ts';

/**
 * Convert held keys to the model's supported movement axes.
 * @param keys - The keys currently held or briefly pressed.
 * @param hasIndependentAxes - Whether the model accepts independent movement axes.
 * @returns Movement and look directions for the model.
 */
export function cameraAxes(
  keys: ReadonlySet<string>,
  hasIndependentAxes: boolean,
): Record<string, string> {
  /**
   * Resolve an opposing pair of keys.
   * @param firstKey - The key for the first direction.
   * @param secondKey - The key for the opposite direction.
   * @param firstDirection - The model's first direction value.
   * @param secondDirection - The model's opposite direction value.
   * @returns The chosen direction, or idle when neither or both keys are held.
   */
  function direction(
    firstKey: string,
    secondKey: string,
    firstDirection: string,
    secondDirection: string,
  ): string {
    if (keys.has(firstKey) === keys.has(secondKey)) return 'idle';
    return keys.has(firstKey) ? firstDirection : secondDirection;
  }
  const forward = direction('w', 's', 'forward', 'back');
  const lateral = direction('a', 'd', 'strafe_left', 'strafe_right');
  return {
    ...(hasIndependentAxes
      ? { move_longitudinal: forward, move_lateral: lateral }
      : { movement: forward !== 'idle' ? forward : lateral }),
    look_horizontal: direction('ArrowLeft', 'ArrowRight', 'left', 'right'),
    look_vertical: direction('ArrowUp', 'ArrowDown', 'up', 'down'),
  };
}

const cameraKeys = ['w', 's', 'a', 'd', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];

/** Combine keyboard, held buttons, and short presses into camera input. */
export class CameraInput {
  private readonly keyboard = new Set<string>();

  private readonly pointers = new Map<number, string>();

  private readonly pointerStarted = new Map<number, number>();

  private readonly nudges = new Map<string, ReturnType<typeof setTimeout>>();

  private lastHold: { key: string; milliseconds: number } | undefined;

  /**
   * Bind camera input for the lifetime of the panel.
   * @param surface - The keyboard camera surface.
   * @param controls - The camera direction buttons.
   * @param signal - The panel's listener lifetime.
   * @param update - Receive the combined keys and explicit release requests.
   */
  constructor(
    surface: HTMLElement,
    controls: HTMLElement,
    signal: AbortSignal,
    private readonly update: (keys: ReadonlySet<string>, release?: boolean) => void,
  ) {
    surface.addEventListener(
      'keydown',
      (event) => {
        const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
        if (cameraKeys.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
          this.keyboard.add(key);
          this.publish();
        } else if (key === 'Escape') {
          event.preventDefault();
          event.stopPropagation();
          this.release();
          surface.blur();
        }
      },
      { signal },
    );
    surface.addEventListener(
      'keyup',
      (event) => {
        const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
        if (cameraKeys.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
          this.keyboard.delete(key);
          this.publish();
        }
      },
      { signal },
    );
    surface.addEventListener('blur', this.release.bind(this), { signal });
    this.bindButtons(controls, signal);
    window.addEventListener('blur', this.release.bind(this), { signal });
    document.addEventListener(
      'visibilitychange',
      () => {
        if (document.hidden) this.release();
      },
      { signal },
    );
    signal.addEventListener('abort', this.release.bind(this), { once: true });
  }

  /**
   * Send combined input after a key, pointer, or timer changes.
   * @param release - Whether the user explicitly released all input.
   */

  private publish(release = false): void {
    const keys = new Set(this.keyboard);
    for (const key of this.pointers.values()) keys.add(key);
    for (const key of this.nudges.keys()) keys.add(key);
    this.update(keys, release);
  }

  /**
   * Keep a short press visible for the next server update.
   * @param key - The direction key to hold briefly.
   * @param milliseconds - Remaining duration of the short press.
   */
  private nudge(key: string, milliseconds: number): void {
    const previous = this.nudges.get(key);
    if (previous !== undefined) clearTimeout(previous);
    this.nudges.set(
      key,

      setTimeout(() => {
        this.nudges.delete(key);
        this.publish();
      }, milliseconds),
    );
  }

  /** Clear every held input and timer, then send an explicit release. */
  release(): void {
    this.keyboard.clear();
    this.pointers.clear();
    this.pointerStarted.clear();
    this.lastHold = undefined;
    for (const timer of this.nudges.values()) clearTimeout(timer);
    this.nudges.clear();
    this.publish(true);
  }

  /**
   * Bind mouse, touch, keyboard, and assistive button activation.
   * @param controls - The container for direction buttons.
   * @param signal - The panel's listener lifetime.
   */
  private bindButtons(controls: HTMLElement, signal: AbortSignal): void {
    controls.addEventListener(
      'pointerdown',
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key || event.button !== 0)
          return;
        event.preventDefault();
        target.setPointerCapture(event.pointerId);
        this.lastHold = undefined;
        this.pointers.set(event.pointerId, target.dataset.key);
        this.pointerStarted.set(event.pointerId, performance.now());
        this.publish();
      },
      { signal },
    );
    for (const kind of ['pointerup', 'pointercancel', 'lostpointercapture'] as const)
      controls.addEventListener(kind, this.releasePointer.bind(this), { signal });
    for (const kind of ['keydown', 'keyup'] as const)
      controls.addEventListener(kind, this.buttonKey.bind(this), { signal });
    controls.addEventListener('focusout', this.release.bind(this), { signal });
    controls.addEventListener(
      'click',
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key) return;
        if (event.detail !== 0 && this.lastHold?.key === target.dataset.key) return;
        this.nudge(target.dataset.key, browserLimits.inputNudgeMilliseconds);
        this.publish();
      },
      { signal },
    );
  }

  /**
   * Finish a held button and preserve very short presses.
   * @param event - The pointer release or cancellation.
   */
  private releasePointer(event: PointerEvent): void {
    const key = this.pointers.get(event.pointerId);
    const started = this.pointerStarted.get(event.pointerId);
    if (event.type === 'pointerup' && key && started !== undefined) {
      this.lastHold = { key, milliseconds: performance.now() - started };
      if (this.lastHold.milliseconds < browserLimits.inputNudgeMilliseconds)
        this.nudge(key, browserLimits.inputNudgeMilliseconds - this.lastHold.milliseconds);
    }
    this.pointers.delete(event.pointerId);
    this.pointerStarted.delete(event.pointerId);
    this.publish();
  }

  /**
   * Treat Space and Enter as a held direction on a focused button.
   * @param event - A key press or release on the button container.
   */
  private buttonKey(event: KeyboardEvent): void {
    const target = event.target;
    if (
      !(target instanceof HTMLButtonElement) ||
      !target.dataset.key ||
      ![' ', 'Enter'].includes(event.key)
    )
      return;
    event.preventDefault();
    event.stopPropagation();
    if (event.type === 'keydown') this.keyboard.add(target.dataset.key);
    else this.keyboard.delete(target.dataset.key);
    this.publish();
  }
}
