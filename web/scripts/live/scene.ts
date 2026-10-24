import { message } from '#web/text.ts';
import type { Fetcher } from '#web/http.ts';
import { exchange } from '#web/live/api.ts';
import { pause } from '#web/live/polling.ts';
import { button, element } from '#web/dom.ts';
import { LivePanel } from '#web/live/panel.ts';
import { browserLimits } from '#web/browser.ts';
import { CameraInput } from '#web/live/input.ts';
import { CameraStates } from '#web/live/state.ts';
import { promptSection, sessionHeader } from '#web/live/layout.ts';
import { type LiveStatus, type SceneInvitation, parseSceneInvitation } from '#web/live/schema.ts';

const panels = new Set<string>();

/** The elapsed time shows tenths of a second. */
const ELAPSED_STEPS_PER_SECOND = 10;

/** Own the camera controls and live preview for a LingBot session. */
class ScenePanel extends LivePanel {
    protected override readonly panels = panels;

    private readonly status = element('p', message('live.connectingPanel'));

    private readonly elapsed = element('small');

    private readonly prompt = element('textarea');

    private readonly apply = button(message('live.applyPrompt'));

    private readonly surface = element('div');

    private readonly controls = element('div');

    private readonly end = button(message('live.endSession'));

    private readonly states: CameraStates;

    private readonly release: () => void;

