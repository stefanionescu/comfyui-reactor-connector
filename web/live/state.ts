import { browserLimits } from '#web/browser.ts';
import { cameraAxes } from '#web/live/input.ts';

type CameraState = { axes: Record<string, string>; release: boolean };

export class CameraStates {
  private current: Record<string, string>;

  private pending: CameraState[];

  private hasIndependentAxes: boolean;

  /**
   * Initialize idle camera movement for the selected model.
   * @param hasIndependentAxes - Whether independent movement axes are supported.
   */
  constructor(hasIndependentAxes: boolean) {
    this.hasIndependentAxes = hasIndependentAxes;
    this.current = cameraAxes(new Set(), hasIndependentAxes);
    this.pending = [];
  }

  /**
   * Queue changed camera input while preserving explicit releases.
   * @param keys - The keys currently held or briefly pressed.
   * @param release - Whether to clear queued movement before this update.
   */
  update(keys: ReadonlySet<string>, release = false): void {
    const axes = cameraAxes(keys, this.hasIndependentAxes);
    if (release) this.pending = [];
    if (release || JSON.stringify(axes) !== JSON.stringify(this.current)) {
      if (this.pending.length >= browserLimits.maxPendingInputs) {
        // Stop old movement before applying the latest input.
        this.pending = [{ axes: cameraAxes(new Set(), this.hasIndependentAxes), release: true }];
        if (!Object.values(axes).every(Object.is.bind(null, 'idle')))
          this.pending.push({ axes, release: false });
      } else this.pending.push({ axes, release });
    }
    this.current = axes;
  }

  /**
   * Consume a queued camera update or keep the current held movement.
   * @returns The axes and release flag for the next exchange.
   */
  take(): CameraState {
    const queued = this.pending.shift();
    if (queued) return queued;
    return { axes: this.current, release: false };
  }
}
