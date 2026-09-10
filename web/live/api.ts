import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { cameraAxes } from '#web/live/input.ts';
import { browserRoutes } from '#config/web/routes.ts';
import { browserLimits, browserPatterns } from '#config/web/browser.ts';

export type Invitation = {
  lease: string;
  capability: string;
  model: string;
  modelTitle: string;
  durationSeconds: number;
  axes: Record<string, string[]>;
};

export type SceneInvitation = Invitation & { prompt: string; promptCharacterLimit: number };

function isRecord(value: unknown): value is Record<string, unknown> {
  if (typeof value !== 'object' || value === null) return false;
  return !Array.isArray(value);
}

function axisChoices(value: unknown): string[] | undefined {
  if (!Array.isArray(value) || !value.includes('idle')) return;
  for (const choice of value) {
    if (typeof choice !== 'string') return;
  }
  return value as string[];
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
    value.model_title.length > browserLimits.maxTextCharacters ||
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
  const axes = new Map<string, string[]>();
  const offered = new Map(Object.entries(value.axes));
  const expected = Object.keys(
    cameraAxes(new Set(), Object.hasOwn(value.axes, 'move_longitudinal')),
  );
  if (offered.size !== expected.length) return;
  for (const key of expected) {
    const choices = axisChoices(offered.get(key));
    if (!choices) return;
    axes.set(key, choices);
  }
  return {
    lease: value.lease,
    capability: value.capability,
    model: value.model,
    modelTitle: value.model_title,
    durationSeconds: value.duration_seconds,
    axes: Object.fromEntries(axes),
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
