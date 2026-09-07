import { app } from '../../scripts/app.js';
import { openHelpDialog } from '#web/help/dialog.ts';

export const HELP_COMMAND = 'ReactorInc.OpenNodeHelp';

function nodeId(item: unknown): string | undefined {
  if (typeof item !== 'object' || item === null || !('comfyClass' in item)) return;
  const id = item.comfyClass;
  return typeof id === 'string' && /^ReactorInc[A-Za-z0-9]+$/.test(id) ? id : undefined;
}

/**
 * Offer node help only for a selected Reactor node.
 * @param item - The selected ComfyUI canvas item.
 * @returns The help command ID, or an empty list for other items.
 */
export function helpCommands(item: unknown): string[] {
  if (!nodeId(item)) return [];
  return [HELP_COMMAND];
}

/**
 * Open the guide for the first selected Reactor node.
 */
export function openNodeHelp(): void {
  const id = Array.from(app.canvas.selectedItems ?? [])
    .map(nodeId)
    .find(Boolean);
  if (!id) return;
  openHelpDialog(id);
}
