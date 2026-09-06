import type { Fetcher } from "./configuration.ts";

export type Invitation = {
  lease: string;
  capability: string;
  model: string;
  modelTitle: string;
  duration_seconds: number;
  axes: Record<string, string[]>;
};

export type CameraInvitation = Invitation & { prompt: string; prompt_limit: number };

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function invitation(value: unknown): CameraInvitation | undefined {
  if (!record(value) || !record(value.axes)) return;
  if (
    typeof value.lease !== "string" ||
    !/^[a-f0-9]{32}$/.test(value.lease) ||
    typeof value.capability !== "string" ||
    !/^[A-Za-z0-9_-]{43}$/.test(value.capability) ||
    typeof value.model !== "string" ||
    !["reactor/lingbot", "reactor/lingbot-world-2"].includes(value.model) ||
    typeof value.prompt !== "string" ||
    value.prompt.length > 2000 ||
    value.prompt_limit !== 1000 ||
    typeof value.duration_seconds !== "number" ||
    !Number.isFinite(value.duration_seconds) ||
    value.duration_seconds <= 0 ||
    value.duration_seconds > 3600
  )
    return;
  const axes: Record<string, string[]> = {};
  const allowed: Record<string, string[]> = {
    movement: ["idle", "forward", "back", "strafe_left", "strafe_right"],
    move_longitudinal: ["idle", "forward", "back"],
    move_lateral: ["idle", "strafe_left", "strafe_right"],
    look_horizontal: ["idle", "left", "right"],
    look_vertical: ["idle", "up", "down"],
  };
  const expected =
    value.model === "reactor/lingbot"
      ? ["movement", "look_horizontal", "look_vertical"]
      : ["move_longitudinal", "move_lateral", "look_horizontal", "look_vertical"];
  if (Object.keys(value.axes).length !== expected.length) return;
  for (const key of expected) {
    const choices = value.axes[key];
    if (!Array.isArray(choices) || JSON.stringify(choices) !== JSON.stringify(allowed[key])) return;
    axes[key] = allowed[key] ?? [];
  }
  return {
    lease: value.lease,
    capability: value.capability,
    model: value.model,
    modelTitle: value.model === "reactor/lingbot" ? "LingBot" : "LingBot World 2",
    duration_seconds: value.duration_seconds,
    axes,
    prompt: value.prompt,
    prompt_limit: value.prompt_limit,
  };
}

export type LiveStatus = {
  closed: boolean;
  termination_confirmed: boolean;
  failed: boolean;
  controls_ready: boolean;
  finishing: boolean;
  elapsed_seconds: number;
  preview_sequence: number;
  preview: string;
};

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
  const response = await fetcher("/reactor-inc/v1/live/exchange", {
    method: "POST",
    cache: "no-store",
    signal,
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
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
  if (!response.ok) throw new Error("Live controls could not reach their session.");
  const value: unknown = await response.json();
  if (
    !record(value) ||
    typeof value.closed !== "boolean" ||
    typeof value.termination_confirmed !== "boolean" ||
    typeof value.failed !== "boolean" ||
    typeof value.controls_ready !== "boolean" ||
    typeof value.finishing !== "boolean" ||
    typeof value.elapsed_seconds !== "number" ||
    !Number.isFinite(value.elapsed_seconds) ||
    typeof value.preview_sequence !== "number" ||
    !Number.isSafeInteger(value.preview_sequence) ||
    typeof value.preview !== "string" ||
    value.preview.length > 350_000 ||
    !/^[A-Za-z0-9+/]*={0,2}$/.test(value.preview)
  ) {
    throw new Error("The live panel received an invalid status.");
  }
  return {
    closed: value.closed,
    termination_confirmed: value.termination_confirmed,
    failed: value.failed,
    controls_ready: value.controls_ready,
    finishing: value.finishing,
    elapsed_seconds: value.elapsed_seconds,
    preview_sequence: value.preview_sequence,
    preview: value.preview,
  };
}
