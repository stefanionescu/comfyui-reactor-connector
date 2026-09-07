import { Webcam } from '#web/live/webcam.ts';
import { button, element } from '#web/dom.ts';
import { SoundControls } from '#web/live/sound.ts';
import type { Fetcher } from '#web/settings/api.ts';
import { PointerPreview } from '#web/live/pointer.ts';
import { DragInput, type Pointer } from '#web/live/drag.ts';
import { exchange, type LiveStatus } from '#web/live/api.ts';
import { action, type Controls, controls } from '#web/live/commands.ts';

const panels = new Set<string>();

/** Own a live session's prompt, webcam, sound, and pointer controls. */
class ControlPanel {
  private readonly prior = document.activeElement;

  private readonly abort = new AbortController();

  private readonly dialog = element('dialog');

  private readonly image = element('img');

  private readonly status = element('p', 'Choose your input, then start within 60 seconds.');

  private readonly prompt = element('textarea');

  private readonly start = button('Start session');

  private readonly update = button('Apply prompt');

  private readonly end = button('Cancel');

  private readonly pointerPreview: PointerPreview | undefined;

  private readonly camera: Webcam | undefined;

  private readonly sound: SoundControls | undefined;

  private readonly pointers: Pointer[] = [];

  private ending = false;

  private finished = false;

  private ready = false;

  private sequence = 0;

  private actionSequence = 0;

  private previewSequence = 0;

  private pendingPrompt: string | undefined;

  private startRequested = false;

  private startAttempted = false;

  /**
   * Build only the controls supported by this session.
   * @param owner - The validated session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(
    private readonly owner: Controls,
    private readonly fetcher: Fetcher,
  ) {
    this.dialog.className = 'reactor-settings reactor-controls';
    this.dialog.setAttribute('aria-label', 'Reactor live controls');
    this.image.alt = 'Live model output';
    this.image.hidden = true;
    this.pointerPreview = owner.pointer
      ? new PointerPreview(this.image, this.abort.signal)
      : undefined;
    this.status.setAttribute('role', 'status');
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.prompt_limit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.update.disabled = true;
    this.sound = owner.sound ? new SoundControls(owner.audio_prompt) : undefined;
    this.camera = owner.webcam
      ? new Webcam(owner, fetcher, (message) => this.stop(message))
      : undefined;
    if (owner.pointer)
      new DragInput(this.image, this.abort.signal, (next) => this.queuePointer(next));
    this.bindActions();
    this.appendContent();
  }

  /** Build the preview, supported inputs, and session actions. */
  private appendContent(): void {
    this.dialog.append(
      element('h2', 'Reactor live controls'),
      element('p', `${this.owner.modelTitle} · ${this.owner.duration_seconds} seconds of video`),
      element(
        'p',
        'Starting uses Reactor credits. Recording stops at the chosen duration. Ending early discards the unfinished video. The preview has no sound.',
      ),
    );
    if (this.camera) this.dialog.append(this.camera.view);
    this.dialog.append(this.pointerPreview?.view ?? this.image);
    if (this.owner.pointer)
      this.dialog.append(
        element(
          'p',
          'Drag on the output to steer the subject. Release to stop. With the picture focused, arrow keys position the pointer, Space holds it, and Escape releases it.',
        ),
      );
    if (this.pointerPreview) this.dialog.append(this.pointerPreview.status);
    const label = element('label', 'Scene prompt ');
    label.append(this.prompt);
    this.dialog.append(label, this.update);
    if (this.sound) this.dialog.append(this.sound.view);
    const footer = element('footer');
    const actions = element('div');
    actions.className = 'reactor-actions';
    actions.append(this.start, this.end);
    footer.append(this.status, actions);
    this.dialog.append(footer);
  }

