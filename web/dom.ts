import { textNode, type Message } from '#web/localization.ts';

/**
 * Create a typed element and insert optional text safely.
 * @param tag - The HTML tag to create.
 * @param text - Plain text content, if needed.
 * @returns The new element.
 */
export function element<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  text?: string | Message,
): HTMLElementTagNameMap[K] {
  // reason: Callers supply literal UI tags; content becomes a Text node, never parsed HTML.
  // bearer:disable javascript_lang_dangerous_insert_html
  const node = document.createElement(tag);
  if (text !== undefined) node.appendChild(textNode(text));
  return node;
}

/**
 * Create a button with an explicit form behavior.
 * @param text - The visible button label.
 * @param type - Whether the button submits its form.
 * @returns The new button.
 */
export function button(
  text: string | Message,
  type: 'button' | 'submit' = 'button',
): HTMLButtonElement {
  const node = element('button', text);
  node.type = type;
  return node;
}
