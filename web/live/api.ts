import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { cameraAxes } from '#web/live/input.ts';
import { browserLimits, browserPatterns } from '#config/browser.ts';

export type Invitation = {
  lease: string;
  capability: string;
  model: string;
  modelTitle: string;
  durationSeconds: number;
  axes: Record<string, string[]>;
};

export type SceneInvitation = Invitation & { prompt: string; promptCharacterLimit: number };

// eslint-disable-next-line local/no-trivial-functions -- This type guard narrows untrusted event and response values before field access.
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Validate a LingBot session invitation and its supported camera axes.
 * @param value - The untrusted ComfyUI event payload.
 * @returns The scene invitation, or undefined when it is invalid.
 */
export function parseSceneInvitation(value: unknown): SceneInvitation | undefined {
  if (!isRecord(value) || !isRecord(value.axes)) return;
  if (
    typeof value.lease !== 'string' ||
    !browserPatterns.lease.test(value.lease) ||
    typeof value.capability !== 'string' ||
    !browserPatterns.capability.test(value.capability) ||
    typeof value.model !== 'string' ||
    typeof value.model_title !== 'string' ||
    value.model_title.length < 1 ||
    value.model_title.length > 200 ||
    typeof value.prompt !== 'string' ||
    typeof value.prompt_limit !== 'number' ||
    !Number.isSafeInteger(value.prompt_limit) ||
    value.prompt_limit < 1 ||
    value.prompt.length > value.prompt_limit ||
    typeof value.duration_seconds !== 'number' ||
    !Number.isFinite(value.duration_seconds) ||
    value.duration_seconds <= 0
  )
    return;
  const axes: Record<string, string[]> = {};
  const expected = Object.keys(
    cameraAxes(new Set(), Object.hasOwn(value.axes, 'move_longitudinal')),
  );
  if (Object.keys(value.axes).length !== expected.length) return;
  for (const key of expected) {
    const choices = value.axes[key];
    if (
      !Array.isArray(choices) ||
      !choices.includes('idle') ||
      !choices.every((choice): choice is string => typeof choice === 'string')
    )
      return;
    axes[key] = choices;
  }
  return {
    lease: value.lease,
    capability: value.capability,
    model: value.model,
    modelTitle: value.model_title,
    durationSeconds: value.duration_seconds,
    axes,
    prompt: value.prompt,
    promptCharacterLimit: value.prompt_limit,
  };
}

export type LiveStatus = {
  closed: boolean;
  terminationConfirmed: boolean;
  failed: boolean;
  controlsReady: boolean;
  finishing: boolean;
  elapsedSeconds: number;
  previewSequence: number;
  preview: string;
};

/**
 * Send camera input and receive session status through ComfyUI.
 * @param fetcher - ComfyUI's local API client.
 * @param owner - The session invitation and its private control capability.
 * @param sequence - The increasing exchange sequence for this panel.
 * @param axes - Current camera movement and look directions.
 * @param end - Whether to end the session.
 * @param previewSequence - The latest preview already displayed.
 * @param signal - The request deadline or cancellation signal.
 * @param release - Whether to clear previous camera movement immediately.
 * @returns The validated status and optional preview.
 */
export async function exchange(
  fetcher: Fetcher,
  owner: Invitation,
  sequence: number,
  axes: Record<string, string>,
  end: boolean,
  previewSequence: number,
  signal: AbortSignal,
  release = false,
): Promise<LiveStatus> {
  const response = await fetcher('/reactor-inc/v1/live/exchange', {
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
  if (!response.ok) throw new Error(translate('live.unreachable'));
  const value: unknown = await response.json();
  if (
    !isRecord(value) ||
    typeof value.closed !== 'boolean' ||
    typeof value.termination_confirmed !== 'boolean' ||
    typeof value.failed !== 'boolean' ||
    typeof value.controls_ready !== 'boolean' ||
    typeof value.finishing !== 'boolean' ||
    typeof value.elapsed_seconds !== 'number' ||
    !Number.isFinite(value.elapsed_seconds) ||
    typeof value.preview_sequence !== 'number' ||
    !Number.isSafeInteger(value.preview_sequence) ||
    typeof value.preview !== 'string' ||
    value.preview.length > browserLimits.maxPreviewCharacters ||
    !browserPatterns.preview.test(value.preview)
  ) {
    throw new Error(translate('live.invalidStatus'));
  }
  return {
    closed: value.closed,
    terminationConfirmed: value.termination_confirmed,
    failed: value.failed,
    controlsReady: value.controls_ready,
    finishing: value.finishing,
    elapsedSeconds: value.elapsed_seconds,
    previewSequence: value.preview_sequence,
    preview: value.preview,
  };
}
