import type { Fetcher } from '#web/http.ts';
import { translate } from '#web/language.ts';
import { button, element } from '#web/dom.ts';
import { browserLimits } from '#config/browser.ts';
import { bindWidgetLabel } from '#web/nodes/labels.ts';
import type { ReactorNode } from '#web/nodes/contracts.ts';
import { formatCreditSummary } from '#web/discovery/pricing.ts';
import { message, setTextAttribute, setText } from '#web/localization.ts';
import { type Model, requestModels, metadataStatus } from '#web/discovery/api.ts';

/**
 * Read the requested video length only when it is known in the editor.
 * @param node - The node whose rate the user opened.
 * @returns Requested video seconds, or undefined for connected or unknown inputs.
 */
function requestedSeconds(node: ReactorNode): number | undefined {
  /**
   * Read a positive numeric widget that is not replaced by a connection.
   * @param name - The saved widget and input name.
   * @returns The widget value, if it is available and valid.
   */
  function value(name: string): number | undefined {
    if (node.inputs?.some((input) => input.name === name && input.link != null)) return undefined;
    const raw = node.widgets?.find((widget) => widget.name === name)?.value;
    return typeof raw === 'number' && Number.isFinite(raw) && raw > 0 ? raw : undefined;
  }
  if (node.comfyClass === 'ReactorIncFastContinue') {
    const seconds = value('clip_seconds');
    const count = value('clip_count');
    return seconds !== undefined && count !== undefined ? seconds * count : undefined;
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
    close.addEventListener('click', () => this.dialog.close());
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
    this.duration.addEventListener('input', () => this.render());
    this.dialog.addEventListener('close', () => this.dispose(), { once: true });
    this.render();
  }

  /**
   * Read public rates from the local model list.
   * @param fetcher - ComfyUI's local API client.
   * @returns When rates or an error are displayed.
   */
  private async readRates(fetcher: Fetcher): Promise<void> {
    try {
      const catalog = await requestModels(fetcher, this.controller.signal, 'read');
      if (this.controller.signal.aborted) return;
      this.models = catalog.models.filter((model) =>
        model.node_ids.includes(this.node.comfyClass ?? ''),
      );
      setText(this.status, metadataStatus(catalog.retrieved_at));
      if (!this.models.length) setText(this.status, message('pricing.modelUnavailable'));
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(
          this.status,
          error instanceof Error ? error.message : message('pricing.loadFailed'),
        );
    }
  }

  /** Validate session time and update every rate calculation. */
  private render(): void {
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
  if (
    !id?.startsWith('ReactorInc') ||
    id === 'ReactorIncHeliosAddPrompt' ||
    id === 'ReactorIncLongLiveAddShot'
  )
    return;
  const widget = node.addWidget(
    'button',
    translate('pricing.viewRate'),
    '',
    () => openCreditRate(node, fetcher),
    {
      serialize: false,
    },
  );
  bindWidgetLabel(node, widget, 'pricing.viewRate');
}
