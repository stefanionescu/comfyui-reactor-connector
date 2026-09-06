import type { Fetcher } from "./configuration.ts";
import { action } from "./control-api.ts";
import { button, element } from "./dom.ts";
import { type CameraInvitation, exchange, invitation } from "./live-api.ts";
import { bindCameraInput, cameraKeys } from "./live-input.ts";
import { CameraStates } from "./live-state.ts";
import { settingsStyles } from "./styles.ts";

const panels = new Map<string, HTMLDialogElement>();

export function openLive(value: unknown, fetcher: Fetcher): void {
  const owner = invitation(value);
  if (!owner || panels.has(owner.lease)) return;
  createPanel(owner, fetcher);
}

function createPanel(owner: CameraInvitation, fetcher: Fetcher): void {
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  panels.set(owner.lease, dialog);
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
  `,
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
    "Prompt changes affect later frames. The starting image stays fixed.",
  );
  promptStatus.setAttribute("role", "status");
  let pendingPrompt: string | undefined;
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
    "Live view. W A S D moves. Arrow keys turn. Escape stops camera movement.",
  );
  const image = element("img");
  image.alt = "Live model output";
  image.hidden = true;
  surface.append(image);
  const controls = element("div");
  controls.className = "reactor-actions";
  const labels = [
    "Forward",
    "Back",
    "Move left",
    "Move right",
    "Look left",
    "Look right",
    "Look up",
    "Look down",
  ];
  cameraKeys.forEach((key, index) => {
    const control = button(labels[index] ?? key);
    control.dataset.key = key;
    control.disabled = true;
    controls.append(control);
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
  const release = bindCameraInput(surface, controls, controller.signal, (keys, urgent) => {
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
    panels.delete(owner.lease);
    dialog.remove();
    if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
  });
  dialog.append(
    styles,
    header,
    element("p", `${owner.modelTitle} · ${owner.duration_seconds} seconds of video`),
    element(
      "p",
      "Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement.",
    ),
    surface,
    controls,
    promptLabel,
    apply,
    promptStatus,
    status,
    elapsed,
    element(
      "p",
      "The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Setup and recording use credits. Ending early discards the unfinished video.",
    ),
  );
  document.body.append(dialog);
  dialog.showModal();
  surface.focus();
  void poll();

  async function poll(): Promise<void> {
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
          AbortSignal.timeout(2000),
          input.release,
        );
        previewSequence = result.preview_sequence;
        if (!disposed) {
          for (const control of controls.querySelectorAll("button")) {
            control.disabled = !result.controls_ready || ending;
          }
          prompt.disabled = !result.controls_ready || ending;
          apply.disabled = prompt.disabled || pendingPrompt !== undefined;
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
            status.textContent =
              result.controls_ready && result.preview_sequence > 0
                ? "Live preview. Controls are active."
                : "Waiting for model video…";
        }
        if (result.closed) {
          finished = true;
          status.textContent = result.termination_confirmed
            ? result.failed
              ? "Recording failed. The session ended. Close this panel to see the workflow error."
              : "Session ended. Close this panel to view the workflow result."
            : "Reactor has not confirmed that the session ended. Wait for its time limit before another run.";
        } else {
          if (
            result.controls_ready &&
            !result.finishing &&
            !ending &&
            pendingPrompt !== undefined
          ) {
            await action(fetcher, owner, actionSequence++, "prompt", { prompt: pendingPrompt });
            pendingPrompt = undefined;
            promptStatus.textContent = "Prompt sent. Watch the video for the change.";
          }
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
      }
    } catch {
      finished = true;
      status.textContent =
        "The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.";
    } finally {
      release();
      controller.abort();
      end.disabled = false;
      end.textContent = "Close";
      prompt.disabled = apply.disabled = true;
      for (const control of controls.querySelectorAll("button")) control.disabled = true;
      if (disposed) panels.delete(owner.lease);
    }
  }
}
