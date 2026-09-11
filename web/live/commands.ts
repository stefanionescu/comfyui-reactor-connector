import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import type { Invitation } from '#web/live/schema.ts';
import { browserRoutes } from '#config/web/routes.ts';
import { browserLimits } from '#config/web/browser.ts';

/**
 * Send one ordered live action through the local ComfyUI server.
 * @param fetcher - ComfyUI's local API client.
 * @param owner - The session lease and private control capability.
 * @param sequence - The increasing action sequence for this panel.
 * @param name - The supported action name.
 * @param fields - The fields required by that action.
 * @returns When the server accepts the action; failures throw an error.
 */
export async function sendAction(
  fetcher: Fetcher,
  owner: Pick<Invitation, 'lease' | 'capability'>,
  sequence: number,
  name: string,
  fields: Record<string, unknown>,
): Promise<void> {
  const response = await fetcher(browserRoutes.live.action, {
    method: 'POST',
    cache: 'no-store',
    signal: AbortSignal.timeout(browserLimits.actionTimeoutMilliseconds),
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
    body: JSON.stringify({
      lease: owner.lease,
      capability: owner.capability,
      sequence,
      action: name,
      fields,
    }),
  });
  if (!response.ok) throw new Error(translate('live.actionRejected'));
}
