// web/extension.ts
import { api } from "../../scripts/api.js";
import { app as app2 } from "../../scripts/app.js";

// web/dom.ts
function element(tag, text) {
  const node = document.createElement(tag);
  if (text !== void 0) node.textContent = text;
  return node;
}
function button(text, type = "button") {
  const node = element("button", text);
  node.type = type;
  return node;
}

// web/live/commands.ts
var modelTitles = /* @__PURE__ */ new Map([
  ["reactor/helios", "Helios"],
  ["reactor/longlive-v2", "LongLive"],
  ["reactor/sana-streaming", "SANA"],
  ["xmax/x2", "X2"],
  ["reactor/visko-orbis-stable", "Visko Stable"],
  ["reactor/visko-orbis-dynamic", "Visko Dynamic"]
]);
function controls(value) {
  if (typeof value !== "object" || value === null) return;
  const v = value;
  const modelTitle = typeof v.model === "string" ? modelTitles.get(v.model) : void 0;
  if (typeof v.lease !== "string" || !/^[a-f0-9]{32}$/.test(v.lease) || typeof v.capability !== "string" || !/^[A-Za-z0-9_-]{43}$/.test(v.capability) || typeof v.model !== "string" || modelTitle === void 0 || typeof v.prompt !== "string" || typeof v.prompt_limit !== "number" || v.prompt_limit < 1 || v.prompt_limit > 2e4 || typeof v.webcam !== "boolean" || typeof v.pointer !== "boolean" || typeof v.sound !== "boolean" || typeof v.audio_prompt !== "string" || v.audio_prompt.length > 2e3 || typeof v.duration_seconds !== "number" || !Number.isFinite(v.duration_seconds) || v.duration_seconds <= 0 || v.duration_seconds > 3600)
    return;
  return {
    lease: v.lease,
    capability: v.capability,
    model: v.model,
    modelTitle,
    duration_seconds: v.duration_seconds,
    axes: {},
    prompt: v.prompt,
    prompt_limit: v.prompt_limit,
    webcam: v.webcam,
    pointer: v.pointer,
    sound: v.sound,
    audio_prompt: v.audio_prompt
  };
}
async function action(fetcher, owner, sequence, name, data) {
  const response = await fetcher("/reactor-inc/v1/live/action", {
    method: "POST",
    cache: "no-store",
    signal: AbortSignal.timeout(2e3),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      action: name,
      data
    })
  });
  if (!response.ok) throw new Error("The live action was not accepted. The session is ending.");
}

// web/live/input.ts
function cameraAxes(keys, independentAxes) {
  function direction(negative, positive, first, second) {
    if (keys.has(negative) === keys.has(positive)) return "idle";
    return keys.has(negative) ? first : second;
  }
  const forward = direction("w", "s", "forward", "back");
  const lateral = direction("a", "d", "strafe_left", "strafe_right");
  return {
    ...independentAxes ? { move_longitudinal: forward, move_lateral: lateral } : { movement: forward !== "idle" ? forward : lateral },
    look_horizontal: direction("ArrowLeft", "ArrowRight", "left", "right"),
    look_vertical: direction("ArrowUp", "ArrowDown", "up", "down")
  };
}
var cameraKeys = ["w", "s", "a", "d", "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
var CameraInput = class {
  /**
   * Bind camera input for the lifetime of the panel.
   * @param surface - The keyboard camera surface.
   * @param controls - The camera direction buttons.
   * @param signal - The panel's listener lifetime.
   * @param update - Receive the combined keys and explicit release requests.
   */
  constructor(surface, controls2, signal, update) {
    this.update = update;
    surface.addEventListener(
      "keydown",
      (event) => {
        const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
        if (cameraKeys.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
          this.keyboard.add(key);
          this.publish();
        } else if (key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          this.release();
          surface.blur();
        }
      },
      { signal }
    );
    surface.addEventListener(
      "keyup",
      (event) => {
        const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
        if (cameraKeys.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
          this.keyboard.delete(key);
          this.publish();
        }
      },
      { signal }
    );
    surface.addEventListener("blur", () => this.release(), { signal });
    this.bindButtons(controls2, signal);
    window.addEventListener("blur", () => this.release(), { signal });
    document.addEventListener(
      "visibilitychange",
      () => {
        if (document.hidden) this.release();
      },
      { signal }
    );
    signal.addEventListener("abort", () => this.release(), { once: true });
  }
  update;
  keyboard = /* @__PURE__ */ new Set();
  pointers = /* @__PURE__ */ new Map();
  pointerStarted = /* @__PURE__ */ new Map();
  nudges = /* @__PURE__ */ new Map();
  lastHold;
  /**
   * Send combined input after a key, pointer, or timer changes.
   * @param release - Whether the user explicitly released all input.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Each event must publish the same combined keyboard, pointer, and timer state.
  publish(release = false) {
    const keys = /* @__PURE__ */ new Set([...this.keyboard, ...this.pointers.values(), ...this.nudges.keys()]);
    this.update(keys, release);
  }
  /**
   * Keep a short press visible for the next server update.
   * @param key - The direction key to hold briefly.
   * @param milliseconds - Remaining duration of the short press.
   */
  nudge(key, milliseconds) {
    const previous = this.nudges.get(key);
    if (previous !== void 0) clearTimeout(previous);
    this.nudges.set(
      key,
      // eslint-disable-next-line local/no-trivial-functions -- The timer removes its key before publishing the remaining held inputs.
      setTimeout(() => {
        this.nudges.delete(key);
        this.publish();
      }, milliseconds)
    );
  }
  /** Clear every held input and timer, then send an explicit release. */
  release() {
    this.keyboard.clear();
    this.pointers.clear();
    this.pointerStarted.clear();
    this.lastHold = void 0;
    for (const timer of this.nudges.values()) clearTimeout(timer);
    this.nudges.clear();
    this.publish(true);
  }
  /**
   * Bind mouse, touch, keyboard, and assistive button activation.
   * @param controls - The container for direction buttons.
   * @param signal - The panel's listener lifetime.
   */
  bindButtons(controls2, signal) {
    controls2.addEventListener(
      "pointerdown",
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key || event.button !== 0)
          return;
        event.preventDefault();
        target.setPointerCapture(event.pointerId);
        this.lastHold = void 0;
        this.pointers.set(event.pointerId, target.dataset.key);
        this.pointerStarted.set(event.pointerId, performance.now());
        this.publish();
      },
      { signal }
    );
    for (const kind of ["pointerup", "pointercancel", "lostpointercapture"])
      controls2.addEventListener(kind, (event) => this.releasePointer(event), { signal });
    for (const kind of ["keydown", "keyup"])
      controls2.addEventListener(kind, (event) => this.buttonKey(event), { signal });
    controls2.addEventListener("focusout", () => this.release(), { signal });
    controls2.addEventListener(
      "click",
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLButtonElement) || !target.dataset.key) return;
        if (event.detail !== 0 && this.lastHold?.key === target.dataset.key) return;
        this.nudge(target.dataset.key, 250);
        this.publish();
      },
      { signal }
    );
  }
  /**
   * Finish a held button and preserve very short presses.
   * @param event - The pointer release or cancellation.
   */
  releasePointer(event) {
    const key = this.pointers.get(event.pointerId);
    const started = this.pointerStarted.get(event.pointerId);
    if (event.type === "pointerup" && key && started !== void 0) {
      this.lastHold = { key, milliseconds: performance.now() - started };
      if (this.lastHold.milliseconds < 250) this.nudge(key, 250 - this.lastHold.milliseconds);
    }
    this.pointers.delete(event.pointerId);
    this.pointerStarted.delete(event.pointerId);
    this.publish();
  }
  /**
   * Treat Space and Enter as a held direction on a focused button.
   * @param event - A key press or release on the button container.
   */
  buttonKey(event) {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement) || !target.dataset.key || ![" ", "Enter"].includes(event.key))
      return;
    event.preventDefault();
    event.stopPropagation();
    if (event.type === "keydown") this.keyboard.add(target.dataset.key);
    else this.keyboard.delete(target.dataset.key);
    this.publish();
  }
};

