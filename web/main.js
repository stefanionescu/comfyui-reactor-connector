// Generated from frontend source. Run mise run frontend:build.
// frontend/extension.ts
import { api } from "../../scripts/api.js";
import { app as app2 } from "../../scripts/app.js";

// frontend/catalog-api.ts
function invalid() {
  return new Error("ComfyUI returned an invalid Reactor model list.");
}
function record(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw invalid();
  return value;
}
function shortText(value, max = 200) {
  return typeof value === "string" && value.length > 0 && value.length <= max;
}
function model(value) {
  const row = record(value);
  if (!shortText(row.key) || !shortText(row.name) || !shortText(row.title) || !(row.connect_name === null || shortText(row.connect_name)) || !(row.documentation_url === null || typeof row.documentation_url === "string" && /^https:\/\/docs\.reactor\.inc\/model-api-reference\/[a-z0-9._-]+\/overview$/.test(
    row.documentation_url
  )) || !(row.credits_per_second === null || typeof row.credits_per_second === "number" && Number.isFinite(row.credits_per_second) && row.credits_per_second >= 0) || typeof row.observed !== "boolean" || !["available", "adapter_required"].includes(String(row.support)) || !Array.isArray(row.node_ids) || row.node_ids.length > 100 || !row.node_ids.every((id) => typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id)))
    throw invalid();
  return row;
}
function parseCatalog(value) {
  const document2 = record(value);
  if (typeof document2.revision !== "string" || !/^[a-f0-9]{64}$/.test(document2.revision) || !shortText(document2.retrieved_at, 40) || !Number.isFinite(Date.parse(document2.retrieved_at)) || typeof document2.can_rollback !== "boolean" || typeof document2.mutation_allowed !== "boolean" || !Array.isArray(document2.models) || document2.models.length < 1 || document2.models.length > 1024)
    throw invalid();
  const models = document2.models.map(model);
  if (document2.automatic_check !== void 0) {
    const check = record(document2.automatic_check);
    if (typeof check.enabled !== "boolean" || typeof check.running !== "boolean" || typeof check.interval_hours !== "number" || !Number.isInteger(check.interval_hours) || check.interval_hours < 1 || check.interval_hours > 3600 || !(check.checked_at === null || shortText(check.checked_at, 40) && Number.isFinite(Date.parse(check.checked_at))) || !(check.update_available === null || typeof check.update_available === "boolean") || !(check.error === null || shortText(check.error, 1024)))
      throw invalid();
  }
  if (new Set(models.map((row) => row.key)).size !== models.length) throw invalid();
  return { ...document2, models };
}
async function requestCatalog(fetcher, signal, action2, revision) {
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
    throw invalid();
  }
  if (!response.ok) {
    const error = record(body).error;
    throw new Error(shortText(error, 1024) ? error : "The catalog request failed.");
  }
  return parseCatalog(body);
}

// frontend/dom.ts
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

// frontend/styles.ts
var settingsStyles = `
.reactor-settings {
  width: min(38rem, calc(100vw - 2rem));
  max-height: calc(100vh - 2rem);
  overflow: auto;
  border: 1px solid var(--border-color, GrayText);
  border-radius: .6rem;
  padding: 1.5rem;
  color: var(--fg-color, CanvasText);
  background: var(--comfy-menu-bg, Canvas);
  font: inherit;
}
.reactor-settings::backdrop { background: #0008; }
.reactor-settings header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.reactor-settings h2 { margin: 0; font-size: 1.3rem; }
.reactor-settings p { line-height: 1.5; }
.reactor-settings form { margin-top: 1.5rem; }
.reactor-settings fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
.reactor-settings legend { font-weight: 600; margin-bottom: .75rem; }
.reactor-settings label { display: grid; gap: .35rem; margin: .8rem 0; }
.reactor-settings input {
  box-sizing: border-box; width: 100%; padding: .55rem; border: 1px solid var(--border-color, GrayText);
  border-radius: .25rem; color: var(--input-text, CanvasText); background: var(--comfy-input-bg, Field);
  font: inherit;
}
.reactor-settings button {
  font: inherit; padding: .45rem .75rem; border: 1px solid var(--border-color, GrayText);
  border-radius: .25rem; color: var(--input-text, ButtonText); background: var(--comfy-input-bg, ButtonFace);
  cursor: pointer;
}
.reactor-settings input[type="checkbox"] { width: auto; padding: 0; margin: 0; }
.reactor-settings label:has(input[type="checkbox"]) { display: flex; align-items: center; gap: .6rem; }
.reactor-settings button:disabled { cursor: default; opacity: .55; }
.reactor-settings :focus-visible { outline: 2px solid Highlight; outline-offset: 3px; }
.reactor-settings .reactor-actions { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: .75rem; }
.reactor-settings [role="status"] { min-height: 1.5em; }
.reactor-settings summary { cursor: pointer; padding: .5rem 0; }
`;

