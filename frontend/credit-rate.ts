import { requestCatalog } from "./catalog-api.ts";
import type { Fetcher } from "./configuration.ts";
import { button, element } from "./dom.ts";
import type { ReactorNode } from "./node-types.ts";
import { settingsStyles } from "./styles.ts";

function requestedSeconds(node: ReactorNode): number | undefined {
  function value(name: string): number | undefined {
    if (node.inputs?.some((input) => input.name === name && input.link != null)) return undefined;
    const raw = node.widgets?.find((widget) => widget.name === name)?.value;
    return typeof raw === "number" && Number.isFinite(raw) && raw > 0 ? raw : undefined;
  }
  if (node.comfyClass === "ReactorIncFastContinue") {
    const seconds = value("clip_seconds");
    const count = value("clip_count");
    return seconds !== undefined && count !== undefined ? seconds * count : undefined;
  }
  return value("duration_seconds");
}

let current: HTMLDialogElement | undefined;

function openCreditRate(node: ReactorNode, fetcher: Fetcher): void {
  if (current?.open) {
    current.focus();
    return;
  }
  const previousFocus = document.activeElement;
  const controller = new AbortController();
  const dialog = element("dialog");
  current = dialog;
  dialog.className = "reactor-settings";
  dialog.setAttribute("aria-labelledby", "reactor-rate-title");
  const style = element("style", settingsStyles);
  const title = element("h2", "Credit rate");
  title.id = "reactor-rate-title";
  const close = button("Close");
  close.addEventListener("click", () => dialog.close());
  const header = element("header");
  header.append(title, close);
  const seconds = requestedSeconds(node);
  const request = element(
    "p",
    seconds === undefined
      ? "The video length comes from a connected input or is not available. Enter a session time below to calculate credits."
      : `This node requests ${seconds.toLocaleString()} seconds of video. Setup, pauses, and recording can add paid time.`,
  );
  const label = element("label", "Session time to calculate (seconds)");
  const duration = element("input");
  duration.type = "number";
  duration.min = "0.1";
  duration.max = "3600";
  duration.step = "any";
  duration.placeholder = "Enter total paid session time";
  if (seconds !== undefined) duration.value = String(seconds);
  label.append(duration);
  const validation = element("p");
  validation.setAttribute("role", "status");
  const validateDuration = () => {
    validation.textContent =
      duration.value === "" || !duration.validity.valid
        ? "Enter a session time from 0.1 to 3,600 seconds."
        : "";
  };
  duration.addEventListener("input", validateDuration);
  validateDuration();
  const status = element("p", "Loading the local credit rate…");
  status.setAttribute("role", "status");
  const rates = element("div");
  rates.setAttribute("aria-live", "polite");
  dialog.append(
    header,
    request,
    label,
    validation,
    element(
      "p",
      "This is rate × time, not an exact charge or a spending limit. The starting time uses the requested video length and excludes extra paid time. Your Reactor account shows actual charges.",
    ),
    status,
    rates,
  );
  dialog.addEventListener(
    "close",
    () => {
      controller.abort();
      dialog.remove();
      style.remove();
      current = undefined;
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    },
    { once: true },
  );
  document.head.append(style);
  document.body.append(dialog);
  dialog.showModal();
  void requestCatalog(fetcher, controller.signal, "read")
    .then((catalog) => {
      if (controller.signal.aborted) return;
      const models = catalog.models.filter((model) =>
        model.node_ids.includes(node.comfyClass ?? ""),
      );
      status.textContent = `Rates checked ${new Date(catalog.retrieved_at).toLocaleString()}.`;
      if (!models.length)
        status.textContent =
          "No rate is listed for this node. Open the ComfyUI menu, then Extensions → Reactor → Reactor models, and refresh the list.";
      function render(): void {
        rates.replaceChildren();
        for (const model of models) {
          rates.append(element("h3", model.title));
          const rate = model.credits_per_second;
          if (!model.observed || rate === null) {
            rates.append(
              element(
                "p",
                "A current rate is not available. Refresh Reactor models before relying on a calculation.",
              ),
            );
            continue;
          }
          rates.append(element("p", `${rate.toLocaleString()} credits per session second.`));
          if (duration.value !== "" && duration.validity.valid) {
            const total = (rate * duration.valueAsNumber).toLocaleString(undefined, {
              maximumFractionDigits: 2,
            });
            rates.append(
              element(
                "p",
                `${duration.valueAsNumber.toLocaleString()} seconds × ${rate.toLocaleString()} = ${total} credits.`,
              ),
            );
          }
        }
      }
      duration.addEventListener("input", render);
      render();
    })
    .catch((error: unknown) => {
      if (!controller.signal.aborted)
        status.textContent =
          error instanceof Error ? error.message : "Cannot load the credit rate.";
    });
}

export function bindCreditRate(node: ReactorNode, fetcher: Fetcher): void {
  const id = node.comfyClass;
  if (
    !id?.startsWith("ReactorInc") ||
    id === "ReactorIncHeliosAddPrompt" ||
    id === "ReactorIncLongLiveAddShot"
  )
    return;
  node.addWidget("button", "View credit rate", "", () => openCreditRate(node, fetcher), {
    serialize: false,
  });
}
