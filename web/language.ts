import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import english from '#locales/en/main.json';

export type MessageKey = keyof typeof english.reactorInc;

let messages: Record<string, Record<string, string>> = {};

/**
 * Keep string messages from one installed language document.
 * @param document - A language entry returned by ComfyUI.
 * @returns The connector's messages, or an empty set if none are provided.
 */
function readLanguage(document: unknown): Record<string, string> {
  if (typeof document !== 'object' || document === null) return {};
  const source = (document as Record<string, unknown>).reactorInc;
  if (typeof source !== 'object' || source === null) return {};
  const translated: Record<string, string> = {};
  for (const [key, value] of Object.entries(source)) {
    if (typeof value === 'string') translated[key] = value;
  }
  return translated;
}

/** Load the connector's messages from ComfyUI's installed language files. */
export async function loadLanguage(): Promise<void> {
  try {
    const languages = await api.getCustomNodesI18n();
    const available: Record<string, Record<string, string>> = {};
    for (const [language, document] of Object.entries(languages)) {
      available[language] = readLanguage(document);
    }
    messages = available;
  } catch {
    // Bundled English remains available if ComfyUI cannot serve translations.
    messages = {};
  }
}

/**
 * Read the selected language and fall back to the bundled English message.
 * @param key - A message in the connector's language file.
 * @param values - Named values inserted as plain text.
 * @param fallback - Text supplied by the server for an unfamiliar setting.
 * @returns The message for the current ComfyUI language.
 */
export function translate(
  key: MessageKey,
  values: Record<string, string | number> = {},
  fallback?: string,
): string {
  const selected = app.extensionManager.setting.get('Comfy.Locale');
  const language = typeof selected === 'string' ? selected : 'en';
  const defaults: Record<string, string> = english.reactorInc;
  const message = messages[language]?.[key] ?? defaults[key] ?? fallback ?? key;
  return message.replaceAll(/\{(\w+)\}/g, (placeholder: string, name: string) =>
    Object.hasOwn(values, name) ? String(values[name]) : placeholder,
  );
}
