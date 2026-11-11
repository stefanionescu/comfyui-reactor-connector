import { browserLimits } from '#web/browser.ts';
import { button, element } from '#web/dom.ts';
import type { Fetcher } from '#web/http.ts';
import { exchange } from '#web/live/api.ts';
import { sendAction } from '#web/live/commands.ts';
import { DragInput, type Pointer } from '#web/live/drag.ts';
import { promptSection, sessionHeader } from '#web/live/layout.ts';
import { LivePanel } from '#web/live/panel.ts';
import { PointerPreview } from '#web/live/pointer.ts';
import { pause } from '#web/live/polling.ts';
import { type ControlsInvitation, type LiveStatus, parseControlsInvitation } from '#web/live/schema.ts';
import { SoundControls } from '#web/live/sound.ts';
import { Webcam } from '#web/live/webcam.ts';
import { message } from '#web/text.ts';

const panels = new Set<string>();

/**
Own a live session's prompt, webcam, sound, and pointer controls.
*/
class ControlPanel extends LivePanel {
    private readonly status = element('p', message('controls.chooseInput'));

    private readonly prompt = element('textarea');

    private readonly start = button(message('controls.start'));

    private readonly update = button(message('live.applyPrompt'));

    private readonly end = button(message('cancel'));

    private readonly pointerPreview: PointerPreview | undefined;

    private readonly camera: Webcam | undefined;

    private readonly sound: SoundControls | undefined;

    private readonly pointers: Pointer[] = [];

    private ready = false;

    private startRequested = false;

    private startAttempted = false;

    protected override readonly panels = panels;

    /**
    Build only the controls supported by this session.

    @param owner - The validated session invitation.
    @param fetcher - ComfyUI's local API client.
    */
    constructor(
        protected override readonly owner: ControlsInvitation,
        protected override readonly fetcher: Fetcher,
    ) {
        super();
        try {
            this.dialog.className = 'reactor-dialog reactor-controls';
            this.dialog.setAttribute('aria-label', message('controls.title', { model: this.owner.modelTitle }));
            this.image.setAttribute('alt', message('live.output'));
            this.image.hidden = true;
            this.pointerPreview = owner.pointer ? new PointerPreview(this.image, this.abort.signal) : undefined;
            this.status.setAttribute('role', 'status');
            this.prompt.value = owner.prompt;
            this.prompt.maxLength = owner.promptCharacterLimit;
            this.prompt.rows = 2;
            this.prompt.disabled = this.update.disabled = true;
            this.sound = owner.sound
                ? new SoundControls(owner.audioPrompt, owner.audioPromptCharacterLimit)
                : undefined;
            this.camera = owner.webcam ? new Webcam(owner, fetcher, this.stop.bind(this)) : undefined;
            if (owner.pointer) new DragInput(this.image, this.queuePointer.bind(this)).listen(this.abort.signal);
            this.bindActions();
            this.appendContent();
        } catch (error) {
            this.dispose();
            throw error;
        }
    }

    /**
    Build the preview, supported inputs, and session actions.
    */
    private appendContent(): void {
        const header = sessionHeader(
            message('controls.title', { model: this.owner.modelTitle }),
            this.owner,
            this.status,
        );
        this.promptStatus.setAttribute('role', 'status');
        this.dialog.append(header);
        if (this.camera) this.dialog.append(this.camera.view);
        this.dialog.append(this.pointerPreview?.view ?? this.image);
        if (this.pointerPreview) this.dialog.append(this.pointerPreview.status);
        this.dialog.append(
            promptSection(
                message(this.owner.promptKind === 'edit' ? 'live.editPrompt' : 'live.scenePrompt'),
                this.prompt,
                this.update,
                this.promptStatus,
            ),
        );
        if (this.sound) this.dialog.append(this.sound.view);
        const footer = element('footer');
        const actions = element('div');
        actions.className = 'reactor-actions';
        this.start.className = 'reactor-primary';
        actions.append(this.end, this.start);
        footer.append(actions);
        const help = element('details');
        help.className = 'reactor-help';
        help.append(
            element('summary', message('live.help')),
            element('p', message('live.previewNotice')),
            element('p', message('live.recordingNotice')),
        );
        if (this.owner.pointer) {
            const instructions = element('p', message('controls.dragInstructions'));
            instructions.id = `reactor-pointer-help-${crypto.randomUUID()}`;
            this.image.setAttribute('aria-describedby', instructions.id);
            help.append(instructions);
        }
        this.dialog.append(help, footer);
    }

