import { translate } from '#web/language.ts';
import type { Model } from '#web/discovery/api.ts';

/**
 * Describe a listed credit rate and calculate credits only for a current rate.
 * @param model - A validated entry from the local model list.
 * @param seconds - Optional total paid session time.
 * @returns Rate details and an optional calculation for display.
 */
export function formatCreditSummary(model: Model, seconds: number | undefined): string[] {
  const rate = model.credits_per_second;
  if (rate === null) return [translate('pricing.rateUnavailable')];
  const details = [translate('pricing.rate', { rate: rate.toLocaleString() })];
  if (!model.observed) {
    details.push(translate('pricing.rateOutdated'));
  } else if (seconds !== undefined) {
    const credits = (rate * seconds).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
    details.push(
      translate('pricing.calculation', {
        seconds: seconds.toLocaleString(),
        rate: rate.toLocaleString(),
        credits,
      }),
    );
  }
  return details;
}
