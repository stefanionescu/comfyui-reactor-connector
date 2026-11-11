import * as v from 'valibot';

import { browserLimits } from '#web/browser.ts';

const errorTextSchema = v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxErrorCharacters));
const publicErrorSchema = v.object({ error: v.optional(errorTextSchema) });

/**
Read a bounded message from a failed local API response.

@param value - The untrusted JSON response.
@returns The reviewed server message, or undefined for a malformed error response.
*/
export function parsePublicError(value: unknown): string | undefined {
    const result = v.safeParse(publicErrorSchema, value);
    if (!result.success) return undefined;
    return result.output.error;
}
