import { button, element } from '#web/dom.ts';
import { translate, type MessageKey } from '#web/language.ts';
import { type Configuration, type Fetcher, requestConfiguration } from '#web/settings/api.ts';

let current: SettingsDialog | undefined;

/** Edit server settings and cancel pending requests when the dialog closes. */
class SettingsDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly status = element('p', translate('settings.loading'));

  private readonly source = element('p');

  private readonly reload = button(translate('settings.reload'));

  private readonly key = element('input');

  private readonly keyFields = element('fieldset');

  private readonly limitFields = element('fieldset');

  private readonly catalogFields = element('fieldset');

  private readonly automatic = element('input');

  private readonly interval = element('input');

  private readonly inputs = new Map<string, HTMLInputElement>();

  private configuration: Configuration | undefined;

  /**
   * Build settings forms without contacting Reactor.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(private readonly fetcher: Fetcher) {
    this.dialog.className = 'reactor-settings';
    this.dialog.setAttribute('aria-labelledby', 'reactor-settings-title');
    const heading = element('h2', translate('settings.title'));
    heading.id = 'reactor-settings-title';
    const close = button(translate('close'));
    close.setAttribute('aria-label', translate('settings.close'));
    close.addEventListener('click', () => this.dialog.close());
    const header = element('header');
    header.append(heading, close);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.reload.addEventListener(
      'click',
      () => void this.updateSettings(translate('settings.loaded')),
    );
    this.dialog.append(
      header,
      element('p', translate('settings.accountNotice')),
      this.source,
      this.credentials(),
      element('p', translate('settings.keyNotice')),
      this.limits(),
      element('p', translate('settings.timeNotice')),
      this.modelUpdates(),
      this.status,
      this.reload,
    );
    this.dialog.addEventListener('close', () => this.dispose(), { once: true });
  }

  /**
   * Build the private key form.
   * @returns The form for saving or clearing the server's key.
   */
  private credentials(): HTMLFormElement {
    const form = element('form');
    this.keyFields.disabled = true;
    const label = element('label', translate('settings.credentialLabel'));
    this.key.type = 'password';
    this.key.autocomplete = 'off';
    this.key.spellcheck = false;
    this.key.required = true;
    label.append(this.key);
    const clear = button(translate('settings.clearKey'));
    // eslint-disable-next-line local/no-trivial-functions -- Clearing the key field must happen before this user-triggered request.
    clear.addEventListener('click', () => {
      this.key.value = '';
      void this.updateSettings(translate('settings.keyCleared'), '/credential', 'DELETE');
    });
    const actions = element('div');
    actions.className = 'reactor-actions';
    actions.append(button(translate('settings.saveKey'), 'submit'), clear);
    this.keyFields.append(element('legend', translate('settings.credentials')), label, actions);
    form.append(this.keyFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.key.value = '';
      void this.updateSettings(translate('settings.keySaved'), '/credential', 'PUT', {
        api_key: value,
      });
    });
    return form;
  }

  /**
   * Build duration, timeout, and media size inputs.
   * @returns The form for execution limits.
   */
  private limits(): HTMLFormElement {
    const form = element('form');
    this.limitFields.disabled = true;
    this.limitFields.append(element('legend', translate('settings.limits')));
    this.limitFields.append(button(translate('settings.saveLimits'), 'submit'));
    form.append(this.limitFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }

  /**
   * Build fields from the backend's setting definitions.
   * @param configuration - The validated limits and labels.
   */
  private populateLimits(configuration: Configuration): void {
    this.limitFields.replaceChildren(element('legend', translate('settings.limits')));
    const advanced = element('details');
    advanced.append(element('summary', translate('settings.advancedLimits')));
    for (const [index, [name, definition]] of Object.entries(configuration.definitions)
      .filter(([name]) => name !== 'catalog_interval_hours')
      .entries()) {
      const label = element(
        'label',
        translate(`settings.limit.${name}` as MessageKey, {}, definition.label),
      );
      const input = element('input');
      input.type = 'number';
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.step = '1';
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      (index < 2 ? this.limitFields : advanced).append(label);
    }
    this.limitFields.append(advanced, button(translate('settings.saveLimits'), 'submit'));
  }

  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  private saveLimits(configuration: Configuration): void {
    const changes: Record<string, number> = {};
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== configuration.settings[name]) changes[name] = input.valueAsNumber;
    }
    if (Object.keys(changes).length === 0) {
      this.status.textContent = translate('settings.noLimitChanges');
      return;
    }
    void this.updateSettings(translate('settings.limitsSaved'), '/settings', 'PATCH', {
      revision: configuration.revision,
      settings: changes,
    });
  }

  /**
   * Build the controls for checking public model sources.
   * @returns The automatic model check form.
   */
  private modelUpdates(): HTMLFormElement {
    const form = element('form');
    this.catalogFields.disabled = true;
    const automaticLabel = element('label', translate('settings.automaticChecks'));
    this.automatic.type = 'checkbox';
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element('label', translate('settings.checkInterval'));
    this.interval.type = 'number';
    this.interval.step = '1';
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.catalogFields.append(
      element('legend', translate('settings.modelUpdates')),
      automaticLabel,
      intervalLabel,
      element('p', translate('settings.checkNotice')),
      button(translate('settings.saveChecks'), 'submit'),
    );
    form.append(this.catalogFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveModelUpdates(this.configuration);
    });
    return form;
  }

  /**
   * Save automatic checks without changing the displayed model list.
   * @param configuration - The settings and revision currently shown.
   */
  private saveModelUpdates(configuration: Configuration): void {
    const settings = {
      catalog_auto_check: this.automatic.checked,
      catalog_interval_hours: this.interval.valueAsNumber,
    };
    if (
      settings.catalog_auto_check === configuration.settings.catalog_auto_check &&
      settings.catalog_interval_hours === configuration.settings.catalog_interval_hours
    ) {
      this.status.textContent = translate('settings.noCheckChanges');
      return;
    }
    void this.updateSettings(translate('settings.checksSaved'), '/settings', 'PATCH', {
      revision: configuration.revision,
      settings,
    });
  }

  /**
   * Show validated settings and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  private display(configuration: Configuration): void {
    this.configuration = configuration;
    if (this.inputs.size === 0) this.populateLimits(configuration);
    this.key.maxLength = configuration.credentialLimit;
    const interval = configuration.definitions.catalog_interval_hours;
    this.interval.min = String(interval.minimum);
    this.interval.max = String(interval.maximum);
    this.source.textContent = {
      missing: translate('settings.missingKey'),
      saved: translate('settings.savedKey'),
      environment: translate('settings.environmentKey'),
    }[configuration.credentialSource];
    this.automatic.checked = configuration.settings.catalog_auto_check;
    this.interval.value = String(configuration.settings.catalog_interval_hours);
    for (const [name, definition] of Object.entries(configuration.definitions)) {
      const input = this.inputs.get(name);
      if (!input) continue;
      input.min = String(definition.minimum);
      input.max = String(definition.maximum);
      input.value = String(configuration.settings[name]);
    }
    if (!configuration.mutationAllowed) this.status.textContent = translate('settings.readOnly');
  }

  /**
   * Keep settings requests serial and show the server's response.
   * @param message - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  private async updateSettings(
    message: string,
    route?: string,
    method?: string,
    body?: unknown,
  ): Promise<void> {
    this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = true;
    this.reload.disabled = true;
    this.status.textContent = translate('working');
    try {
      const value = await requestConfiguration(
        this.fetcher,
        this.controller.signal,
        route,
        method,
        body,
      );
      if (this.controller.signal.aborted) return;
      this.status.textContent = message;
      this.display(value);
    } catch (error) {
      if (!this.controller.signal.aborted)
        this.status.textContent =
          error instanceof Error ? error.message : translate('settings.updateFailed');
    } finally {
      if (!this.controller.signal.aborted) {
        this.keyFields.disabled =
          this.limitFields.disabled =
          this.catalogFields.disabled =
            !this.configuration?.mutationAllowed;
        this.reload.disabled = false;
      }
    }
  }

  /** Show the dialog and read local settings. */
  show(): void {
    document.body.append(this.dialog);
    this.dialog.showModal();
    void this.updateSettings(translate('settings.loaded'));
  }

  /** Clear the key input, stop requests, and return focus to the caller. */
  private dispose(): void {
    this.key.value = '';
    this.controller.abort();
    this.dialog.remove();
    if (current === this) current = undefined;
    if (this.previousFocus instanceof HTMLElement && this.previousFocus.isConnected)
      this.previousFocus.focus();
  }
}

/**
 * Open one settings dialog at a time.
 * @param fetcher - ComfyUI's local API client.
 */
export function openSettings(fetcher: Fetcher): void {
  if (current?.dialog.open) {
    current.dialog.focus();
    return;
  }
  current = new SettingsDialog(fetcher);
  current.show();
}
