import type { Fetcher } from '#web/http.ts';
import { browserRoutes } from '#web/routes.ts';
import { browserLimits } from '#web/browser.ts';
import { parsePublicError } from '#web/schema.ts';
import { translate, formatDate } from '#web/language.ts';
import { message, type Message } from '#web/localization.ts';
import { parseModelList, type ModelList } from '#web/discovery/schema.ts';

type ModelAction = 'read' | 'refresh' | 'rollback';

function modelRoute(action: ModelAction): string {
  if (action === 'read') return browserRoutes.models.read;
  if (action === 'refresh') return browserRoutes.models.refresh;
  return browserRoutes.models.rollback;
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
    throw new Error(parsePublicError(body) ?? translate('models.requestFailed'));
  }
  return parseModelList(body);
}
