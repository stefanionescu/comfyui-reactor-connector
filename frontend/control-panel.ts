import type { Fetcher } from "./configuration.ts";
import { action, type Controls, controls } from "./control-api.ts";
import { button, element } from "./dom.ts";
import { bindDrag, type Pointer } from "./drag.ts";
import { exchange } from "./live-api.ts";
import { PointerPreview } from "./pointer-preview.ts";
import { SoundControls } from "./sound-controls.ts";
import { settingsStyles } from "./styles.ts";
import { Webcam } from "./webcam.ts";

const panels = new Set<string>();

export function openControls(value: unknown, fetcher: Fetcher): void {
  const owner = controls(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  createPanel(owner, fetcher);
}

function createPanel(owner: Controls, fetcher: Fetcher): void {
  const prior = document.activeElement;
  const abort = new AbortController();
  const dialog = element("dialog");
  dialog.className = "reactor-settings reactor-controls";
  dialog.setAttribute("aria-label", "Reactor live controls");
  const image = element("img");
  image.alt = "Live model output";
  image.hidden = true;
  const pointerPreview = owner.pointer ? new PointerPreview(image, abort.signal) : undefined;
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
  const pointers: Pointer[] = [];
  let pendingPrompt: string | undefined;
  let startRequested = false;
  let startAttempted = false;
  const sound = owner.sound ? new SoundControls(owner.audio_prompt) : undefined;
  const stop = (message = "Ending the session…") => {
    ending = true;
    ready = false;
    start.disabled = update.disabled = true;
    sound?.setReady(false);
    pointerPreview?.stop();
    status.textContent = message;
    camera?.close();
  };
  const camera = owner.webcam ? new Webcam(owner, fetcher, stop) : undefined;
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
      `,
    ),
    element("h2", "Reactor live controls"),
    element("p", `${owner.modelTitle} · ${owner.duration_seconds} seconds of video`),
    element(
      "p",
      "Starting uses Reactor credits. Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound.",
    ),
  );
  if (camera) dialog.append(camera.view);
  dialog.append(pointerPreview?.view ?? image);
  if (owner.pointer)
    dialog.append(
      element(
        "p",
        "Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it.",
      ),
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
          AbortSignal.timeout(2000),
        );
        const wasReady = ready;
        ready = reply.controls_ready && !reply.finishing && !ending;
        prompt.disabled = !ready;
        sound?.setReady(ready);
        if (ready && !wasReady) status.textContent = "Recording. Live controls are ready.";
        update.disabled = !ready || pendingPrompt !== undefined;
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
          status.textContent = reply.termination_confirmed
            ? reply.failed
              ? "Recording failed. The session ended. Close this panel to see the workflow error."
              : "Session ended. Close this panel to view the workflow result."
            : "Connection closed. Check Reactor session status before starting again.";
          if (!startAttempted && reply.termination_confirmed)
            status.textContent =
              "Recording did not start. Close this panel to view the workflow result.";
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
          if (ready && pendingPrompt !== undefined) {
            await action(fetcher, owner, actionSequence++, "prompt", { prompt: pendingPrompt });
            pendingPrompt = undefined;
            status.textContent = "Prompt sent. The model applies changes to later frames.";
          }
          if (ready && pointers.length) {
            const next = pointers.shift();
            if (!next) continue;
            await action(fetcher, owner, actionSequence++, "pointer", next);
            pointerPreview?.confirm(next);
          }
          const audioPrompt = ready ? sound?.takePrompt() : undefined;
          if (audioPrompt !== undefined) {
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
