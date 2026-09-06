import {
  type Configuration,
  type Fetcher,
  type FieldName,
  fields,
  requestConfiguration,
} from "./configuration.ts";
import { button, element } from "./dom.ts";
import { settingsStyles } from "./styles.ts";

let currentDialog: HTMLDialogElement | undefined;

export function openSettings(fetcher: Fetcher): void {
  if (currentDialog?.open) {
    currentDialog.focus();
    return;
  }
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  currentDialog = dialog;
  dialog.className = "reactor-settings";
  dialog.setAttribute("aria-labelledby", "reactor-settings-title");
  const styles = element("style", settingsStyles);
  const heading = element("h2", "Reactor settings");
  heading.id = "reactor-settings-title";
  const close = button("Close");
  close.setAttribute("aria-label", "Close Reactor settings");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const status = element("p", "Loading local settings…");
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  const source = element("p");
  const reload = button("Reload settings");

  const keyForm = element("form");
  const keyFields = element("fieldset");
  keyFields.disabled = true;
  const keyLabel = element("label", "Reactor API key");
  const key = element("input");
  key.type = "password";
  key.autocomplete = "off";
  key.spellcheck = false;
  key.maxLength = 1024;
  key.required = true;
  keyLabel.append(key);
  const saveKey = button("Save key", "submit");
  const clearKey = button("Clear saved key");
  const keyActions = element("div");
  keyActions.className = "reactor-actions";
  keyActions.append(saveKey, clearKey);
  keyFields.append(element("legend", "Credentials"), keyLabel, keyActions);
  keyForm.append(keyFields);

  const limitsForm = element("form");
  const limitFields = element("fieldset");
  limitFields.disabled = true;
  limitFields.append(element("legend", "Execution limits"));
  const advanced = element("details");
  advanced.append(element("summary", "Advanced limits"));
  const inputs = new Map<FieldName, HTMLInputElement>();
  fields.forEach(([name, title], index) => {
    const label = element("label", title);
    const input = element("input");
    input.type = "number";
    input.min = "1";
    input.max = "3600";
    input.step = "1";
    input.required = true;
    inputs.set(name, input);
    label.append(input);
    (index < 2 ? limitFields : advanced).append(label);
  });
  limitFields.append(advanced, button("Save limits", "submit"));
  limitsForm.append(limitFields);
  const catalogForm = element("form");
  const catalogFields = element("fieldset");
  catalogFields.disabled = true;
  const automaticLabel = element("label", "Check for model updates automatically");
  const automatic = element("input");
  automatic.type = "checkbox";
  automaticLabel.prepend(automatic);
  const intervalLabel = element("label", "Check interval (hours)");
  const interval = element("input");
  interval.type = "number";
  interval.min = "1";
  interval.max = "3600";
  interval.step = "1";
  interval.required = true;
  intervalLabel.append(interval);
  catalogFields.append(
    element("legend", "Model updates"),
    automaticLabel,
    intervalLabel,
    element(
      "p",
      "Checks read public prices and model guides. They do not use your key or spend credits. Open Reactor models to see changes and refresh your list.",
    ),
    button("Save model check settings", "submit"),
  );
  catalogForm.append(catalogFields);
  dialog.append(
    header,
    element(
      "p",
      "Reactor uses its own account and credits. Opening settings and saving a key do not start generation.",
    ),
    source,
    keyForm,
    element(
      "p",
      "The saved key stays on the ComfyUI server. An environment key takes precedence. Keys are not checked with Reactor here.",
    ),
    limitsForm,
    element(
      "p",
      "Session time includes setup and generation. These limits do not buy credits or change account billing.",
    ),
    catalogForm,
    status,
    reload,
  );

  let configuration: Configuration | undefined;
  function display(value: Configuration): void {
    configuration = value;
    source.textContent = {
      missing: "No Reactor key is configured.",
      saved: "A saved key is configured on this server.",
      environment: "The server's REACTOR_API_KEY environment variable is active.",
    }[value.credentialSource];
    keyFields.disabled = !value.mutationAllowed;
    limitFields.disabled = !value.mutationAllowed;
    catalogFields.disabled = !value.mutationAllowed;
    automatic.checked = value.settings.catalog_auto_check;
    interval.value = String(value.settings.catalog_interval_hours);
    for (const [name, input] of inputs) input.value = String(value.settings[name]);
    if (!value.mutationAllowed)
      status.textContent = "Changes are disabled in this host's multi-user mode.";
  }

  async function perform(operation: () => Promise<Configuration>, message: string): Promise<void> {
    keyFields.disabled = true;
    limitFields.disabled = true;
    catalogFields.disabled = true;
    reload.disabled = true;
    status.textContent = "Working…";
    try {
      const value = await operation();
      if (controller.signal.aborted) return;
      status.textContent = message;
      display(value);
    } catch (error) {
      if (!controller.signal.aborted) {
        status.textContent =
          error instanceof Error ? error.message : "Reactor settings could not be saved.";
      }
    } finally {
      if (!controller.signal.aborted) {
        keyFields.disabled = !configuration?.mutationAllowed;
        limitFields.disabled = !configuration?.mutationAllowed;
        catalogFields.disabled = !configuration?.mutationAllowed;
        reload.disabled = false;
      }
    }
  }

  const request = (route?: string, method?: string, body?: unknown) =>
    requestConfiguration(fetcher, controller.signal, route, method, body);
  keyForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!keyForm.reportValidity()) return;
    const value = key.value;
    key.value = "";
    void perform(
      () => request("/credential", "PUT", { api_key: value }),
      "Key saved on this server. Reactor checks it when you start a session.",
    );
  });
  clearKey.addEventListener("click", () => {
    key.value = "";
    void perform(
      () => request("/credential", "DELETE"),
      "Saved key cleared. Any environment key remains active.",
    );
  });
  limitsForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!configuration || !limitsForm.reportValidity()) return;
    const changes: Partial<Record<FieldName, number>> = {};
    for (const [name, input] of inputs) {
      if (input.valueAsNumber !== configuration.settings[name]) changes[name] = input.valueAsNumber;
    }
    if (Object.keys(changes).length === 0) {
      status.textContent = "No limit changes to save.";
      return;
    }
    const revision = configuration.revision;
    void perform(
      () => request("/settings", "PATCH", { revision, settings: changes }),
      "Limits saved. They apply to new executions.",
    );
  });
  reload.addEventListener("click", () => void perform(() => request(), "Local settings loaded."));
  catalogForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!configuration || !catalogForm.reportValidity()) return;
    const settings = {
      catalog_auto_check: automatic.checked,
      catalog_interval_hours: interval.valueAsNumber,
    };
    if (
      settings.catalog_auto_check === configuration.settings.catalog_auto_check &&
      settings.catalog_interval_hours === configuration.settings.catalog_interval_hours
    ) {
      status.textContent = "No model check changes to save.";
      return;
    }
    const revision = configuration.revision;
    void perform(
      () => request("/settings", "PATCH", { revision, settings }),
      "Model check settings saved. The scheduler reads changes within one minute.",
    );
  });
  dialog.addEventListener(
    "close",
    () => {
      key.value = "";
      controller.abort();
      dialog.remove();
      styles.remove();
      currentDialog = undefined;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true },
  );
  document.head.append(styles);
  document.body.append(dialog);
  dialog.showModal();
  void perform(() => request(), "Local settings loaded.");
}
