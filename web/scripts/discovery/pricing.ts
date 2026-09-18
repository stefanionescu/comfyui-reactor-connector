import { formatNumber, message } from '#web/text.ts';
import type { Model } from '#web/discovery/schema.ts';

/**
 * Describe a listed credit rate and calculate credits only for a current rate.
 * @param model - A validated entry from the local model list.
 * @param seconds - Optional total session time.
 * @returns Rate details and an optional calculation for display.
 */
export function formatCreditSummary(model: Model, seconds: number | undefined): string[] {
  const rate = model.creditsPerSecond;
  if (rate === null) return [message('pricing.rateUnavailable')];
  const summary = [message('pricing.rate', { rate: rate })];
  if (!model.observed) {
    summary.push(message('pricing.rateOutdated'));
  } else if (seconds !== undefined) {
    summary.push(
      message('pricing.calculation', {
        seconds: seconds,
        rate: rate,
        credits: formatNumber(rate * seconds, { maximumFractionDigits: 2 }),
      }),
    );
  }
  return summary;
}
