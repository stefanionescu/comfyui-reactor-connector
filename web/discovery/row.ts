import { element } from '#web/dom.ts';
import { message } from '#web/localization.ts';
import type { Model } from '#web/discovery/api.ts';
import { formatCreditSummary } from '#web/discovery/pricing.ts';

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
    model.support === 'available'
      ? message('models.nodesAvailable')
      : message('models.nodeUnavailable');
  row.append(element('p', support));
  if (model.connect_name)
    row.append(element('p', message('models.connectName', { name: model.connect_name })));
  for (const detail of formatCreditSummary(model, seconds)) row.append(element('p', detail));
  if (model.documentation_url) {
    const link = element('a', message('models.openGuide'));
    link.href = model.documentation_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    row.append(link);
  } else row.append(element('p', message('models.guideUnavailable')));
  return row;
}
