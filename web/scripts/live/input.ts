import { browserLimits } from '#web/browser.ts';

/**
 * Convert held keys to the model's supported movement axes.
 *
 * @param keys - The keys currently held or briefly pressed.
 * @param hasIndependentAxes - Whether the model accepts independent movement axes.
 * @returns Movement and look directions for the model.
 */
export function cameraAxes(keys: ReadonlySet<string>, hasIndependentAxes: boolean): Record<string, string> {
    /**
     * Resolve an opposing pair of keys.
     *
     * @param firstKey - The key for the first direction.
     * @param secondKey - The key for the opposite direction.
     * @param firstDirection - The model's first direction value.
     * @param secondDirection - The model's opposite direction value.
     * @returns The chosen direction, or idle when the user holds neither key or both.
     */
    function direction(firstKey: string, secondKey: string, firstDirection: string, secondDirection: string): string {
        if (keys.has(firstKey) === keys.has(secondKey)) return 'idle';
        return keys.has(firstKey) ? firstDirection : secondDirection;
    }
    const forward = direction('w', 's', 'forward', 'back');
    const lateral = direction('a', 'd', 'strafe_left', 'strafe_right');
    return {
        ...(hasIndependentAxes
            ? { move_longitudinal: forward, move_lateral: lateral }
            : { movement: forward === 'idle' ? lateral : forward }),
        look_horizontal: direction('ArrowLeft', 'ArrowRight', 'left', 'right'),
        look_vertical: direction('ArrowUp', 'ArrowDown', 'up', 'down'),
    };
}

