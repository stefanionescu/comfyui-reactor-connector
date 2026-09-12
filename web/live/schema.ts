import * as v from 'valibot';
import { cameraAxes } from '#web/live/input.ts';
import { browserLimits, browserPatterns } from '#web/browser.ts';

const invitationEntries = {
  lease: v.pipe(v.string(), v.regex(browserPatterns.lease)),
  capability: v.pipe(v.string(), v.regex(browserPatterns.capability)),
  model_title: v.pipe(v.string(), v.minLength(1), v.maxLength(browserLimits.maxTextCharacters)),
  duration_seconds: v.pipe(v.number(), v.finite(), v.gtValue(0)),
  prompt_kind: v.picklist(['scene', 'edit']),
  allow_empty_prompt: v.boolean(),
} as const;

const invitationSchema = v.object(invitationEntries);
type InvitationDocument = v.InferOutput<typeof invitationSchema>;

function buildInvitation(document: InvitationDocument, axes: Record<string, string[]>) {
  const identity = { lease: document.lease, capability: document.capability };
  const presentation = { modelTitle: document.model_title, promptKind: document.prompt_kind };
  return {
    ...identity,
    ...presentation,
    durationSeconds: document.duration_seconds,
    allowEmptyPrompt: document.allow_empty_prompt,
    axes,
  };
}

const promptEntries = {
  prompt: v.string(),
  prompt_limit: v.pipe(v.number(), v.safeInteger(), v.minValue(1)),
} as const;

const axisChoicesSchema = v.pipe(v.array(v.string()), v.includes('idle'));
const axesSchema = v.record(v.string(), axisChoicesSchema);

const sceneInvitationSchema = v.pipe(
  v.object({
    ...invitationSchema.entries,
    ...promptEntries,
    axes: axesSchema,
  }),
  v.check((document) => {
    const promptLength = document.prompt.length;
    const charactersRemaining = document.prompt_limit - promptLength;
    return Number.isSafeInteger(charactersRemaining) && charactersRemaining >= 0;
  }),
  v.check((document) => {
    const hasIndependentAxes = Object.hasOwn(document.axes, 'move_longitudinal');
    const expected = Object.keys(cameraAxes(new Set(), hasIndependentAxes));
    if (Object.keys(document.axes).length !== expected.length) return false;
    for (const name of expected) {
      if (!Object.hasOwn(document.axes, name)) return false;
    }
    return true;
  }),
  v.transform((document) => {
    const invitation = buildInvitation(document, document.axes);
    const prompt = { prompt: document.prompt, promptCharacterLimit: document.prompt_limit };
    return { ...invitation, ...prompt };
  }),
);

const controlsInvitationSchema = v.pipe(
  v.object({
    ...invitationSchema.entries,
    ...promptEntries,
    webcam: v.boolean(),
    pointer: v.boolean(),
    sound: v.boolean(),
    audio_prompt: v.string(),
    audio_prompt_limit: v.pipe(v.number(), v.safeInteger(), v.minValue(1)),
  }),
  v.check((document) => {
    if (document.prompt.length > document.prompt_limit) return false;
    return document.audio_prompt.length <= document.audio_prompt_limit;
  }),
  v.transform((document) => {
    const invitation = buildInvitation(document, {});
    const prompt = { prompt: document.prompt, promptCharacterLimit: document.prompt_limit };
    const audioPrompt = {
      audioPrompt: document.audio_prompt,
      audioPromptCharacterLimit: document.audio_prompt_limit,
    };
    return {
      ...invitation,
      ...prompt,
      ...audioPrompt,
      webcam: document.webcam,
      pointer: document.pointer,
      sound: document.sound,
    };
  }),
);

const liveStatusSchema = v.pipe(
  v.object({
    closed: v.boolean(),
    termination_confirmed: v.boolean(),
    failed: v.boolean(),
    controls_ready: v.boolean(),
    finishing: v.boolean(),
    elapsed_seconds: v.pipe(v.number(), v.finite()),
    preview_sequence: v.pipe(v.number(), v.safeInteger()),
    preview: v.pipe(
      v.string(),
      v.maxLength(browserLimits.maxPreviewCharacters),
      v.regex(browserPatterns.preview),
    ),
  }),
  v.transform((status) => {
    const termination = {
      closed: status.closed,
      terminationConfirmed: status.termination_confirmed,
      failed: status.failed,
    };
    const progress = { controlsReady: status.controls_ready, finishing: status.finishing };
    return {
      ...termination,
      ...progress,
      elapsedSeconds: status.elapsed_seconds,
      previewSequence: status.preview_sequence,
      preview: status.preview,
    };
  }),
);

export type Invitation = ReturnType<typeof buildInvitation>;
export type SceneInvitation = v.InferOutput<typeof sceneInvitationSchema>;
export type Controls = v.InferOutput<typeof controlsInvitationSchema>;
export type LiveStatus = v.InferOutput<typeof liveStatusSchema>;

/**
 * Validate a camera-session invitation before opening its panel.
 * @param value - The untrusted ComfyUI event payload.
 * @returns The scene invitation, or undefined when it is invalid.
 */
export function parseSceneInvitation(value: unknown): SceneInvitation | undefined {
  const result = v.safeParse(sceneInvitationSchema, value);
  if (!result.success) return;
  return result.output;
}

/**
 * Validate an editing-session invitation before opening its panel.
 * @param value - The untrusted ComfyUI event payload.
 * @returns The controls invitation, or undefined when it is invalid.
 */
export function parseControlsInvitation(value: unknown): Controls | undefined {
  const result = v.safeParse(controlsInvitationSchema, value);
  if (!result.success) return;
  return result.output;
}

/**
 * Validate and transform one live polling response.
 * @param value - The untrusted JSON response.
 * @returns The live status, or undefined when it is invalid.
 */
export function parseLiveStatus(value: unknown): LiveStatus | undefined {
  const result = v.safeParse(liveStatusSchema, value);
  if (!result.success) return;
  return result.output;
}
