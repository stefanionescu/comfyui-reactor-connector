export function element<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  text?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
}

export function button(text: string, type: "button" | "submit" = "button"): HTMLButtonElement {
  const node = element("button", text);
  node.type = type;
  return node;
}