  /** Bind start, prompt, stop, and dialog cleanup actions. */
  private bindActions(): void {
    // eslint-disable-next-line local/no-trivial-functions -- This click queues the start and disables repeat activation.
    this.start.addEventListener('click', () => {
      this.startRequested = true;
      this.start.disabled = true;
    });
    this.update.addEventListener('click', () => {
      if (!this.prompt.value.trim() && this.owner.model !== 'reactor/sana-streaming') {
        this.status.textContent = 'Enter a prompt before applying it.';
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.update.disabled = true;
    });
    this.end.addEventListener('click', () => {
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener('cancel', (event) => {
      event.preventDefault();
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener(
      'close',
      () => {
        this.stop();
        this.abort.abort();
        this.image.removeAttribute('src');
        this.dialog.remove();
        panels.delete(this.owner.lease);
        if (this.prior instanceof HTMLElement && this.prior.isConnected) this.prior.focus();
      },
      { once: true },
    );
  }

  /**
   * Keep pointer releases while combining consecutive held moves.
   * @param next - The next normalized pointer update.
   */
  private queuePointer(next: Pointer): void {
    if (!this.ready || this.ending) return;
    this.pointerPreview?.move(next);
    const previous = this.pointers.at(-1);
    if (previous?.active && next.active) this.pointers.pop();
    if (this.pointers.length >= 8) {
      this.stop('Pointer input arrived too quickly. The session is ending.');
      return;
    }
    this.pointers.push(next);
  }

  /**
   * Stop sending input while waiting for the server to end the session.
   * @param message - The reason shown in the panel.
   */
  private stop(message = 'Ending the session…'): void {
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
  private display(reply: LiveStatus): void {
    const wasReady = this.ready;
    this.ready = reply.controls_ready && !reply.finishing && !this.ending;
    this.prompt.disabled = !this.ready;
    this.sound?.setReady(this.ready);
    if (this.ready && !wasReady) this.status.textContent = 'Recording. Live controls are ready.';
    this.update.disabled = !this.ready || this.pendingPrompt !== undefined;
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
  private finish(reply: LiveStatus): void {
    this.finished = true;
    this.camera?.close();
    this.start.disabled = this.update.disabled = true;
    this.sound?.setReady(false);
    this.pointerPreview?.stop();
    if (!reply.termination_confirmed)
      this.status.textContent =
        'Connection closed. Check Reactor session status before starting again.';
    else if (!this.startAttempted)
      this.status.textContent =
        'Recording did not start. Close this panel to view the workflow result.';
    else
      this.status.textContent = reply.failed
        ? 'The session ended without saving a video. Close this panel to view the workflow result.'
        : 'Session ended. Close this panel to view the workflow result.';
    this.end.textContent = 'Close';
  }

  /**
   * Upload camera input and apply a requested start once a frame is ready.
   * @returns When this cycle's camera upload and start request finish.
   */
  private async prepare(): Promise<void> {
    const hasFrame = this.camera ? await this.camera.frame() : true;
    if (!this.startRequested) return;
    if (hasFrame) {
      this.startAttempted = true;
      await action(this.fetcher, this.owner, this.actionSequence++, 'start', {});
      this.end.textContent = 'End session';
      this.status.textContent = 'Connecting to Reactor…';
    } else {
      this.status.textContent = 'Enable a camera before starting.';
      this.start.disabled = false;
    }
    this.startRequested = false;
  }

  /**
   * Send queued prompt, pointer, and sound changes in order.
   * @returns When this cycle's pending controls have been sent.
   */
  private async sendControls(): Promise<void> {
    if (!this.ready) return;
    if (this.pendingPrompt !== undefined) {
      await action(this.fetcher, this.owner, this.actionSequence++, 'prompt', {
        prompt: this.pendingPrompt,
      });
      this.pendingPrompt = undefined;
      this.status.textContent = 'Prompt sent. The model applies changes to later frames.';
    }
    const next = this.pointers.shift();
    if (next) {
      await action(this.fetcher, this.owner, this.actionSequence++, 'pointer', next);
      this.pointerPreview?.confirm(next);
    }
    const audioPrompt = this.sound?.takePrompt();
    if (audioPrompt !== undefined) {
      await action(this.fetcher, this.owner, this.actionSequence++, 'audio_prompt', {
        prompt: audioPrompt,
      });
      this.status.textContent = 'Sound prompt sent. The model applies changes to later audio.';
    }
  }

  /**
   * Read and display the session's current state.
   * @returns The validated session status.
   */
  private async refresh(): Promise<LiveStatus> {
    const reply = await exchange(
      this.fetcher,
      this.owner,
      this.sequence++,
      {},
      this.ending,
      this.previewSequence,
      AbortSignal.timeout(2000),
    );
    this.display(reply);
    return reply;
  }

  /**
   * Send input and check whether a rejection coincided with session completion.
   * @param reply - The status received before sending input.
   * @returns The current status after input is sent or recording ends.
   */
  private async sendInput(reply: LiveStatus): Promise<LiveStatus> {
    try {
      await this.prepare();
      await this.sendControls();
      return reply;
    } catch (error) {
      // Recording can end between the status reply and the next input upload.
      const current = await this.refresh();
      if (!current.closed && !current.finishing) throw error;
      return current;
    }
  }

  /**
   * Exchange status, apply pending input, and handle session completion.
   * @returns When one status and input cycle finishes.
   */
  private async cycle(): Promise<void> {
    let reply = await this.refresh();
    if (!this.ending && !reply.closed && !reply.finishing) reply = await this.sendInput(reply);
    if (reply.closed) this.finish(reply);
    else if (reply.finishing) {
      this.camera?.close();
      this.status.textContent = 'Ending the session…';
    }
  }

  /**
   * Exchange status and input until the session ends or the panel closes.
   * @returns When polling ends and the panel shows its final state.
   */
  private async poll(): Promise<void> {
    try {
      while (!this.finished && !this.abort.signal.aborted) {
        await this.cycle();
        if (this.finished) break;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } catch (error) {
      this.stop(error instanceof Error ? error.message : 'The live connection ended.');
      this.finished = true;
      this.end.textContent = 'Close';
    }
  }

  /** Show the session panel and begin the local status exchange. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.start.focus();
    void this.poll();
  }
}

/**
 * Open one controls panel for each validated session invitation.
 * @param value - The untrusted ComfyUI event payload.
 * @param fetcher - ComfyUI's local API client.
 */
export function openControls(value: unknown, fetcher: Fetcher): void {
  const owner = controls(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new ControlPanel(owner, fetcher);
  panel.show();
}
