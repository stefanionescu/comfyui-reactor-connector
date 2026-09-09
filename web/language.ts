import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import english from '#locales/en/main.json';

export type MessageValues = Record<string, string | number | (() => string)>;

export type MessageKey = keyof typeof english.reactorInc;

export const languageEvents = new EventTarget();

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
export async function initializeLanguage(): Promise<void> {
  try {
    const languages = await api.getCustomNodesI18n();
    const available: Record<string, Record<string, string>> = {};
    for (const [language, document] of Object.entries(languages)) {
      available[language.toLowerCase()] = readLanguage(document);
    }
    messages = available;
  } catch {
    // Bundled English remains available if ComfyUI cannot serve translations.
    messages = {};
  }
  app.ui.settings.addEventListener('Comfy.Locale.change', () =>
    languageEvents.dispatchEvent(new Event('change')),
  );
}

/**
 * Read the selected language and fall back to the bundled English message.
 * @param key - A message in the connector's language file.
 * @param values - Named values inserted as plain text.
 * @param fallback - Text supplied by the server for an unfamiliar setting.
 * @returns The message for the current ComfyUI language.
 */
export function translate(key: MessageKey, values: MessageValues = {}, fallback?: string): string {
  const languages = localeCandidates(selectedLocale());
  const defaults: Record<string, string> = english.reactorInc;
  const message =
    languages.map((language) => messages[language]?.[key]).find((value) => value !== undefined) ??
    defaults[key] ??
    fallback ??
    key;
  return message.replaceAll(/\{(\w+)\}/g, (placeholder: string, name: string) =>
    Object.hasOwn(values, name) ? displayValue(values[name]) : placeholder,
  );
}

/**
 * Read the active locale, preserving regional number and date formatting.
 * @returns A valid language tag, or English when the setting is invalid.
 */
export function selectedLocale(): string {
  const value = app.extensionManager.setting.get('Comfy.Locale');
  try {
    return (
      Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ??
      'en'
    );
  } catch {
    return 'en';
  }
}

/**
 * Match regional resources without treating Traditional Chinese as Simplified Chinese.
 * @param locale - The requested language tag.
 * @returns Exact, language-level, and English fallback keys in preference order.
 */
export function localeCandidates(locale: string): string[] {
  const exact = locale.replaceAll('_', '-').toLowerCase();
  const base = exact.split('-')[0] ?? 'en';
  const chinese = ['zh-tw', 'zh-hk', 'zh-mo', 'zh-hant'].some(
    (tag) => exact === tag || exact.startsWith(tag + '-'),
  );
  return [...new Set([exact, chinese ? 'zh-tw' : base, 'en'])];
}

/**
 * Format display numbers without changing serialized values.
 * @param value - The number to display.
 * @param options - Precision and other display options.
 * @returns The number in the selected ComfyUI locale.
 */
// eslint-disable-next-line local/no-trivial-functions -- The shared formatter applies the selected ComfyUI locale to display values.
export function formatNumber(value: number, options?: Intl.NumberFormatOptions): string {
  return new Intl.NumberFormat(selectedLocale(), options).format(value);
}

/**
 * Format a server timestamp for the selected ComfyUI locale.
 * @param value - A validated timestamp.
 * @returns The local date and time.
 */
// eslint-disable-next-line local/no-trivial-functions -- The shared formatter applies the selected ComfyUI locale to timestamps.
export function formatDate(value: string): string {
  return new Date(value).toLocaleString(selectedLocale());
}

function displayValue(value: MessageValues[string] | undefined): string {
  if (typeof value === 'function') return value();
  return typeof value === 'number' ? formatNumber(value) : String(value);
}
