import { element } from '#web/dom.ts';
import type { Model } from '#web/discovery/api.ts';

/**
 * Show a model, its support, and its public rate.
 * @param model - A validated entry from the local model list.
 * @param seconds - Optional total session time for a credit calculation.
 * @returns One model list item.
 */
export function modelRow(model: Model, seconds: number | undefined): HTMLElement {
  const row = element('li');
  row.append(element('h3', model.title), element('code', model.name));
  const support =
    model.support === 'available' ? 'Nodes available.' : 'No connector node available.';
  row.append(element('p', support));
  if (model.connect_name) row.append(element('p', `Connect name: ${model.connect_name}`));
  const rate =
    model.credits_per_second === null
      ? 'Rate not listed.'
      : `${model.credits_per_second} credits per session second.`;
  row.append(
    element('p', model.observed ? rate : `${rate} Not observed in the latest source check.`),
  );
  if (model.observed && model.credits_per_second !== null && seconds !== undefined) {
    const credits = (model.credits_per_second * seconds).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
    row.append(element('p', `${seconds} session seconds × listed rate = ${credits} credits.`));
  }
  if (model.documentation_url) {
    const link = element('a', 'Reactor model guide');
    link.href = model.documentation_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    row.append(link);
  } else row.append(element('p', 'No matching public guide was found.'));
  return row;
}