// frontend/catalog.ts
var currentDialog;
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
function openCatalog(fetcher, nodeId2) {
  if (currentDialog?.open) {
    currentDialog.focus();
    return;
  }
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  currentDialog = dialog;
  dialog.className = "reactor-settings reactor-catalog";
  dialog.setAttribute("aria-labelledby", "reactor-catalog-title");
  const styles = element(
    "style",
    `${settingsStyles}
    .reactor-catalog { box-sizing: border-box; width: min(54rem, calc(100vw - 2rem)); }
    .reactor-catalog ul { list-style: none; padding: 0; }
    .reactor-catalog li { border-top: 1px solid var(--border-color, GrayText); padding: 1rem 0; }
    .reactor-catalog h3 { margin: 0 0 .4rem; }
    .reactor-catalog li p { margin: .35rem 0; }
    .reactor-catalog code { overflow-wrap: anywhere; }
    .reactor-catalog details { margin: .75rem 0; }
  `
  );
  const heading = element("h2", "Reactor models");
  heading.id = "reactor-catalog-title";
  const close = button("Close");
  close.setAttribute("aria-label", "Close Reactor models");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const searchLabel = element("label", "Search models");
  const search = element("input");
  search.type = "search";
  search.placeholder = "Name or connect name";
  searchLabel.append(search);
  const durationLabel = element("label", "Session time to calculate (seconds)");
  const duration = element("input");
  duration.type = "number";
  duration.min = "0.1";
  duration.max = "3600";
  duration.step = "any";
  duration.placeholder = "Enter total paid session time";
  durationLabel.append(duration);
  const showAll = button("Show all models");
  showAll.hidden = !nodeId2;
  showAll.addEventListener("click", () => {
    nodeId2 = void 0;
    showAll.hidden = true;
    render();
  });
  const refresh = button("Refresh models");
  const rollback = button("Restore previous list");
  refresh.disabled = rollback.disabled = true;
  const actions = element("div");
  actions.className = "reactor-actions";
  actions.append(refresh, rollback, showAll);
  const status = element("p", "Loading the local model list…");
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  const checked = element("p");
  const automatic = element("p");
  const count = element("p");
  const list = element("ul");
  list.setAttribute("aria-label", "Reactor models");
  const calculation = element("details");
  calculation.append(
    element("summary", "Calculate credits for session time"),
    durationLabel,
    element(
      "p",
      "Use total session time, including setup, pauses, and recording. Saved video length may be shorter. This estimate is not a spending limit or a quote."
    )
  );
  const sources = element("details");
  sources.append(element("summary", "Model sources and automatic checks"), checked, automatic);
  dialog.append(
    header,
    element(
      "p",
      "Refresh checks Reactor's public model list and prices. It sends no API key and uses no credits. New models need a compatible connector node."
    ),
    actions,
    status,
    searchLabel,
    calculation,
    sources,
    count,
    list
  );
  let catalog;
  function render() {
    const query = search.value.trim().toLowerCase();
    const visible = catalog?.models.filter(
      (model2) => (!nodeId2 || model2.node_ids.includes(nodeId2)) && `${model2.name} ${model2.title} ${model2.connect_name ?? ""}`.toLowerCase().includes(query)
    ) ?? [];
    const seconds = duration.validity.valid && duration.value !== "" ? duration.valueAsNumber : void 0;
    list.replaceChildren(...visible.map((model2) => modelRow(model2, seconds)));
    count.textContent = `${visible.length} of ${catalog?.models.length ?? 0} catalog entries`;
  }
  async function perform(action2) {
    refresh.disabled = rollback.disabled = true;
    status.textContent = action2 === "refresh" ? "Checking public model sources…" : "Loading model list…";
    try {
      const next = await requestCatalog(fetcher, controller.signal, action2, catalog?.revision);
      if (controller.signal.aborted) return;
      catalog = next;
      checked.textContent = `Last source check: ${new Date(next.retrieved_at).toLocaleString()}. Your Reactor account determines which models you can use.`;
      const check = next.automatic_check;
      automatic.textContent = !check ? "" : !check.enabled ? "Automatic model checks are off. Change this in Reactor settings." : check.running ? "An automatic model check is running. Reopen this list to see its result." : check.error ? check.error : check.update_available === true ? "The model list has changed. Select Refresh models to update your list." : check.checked_at ? `Automatic check: ${new Date(check.checked_at).toLocaleString()}. Checks run every ${check.interval_hours} hours.` : "An automatic model check is due. Checks do not change this list.";
      status.textContent = action2 === "refresh" ? "Model list refreshed. No generation started." : action2 === "rollback" ? "Previous model list restored. This does not change which models Reactor offers." : "Local model list loaded.";
      render();
    } catch (error) {
      if (!controller.signal.aborted)
        status.textContent = error instanceof Error ? error.message : "Cannot load models.";
    } finally {
      if (!controller.signal.aborted) {
        refresh.disabled = !catalog?.mutation_allowed;
        rollback.disabled = !catalog?.mutation_allowed || !catalog.can_rollback;
      }
    }
  }
  search.addEventListener("input", render);
  duration.addEventListener("input", render);
  refresh.addEventListener("click", () => void perform("refresh"));
  rollback.addEventListener("click", () => void perform("rollback"));
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      styles.remove();
      currentDialog = void 0;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true }
  );
  document.head.append(styles);
  document.body.append(dialog);
  dialog.showModal();
  void perform("read");
}

// frontend/control-api.ts
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

// frontend/drag.ts
function bindDrag(image, signal, send) {
  let pointer = { x: 0.5, y: 0.5, active: false };
  let captured;
  image.tabIndex = 0;
  image.draggable = false;
  image.style.touchAction = "none";
  image.setAttribute(
    "aria-label",
    "Drag on the output to move the subject. Use arrow keys to position the pointer, Space to hold it, and Escape to release it."
  );
  const release = () => {
    const wasActive = pointer.active;
    pointer = { ...pointer, active: false };
    const previousCapture = captured;
    captured = void 0;
    if (wasActive) send(pointer);
    if (previousCapture !== void 0 && image.hasPointerCapture(previousCapture))
      image.releasePointerCapture(previousCapture);
  };
  const position = (event, active) => {
    const rect = image.getBoundingClientRect();
    pointer = {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)),
      active
    };
    send(pointer);
  };
  image.addEventListener(
    "pointerdown",
    (event) => {
      if (event.button !== 0 || captured !== void 0) return;
      captured = event.pointerId;
      image.setPointerCapture(captured);
      image.focus();
      position(event, true);
    },
    { signal }
  );
  image.addEventListener(
    "pointermove",
    (event) => {
      if (captured === event.pointerId) position(event, true);
    },
    { signal }
  );
  for (const name of ["pointerup", "pointercancel", "lostpointercapture"])
    image.addEventListener(name, release, { signal });
  image.addEventListener(
    "keydown",
    (event) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " ", "Escape"].includes(event.key))
        return;
      event.preventDefault();
      event.stopPropagation();
      if (event.key === "Escape") {
        release();
        image.blur();
        return;
      }
      pointer = {
        x: Math.max(
          0,
          Math.min(
            1,
            pointer.x + (event.key === "ArrowRight" ? 0.03 : event.key === "ArrowLeft" ? -0.03 : 0)
          )
        ),
        y: Math.max(
          0,
          Math.min(
            1,
            pointer.y + (event.key === "ArrowDown" ? 0.03 : event.key === "ArrowUp" ? -0.03 : 0)
          )
        ),
        active: event.key === " " || pointer.active
      };
      send(pointer);
    },
    { signal }
  );
  image.addEventListener(
    "keyup",
    (event) => {
      if (event.key === " ") {
        event.preventDefault();
        event.stopPropagation();
        release();
      }
    },
    { signal }
  );
  image.addEventListener("blur", release, { signal });
  window.addEventListener("blur", release, { signal });
  document.addEventListener(
    "visibilitychange",
    () => {
      if (document.hidden) release();
    },
    { signal }
  );
  signal.addEventListener("abort", release, { once: true });
  return release;
}

