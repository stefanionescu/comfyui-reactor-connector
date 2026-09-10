import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import type { Invitation } from '#web/live/api.ts';
import { browserLimits, browserPatterns } from '#config/web/browser.ts';

export type Controls = Invitation & {
  prompt: string;
  promptCharacterLimit: number;
  webcam: boolean;
  pointer: boolean;
  sound: boolean;
  audioPrompt: string;
  audioPromptCharacterLimit: number;
};

/**
 * Validate a live session invitation and expose its supported inputs.
 * @param value - The untrusted ComfyUI event payload.
 * @returns The controls invitation, or undefined when it is invalid.
 */
export function parseControlsInvitation(value: unknown): Controls | undefined {
  if (typeof value !== 'object' || value === null) return;
  const document = value as Record<string, unknown>;
  if (
    typeof document.lease !== 'string' ||
    !browserPatterns.lease.test(document.lease) ||
    typeof document.capability !== 'string' ||
    !browserPatterns.capability.test(document.capability) ||
    typeof document.model !== 'string' ||
    typeof document.model_title !== 'string' ||
    document.model_title.length < 1 ||
    document.model_title.length > 200 ||
    typeof document.prompt !== 'string' ||
    typeof document.prompt_limit !== 'number' ||
    document.prompt_limit < 1 ||
    !Number.isSafeInteger(document.prompt_limit) ||
    document.prompt.length > document.prompt_limit ||
    typeof document.webcam !== 'boolean' ||
    typeof document.pointer !== 'boolean' ||
    typeof document.sound !== 'boolean' ||
    typeof document.audio_prompt !== 'string' ||
    typeof document.audio_prompt_limit !== 'number' ||
    !Number.isSafeInteger(document.audio_prompt_limit) ||
    document.audio_prompt_limit < 1 ||
    document.audio_prompt.length > document.audio_prompt_limit ||
    typeof document.duration_seconds !== 'number' ||
    !Number.isFinite(document.duration_seconds) ||
    document.duration_seconds <= 0
  )
    return;
  return {
    lease: document.lease,
    capability: document.capability,
    model: document.model,
    modelTitle: document.model_title,
    durationSeconds: document.duration_seconds,
    axes: {},
    prompt: document.prompt,
    promptCharacterLimit: document.prompt_limit,
    webcam: document.webcam,
    pointer: document.pointer,
    sound: document.sound,
    audioPrompt: document.audio_prompt,
    audioPromptCharacterLimit: document.audio_prompt_limit,
  };
}

/**
 * Send one ordered live action through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param owner - The session lease and private control capability.
 * @param sequence - The increasing action sequence for this panel.
 * @param name - The supported action name.
 * @param fields - The fields required by that action.
 * @returns When the server accepts the action; failures throw an error.
 */
export async function sendAction(
  fetcher: Fetcher,
  owner: Pick<Invitation, 'lease' | 'capability'>,
  sequence: number,
  name: string,
  fields: Record<string, unknown>,
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
      fields,
    }),
  });
  if (!response.ok) throw new Error(translate('live.actionRejected'));
}