const cameraKeys = new Set(['w', 's', 'a', 'd', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']);

/**
 * Release held input when the window loses focus, the page hides, or the panel closes.
 *
 * @param release - Clear every held input.
 * @param signal - The panel's listener lifetime.
 */
export function releaseOnLeave(release: () => void, signal: AbortSignal): void {
    window.addEventListener('blur', release, { signal });
    document.addEventListener(
        'visibilitychange',
        () => {
            if (document.hidden) release();
        },
        { signal },
    );
    signal.addEventListener('abort', release, { once: true });
}

/**
 * Find the camera direction button that an event reached.
 *
 * @param event - A pointer, click, or key event on the button container.
 * @returns The button and its direction key, or undefined when the event reached no direction button.
 */
function findDirectionButton(event: Event): { button: HTMLButtonElement; key: string } | undefined {
    const target = event.target;
    if (!(target instanceof HTMLButtonElement)) return undefined;
    const key = target.dataset['key'];
    if (key === undefined || key === '') return undefined;
    return { button: target, key };
}

/** Combine keyboard, held buttons, and short presses into camera input. */
export class CameraInput {
    private readonly keyboard = new Set<string>();

    private readonly pointers = new Map<number, string>();

    private readonly pointerStarted = new Map<number, number>();

    private readonly nudges = new Map<string, ReturnType<typeof setTimeout>>();

    private lastHold: { key: string; milliseconds: number } | undefined;

    /**
     * Bind camera input for the lifetime of the panel.
     *
     * @param surface - The keyboard camera surface.
     * @param controls - The camera direction buttons.
     * @param signal - The panel's listener lifetime.
     * @param update - Receive the combined keys and explicit release requests.
     */
    constructor(
        surface: HTMLElement,
        controls: HTMLElement,
        signal: AbortSignal,
        private readonly update: (keys: ReadonlySet<string>, release?: boolean) => void,
    ) {
        surface.addEventListener(
            'keydown',
            (event) => {
                const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
                if (cameraKeys.has(key)) {
                    event.preventDefault();
                    event.stopPropagation();
                    this.keyboard.add(key);
                    this.publish();
                } else if (key === 'Escape') {
                    event.preventDefault();
                    event.stopPropagation();
                    this.release();
                    surface.blur();
                }
            },
            { signal },
        );
        surface.addEventListener(
            'keyup',
            (event) => {
                const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
                if (cameraKeys.has(key)) {
                    event.preventDefault();
                    event.stopPropagation();
                    this.keyboard.delete(key);
                    this.publish();
                }
            },
            { signal },
        );
        surface.addEventListener('blur', this.release.bind(this), { signal });
        this.bindButtons(controls, signal);
        releaseOnLeave(this.release.bind(this), signal);
    }

    /**
     * Send combined input after a key, pointer, or timer changes.
     *
     * @param release - Whether the user explicitly released all input.
     */

    private publish(release = false): void {
        const keys = new Set(this.keyboard);
        for (const key of this.pointers.values()) keys.add(key);
        for (const key of this.nudges.keys()) keys.add(key);
        this.update(keys, release);
    }

    /**
     * Keep a short press visible for the next server update.
     *
     * @param key - The direction key to hold briefly.
     * @param milliseconds - Remaining duration of the short press.
     */
    private nudge(key: string, milliseconds: number): void {
        const previous = this.nudges.get(key);
        if (previous !== undefined) clearTimeout(previous);
        this.nudges.set(
            key,

            setTimeout(() => {
                this.nudges.delete(key);
                this.publish();
            }, milliseconds),
        );
    }

    /** Clear every held input and timer, then send an explicit release. */
    release(): void {
        this.keyboard.clear();
        this.pointers.clear();
        this.pointerStarted.clear();
        this.lastHold = undefined;
        for (const timer of this.nudges.values()) clearTimeout(timer);
        this.nudges.clear();
        this.publish(true);
    }

    /**
     * Bind mouse, touch, keyboard, and assistive button activation.
     *
     * @param controls - The container for direction buttons.
     * @param signal - The panel's listener lifetime.
     */
    private bindButtons(controls: HTMLElement, signal: AbortSignal): void {
        controls.addEventListener(
            'pointerdown',
            (event) => {
                const direction = findDirectionButton(event);
                if (direction === undefined || event.button !== 0) return;
                event.preventDefault();
                direction.button.setPointerCapture(event.pointerId);
                this.lastHold = undefined;
                this.pointers.set(event.pointerId, direction.key);
                this.pointerStarted.set(event.pointerId, performance.now());
                this.publish();
            },
            { signal },
        );
        for (const kind of ['pointerup', 'pointercancel', 'lostpointercapture'] as const)
            controls.addEventListener(kind, this.releasePointer.bind(this), { signal });
        for (const kind of ['keydown', 'keyup'] as const)
            controls.addEventListener(kind, this.buttonKey.bind(this), { signal });
        controls.addEventListener('focusout', this.release.bind(this), { signal });
        controls.addEventListener(
            'click',
            (event) => {
                const direction = findDirectionButton(event);
                if (direction === undefined) return;
                if (event.detail !== 0 && this.lastHold?.key === direction.key) return;
                this.nudge(direction.key, browserLimits.inputNudgeMilliseconds);
                this.publish();
            },
            { signal },
        );
    }

    /**
     * Finish a held button and keep a press shorter than a nudge.
     *
     * @param event - The pointer release or cancellation.
     */
    private releasePointer(event: PointerEvent): void {
        const key = this.pointers.get(event.pointerId);
        const started = this.pointerStarted.get(event.pointerId);
        if (event.type === 'pointerup' && key !== undefined && started !== undefined) {
            this.lastHold = { key, milliseconds: performance.now() - started };
            if (this.lastHold.milliseconds < browserLimits.inputNudgeMilliseconds)
                this.nudge(key, browserLimits.inputNudgeMilliseconds - this.lastHold.milliseconds);
        }
        this.pointers.delete(event.pointerId);
        this.pointerStarted.delete(event.pointerId);
        this.publish();
    }

    /**
     * Treat Space and Enter as a held direction on a focused button.
     *
     * @param event - A key press or release on the button container.
     */
    private buttonKey(event: KeyboardEvent): void {
        const direction = findDirectionButton(event);
        if (direction === undefined || ![' ', 'Enter'].includes(event.key)) return;
        event.preventDefault();
        event.stopPropagation();
        if (event.type === 'keydown') this.keyboard.add(direction.key);
        else this.keyboard.delete(direction.key);
        this.publish();
    }
}
