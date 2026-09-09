import { formatNumber } from '#web/language.ts';
import type { Model } from '#web/discovery/api.ts';
import { message, type Message } from '#web/localization.ts';

/**
 * Describe a listed credit rate and calculate credits only for a current rate.
 * @param model - A validated entry from the local model list.
 * @param seconds - Optional total session time.
 * @returns Rate details and an optional calculation for display.
 */
export function formatCreditSummary(model: Model, seconds: number | undefined): Message[] {
  const rate = model.creditsPerSecond;
  if (rate === null) return [message('pricing.rateUnavailable')];
  const summary = [message('pricing.rate', { rate: rate })];
  if (!model.observed) {
    summary.push(message('pricing.rateOutdated'));
  } else if (seconds !== undefined) {
    // eslint-disable-next-line local/no-trivial-functions -- Defer formatting so existing estimates follow language changes.
    const credits = () =>
      formatNumber(rate * seconds, {
        maximumFractionDigits: 2,
      });
    summary.push(
      message('pricing.calculation', {
        seconds: seconds,
        rate: rate,
        credits,
      }),
    );
  }
  return summary;
}
