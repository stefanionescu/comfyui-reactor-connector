import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";
import { openCatalog } from "./catalog.ts";
import { openControls } from "./control-panel.ts";
import { bindCreditRate } from "./credit-rate.ts";
import { openLive } from "./live.ts";
import { HELP_COMMAND, helpCommands, openNodeHelp } from "./node-help.ts";
import { bindNodeWidgets, configureNodeWidgets } from "./node-labels.ts";
import { openSettings } from "./settings.ts";

api.addEventListener("reactor-inc.live", (event) => {
  if (event instanceof CustomEvent) {
    openLive(event.detail, (route, options) => api.fetchApi(route, options));
  }
});

api.addEventListener("reactor-inc.controls", (event) => {
  if (event instanceof CustomEvent)
    openControls(event.detail, (route, options) => api.fetchApi(route, options));
});

app.registerExtension({
  name: "reactor.inc.configuration",
  nodeCreated: (node) => {
    bindNodeWidgets(node);
    const fetcher = (route: string, options?: RequestInit) => api.fetchApi(route, options);
    bindCreditRate(node, fetcher);
  },
  loadedGraphNode: configureNodeWidgets,
  getSelectionToolboxCommands: helpCommands,
  commands: [
    {
      id: HELP_COMMAND,
      label: "Help",
      icon: "pi pi-question-circle",
      function: openNodeHelp,
    },
    {
      id: "ReactorInc.OpenSettings",
      label: "Reactor settings",
      function: () => openSettings((route, options) => api.fetchApi(route, options)),
    },
    {
      id: "ReactorInc.OpenCatalog",
      label: "Reactor models",
      function: () => openCatalog((route, options) => api.fetchApi(route, options)),
    },
  ],
  menuCommands: [
    {
      path: ["Extensions", "Reactor"],
      commands: ["ReactorInc.OpenSettings", "ReactorInc.OpenCatalog"],
    },
  ],
});
