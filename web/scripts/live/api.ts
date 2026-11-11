import { browserLimits } from '#web/browser.ts';
import type { Fetcher } from '#web/http.ts';
import { type Invitation, type LiveStatus, parseLiveStatus } from '#web/live/schema.ts';
import { browserRoutes } from '#web/routes.ts';
import { parsePublicError } from '#web/schema.ts';
import { message } from '#web/text.ts';

/**
One status exchange: its order, camera input, deadline, and whether it ends the session.
*/
export type ExchangeRequest = {
    /**
    The increasing exchange sequence for this panel.
    */
    sequence: number;
    /**
    Current camera movement and look directions.
    */
    axes: Record<string, string>;
    /**
    Whether to end the session.
    */
    end: boolean;
    /**
    The latest preview already displayed.
    */
    previewSequence: number;
    /**
    The request deadline or cancellation signal.
    */
    signal: AbortSignal;
    /**
    Whether to clear previous camera movement immediately.
    */
    release?: boolean;
};

/**
Send camera input and receive session status through ComfyUI.

@param fetcher - ComfyUI's local API client.
@param owner - The session invitation and its private control capability.
@param request - The exchange's sequence, input, and deadline.
@returns The validated status and optional preview.
*/
export async function exchange(fetcher: Fetcher, owner: Invitation, request: ExchangeRequest): Promise<LiveStatus> {
    const { sequence, axes, end, previewSequence, signal, release = false } = request;
    const response = await fetcher(browserRoutes.live.exchange, {
        method: 'POST',
        cache: 'no-store',
        signal,
        headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
        body: JSON.stringify({
            lease: owner.lease,
            capability: owner.capability,
            sequence,
            axes,
            end,
            release,
            preview_sequence: previewSequence,
        }),
    });
    if (!response.ok) {
        let document: unknown;
        try {
            document = await response.json();
        } catch {
            throw new Error(message('live.unreachable'));
        }
        throw new Error(parsePublicError(document) ?? message('live.unreachable'));
    }
    const status = parseLiveStatus(await response.json());
    signal.throwIfAborted();
    if (!status) throw new Error(message('live.invalidStatus'));
    return status;
}

/**
Send one final end request after the panel cancels its other requests.

@param fetcher - ComfyUI's local API client.
@param owner - The session invitation and its private capability.
@param sequence - A sequence newer than all requests made by this panel.
@param previewSequence - The last preview received.
*/
export function endSession(fetcher: Fetcher, owner: Invitation, sequence: number, previewSequence: number): void {
    const axes = Object.fromEntries(Object.keys(owner.axes).map((axis) => [axis, 'idle']));
    exchange(fetcher, owner, {
        sequence,
        axes,
        end: true,
        previewSequence,
        signal: AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
        release: true,
    }).catch(() => {
        // The server's client timeout still ends the lease if this final request fails.
    });
}
