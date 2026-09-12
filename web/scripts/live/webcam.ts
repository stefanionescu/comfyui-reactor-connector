import type { Fetcher } from '#web/http.ts';
import { button, element } from '#web/dom.ts';
import { browserRoutes } from '#web/routes.ts';
import type { ControlsInvitation } from '#web/live/schema.ts';
import { browserInput, browserLimits } from '#web/browser.ts';
import { translate, type MessageKey } from '#web/language.ts';
import { releaseText, message, setTextAttribute, setText } from '#web/localization.ts';

export class Webcam {
  readonly view = element('section');

  readonly video = element('video');

  readonly enable = button(message('camera.enable'));

  readonly select = element('select');

  readonly status = element('p', message('camera.disabled'));

  private stream: MediaStream | undefined;

  private closed = false;

  private sequence = 0;

  private readonly canvas = element('canvas');

  private upload: Promise<boolean> | undefined;

  private readonly controller = new AbortController();

  /**
   * Build camera selection and a muted input preview.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   * @param fail - Request session ending if the camera disconnects.
   */
  constructor(
    private owner: ControlsInvitation,
    private fetcher: Fetcher,
    private fail: (message: string) => void,
  ) {
    this.view.className = 'reactor-webcam';
    const heading = element('header');
    heading.append(element('h3', message('camera.label')), this.status);
    this.status.setAttribute('role', 'status');
    setTextAttribute(this.select, 'aria-label', message('camera.label'));
    const defaultCamera = element('option', message('camera.default'));
    defaultCamera.value = '';
    this.select.append(defaultCamera);
    this.video.muted = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.hidden = true;
    setTextAttribute(this.video, 'aria-label', message('camera.preview'));
    const controls = element('div');
    controls.className = 'reactor-camera-controls';
    controls.append(this.select, this.enable);
    this.view.append(heading, controls, this.video);
    this.enable.addEventListener('click', () => {
      this.enable.disabled = true;
      const selected = this.select.value;
      void this.start(selected);
    });
  }

  private async start(selected: string): Promise<void> {
    try {
      if (!(await this.openCamera(selected))) return;
      await this.listCameras();
      if (this.closed) return;
      setText(this.enable, message('camera.select'));
      setText(this.status, message('camera.enabled'));
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      const errors = new Map<string, MessageKey>([
        ['NotAllowedError', 'camera.permissionDenied'],
        ['SecurityError', 'camera.browserRequirements'],
        ['NotFoundError', 'camera.notFound'],
        ['NotReadableError', 'camera.busy'],
        ['OverconstrainedError', 'camera.unavailableSelection'],
      ]);
      setText(
        this.status,
        message(
          error instanceof Error
            ? (errors.get(error.name) ?? 'camera.accessFailed')
            : 'camera.accessFailed',
        ),
      );
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }

  /**
   * Open the selected camera and release any previous stream.
   * @param selected - The selected device ID, or an empty string for the default camera.
   * @returns Whether the camera is ready and the panel is still open.
   */
  private async openCamera(selected: string): Promise<boolean> {
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition -- DOM types omit browsers and insecure contexts where camera access is unavailable.
    if (!navigator.mediaDevices?.getUserMedia) throw new DOMException('', 'SecurityError');
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        width: { ideal: browserInput.cameraWidth },
        height: { ideal: browserInput.cameraHeight },
        frameRate: {
          ideal: browserInput.cameraIdealFrameRate,
          max: browserInput.cameraMaxFrameRate,
        },
        ...(selected ? { deviceId: { exact: selected } } : {}),
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
    const options = document.createDocumentFragment();
    for (const device of devices) {
      if (device.kind !== 'videoinput') continue;
      const option = element(
        'option',
        device.label || message('camera.number', { number: options.childElementCount + 1 }),
      );
      option.value = device.deviceId;
      option.selected = device.deviceId === selected;
      options.appendChild(option);
    }
    releaseText(this.select);
    this.select.replaceChildren();
    this.select.appendChild(options);
  }

  /**
   * Upload a camera frame without overlapping uploads.
   * @returns Whether a camera frame was uploaded successfully.
   */
  async frame(): Promise<boolean> {
    if (this.closed || !this.stream || this.video.readyState < 2) return false;
    for (const track of this.stream.getVideoTracks()) {
      if (track.readyState === 'live') continue;
      this.fail(translate('camera.disconnected'));
      return false;
    }
    if (this.upload) {
      return await this.upload;
    }
    const ratio = Math.min(
      browserInput.cameraWidth / this.video.videoWidth,
      browserInput.cameraHeight / this.video.videoHeight,
      1,
    );
    this.canvas.width = Math.max(1, Math.round(this.video.videoWidth * ratio));
    this.canvas.height = Math.max(1, Math.round(this.video.videoHeight * ratio));
    this.upload = this.send();
    try {
      return await this.upload;
    } finally {
      this.upload = undefined;
    }
  }

  private async send(): Promise<boolean> {
    const blob = await new Promise<Blob | null>((fulfill) => {
      const context = this.canvas.getContext('2d');
      if (!context) throw new Error(translate('camera.readFailed'));
      context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
      this.canvas.toBlob(fulfill, 'image/jpeg', browserInput.cameraJpegQuality);
    });
    if (this.closed) return false;
    if (!blob) throw new Error(translate('camera.readFailed'));
    const response = await this.fetcher(browserRoutes.live.camera, {
      method: 'POST',
      cache: 'no-store',
      body: blob,
      signal: AbortSignal.any([
        this.controller.signal,
        AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
      ]),
      headers: {
        'Content-Type': 'image/jpeg',
        'X-Reactor-Comfy': '1',
        'X-Reactor-Lease': this.owner.lease,
        'X-Reactor-Capability': this.owner.capability,
        'X-Reactor-Sequence': String(this.sequence++),
      },
    });
    if (!response.ok) throw new Error(translate('camera.uploadFailed'));
    return true;
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
