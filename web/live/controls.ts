import type { Fetcher } from '#web/http.ts';
import { exchange } from '#web/live/api.ts';
import { Webcam } from '#web/live/webcam.ts';
import { pause } from '#web/live/polling.ts';
import { translate } from '#web/language.ts';
import { button, element } from '#web/dom.ts';
import { SoundControls } from '#web/live/sound.ts';
import { sendAction } from '#web/live/commands.ts';
import { PointerPreview } from '#web/live/pointer.ts';
import { browserLimits } from '#config/web/browser.ts';
import { DragInput, type Pointer } from '#web/live/drag.ts';
import { message, setTextAttribute, setText } from '#web/localization.ts';
import { type Controls, type LiveStatus, parseControlsInvitation } from '#web/live/schema.ts';

const panels = new Set<string>();

/** Own a live session's prompt, webcam, sound, and pointer controls. */
class ControlPanel {
  private readonly prior = document.activeElement;

  private readonly abort = new AbortController();

  private readonly dialog = element('dialog');

  private readonly image = element('img');

  private readonly status = element('p', message('controls.chooseInput'));

  private readonly prompt = element('textarea');

  private readonly start = button(message('controls.start'));

  private readonly update = button(message('live.applyPrompt'));

  private readonly end = button(message('cancel'));

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
    this.dialog.className = 'reactor-dialog reactor-controls';
    setTextAttribute(this.dialog, 'aria-label', message('controls.title'));
    setTextAttribute(this.image, 'alt', message('live.output'));
    this.image.hidden = true;
    this.pointerPreview = owner.pointer
      ? new PointerPreview(this.image, this.abort.signal)
      : undefined;
    this.status.setAttribute('role', 'status');
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.promptCharacterLimit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.update.disabled = true;
    this.sound = owner.sound
      ? new SoundControls(owner.audioPrompt, owner.audioPromptCharacterLimit)
      : undefined;
    this.camera = owner.webcam ? new Webcam(owner, fetcher, this.stop.bind(this)) : undefined;
    if (owner.pointer) new DragInput(this.image, this.abort.signal, this.queuePointer.bind(this));
    this.bindActions();
    this.appendContent();
  }

  /** Build the preview, supported inputs, and session actions. */
  private appendContent(): void {
    this.dialog.append(
      element('h2', message('controls.title')),
      element(
        'p',
        message('live.duration', {
          model: this.owner.modelTitle,
          seconds: this.owner.durationSeconds,
        }),
      ),
      element('p', message('controls.recordingNotice')),
    );
    if (this.camera) this.dialog.append(this.camera.view);
    this.dialog.append(this.pointerPreview?.view ?? this.image);
    if (this.owner.pointer) this.dialog.append(element('p', message('controls.dragInstructions')));
    if (this.pointerPreview) this.dialog.append(this.pointerPreview.status);
    const label = element(
      'label',
      message(this.owner.promptKind === 'edit' ? 'live.editPrompt' : 'live.scenePrompt'),
    );
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
    this.dialog.addEventListener('click', (event) => {
      if (event.target === this.start) {
        this.startRequested = true;
        this.start.disabled = true;
      } else if (event.target === this.end) {
        if (this.finished) this.dialog.close();
        else this.stop();
      }
    });
    this.update.addEventListener('click', () => {
      if (!this.prompt.value.trim() && !this.owner.allowEmptyPrompt) {
        setText(this.status, message('controls.emptyPrompt'));
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.update.disabled = true;
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
    if (this.pointers.length >= browserLimits.maxPendingInputs) {
      this.stop(translate('controls.pointerRateExceeded'));
      return;
    }
    this.pointers.push(next);
  }

  /**
   * Stop sending input while waiting for the server to end the session.
   * @param message - The reason shown in the panel.
   */
  private stop(message = translate('live.ending')): void {
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
    this.ready = reply.controlsReady && !reply.finishing && !this.ending;
    this.prompt.disabled = !this.ready;
    this.sound?.setReady(this.ready);
    if (this.ready && !wasReady) setText(this.status, message('controls.recording'));
    this.update.disabled = !this.ready || this.pendingPrompt !== undefined;
    if (reply.preview) {
      this.image.src = `data:image/jpeg;base64,${reply.preview}`;
      this.image.hidden = false;
    }
    this.previewSequence = reply.previewSequence;
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
    if (!reply.terminationConfirmed) setText(this.status, message('controls.connectionClosed'));
    else if (!this.startAttempted) setText(this.status, message('controls.recordingNotStarted'));
    else setText(this.status, reply.failed ? message('live.discarded') : message('live.ended'));
    setText(this.end, message('close'));
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
      await sendAction(this.fetcher, this.owner, this.actionSequence++, 'start', {});
      setText(this.end, message('live.endSession'));
      setText(this.status, message('controls.connecting'));
    } else {
      setText(this.status, message('controls.cameraRequired'));
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
      await sendAction(this.fetcher, this.owner, this.actionSequence++, 'prompt', {
        prompt: this.pendingPrompt,
      });
      this.pendingPrompt = undefined;
      setText(this.status, message('controls.promptSent'));
    }
    const next = this.pointers.shift();
    if (next) {
      await sendAction(this.fetcher, this.owner, this.actionSequence++, 'pointer', next);
      this.pointerPreview?.confirm(next);
    }
    const audioPrompt = this.sound?.takePrompt();
    if (audioPrompt !== undefined) {
      await sendAction(this.fetcher, this.owner, this.actionSequence++, 'audio_prompt', {
        prompt: audioPrompt,
      });
      setText(this.status, message('controls.soundSent'));
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
      AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
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
   * @returns Whether the session needs another status update.
   */
  private async cycle(): Promise<boolean> {
    let reply = await this.refresh();
    if (!this.ending && !reply.closed && !reply.finishing) reply = await this.sendInput(reply);
    if (reply.closed) this.finish(reply);
    else if (reply.finishing) {
      this.camera?.close();
      setText(this.status, message('live.ending'));
    }
    return !this.finished;
  }

  /**
   * Exchange status and input until the session ends or the panel closes.
   * @returns When polling ends and the panel shows its final state.
   */
  private async poll(): Promise<void> {
    try {
      while (!this.finished && !this.abort.signal.aborted) {
        if (!(await this.cycle())) break;
        await pause(browserLimits.pollIntervalMilliseconds, this.abort.signal);
      }
    } catch (error) {
      this.stop(error instanceof Error ? error.message : translate('controls.connectionEnded'));
      this.finished = true;
      setText(this.end, message('close'));
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
  const owner = parseControlsInvitation(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new ControlPanel(owner, fetcher);
  panel.show();
}
