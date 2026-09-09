import type { Fetcher } from '#web/http.ts';
import { button, element } from '#web/dom.ts';
import type { Controls } from '#web/live/commands.ts';
import { translate, type MessageKey } from '#web/language.ts';
import { message, setTextAttribute, setText } from '#web/localization.ts';

export class Webcam {
  readonly view = element('section');

  readonly video = element('video');

  readonly enable = button(message('camera.enable'));

  readonly select = element('select');

  readonly status = element('p');

  private stream: MediaStream | undefined;

  private closed = false;

  private sequence = 0;

  private readonly canvas = element('canvas');

  private upload: Promise<void> | undefined;

  private readonly controller = new AbortController();

  /**
   * Build camera selection and a muted input preview.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   * @param fail - Request session ending if the camera disconnects.
   */
  constructor(
    private owner: Controls,
    private fetcher: Fetcher,
    private fail: (message: string) => void,
  ) {
    this.view.className = 'reactor-webcam';
    const label = element('label', message('camera.label'));
    label.append(this.select);
    const defaultCamera = element('option', message('camera.default'));
    defaultCamera.value = '';
    this.select.append(defaultCamera);
    this.video.muted = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.hidden = true;
    setTextAttribute(this.video, 'aria-label', message('camera.preview'));
    const controls = element('div');
    controls.append(label, this.enable);
    this.view.append(controls, this.video, this.status);
    this.enable.addEventListener('click', () => void this.start());
  }

  private async start(): Promise<void> {
    this.enable.disabled = true;
    try {
      if (!(await this.openCamera())) return;
      await this.listCameras();
      if (this.closed) return;
      setText(this.enable, message('camera.select'));
      setText(this.status, message('camera.enabled'));
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      const errors: Record<string, MessageKey> = {
        NotAllowedError: 'camera.permissionDenied',
        SecurityError: 'camera.browserRequirements',
        NotFoundError: 'camera.notFound',
        NotReadableError: 'camera.busy',
        OverconstrainedError: 'camera.unavailableSelection',
      };
      setText(
        this.status,
        message(
          error instanceof Error
            ? (errors[error.name] ?? 'camera.accessFailed')
            : 'camera.accessFailed',
        ),
      );
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }

  /**
   * Open the selected camera and release any previous stream.
   * @returns Whether the camera is ready and the panel is still open.
   */
  private async openCamera(): Promise<boolean> {
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition -- DOM types omit browsers and insecure contexts where camera access is unavailable.
    if (!navigator.mediaDevices?.getUserMedia) throw new DOMException('', 'SecurityError');
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
      return false;
    }
    for (const track of this.stream?.getTracks() ?? []) {
      track.stop();
    }
    this.stream = stream;
    this.video.srcObject = stream;
    await this.video.play();
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition -- The panel can close while video.play() is awaiting playback.
    if (this.closed) return false;
    this.video.hidden = false;
    return true;
  }

  /**
   * List cameras after permission reveals their names.
   * @returns When the available camera choices have been updated.
   */
  private async listCameras(): Promise<void> {
    const devices = await navigator.mediaDevices.enumerateDevices();
    if (this.closed) return;
    const selected = this.stream?.getVideoTracks()[0]?.getSettings().deviceId;
    this.select.replaceChildren(
      ...devices
        .filter((device) => device.kind === 'videoinput')
        .map((device, index) => {
          const option = element(
            'option',
            device.label || message('camera.number', { number: index + 1 }),
          );
          option.value = device.deviceId;
          option.selected = device.deviceId === selected;
          return option;
        }),
    );
  }

  /**
   * Upload a camera frame without overlapping uploads.
   * @returns Whether a camera frame was available to send.
   */
  async frame(): Promise<boolean> {
    if (this.closed || !this.stream || this.video.readyState < 2) return false;
    if (this.stream.getVideoTracks().some((track) => track.readyState !== 'live')) {
      this.fail(translate('camera.disconnected'));
      return false;
    }
    if (this.upload) {
      await this.upload;
      return true;
    }
    const ratio = Math.min(640 / this.video.videoWidth, 480 / this.video.videoHeight, 1);
    this.canvas.width = Math.max(1, Math.round(this.video.videoWidth * ratio));
    this.canvas.height = Math.max(1, Math.round(this.video.videoHeight * ratio));
    const context = this.canvas.getContext('2d');
    if (!context) throw new Error(translate('camera.readFailed'));
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
    const blob = await new Promise<Blob | null>((fulfill) =>
      this.canvas.toBlob(fulfill, 'image/jpeg', 0.8),
    );
    if (this.closed || !blob) return;
    const response = await this.fetcher('/reactor-inc/v1/live/camera', {
      method: 'POST',
      cache: 'no-store',
      body: blob,
      signal: AbortSignal.any([this.controller.signal, AbortSignal.timeout(2000)]),
      headers: {
        'Content-Type': 'image/jpeg',
        'X-Reactor-Comfy': '1',
        'X-Reactor-Lease': this.owner.lease,
        'X-Reactor-Capability': this.owner.capability,
        'X-Reactor-Sequence': String(this.sequence++),
      },
    });
    if (!response.ok) throw new Error(translate('camera.uploadFailed'));
  }

  /**
   * Stop the camera, cancel uploads, and clear the capture canvas.
   */
  close(): void {
    this.closed = true;
    this.controller.abort();
    this.stopCamera();
    this.select.disabled = this.enable.disabled = true;
    setText(this.status, message('camera.disabled'));
    this.canvas.width = this.canvas.height = 0;
  }

  private stopCamera(): void {
    this.video.hidden = true;
    for (const track of this.stream?.getTracks() ?? []) {
      track.stop();
    }
    this.stream = undefined;
    this.video.srcObject = null;
  }
}