    /**
    Bind start, prompt, stop, and dialog cleanup actions.
    */
    private bindActions(): void {
        this.dialog.addEventListener('click', (event) => {
            if (event.target === this.start) {
                this.startRequested = true;
                this.start.disabled = true;
            } else if (event.target === this.end) this.dispose();
        });
        this.update.addEventListener('click', () => {
            if (!this.prompt.value.trim() && !this.owner.allowEmptyPrompt) {
                this.promptStatus.textContent = message('controls.emptyPrompt');
                return;
            }
            this.pendingPrompt = this.prompt.value;
            this.update.disabled = true;
        });
        this.dialog.addEventListener('cancel', (event) => {
            event.preventDefault();
            this.dispose();
        });
        this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
    }

    /**
    Keep pointer releases while combining consecutive held moves.

    @param next - The next normalized pointer update.
    */
    private queuePointer(next: Pointer): void {
        if (!this.ready || this.ending) return;
        this.pointerPreview?.move(next);
        const previous = this.pointers.at(-1);
        if (previous?.active === true && next.active) this.pointers.pop();
        if (this.pointers.length >= browserLimits.maxPendingInputs) {
            this.stop(message('controls.pointerRateExceeded'));
            return;
        }
        this.pointers.push(next);
    }

    /**
    Stop sending input while waiting for the server to end the session.

    @param reason - The reason shown in the panel.
    */
    private stop(reason: string = message('live.ending')): void {
        this.ending = true;
        this.ready = false;
        this.start.disabled = this.update.disabled = true;
        this.sound?.setReady(false);
        this.pointerPreview?.stop();
        this.status.textContent = reason;
        this.camera?.close();
    }

    /**
    Apply current readiness and the latest preview.

    @param reply - The validated session status.
    */
    private display(reply: LiveStatus): void {
        const isAlreadyReady = this.ready;
        this.ready = reply.controlsReady && !reply.finishing && !this.ending;
        this.prompt.disabled = !this.ready;
        this.sound?.setReady(this.ready);
        if (this.ready && !isAlreadyReady) this.status.textContent = message('controls.recording');
        this.update.disabled = !this.ready || this.pendingPrompt !== undefined;
        if (reply.preview) {
            this.image.src = `data:image/jpeg;base64,${reply.preview}`;
            this.image.hidden = false;
        }
        this.previewSequence = reply.previewSequence;
    }

    /**
    Release devices and explain how the session ended.

    @param reply - The terminal session status.
    */
    private finish(reply: LiveStatus): void {
        this.finished = true;
        this.camera?.close();
        this.start.hidden = true;
        this.start.disabled = this.update.disabled = true;
        this.sound?.setReady(false);
        this.pointerPreview?.stop();
        if (!reply.terminationConfirmed) this.status.textContent = message('controls.connectionClosed');
        else if (this.startAttempted) {
            this.status.textContent = message(reply.failed ? 'live.discarded' : 'live.ended');
        } else {
            this.status.textContent = message('controls.recordingNotStarted');
        }
        this.end.textContent = message('close');
    }

    /**
    Upload camera input and apply a requested start once a frame is ready.

    @returns When this cycle's camera upload and start request finish.
    */
    private async prepare(): Promise<void> {
        const hasFrame = this.camera ? await this.camera.frame() : true;
        if (!this.startRequested) return;
        if (hasFrame) {
            this.startAttempted = true;
            await sendAction(this.fetcher, this.owner, this.actionSequence++, 'start', {}, this.abort.signal);
            this.end.textContent = message('live.endSession');
            this.status.textContent = message('controls.connecting');
        } else {
            this.status.textContent = message('controls.cameraRequired');
            this.start.disabled = false;
        }
        this.startRequested = false;
    }

