import { cameraAxes } from "./live-input.ts";

type CameraState = { axes: Record<string, string>; release: boolean };

export class CameraStates {
  private current: Record<string, string>;
  private pending: CameraState[] = [];
  private world2: boolean;

  constructor(world2: boolean) {
    this.world2 = world2;
    this.current = cameraAxes(new Set(), world2);
  }

  update(keys: ReadonlySet<string>, release = false): void {
    const axes = cameraAxes(keys, this.world2);
    if (release) this.pending = [];
    if (release || JSON.stringify(axes) !== JSON.stringify(this.current)) {
      if (this.pending.length >= 8) {
        // Stop old movement before applying the latest input.
        this.pending = [{ axes: cameraAxes(new Set(), this.world2), release: true }];
        if (Object.values(axes).some((value) => value !== "idle"))
          this.pending.push({ axes, release: false });
      } else this.pending.push({ axes, release });
    }
    this.current = axes;
  }

  take(): CameraState {
    return this.pending.shift() ?? { axes: this.current, release: false };
  }
}
