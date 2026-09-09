import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { button, element } from '#web/dom.ts';
import { CameraStates } from '#web/live/state.ts';
import { browserLimits } from '#config/browser.ts';
import { sendAction } from '#web/live/commands.ts';
import { CameraInput, cameraKeys } from '#web/live/input.ts';
import { message, setTextAttribute, setText } from '#web/localization.ts';

import {
  type SceneInvitation,
  exchange,
  parseSceneInvitation,
  type LiveStatus,
} from '#web/live/api.ts';

const panels = new Set<string>();

/** Own the camera controls and live preview for a LingBot session. */
class ScenePanel {
  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly dialog = element('dialog');

  private readonly status = element('p', message('live.connectingPanel'));

  private readonly elapsed = element('p');

  private readonly prompt = element('textarea');

  private readonly apply = button(message('live.applyPrompt'));

  private readonly promptStatus = element('p', message('live.promptNotice'));

  private readonly surface = element('div');

  private readonly image = element('img');

  private readonly controls = element('div');

  private readonly end = button(message('live.endSession'));

  private readonly states: CameraStates;

  private readonly release: () => void;

  private pendingPrompt: string | undefined;

  private actionSequence = 0;

  private ending = false;

  private finished = false;

  private disposed = false;

  private sequence = 0;

  private previewSequence = 0;

  /**
   * Build camera controls for the invited model.
   * @param owner - The validated camera session invitation.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(
    private readonly owner: SceneInvitation,
    private readonly fetcher: Fetcher,
  ) {
    this.dialog.className = 'reactor-dialog reactor-live';
    setTextAttribute(this.dialog, 'aria-label', message('live.sceneTitle'));
    this.status.setAttribute('role', 'status');
    this.promptStatus.setAttribute('role', 'status');
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.promptCharacterLimit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.apply.disabled = true;
    this.surface.className = 'reactor-preview';
    this.surface.tabIndex = 0;
    setTextAttribute(this.surface, 'aria-label', message('live.movementLabel'));
    setTextAttribute(this.image, 'alt', message('live.output'));
    this.image.hidden = true;
    this.surface.append(this.image);
    this.controls.className = 'reactor-actions';
    const labels = [
      translate('live.forward'),
      translate('live.back'),
      translate('live.moveLeft'),
      translate('live.moveRight'),
      translate('live.lookLeft'),
      translate('live.lookRight'),
      translate('live.lookUp'),
      translate('live.lookDown'),
    ];
    for (const [index, key] of cameraKeys.entries()) {
      const control = button(labels[index] ?? key);
      control.dataset.key = key;
      control.disabled = true;
      this.controls.append(control);
    }
    this.states = new CameraStates(owner.model.endsWith('world-2'));
    const input = new CameraInput(
      this.surface,
      this.controls,
      this.controller.signal,
      (keys, urgent) => this.states.update(keys, urgent),
    );
    this.release = input.release.bind(input);
    this.bindActions();
    this.appendContent();
  }

  /** Build the session header, movement parseControlsInvitation, and prompt input. */
  private appendContent(): void {
    const header = element('header');
    header.append(element('h2', message('live.sceneTitle')), this.end);
    const promptLabel = element('label', message('live.scenePrompt'));
    promptLabel.append(this.prompt);
    this.dialog.append(
      header,
      element(
        'p',
        message('live.duration', {
          model: this.owner.modelTitle,
          seconds: this.owner.durationSeconds,
        }),
      ),
      element('p', message('live.movementInstructions')),
      this.surface,
      this.controls,
      promptLabel,
      this.apply,
      this.promptStatus,
      this.status,
      this.elapsed,
      element('p', message('live.recordingNotice')),
    );
  }

