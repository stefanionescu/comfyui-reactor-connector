import { button, element } from '#web/dom.ts';

import {
  type Configuration,
  type Fetcher,
  type FieldName,
  fields,
  requestConfiguration,
} from '#web/settings/api.ts';

let current: SettingsDialog | undefined;

/** Edit server settings and cancel pending requests when the dialog closes. */
class SettingsDialog {
  readonly dialog = element('dialog');

  private readonly previousFocus = document.activeElement;

  private readonly controller = new AbortController();

  private readonly status = element('p', 'Loading local settings…');

  private readonly source = element('p');

  private readonly reload = button('Reload settings');

  private readonly key = element('input');

  private readonly keyFields = element('fieldset');

  private readonly limitFields = element('fieldset');

  private readonly catalogFields = element('fieldset');

  private readonly automatic = element('input');

  private readonly interval = element('input');

  private readonly inputs = new Map<FieldName, HTMLInputElement>();

  private configuration: Configuration | undefined;

  /**
   * Build settings forms without contacting Reactor.
   * @param fetcher - ComfyUI's local API client.
   */
  constructor(private readonly fetcher: Fetcher) {
    this.dialog.className = 'reactor-settings';
    this.dialog.setAttribute('aria-labelledby', 'reactor-settings-title');
    const heading = element('h2', 'Reactor settings');
    heading.id = 'reactor-settings-title';
    const close = button('Close');
    close.setAttribute('aria-label', 'Close Reactor settings');
    close.addEventListener('click', () => this.dialog.close());
    const header = element('header');
    header.append(heading, close);
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.reload.addEventListener('click', () => void this.perform('Local settings loaded.'));
    this.dialog.append(
      header,
      element(
        'p',
        'Reactor uses its own account and credits. Opening settings and saving a key do not start generation.',
      ),
      this.source,
      this.credentials(),
      element(
        'p',
        'The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here.',
      ),
      this.limits(),
      element(
        'p',
        'Session time includes setup and generation. These limits do not buy credits or change account billing.',
      ),
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
    const label = element('label', 'Reactor API key');
    this.key.type = 'password';
    this.key.autocomplete = 'off';
    this.key.spellcheck = false;
    this.key.maxLength = 1024;
    this.key.required = true;
    label.append(this.key);
    const clear = button('Clear saved key');
    // eslint-disable-next-line local/no-trivial-functions -- Clearing the key field must happen before this user-triggered request.
    clear.addEventListener('click', () => {
      this.key.value = '';
      void this.perform(
        'Saved key cleared. Any environment key remains active.',
        '/credential',
        'DELETE',
      );
    });
    const actions = element('div');
    actions.className = 'reactor-actions';
    actions.append(button('Save key', 'submit'), clear);
    this.keyFields.append(element('legend', 'Credentials'), label, actions);
    form.append(this.keyFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const value = this.key.value;
      this.key.value = '';
      void this.perform(
        'Key saved on this server. Reactor checks it when you start a session.',
        '/credential',
        'PUT',
        { api_key: value },
      );
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
    this.limitFields.append(element('legend', 'Execution limits'));
    const advanced = element('details');
    advanced.append(element('summary', 'Advanced limits'));
    for (const [index, [name, title]] of fields.entries()) {
      const label = element('label', title);
      const input = element('input');
      input.type = 'number';
      input.min = '1';
      input.max = '3600';
      input.step = '1';
      input.required = true;
      this.inputs.set(name, input);
      label.append(input);
      (index < 2 ? this.limitFields : advanced).append(label);
    }
    this.limitFields.append(advanced, button('Save limits', 'submit'));
    form.append(this.limitFields);
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (this.configuration && form.reportValidity()) this.saveLimits(this.configuration);
    });
    return form;
  }

  /**
   * Save only limits changed since the last successful read.
   * @param configuration - The settings and revision currently shown.
   */
  private saveLimits(configuration: Configuration): void {
    const changes: Partial<Record<FieldName, number>> = {};
    for (const [name, input] of this.inputs) {
      if (input.valueAsNumber !== configuration.settings[name]) changes[name] = input.valueAsNumber;
    }
    if (Object.keys(changes).length === 0) {
      this.status.textContent = 'No limit changes to save.';
      return;
    }
    void this.perform('Limits saved. They apply to new executions.', '/settings', 'PATCH', {
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
    const automaticLabel = element('label', 'Check for model updates automatically');
    this.automatic.type = 'checkbox';
    automaticLabel.prepend(this.automatic);
    const intervalLabel = element('label', 'Check interval (hours)');
    this.interval.type = 'number';
    this.interval.min = '1';
    this.interval.max = '3600';
    this.interval.step = '1';
    this.interval.required = true;
    intervalLabel.append(this.interval);
    this.catalogFields.append(
      element('legend', 'Model updates'),
      automaticLabel,
      intervalLabel,
      element(
        'p',
        'Checks read public prices and model guides. They do not use your key or spend credits. Open Reactor models to see changes and refresh your list.',
      ),
      button('Save model check settings', 'submit'),
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
      this.status.textContent = 'No model check changes to save.';
      return;
    }
    void this.perform(
      'Model check settings saved. The scheduler reads changes within one minute.',
      '/settings',
      'PATCH',
      { revision: configuration.revision, settings },
    );
  }

  /**
   * Show validated settings and apply the server's editing policy.
   * @param configuration - The last successful server response.
   */
  private display(configuration: Configuration): void {
    this.configuration = configuration;
    this.source.textContent = {
      missing: 'No Reactor key is configured.',
      saved: 'A saved key is configured on this server.',
      environment: "The server's REACTOR_API_KEY environment variable is active.",
    }[configuration.credentialSource];
    this.automatic.checked = configuration.settings.catalog_auto_check;
    this.interval.value = String(configuration.settings.catalog_interval_hours);
    for (const [name, input] of this.inputs) input.value = String(configuration.settings[name]);
    if (!configuration.mutationAllowed)
      this.status.textContent = "Changes are disabled in this host's multi-user mode.";
  }

  /**
   * Keep settings requests serial and show the server's response.
   * @param message - The success message.
   * @param route - The local settings route.
   * @param method - The HTTP method.
   * @param body - The settings change, if any.
   * @returns When the response or error is displayed.
   */
  private async perform(
    message: string,
    route?: string,
    method?: string,
    body?: unknown,
  ): Promise<void> {
    this.keyFields.disabled = this.limitFields.disabled = this.catalogFields.disabled = true;
    this.reload.disabled = true;
    this.status.textContent = 'Working…';
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
          error instanceof Error ? error.message : 'Reactor settings could not be saved.';
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
    void this.perform('Local settings loaded.');
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
