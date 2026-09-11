import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { browserRoutes } from '#config/web/routes.ts';
import { parseLiveStatus, type Invitation, type LiveStatus } from '#web/live/schema.ts';

/**
 * Send camera input and receive session status through ComfyUI.
 * @param fetcher - ComfyUI's local API client.
 * @param owner - The session invitation and its private control capability.
 * @param sequence - The increasing exchange sequence for this panel.
 * @param axes - Current camera movement and look directions.
 * @param end - Whether to end the session.
 * @param previewSequence - The latest preview already displayed.
 * @param signal - The request deadline or cancellation signal.
 * @param release - Whether to clear previous camera movement immediately.
 * @returns The validated status and optional preview.
 */
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
  const response = await fetcher(browserRoutes.live.exchange, {
    method: 'POST',
    cache: 'no-store',
    signal,
    headers: { 'Content-Type': 'application/json', 'X-Reactor-Comfy': '1' },
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
  if (!response.ok) throw new Error(translate('live.unreachable'));
  const status = parseLiveStatus(await response.json());
  if (!status) throw new Error(translate('live.invalidStatus'));
  return status;
}
