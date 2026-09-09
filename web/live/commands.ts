import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import type { Invitation } from '#web/live/api.ts';
import { browserLimits, browserPatterns } from '#config/browser.ts';

export type Controls = Invitation & {
  prompt: string;
  promptLimit: number;
  webcam: boolean;
  pointer: boolean;
  sound: boolean;
  audioPrompt: string;
  audioPromptLimit: number;
};

/**
 * Validate a live session invitation and expose its supported inputs.
 * @param value - The untrusted ComfyUI event payload.
 * @returns The controls invitation, or undefined when it is invalid.
 */
export function controls(value: unknown): Controls | undefined {
  if (typeof value !== 'object' || value === null) return;
  const v = value as Record<string, unknown>;
  if (
    typeof v.lease !== 'string' ||
    !browserPatterns.lease.test(v.lease) ||
    typeof v.capability !== 'string' ||
    !browserPatterns.capability.test(v.capability) ||
    typeof v.model !== 'string' ||
    typeof v.model_title !== 'string' ||
    v.model_title.length < 1 ||
    v.model_title.length > 200 ||
    typeof v.prompt !== 'string' ||
    typeof v.prompt_limit !== 'number' ||
    v.prompt_limit < 1 ||
    !Number.isSafeInteger(v.prompt_limit) ||
    v.prompt.length > v.prompt_limit ||
    typeof v.webcam !== 'boolean' ||
    typeof v.pointer !== 'boolean' ||
    typeof v.sound !== 'boolean' ||
    typeof v.audio_prompt !== 'string' ||
    typeof v.audio_prompt_limit !== 'number' ||
    !Number.isSafeInteger(v.audio_prompt_limit) ||
    v.audio_prompt_limit < 1 ||
    v.audio_prompt.length > v.audio_prompt_limit ||
    typeof v.duration_seconds !== 'number' ||
    !Number.isFinite(v.duration_seconds) ||
    v.duration_seconds <= 0
  )
    return;
  return {
    lease: v.lease,
    capability: v.capability,
    model: v.model,
    modelTitle: v.model_title,
    durationSeconds: v.duration_seconds,
    axes: {},
    prompt: v.prompt,
    promptLimit: v.prompt_limit,
    webcam: v.webcam,
    pointer: v.pointer,
    sound: v.sound,
    audioPrompt: v.audio_prompt,
    audioPromptLimit: v.audio_prompt_limit,
  };
}

/**
 * Send one ordered live action through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param owner - The session lease and private control capability.
 * @param sequence - The increasing action sequence for this panel.
 * @param name - The supported action name.
 * @param data - The fields required by that action.
 * @returns When the server accepts the action; failures throw an error.
 */
export async function action(
  fetcher: Fetcher,
  owner: Pick<Invitation, 'lease' | 'capability'>,
  sequence: number,
  name: string,
  data: Record<string, unknown>,
): Promise<void> {
  const response = await fetcher('/reactor-inc/v1/live/action', {
    method: 'POST',
    cache: 'no-store',
    signal: AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      action: name,
      data,
    }),
  });
  if (!response.ok) throw new Error(translate('live.actionRejected'));
}
