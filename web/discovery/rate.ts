import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { button, element } from '#web/dom.ts';
import { inputValues } from '#web/nodes/inputs.ts';
import { bindWidgetLabel } from '#web/nodes/labels.ts';
import { browserLimits } from '#config/web/browser.ts';
import { nodePricingRules } from '#config/web/pricing.ts';
import type { ReactorNode } from '#web/nodes/contracts.ts';
import { formatCreditSummary } from '#web/discovery/pricing.ts';
import type { Model, ModelList } from '#web/discovery/schema.ts';
import { requestModels, metadataStatus } from '#web/discovery/api.ts';
import { message, setTextAttribute, setText } from '#web/localization.ts';

/**
 * Read the requested video length only when it is known in the editor.
 * @param node - The node whose rate the user opened.
 * @returns Requested video seconds, or undefined for connected or unknown inputs.
 */
function requestedSeconds(node: ReactorNode): number | undefined {
  const widgets = inputValues(node);
  /**
   * Read a positive numeric widget that is not replaced by a connection.
   * @param name - The saved widget and input name.
   * @returns The widget value, if it is available and valid.
   */
  function value(name: string): number | undefined {
    const raw = widgets.get(name);
    if (typeof raw !== 'number' || !Number.isFinite(raw) || raw <= 0) return undefined;
    return raw;
  }
  const factors = node.comfyClass
    ? nodePricingRules.multipliedDurationInputs[node.comfyClass]
    : undefined;
  if (factors) {
    const first = value(factors[0]);
    const second = value(factors[1]);
    return first !== undefined && second !== undefined ? first * second : undefined;
  }
  return value('duration_seconds');
}

let current: CreditDialog | undefined;

/** Calculate credits from the local public rate and a chosen session time. */
class CreditDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly duration = element('input');

  private readonly validation = element('p');

  private readonly status = element('p', message('pricing.loading'));

  private readonly rates = element('div');

  private models: Model[] = [];

  /**
   * Build the calculator for a node.
   * @param node - The node whose public rate is requested.
   */
  constructor(private readonly node: ReactorNode) {
    this.dialog.className = 'reactor-dialog';
    this.dialog.setAttribute('aria-labelledby', 'reactor-rate-title');
    const title = element('h2', message('pricing.title'));
    title.id = 'reactor-rate-title';
    const close = button(message('close'));
    close.addEventListener('click', this.dialog.close.bind(this.dialog, undefined));
    const header = element('header');
    header.append(title, close);
    const seconds = requestedSeconds(node);
    const request = element(
      'p',
      seconds === undefined
        ? message('pricing.unknownDuration')
        : message('pricing.requestedDuration', { seconds }),
    );
    const label = element('label', message('pricing.sessionTime'));
    this.duration.type = 'number';
    this.duration.min = '0.1';
    this.duration.max = String(browserLimits.maxCalculatorSeconds);
    this.duration.step = 'any';
    setTextAttribute(this.duration, 'placeholder', message('pricing.enterTime'));
    if (seconds !== undefined) this.duration.value = String(seconds);
    label.append(this.duration);
    this.validation.setAttribute('role', 'status');
    this.status.setAttribute('role', 'status');
    this.rates.setAttribute('aria-live', 'polite');
    this.dialog.append(
      header,
      request,
      label,
      this.validation,
      element('p', message('pricing.estimateNotice')),
      this.status,
      this.rates,
    );
    this.duration.addEventListener('input', this.updateView.bind(this));
    this.dialog.addEventListener('close', this.dispose.bind(this), { once: true });
    this.updateView();
  }

  /**
   * Read public rates from the local model list.
   * @param fetcher - ComfyUI's local API client.
   * @returns When rates or an error are displayed.
   */
  private async readRates(fetcher: Fetcher): Promise<void> {
    try {
      const modelList = await requestModels(fetcher, this.controller.signal, 'read');
      if (this.controller.signal.aborted) return;
      this.displayRates(modelList);
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message('pricing.loadFailed'),
        );
    }
  }

  /**
   * Display rates for the selected node and update its calculation.
   * @param modelList - The validated local model list.
   */
  private displayRates(modelList: ModelList): void {
    this.models = [];
    for (const model of modelList.models) {
      if (model.nodeIds.includes(this.node.comfyClass ?? '')) this.models.push(model);
    }
    setText(this.status, metadataStatus(modelList.retrievedAt));
    if (!this.models.length) setText(this.status, message('pricing.modelUnavailable'));
    this.updateView();
  }

  /** Validate session time and update every rate calculation. */
  private updateView(): void {
    const valid = this.duration.value !== '' && this.duration.validity.valid;
    setText(
      this.validation,
      valid
        ? ''
        : message('pricing.timeRange', {
            maximum: browserLimits.maxCalculatorSeconds,
          }),
    );
    this.rates.replaceChildren();
    for (const model of this.models) {
      this.rates.append(element('h3', model.title));
      const seconds = valid ? this.duration.valueAsNumber : undefined;
      for (const detail of formatCreditSummary(model, seconds))
        this.rates.append(element('p', detail));
    }
  }

  /**
   * Show the calculator and read local rates.
   * @param fetcher - ComfyUI's local API client.
   */
  show(fetcher: Fetcher): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.readRates(fetcher);
  }

  /** Stop the request and return focus to the caller. */
  private dispose(): void {
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = undefined;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
}

/**
 * Open one rate calculator at a time.
 * @param node - The node whose rate is requested.
 * @param fetcher - ComfyUI's local API client.
 */
function openCreditRate(node: ReactorNode, fetcher: Fetcher): void {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new CreditDialog(node);
  current.show(fetcher);
}

/**
 * Add a credit rate button to nodes that generate media.
 * @param node - The newly created ComfyUI node.
 * @param fetcher - ComfyUI's local API client.
 */
export function bindCreditRate(node: ReactorNode, fetcher: Fetcher): void {
  const id = node.comfyClass;
  if (!id?.startsWith('ReactorInc') || nodePricingRules.excludedNodeIds.includes(id)) return;
  const widget = node.addWidget(
    'button',
    translate('pricing.viewRate'),
    '',
    openCreditRate.bind(null, node, fetcher),
    {
      serialize: false,
    },
  );
  bindWidgetLabel(node, widget, 'pricing.viewRate');
}
