import { button, element } from '#web/dom.ts';
import { action } from '#web/live/commands.ts';
import { CameraStates } from '#web/live/state.ts';
import type { Fetcher } from '#web/settings/api.ts';
import { CameraInput, cameraKeys } from '#web/live/input.ts';
import { type CameraInvitation, exchange, invitation, type LiveStatus } from '#web/live/api.ts';

const panels = new Set<string>();

/** Own the camera controls and live preview for a LingBot session. */
class CameraPanel {
  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly dialog = element('dialog');

  private readonly status = element('p', 'Connecting the live panel…');

  private readonly elapsed = element('p');

  private readonly prompt = element('textarea');

  private readonly apply = button('Apply prompt');

  private readonly promptStatus = element(
    'p',
    'Prompt changes affect later frames. The starting image stays fixed.',
  );

  private readonly surface = element('div');

  private readonly image = element('img');

  private readonly controls = element('div');

  private readonly end = button('End session');

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
    private readonly owner: CameraInvitation,
    private readonly fetcher: Fetcher,
  ) {
    this.dialog.className = 'reactor-settings reactor-live';
    this.dialog.setAttribute('aria-label', 'Reactor live camera');
    this.status.setAttribute('role', 'status');
    this.promptStatus.setAttribute('role', 'status');
    this.prompt.value = owner.prompt;
    this.prompt.maxLength = owner.prompt_limit;
    this.prompt.rows = 2;
    this.prompt.disabled = this.apply.disabled = true;
    this.surface.className = 'reactor-preview';
    this.surface.tabIndex = 0;
    this.surface.setAttribute(
      'aria-label',
      'Live view. W A S D moves. Arrow keys turn. Escape stops camera movement.',
    );
    this.image.alt = 'Live model output';
    this.image.hidden = true;
    this.surface.append(this.image);
    this.controls.className = 'reactor-actions';
    const labels = [
      'Forward',
      'Back',
      'Move left',
      'Move right',
      'Look left',
      'Look right',
      'Look up',
      'Look down',
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

  /** Build the session header, movement controls, and prompt input. */
  private appendContent(): void {
    const header = element('header');
    header.append(element('h2', 'Reactor live camera'), this.end);
    const promptLabel = element('label', 'Scene prompt ');
    promptLabel.append(this.prompt);
    this.dialog.append(
      header,
      element('p', `${this.owner.modelTitle} · ${this.owner.duration_seconds} seconds of video`),
      element(
        'p',
        'Click the picture, then use W A S D to move and arrow keys to turn. Click a button for a brief movement, or hold it to keep moving. Escape stops camera movement.',
      ),
      this.surface,
      this.controls,
      promptLabel,
      this.apply,
      this.promptStatus,
      this.status,
      this.elapsed,
      element(
        'p',
        'The preview has fewer frames per second than the saved video and has no sound. Save Video saves the finished recording. Setup and recording use credits. Ending early discards the unfinished video.',
      ),
    );
  }

  /** Bind prompt updates, explicit ending, and focus cleanup. */
  private bindActions(): void {
    this.apply.addEventListener('click', () => {
      if (!this.prompt.value.trim()) {
        this.promptStatus.textContent = 'Enter a scene prompt before applying it.';
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
    this.status.textContent = 'Ending the session…';
  }

  /**
   * Update camera controls and the preview while the panel is visible.
   * @param result - The validated session status.
   */
  private display(result: LiveStatus): void {
    if (this.disposed) return;
    for (const control of this.controls.querySelectorAll('button'))
      control.disabled = !result.controls_ready || this.ending;
    this.prompt.disabled = !result.controls_ready || this.ending;
    this.apply.disabled = this.prompt.disabled || this.pendingPrompt !== undefined;
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
  private displayProgress(result: LiveStatus): void {
    if (result.finishing && !result.closed) {
      this.release();
      this.surface.blur();
      this.end.disabled = true;
      this.status.textContent = 'Ending the session…';
    } else if (!this.ending) {
      this.status.textContent =
        result.controls_ready && result.preview_sequence > 0
          ? 'Live preview. Controls are active.'
          : 'Waiting for model video…';
    }
  }

  /**
   * Show the final session result without implying unconfirmed termination.
   * @param result - The terminal session status.
   */
  private finish(result: LiveStatus): void {
    this.finished = true;
    if (!result.termination_confirmed)
      this.status.textContent =
        'Reactor has not confirmed that the session ended. Wait for its time limit before another run.';
    else
      this.status.textContent = result.failed
        ? 'The session ended without saving a video. Close this panel to view the workflow result.'
        : 'Session ended. Close this panel to view the workflow result.';
  }

  /**
   * Send a queued prompt only while the session accepts controls.
   * @param result - The current session readiness.
   * @returns When the prompt request, if any, finishes.
   */
  private async sendPrompt(result: LiveStatus): Promise<void> {
    if (
      !result.controls_ready ||
      result.finishing ||
      this.ending ||
      this.pendingPrompt === undefined
    )
      return;
    await action(this.fetcher, this.owner, this.actionSequence++, 'prompt', {
      prompt: this.pendingPrompt,
    });
    this.pendingPrompt = undefined;
    this.promptStatus.textContent = 'Prompt sent. Watch the video for the change.';
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
      this.status.textContent =
        'The live connection was lost. The connector will ask Reactor to stop after five seconds without a browser connection. Check Reactor Usage to confirm the session has ended before another run.';
    } finally {
      this.release();
      this.controller.abort();
      this.end.disabled = false;
      this.end.textContent = 'Close';
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
export function openLive(value: unknown, fetcher: Fetcher): void {
  const owner = invitation(value);
  if (!owner || panels.has(owner.lease)) return;
  panels.add(owner.lease);
  const panel = new CameraPanel(owner, fetcher);
  panel.show();
}
