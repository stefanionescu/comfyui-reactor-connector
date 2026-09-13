import { element } from '#web/dom.ts';
import type { Message } from '#web/localization.ts';

/**
 * Group a prompt field with its reply and apply action.
 * @param title - The visible field label.
 * @param input - The prompt editor.
 * @param apply - The button that sends the edited prompt.
 * @param status - The reply to the latest prompt change.
 * @returns The prompt section.
 */
export function promptSection(
  title: Message,
  input: HTMLTextAreaElement,
  apply: HTMLButtonElement,
  status: HTMLElement,
): HTMLElement {
  const section = element('section');
  section.className = 'reactor-prompt';
  const label = element('label', title);
  label.append(input);
  const actions = element('div');
  actions.className = 'reactor-prompt-actions';
  actions.append(status, apply);
  section.append(label, actions);
  return section;
}

/**
 * Place the session name, requested duration, and current status together.
 * @param title - The model and control panel name.
 * @param duration - The requested video duration.
 * @param status - The current session status.
 * @param elapsed - The optional elapsed-time display.
 * @returns The session header.
 */
export function sessionHeader(
  title: Message,
  duration: Message,
  status: HTMLElement,
  elapsed?: HTMLElement,
): HTMLElement {
  const header = element('header');
  const state = element('div');
  state.className = 'reactor-session-status';
  state.append(status);
  if (elapsed) state.append(elapsed);
  header.append(element('h2', title), element('small', duration), state);
  return header;
}
