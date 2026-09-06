import { app } from "../../scripts/app.js";
import { openHelpDialog } from "./help-dialog.ts";

export const HELP_COMMAND = "ReactorInc.OpenNodeHelp";

function nodeId(item: unknown): string | undefined {
  if (typeof item !== "object" || item === null || !("comfyClass" in item)) return;
  const id = item.comfyClass;
  return typeof id === "string" && /^ReactorInc[A-Za-z0-9]+$/.test(id) ? id : undefined;
}

export function helpCommands(item: unknown): string[] {
  return nodeId(item) ? [HELP_COMMAND] : [];
}

export function openNodeHelp(): void {
  const id = Array.from(app.canvas.selectedItems ?? [])
    .map(nodeId)
    .find(Boolean);
  if (!id) return;
  openHelpDialog(id);
}