    /**
     * Build camera controls for the invited model.
     *
     * @param owner - The validated camera session invitation.
     * @param fetcher - ComfyUI's local API client.
     */
    constructor(
        protected override readonly owner: SceneInvitation,
        protected override readonly fetcher: Fetcher,
    ) {
        super();
        try {
            this.dialog.className = 'reactor-dialog reactor-live';
            this.dialog.setAttribute('aria-label', message('live.sceneTitle', { model: this.owner.modelTitle }));
            this.status.setAttribute('role', 'status');
            this.promptStatus.setAttribute('role', 'status');
            this.prompt.value = owner.prompt;
            this.prompt.maxLength = owner.promptCharacterLimit;
            this.prompt.rows = 2;
            this.prompt.disabled = this.apply.disabled = true;
            this.surface.className = 'reactor-preview';
            this.surface.tabIndex = 0;
            this.surface.setAttribute('aria-label', message('live.movementLabel'));
            this.image.setAttribute('alt', message('live.output'));
            this.image.hidden = true;
            this.surface.append(this.image, element('p', message('live.waitingVideo')));
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
                control.dataset['key'] = key;
                control.disabled = true;
                this.controls.append(control);
            }
            this.states = new CameraStates(Object.hasOwn(owner.axes, 'move_longitudinal'));
            const input = new CameraInput(
                this.surface,
                this.controls,
                this.abort.signal,
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
        const footer = element('footer');
        footer.append(this.end);
        const help = element('details');
        help.className = 'reactor-help';
        help.append(
            element('summary', message('live.help')),
            element('p', message('live.movementInstructions')),
            element('p', message('live.promptNotice')),
            element('p', message('live.previewNotice')),
            element('p', message('live.recordingNotice')),
        );
        const header = sessionHeader(
            message('live.sceneTitle', { model: this.owner.modelTitle }),
            this.owner,
            this.status,
            this.elapsed,
        );
        this.dialog.append(
            header,
            this.surface,
            this.controls,
            promptSection(message('live.scenePrompt'), this.prompt, this.apply, this.promptStatus),
            help,
            footer,
        );
    }

    /** Bind prompt updates, explicit ending, and focus cleanup. */
    private bindActions(): void {
        this.apply.addEventListener('click', () => {
            if (!this.prompt.value.trim()) {
                this.promptStatus.textContent = message('live.emptyScenePrompt');
                return;
            }
            this.pendingPrompt = this.prompt.value;
            this.apply.disabled = true;
        });
        this.end.addEventListener('click', this.dispose.bind(this));
        this.dialog.addEventListener('cancel', (event) => {
            event.preventDefault();
            this.release();
            this.surface.blur();
        });
        this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
    }

    /**
     * Update camera controls and the preview while the panel is visible.
     *
     * @param result - The validated session status.
     */
    private display(result: LiveStatus): void {
        if (this.disposed) return;
        for (const control of this.controls.querySelectorAll('button'))
            control.disabled = !result.controlsReady || this.ending;
        this.prompt.disabled = !result.controlsReady || this.ending;
        this.apply.disabled = this.prompt.disabled || this.pendingPrompt !== undefined;
        this.elapsed.textContent = message('live.elapsed', {
            seconds: Math.round(result.elapsedSeconds * ELAPSED_STEPS_PER_SECOND) / ELAPSED_STEPS_PER_SECOND,
        });
        if (result.preview) {
            this.image.src = `data:image/jpeg;base64,${result.preview}`;
            this.image.hidden = false;
        }
        this.displayProgress(result);
    }

    /**
     * Describe whether the model is preparing, recording, or finishing.
     *
     * @param result - The validated session status.
     */
    private displayProgress(result: LiveStatus): void {
        if (result.finishing && !result.closed) {
            this.release();
            this.surface.blur();
            this.end.disabled = true;
            this.status.textContent = message('live.ending');
        } else if (!this.ending) {
            this.status.textContent =
                result.controlsReady && result.previewSequence > 0
                    ? message('live.previewReady')
                    : message('live.waitingVideo');
        }
    }

    /**
     * Show the final session result without implying unconfirmed termination.
     *
     * @param result - The terminal session status.
     */
    private finish(result: LiveStatus): void {
        this.finished = true;
        if (result.terminationConfirmed) {
            this.status.textContent = result.failed ? message('live.discarded') : message('live.ended');
        } else {
            this.status.textContent = message('live.unconfirmedEnd');
        }
    }

    /**
     * Send a queued prompt only while the session accepts controls.
     *
     * @param result - The current session readiness.
     * @returns When the prompt request, if any, finishes.
     */
    private async sendPrompt(result: LiveStatus): Promise<void> {
        if (!result.controlsReady || result.finishing || this.ending || this.pendingPrompt === undefined) return;
        await this.sendPendingPrompt(this.pendingPrompt, 'live.promptSent');
    }

    /**
     * Exchange input and status until the server ends the session.
     *
     * @returns When polling and listener cleanup finish.
     */
    private async poll(): Promise<void> {
        try {
            while (!this.finished) {
                const input = this.states.take();
                const result = await exchange(this.fetcher, this.owner, {
                    sequence: this.sequence++,
                    axes: input.axes,
                    end: this.ending,
                    previewSequence: this.previewSequence,
                    signal: AbortSignal.any([
                        this.abort.signal,
                        AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
                    ]),
                    release: input.release,
                });
                this.previewSequence = result.previewSequence;
                this.display(result);
                if (result.closed) this.finish(result);
                else {
                    await this.sendPrompt(result);
                    await pause(browserLimits.pollIntervalMilliseconds, this.abort.signal);
                }
            }
        } catch {
            if (this.disposed) return;
            this.finished = true;
            this.status.textContent = message('live.connectionLost');
        } finally {
            this.release();
            this.abort.abort();
            this.finishPolling();
        }
    }

    /** Leave completed panels readable without recreating labels after disposal. */
    private finishPolling(): void {
        if (this.disposed) return;
        this.end.disabled = false;
        this.end.textContent = message('close');
        this.prompt.disabled = this.apply.disabled = true;
        for (const control of this.controls.querySelectorAll('button')) control.disabled = true;
    }

    /** Show the panel, focus camera input, and begin exchanging session status. */
    show(): void {
        document.body.append(this.dialog);
        this.dialog.showModal();
        this.surface.focus();
        this.poll().catch(reportError);
    }
}

/**
 * Open one camera panel for each validated session invitation.
 *
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