  /** Bind prompt updates, explicit ending, and focus cleanup. */
  private bindActions(): void {
    this.apply.addEventListener('click', () => {
      if (!this.prompt.value.trim()) {
        setText(this.promptStatus, message('live.emptyScenePrompt'));
        return;
      }
      this.pendingPrompt = this.prompt.value;
      this.apply.disabled = true;
    });
    this.end.addEventListener('click', () => {
      if (this.finished) this.dialog.close();
      else this.stop();
    });
    this.dialog.addEventListener('cancel', (event) => {
      event.preventDefault();
      this.release();
      this.surface.blur();
    });
    this.dialog.addEventListener(
      'close',
      () => {
        this.stop();
        this.disposed = true;
        this.controller.abort();
        this.image.removeAttribute('src');
        panels.delete(this.owner.lease);
        this.dialog.remove();
        if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
          this.previousFocus.focus();
      },
      { once: true },
    );
  }

  /** Stop camera movement and request the end of the session. */
  private stop(): void {
    this.ending = true;
    this.release();
    this.end.disabled = true;
    this.apply.disabled = this.prompt.disabled = true;
    setText(this.status, message('live.ending'));
  }

  /**
   * Update camera controls and the preview while the panel is visible.
   * @param result - The validated session status.
   */
  private display(result: LiveStatus): void {
    if (this.disposed) return;
    for (const control of this.controls.querySelectorAll('button'))
      control.disabled = !result.controlsReady || this.ending;
    this.prompt.disabled = !result.controlsReady || this.ending;
    this.apply.disabled = this.prompt.disabled || this.pendingPrompt !== undefined;
    setText(
      this.elapsed,
      message('live.elapsed', {
        seconds: Math.round(result.elapsedSeconds * 10) / 10,
      }),
    );
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
  private displayProgress(result: LiveStatus): void {
    if (result.finishing && !result.closed) {
      this.release();
      this.surface.blur();
      this.end.disabled = true;
      setText(this.status, message('live.ending'));
    } else if (!this.ending) {
      setText(
        this.status,
        result.controlsReady && result.previewSequence > 0
          ? message('live.previewReady')
          : message('live.waitingVideo'),
      );
    }
  }

  /**
   * Show the final session result without implying unconfirmed termination.
   * @param result - The terminal session status.
   */
  private finish(result: LiveStatus): void {
    this.finished = true;
    if (!result.terminationConfirmed) setText(this.status, message('live.unconfirmedEnd'));
    else setText(this.status, result.failed ? message('live.discarded') : message('live.ended'));
  }

  /**
   * Send a queued prompt only while the session accepts controls.
   * @param result - The current session readiness.
   * @returns When the prompt request, if any, finishes.
   */
  private async sendPrompt(result: LiveStatus): Promise<void> {
    if (
      !result.controlsReady ||
      result.finishing ||
      this.ending ||
      this.pendingPrompt === undefined
    )
      return;
    await sendAction(this.fetcher, this.owner, this.actionSequence++, 'prompt', {
      prompt: this.pendingPrompt,
    });
    this.pendingPrompt = undefined;
    setText(this.promptStatus, message('live.promptSent'));
  }

  /**
   * Exchange input and status until the server ends the session.
   * @returns When polling and listener cleanup finish.
   */
  private async poll(): Promise<void> {
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
          AbortSignal.timeout(2000),
          input.release,
        );
        this.previewSequence = result.previewSequence;
        this.display(result);
        if (result.closed) this.finish(result);
        else {
          await this.sendPrompt(result);
          await new Promise((fulfill) =>
            setTimeout(fulfill, browserLimits.pollIntervalMilliseconds),
          );
        }
      }
    } catch {
      this.finished = true;
      setText(this.status, message('live.connectionLost'));
    } finally {
      this.release();
      this.controller.abort();
      this.end.disabled = false;
      setText(this.end, message('close'));
      this.prompt.disabled = this.apply.disabled = true;
      for (const control of this.controls.querySelectorAll('button')) control.disabled = true;
      if (this.disposed) panels.delete(this.owner.lease);
    }
  }

  /** Show the panel, focus camera input, and begin exchanging session status. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    this.surface.focus();
    void this.poll();
  }
}

/**
 * Open one camera panel for each validated session invitation.
 * @param value - The untrusted ComfyUI event payload.
 * @param fetcher - ComfyUI's local API client.
 */
export function openSceneControls(value: unknown, fetcher: Fetcher): void {
  const owner = parseSceneInvitation(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new ScenePanel(owner, fetcher);
  panel.show();
}
