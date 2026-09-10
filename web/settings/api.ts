import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { browserRoutes } from '#config/web/routes.ts';
import { browserPatterns, browserLimits } from '#config/web/browser.ts';

type SettingDefinition = { label: string; minimum: number; maximum: number };
export type Configuration = {
  revision: string;
  credentialSource: 'missing' | 'saved' | 'environment';
  credentialLimit: number;
  mutationAllowed: boolean;
  definitions: Record<string, SettingDefinition> & { catalog_interval_hours: SettingDefinition };
  settings: Record<string, number | boolean> & {
    catalog_auto_check: boolean;
    catalog_interval_hours: number;
  };
};

function record(value: unknown): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error(translate('settings.invalidResponse'));
  }
  return value as Record<string, unknown>;
}

/**
 * Read the settings fields and ranges supplied by the backend.
 * @param value - The untrusted field definitions.
 * @returns Validated definitions for the settings form.
 */
function parseDefinitions(value: unknown): Configuration['definitions'] {
  const definitions = record(value);
  if (!Object.hasOwn(definitions, 'catalog_interval_hours'))
    throw new Error(translate('settings.incompleteResponse'));
  const result = new Map<string, SettingDefinition>();
  for (const [name, raw] of Object.entries(definitions)) {
    const field = record(raw);
    if (
      !browserPatterns.settingName.test(name) ||
      typeof field.label !== 'string' ||
      field.label.length < 1 ||
      field.label.length > browserLimits.maxTextCharacters ||
      typeof field.minimum !== 'number' ||
      !Number.isSafeInteger(field.minimum) ||
      typeof field.maximum !== 'number' ||
      !Number.isSafeInteger(field.maximum) ||
      field.minimum > field.maximum
    )
      throw new Error(translate('settings.invalidDefinition'));
    result.set(name, { label: field.label, minimum: field.minimum, maximum: field.maximum });
  }
  return Object.fromEntries(result) as Configuration['definitions'];
}

/**
 * Validate local settings without exposing a saved key.
 * @param value - The untrusted JSON response.
 * @returns The validated settings and credential source.
 */
function parseConfiguration(value: unknown): Configuration {
  const document = record(value);
  const settings = record(document.settings);
  const credential = record(document.credential);
  if (
    typeof document.revision !== 'string' ||
    !browserPatterns.revision.test(document.revision) ||
    typeof document.mutation_allowed !== 'boolean' ||
    typeof credential.source !== 'string' ||
    !['missing', 'saved', 'environment'].includes(credential.source)
  ) {
    throw new Error(translate('settings.invalidResponse'));
  }
  const definitions = parseDefinitions(document.integer_settings);
  if (
    typeof settings.catalog_auto_check !== 'boolean' ||
    typeof document.credential_limit !== 'number' ||
    !Number.isSafeInteger(document.credential_limit) ||
    document.credential_limit < 1
  )
    throw new Error(translate('settings.invalidChecks'));
  const settingsByName = new Map(Object.entries(settings));
  for (const [name, definition] of Object.entries(definitions)) {
    const value = settingsByName.get(name);
    if (
      typeof value !== 'number' ||
      !Number.isSafeInteger(value) ||
      value < definition.minimum ||
      value > definition.maximum
    )
      throw new Error(translate('settings.invalidLimit'));
  }
  return {
    revision: document.revision,
    credentialSource: credential.source as Configuration['credentialSource'],
    mutationAllowed: document.mutation_allowed,
    settings: settings as Configuration['settings'],
    definitions,
    credentialLimit: document.credential_limit,
  };
}

/**
 * Read or change settings through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The settings dialog's request lifetime.
 * @param route - The local settings route.
 * @param method - The HTTP method.
 * @param body - The change to save, if any.
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
    const error = record(document).error;
    throw new Error(
      typeof error === 'string' && error.length <= browserLimits.maxErrorCharacters
        ? error
        : translate('settings.saveFailed'),
    );
  }
  return parseConfiguration(document);
}
