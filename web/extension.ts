import './styles.css';
import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import { openLive } from '#web/live/dialog.ts';
import { openControls } from '#web/live/controls.ts';
import { openModels } from '#web/discovery/dialog.ts';
import { bindCreditRate } from '#web/settings/rate.ts';
import { openSettings } from '#web/settings/dialog.ts';
import { bindNodeWidgets, configureNodeWidgets } from '#web/nodes/labels.ts';
import { HELP_COMMAND, helpCommands, openNodeHelp } from '#web/help/command.ts';

const stylesheet = document.createElement('link');
stylesheet.rel = 'stylesheet';
stylesheet.href = new URL('./main.css', import.meta.url).href;
document.head.append(stylesheet);

api.addEventListener('reactor-inc.live', (event) => {
  if (event instanceof CustomEvent) {
    openLive(event.detail, (route, options) => api.fetchApi(route, options));
  }
});

api.addEventListener('reactor-inc.controls', (event) => {
  if (event instanceof CustomEvent)
    openControls(event.detail, (route, options) => api.fetchApi(route, options));
});

app.registerExtension({
  name: 'reactor.inc.configuration',
  // eslint-disable-next-line local/no-trivial-functions -- ComfyUI calls this hook once to attach labels and the credit rate button.
  nodeCreated: (node) => {
    bindNodeWidgets(node);
    bindCreditRate(node, (route, options) => api.fetchApi(route, options));
  },
  loadedGraphNode: configureNodeWidgets,
  getSelectionToolboxCommands: helpCommands,
  commands: [
    {
      id: HELP_COMMAND,
      label: 'Help',
      icon: 'pi pi-question-circle',
      function: openNodeHelp,
    },
    {
      id: 'ReactorInc.OpenSettings',
      label: 'Reactor settings',
      function: () => openSettings((route, options) => api.fetchApi(route, options)),
    },
    {
      id: 'ReactorInc.OpenCatalog',
      label: 'Reactor models',
      function: () => openModels((route, options) => api.fetchApi(route, options)),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'Reactor'],
      commands: ['ReactorInc.OpenSettings', 'ReactorInc.OpenCatalog'],
    },
  ],
});
