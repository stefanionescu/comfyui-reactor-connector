import { cameraAxes } from '#web/live/input.ts';
import { browserLimits } from '#config/browser.ts';

type CameraState = { axes: Record<string, string>; release: boolean };

export class CameraStates {
  private current: Record<string, string>;

  private pending: CameraState[] = [];

  private hasIndependentAxes: boolean;

  /**
   * Initialize idle camera movement for the selected model.
   * @param hasIndependentAxes - Whether independent movement axes are supported.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Construction records the model and initializes its supported idle axes.
  constructor(hasIndependentAxes: boolean) {
    this.hasIndependentAxes = hasIndependentAxes;
    this.current = cameraAxes(new Set(), hasIndependentAxes);
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
        if (Object.values(axes).some((value) => value !== 'idle'))
          this.pending.push({ axes, release: false });
      } else this.pending.push({ axes, release });
    }
    this.current = axes;
  }

  /**
   * Consume a queued camera update or keep the current held movement.
   * @returns The axes and release flag for the next exchange.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Reading the next state consumes a queued update, so callers must use this owner.
  take(): CameraState {
    return this.pending.shift() ?? { axes: this.current, release: false };
  }
}
