import type { Fetcher } from '#web/http.ts';
import { browserPatterns } from '#config/browser.ts';
import { translate, formatDate } from '#web/language.ts';
import { message, type Message } from '#web/localization.ts';

export type Model = {
  key: string;
  name: string;
  title: string;
  connect_name: string | null;
  documentation_url: string | null;
  credits_per_second: number | null;
  observed: boolean;
  support: 'available' | 'adapter_required';
  node_ids: string[];
};
export type ModelList = {
  revision: string;
  retrieved_at: string | null;
  models: Model[];
  can_rollback: boolean;
  mutation_allowed: boolean;
  automatic_check?: {
    enabled: boolean;
    running: boolean;
    interval_hours: number;
    checked_at: string | null;
    update_available: boolean | null;
    error: string | null;
  };
};

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new Error(translate('models.invalidResponse'));
  return value as Record<string, unknown>;
}

// eslint-disable-next-line local/no-trivial-functions -- This shared type guard validates repeated fields at the API boundary.
function shortText(value: unknown, max = 200): value is string {
  return typeof value === 'string' && value.length > 0 && value.length <= max;
}

function model(value: unknown): Model {
  const row = record(value);
  if (
    !shortText(row.key) ||
    !shortText(row.name) ||
    !shortText(row.title) ||
    !(row.connect_name === null || shortText(row.connect_name)) ||
    !(
      row.documentation_url === null ||
      (typeof row.documentation_url === 'string' &&
        /^https:\/\/docs\.reactor\.inc\/model-api-reference\/[a-z0-9._-]+\/overview$/.test(
          row.documentation_url,
        ))
    ) ||
    !(
      row.credits_per_second === null ||
      (typeof row.credits_per_second === 'number' &&
        Number.isFinite(row.credits_per_second) &&
        row.credits_per_second >= 0)
    ) ||
    typeof row.observed !== 'boolean' ||
    !['available', 'adapter_required'].includes(String(row.support)) ||
    !Array.isArray(row.node_ids) ||
    row.node_ids.length > 100 ||
    !row.node_ids.every((id) => typeof id === 'string' && /^ReactorInc[A-Za-z0-9]+$/.test(id))
  )
    throw new Error(translate('models.invalidResponse'));
  return row as Model;
}

/**
 * Validate a local model list before displaying it.
 * @param value - The untrusted JSON response.
 * @returns The validated list; malformed responses throw an error.
 */
function parseCatalog(value: unknown): ModelList {
  const document = record(value);
  if (
    typeof document.revision !== 'string' ||
    !browserPatterns.revision.test(document.revision) ||
    !(
      document.retrieved_at === null ||
      (shortText(document.retrieved_at, 40) && Number.isFinite(Date.parse(document.retrieved_at)))
    ) ||
    typeof document.can_rollback !== 'boolean' ||
    typeof document.mutation_allowed !== 'boolean' ||
    !Array.isArray(document.models) ||
    document.models.length < 1 ||
    document.models.length > 1024
  )
    throw new Error(translate('models.invalidResponse'));
  const models = document.models.map(model);
  if (document.automatic_check !== undefined) {
    const check = record(document.automatic_check);
    if (
      typeof check.enabled !== 'boolean' ||
      typeof check.running !== 'boolean' ||
      typeof check.interval_hours !== 'number' ||
      !Number.isSafeInteger(check.interval_hours) ||
      check.interval_hours < 1 ||
      !(
        check.checked_at === null ||
        (shortText(check.checked_at, 40) && Number.isFinite(Date.parse(check.checked_at)))
      ) ||
      !(check.update_available === null || typeof check.update_available === 'boolean') ||
      !(check.error === null || shortText(check.error, 1024))
    )
      throw new Error(translate('models.invalidResponse'));
  }
  if (new Set(models.map((row) => row.key)).size !== models.length)
    throw new Error(translate('models.invalidResponse'));
  return { ...document, models } as ModelList;
}

/**
 * Describe whether the saved public metadata has a retrieval date.
 * @param retrievedAt - The saved retrieval time, or null before the first refresh.
 * @returns A readable date or the action needed to load metadata.
 */
// eslint-disable-next-line local/no-trivial-functions -- Share first-refresh guidance and date formatting between model and rate dialogs.
export function metadataStatus(retrievedAt: string | null): Message {
  return retrievedAt === null
    ? message('models.installedList')
    : message('models.lastRefresh', { date: () => formatDate(retrievedAt) });
}

/**
 * Read or update the model list through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The dialog's request lifetime.
 * @param action - Read, refresh public sources, or restore the previous list.
 * @param revision - The currently displayed revision required for rollback.
 * @returns The validated model list.
 */
export async function requestModels(
  fetcher: Fetcher,
  signal: AbortSignal,
  action: 'read' | 'refresh' | 'rollback',
  revision?: string,
): Promise<ModelList> {
  const options: RequestInit = {
    method: action === 'read' ? 'GET' : 'POST',
    cache: 'no-store',
    credentials: 'same-origin',
    signal: AbortSignal.any([signal, AbortSignal.timeout(30_000)]),
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
  };
  if (action === 'rollback') options.body = JSON.stringify({ revision });
  const suffix = action === 'read' ? '' : `/${action}`;
  let response: Response;
  try {
    response = await fetcher(`/reactor-inc/v1/catalog${suffix}`, options);
  } catch {
    throw new Error(translate('models.unreachable'));
  }
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new Error(translate('models.invalidResponse'));
  }
  if (!response.ok) {
    const error = record(body).error;
    throw new Error(shortText(error, 1024) ? error : translate('models.requestFailed'));
  }
  return parseCatalog(body);
}