// web/live/state.ts
var CameraStates = class {
  current;
  pending = [];
  independentAxes;
  /**
   * Initialize idle camera movement for the selected model.
   * @param independentAxes - Whether independent movement axes are supported.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Construction records the model and initializes its supported idle axes.
  constructor(independentAxes) {
    this.independentAxes = independentAxes;
    this.current = cameraAxes(/* @__PURE__ */ new Set(), independentAxes);
  }
  /**
   * Queue changed camera input while preserving explicit releases.
   * @param keys - The keys currently held or briefly pressed.
   * @param release - Whether to clear queued movement before this update.
   */
  update(keys, release = false) {
    const axes = cameraAxes(keys, this.independentAxes);
    if (release) this.pending = [];
    if (release || JSON.stringify(axes) !== JSON.stringify(this.current)) {
      if (this.pending.length >= 8) {
        this.pending = [{ axes: cameraAxes(/* @__PURE__ */ new Set(), this.independentAxes), release: true }];
        if (Object.values(axes).some((value) => value !== "idle"))
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
  take() {
    return this.pending.shift() ?? { axes: this.current, release: false };
  }
};

// web/live/api.ts
function record(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function invitation(value) {
  if (!record(value) || !record(value.axes)) return;
  if (typeof value.lease !== "string" || !/^[a-f0-9]{32}$/.test(value.lease) || typeof value.capability !== "string" || !/^[A-Za-z0-9_-]{43}$/.test(value.capability) || typeof value.model !== "string" || !["reactor/lingbot", "reactor/lingbot-world-2"].includes(value.model) || typeof value.prompt !== "string" || value.prompt.length > 2e3 || value.prompt_limit !== 1e3 || typeof value.duration_seconds !== "number" || !Number.isFinite(value.duration_seconds) || value.duration_seconds <= 0 || value.duration_seconds > 3600)
    return;
  const axes = {};
  const allowed = {
    movement: ["idle", "forward", "back", "strafe_left", "strafe_right"],
    move_longitudinal: ["idle", "forward", "back"],
    move_lateral: ["idle", "strafe_left", "strafe_right"],
    look_horizontal: ["idle", "left", "right"],
    look_vertical: ["idle", "up", "down"]
  };
  const expected = value.model === "reactor/lingbot" ? ["movement", "look_horizontal", "look_vertical"] : ["move_longitudinal", "move_lateral", "look_horizontal", "look_vertical"];
  if (Object.keys(value.axes).length !== expected.length) return;
  for (const key of expected) {
    const choices = value.axes[key];
    if (!Array.isArray(choices) || JSON.stringify(choices) !== JSON.stringify(allowed[key])) return;
    axes[key] = allowed[key] ?? [];
  }
  return {
    lease: value.lease,
    capability: value.capability,
    model: value.model,
    modelTitle: value.model === "reactor/lingbot" ? "LingBot" : "LingBot World 2",
    duration_seconds: value.duration_seconds,
    axes,
    prompt: value.prompt,
    prompt_limit: value.prompt_limit
  };
}
async function exchange(fetcher, owner, sequence, axes, end, previewSequence, signal, release = false) {
  const response = await fetcher("/reactor-inc/v1/live/exchange", {
    method: "POST",
    cache: "no-store",
    signal,
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      axes,
      end,
      release,
      preview_sequence: previewSequence
    })
  });
  if (!response.ok) throw new Error("Live controls could not reach their session.");
  const value = await response.json();
  if (!record(value) || typeof value.closed !== "boolean" || typeof value.termination_confirmed !== "boolean" || typeof value.failed !== "boolean" || typeof value.controls_ready !== "boolean" || typeof value.finishing !== "boolean" || typeof value.elapsed_seconds !== "number" || !Number.isFinite(value.elapsed_seconds) || typeof value.preview_sequence !== "number" || !Number.isSafeInteger(value.preview_sequence) || typeof value.preview !== "string" || value.preview.length > 35e4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(value.preview)) {
    throw new Error("The live panel received an invalid status.");
  }
  return {
    closed: value.closed,
    termination_confirmed: value.termination_confirmed,
    failed: value.failed,
    controls_ready: value.controls_ready,
    finishing: value.finishing,
    elapsed_seconds: value.elapsed_seconds,
    preview_sequence: value.preview_sequence,
    preview: value.preview
  };
}

// web/live/dialog.ts
var panels = /* @__PURE__ */ new Set();
var CameraPanel = class {
  /**
   * Build camera controls for the invited model.
   * @param owner - The validated camera session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(owner, fetcher) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.dialog.className = "reactor-settings reactor-live";
    this.dialog.setAttribute("aria-label", "Reactor live camera");
    this.status.setAttribute("role", "status");
    this.promptStatus.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.prompt_limit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.apply.disabled = true;
    this.surface.className = "reactor-preview";
    this.surface.tabIndex = 0;
    this.surface.setAttribute(
      "aria-label",
      "Live view. W A S D moves. Arrow keys turn. Escape stops camera movement."
    );
    this.image.alt = "Live model output";
    this.image.hidden = true;
    this.surface.append(this.image);
    this.controls.className = "reactor-actions";
    const labels = [
      "Forward",
      "Back",
      "Move left",
      "Move right",
      "Look left",
      "Look right",
      "Look up",
      "Look down"
    ];
    for (const [index, key] of cameraKeys.entries()) {
      const control = button(labels[index] ?? key);
      control.dataset.key = key;
      control.disabled = true;
      this.controls.append(control);
    }
    this.states = new CameraStates(owner.model.endsWith("world-2"));
    const input = new CameraInput(
      this.surface,
      this.controls,
      this.controller.signal,
      (keys, urgent) => this.states.update(keys, urgent)
    );
    this.release = input.release.bind(input);
    this.bindActions();
    this.appendContent();
  }
  owner;
  fetcher;
  previousFocus = document.activeElement;
  controller = new AbortController();
  dialog = element("dialog");
  status = element("p", "Connecting the live panel…");
  elapsed = element("p");
  prompt = element("textarea");
  apply = button("Apply prompt");
  promptStatus = element(
    "p",
    "Prompt changes affect later frames. The starting image stays fixed."
  );
  surface = element("div");
  image = element("img");
  controls = element("div");
  end = button("End session");
  states;
  release;
  pendingPrompt;
  actionSequence = 0;
  ending = false;
  finished = false;
  disposed = false;
  sequence = 0;
  previewSequence = 0;
  /** Build the session header, movement controls, and prompt input. */
  appendContent() {
    const header = element("header");
    header.append(element("h2", "Reactor live camera"), this.end);
    const promptLabel = element("label", "Scene prompt ");
    promptLabel.append(this.prompt);
    this.dialog.append(
      header,
      element("p", `${this.owner.modelTitle} · ${this.owner.duration_seconds} seconds of video`),
      element(
        "p",
        "Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement."
      ),
      this.surface,
      this.controls,
      promptLabel,
      this.apply,
      this.promptStatus,
      this.status,
      this.elapsed,
      element(
        "p",
        "The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Setup and recording use credits. Ending early discards the unfinished video."
      )
    );
  }
  /** Bind prompt updates, explicit ending, and focus cleanup. */
  bindActions() {
    this.apply.addEventListener("click", () => {
      if (!this.prompt.value.trim()) {
        this.promptStatus.textContent = "Enter a scene prompt before applying it.";
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.apply.disabled = true;
    });
    this.end.addEventListener("click", () => {
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      this.release();
      this.surface.blur();
    });
    this.dialog.addEventListener(
      "close",
      () => {
        this.stop();
        this.disposed = true;
        this.controller.abort();
        this.image.removeAttribute("src");
        panels.delete(this.owner.lease);
        this.dialog.remove();
        if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
          this.previousFocus.focus();
      },
      { once: true }
    );
  }
  /** Stop camera movement and request the end of the session. */
  stop() {
    this.ending = true;
    this.release();
    this.end.disabled = true;
    this.apply.disabled = this.prompt.disabled = true;
    this.status.textContent = "Ending the session…";
  }
  /**
   * Update camera controls and the preview while the panel is visible.
   * @param result - The validated session status.
   */
  display(result) {
    if (this.disposed) return;
    for (const control of this.controls.querySelectorAll("button"))
      control.disabled = !result.controls_ready || this.ending;
    this.prompt.disabled = !result.controls_ready || this.ending;
    this.apply.disabled = this.prompt.disabled || this.pendingPrompt !== void 0;
    this.elapsed.textContent = `Time spent on setup and recording: ${result.elapsed_seconds.toFixed(1)} seconds.`;
    if (result.preview) {
      this.image.src = `data:image/jpeg;base64,${result.preview}`;
      this.image.hidden = false;
    }
    this.displayProgress(result);
  }
  /**
   * Describe whether the model is preparing, recording, or finishing.
   * @param result - The validated session status.
   */
  displayProgress(result) {
    if (result.finishing && !result.closed) {
      this.release();
      this.surface.blur();
      this.end.disabled = true;
      this.status.textContent = "Ending the session…";
    } else if (!this.ending) {
      this.status.textContent = result.controls_ready && result.preview_sequence > 0 ? "Live preview. Controls are active." : "Waiting for model video…";
    }
  }
  /**
   * Show the final session result without implying unconfirmed termination.
   * @param result - The terminal session status.
   */
  finish(result) {
    this.finished = true;
    if (!result.termination_confirmed)
      this.status.textContent = "Reactor has not confirmed that the session ended. Wait for its time limit before another run.";
    else
      this.status.textContent = result.failed ? "The session ended without saving a video. Close this panel to view the workflow result." : "Session ended. Close this panel to view the workflow result.";
  }
  /**
   * Send a queued prompt only while the session accepts controls.
   * @param result - The current session readiness.
   * @returns When the prompt request, if any, finishes.
   */
  async sendPrompt(result) {
    if (!result.controls_ready || result.finishing || this.ending || this.pendingPrompt === void 0)
      return;
    await action(this.fetcher, this.owner, this.actionSequence++, "prompt", {
      prompt: this.pendingPrompt
    });
    this.pendingPrompt = void 0;
    this.promptStatus.textContent = "Prompt sent. Watch the video for the change.";
  }
  /**
   * Exchange input and status until the server ends the session.
   * @returns When polling and listener cleanup finish.
   */
  async poll() {
    try {
      while (!this.finished) {
        const input = this.states.take();
        const result = await exchange(
          this.fetcher,
          this.owner,
          this.sequence++,
          input.axes,
          this.ending,
          this.previewSequence,
          AbortSignal.timeout(2e3),
          input.release
        );
        this.previewSequence = result.preview_sequence;
        this.display(result);
        if (result.closed) this.finish(result);
        else {
          await this.sendPrompt(result);
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
      }
    } catch {
      this.finished = true;
      this.status.textContent = "The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.";
    } finally {
      this.release();
      this.controller.abort();
      this.end.disabled = false;
      this.end.textContent = "Close";
      this.prompt.disabled = this.apply.disabled = true;
      for (const control of this.controls.querySelectorAll("button")) control.disabled = true;
      if (this.disposed) panels.delete(this.owner.lease);
    }
  }
  /** Show the panel, focus camera input, and begin exchanging session status. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.surface.focus();
    void this.poll();
  }
};
function openLive(value, fetcher) {
  const owner = invitation(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new CameraPanel(owner, fetcher);
  panel.show();
}

// web/live/webcam.ts
var Webcam = class {
  /**
   * Build camera selection and a muted input preview.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   * @param fail - Request session ending if the camera disconnects.
   */
  constructor(owner, fetcher, fail) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.fail = fail;
    this.view.className = "reactor-webcam";
    const label = element("label", "Camera ");
    label.append(this.select);
    this.select.append(new Option("Default camera", ""));
    this.video.muted = true;
    this.video.autoplay = true;
    this.video.playsInline = true;
    this.video.hidden = true;
    this.video.setAttribute("aria-label", "Your camera input");
    const controls2 = element("div");
    controls2.append(label, this.enable);
    this.view.append(controls2, this.video, this.status);
    this.enable.addEventListener("click", () => void this.start());
  }
  owner;
  fetcher;
  fail;
  view = element("section");
  video = element("video");
  enable = button("Enable camera");
  select = element("select");
  status = element("p");
  stream;
  closed = false;
  sequence = 0;
  canvas = element("canvas");
  upload;
  controller = new AbortController();
  async start() {
    this.enable.disabled = true;
    try {
      if (!await this.openCamera()) return;
      await this.listCameras();
      if (this.closed) return;
      this.enable.textContent = "Use selected camera";
      this.status.textContent = "Camera on. Microphone audio is off.";
    } catch (error) {
      this.stopCamera();
      if (this.closed) return;
      this.status.textContent = error instanceof Error ? error.message : "Camera access failed. Choose a camera and try again.";
    } finally {
      if (!this.closed) this.enable.disabled = false;
    }
  }
  /**
   * Open the selected camera and release any previous stream.
   * @returns Whether the camera is ready and the panel is still open.
   */
  async openCamera() {
    if (!navigator.mediaDevices?.getUserMedia)
      throw new Error("Camera access needs localhost or HTTPS and a supported browser.");
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 12, max: 24 },
        ...this.select.value ? { deviceId: { exact: this.select.value } } : {}
      }
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
    if (this.closed) return false;
    this.video.hidden = false;
    return true;
  }
  /**
   * List cameras after permission reveals their names.
   * @returns When the available camera choices have been updated.
   */
  async listCameras() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    if (this.closed) return;
    const selected = this.stream?.getVideoTracks()[0]?.getSettings().deviceId;
    this.select.replaceChildren(
      ...devices.filter((device) => device.kind === "videoinput").map(
        (device, index) => new Option(
          device.label || `Camera ${index + 1}`,
          device.deviceId,
          false,
          device.deviceId === selected
        )
      )
    );
  }
  /**
   * Upload a camera frame without overlapping uploads.
   * @returns Whether a camera frame was available to send.
   */
  async frame() {
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
      this.upload = void 0;
    }
  }
  async send() {
    const blob = await new Promise(
      (resolve) => this.canvas.toBlob(resolve, "image/jpeg", 0.8)
    );
    if (this.closed || !blob) return;
    const response = await this.fetcher("/reactor-inc/v1/live/camera", {
      method: "POST",
      cache: "no-store",
      body: blob,
      signal: AbortSignal.any([this.controller.signal, AbortSignal.timeout(2e3)]),
      headers: {
        "Content-Type": "image/jpeg",
        "X-Reactor-Comfy": "1",
        "X-Reactor-Lease": this.owner.lease,
        "X-Reactor-Capability": this.owner.capability,
        "X-Reactor-Sequence": String(this.sequence++)
      }
    });
    if (!response.ok) throw new Error("Camera frames could not reach the session.");
  }
  /**
   * Stop the camera, cancel uploads, and clear the capture canvas.
   */
  close() {
    this.closed = true;
    this.controller.abort();
    this.stopCamera();
    this.select.disabled = this.enable.disabled = true;
    this.status.textContent = "Camera off.";
    this.canvas.width = this.canvas.height = 0;
  }
  stopCamera() {
    this.video.hidden = true;
    for (const track of this.stream?.getTracks() ?? []) {
      track.stop();
    }
    this.stream = void 0;
    this.video.srcObject = null;
  }
};

