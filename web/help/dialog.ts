import { button, element } from '#web/dom.ts';
import { message, setTextAttribute, textNode } from '#web/localization.ts';
import { languageEvents, selectedLocale, localeCandidates } from '#web/language.ts';

let current: HTMLDialogElement | undefined;

/**
 * Display a bundled node guide in a keyboard-accessible dialog.
 * @param nodeId - The validated Reactor node ID.
 */
export function openHelpDialog(nodeId: string): void {
  current?.close();
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element('dialog');
  current = dialog;
  dialog.className = 'reactor-dialog reactor-node-help';
  dialog.setAttribute('aria-labelledby', 'reactor-node-help-title');
  const heading = element('h2', message('help.title'));
  heading.id = 'reactor-node-help-title';
  const close = button(message('close'));
  setTextAttribute(close, 'aria-label', message('help.close'));
  close.addEventListener('click', dialog.close.bind(dialog, undefined));
  const header = element('header');
  header.append(heading, close);
  const frame = element('iframe');
  setTextAttribute(frame, 'title', message('help.guide'));
  frame.sandbox.add(
    'allow-same-origin',
    'allow-popups',
    'allow-popups-to-escape-sandbox',
    'allow-downloads',
  );
  selectGuide(frame, nodeId, controller.signal);
  frame.addEventListener('load', prepareGuide.bind(null, frame, dialog, controller.signal));
  dialog.append(header, frame);
  languageEvents.addEventListener(
    'change',
    selectGuide.bind(null, frame, nodeId, controller.signal),
    { signal: controller.signal },
  );
  dialog.addEventListener(
    'close',
    () => {
      controller.abort();
      dialog.remove();

      if (current === dialog) current = undefined;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true },
  );

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
  guide.documentElement.style.setProperty('--guide-background', colors.backgroundColor);
  guide.documentElement.style.setProperty('--guide-color', colors.color);
  guide.documentElement.style.setProperty('--guide-link', colors.color);
  guide.documentElement.style.setProperty(
    '--guide-code-background',
    colors.getPropertyValue('--comfy-input-bg') || colors.backgroundColor,
  );
  for (const link of guide.querySelectorAll('a')) {
    if (new URL(link.href).origin !== location.origin) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.append(textNode(message('help.newTab')));
    }
  }
  guide.addEventListener(
    'keydown',
    (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        dialog.close();
      }
    },
    { signal },
  );
}

/**
 * Select an installed guide variant and fall back to the authored English guide.
 * @param frame - The help frame owned by the open dialog.
 * @param nodeId - A registered Reactor node ID.
 * @param signal - The dialog lifetime.
 */
function selectGuide(frame: HTMLIFrameElement, nodeId: string, signal: AbortSignal): void {
  const requested = selectedLocale();
  const inventoryUrl = new URL('./guides/languages.json', import.meta.url);
  void displayGuide(frame, nodeId, signal, requested, inventoryUrl);
}

async function displayGuide(
  frame: HTMLIFrameElement,
  nodeId: string,
  signal: AbortSignal,
  requested: string,
  inventoryUrl: URL,
): Promise<void> {
  let language = 'en';
  try {
    const response = await fetch(inventoryUrl, { signal });
    const inventory: unknown = response.ok ? await response.json() : undefined;
    language = guideLanguage(inventory, nodeId, requested);
  } catch {
    // The default guide remains usable if the optional language inventory is unavailable.
  }
  if (signal.aborted || requested !== selectedLocale()) return;
  const path =
    language === 'en' ? `${nodeId}.html` : `${nodeId}/${encodeURIComponent(language)}.html`;
  const url = new URL(`./guides/nodes/${path}`, import.meta.url).href;
  if (frame.src !== url) frame.src = url;
}

function guideLanguage(inventory: unknown, nodeId: string, requested: string): string {
  const names = guideVariants(inventory, nodeId);
  for (const candidate of localeCandidates(requested)) {
    const match = names.get(candidate);
    if (match) return match;
  }
  return 'en';
}

function guideVariants(inventory: unknown, nodeId: string): Map<string, string> {
  const names = new Map<string, string>();
  if (typeof inventory !== 'object' || inventory === null || Array.isArray(inventory)) return names;
  const installed: unknown = new Map(Object.entries(inventory)).get(nodeId);
  if (!Array.isArray(installed)) return names;
  for (const value of installed) {
    if (typeof value === 'string' && !names.has(value.toLowerCase()))
      names.set(value.toLowerCase(), value);
  }
  return names;
}
