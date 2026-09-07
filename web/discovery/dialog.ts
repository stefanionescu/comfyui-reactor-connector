import { button, element } from '#web/dom.ts';
import { modelRow } from '#web/discovery/row.ts';
import type { Fetcher } from '#web/settings/api.ts';
import { type ModelList, requestModels } from '#web/discovery/api.ts';

let current: ModelDialog | undefined;

/**
 * Explain the most recent automatic model check.
 * @param check - The scheduler's report, if available.
 * @returns A status message for the model sources section.
 */
function automaticStatus(check: ModelList['automatic_check']): string {
  if (!check) return '';
  if (!check.enabled) return 'Automatic model checks are off. Change this in Reactor settings.';
  if (check.running)
    return 'An automatic model check is running. Reopen this list to see its result.';
  if (check.error) return check.error;
  if (check.update_available === true)
    return 'The model list has changed. Select Refresh models to update your list.';
  if (check.checked_at)
    return `Automatic check: ${new Date(check.checked_at).toLocaleString()}. Checks run every ${check.interval_hours} hours.`;
  return 'An automatic model check is due. Checks do not change this list.';
}

/** Browse public model information without opening an account session. */
class ModelDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly search = element('input');

  private readonly duration = element('input');

  private readonly refresh = button('Refresh models');

  private readonly rollback = button('Restore previous list');

  private readonly status = element('p', 'Loading the local model list…');

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
    this.dialog.className = 'reactor-settings reactor-catalog';
    this.dialog.setAttribute('aria-labelledby', 'reactor-catalog-title');
    const heading = element('h2', 'Reactor models');
    heading.id = 'reactor-catalog-title';
    const close = button('Close');
    close.setAttribute('aria-label', 'Close Reactor models');
    close.addEventListener('click', () => this.dialog.close());
    const header = element('header');
    header.append(heading, close);
    const searchLabel = element('label', 'Search models');
    this.search.type = 'search';
    this.search.placeholder = 'Name or connect name';
    searchLabel.append(this.search);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.list.setAttribute('aria-label', 'Reactor models');
    const sources = element('details');
    sources.append(
      element('summary', 'Model sources and automatic checks'),
      this.checked,
      this.automatic,
    );
    this.dialog.append(
      header,
      element(
        'p',
        "Refresh checks Reactor's public model list and prices. It sends no API key and uses no credits. New models need a compatible connector node.",
      ),
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
    const showAll = button('Show all models');
    showAll.hidden = !this.nodeId;
    showAll.addEventListener('click', () => {
      this.nodeId = undefined;
      showAll.hidden = true;
      this.render();
    });
    this.refresh.disabled = this.rollback.disabled = true;
    this.refresh.addEventListener('click', () => void this.perform('refresh'));
    this.rollback.addEventListener('click', () => void this.perform('rollback'));
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
    const label = element('label', 'Session time to calculate (seconds)');
    this.duration.type = 'number';
    this.duration.min = '0.1';
    this.duration.max = '3600';
    this.duration.step = 'any';
    this.duration.placeholder = 'Enter total paid session time';
    label.append(this.duration);
    const calculation = element('details');
    calculation.append(
      element('summary', 'Calculate credits for session time'),
      label,
      element(
        'p',
        'Use total session time, including setup, pauses, and recording. Saved video length may be shorter. This estimate is not a spending limit or a quote.',
      ),
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
    this.count.textContent = `${visible.length} of ${this.catalog?.models.length ?? 0} catalog entries`;
  }

  /**
   * Read or update the locally stored model list.
   * @param action - Read, refresh from public sources, or restore the previous list.
   * @returns When the model list or error is displayed.
   */
  private async perform(action: 'read' | 'refresh' | 'rollback'): Promise<void> {
    this.refresh.disabled = this.rollback.disabled = true;
    this.status.textContent =
      action === 'refresh' ? 'Checking public model sources…' : 'Loading model list…';
    try {
      const next = await requestModels(
        this.fetcher,
        this.controller.signal,
        action,
        this.catalog?.revision,
      );
      if (this.controller.signal.aborted) return;
      this.catalog = next;
      this.checked.textContent = `Last source check: ${new Date(next.retrieved_at).toLocaleString()}. Your Reactor account determines which models you can use.`;
      this.automatic.textContent = automaticStatus(next.automatic_check);
      this.status.textContent = {
        refresh: 'Model list refreshed. No generation started.',
        rollback: 'Previous model list restored. This does not change which models Reactor offers.',
        read: 'Local model list loaded.',
      }[action];
      this.render();
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent = error instanceof Error ? error.message : 'Cannot load models.';
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
    void this.perform('read');
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
