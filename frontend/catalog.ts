import { type Catalog, type Model, requestCatalog } from "./catalog-api.ts";
import type { Fetcher } from "./configuration.ts";
import { button, element } from "./dom.ts";
import { settingsStyles } from "./styles.ts";

let currentDialog: HTMLDialogElement | undefined;

function modelRow(model: Model, seconds: number | undefined): HTMLElement {
  const row = element("li");
  row.append(element("h3", model.title), element("code", model.name));
  const support =
    model.support === "available" ? "Nodes available." : "No connector node available.";
  row.append(element("p", support));
  if (model.connect_name) row.append(element("p", `Connect name: ${model.connect_name}`));
  const rate =
    model.credits_per_second === null
      ? "Rate not listed."
      : `${model.credits_per_second} credits per session second.`;
  row.append(
    element("p", model.observed ? rate : `${rate} Not observed in the latest source check.`),
  );
  if (model.observed && model.credits_per_second !== null && seconds !== undefined) {
    const credits = (model.credits_per_second * seconds).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
    row.append(element("p", `${seconds} session seconds × listed rate = ${credits} credits.`));
  }
  if (model.documentation_url) {
    const link = element("a", "Reactor model guide");
    link.href = model.documentation_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    row.append(link);
  } else row.append(element("p", "No matching public guide was found."));
  return row;
}

export function openCatalog(fetcher: Fetcher, nodeId?: string): void {
  if (currentDialog?.open) {
    currentDialog.focus();
    return;
  }
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  currentDialog = dialog;
  dialog.className = "reactor-settings reactor-catalog";
  dialog.setAttribute("aria-labelledby", "reactor-catalog-title");
  const styles = element(
    "style",
    `${settingsStyles}
    .reactor-catalog { box-sizing: border-box; width: min(54rem, calc(100vw - 2rem)); }
    .reactor-catalog ul { list-style: none; padding: 0; }
    .reactor-catalog li { border-top: 1px solid var(--border-color, GrayText); padding: 1rem 0; }
    .reactor-catalog h3 { margin: 0 0 .4rem; }
    .reactor-catalog li p { margin: .35rem 0; }
    .reactor-catalog code { overflow-wrap: anywhere; }
    .reactor-catalog details { margin: .75rem 0; }
  `,
  );
  const heading = element("h2", "Reactor models");
  heading.id = "reactor-catalog-title";
  const close = button("Close");
  close.setAttribute("aria-label", "Close Reactor models");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(heading, close);
  const searchLabel = element("label", "Search models");
  const search = element("input");
  search.type = "search";
  search.placeholder = "Name or connect name";
  searchLabel.append(search);
  const durationLabel = element("label", "Session time to calculate (seconds)");
  const duration = element("input");
  duration.type = "number";
  duration.min = "0.1";
  duration.max = "3600";
  duration.step = "any";
  duration.placeholder = "Enter total paid session time";
  durationLabel.append(duration);
  const showAll = button("Show all models");
  showAll.hidden = !nodeId;
  showAll.addEventListener("click", () => {
    nodeId = undefined;
    showAll.hidden = true;
    render();
  });
  const refresh = button("Refresh models");
  const rollback = button("Restore previous list");
  refresh.disabled = rollback.disabled = true;
  const actions = element("div");
  actions.className = "reactor-actions";
  actions.append(refresh, rollback, showAll);
  const status = element("p", "Loading the local model list…");
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  const checked = element("p");
  const automatic = element("p");
  const count = element("p");
  const list = element("ul");
  list.setAttribute("aria-label", "Reactor models");
  const calculation = element("details");
  calculation.append(
    element("summary", "Calculate credits for session time"),
    durationLabel,
    element(
      "p",
      "Use total session time, including setup, pauses, and recording. Saved video length may be shorter. This estimate is not a spending limit or a quote.",
    ),
  );
  const sources = element("details");
  sources.append(element("summary", "Model sources and automatic checks"), checked, automatic);
  dialog.append(
    header,
    element(
      "p",
      "Refresh checks Reactor's public model list and prices. It sends no API key and uses no credits. New models need a compatible connector node.",
    ),
    actions,
    status,
    searchLabel,
    calculation,
    sources,
    count,
    list,
  );
  let catalog: Catalog | undefined;
  function render(): void {
    const query = search.value.trim().toLowerCase();
    const visible =
      catalog?.models.filter(
        (model) =>
          (!nodeId || model.node_ids.includes(nodeId)) &&
          `${model.name} ${model.title} ${model.connect_name ?? ""}`.toLowerCase().includes(query),
      ) ?? [];
    const seconds =
      duration.validity.valid && duration.value !== "" ? duration.valueAsNumber : undefined;
    list.replaceChildren(...visible.map((model) => modelRow(model, seconds)));
    count.textContent = `${visible.length} of ${catalog?.models.length ?? 0} catalog entries`;
  }
  async function perform(action: "read" | "refresh" | "rollback"): Promise<void> {
    refresh.disabled = rollback.disabled = true;
    status.textContent =
      action === "refresh" ? "Checking public model sources…" : "Loading model list…";
    try {
      const next = await requestCatalog(fetcher, controller.signal, action, catalog?.revision);
      if (controller.signal.aborted) return;
      catalog = next;
      checked.textContent = `Last source check: ${new Date(next.retrieved_at).toLocaleString()}. Your Reactor account determines which models you can use.`;
      const check = next.automatic_check;
      automatic.textContent = !check
        ? ""
        : !check.enabled
          ? "Automatic model checks are off. Change this in Reactor settings."
          : check.running
            ? "An automatic model check is running. Reopen this list to see its result."
            : check.error
              ? check.error
              : check.update_available === true
                ? "The model list has changed. Select Refresh models to update your list."
                : check.checked_at
                  ? `Automatic check: ${new Date(check.checked_at).toLocaleString()}. Checks run every ${check.interval_hours} hours.`
                  : "An automatic model check is due. Checks do not change this list.";
      status.textContent =
        action === "refresh"
          ? "Model list refreshed. No generation started."
          : action === "rollback"
            ? "Previous model list restored. This does not change which models Reactor offers."
            : "Local model list loaded.";
      render();
    } catch (error) {
      if (!controller.signal.aborted)
        status.textContent = error instanceof Error ? error.message : "Cannot load models.";
    } finally {
      if (!controller.signal.aborted) {
        refresh.disabled = !catalog?.mutation_allowed;
        rollback.disabled = !catalog?.mutation_allowed || !catalog.can_rollback;
      }
    }
  }
  search.addEventListener("input", render);
  duration.addEventListener("input", render);
  refresh.addEventListener("click", () => void perform("refresh"));
  rollback.addEventListener("click", () => void perform("rollback"));
  dialog.addEventListener(
    "close",
    () => {
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
  void perform("read");
}
