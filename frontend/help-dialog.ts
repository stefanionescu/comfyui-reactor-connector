import { button, element } from "./dom.ts";
import { settingsStyles } from "./styles.ts";

let current: HTMLDialogElement | undefined;

export function openHelpDialog(nodeId: string): void {
  current?.close();
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  current = dialog;
  dialog.className = "reactor-settings reactor-node-help";
  dialog.setAttribute("aria-labelledby", "reactor-node-help-title");
  const heading = element("h2", "Node help");
  heading.id = "reactor-node-help-title";
  const close = button("Close");
  close.setAttribute("aria-label", "Close node help");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const frame = element("iframe");
  frame.title = "Reactor node guide";
  frame.sandbox.add("allow-same-origin", "allow-popups", "allow-popups-to-escape-sandbox");
  frame.src = `/extensions/reactor-inc/guides/docs/nodes/${nodeId}.html`;
  frame.addEventListener("load", () => prepareGuide(frame, dialog, controller.signal));
  const styles = element("style", `${settingsStyles}\n${helpStyles}`);
  dialog.append(header, frame);
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      styles.remove();
      if (current === dialog) current = undefined;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true },
  );
  document.head.append(styles);
  document.body.append(dialog);
  dialog.showModal();
  close.focus();
}

function prepareGuide(
  frame: HTMLIFrameElement,
  dialog: HTMLDialogElement,
  signal: AbortSignal,
): void {
  const guide = frame.contentDocument;
  if (!guide) return;
  const colors = getComputedStyle(dialog);
  guide.body.style.background = colors.backgroundColor;
  guide.body.style.color = colors.color;
  for (const link of guide.querySelectorAll("a")) {
    link.style.color = "inherit";
    if (new URL(link.href).origin !== location.origin) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
  }
  for (const block of guide.querySelectorAll("pre")) {
    block.style.background = colors.getPropertyValue("--comfy-input-bg") || colors.backgroundColor;
  }
  guide.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        dialog.close();
      }
    },
    { signal },
  );
}

const helpStyles = `
.reactor-node-help { width: min(64rem, calc(100vw - 2rem)); padding: 1rem; }
.reactor-node-help iframe { display: block; width: 100%; height: min(72vh, 55rem); border: 0; margin-top: 1rem; }
`;
