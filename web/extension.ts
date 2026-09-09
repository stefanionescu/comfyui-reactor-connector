import './styles/interface.css';
import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { openLive } from '#web/live/dialog.ts';
import { refreshText } from '#web/localization.ts';
import { openControls } from '#web/live/controls.ts';
import { openModels } from '#web/discovery/dialog.ts';
import { openSettings } from '#web/settings/dialog.ts';
import { bindCreditRate } from '#web/discovery/rate.ts';
import { HELP_COMMAND, helpCommands, openNodeHelp } from '#web/help/command.ts';
import { translate, initializeLanguage, languageEvents } from '#web/language.ts';
import { bindNodeWidgets, configureNodeWidgets, refreshWidgetLabels } from '#web/nodes/labels.ts';

app.registerExtension({
  name: 'reactor.inc.configuration',
  init: initializeLanguage,
  setup: () => {
    languageEvents.addEventListener('change', refreshText);
    languageEvents.addEventListener('change', refreshWidgetLabels);
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./main.css', import.meta.url).href;
    if (
      ![...document.querySelectorAll('link[rel=stylesheet]')].some(
        (link) => link.getAttribute('href') === stylesheet.href,
      )
    )
      document.head.append(stylesheet);

    api.addEventListener('reactor-inc.live', (event) => {
      if (event instanceof CustomEvent) {
        openLive(event.detail, requestLocal);
      }
    });

    api.addEventListener('reactor-inc.controls', (event) => {
      if (event instanceof CustomEvent) openControls(event.detail, requestLocal);
    });
  },
  // eslint-disable-next-line local/no-trivial-functions -- ComfyUI calls this hook once to attach labels and the credit rate button.
  nodeCreated: (node) => {
    bindNodeWidgets(node);
    bindCreditRate(node, requestLocal);
  },
  loadedGraphNode: configureNodeWidgets,
  getSelectionToolboxCommands: helpCommands,
  commands: [
    {
      id: HELP_COMMAND,
      label: translate('help'),
      icon: 'pi pi-question-circle',
      function: openNodeHelp,
    },
    {
      id: 'ReactorInc.OpenSettings',
      label: translate('settings.title'),
      function: () => openSettings(requestLocal),
    },
    {
      id: 'ReactorInc.OpenCatalog',
      label: translate('models.title'),
      function: () => openModels(requestLocal),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'Reactor'],
      commands: ['ReactorInc.OpenSettings', 'ReactorInc.OpenCatalog'],
    },
  ],
});
