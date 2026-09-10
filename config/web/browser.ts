/** Request deadlines, local input buffering, and response size limits for the interface. */
export const browserLimits = {
  requestTimeoutMilliseconds: 10_000,
  pollIntervalMilliseconds: 100,
  actionTimeoutMilliseconds: 2_000,
  maxPendingInputs: 8,
  maxPreviewCharacters: 350_000,
  maxCalculatorSeconds: 3_600,
} as const;

/** Formats accepted from the local ComfyUI API. */
export const browserPatterns = {
  lease: /^[a-f0-9]{32}$/,
  revision: /^[a-f0-9]{64}$/,
  preview: /^[A-Za-z0-9+/]*={0,2}$/,
  capability: /^[A-Za-z0-9_-]{43}$/,
} as const;
