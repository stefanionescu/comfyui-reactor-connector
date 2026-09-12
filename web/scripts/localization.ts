import { translate, type MessageKey, type MessageValues } from '#web/language.ts';

export type Message = { key: MessageKey; values: MessageValues; fallback?: string };
type Binding = { target: WeakRef<Node>; message: Message; attribute?: string; rendered: string };
const bindings = new Set<Binding>();

/**
 * Keep message identity so an existing label can follow language changes.
 * @param key - The connector message key.
 * @param values - Named display values; deferred values are formatted on refresh.
 * @param fallback - Server text for an unfamiliar setting.
 * @returns The message description, without rendered markup.
 */
export function message(key: MessageKey, values: MessageValues = {}, fallback?: string): Message {
  const content: Message = { key, values };
  if (fallback !== undefined) content.fallback = fallback;
  return content;
}

/**
 * Create a translated text node without replacing adjacent controls.
 * @param content - Plain text or a connector message.
 * @returns A text node whose owned message follows the selected language.
 */
export function textNode(content: string | Message): Text {
  const node = document.createTextNode(
    typeof content === 'string'
      ? content
      : translate(content.key, content.values, content.fallback),
  );
  if (typeof content !== 'string') {
    const binding = { target: new WeakRef(node), message: content, rendered: node.data };
    bindings.add(binding);
  }
  return node;
}

/**
 * Replace a status or button label, preserving its message identity.
 * @param target - The element whose text is owned by the connector.
 * @param content - Plain text or a translated message.
 */
export function setText(target: HTMLElement, content: string | Message): void {
  for (const child of target.childNodes) {
    releaseText(child);
  }
  target.replaceChildren();
  target.appendChild(textNode(content));
}

/**
 * Release translated labels before removing or replacing a panel's content.
 * @param root - The subtree whose labels will no longer be displayed.
 */
export function releaseText(root: Node): void {
  for (const binding of bindings) {
    const target = binding.target.deref();
    if (!target || root.contains(target)) {
      bindings.delete(binding);
    }
  }
}

/**
 * Set an accessible name or placeholder that follows language changes.
 * @param target - The connector-owned element.
 * @param attribute - The text attribute to set.
 * @param content - The connector message.
 */
export function setTextAttribute(target: Element, attribute: string, content: Message): void {
  const rendered = translate(content.key, content.values, content.fallback);
  target.setAttribute(attribute, rendered);
  for (const binding of bindings) {
    if (binding.target.deref() === target && binding.attribute === attribute)
      bindings.delete(binding);
  }
  bindings.add({ target: new WeakRef(target), attribute, message: content, rendered });
}

/** Refresh only connector-owned text, leaving edited values and active controls intact. */
export function refreshText(): void {
  for (const binding of bindings) {
    const target = binding.target.deref();
    if (!target?.isConnected) {
      bindings.delete(binding);
      continue;
    }
    const current = bindingText(target, binding.attribute);
    if (current !== binding.rendered) {
      bindings.delete(binding);
      continue;
    }
    updateBinding(target, binding);
  }
}

function bindingText(target: Node, attribute: string | undefined): string | null {
  if (target instanceof Text) return target.data;
  return target instanceof Element && attribute ? target.getAttribute(attribute) : null;
}

function updateBinding(target: Node, binding: Binding): void {
  binding.rendered = translate(
    binding.message.key,
    binding.message.values,
    binding.message.fallback,
  );
  if (target instanceof Text) target.data = binding.rendered;
  else if (target instanceof Element && binding.attribute)
    target.setAttribute(binding.attribute, binding.rendered);
}