    /**
    Send queued prompt, pointer, and sound changes in order.

    @returns When the server accepts this cycle's pending controls.
    */
    private async sendControls(): Promise<void> {
        if (!this.ready) return;
        if (this.pendingPrompt !== undefined) await this.sendPendingPrompt(this.pendingPrompt, 'controls.promptSent');
        const next = this.pointers.shift();
        if (next) {
            await sendAction(this.fetcher, this.owner, this.actionSequence++, 'pointer', next, this.abort.signal);
            this.pointerPreview?.confirm(next);
        }
        const audioPrompt = this.sound?.takePrompt();
        if (audioPrompt === undefined) {
            return;
        }

        await sendAction(
            this.fetcher,
            this.owner,
            this.actionSequence++,
            'audio_prompt',
            {
                prompt: audioPrompt,
            },
            this.abort.signal,
        );
        if (this.sound) this.sound.status.textContent = message('controls.soundSent');
    }

    /**
    Read and display the session's current state.

    @returns The validated session status.
    */
    private async refresh(): Promise<LiveStatus> {
        const reply = await exchange(this.fetcher, this.owner, {
            sequence: this.sequence++,
            axes: {},
            end: this.ending,
            previewSequence: this.previewSequence,
            signal: AbortSignal.any([this.abort.signal, AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds)]),
        });
        this.display(reply);
        return reply;
    }

    /**
    Send input and check whether a rejection coincided with session completion.

    @param reply - The status received before sending input.
    @returns The current status after the server accepts the input or recording ends.
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
    Exchange status, apply pending input, and handle session completion.

    @returns Whether the session needs another status update.
    */
    private async cycle(): Promise<boolean> {
        let reply = await this.refresh();
        if (!this.ending && !reply.closed && !reply.finishing) reply = await this.sendInput(reply);
        if (reply.closed) this.finish(reply);
        else if (reply.finishing) {
            this.camera?.close();
            this.status.textContent = message('live.ending');
        }
        return !this.finished;
    }

    /**
    Exchange status and input until the session ends or the panel closes.

    @returns When polling ends and the panel shows its final state.
    */
    private async poll(): Promise<void> {
        try {
            while (!this.abort.signal.aborted && (await this.cycle())) {
                await pause(browserLimits.pollIntervalMilliseconds, this.abort.signal);
            }
        } catch (error) {
            if (this.disposed) return;
            this.stop(error instanceof Error ? error.message : message('controls.connectionEnded'));
            this.finished = true;
            this.start.hidden = true;
            this.end.textContent = message('close');
        }
        if (this.finished) this.dialog.classList.add('reactor-finished');
    }

    /**
    Stop the camera and pointer input, then close the panel.
    */
    override dispose(): void {
        if (this.disposed) return;
        this.ready = false;
        this.camera?.close();
        this.pointerPreview?.stop();
        super.dispose();
    }

    /**
    Show the session panel and begin the local status exchange.
    */
    show(): void {
        document.body.append(this.dialog);
        this.dialog.showModal();
        (this.camera?.enable ?? this.start).focus();
        this.poll().catch(reportError);
    }
}

/**
Open one controls panel for each validated session invitation.

@param value - The untrusted ComfyUI event payload.
@param fetcher - ComfyUI's local API client.
*/
export function openControls(value: unknown, fetcher: Fetcher): void {
    const owner = parseControlsInvitation(value);
    if (!owner || panels.has(owner.lease)) return;
    panels.add(owner.lease);
    let panel: ControlPanel | undefined;
    try {
        panel = new ControlPanel(owner, fetcher);
        panel.show();
    } catch (error) {
        panels.delete(owner.lease);
        panel?.dispose();
        throw error;
    }
}