// web/live/sound.ts
var SoundControls = class {
  view = element("fieldset");
  prompt = element("textarea");
  apply = button("Apply sound prompt");
  pending;
  /**
   * Build the sound prompt controls in their disabled state.
   * @param initialPrompt - The workflow's starting sound prompt.
   */
  constructor(initialPrompt) {
    this.prompt.value = initialPrompt;
    this.prompt.maxLength = 1e3;
    this.prompt.rows = 2;
    const label = element("label", "Sound prompt ");
    label.append(this.prompt);
    this.view.append(
      element("legend", "Sound"),
      label,
      this.apply,
      element("p", "Describe the sound briefly. Leave blank to use the picture alone.")
    );
    this.apply.addEventListener("click", () => {
      this.pending = this.prompt.value;
      this.apply.disabled = true;
    });
    this.setReady(false);
  }
  /**
   * Enable sound input only when the session accepts changes.
   * @param ready - Whether the model accepts live controls.
   */
  // eslint-disable-next-line local/no-trivial-functions -- Both controls follow session readiness while a queued prompt keeps Apply disabled.
  setReady(ready) {
    this.prompt.disabled = !ready;
    this.apply.disabled = !ready || this.pending !== void 0;
  }
  /**
   * Consume the next sound prompt queued by the user.
   * @returns The queued prompt, or undefined when none is waiting.
   */
  takePrompt() {
    const value = this.pending;
    this.pending = void 0;
    return value;
  }
};

