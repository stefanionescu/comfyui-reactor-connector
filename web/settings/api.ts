import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { browserRoutes } from '#config/web/routes.ts';
import { browserLimits } from '#config/web/browser.ts';

import {
  parseConfiguration,
  parseSettingsError,
  type Configuration,
} from '#web/settings/schema.ts';

/**
 * Read or change settings through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The settings dialog's request lifetime.
 * @param route - The local settings route.
 * @param method - The HTTP method.
 * @param body - The settings change, if any.
 * @returns The validated settings after the request.
 */
export async function requestConfiguration(
  fetcher: Fetcher,
  signal: AbortSignal,
  route = browserRoutes.settings.status,
  method = 'GET',
  body?: unknown,
): Promise<Configuration> {
  const options: RequestInit = {
    method,
    cache: 'no-store',
    credentials: 'same-origin',
    signal: AbortSignal.any([
      signal,
      AbortSignal.timeout(browserLimits.requestTimeoutMilliseconds),
    ]),
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
  };
  if (body !== undefined) options.body = JSON.stringify(body);
  let response: Response;
  try {
    response = await fetcher(route, options);
  } catch {
    throw new Error(translate('settings.unreachable'));
  }
  let document: unknown;
  try {
    document = await response.json();
  } catch {
    throw new Error(translate('settings.unreadableResponse'));
  }
  if (!response.ok) {
    throw new Error(parseSettingsError(document) ?? translate('settings.saveFailed'));
  }
  return parseConfiguration(document);
}
