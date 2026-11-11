import { element } from '#web/dom.ts';
import type { Pointer } from '#web/live/drag.ts';
import { message } from '#web/text.ts';

/**
The pointer position shows as a percentage of the image size.
*/
const PERCENT = 100;

export class PointerPreview {
    readonly #marker = element('span');

    readonly #state = element('span');

    readonly #position = element('span');

    readonly #image: HTMLImageElement;

    #pointer: Pointer | undefined;

    readonly view = element('div');

    readonly status = element('p');

    /**
    Show pointer position alongside the output image.

    @param image - The model output used for dragging.
    @param signal - The panel's listener and observer lifetime.
    */
    constructor(image: HTMLImageElement, signal: AbortSignal) {
        this.#image = image;
        this.view.className = 'reactor-pointer-preview';
        this.#marker.className = 'reactor-pointer-marker';
        this.#marker.hidden = true;
        this.#marker.setAttribute('aria-hidden', 'true');
        this.#state.setAttribute('role', 'status');
        this.status.hidden = true;
        this.status.append(this.#state, this.#position);
        this.view.append(image, this.#marker);
        const resize = new ResizeObserver(this.#place.bind(this));
        resize.observe(image);
        image.addEventListener('blur', this.#place.bind(this), { signal });
        image.addEventListener('focus', this.#place.bind(this), { signal });
        signal.addEventListener('abort', resize.disconnect.bind(resize), { once: true });
    }

    #place(): void {
        const pointer = this.#pointer;
        const isHidden =
            pointer === undefined || this.#image.hidden !== false || document.activeElement !== this.#image;
        this.#marker.hidden = isHidden;
        if (isHidden) return;
        this.#marker.style.left = `${String(this.#image.offsetLeft + pointer.x * this.#image.clientWidth)}px`;
        this.#marker.style.top = `${String(this.#image.offsetTop + pointer.y * this.#image.clientHeight)}px`;
    }

    /**
    Move the marker to the user's latest pointer position.

    @param pointer - The normalized image coordinates and hold state.
    */
    move(pointer: Pointer): void {
        this.#pointer = pointer;
        this.status.hidden = false;
        this.#position.textContent = message('pointer.position', {
            x: Math.round(pointer.x * PERCENT),
            y: Math.round(pointer.y * PERCENT),
        });
        this.#place();
    }

    /**
    Announce a hold or release after the server accepts it.

    @param pointer - The pointer update accepted by the server.
    */
    confirm(pointer: Pointer): void {
        const key = pointer.active ? 'pointer.held' : 'pointer.released';
        if (this.#state.textContent !== message(key)) this.#state.textContent = message(key);
    }

    /**
    Hide the marker and announce that pointer input has stopped.
    */
    stop(): void {
        this.#pointer = undefined;
        this.#marker.hidden = true;
        if (this.status.hidden === false) this.#state.textContent = message('pointer.stopped');
    }
}
