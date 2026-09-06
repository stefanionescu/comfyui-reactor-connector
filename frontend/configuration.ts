export const fields = [
  ["max_capture_seconds", "Maximum video duration (seconds)"],
  ["max_session_seconds", "Maximum session duration (seconds)"],
  ["connect_timeout_seconds", "Connection timeout (seconds)"],
  ["first_frame_timeout_seconds", "First-frame timeout (seconds)"],
  ["cleanup_timeout_seconds", "Disconnect timeout (seconds)"],
  ["queue_timeout_seconds", "Queue wait timeout (seconds)"],
  ["max_upload_megabytes", "Maximum upload size (MiB)"],
  ["max_capture_megabytes", "Maximum video file size (MiB)"],
  ["max_queue_megabytes", "Maximum queued frame data (MiB)"],
] as const;

export type FieldName = (typeof fields)[number][0];
export type Configuration = {
  revision: string;
  credentialSource: "missing" | "saved" | "environment";
  mutationAllowed: boolean;
  settings: Record<FieldName, number> & {
    catalog_auto_check: boolean;
    catalog_interval_hours: number;
  };
};
export type Fetcher = (route: string, options: RequestInit) => Promise<Response>;

function record(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("ComfyUI returned an invalid Reactor settings response.");
  }
  return value as Record<string, unknown>;
}

export function parseConfiguration(value: unknown): Configuration {
  const document = record(value);
  const settings = record(document.settings);
  const credential = record(document.credential);
  if (
    typeof document.revision !== "string" ||
    !/^[a-f0-9]{64}$/.test(document.revision) ||
    typeof document.mutation_allowed !== "boolean" ||
    typeof credential.source !== "string" ||
    !["missing", "saved", "environment"].includes(credential.source)
  ) {
    throw new Error("ComfyUI returned an invalid Reactor settings response.");
  }
  if (
    typeof settings.catalog_auto_check !== "boolean" ||
    typeof settings.catalog_interval_hours !== "number" ||
    !Number.isInteger(settings.catalog_interval_hours) ||
    settings.catalog_interval_hours < 1 ||
    settings.catalog_interval_hours > 3600
  )
    throw new Error("ComfyUI returned invalid model check settings.");
  const validated = {
    catalog_auto_check: settings.catalog_auto_check,
    catalog_interval_hours: settings.catalog_interval_hours,
  } as Configuration["settings"];
  for (const [name] of fields) {
    const value = settings[name];
    if (typeof value !== "number" || !Number.isInteger(value) || value < 1 || value > 3600) {
      throw new Error("ComfyUI returned an invalid Reactor limit.");
    }
    validated[name] = value;
  }
  return {
    revision: document.revision,
    credentialSource: credential.source as Configuration["credentialSource"],
    mutationAllowed: document.mutation_allowed,
    settings: validated,
  };
}

export async function requestConfiguration(
  fetcher: Fetcher,
  signal: AbortSignal,
  route = "/status",
  method = "GET",
  body?: unknown,
): Promise<Configuration> {
  const options: RequestInit = {
    method,
    cache: "no-store",
    credentials: "same-origin",
    signal: AbortSignal.any([signal, AbortSignal.timeout(10_000)]),
    headers: { "Content-Type": "application/json", "X-Reactor-Comfy": "1" },
  };
  if (body !== undefined) options.body = JSON.stringify(body);
  let response: Response;
  try {
    response = await fetcher(`/reactor-inc/v1${route}`, options);
  } catch {
    throw new Error("Cannot reach Reactor settings. Check ComfyUI and try again.");
  }
  let document: unknown;
  try {
    document = await response.json();
  } catch {
    throw new Error("ComfyUI returned an unreadable Reactor settings response.");
  }
  if (!response.ok) {
    const error = record(document).error;
    throw new Error(
      typeof error === "string" && error.length <= 1024
        ? error
        : "ComfyUI could not save Reactor settings.",
    );
  }
  return parseConfiguration(document);
}
