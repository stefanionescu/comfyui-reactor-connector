import { translate } from '#web/language.ts';
import type { ReactorNode } from '#web/nodes/contracts.ts';

/**
 * Apply readable labels while preserving connected input labels.
 * @param node - The Reactor node being created or restored.
 */
export function configureNodeWidgets(node: ReactorNode): void {
  if (!node.comfyClass?.startsWith('ReactorInc')) return;
  const control = node.widgets?.find((widget) => widget.name === 'control_after_generate');
  if (control) control.label = translate('nodes.seedBehavior');
  for (const widget of node.widgets ?? []) {
    if (typeof widget.options?.advanced !== 'boolean') continue;
    const connected = node.inputs?.some(
      (input) => input.name === widget.name && input.link != null,
    );
    // The canvas renderer needs this flag, but connected inputs must keep their labels.
    widget.advanced = widget.options.advanced && !connected;
  }
}

/**
 * Refresh widget labels after ComfyUI changes input connections.
 * @param node - The newly created Reactor node.
 */
export function bindNodeWidgets(node: ReactorNode): void {
  if (!node.comfyClass?.startsWith('ReactorInc')) return;
  configureNodeWidgets(node);
  const changed = node.onConnectionsChange;
  // eslint-disable-next-line local/no-trivial-functions -- ComfyUI requires a callback that preserves the previous listener and refreshes widget labels.
  node.onConnectionsChange = function (...args: unknown[]) {
    changed?.apply(this, args);
    configureNodeWidgets(node);
  };
}