// frontend/live-api.ts
function record2(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function invitation(value) {
  if (!record2(value) || !record2(value.axes)) return;
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
  if (!record2(value) || typeof value.closed !== "boolean" || typeof value.termination_confirmed !== "boolean" || typeof value.failed !== "boolean" || typeof value.controls_ready !== "boolean" || typeof value.finishing !== "boolean" || typeof value.elapsed_seconds !== "number" || !Number.isFinite(value.elapsed_seconds) || typeof value.preview_sequence !== "number" || !Number.isSafeInteger(value.preview_sequence) || typeof value.preview !== "string" || value.preview.length > 35e4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(value.preview)) {
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

// frontend/pointer-preview.ts
var PointerPreview = class {
  view = element("div");
  status = element("p");
  #marker = element("span");
  #state = element("span");
  #position = element("span");
  #image;
  #pointer;
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
  move(pointer) {
    this.#pointer = pointer;
    this.status.hidden = false;
    this.#position.textContent = ` ${Math.round(pointer.x * 100)}% across, ${Math.round(pointer.y * 100)}% down.`;
    this.#place();
  }
  confirm(pointer) {
    const message = pointer.active ? "Pointer held." : "Pointer released.";
    if (this.#state.textContent !== message) this.#state.textContent = message;
  }
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

// frontend/sound-controls.ts
var SoundControls = class {
  view = element("fieldset");
  prompt = element("textarea");
  apply = button("Apply sound prompt");
  pending;
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
  setReady(ready) {
    this.prompt.disabled = !ready;
    this.apply.disabled = !ready || this.pending !== void 0;
  }
  takePrompt() {
    const value = this.pending;
    this.pending = void 0;
    return value;
  }
};

// frontend/webcam.ts
var Webcam = class {
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
    this.enable.addEventListener("click", () => {
      void this.start();
    });
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
        ...devices.filter((device) => device.kind === "videoinput").map(
          (device, index) => new Option(
            device.label || `Camera ${index + 1}`,
            device.deviceId,
            false,
            device.deviceId === selected
          )
        )
      );
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
    this.stream?.getTracks().forEach((track) => {
      track.stop();
    });
    this.stream = void 0;
    this.video.srcObject = null;
  }
};

// frontend/control-panel.ts
var panels = /* @__PURE__ */ new Set();
function openControls(value, fetcher) {
  const owner = controls(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  createPanel(owner, fetcher);
}
function createPanel(owner, fetcher) {
  const prior = document.activeElement;
  const abort = new AbortController();
  const dialog = element("dialog");
  dialog.className = "reactor-settings reactor-controls";
  dialog.setAttribute("aria-label", "Reactor live controls");
  const image = element("img");
  image.alt = "Live model output";
  image.hidden = true;
  const pointerPreview = owner.pointer ? new PointerPreview(image, abort.signal) : void 0;
  const status = element("p", "Choose your input, then start within 60 seconds.");
  status.setAttribute("role", "status");
  const prompt = element("textarea");
  prompt.value = owner.prompt;
  prompt.maxLength = owner.prompt_limit;
  prompt.rows = 2;
  prompt.disabled = true;
  const label = element("label", "Scene prompt ");
  label.append(prompt);
  const start = button("Start session");
  const update = button("Apply prompt");
  update.disabled = true;
  const end = button("Cancel");
  let ending = false;
  let finished = false;
  let ready = false;
  let sequence = 0;
  let actionSequence = 0;
  let previewSequence = 0;
  const pointers = [];
  let pendingPrompt;
  let startRequested = false;
  let startAttempted = false;
  const sound = owner.sound ? new SoundControls(owner.audio_prompt) : void 0;
  const stop = (message = "Ending the session…") => {
    ending = true;
    ready = false;
    start.disabled = update.disabled = true;
    sound?.setReady(false);
    pointerPreview?.stop();
    status.textContent = message;
    camera?.close();
  };
  const camera = owner.webcam ? new Webcam(owner, fetcher, stop) : void 0;
  if (owner.pointer)
    bindDrag(image, abort.signal, (next) => {
      if (!ready || ending) return;
      pointerPreview?.move(next);
      const previous = pointers.at(-1);
      if (previous?.active && next.active) pointers.pop();
      if (pointers.length >= 8) {
        stop("Pointer input arrived too quickly. The session is ending.");
        return;
      }
      pointers.push(next);
    });
  start.addEventListener("click", () => {
    startRequested = true;
    start.disabled = true;
  });
  update.addEventListener("click", () => {
    if (!prompt.value.trim() && owner.model !== "reactor/sana-streaming") {
      status.textContent = "Enter a prompt before applying it.";
      return;
    }
    pendingPrompt = prompt.value;
    update.disabled = true;
  });
  end.addEventListener("click", () => {
    if (finished) dialog.close();
    else stop();
  });
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    if (finished) dialog.close();
    else stop();
  });
  dialog.addEventListener("close", () => {
    stop();
    abort.abort();
    image.removeAttribute("src");
    dialog.remove();
    panels.delete(owner.lease);
    if (prior instanceof HTMLElement && prior.isConnected) prior.focus();
  });
  dialog.append(
    element(
      "style",
      `${settingsStyles}
      .reactor-controls { box-sizing:border-box; width:min(48rem, calc(100vw - 2rem)); scroll-padding-bottom:7rem; }
      .reactor-controls h2 { margin:0 0 .5rem; }
      .reactor-controls p { margin:.5rem 0; }
      .reactor-controls img { display:block; width:auto; height:auto; max-width:100%; max-height:30vh; margin:auto; }
      .reactor-controls img[hidden] { display:none; }
      .reactor-controls textarea { width:100%; box-sizing:border-box; }
      .reactor-controls footer { position:sticky; bottom:-1.5rem; z-index:1; margin-top:.5rem; padding:.5rem 0; background:var(--comfy-menu-bg, Canvas); }
      .reactor-controls footer p { margin:0 0 .5rem; }
      .reactor-webcam { display:grid; grid-template-columns:minmax(0,1fr) 160px; gap:.5rem 1rem; align-items:center; }
      .reactor-webcam video { width:160px; max-height:120px; object-fit:contain; }
      .reactor-webcam video[hidden] { display:none; }
      .reactor-webcam select { width:100%; }
      .reactor-webcam p { grid-column:1 / -1; margin:.25rem 0 .75rem; }
      @media (max-width:600px) { .reactor-webcam { grid-template-columns:1fr; } }
      .reactor-pointer-preview { position:relative; }
      .reactor-pointer-marker { position:absolute; width:14px; height:14px; border:2px solid white; outline:2px solid black; border-radius:50%; transform:translate(-50%, -50%); pointer-events:none; }
      `
    ),
    element("h2", "Reactor live controls"),
    element("p", `${owner.modelTitle} · ${owner.duration_seconds} seconds of video`),
    element(
      "p",
      "Starting uses Reactor credits. Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound."
    )
  );
  if (camera) dialog.append(camera.view);
  dialog.append(pointerPreview?.view ?? image);
  if (owner.pointer)
    dialog.append(
      element(
        "p",
        "Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it."
      )
    );
  if (pointerPreview) dialog.append(pointerPreview.status);
  dialog.append(label, update);
  if (sound) dialog.append(sound.view);
  const footer = element("footer");
  const actions = element("div");
  actions.className = "reactor-actions";
  actions.append(start, end);
  footer.append(status, actions);
  dialog.append(footer);
  document.body.append(dialog);
  dialog.showModal();
  start.focus();
  const poll = async () => {
    try {
      while (!finished && !abort.signal.aborted) {
        const reply = await exchange(
          fetcher,
          owner,
          sequence++,
          {},
          ending,
          previewSequence,
          AbortSignal.timeout(2e3)
        );
        const wasReady = ready;
        ready = reply.controls_ready && !reply.finishing && !ending;
        prompt.disabled = !ready;
        sound?.setReady(ready);
        if (ready && !wasReady) status.textContent = "Recording. Live controls are ready.";
        update.disabled = !ready || pendingPrompt !== void 0;
        if (reply.preview) {
          image.src = `data:image/jpeg;base64,${reply.preview}`;
          image.hidden = false;
        }
        previewSequence = reply.preview_sequence;
        if (reply.closed) {
          finished = true;
          camera?.close();
          start.disabled = update.disabled = true;
          sound?.setReady(false);
          pointerPreview?.stop();
          status.textContent = reply.termination_confirmed ? reply.failed ? "Recording failed. The session ended. Close this panel to see the workflow error." : "Session ended. Close this panel to view the workflow result." : "Connection closed. Check Reactor session status before starting again.";
          if (!startAttempted && reply.termination_confirmed)
            status.textContent = "Recording did not start. Close this panel to view the workflow result.";
          end.textContent = "Close";
          break;
        }
        if (!ending && !reply.finishing) {
          const hasFrame = camera ? await camera.frame() : true;
          if (startRequested && hasFrame) {
            startAttempted = true;
            await action(fetcher, owner, actionSequence++, "start", {});
            startRequested = false;
            end.textContent = "End session";
            status.textContent = "Connecting to Reactor…";
          } else if (startRequested) {
            status.textContent = "Enable a camera before starting.";
            start.disabled = false;
            startRequested = false;
          }
          if (ready && pendingPrompt !== void 0) {
            await action(fetcher, owner, actionSequence++, "prompt", { prompt: pendingPrompt });
            pendingPrompt = void 0;
            status.textContent = "Prompt sent. The model applies changes to later frames.";
          }
          if (ready && pointers.length) {
            const next = pointers.shift();
            if (!next) continue;
            await action(fetcher, owner, actionSequence++, "pointer", next);
            pointerPreview?.confirm(next);
          }
          const audioPrompt = ready ? sound?.takePrompt() : void 0;
          if (audioPrompt !== void 0) {
            await action(fetcher, owner, actionSequence++, "audio_prompt", { prompt: audioPrompt });
            status.textContent = "Sound prompt sent. The model applies changes to later audio.";
          }
        }
        if (reply.finishing) {
          camera?.close();
          status.textContent = "Saving the video and ending the session…";
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } catch (error) {
      stop(error instanceof Error ? error.message : "The live connection ended.");
      finished = true;
      end.textContent = "Close";
    }
  };
  void poll();
}

// frontend/credit-rate.ts
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
var current;
function openCreditRate(node, fetcher) {
  if (current?.open) {
    current.focus();
    return;
  }
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  current = dialog;
  dialog.className = "reactor-settings";
  dialog.setAttribute("aria-labelledby", "reactor-rate-title");
  const style = element("style", settingsStyles);
  const title = element("h2", "Credit rate");
  title.id = "reactor-rate-title";
  const close = button("Close");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(title, close);
  const seconds = requestedSeconds(node);
  const request = element(
    "p",
    seconds === void 0 ? "The video length comes from a connected input or is not available. Enter a session time below to calculate credits." : `This node requests ${seconds.toLocaleString()} seconds of video. Setup, pauses, and recording can add paid time.`
  );
  const label = element("label", "Session time to calculate (seconds)");
  const duration = element("input");
  duration.type = "number";
  duration.min = "0.1";
  duration.max = "3600";
  duration.step = "any";
  duration.placeholder = "Enter total paid session time";
  if (seconds !== void 0) duration.value = String(seconds);
  label.append(duration);
  const validation = element("p");
  validation.setAttribute("role", "status");
  const validateDuration = () => {
    validation.textContent = duration.value === "" || !duration.validity.valid ? "Enter a session time from 0.1 to 3,600 seconds." : "";
  };
  duration.addEventListener("input", validateDuration);
  validateDuration();
  const status = element("p", "Loading the local credit rate…");
  status.setAttribute("role", "status");
  const rates = element("div");
  rates.setAttribute("aria-live", "polite");
  dialog.append(
    header,
    request,
    label,
    validation,
    element(
      "p",
      "This is rate × time, not an exact charge or a spending limit. The starting time uses the requested video length and excludes extra paid time. Your Reactor account shows actual charges."
    ),
    status,
    rates
  );
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      style.remove();
      current = void 0;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true }
  );
  document.head.append(style);
  document.body.append(dialog);
  dialog.showModal();
  void requestCatalog(fetcher, controller.signal, "read").then((catalog) => {
    if (controller.signal.aborted) return;
    const models = catalog.models.filter(
      (model2) => model2.node_ids.includes(node.comfyClass ?? "")
    );
    status.textContent = `Rates checked ${new Date(catalog.retrieved_at).toLocaleString()}.`;
    if (!models.length)
      status.textContent = "No rate is listed for this node. Open the ComfyUI menu, then Extensions → Reactor → Reactor models, and refresh the list.";
    function render() {
      rates.replaceChildren();
      for (const model2 of models) {
        rates.append(element("h3", model2.title));
        const rate = model2.credits_per_second;
        if (!model2.observed || rate === null) {
          rates.append(
            element(
              "p",
              "A current rate is not available. Refresh Reactor models before relying on a calculation."
            )
          );
          continue;
        }
        rates.append(element("p", `${rate.toLocaleString()} credits per session second.`));
        if (duration.value !== "" && duration.validity.valid) {
          const total = (rate * duration.valueAsNumber).toLocaleString(void 0, {
            maximumFractionDigits: 2
          });
          rates.append(
            element(
              "p",
              `${duration.valueAsNumber.toLocaleString()} seconds × ${rate.toLocaleString()} = ${total} credits.`
            )
          );
        }
      }
    }
    duration.addEventListener("input", render);
    render();
  }).catch((error) => {
    if (!controller.signal.aborted)
      status.textContent = error instanceof Error ? error.message : "Cannot load the credit rate.";
  });
}
function bindCreditRate(node, fetcher) {
  const id = node.comfyClass;
  if (!id?.startsWith("ReactorInc") || id === "ReactorIncHeliosAddPrompt" || id === "ReactorIncLongLiveAddShot")
    return;
  node.addWidget("button", "View credit rate", "", () => openCreditRate(node, fetcher), {
    serialize: false
  });
}

// frontend/live-input.ts
function cameraAxes(keys, world2) {
  const direction = (negative, positive, first, second) => keys.has(negative) === keys.has(positive) ? "idle" : keys.has(negative) ? first : second;
  const forward = direction("w", "s", "forward", "back");
  const lateral = direction("a", "d", "strafe_left", "strafe_right");
  return {
    ...world2 ? { move_longitudinal: forward, move_lateral: lateral } : { movement: forward !== "idle" ? forward : lateral },
    look_horizontal: direction("ArrowLeft", "ArrowRight", "left", "right"),
    look_vertical: direction("ArrowUp", "ArrowDown", "up", "down")
  };
}
var cameraKeys = ["w", "s", "a", "d", "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
function bindCameraInput(surface, controls2, signal, update) {
  const keyboard = /* @__PURE__ */ new Set();
  const pointers = /* @__PURE__ */ new Map();
  const pointerStarted = /* @__PURE__ */ new Map();
  let lastHold;
  const nudges = /* @__PURE__ */ new Map();
  const publish = (release2 = false) => update(/* @__PURE__ */ new Set([...keyboard, ...pointers.values(), ...nudges.keys()]), release2);
  const nudge = (key, milliseconds) => {
    const previous = nudges.get(key);
    if (previous !== void 0) clearTimeout(previous);
    nudges.set(
      key,
      setTimeout(() => {
        nudges.delete(key);
        publish();
      }, milliseconds)
    );
  };
  const release = () => {
    keyboard.clear();
    pointers.clear();
    pointerStarted.clear();
    lastHold = void 0;
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
    { signal }
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
    { signal }
  );
  surface.addEventListener("blur", release, { signal });
  controls2.addEventListener(
    "pointerdown",
    (event) => {
      const target = event.target;
      if (!(target instanceof HTMLButtonElement) || !target.dataset.key || event.button !== 0)
        return;
      event.preventDefault();
      target.setPointerCapture(event.pointerId);
      lastHold = void 0;
      pointers.set(event.pointerId, target.dataset.key);
      pointerStarted.set(event.pointerId, performance.now());
      publish();
    },
    { signal }
  );
  for (const kind of ["pointerup", "pointercancel", "lostpointercapture"]) {
    controls2.addEventListener(
      kind,
      (event) => {
        const key = pointers.get(event.pointerId);
        const started = pointerStarted.get(event.pointerId);
        if (kind === "pointerup" && key && started !== void 0) {
          lastHold = { key, milliseconds: performance.now() - started };
          if (lastHold.milliseconds < 250) nudge(key, 250 - lastHold.milliseconds);
        }
        pointers.delete(event.pointerId);
        pointerStarted.delete(event.pointerId);
        publish();
      },
      { signal }
    );
  }
  controls2.addEventListener(
    "keydown",
    (event) => {
      const target = event.target;
      if (target instanceof HTMLButtonElement && target.dataset.key && [" ", "Enter"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        keyboard.add(target.dataset.key);
        publish();
      }
    },
    { signal }
  );
  controls2.addEventListener(
    "keyup",
    (event) => {
      const target = event.target;
      if (target instanceof HTMLButtonElement && target.dataset.key && [" ", "Enter"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        keyboard.delete(target.dataset.key);
        publish();
      }
    },
    { signal }
  );
  controls2.addEventListener("focusout", release, { signal });
  controls2.addEventListener(
    "click",
    (event) => {
      const target = event.target;
      if (!(target instanceof HTMLButtonElement) || !target.dataset.key) return;
      if (event.detail !== 0 && lastHold?.key === target.dataset.key) return;
      const key = target.dataset.key;
      nudge(key, 250);
      publish();
    },
    { signal }
  );
  window.addEventListener("blur", release, { signal });
  document.addEventListener(
    "visibilitychange",
    () => {
      if (document.hidden) release();
    },
    { signal }
  );
  signal.addEventListener("abort", release, { once: true });
  return release;
}

// frontend/live-state.ts
var CameraStates = class {
  current;
  pending = [];
  world2;
  constructor(world2) {
    this.world2 = world2;
    this.current = cameraAxes(/* @__PURE__ */ new Set(), world2);
  }
  update(keys, release = false) {
    const axes = cameraAxes(keys, this.world2);
    if (release) this.pending = [];
    if (release || JSON.stringify(axes) !== JSON.stringify(this.current)) {
      if (this.pending.length >= 8) {
        this.pending = [{ axes: cameraAxes(/* @__PURE__ */ new Set(), this.world2), release: true }];
        if (Object.values(axes).some((value) => value !== "idle"))
          this.pending.push({ axes, release: false });
      } else this.pending.push({ axes, release });
    }
    this.current = axes;
  }
  take() {
    return this.pending.shift() ?? { axes: this.current, release: false };
  }
};

// frontend/live.ts
var panels2 = /* @__PURE__ */ new Map();
function openLive(value, fetcher) {
  const owner = invitation(value);
  if (!owner || panels2.has(owner.lease)) return;
  createPanel2(owner, fetcher);
}
function createPanel2(owner, fetcher) {
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  panels2.set(owner.lease, dialog);
  dialog.className = "reactor-settings reactor-live";
  dialog.setAttribute("aria-label", "Reactor live camera");
  const styles = element(
    "style",
    `${settingsStyles}
    .reactor-live { width: min(52rem, calc(100vw - 2rem)); box-sizing: border-box; }
    .reactor-live header { position: sticky; top: -1.5rem; padding: .5rem 0; background: var(--comfy-menu-bg, Canvas); }
    .reactor-live p { margin: .6rem 0; }
    .reactor-live .reactor-preview { min-height: 0; background: #111; display: grid; place-items: center; }
    .reactor-live img { max-width: 100%; max-height: 32vh; object-fit: contain; }
    .reactor-live .reactor-actions { display: grid; grid-template-columns: repeat(4, 1fr); touch-action: none; }
    @media (max-width: 420px) { .reactor-live .reactor-actions { grid-template-columns: repeat(2, 1fr); } }
    .reactor-live textarea { width: 100%; box-sizing: border-box; }
  `
  );
  const title = element("h2", "Reactor live camera");
  const status = element("p", "Connecting the live panel…");
  status.setAttribute("role", "status");
  const elapsed = element("p");
  const prompt = element("textarea");
  prompt.value = owner.prompt;
  prompt.maxLength = owner.prompt_limit;
  prompt.rows = 2;
  prompt.disabled = true;
  const promptLabel = element("label", "Scene prompt ");
  promptLabel.append(prompt);
  const apply = button("Apply prompt");
  apply.disabled = true;
  const promptStatus = element(
    "p",
    "Prompt changes affect later frames. The starting image stays fixed."
  );
  promptStatus.setAttribute("role", "status");
  let pendingPrompt;
  let actionSequence = 0;
  apply.addEventListener("click", () => {
    if (!prompt.value.trim()) {
      promptStatus.textContent = "Enter a scene prompt before applying it.";
      return;
    }
    pendingPrompt = prompt.value;
    apply.disabled = true;
  });
  const surface = element("div");
  surface.className = "reactor-preview";
  surface.tabIndex = 0;
  surface.setAttribute(
    "aria-label",
    "Live view. W A S D moves. Arrow keys turn. Escape stops camera movement."
  );
  const image = element("img");
  image.alt = "Live model output";
  image.hidden = true;
  surface.append(image);
  const controls2 = element("div");
  controls2.className = "reactor-actions";
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
  cameraKeys.forEach((key, index) => {
    const control = button(labels[index] ?? key);
    control.dataset.key = key;
    control.disabled = true;
    controls2.append(control);
  });
  const end = button("End session");
  const header = element("header");
  header.append(title, end);
  let ending = false;
  let finished = false;
  let disposed = false;
  let sequence = 0;
  let previewSequence = 0;
  const states = new CameraStates(owner.model.endsWith("world-2"));
  const release = bindCameraInput(surface, controls2, controller.signal, (keys, urgent) => {
    states.update(keys, urgent);
  });
  const stop = () => {
    ending = true;
    release();
    end.disabled = true;
    apply.disabled = prompt.disabled = true;
    status.textContent = "Ending the session…";
  };
  end.addEventListener("click", () => {
    if (finished) dialog.close();
    else stop();
  });
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    release();
    surface.blur();
  });
  dialog.addEventListener("close", () => {
    stop();
    disposed = true;
    controller.abort();
    image.removeAttribute("src");
    panels2.delete(owner.lease);
    dialog.remove();
    if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
  });
  dialog.append(
    styles,
    header,
    element("p", `${owner.modelTitle} · ${owner.duration_seconds} seconds of video`),
    element(
      "p",
      "Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement."
    ),
    surface,
    controls2,
    promptLabel,
    apply,
    promptStatus,
    status,
    elapsed,
    element(
      "p",
      "The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Setup and recording use credits. Ending early discards the unfinished video."
    )
  );
  document.body.append(dialog);
  dialog.showModal();
  surface.focus();
  void poll();
  async function poll() {
    try {
      while (!finished) {
        const input = states.take();
        const result = await exchange(
          fetcher,
          owner,
          sequence++,
          input.axes,
          ending,
          previewSequence,
          AbortSignal.timeout(2e3),
          input.release
        );
        previewSequence = result.preview_sequence;
        if (!disposed) {
          for (const control of controls2.querySelectorAll("button")) {
            control.disabled = !result.controls_ready || ending;
          }
          prompt.disabled = !result.controls_ready || ending;
          apply.disabled = prompt.disabled || pendingPrompt !== void 0;
          elapsed.textContent = `Time spent on setup and recording: ${result.elapsed_seconds.toFixed(1)} seconds.`;
          if (result.preview) {
            image.src = `data:image/jpeg;base64,${result.preview}`;
            image.hidden = false;
          }
          if (result.finishing && !result.closed) {
            release();
            surface.blur();
            end.disabled = true;
            status.textContent = "Finishing the video and ending the session…";
          } else if (!ending)
            status.textContent = result.controls_ready && result.preview_sequence > 0 ? "Live preview. Controls are active." : "Waiting for model video…";
        }
        if (result.closed) {
          finished = true;
          status.textContent = result.termination_confirmed ? result.failed ? "Recording failed. The session ended. Close this panel to see the workflow error." : "Session ended. Close this panel to view the workflow result." : "Reactor has not confirmed that the session ended. Wait for its time limit before another run.";
        } else {
          if (result.controls_ready && !result.finishing && !ending && pendingPrompt !== void 0) {
            await action(fetcher, owner, actionSequence++, "prompt", { prompt: pendingPrompt });
            pendingPrompt = void 0;
            promptStatus.textContent = "Prompt sent. Watch the video for the change.";
          }
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
      }
    } catch {
      finished = true;
      status.textContent = "The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.";
    } finally {
      release();
      controller.abort();
      end.disabled = false;
      end.textContent = "Close";
      prompt.disabled = apply.disabled = true;
      for (const control of controls2.querySelectorAll("button")) control.disabled = true;
      if (disposed) panels2.delete(owner.lease);
    }
  }
}

// frontend/node-help.ts
import { app } from "../../scripts/app.js";

// frontend/help-dialog.ts
var current2;
function openHelpDialog(nodeId2) {
  current2?.close();
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  current2 = dialog;
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
  frame.sandbox.add("allow-same-origin", "allow-popups", "allow-popups-to-escape-sandbox");
  frame.src = `/extensions/reactor-inc/guides/docs/nodes/${nodeId2}.html`;
  frame.addEventListener("load", () => prepareGuide(frame, dialog, controller.signal));
  const styles = element("style", `${settingsStyles}
${helpStyles}`);
  dialog.append(header, frame);
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      styles.remove();
      if (current2 === dialog) current2 = void 0;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true }
  );
  document.head.append(styles);
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
var helpStyles = `
.reactor-node-help { width: min(64rem, calc(100vw - 2rem)); padding: 1rem; }
.reactor-node-help iframe { display: block; width: 100%; height: min(72vh, 55rem); border: 0; margin-top: 1rem; }
`;

// frontend/node-help.ts
var HELP_COMMAND = "ReactorInc.OpenNodeHelp";
function nodeId(item) {
  if (typeof item !== "object" || item === null || !("comfyClass" in item)) return;
  const id = item.comfyClass;
  return typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id) ? id : void 0;
}
function helpCommands(item) {
  return nodeId(item) ? [HELP_COMMAND] : [];
}
function openNodeHelp() {
  const id = Array.from(app.canvas.selectedItems ?? []).map(nodeId).find(Boolean);
  if (!id) return;
  openHelpDialog(id);
}

// frontend/node-labels.ts
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

// frontend/configuration.ts
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

// frontend/settings.ts
var currentDialog2;
function openSettings(fetcher) {
  if (currentDialog2?.open) {
    currentDialog2.focus();
    return;
  }
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  currentDialog2 = dialog;
  dialog.className = "reactor-settings";
  dialog.setAttribute("aria-labelledby", "reactor-settings-title");
  const styles = element("style", settingsStyles);
  const heading = element("h2", "Reactor settings");
  heading.id = "reactor-settings-title";
  const close = button("Close");
  close.setAttribute("aria-label", "Close Reactor settings");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const status = element("p", "Loading local settings…");
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  const source = element("p");
  const reload = button("Reload settings");
  const keyForm = element("form");
  const keyFields = element("fieldset");
  keyFields.disabled = true;
  const keyLabel = element("label", "Reactor API key");
  const key = element("input");
  key.type = "password";
  key.autocomplete = "off";
  key.spellcheck = false;
  key.maxLength = 1024;
  key.required = true;
  keyLabel.append(key);
  const saveKey = button("Save key", "submit");
  const clearKey = button("Clear saved key");
  const keyActions = element("div");
  keyActions.className = "reactor-actions";
  keyActions.append(saveKey, clearKey);
  keyFields.append(element("legend", "Credentials"), keyLabel, keyActions);
  keyForm.append(keyFields);
  const limitsForm = element("form");
  const limitFields = element("fieldset");
  limitFields.disabled = true;
  limitFields.append(element("legend", "Execution limits"));
  const advanced = element("details");
  advanced.append(element("summary", "Advanced limits"));
  const inputs = /* @__PURE__ */ new Map();
  fields.forEach(([name, title], index) => {
    const label = element("label", title);
    const input = element("input");
    input.type = "number";
    input.min = "1";
    input.max = "3600";
    input.step = "1";
    input.required = true;
    inputs.set(name, input);
    label.append(input);
    (index < 2 ? limitFields : advanced).append(label);
  });
  limitFields.append(advanced, button("Save limits", "submit"));
  limitsForm.append(limitFields);
  const catalogForm = element("form");
  const catalogFields = element("fieldset");
  catalogFields.disabled = true;
  const automaticLabel = element("label", "Check for model updates automatically");
  const automatic = element("input");
  automatic.type = "checkbox";
  automaticLabel.prepend(automatic);
  const intervalLabel = element("label", "Check interval (hours)");
  const interval = element("input");
  interval.type = "number";
  interval.min = "1";
  interval.max = "3600";
  interval.step = "1";
  interval.required = true;
  intervalLabel.append(interval);
  catalogFields.append(
    element("legend", "Model updates"),
    automaticLabel,
    intervalLabel,
    element(
      "p",
      "Checks read public prices and model guides. They do not use your key or spend credits. Open Reactor models to see changes and refresh your list."
    ),
    button("Save model check settings", "submit")
  );
  catalogForm.append(catalogFields);
  dialog.append(
    header,
    element(
      "p",
      "Reactor uses its own account and credits. Opening settings and saving a key do not start generation."
    ),
    source,
    keyForm,
    element(
      "p",
      "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here."
    ),
    limitsForm,
    element(
      "p",
      "Session time includes setup and generation. These limits do not buy credits or change account billing."
    ),
    catalogForm,
    status,
    reload
  );
  let configuration;
  function display(value) {
    configuration = value;
    source.textContent = {
      missing: "No Reactor key is configured.",
      saved: "A saved key is configured on this server.",
      environment: "The server's REACTOR_API_KEY environment variable is active."
    }[value.credentialSource];
    keyFields.disabled = !value.mutationAllowed;
    limitFields.disabled = !value.mutationAllowed;
    catalogFields.disabled = !value.mutationAllowed;
    automatic.checked = value.settings.catalog_auto_check;
    interval.value = String(value.settings.catalog_interval_hours);
    for (const [name, input] of inputs) input.value = String(value.settings[name]);
    if (!value.mutationAllowed)
      status.textContent = "Changes are disabled in this host's multi-user mode.";
  }
  async function perform(operation, message) {
    keyFields.disabled = true;
    limitFields.disabled = true;
    catalogFields.disabled = true;
    reload.disabled = true;
    status.textContent = "Working…";
    try {
      const value = await operation();
      if (controller.signal.aborted) return;
      status.textContent = message;
      display(value);
    } catch (error) {
      if (!controller.signal.aborted) {
        status.textContent = error instanceof Error ? error.message : "Reactor settings could not be saved.";
      }
    } finally {
      if (!controller.signal.aborted) {
        keyFields.disabled = !configuration?.mutationAllowed;
        limitFields.disabled = !configuration?.mutationAllowed;
        catalogFields.disabled = !configuration?.mutationAllowed;
        reload.disabled = false;
      }
    }
  }
  const request = (route, method, body) => requestConfiguration(fetcher, controller.signal, route, method, body);
  keyForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!keyForm.reportValidity()) return;
    const value = key.value;
    key.value = "";
    void perform(
      () => request("/credential", "PUT", { api_key: value }),
      "Key saved on this server. Reactor checks it when you start a session."
    );
  });
  clearKey.addEventListener("click", () => {
    key.value = "";
    void perform(
      () => request("/credential", "DELETE"),
      "Saved key cleared. Any environment key remains active."
    );
  });
  limitsForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!configuration || !limitsForm.reportValidity()) return;
    const changes = {};
    for (const [name, input] of inputs) {
      if (input.valueAsNumber !== configuration.settings[name]) changes[name] = input.valueAsNumber;
    }
    if (Object.keys(changes).length === 0) {
      status.textContent = "No limit changes to save.";
      return;
    }
    const revision = configuration.revision;
    void perform(
      () => request("/settings", "PATCH", { revision, settings: changes }),
      "Limits saved. They apply to new executions."
    );
  });
  reload.addEventListener("click", () => void perform(() => request(), "Local settings loaded."));
  catalogForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!configuration || !catalogForm.reportValidity()) return;
    const settings = {
      catalog_auto_check: automatic.checked,
      catalog_interval_hours: interval.valueAsNumber
    };
    if (settings.catalog_auto_check === configuration.settings.catalog_auto_check && settings.catalog_interval_hours === configuration.settings.catalog_interval_hours) {
      status.textContent = "No model check changes to save.";
      return;
    }
    const revision = configuration.revision;
    void perform(
      () => request("/settings", "PATCH", { revision, settings }),
      "Model check settings saved. The scheduler reads changes within one minute."
    );
  });
  dialog.addEventListener(
    "close",
    () => {
      key.value = "";
      controller.abort();
      dialog.remove();
      styles.remove();
      currentDialog2 = void 0;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true }
  );
  document.head.append(styles);
  document.body.append(dialog);
  dialog.showModal();
  void perform(() => request(), "Local settings loaded.");
}

// frontend/extension.ts
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
  nodeCreated: (node) => {
    bindNodeWidgets(node);
    const fetcher = (route, options) => api.fetchApi(route, options);
    bindCreditRate(node, fetcher);
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
      function: () => openCatalog((route, options) => api.fetchApi(route, options))
    }
  ],
  menuCommands: [
    {
      path: ["Extensions", "Reactor"],
      commands: ["ReactorInc.OpenSettings", "ReactorInc.OpenCatalog"]
    }
  ]
});
