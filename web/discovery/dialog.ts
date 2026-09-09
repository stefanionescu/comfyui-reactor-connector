import type { Fetcher } from '#web/http.ts';
import { button, element } from '#web/dom.ts';
import { formatDate } from '#web/language.ts';
import { modelRow } from '#web/discovery/row.ts';
import { browserLimits } from '#config/browser.ts';
import type { Message } from '#web/localization.ts';
import { message, setTextAttribute, setText } from '#web/localization.ts';
import { type ModelList, requestModels, metadataStatus } from '#web/discovery/api.ts';

let current: ModelDialog | undefined;

/**
 * Explain the most recent automatic model check.
 * @param check - The scheduler's report, if available.
 * @returns A status message for the model sources section.
 */
function automaticStatus(check: ModelList['automatic_check']): string | Message {
  if (!check) return '';
  if (!check.enabled) return message('models.checksOff');
  if (check.running) return message('models.checkRunning');
  if (check.error) return check.error;
  if (check.update_available === true) return message('models.listChanged');
  if (check.checked_at)
    return message('models.checkSchedule', {
      date: () => formatDate(check.checked_at ?? ''),
      hours: check.interval_hours,
    });
  return message('models.checkDue');
}

/** Browse public model information without opening an account session. */
class ModelDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly search = element('input');

  private readonly duration = element('input');

  private readonly refresh = button(message('models.refresh'));

  private readonly rollback = button(message('models.restore'));

  private readonly status = element('p', message('models.loadingLocal'));

  private readonly checked = element('p');

  private readonly automatic = element('p');

  private readonly count = element('p');

  private readonly list = element('ul');

  private catalog: ModelList | undefined;

  /**
   * Build the model browser and its optional node filter.
   * @param fetcher - ComfyUI's local API client.
   * @param nodeId - Show models supported by this node, if supplied.
   */
  constructor(
    private readonly fetcher: Fetcher,
    private nodeId: string | undefined,
  ) {
    this.dialog.className = 'reactor-dialog reactor-catalog';
    this.dialog.setAttribute('aria-labelledby', 'reactor-catalog-title');
    const heading = element('h2', message('models.title'));
    heading.id = 'reactor-catalog-title';
    const close = button(message('close'));
    setTextAttribute(close, 'aria-label', message('models.close'));
    close.addEventListener('click', () => this.dialog.close());
    const header = element('header');
    header.append(heading, close);
    const searchLabel = element('label', message('models.search'));
    this.search.type = 'search';
    setTextAttribute(this.search, 'placeholder', message('models.searchPlaceholder'));
    searchLabel.append(this.search);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    setTextAttribute(this.list, 'aria-label', message('models.title'));
    const sources = element('details');
    sources.append(element('summary', message('models.sources')), this.checked, this.automatic);
    this.dialog.append(
      header,
      element('p', message('models.refreshNotice')),
      this.actions(),
      this.status,
      searchLabel,
      this.calculation(),
      sources,
      this.count,
      this.list,
    );
    this.search.addEventListener('input', () => this.render());
    this.duration.addEventListener('input', () => this.render());
    this.dialog.addEventListener('close', () => this.dispose(), { once: true });
  }

  /**
   * Build list updates and the node filter reset.
   * @returns The model browser actions.
   */
  private actions(): HTMLElement {
    const showAll = button(message('models.showAll'));
    showAll.hidden = !this.nodeId;
    showAll.addEventListener('click', () => {
      this.nodeId = undefined;
      showAll.hidden = true;
      this.render();
    });
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener('click', () => void this.updateModels('refresh'));
    this.rollback.addEventListener('click', () => void this.updateModels('rollback'));
    const actions = element('div');
    actions.className = 'reactor-actions';
    actions.append(this.refresh, this.rollback, showAll);
    return actions;
  }

  /**
   * Build the optional session time calculation.
   * @returns The collapsed calculation controls.
   */
  private calculation(): HTMLElement {
    const label = element('label', message('pricing.sessionTime'));
    this.duration.type = 'number';
    this.duration.min = '0.1';
    this.duration.max = String(browserLimits.maxCalculatorSeconds);
    this.duration.step = 'any';
    setTextAttribute(this.duration, 'placeholder', message('pricing.enterTime'));
    label.append(this.duration);
    const calculation = element('details');
    calculation.append(
      element('summary', message('pricing.calculate')),
      label,
      element('p', message('pricing.totalTimeNotice')),
    );
    return calculation;
  }

  /** Update matching models and calculations from the current controls. */
  private render(): void {
    const query = this.search.value.trim().toLowerCase();
    const nodeId = this.nodeId;
    const visible =
      this.catalog?.models.filter(
        (model) =>
          (!nodeId || model.node_ids.includes(nodeId)) &&
          `${model.name} ${model.title} ${model.connect_name ?? ''}`.toLowerCase().includes(query),
      ) ?? [];
    const seconds =
      this.duration.validity.valid && this.duration.value !== ''
        ? this.duration.valueAsNumber
        : undefined;
    this.list.replaceChildren(...visible.map((model) => modelRow(model, seconds)));
    setText(
      this.count,
      message('models.count', {
        visible: visible.length,
        total: this.catalog?.models.length ?? 0,
      }),
    );
  }

  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   * @returns When the model list or error is displayed.
   */
  private async updateModels(action: 'read' | 'refresh' | 'rollback'): Promise<void> {
    this.refresh.disabled = this.rollback.disabled = true;
    setText(
      this.status,
      action === 'refresh' ? message('models.checking') : message('models.loading'),
    );
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action,
        this.catalog?.revision,
      );
      if (this.controller.signal.aborted) return;
      this.catalog = next;
      setText(this.checked, metadataStatus(next.retrieved_at));
      setText(this.automatic, automaticStatus(next.automatic_check));
      setText(
        this.status,
        {
          refresh: message('models.refreshed'),
          rollback: message('models.restored'),
          read: message('models.loaded'),
        }[action],
      );
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        setText(this.status, error instanceof Error ? error.message : message('models.loadFailed'));
    } finally {
      this.restoreActions();
    }
  }

  /** Re-enable allowed list changes after the current request finishes. */
  private restoreActions(): void {
    if (this.controller.signal.aborted) return;
    this.refresh.disabled = !this.catalog?.mutation_allowed;
    this.rollback.disabled = !this.catalog?.mutation_allowed || !this.catalog.can_rollback;
  }

  /** Show the dialog and read the local model list. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.updateModels('read');
  }

  /** Stop pending requests and return focus to the caller. */
  private dispose(): void {
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = undefined;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
}

/**
 * Open one model browser at a time.
 * @param fetcher - ComfyUI's local API client.
 * @param nodeId - Show models supported by this node, if supplied.
 */
export function openModels(fetcher: Fetcher, nodeId?: string): void {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new ModelDialog(fetcher, nodeId);
  current.show();
}
