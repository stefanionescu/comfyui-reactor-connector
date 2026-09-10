import type { Fetcher } from '#web/http.ts';
import { browserRoutes } from '#config/web/routes.ts';
import { translate, formatDate } from '#web/language.ts';
import { message, type Message } from '#web/localization.ts';
import { browserLimits, browserPatterns } from '#config/web/browser.ts';

export type Model = {
  entryKey: string;
  modelSlug: string;
  title: string;
  connectionName: string | null;
  documentationUrl: string | null;
  creditsPerSecond: number | null;
  observed: boolean;
  support: 'available' | 'adapter_required';
  nodeIds: string[];
};
export type ModelList = {
  revision: string;
  retrievedAt: string | null;
  models: Model[];
  canRollback: boolean;
  mutationAllowed: boolean;
  automaticCheck?: {
    enabled: boolean;
    running: boolean;
    intervalHours: number;
    checkedAt: string | null;
    updateAvailable: boolean | null;
    error: string | null;
  };
};

type ModelAction = 'read' | 'refresh' | 'rollback';

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new Error(translate('models.invalidResponse'));
  return value as Record<string, unknown>;
}

function isShortText(value: unknown, max = browserLimits.maxTextCharacters): value is string {
  if (typeof value !== 'string') return false;
  return value.length > 0 && value.length <= max;
}

function isNodeId(value: unknown): value is string {
  if (typeof value !== 'string') return false;
  return browserPatterns.nodeId.test(value);
}

function modelRoute(action: ModelAction): string {
  if (action === 'read') return browserRoutes.models.read;
  if (action === 'refresh') return browserRoutes.models.refresh;
  return browserRoutes.models.rollback;
}

function parseModel(value: unknown): Model {
  const row = record(value);
  if (
    !isShortText(row.key) ||
    !isShortText(row.name) ||
    !isShortText(row.title) ||
    !(row.connect_name === null || isShortText(row.connect_name)) ||
    !(
      row.documentation_url === null ||
      (typeof row.documentation_url === 'string' &&
        browserPatterns.documentation.test(row.documentation_url))
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
    row.node_ids.length > browserLimits.maxModelNodeIds ||
    !row.node_ids.every(isNodeId)
  )
    throw new Error(translate('models.invalidResponse'));
  return {
    entryKey: row.key,
    modelSlug: row.name,
    title: row.title,
    connectionName: row.connect_name,
    documentationUrl: row.documentation_url,
    creditsPerSecond: row.credits_per_second,
    observed: row.observed,
    support: row.support as Model['support'],
    nodeIds: row.node_ids,
  };
}

/**
 * Validate a local model list before displaying it.
 * @param value - The untrusted JSON response.
 * @returns The validated list; malformed responses throw an error.
 */
function parseModelList(value: unknown): ModelList {
  const document = record(value);
  if (
    typeof document.revision !== 'string' ||
    !browserPatterns.revision.test(document.revision) ||
    !(
      document.retrieved_at === null ||
      (isShortText(document.retrieved_at, browserLimits.maxRetrievalTimeCharacters) &&
        Number.isFinite(Date.parse(document.retrieved_at)))
    ) ||
    typeof document.can_rollback !== 'boolean' ||
    typeof document.mutation_allowed !== 'boolean' ||
    !Array.isArray(document.models) ||
    document.models.length < 1 ||
    document.models.length > browserLimits.maxModels
  )
    throw new Error(translate('models.invalidResponse'));
  const models = document.models.map(parseModel);
  const keys = new Set<string>();
  for (const model of models) {
    if (keys.has(model.entryKey)) throw new Error(translate('models.invalidResponse'));
    keys.add(model.entryKey);
  }
  return {
    revision: document.revision,
    retrievedAt: document.retrieved_at,
    canRollback: document.can_rollback,
    mutationAllowed: document.mutation_allowed,
    models,
    ...(document.automatic_check === undefined
      ? {}
      : { automaticCheck: parseAutomaticCheck(document.automatic_check) }),
  };
}

function parseAutomaticCheck(value: unknown): NonNullable<ModelList['automaticCheck']> {
  const check = record(value);
  if (
    typeof check.enabled !== 'boolean' ||
    typeof check.running !== 'boolean' ||
    typeof check.interval_hours !== 'number' ||
    !Number.isSafeInteger(check.interval_hours) ||
    check.interval_hours < 1 ||
    !(
      check.checked_at === null ||
      (isShortText(check.checked_at, browserLimits.maxRetrievalTimeCharacters) &&
        Number.isFinite(Date.parse(check.checked_at)))
    ) ||
    !(check.update_available === null || typeof check.update_available === 'boolean') ||
    !(check.error === null || isShortText(check.error, browserLimits.maxErrorCharacters))
  )
    throw new Error(translate('models.invalidResponse'));
  return {
    enabled: check.enabled,
    running: check.running,
    intervalHours: check.interval_hours,
    checkedAt: check.checked_at,
    updateAvailable: check.update_available,
    error: check.error,
  };
}

/**
 * Describe whether the saved public metadata has a retrieval date.
 * @param retrievedAt - The saved retrieval time, or null before the first refresh.
 * @returns A readable date or the action needed to load metadata.
 */
export function metadataStatus(retrievedAt: string | null): Message {
  if (retrievedAt === null) return message('models.installedList');
  return message('models.lastRefresh', { date: formatDate.bind(null, retrievedAt) });
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
  action: ModelAction,
  revision?: string,
): Promise<ModelList> {
  const options: RequestInit = {
    method: action === 'read' ? 'GET' : 'POST',
    cache: 'no-store',
    credentials: 'same-origin',
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.discoveryTimeoutMilliseconds),
    ]),
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
  };
  if (action === 'rollback') options.body = JSON.stringify({ revision });
  let response: Response;
  try {
    response = await fetcher(modelRoute(action), options);
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
    throw new Error(
      isShortText(error, browserLimits.maxErrorCharacters)
        ? error
        : translate('models.requestFailed'),
    );
  }
  return parseModelList(body);
}
