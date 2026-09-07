import type { Invitation } from '#web/live/api.ts';
import type { Fetcher } from '#web/settings/api.ts';

const modelTitles = new Map<string, string>([
  ['reactor/helios', 'Helios'],
  ['reactor/longlive-v2', 'LongLive'],
  ['reactor/sana-streaming', 'SANA'],
  ['xmax/x2', 'X2'],
  ['reactor/visko-orbis-stable', 'Visko Stable'],
  ['reactor/visko-orbis-dynamic', 'Visko Dynamic'],
]);

export type Controls = Invitation & {
  prompt: string;
  prompt_limit: number;
  webcam: boolean;
  pointer: boolean;
  sound: boolean;
  audio_prompt: string;
};

/**
 * Validate a live session invitation and expose its supported inputs.
 * @param value - The untrusted ComfyUI event payload.
 * @returns The controls invitation, or undefined when it is invalid.
 */
export function controls(value: unknown): Controls | undefined {
  if (typeof value !== 'object' || value === null) return;
  const v = value as Record<string, unknown>;
  const modelTitle = typeof v.model === 'string' ? modelTitles.get(v.model) : undefined;
  if (
    typeof v.lease !== 'string' ||
    !/^[a-f0-9]{32}$/.test(v.lease) ||
    typeof v.capability !== 'string' ||
    !/^[A-Za-z0-9_-]{43}$/.test(v.capability) ||
    typeof v.model !== 'string' ||
    modelTitle === undefined ||
    typeof v.prompt !== 'string' ||
    typeof v.prompt_limit !== 'number' ||
    v.prompt_limit < 1 ||
    v.prompt_limit > 20_000 ||
    typeof v.webcam !== 'boolean' ||
    typeof v.pointer !== 'boolean' ||
    typeof v.sound !== 'boolean' ||
    typeof v.audio_prompt !== 'string' ||
    v.audio_prompt.length > 2000 ||
    typeof v.duration_seconds !== 'number' ||
    !Number.isFinite(v.duration_seconds) ||
    v.duration_seconds <= 0 ||
    v.duration_seconds > 3600
  )
    return;
  return {
    lease: v.lease,
    capability: v.capability,
    model: v.model,
    modelTitle,
    duration_seconds: v.duration_seconds,
    axes: {},
    prompt: v.prompt,
    prompt_limit: v.prompt_limit,
    webcam: v.webcam,
    pointer: v.pointer,
    sound: v.sound,
    audio_prompt: v.audio_prompt,
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
    signal: AbortSignal.timeout(2000),
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      action: name,
      data,
    }),
  });
  if (!response.ok) throw new Error('The live action was not accepted. The session is ending.');
}