// web/live/pointer.ts
var PointerPreview = class {
  view = element("div");
  status = element("p");
  #marker = element("span");
  #state = element("span");
  #position = element("span");
  #image;
  #pointer;
  /**
   * Show pointer position alongside the output image.
   * @param image - The model output used for dragging.
   * @param signal - The panel's listener and observer lifetime.
   */
  constructor(image, signal) {
    this.#image = image;
    this.view.className = "reactor-pointer-preview";
    this.#marker.className = "reactor-pointer-marker";
    this.#marker.hidden = true;
    this.#marker.setAttribute("aria-hidden", "true");
    this.#state.setAttribute("role", "status");
    this.status.hidden = true;
    this.status.append(this.#state, this.#position);
    this.view.append(image, this.#marker);
    const resize = new ResizeObserver(() => this.#place());
    resize.observe(image);
    image.addEventListener("blur", () => this.#marker.hidden = true, { signal });
    image.addEventListener("focus", () => this.#place(), { signal });
    signal.addEventListener("abort", () => resize.disconnect(), { once: true });
  }
  /**
   * Move the marker to the user's latest pointer position.
   * @param pointer - The normalized image coordinates and hold state.
   */
  move(pointer) {
    this.#pointer = pointer;
    this.status.hidden = false;
    this.#position.textContent = ` ${Math.round(pointer.x * 100)}% across, ${Math.round(pointer.y * 100)}% down.`;
    this.#place();
  }
  /**
   * Announce a hold or release after the server accepts it.
   * @param pointer - The pointer update accepted by the server.
   */
  confirm(pointer) {
    const message = pointer.active ? "Pointer held." : "Pointer released.";
    if (this.#state.textContent !== message) this.#state.textContent = message;
  }
  /**
   * Hide the marker and announce that pointer input has stopped.
   */
  stop() {
    this.#pointer = void 0;
    this.#marker.hidden = true;
    if (!this.status.hidden) this.#state.textContent = "Pointer controls stopped.";
  }
  #place() {
    const pointer = this.#pointer;
    if (!pointer || this.#image.hidden || document.activeElement !== this.#image) return;
    this.#marker.hidden = false;
    this.#marker.style.left = `${this.#image.offsetLeft + pointer.x * this.#image.clientWidth}px`;
    this.#marker.style.top = `${this.#image.offsetTop + pointer.y * this.#image.clientHeight}px`;
  }
};

// web/live/drag.ts
var DragInput = class {
  /**
   * Bind input until the panel's abort signal fires.
   * @param image - The output image that receives input.
   * @param signal - The panel's listener lifetime.
   * @param send - Receive pointer updates in normalized image coordinates.
   */
  constructor(image, signal, send) {
    this.image = image;
    this.send = send;
    image.tabIndex = 0;
    image.draggable = false;
    image.style.touchAction = "none";
    image.setAttribute(
      "aria-label",
      "Drag on the output to move the subject. Use arrow keys to position the pointer, Space to hold it, and Escape to release it."
    );
    image.addEventListener(
      "pointerdown",
      (event) => {
        if (event.button !== 0 || this.captured !== void 0) return;
        this.captured = event.pointerId;
        image.setPointerCapture(this.captured);
        image.focus();
        this.position(event);
      },
      { signal }
    );
    image.addEventListener(
      "pointermove",
      (event) => {
        if (this.captured === event.pointerId) this.position(event);
      },
      { signal }
    );
    for (const name of ["pointerup", "pointercancel", "lostpointercapture", "blur"])
      image.addEventListener(name, () => this.release(), { signal });
    image.addEventListener("keydown", (event) => this.keydown(event), { signal });
    image.addEventListener(
      "keyup",
      (event) => {
        if (event.key === " ") {
          event.preventDefault();
          event.stopPropagation();
          this.release();
        }
      },
      { signal }
    );
    window.addEventListener("blur", () => this.release(), { signal });
    document.addEventListener(
      "visibilitychange",
      () => {
        if (document.hidden) this.release();
      },
      { signal }
    );
    signal.addEventListener("abort", () => this.release(), { once: true });
  }
  image;
  send;
  pointer = { x: 0.5, y: 0.5, active: false };
  captured;
  /** Stop holding the pointer and release any browser pointer capture. */
  release() {
    const wasActive = this.pointer.active;
    this.pointer = { ...this.pointer, active: false };
    const previousCapture = this.captured;
    this.captured = void 0;
    if (wasActive) this.send(this.pointer);
    if (previousCapture !== void 0 && this.image.hasPointerCapture(previousCapture))
      this.image.releasePointerCapture(previousCapture);
  }
  /**
   * Normalize a drag event to the displayed image bounds.
   * @param event - The captured pointer event.
   */
  position(event) {
    const rect = this.image.getBoundingClientRect();
    this.pointer = {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
      active: true
    };
    this.send(this.pointer);
  }
  /**
   * Move, hold, or release the pointer with the keyboard.
   * @param event - A key pressed while the preview has focus.
   */
  keydown(event) {
    const offsets = {
      ArrowLeft: [-0.03, 0],
      ArrowRight: [0.03, 0],
      ArrowUp: [0, -0.03],
      ArrowDown: [0, 0.03],
      " ": [0, 0],
      Escape: [0, 0]
    };
    const offset = Object.hasOwn(offsets, event.key) ? offsets[event.key] : void 0;
    if (!offset) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.key === "Escape") {
      this.release();
      this.image.blur();
      return;
    }
    this.pointer = {
      x: Math.max(0, Math.min(1, this.pointer.x + offset[0])),
      y: Math.max(0, Math.min(1, this.pointer.y + offset[1])),
      active: event.key === " " || this.pointer.active
    };
    this.send(this.pointer);
  }
};

// web/live/controls.ts
var panels2 = /* @__PURE__ */ new Set();
var ControlPanel = class {
  /**
   * Build only the controls supported by this session.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(owner, fetcher) {
    this.owner = owner;
    this.fetcher = fetcher;
    this.dialog.className = "reactor-settings reactor-controls";
    this.dialog.setAttribute("aria-label", "Reactor live controls");
    this.image.alt = "Live model output";
    this.image.hidden = true;
    this.pointerPreview = owner.pointer ? new PointerPreview(this.image, this.abort.signal) : void 0;
    this.status.setAttribute("role", "status");
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.prompt_limit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.update.disabled = true;
    this.sound = owner.sound ? new SoundControls(owner.audio_prompt) : void 0;
    this.camera = owner.webcam ? new Webcam(owner, fetcher, (message) => this.stop(message)) : void 0;
    if (owner.pointer)
      new DragInput(this.image, this.abort.signal, (next) => this.queuePointer(next));
    this.bindActions();
    this.appendContent();
  }
  owner;
  fetcher;
  prior = document.activeElement;
  abort = new AbortController();
  dialog = element("dialog");
  image = element("img");
  status = element("p", "Choose your input, then start within 60 seconds.");
  prompt = element("textarea");
  start = button("Start session");
  update = button("Apply prompt");
  end = button("Cancel");
  pointerPreview;
  camera;
  sound;
  pointers = [];
  ending = false;
  finished = false;
  ready = false;
  sequence = 0;
  actionSequence = 0;
  previewSequence = 0;
  pendingPrompt;
  startRequested = false;
  startAttempted = false;
  /** Build the preview, supported inputs, and session actions. */
  appendContent() {
    this.dialog.append(
      element("h2", "Reactor live controls"),
      element("p", `${this.owner.modelTitle} · ${this.owner.duration_seconds} seconds of video`),
      element(
        "p",
        "Starting uses Reactor credits. Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound."
      )
    );
    if (this.camera) this.dialog.append(this.camera.view);
    this.dialog.append(this.pointerPreview?.view ?? this.image);
    if (this.owner.pointer)
      this.dialog.append(
        element(
          "p",
          "Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it."
        )
      );
    if (this.pointerPreview) this.dialog.append(this.pointerPreview.status);
    const label = element("label", "Scene prompt ");
    label.append(this.prompt);
    this.dialog.append(label, this.update);
    if (this.sound) this.dialog.append(this.sound.view);
    const footer = element("footer");
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(this.start, this.end);
    footer.append(this.status, actions);
    this.dialog.append(footer);
  }
  /** Bind start, prompt, stop, and dialog cleanup actions. */
  bindActions() {
    this.start.addEventListener("click", () => {
      this.startRequested = true;
      this.start.disabled = true;
    });
    this.update.addEventListener("click", () => {
      if (!this.prompt.value.trim() && this.owner.model !== "reactor/sana-streaming") {
        this.status.textContent = "Enter a prompt before applying it.";
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.update.disabled = true;
    });
    this.end.addEventListener("click", () => {
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener(
      "close",
      () => {
        this.stop();
        this.abort.abort();
        this.image.removeAttribute("src");
        this.dialog.remove();
        panels2.delete(this.owner.lease);
        if (this.prior instanceof HTMLElement && this.prior.isConnected) this.prior.focus();
      },
      { once: true }
    );
  }
  /**
   * Keep pointer releases while combining consecutive held moves.
   * @param next - The next normalized pointer update.
   */
  queuePointer(next) {
    if (!this.ready || this.ending) return;
    this.pointerPreview?.move(next);
    const previous = this.pointers.at(-1);
    if (previous?.active && next.active) this.pointers.pop();
    if (this.pointers.length >= 8) {
      this.stop("Pointer input arrived too quickly. The session is ending.");
      return;
    }
    this.pointers.push(next);
  }
  /**
   * Stop sending input while waiting for the server to end the session.
   * @param message - The reason shown in the panel.
   */
  stop(message = "Ending the session…") {
    this.ending = true;
    this.ready = false;
    this.start.disabled = this.update.disabled = true;
    this.sound?.setReady(false);
    this.pointerPreview?.stop();
    this.status.textContent = message;
    this.camera?.close();
  }
  /**
   * Apply current readiness and the latest preview.
   * @param reply - The validated session status.
   */
  display(reply) {
    const wasReady = this.ready;
    this.ready = reply.controls_ready && !reply.finishing && !this.ending;
    this.prompt.disabled = !this.ready;
    this.sound?.setReady(this.ready);
    if (this.ready && !wasReady) this.status.textContent = "Recording. Live controls are ready.";
    this.update.disabled = !this.ready || this.pendingPrompt !== void 0;
    if (reply.preview) {
      this.image.src = `data:image/jpeg;base64,${reply.preview}`;
      this.image.hidden = false;
    }
    this.previewSequence = reply.preview_sequence;
  }
  /**
   * Release devices and explain how the session ended.
   * @param reply - The terminal session status.
   */
  finish(reply) {
    this.finished = true;
    this.camera?.close();
    this.start.disabled = this.update.disabled = true;
    this.sound?.setReady(false);
    this.pointerPreview?.stop();
    if (!reply.termination_confirmed)
      this.status.textContent = "Connection closed. Check Reactor session status before starting again.";
    else if (!this.startAttempted)
      this.status.textContent = "Recording did not start. Close this panel to view the workflow result.";
    else
      this.status.textContent = reply.failed ? "The session ended without saving a video. Close this panel to view the workflow result." : "Session ended. Close this panel to view the workflow result.";
    this.end.textContent = "Close";
  }
  /**
   * Upload camera input and apply a requested start once a frame is ready.
   * @returns When this cycle's camera upload and start request finish.
   */
  async prepare() {
    const hasFrame = this.camera ? await this.camera.frame() : true;
    if (!this.startRequested) return;
    if (hasFrame) {
      this.startAttempted = true;
      await action(this.fetcher, this.owner, this.actionSequence++, "start", {});
      this.end.textContent = "End session";
      this.status.textContent = "Connecting to Reactor…";
    } else {
      this.status.textContent = "Enable a camera before starting.";
      this.start.disabled = false;
    }
    this.startRequested = false;
  }
  /**
   * Send queued prompt, pointer, and sound changes in order.
   * @returns When this cycle's pending controls have been sent.
   */
  async sendControls() {
    if (!this.ready) return;
    if (this.pendingPrompt !== void 0) {
      await action(this.fetcher, this.owner, this.actionSequence++, "prompt", {
        prompt: this.pendingPrompt
      });
      this.pendingPrompt = void 0;
      this.status.textContent = "Prompt sent. The model applies changes to later frames.";
    }
    const next = this.pointers.shift();
    if (next) {
      await action(this.fetcher, this.owner, this.actionSequence++, "pointer", next);
      this.pointerPreview?.confirm(next);
    }
    const audioPrompt = this.sound?.takePrompt();
    if (audioPrompt !== void 0) {
      await action(this.fetcher, this.owner, this.actionSequence++, "audio_prompt", {
        prompt: audioPrompt
      });
      this.status.textContent = "Sound prompt sent. The model applies changes to later audio.";
    }
  }
  /**
   * Read and display the session's current state.
   * @returns The validated session status.
   */
  async refresh() {
    const reply = await exchange(
      this.fetcher,
      this.owner,
      this.sequence++,
      {},
      this.ending,
      this.previewSequence,
      AbortSignal.timeout(2e3)
    );
    this.display(reply);
    return reply;
  }
  /**
   * Send input and check whether a rejection coincided with session completion.
   * @param reply - The status received before sending input.
   * @returns The current status after input is sent or recording ends.
   */
  async sendInput(reply) {
    try {
      await this.prepare();
      await this.sendControls();
      return reply;
    } catch (error) {
      const current5 = await this.refresh();
      if (!current5.closed && !current5.finishing) throw error;
      return current5;
    }
  }
  /**
   * Exchange status, apply pending input, and handle session completion.
   * @returns When one status and input cycle finishes.
   */
  async cycle() {
    let reply = await this.refresh();
    if (!this.ending && !reply.closed && !reply.finishing) reply = await this.sendInput(reply);
    if (reply.closed) this.finish(reply);
    else if (reply.finishing) {
      this.camera?.close();
      this.status.textContent = "Ending the session…";
    }
  }
  /**
   * Exchange status and input until the session ends or the panel closes.
   * @returns When polling ends and the panel shows its final state.
   */
  async poll() {
    try {
      while (!this.finished && !this.abort.signal.aborted) {
        await this.cycle();
        if (this.finished) break;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } catch (error) {
      this.stop(error instanceof Error ? error.message : "The live connection ended.");
      this.finished = true;
      this.end.textContent = "Close";
    }
  }
  /** Show the session panel and begin the local status exchange. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.start.focus();
    void this.poll();
  }
};
function openControls(value, fetcher) {
  const owner = controls(value);
  if (!owner || panels2.has(owner.lease)) return;
  panels2.add(owner.lease);
  const panel = new ControlPanel(owner, fetcher);
  panel.show();
}

// web/discovery/row.ts
function modelRow(model2, seconds) {
  const row = element("li");
  row.append(element("h3", model2.title), element("code", model2.name));
  const support = model2.support === "available" ? "Nodes available." : "No connector node available.";
  row.append(element("p", support));
  if (model2.connect_name) row.append(element("p", `Connect name: ${model2.connect_name}`));
  const rate = model2.credits_per_second === null ? "Rate not listed." : `${model2.credits_per_second} credits per session second.`;
  row.append(
    element("p", model2.observed ? rate : `${rate} Not observed in the latest source check.`)
  );
  if (model2.observed && model2.credits_per_second !== null && seconds !== void 0) {
    const credits = (model2.credits_per_second * seconds).toLocaleString(void 0, {
      maximumFractionDigits: 2
    });
    row.append(element("p", `${seconds} session seconds × listed rate = ${credits} credits.`));
  }
  if (model2.documentation_url) {
    const link = element("a", "Reactor model guide");
    link.href = model2.documentation_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    row.append(link);
  } else row.append(element("p", "No matching public guide was found."));
  return row;
}

// web/discovery/api.ts
var INVALID_MODEL_LIST = "ComfyUI returned an invalid Reactor model list.";
function record2(value) {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error(INVALID_MODEL_LIST);
  return value;
}
function shortText(value, max = 200) {
  return typeof value === "string" && value.length > 0 && value.length <= max;
}
function model(value) {
  const row = record2(value);
  if (!shortText(row.key) || !shortText(row.name) || !shortText(row.title) || !(row.connect_name === null || shortText(row.connect_name)) || !(row.documentation_url === null || typeof row.documentation_url === "string" && /^https:\/\/docs\.reactor\.inc\/model-api-reference\/[a-z0-9._-]+\/overview$/.test(
    row.documentation_url
  )) || !(row.credits_per_second === null || typeof row.credits_per_second === "number" && Number.isFinite(row.credits_per_second) && row.credits_per_second >= 0) || typeof row.observed !== "boolean" || !["available", "adapter_required"].includes(String(row.support)) || !Array.isArray(row.node_ids) || row.node_ids.length > 100 || !row.node_ids.every((id) => typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id)))
    throw new Error(INVALID_MODEL_LIST);
  return row;
}
function parseCatalog(value) {
  const document2 = record2(value);
  if (typeof document2.revision !== "string" || !/^[a-f0-9]{64}$/.test(document2.revision) || !shortText(document2.retrieved_at, 40) || !Number.isFinite(Date.parse(document2.retrieved_at)) || typeof document2.can_rollback !== "boolean" || typeof document2.mutation_allowed !== "boolean" || !Array.isArray(document2.models) || document2.models.length < 1 || document2.models.length > 1024)
    throw new Error(INVALID_MODEL_LIST);
  const models = document2.models.map(model);
  if (document2.automatic_check !== void 0) {
    const check = record2(document2.automatic_check);
    if (typeof check.enabled !== "boolean" || typeof check.running !== "boolean" || typeof check.interval_hours !== "number" || !Number.isInteger(check.interval_hours) || check.interval_hours < 1 || check.interval_hours > 3600 || !(check.checked_at === null || shortText(check.checked_at, 40) && Number.isFinite(Date.parse(check.checked_at))) || !(check.update_available === null || typeof check.update_available === "boolean") || !(check.error === null || shortText(check.error, 1024)))
      throw new Error(INVALID_MODEL_LIST);
  }
  if (new Set(models.map((row) => row.key)).size !== models.length)
    throw new Error(INVALID_MODEL_LIST);
  return { ...document2, models };
}
async function requestModels(fetcher, signal, action2, revision) {
  const options = {
    method: action2 === "read" ? "GET" : "POST",
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([signal, AbortSignal.timeout(3e4)]),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" }
  };
  if (action2 === "rollback") options.body = JSON.stringify({ revision });
  const suffix = action2 === "read" ? "" : `/${action2}`;
  let response;
  try {
    response = await fetcher(`/reactor-inc/v1/catalog${suffix}`, options);
  } catch {
    throw new Error("Cannot reach the Reactor model list. Check ComfyUI and try again.");
  }
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error(INVALID_MODEL_LIST);
  }
  if (!response.ok) {
    const error = record2(body).error;
    throw new Error(shortText(error, 1024) ? error : "The catalog request failed.");
  }
  return parseCatalog(body);
}

// web/discovery/dialog.ts
var current;
function automaticStatus(check) {
  if (!check) return "";
  if (!check.enabled) return "Automatic model checks are off. Change this in Reactor settings.";
  if (check.running)
    return "An automatic model check is running. Reopen this list to see its result.";
  if (check.error) return check.error;
  if (check.update_available === true)
    return "The model list has changed. Select Refresh models to update your list.";
  if (check.checked_at)
    return `Automatic check: ${new Date(check.checked_at).toLocaleString()}. Checks run every ${check.interval_hours} hours.`;
  return "An automatic model check is due. Checks do not change this list.";
}
var ModelDialog = class {
  /**
   * Build the model browser and its optional node filter.
   * @param fetcher - ComfyUI's local API client.
   * @param nodeId - Show models supported by this node, if supplied.
   */
  constructor(fetcher, nodeId2) {
    this.fetcher = fetcher;
    this.nodeId = nodeId2;
    this.dialog.className = "reactor-settings reactor-catalog";
    this.dialog.setAttribute("aria-labelledby", "reactor-catalog-title");
    const heading = element("h2", "Reactor models");
    heading.id = "reactor-catalog-title";
    const close = button("Close");
    close.setAttribute("aria-label", "Close Reactor models");
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(heading, close);
    const searchLabel = element("label", "Search models");
    this.search.type = "search";
    this.search.placeholder = "Name or connect name";
    searchLabel.append(this.search);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.list.setAttribute("aria-label", "Reactor models");
    const sources = element("details");
    sources.append(
      element("summary", "Model sources and automatic checks"),
      this.checked,
      this.automatic
    );
    this.dialog.append(
      header,
      element(
        "p",
        "Refresh checks Reactor's public model list and prices. It sends no API key and uses no credits. New models need a compatible connector node."
      ),
      this.actions(),
      this.status,
      searchLabel,
      this.calculation(),
      sources,
      this.count,
      this.list
    );
    this.search.addEventListener("input", () => this.render());
    this.duration.addEventListener("input", () => this.render());
    this.dialog.addEventListener("close", () => this.dispose(), { once: true });
  }
  fetcher;
  nodeId;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  search = element("input");
  duration = element("input");
  refresh = button("Refresh models");
  rollback = button("Restore previous list");
  status = element("p", "Loading the local model list…");
  checked = element("p");
  automatic = element("p");
  count = element("p");
  list = element("ul");
  catalog;
  /**
   * Build list updates and the node filter reset.
   * @returns The model browser actions.
   */
  actions() {
    const showAll = button("Show all models");
    showAll.hidden = !this.nodeId;
    showAll.addEventListener("click", () => {
      this.nodeId = void 0;
      showAll.hidden = true;
      this.render();
    });
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener("click", () => void this.perform("refresh"));
    this.rollback.addEventListener("click", () => void this.perform("rollback"));
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(this.refresh, this.rollback, showAll);
    return actions;
  }
  /**
   * Build the optional session time calculation.
   * @returns The collapsed calculation controls.
   */
  calculation() {
    const label = element("label", "Session time to calculate (seconds)");
    this.duration.type = "number";
    this.duration.min = "0.1";
    this.duration.max = "3600";
    this.duration.step = "any";
    this.duration.placeholder = "Enter total paid session time";
    label.append(this.duration);
    const calculation = element("details");
    calculation.append(
      element("summary", "Calculate credits for session time"),
      label,
      element(
        "p",
        "Use total session time, including setup, pauses, and recording. Saved video length may be shorter. This estimate is not a spending limit or a quote."
      )
    );
    return calculation;
  }
  /** Update matching models and calculations from the current controls. */
  render() {
    const query = this.search.value.trim().toLowerCase();
    const nodeId2 = this.nodeId;
    const visible = this.catalog?.models.filter(
      (model2) => (!nodeId2 || model2.node_ids.includes(nodeId2)) && `${model2.name} ${model2.title} ${model2.connect_name ?? ""}`.toLowerCase().includes(query)
    ) ?? [];
    const seconds = this.duration.validity.valid && this.duration.value !== "" ? this.duration.valueAsNumber : void 0;
    this.list.replaceChildren(...visible.map((model2) => modelRow(model2, seconds)));
    this.count.textContent = `${visible.length} of ${this.catalog?.models.length ?? 0} catalog entries`;
  }
  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   * @returns When the model list or error is displayed.
   */
  async perform(action2) {
    this.refresh.disabled = this.rollback.disabled = true;
    this.status.textContent = action2 === "refresh" ? "Checking public model sources…" : "Loading model list…";
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action2,
        this.catalog?.revision
      );
      if (this.controller.signal.aborted) return;
      this.catalog = next;
      this.checked.textContent = `Last source check: ${new Date(next.retrieved_at).toLocaleString()}. Your Reactor account determines which models you can use.`;
      this.automatic.textContent = automaticStatus(next.automatic_check);
      this.status.textContent = {
        refresh: "Model list refreshed. No generation started.",
        rollback: "Previous model list restored. This does not change which models Reactor offers.",
        read: "Local model list loaded."
      }[action2];
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : "Cannot load models.";
    } finally {
      this.restoreActions();
    }
  }
  /** Re-enable allowed list changes after the current request finishes. */
  restoreActions() {
    if (this.controller.signal.aborted) return;
    this.refresh.disabled = !this.catalog?.mutation_allowed;
    this.rollback.disabled = !this.catalog?.mutation_allowed || !this.catalog.can_rollback;
  }
  /** Show the dialog and read the local model list. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.perform("read");
  }
  /** Stop pending requests and return focus to the caller. */
  dispose() {
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openModels(fetcher, nodeId2) {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new ModelDialog(fetcher, nodeId2);
  current.show();
}

// web/settings/rate.ts
function requestedSeconds(node) {
  function value(name) {
    if (node.inputs?.some((input) => input.name === name && input.link != null)) return void 0;
    const raw = node.widgets?.find((widget) => widget.name === name)?.value;
    return typeof raw === "number" && Number.isFinite(raw) && raw > 0 ? raw : void 0;
  }
  if (node.comfyClass === "ReactorIncFastContinue") {
    const seconds = value("clip_seconds");
    const count = value("clip_count");
    return seconds !== void 0 && count !== void 0 ? seconds * count : void 0;
  }
  return value("duration_seconds");
}
var current2;
var CreditDialog = class {
  /**
   * Build the calculator for a node.
   * @param node - The node whose public rate is requested.
   */
  constructor(node) {
    this.node = node;
    this.dialog.className = "reactor-settings";
    this.dialog.setAttribute("aria-labelledby", "reactor-rate-title");
    const title = element("h2", "Credit rate");
    title.id = "reactor-rate-title";
    const close = button("Close");
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(title, close);
    const seconds = requestedSeconds(node);
    const request = element(
      "p",
      seconds === void 0 ? "The video length comes from a connected input or is not available. Enter a session time below to calculate credits." : `This node requests ${seconds.toLocaleString()} seconds of video. Setup, pauses, and recording can add paid time.`
    );
    const label = element("label", "Session time to calculate (seconds)");
    this.duration.type = "number";
    this.duration.min = "0.1";
    this.duration.max = "3600";
    this.duration.step = "any";
    this.duration.placeholder = "Enter total paid session time";
    if (seconds !== void 0) this.duration.value = String(seconds);
    label.append(this.duration);
    this.validation.setAttribute("role", "status");
    this.status.setAttribute("role", "status");
    this.rates.setAttribute("aria-live", "polite");
    this.dialog.append(
      header,
      request,
      label,
      this.validation,
      element(
        "p",
        "This is rate × time, not an exact charge or a spending limit. The starting time uses the requested video length and excludes extra paid time. Your Reactor account shows actual charges."
      ),
      this.status,
      this.rates
    );
    this.duration.addEventListener("input", () => this.render());
    this.dialog.addEventListener("close", () => this.dispose(), { once: true });
    this.render();
  }
  node;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  duration = element("input");
  validation = element("p");
  status = element("p", "Loading the local credit rate…");
  rates = element("div");
  models = [];
  /**
   * Read public rates from the local model list.
   * @param fetcher - ComfyUI's local API client.
   * @returns When rates or an error are displayed.
   */
  async readRates(fetcher) {
    try {
      const catalog = await requestModels(fetcher, this.controller.signal, "read");
      if (this.controller.signal.aborted) return;
      this.models = catalog.models.filter(
        (model2) => model2.node_ids.includes(this.node.comfyClass ?? "")
      );
      this.status.textContent = `Rates checked ${new Date(catalog.retrieved_at).toLocaleString()}.`;
      if (!this.models.length)
        this.status.textContent = "No rate is listed for this node. Open the ComfyUI menu, then Extensions → Reactor → Reactor models, and refresh the list.";
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : "Cannot load the credit rate.";
    }
  }
  /** Validate session time and update every rate calculation. */
  render() {
    const valid = this.duration.value !== "" && this.duration.validity.valid;
    this.validation.textContent = valid ? "" : "Enter a session time from 0.1 to 3,600 seconds.";
    this.rates.replaceChildren();
    for (const model2 of this.models) {
      this.rates.append(element("h3", model2.title));
      const rate = model2.credits_per_second;
      if (!model2.observed || rate === null) {
        this.rates.append(
          element(
            "p",
            "A current rate is not available. Refresh Reactor models before relying on a calculation."
          )
        );
        continue;
      }
      this.rates.append(element("p", `${rate.toLocaleString()} credits per session second.`));
      if (valid) {
        const total = (rate * this.duration.valueAsNumber).toLocaleString(void 0, {
          maximumFractionDigits: 2
        });
        this.rates.append(
          element(
            "p",
            `${this.duration.valueAsNumber.toLocaleString()} seconds × ${rate.toLocaleString()} = ${total} credits.`
          )
        );
      }
    }
  }
  /**
   * Show the calculator and read local rates.
   * @param fetcher - ComfyUI's local API client.
   */
  show(fetcher) {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.readRates(fetcher);
  }
  /** Stop the request and return focus to the caller. */
  dispose() {
    this.controller.abort();
    this.dialog.remove();
    if (current2 === this) current2 = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openCreditRate(node, fetcher) {
  if (current2?.dialog.open) {
    current2.dialog.focus();
    return;
  }
  current2 = new CreditDialog(node);
  current2.show(fetcher);
}
function bindCreditRate(node, fetcher) {
  const id = node.comfyClass;
  if (!id?.startsWith("ReactorInc") || id === "ReactorIncHeliosAddPrompt" || id === "ReactorIncLongLiveAddShot")
    return;
  node.addWidget("button", "View credit rate", "", () => openCreditRate(node, fetcher), {
    serialize: false
  });
}

// web/settings/api.ts
var fields = [
  ["max_capture_seconds", "Maximum video duration (seconds)"],
  ["max_session_seconds", "Maximum session duration (seconds)"],
  ["connect_timeout_seconds", "Connection timeout (seconds)"],
  ["first_frame_timeout_seconds", "First-frame timeout (seconds)"],
  ["cleanup_timeout_seconds", "Disconnect timeout (seconds)"],
  ["queue_timeout_seconds", "Queue wait timeout (seconds)"],
  ["max_upload_megabytes", "Maximum upload size (MiB)"],
  ["max_capture_megabytes", "Maximum video file size (MiB)"],
  ["max_queue_megabytes", "Maximum queued frame data (MiB)"]
];
function record3(value) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("ComfyUI returned an invalid Reactor settings response.");
  }
  return value;
}
function parseConfiguration(value) {
  const document2 = record3(value);
  const settings = record3(document2.settings);
  const credential = record3(document2.credential);
  if (typeof document2.revision !== "string" || !/^[a-f0-9]{64}$/.test(document2.revision) || typeof document2.mutation_allowed !== "boolean" || typeof credential.source !== "string" || !["missing", "saved", "environment"].includes(credential.source)) {
    throw new Error("ComfyUI returned an invalid Reactor settings response.");
  }
  if (typeof settings.catalog_auto_check !== "boolean" || typeof settings.catalog_interval_hours !== "number" || !Number.isInteger(settings.catalog_interval_hours) || settings.catalog_interval_hours < 1 || settings.catalog_interval_hours > 3600)
    throw new Error("ComfyUI returned invalid model check settings.");
  const validated = {
    catalog_auto_check: settings.catalog_auto_check,
    catalog_interval_hours: settings.catalog_interval_hours
  };
  for (const [name] of fields) {
    const value2 = settings[name];
    if (typeof value2 !== "number" || !Number.isInteger(value2) || value2 < 1 || value2 > 3600) {
      throw new Error("ComfyUI returned an invalid Reactor limit.");
    }
    validated[name] = value2;
  }
  return {
    revision: document2.revision,
    credentialSource: credential.source,
    mutationAllowed: document2.mutation_allowed,
    settings: validated
  };
}
async function requestConfiguration(fetcher, signal, route = "/status", method = "GET", body) {
  const options = {
    method,
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([signal, AbortSignal.timeout(1e4)]),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" }
  };
  if (body !== void 0) options.body = JSON.stringify(body);
  let response;
  try {
    response = await fetcher(`/reactor-inc/v1${route}`, options);
  } catch {
    throw new Error("Cannot reach Reactor settings. Check ComfyUI and try again.");
  }
  let document2;
  try {
    document2 = await response.json();
  } catch {
    throw new Error("ComfyUI returned an unreadable Reactor settings response.");
  }
  if (!response.ok) {
    const error = record3(document2).error;
    throw new Error(
      typeof error === "string" && error.length <= 1024 ? error : "ComfyUI could not save Reactor settings."
    );
  }
  return parseConfiguration(document2);
}

// web/settings/dialog.ts
var current3;
var SettingsDialog = class {
  /**
   * Build settings forms without contacting Reactor.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(fetcher) {
    this.fetcher = fetcher;
    this.dialog.className = "reactor-settings";
    this.dialog.setAttribute("aria-labelledby", "reactor-settings-title");
    const heading = element("h2", "Reactor settings");
    heading.id = "reactor-settings-title";
    const close = button("Close");
    close.setAttribute("aria-label", "Close Reactor settings");
    close.addEventListener("click", () => this.dialog.close());
    const header = element("header");
    header.append(heading, close);
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.reload.addEventListener("click", () => void this.perform("Local settings loaded."));
    this.dialog.append(
      header,
      element(
        "p",
        "Reactor uses its own account and credits. Opening settings and saving a key do not start generation."
      ),
      this.source,
      this.credentials(),
      element(
        "p",
        "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here."
      ),
      this.limits(),
      element(
        "p",
        "Session time includes setup and generation. These limits do not buy credits or change account billing."
      ),
      this.modelUpdates(),
      this.status,
      this.reload
    );
    this.dialog.addEventListener("close", () => this.dispose(), { once: true });
  }
  fetcher;
  dialog = element("dialog");
  previousFocus = document.activeElement;
  controller = new AbortController();
  status = element("p", "Loading local settings…");
  source = element("p");
  reload = button("Reload settings");
  key = element("input");
  keyFields = element("fieldset");
  limitFields = element("fieldset");
  catalogFields = element("fieldset");
  automatic = element("input");
  interval = element("input");
  inputs = /* @__PURE__ */ new Map();
  configuration;
  /**
   * Build the private key form.
   * @returns The form for saving or clearing the server's key.
   */
  credentials() {
    const form = element("form");
    this.keyFields.disabled = true;
    const label = element("label", "Reactor API key");
    this.key.type = "password";
    this.key.autocomplete = "off";
    this.key.spellcheck = false;
    this.key.maxLength = 1024;
    this.key.required = true;
    label.append(this.key);
    const clear = button("Clear saved key");
    clear.addEventListener("click", () => {
      this.key.value = "";
      void this.perform(
        "Saved key cleared. Any environment key remains active.",
        "/credential",
        "DELETE"
      );
    });
    const actions = element("div");
    actions.className = "reactor-actions";
    actions.append(button("Save key", "submit"), clear);
    this.keyFields.append(element("legend", "Credentials"), label, actions);
    form.append(this.keyFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.key.value = "";
      void this.perform(
        "Key saved on this server. Reactor checks it when you start a session.",
        "/credential",
        "PUT",
        { api_key: value }
      );
    });
    return form;
  }
  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  limits() {
    const form = element("form");
    this.limitFields.disabled = true;
    this.limitFields.append(element("legend", "Execution limits"));
    const advanced = element("details");
    advanced.append(element("summary", "Advanced limits"));
    for (const [index, [name, title]] of fields.entries()) {
      const label = element("label", title);
      const input = element("input");
      input.type = "number";
      input.min = "1";
      input.max = "3600";
      input.step = "1";
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      (index < 2 ? this.limitFields : advanced).append(label);
    }
    this.limitFields.append(advanced, button("Save limits", "submit"));
    form.append(this.limitFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }
  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  saveLimits(configuration) {
    const changes = {};
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== configuration.settings[name]) changes[name] = input.valueAsNumber;
    }
    if (Object.keys(changes).length === 0) {
      this.status.textContent = "No limit changes to save.";
      return;
    }
    void this.perform("Limits saved. They apply to new executions.", "/settings", "PATCH", {
      revision: configuration.revision,
      settings: changes
    });
  }
  /**
   * Build the controls for checking public model sources.
   * @returns The automatic model check form.
   */
  modelUpdates() {
    const form = element("form");
    this.catalogFields.disabled = true;
    const automaticLabel = element("label", "Check for model updates automatically");
    this.automatic.type = "checkbox";
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element("label", "Check interval (hours)");
    this.interval.type = "number";
    this.interval.min = "1";
    this.interval.max = "3600";
    this.interval.step = "1";
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.catalogFields.append(
      element("legend", "Model updates"),
      automaticLabel,
      intervalLabel,
      element(
        "p",
        "Checks read public prices and model guides. They do not use your key or spend credits. Open Reactor models to see changes and refresh your list."
      ),
      button("Save model check settings", "submit")
    );
    form.append(this.catalogFields);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveModelUpdates(this.configuration);
    });
    return form;
  }
  /**
   * Save automatic checks without changing the displayed model list.
   * @param configuration - The settings and revision currently shown.
   */
  saveModelUpdates(configuration) {
    const settings = {
      catalog_auto_check: this.automatic.checked,
      catalog_interval_hours: this.interval.valueAsNumber
    };
    if (settings.catalog_auto_check === configuration.settings.catalog_auto_check && settings.catalog_interval_hours === configuration.settings.catalog_interval_hours) {
      this.status.textContent = "No model check changes to save.";
      return;
    }
    void this.perform(
      "Model check settings saved. The scheduler reads changes within one minute.",
      "/settings",
      "PATCH",
      { revision: configuration.revision, settings }
    );
  }
  /**
   * Show validated settings and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  display(configuration) {
    this.configuration = configuration;
    this.source.textContent = {
      missing: "No Reactor key is configured.",
      saved: "A saved key is configured on this server.",
      environment: "The server's REACTOR_API_KEY environment variable is active."
    }[configuration.credentialSource];
    this.automatic.checked = configuration.settings.catalog_auto_check;
    this.interval.value = String(configuration.settings.catalog_interval_hours);
    for (const [name, input] of this.inputs) input.value = String(configuration.settings[name]);
    if (!configuration.mutationAllowed)
      this.status.textContent = "Changes are disabled in this host's multi-user mode.";
  }
  /**
   * Keep settings requests serial and show the server's response.
   * @param message - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  async perform(message, route, method, body) {
    this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = true;
    this.reload.disabled = true;
    this.status.textContent = "Working…";
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body
      );
      if (this.controller.signal.aborted) return;
      this.status.textContent = message;
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : "Reactor settings could not be saved.";
    } finally {
      if (!this.controller.signal.aborted) {
        this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = !this.configuration?.mutationAllowed;
        this.reload.disabled = false;
      }
    }
  }
  /** Show the dialog and read local settings. */
  show() {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.perform("Local settings loaded.");
  }
  /** Clear the key input, stop requests, and return focus to the caller. */
  dispose() {
    this.key.value = "";
    this.controller.abort();
    this.dialog.remove();
    if (current3 === this) current3 = void 0;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
};
function openSettings(fetcher) {
  if (current3?.dialog.open) {
    current3.dialog.focus();
    return;
  }
  current3 = new SettingsDialog(fetcher);
  current3.show();
}

// web/nodes/labels.ts
function configureNodeWidgets(node) {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  const control = node.widgets?.find((widget) => widget.name === "control_after_generate");
  if (control) control.label = "Seed behavior";
  for (const widget of node.widgets ?? []) {
    if (typeof widget.options?.advanced !== "boolean") continue;
    const connected = node.inputs?.some(
      (input) => input.name === widget.name && input.link != null
    );
    widget.advanced = widget.options.advanced && !connected;
  }
}
function bindNodeWidgets(node) {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  configureNodeWidgets(node);
  const changed = node.onConnectionsChange;
  node.onConnectionsChange = function(...args) {
    changed?.apply(this, args);
    configureNodeWidgets(node);
  };
}

// web/help/command.ts
import { app } from "../../scripts/app.js";

// web/help/dialog.ts
var current4;
function openHelpDialog(nodeId2) {
  current4?.close();
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  current4 = dialog;
  dialog.className = "reactor-settings reactor-node-help";
  dialog.setAttribute("aria-labelledby", "reactor-node-help-title");
  const heading = element("h2", "Node help");
  heading.id = "reactor-node-help-title";
  const close = button("Close");
  close.setAttribute("aria-label", "Close node help");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const frame = element("iframe");
  frame.title = "Reactor node guide";
  frame.sandbox.add(
    "allow-same-origin",
    "allow-popups",
    "allow-popups-to-escape-sandbox",
    "allow-downloads"
  );
  frame.src = `/extensions/reactor-inc/guides/nodes/${nodeId2}.html`;
  frame.addEventListener("load", () => prepareGuide(frame, dialog, controller.signal));
  dialog.append(header, frame);
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      if (current4 === dialog) current4 = void 0;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true }
  );
  document.body.append(dialog);
  dialog.showModal();
  close.focus();
}
function prepareGuide(frame, dialog, signal) {
  const guide = frame.contentDocument;
  if (!guide) return;
  const colors = getComputedStyle(dialog);
  guide.body.style.background = colors.backgroundColor;
  guide.body.style.color = colors.color;
  for (const link of guide.querySelectorAll("a")) {
    link.style.color = "inherit";
    if (new URL(link.href).origin !== location.origin) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  }
  for (const block of guide.querySelectorAll("pre")) {
    block.style.background = colors.getPropertyValue("--comfy-input-bg") || colors.backgroundColor;
  }
  guide.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        dialog.close();
      }
    },
    { signal }
  );
}

// web/help/command.ts
var HELP_COMMAND = "ReactorInc.OpenNodeHelp";
function nodeId(item) {
  if (typeof item !== "object" || item === null || !("comfyClass" in item)) return;
  const id = item.comfyClass;
  return typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id) ? id : void 0;
}
function helpCommands(item) {
  if (!nodeId(item)) return [];
  return [HELP_COMMAND];
}
function openNodeHelp() {
  const id = Array.from(app.canvas.selectedItems ?? []).map(nodeId).find(Boolean);
  if (!id) return;
  openHelpDialog(id);
}

