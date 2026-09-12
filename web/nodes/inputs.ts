import type { ReactorNode } from '#web/nodes/contracts.ts';

/**
 * Identify inputs whose values come from graph connections.
 * @param node - The node being inspected.
 * @returns Names of inputs with a link.
 */
function connectedInputs(node: ReactorNode): Set<string> {
  const names = new Set<string>();
  for (const input of node.inputs) {
    if (input.link != null) names.add(input.name);
  }
  return names;
}

/**
 * Read widget values that have not been replaced by graph connections.
 * @param node - The node being inspected.
 * @returns The first widget value for each unconnected input name.
 */
export function inputValues(node: ReactorNode): Map<string, unknown> {
  const connected = connectedInputs(node);
  const values = new Map<string, unknown>();
  for (const widget of node.widgets ?? []) {
    if (!values.has(widget.name) && !connected.has(widget.name))
      values.set(widget.name, widget.value);
  }
  return values;
}
