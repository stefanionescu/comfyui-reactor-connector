import type { Fetcher } from '#web/http.ts';
import { pause } from '#web/live/polling.ts';
import { button, element } from '#web/dom.ts';
import { browserLimits } from '#web/browser.ts';
import { CameraInput } from '#web/live/input.ts';
import { CameraStates } from '#web/live/state.ts';
import { sendAction } from '#web/live/commands.ts';
import { exchange, endSession } from '#web/live/api.ts';
import { releaseText, message, setTextAttribute, setText } from '#web/localization.ts';
import { type SceneInvitation, parseSceneInvitation, type LiveStatus } from '#web/live/schema.ts';

const panels = new Set<string>();

/** Own the camera controls and live preview for a LingBot session. */
class ScenePanel {
  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly dialog = element('dialog');

  private readonly status = element('p', message('live.connectingPanel'));

  private readonly elapsed = element('small');

  private readonly prompt = element('textarea');

  private readonly apply = button(message('live.applyPrompt'));

  private readonly promptStatus = element('p');

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
    try {
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
      const labels = {
        w: message('live.forward'),
        s: message('live.back'),
        a: message('live.moveLeft'),
        d: message('live.moveRight'),
        ArrowLeft: message('live.lookLeft'),
        ArrowRight: message('live.lookRight'),
        ArrowUp: message('live.lookUp'),
        ArrowDown: message('live.lookDown'),
      };
      for (const [key, label] of Object.entries(labels)) {
        const control = button(label);
        control.dataset.key = key;
        control.disabled = true;
        this.controls.append(control);
      }
      this.states = new CameraStates(Object.hasOwn(owner.axes, 'move_longitudinal'));
      const input = new CameraInput(
        this.surface,
        this.controls,
        this.controller.signal,
        this.states.update.bind(this.states),
      );
      this.release = input.release.bind(input);
      this.bindActions();
      this.appendContent();
    } catch (error) {
      this.dispose();
      throw error;
    }
  }

  /** Build the session header, movement controls, and prompt input. */
  private appendContent(): void {
    const header = element('header');
    const session = element('div');
    session.className = 'reactor-session-status';
    session.append(this.status, this.elapsed);
    header.append(element('h2', message('live.sceneTitle')), session);
    const footer = element('footer');
    footer.append(this.end);
    const promptLabel = element('label', message('live.scenePrompt'));
    promptLabel.append(this.prompt);
    const help = element('details');
    help.className = 'reactor-help';
    help.append(
      element('summary', message('live.help')),
      element('p', message('live.movementInstructions')),
      element('p', message('live.promptNotice')),
      element('p', message('live.previewNotice')),
      element('p', message('live.recordingNotice')),
    );
    this.dialog.append(
      header,
      element(
        'p',
        message('live.duration', {
          model: this.owner.modelTitle,
          seconds: this.owner.durationSeconds,
        }),
      ),
      this.surface,
      this.controls,
      promptLabel,
      this.apply,
      this.promptStatus,
      help,
      footer,
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
    this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
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
    await sendAction(
      this.fetcher,
      this.owner,
      this.actionSequence++,
      'prompt',
      {
        prompt: this.pendingPrompt,
      },
      this.controller.signal,
    );
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
          AbortSignal.any([
            this.controller.signal,
            AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
          ]),
          input.release,
        );
        this.previewSequence = result.previewSequence;
        this.display(result);
        if (result.closed) this.finish(result);
        else {
          await this.sendPrompt(result);
          await pause(browserLimits.pollIntervalMilliseconds, this.controller.signal);
        }
      }
    } catch {
      if (this.disposed) return;
      this.finished = true;
      setText(this.status, message('live.connectionLost'));
    } finally {
      this.release();
      this.controller.abort();
      this.finishPolling();
    }
  }

  /** Leave completed panels readable without recreating labels after disposal. */
  private finishPolling(): void {
    if (this.disposed) return;
    this.end.disabled = false;
    setText(this.end, message('close'));
    this.prompt.disabled = this.apply.disabled = true;
    for (const control of this.controls.querySelectorAll('button')) control.disabled = true;
  }

  /** Release panel resources and give the final end request its own deadline. */
  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.ending = true;
    this.controller.abort();
    if (!this.finished)
      void endSession(this.fetcher, this.owner, this.sequence++, this.previewSequence);
    this.image.removeAttribute('src');
    for (const root of [
      this.dialog,
      this.image,
      this.status,
      this.prompt,
      this.end,
      this.elapsed,
      this.apply,
      this.promptStatus,
      this.surface,
      this.controls,
    ]) {
      releaseText(root);
    }
    this.dialog.remove();
    panels.delete(this.owner.lease);
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
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
  let panel: ScenePanel | undefined;
  try {
    panel = new ScenePanel(owner, fetcher);
    panel.show();
  } catch (error) {
    panels.delete(owner.lease);
    panel?.dispose();
    throw error;
  }
}
