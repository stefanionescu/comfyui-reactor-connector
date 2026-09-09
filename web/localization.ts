import { translate, type MessageKey, type MessageValues } from '#web/language.ts';

export type Message = { key: MessageKey; values: MessageValues; fallback?: string };
type Binding = { target: WeakRef<Node>; message: Message; attribute?: string; rendered: string };
const bindings = new Set<Binding>();
const textBindings = new WeakMap<Text, Binding>();

/**
 * Keep message identity so an existing label can follow language changes.
 * @param key - The connector message key.
 * @param values - Named display values; deferred values are formatted on refresh.
 * @param fallback - Server text for an unfamiliar setting.
 * @returns The message description, without rendered markup.
 */
// eslint-disable-next-line local/no-trivial-functions -- Message identity must survive rendering so existing labels can change language.
export function message(key: MessageKey, values: MessageValues = {}, fallback?: string): Message {
  return { key, values, ...(fallback === undefined ? {} : { fallback }) };
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
    textBindings.set(node, binding);
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
    if (!(child instanceof Text)) continue;
    const previous = textBindings.get(child);
    if (previous) bindings.delete(previous);
  }
  target.replaceChildren();
  target.appendChild(textNode(content));
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
