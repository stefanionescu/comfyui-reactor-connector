import { translate, type MessageKey } from '#web/language.ts';
import type { ReactorNode, NodeWidget } from '#web/nodes/contracts.ts';

/**
 * Apply readable labels while preserving connected input labels.
 * @param node - The Reactor node being created or restored.
 */
export function configureNodeWidgets(node: ReactorNode): void {
  if (!node.comfyClass?.startsWith('ReactorInc')) return;
  const control = node.widgets?.find((widget) => widget.name === 'control_after_generate');
  if (control) bindWidgetLabel(node, control, 'nodes.seedBehavior');
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

const labels = new Map<WeakRef<NodeWidget>, { node: WeakRef<ReactorNode>; key: MessageKey }>();

/**
 * Keep a custom canvas label in step with the interface language.
 * @param node - The label's owning node.
 * @param widget - The custom widget, without changing its serialized value.
 * @param key - The label message.
 */
export function bindWidgetLabel(node: ReactorNode, widget: NodeWidget, key: MessageKey): void {
  widget.label = translate(key);
  for (const [reference] of labels) {
    if (!reference.deref()) labels.delete(reference);
    else if (reference.deref() === widget) return;
  }
  labels.set(new WeakRef(widget), { node: new WeakRef(node), key });
}

/** Refresh custom widget labels without retaining removed nodes. */
export function refreshWidgetLabels(): void {
  for (const [reference, binding] of labels) {
    const widget = reference.deref();
    const node = binding.node.deref();
    if (!widget || !node?.graph) {
      labels.delete(reference);
      continue;
    }
    widget.label = translate(binding.key);
    node.graph.setDirtyCanvas(true);
  }
}
