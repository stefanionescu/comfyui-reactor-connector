import type { ReactorNode } from "./node-types.ts";

export function configureNodeWidgets(node: ReactorNode): void {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  const control = node.widgets?.find((widget) => widget.name === "control_after_generate");
  if (control) control.label = "Seed behavior";
  for (const widget of node.widgets ?? []) {
    if (typeof widget.options?.advanced !== "boolean") continue;
    const connected = node.inputs?.some(
      (input) => input.name === widget.name && input.link != null,
    );
    // The canvas renderer needs this flag, but connected inputs must keep their labels.
    widget.advanced = widget.options.advanced && !connected;
  }
}

export function bindNodeWidgets(node: ReactorNode): void {
  if (!node.comfyClass?.startsWith("ReactorInc")) return;
  configureNodeWidgets(node);
  const changed = node.onConnectionsChange;
  node.onConnectionsChange = function (...args: unknown[]) {
    changed?.apply(this, args);
    configureNodeWidgets(node);
  };
}
