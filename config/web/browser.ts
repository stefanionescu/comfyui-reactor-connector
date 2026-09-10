/** Request deadlines, local input buffering, and response size limits for the interface. */
export const browserLimits = {
  requestTimeoutMilliseconds: 10_000,
  discoveryTimeoutMilliseconds: 30_000,
  pollIntervalMilliseconds: 100,
  actionTimeoutMilliseconds: 2_000,
  inputNudgeMilliseconds: 250,
  maxPendingInputs: 8,
  maxPreviewCharacters: 350_000,
  maxCalculatorSeconds: 3_600,
  maxTextCharacters: 200,
  maxErrorCharacters: 1_024,
  maxRetrievalTimeCharacters: 40,
  maxModelNodeIds: 100,
  maxModels: 1_024,
} as const;

/** Camera capture and pointer input values used by the live interface. */
export const browserInput = {
  pointerCenter: 0.5,
  pointerMinimum: 0,
  pointerMaximum: 1,
  pointerStep: 0.03,
  cameraWidth: 640,
  cameraHeight: 480,
  cameraIdealFrameRate: 12,
  cameraMaxFrameRate: 24,
  cameraJpegQuality: 0.8,
} as const;

/** Formats accepted from the local ComfyUI API. */
export const browserPatterns = {
  lease: /^[a-f0-9]{32}$/,
  revision: /^[a-f0-9]{64}$/,
  preview: /^[A-Za-z0-9+/]*={0,2}$/,
  capability: /^[A-Za-z0-9_-]{43}$/,
  documentation: /^https:\/\/docs\.reactor\.inc\/model-api-reference\/[a-z0-9._-]+\/overview$/,
  nodeId: /^ReactorInc[A-Za-z0-9]+$/,
  settingName: /^[a-z][a-z_]+$/,
} as const;
