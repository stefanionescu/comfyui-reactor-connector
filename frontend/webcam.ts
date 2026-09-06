import type { Fetcher } from "./configuration.ts";
import type { Controls } from "./control-api.ts";
import { button, element } from "./dom.ts";

export class Webcam {
  readonly view = element("section");
  readonly video = element("video");
  readonly enable = button("Enable camera");
  readonly select = element("select");
  readonly status = element("p");
  private stream: MediaStream | undefined;
  private closed = false;
  private sequence = 0;
  private readonly canvas = element("canvas");
  private upload: Promise<void> | undefined;
  private readonly controller = new AbortController();

  constructor(
    private owner: Controls,
    private fetcher: Fetcher,
    private fail: (message: string) => void,
  ) {
    this.view.className = "reactor-webcam";
    const label = element("label", "Camera ");
    label.append(this.select);
    this.select.append(new Option("Default camera", ""));
    this.video.muted = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.hidden = true;
    this.video.setAttribute("aria-label", "Your camera input");
    const controls = element("div");
    controls.append(label, this.enable);
    this.view.append(controls, this.video, this.status);
    this.enable.addEventListener("click", () => {
      void this.start();
    });
  }

  private async start(): Promise<void> {
    this.enable.disabled = true;
    try {
      if (!navigator.mediaDevices?.getUserMedia)
        throw new Error("Camera access needs localhost or HTTPS and a supported browser.");
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          frameRate: { ideal: 12, max: 24 },
          ...(this.select.value ? { deviceId: { exact: this.select.value } } : {}),
        },
      });
      if (this.closed) {
        for (const track of stream.getTracks()) track.stop();
        return;
      }
      this.stream?.getTracks().forEach((track) => {
        track.stop();
      });
      this.stream = stream;
      this.video.srcObject = stream;
      await this.video.play();
      if (this.closed) return;
      this.video.hidden = false;
      const devices = await navigator.mediaDevices.enumerateDevices();
      if (this.closed) return;
      const selected = stream.getVideoTracks()[0]?.getSettings().deviceId;
      this.select.replaceChildren(
        ...devices
          .filter((device) => device.kind === "videoinput")
          .map(
            (device, index) =>
              new Option(
                device.label || `Camera ${index + 1}`,
                device.deviceId,
                false,
                device.deviceId === selected,
              ),
          ),
      );
      this.enable.textContent = "Use selected camera";
      this.status.textContent = "Camera on. Microphone audio is off.";
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      this.status.textContent =
        error instanceof Error
          ? error.message
          : "Camera access failed. Choose a camera and try again.";
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }

  async frame(): Promise<boolean> {
    if (this.closed || !this.stream || this.video.readyState < 2) return false;
    if (this.stream.getVideoTracks().some((track) => track.readyState !== "live")) {
      this.fail("The camera disconnected. The session is ending.");
      return false;
    }
    if (this.upload) {
      await this.upload;
      return true;
    }
    const ratio = Math.min(640 / this.video.videoWidth, 480 / this.video.videoHeight, 1);
    this.canvas.width = Math.max(1, Math.round(this.video.videoWidth * ratio));
    this.canvas.height = Math.max(1, Math.round(this.video.videoHeight * ratio));
    const context = this.canvas.getContext("2d");
    if (!context) throw new Error("Camera frames could not be read.");
    context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
    this.upload = this.send();
    try {
      await this.upload;
      return true;
    } finally {
      this.upload = undefined;
    }
  }

  private async send(): Promise<void> {
    const blob = await new Promise<Blob | null>((resolve) =>
      this.canvas.toBlob(resolve, "image/jpeg", 0.8),
    );
    if (this.closed || !blob) return;
    const response = await this.fetcher("/reactor-inc/v1/live/camera", {
      method: "POST",
      cache: "no-store",
      body: blob,
      signal: AbortSignal.any([this.controller.signal, AbortSignal.timeout(2000)]),
      headers: {
        "Content-Type": "image/jpeg",
        "X-Reactor-Comfy": "1",
        "X-Reactor-Lease": this.owner.lease,
        "X-Reactor-Capability": this.owner.capability,
        "X-Reactor-Sequence": String(this.sequence++),
      },
    });
    if (!response.ok) throw new Error("Camera frames could not reach the session.");
  }

  close(): void {
    this.closed = true;
    this.controller.abort();
    this.stopCamera();
    this.select.disabled = this.enable.disabled = true;
    this.status.textContent = "Camera off.";
    this.canvas.width = this.canvas.height = 0;
  }

  private stopCamera(): void {
    this.video.hidden = true;
    this.stream?.getTracks().forEach((track) => {
      track.stop();
    });
    this.stream = undefined;
    this.video.srcObject = null;
  }
}
