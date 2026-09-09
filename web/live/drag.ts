import { translate } from '#web/language.ts';

export type Pointer = { x: number; y: number; active: boolean };

/** Track one mouse, touch, or keyboard drag on a model preview. */
export class DragInput {
  private pointer: Pointer = { x: 0.5, y: 0.5, active: false };

  private captured: number | undefined;

  /**
   * Bind input until the panel's abort signal fires.
   * @param image - The output image that receives input.
   * @param signal - The panel's listener lifetime.
   * @param send - Receive pointer updates in normalized image coordinates.
   */
  constructor(
    private readonly image: HTMLImageElement,
    signal: AbortSignal,
    private readonly send: (pointer: Pointer) => void,
  ) {
    image.tabIndex = 0;
    image.draggable = false;
    image.style.touchAction = 'none';
    image.setAttribute('aria-label', translate('pointer.instructions'));
    image.addEventListener(
      'pointerdown',
      (event) => {
        if (event.button !== 0 || this.captured !== undefined) return;
        this.captured = event.pointerId;
        image.setPointerCapture(this.captured);
        image.focus();
        this.position(event);
      },
      { signal },
    );
    image.addEventListener(
      'pointermove',
      (event) => {
        if (this.captured === event.pointerId) this.position(event);
      },
      { signal },
    );
    for (const name of ['pointerup', 'pointercancel', 'lostpointercapture', 'blur'])
      image.addEventListener(name, () => this.release(), { signal });
    image.addEventListener('keydown', (event) => this.keydown(event), { signal });
    image.addEventListener(
      'keyup',
      (event) => {
        if (event.key === ' ') {
          event.preventDefault();
          event.stopPropagation();
          this.release();
        }
      },
      { signal },
    );
    window.addEventListener('blur', () => this.release(), { signal });
    document.addEventListener(
      'visibilitychange',
      () => {
        if (document.hidden) this.release();
      },
      { signal },
    );
    signal.addEventListener('abort', () => this.release(), { once: true });
  }

  /** Stop holding the pointer and release any browser pointer capture. */
  release(): void {
    const wasActive = this.pointer.active;
    this.pointer = { ...this.pointer, active: false };
    const previousCapture = this.captured;
    this.captured = undefined;
    if (wasActive) this.send(this.pointer);
    if (previousCapture !== undefined && this.image.hasPointerCapture(previousCapture))
      this.image.releasePointerCapture(previousCapture);
  }

  /**
   * Normalize a drag event to the displayed image bounds.
   * @param event - The captured pointer event.
   */
  private position(event: PointerEvent): void {
    const rect = this.image.getBoundingClientRect();
    this.pointer = {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
      active: true,
    };
    this.send(this.pointer);
  }

  /**
   * Move, hold, or release the pointer with the keyboard.
   * @param event - A key pressed while the preview has focus.
   */
  private keydown(event: KeyboardEvent): void {
    const offsets: Record<string, readonly [number, number]> = {
      ArrowLeft: [-0.03, 0],
      ArrowRight: [0.03, 0],
      ArrowUp: [0, -0.03],
      ArrowDown: [0, 0.03],
      ' ': [0, 0],
      Escape: [0, 0],
    };
    const offset = Object.hasOwn(offsets, event.key) ? offsets[event.key] : undefined;
    if (!offset) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.key === 'Escape') {
      this.release();
      this.image.blur();
      return;
    }
    this.pointer = {
      x: Math.max(0, Math.min(1, this.pointer.x + offset[0])),
      y: Math.max(0, Math.min(1, this.pointer.y + offset[1])),
      active: event.key === ' ' || this.pointer.active,
    };
    this.send(this.pointer);
  }
}
