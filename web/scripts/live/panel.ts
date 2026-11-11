import { element } from '#web/dom.ts';
import type { Fetcher } from '#web/http.ts';
import { endSession } from '#web/live/api.ts';
import { sendAction } from '#web/live/commands.ts';
import type { Invitation } from '#web/live/schema.ts';
import { message, type MessageKey } from '#web/text.ts';

/**
Own what every live session panel shares: its dialog, preview, request order, and closing steps.
*/
export abstract class LivePanel {
    protected readonly previousFocus = document.activeElement;

    protected readonly abort = new AbortController();

    protected readonly dialog = element('dialog');

    protected readonly image = element('img');

    protected readonly promptStatus = element('p');

    /**
    The edited prompt that waits for the next status exchange.
    */
    protected pendingPrompt: string | undefined;

    protected actionSequence = 0;

    protected ending = false;

    protected finished = false;

    protected disposed = false;

    protected sequence = 0;

    protected previewSequence = 0;

    protected abstract readonly owner: Invitation;

    protected abstract readonly fetcher: Fetcher;

    /**
    The leases of the open panels of this kind, so each session opens one panel.
    */
    protected abstract readonly panels: Set<string>;

    /**
    Send the edited prompt, then say that the server accepted it.

    @param prompt - The edited prompt.
    @param sent - The message that confirms the prompt.
    @returns When the server accepts the prompt.
    */
    protected async sendPendingPrompt(prompt: string, sent: MessageKey): Promise<void> {
        await sendAction(this.fetcher, this.owner, this.actionSequence++, 'prompt', { prompt }, this.abort.signal);
        this.pendingPrompt = undefined;
        this.promptStatus.textContent = message(sent);
    }

    /**
    Release panel resources and give the final end request its own deadline.
    */
    dispose(): void {
        if (this.disposed) return;
        this.disposed = true;
        this.ending = true;
        this.abort.abort();
        if (!this.finished) endSession(this.fetcher, this.owner, this.sequence++, this.previewSequence);
        this.image.removeAttribute('src');
        this.dialog.remove();
        this.panels.delete(this.owner.lease);
        if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected) this.previousFocus.focus();
    }
}