// web/extension.ts
var stylesheet = document.createElement("link");
stylesheet.rel = "stylesheet";
stylesheet.href = new URL("./main.css", import.meta.url).href;
document.head.append(stylesheet);
api.addEventListener("reactor-inc.live", (event) => {
  if (event instanceof CustomEvent) {
    openLive(event.detail, (route, options) => api.fetchApi(route, options));
  }
});
api.addEventListener("reactor-inc.controls", (event) => {
  if (event instanceof CustomEvent)
    openControls(event.detail, (route, options) => api.fetchApi(route, options));
});
app2.registerExtension({
  name: "reactor.inc.configuration",
  // eslint-disable-next-line local/no-trivial-functions -- ComfyUI calls this hook once to attach labels and the credit rate button.
  nodeCreated: (node) => {
    bindNodeWidgets(node);
    bindCreditRate(node, (route, options) => api.fetchApi(route, options));
  },
  loadedGraphNode: configureNodeWidgets,
  getSelectionToolboxCommands: helpCommands,
  commands: [
    {
      id: HELP_COMMAND,
      label: "Help",
      icon: "pi pi-question-circle",
      function: openNodeHelp
    },
    {
      id: "ReactorInc.OpenSettings",
      label: "Reactor settings",
      function: () => openSettings((route, options) => api.fetchApi(route, options))
    },
    {
      id: "ReactorInc.OpenCatalog",
      label: "Reactor models",
      function: () => openModels((route, options) => api.fetchApi(route, options))
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "Reactor"],
      commands: ["ReactorInc.OpenSettings", "ReactorInc.OpenCatalog"]
    }
  ]
});
